"""Post whatever is due from each episode's release.yaml. Safe to run any time, any number of times.

    uv run scripts/release_due.py [--dry-run] [--now 2026-11-11T19:00:00Z]

Meant to run from a systemd user timer (hourly and soon after boot or wake), so a laptop
that was off at the planned time posts the item the next time it is on. Nothing is posted
twice: an item is skipped on a platform once published.yaml has any entry for it. A
failed attempt is recorded with state "failed" and is not retried, because it may have
posted anyway; check the platform by hand, then delete that entry to let the job retry.

Each run logs to ~/.local/state/math-videos/release.log and shows a desktop notification
when it posts or fails.
"""

import argparse
import datetime as dt
import fcntl
import json
import subprocess
import sys
from pathlib import Path

import requests
import yaml

ROOT = Path(__file__).resolve().parent.parent
STATE = Path.home() / ".local" / "state" / "math-videos"
LOG = STATE / "release.log"
GH = ["gh", "--repo"]


def log(msg):
    line = f"{dt.datetime.now().isoformat(timespec='seconds')} {msg}"
    print(line, flush=True)
    with LOG.open("a") as f:
        f.write(line + "\n")


def notify(msg, urgent=False):
    subprocess.run(["notify-send", "-a", "Chosen Maths", *(["-u", "critical"] if urgent else []),
                    "Chosen Maths release", msg], check=False)


def run(cmd, dry):
    if dry and cmd[0] == "gh":
        log("would run: " + " ".join(cmd))
        return subprocess.CompletedProcess(cmd, 0, "", "")
    r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    for line in (r.stdout + r.stderr).strip().splitlines():
        log("  " + line)
    return r


def online():
    try:
        requests.head("https://api.github.com", timeout=10)
        return True
    except requests.RequestException:
        return False


def repo_slug():
    url = subprocess.run(["git", "remote", "get-url", "origin"], cwd=ROOT, capture_output=True,
                         text=True, check=True).stdout.strip()
    return url.removesuffix(".git").split("github.com")[1].lstrip(":/")


def published(slug):
    path = ROOT / "episodes" / slug / "published.yaml"
    return (yaml.safe_load(path.read_text()) if path.exists() else None) or []


def mark_failed(slug, platform, item, note):
    from mathvid.publish import record
    record(slug, platform, item, "failed", note=note)


def push(sha, repo, dry):
    """Fast-forward origin's main to exactly `sha`, so later local commits stay unpushed."""
    url = f"https://github.com/{repo}.git"
    remote = subprocess.run(["git", "ls-remote", url, "refs/heads/main"], cwd=ROOT, capture_output=True,
                            text=True).stdout.split()
    full = subprocess.run(["git", "rev-parse", sha], cwd=ROOT, capture_output=True, text=True).stdout.strip()
    if remote and subprocess.run(["git", "merge-base", "--is-ancestor", full, remote[0]], cwd=ROOT).returncode == 0:
        return True  # already on GitHub
    if dry:
        log(f"would push {sha} to {repo} main")
        return True
    r = run(["git", "-c", "credential.helper=", "-c", "credential.helper=!gh auth git-credential",
             "push", url, f"{full}:refs/heads/main"], dry)
    return r.returncode == 0


def ensure_release(slug, title, item, repo, dry):
    """Attach <item>.mp4 and its cover to the episode's release, creating the release if needed."""
    out = ROOT / "out" / slug
    view = subprocess.run(GH + [repo, "release", "view", slug, "--json", "assets"], cwd=ROOT,
                          capture_output=True, text=True)
    if view.returncode != 0:
        r = run(GH + [repo, "release", "create", slug, "--title", f"{title} (shorts)",
                      "--notes", "Vertical cuts of the episode and their covers."], dry)
        if r.returncode != 0:
            return False
        have = set()
    else:
        have = {a["name"] for a in json.loads(view.stdout)["assets"]}
    files = [str(out / f) for f in (f"{item}.mp4", f"{item}-cover.jpg") if f not in have]
    if files and run(GH + [repo, "release", "upload", slug, *files], dry).returncode != 0:
        return False
    return True


def asset(repo, slug, name):
    return f"https://github.com/{repo}/releases/download/{slug}/{name}"


def post_cmd(platform, payload, repo, slug, item):
    uv = ["uv", "run", "scripts/" + ("post_bluesky.py" if platform == "bluesky" else "post_meta.py")]
    if platform == "bluesky":
        return uv + [str(payload)]
    cmd = uv + [platform, str(payload)]
    if platform in ("instagram", "threads"):
        cmd += ["--video-url", asset(repo, slug, f"{item}.mp4")]
    if platform == "instagram":
        cmd += ["--cover-url", asset(repo, slug, f"{item}-cover.jpg")]
    return cmd


def release(slug, now, repo, dry, done):
    plan = yaml.safe_load((ROOT / "episodes" / slug / "release.yaml").read_text())
    meta = yaml.safe_load((ROOT / "episodes" / slug / "metadata.yaml").read_text())
    title = meta["long"]["title"]
    for item, at in sorted(plan["at"].items(), key=lambda kv: str(kv[1])):
        when = at if isinstance(at, dt.datetime) else dt.datetime.fromisoformat(str(at).replace("Z", "+00:00"))
        if when.tzinfo is None:
            when = when.replace(tzinfo=dt.timezone.utc)  # PyYAML may drop the Z
        if when > now:
            continue
        if item == "long":
            if plan.get("push") and not push(plan["push"], repo, dry):
                log(f"{slug}: push failed; will retry next run")
                notify(f"{slug}: pushing the source to GitHub failed. See {LOG}.", urgent=True)
            continue
        seen = {(e["platform"], e["item"]) for e in published(slug)}
        todo = [p for p in plan["platforms"] if (p, item) not in seen]
        if not todo:
            continue
        payload = ROOT / "out" / slug / "publish" / f"{item}.json"
        if not payload.exists():
            log(f"{slug}: {payload} is missing; run publish_prep.py")
            notify(f"{slug} {item}: payload missing. See {LOG}.", urgent=True)
            continue
        if any(p in ("instagram", "threads") for p in todo) and not ensure_release(slug, title, item, repo, dry):
            log(f"{slug}: could not attach {item} to the GitHub release; will retry next run")
            notify(f"{slug} {item}: GitHub release upload failed. See {LOG}.", urgent=True)
            continue
        for platform in todo:
            cmd = post_cmd(platform, payload, repo, slug, item)
            if dry:
                cmd.append("--dry-run")
            log(f"{slug}: {item} -> {platform}: {' '.join(cmd)}")
            r = run(cmd, dry)
            if dry:
                continue
            if r.returncode == 0:
                done.append(f"{item} on {platform}")
                if "WARNING" in r.stdout:
                    notify(f"{slug} {item} on {platform}: posted with a warning. See {LOG}.")
            else:
                err = (r.stderr or r.stdout).strip().splitlines()[-1:] or ["unknown error"]
                mark_failed(slug, platform, item, err[0][:300])
                notify(f"{slug} {item} on {platform} FAILED; it may or may not have posted. "
                       f"Check the platform. See {LOG}.", urgent=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="say what is due; post nothing")
    ap.add_argument("--now", help="pretend it is this UTC time (for testing with --dry-run)")
    a = ap.parse_args()
    if a.now and not a.dry_run:
        sys.exit("--now only works with --dry-run")
    STATE.mkdir(parents=True, exist_ok=True)
    lock = open(STATE / "release.lock", "w")
    try:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        return  # another run is still posting
    now = (dt.datetime.fromisoformat(a.now.replace("Z", "+00:00")) if a.now
           else dt.datetime.now(dt.timezone.utc))
    plans = sorted((ROOT / "episodes").glob("*/release.yaml"))
    if not plans:
        return
    if not online():
        log("offline; will try next run")
        return
    repo, done = repo_slug(), []
    for plan in plans:
        release(plan.parent.name, now, repo, a.dry_run, done)
    if done:
        log("posted: " + ", ".join(done))
        notify("Posted " + ", ".join(done) + ".")


if __name__ == "__main__":
    main()
