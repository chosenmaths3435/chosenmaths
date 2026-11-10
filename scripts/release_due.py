"""Post whatever is due from each episode's release.yaml. Safe to run any time, any number of times.

    uv run scripts/release_due.py [--dry-run] [--now 2026-11-11T19:00:00Z]

Meant to run from a systemd user timer (hourly and soon after boot or wake), so a laptop
that was off at the planned time posts the item the next time it is on. Nothing is posted
twice: an item is skipped on a platform once published.yaml has any entry for it. A
failed attempt is recorded with state "failed" and is not retried, because it may have
posted anyway; check the platform by hand, then delete that entry to let the job retry.

Once a day, while any release is pending, it also runs check_accounts.py and notifies if
a login is broken, so it can be fixed before the next post is due.

When every item of an episode is out (YouTube public, each short on every platform), it
wraps up: sets status: published, commits the episode's records in videos/ and pushes
main, and replaces the "Scheduled" line in the idea's README (private repo, found by
"videos/episodes/<slug>/") with the links, then rebuilds ideas/INDEX.md and commits that.

Each run logs to ~/.local/state/math-videos/release.log and shows a desktop notification
when it posts, fails, or finishes an episode.
"""

import argparse
import datetime as dt
import fcntl
import json
import subprocess
import sys
from pathlib import Path

import re

import requests
import yaml

ROOT = Path(__file__).resolve().parent.parent
PRIVATE = ROOT.parent  # the math-content repo, holding ideas/
STATE = Path.home() / ".local" / "state" / "math-videos"
LOG = STATE / "release.log"
GH = ["gh", "--repo"]
DRY = False  # dry runs print but leave the log alone


def log(msg):
    line = f"{dt.datetime.now().isoformat(timespec='seconds')} {msg}"
    print(line, flush=True)
    if DRY:
        return
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
    """Fast-forward origin's main to `sha` (a commit, or "main" for the local branch)."""
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


def is_public_on_youtube(video_id):
    r = requests.get("https://www.youtube.com/oembed",
                     params={"url": f"https://youtu.be/{video_id}", "format": "json"}, timeout=30)
    return r.status_code == 200  # private and scheduled videos return 401/403


def check_accounts(dry):
    """Once a day: notify if any platform login is broken."""
    stamp = STATE / "accounts-checked"
    today = dt.date.today().isoformat()
    if dry or (stamp.exists() and stamp.read_text().strip() == today):
        return
    try:
        r = subprocess.run(["uv", "run", "scripts/check_accounts.py"], cwd=ROOT, capture_output=True,
                           text=True, timeout=300)
        bad = [ln for ln in r.stdout.splitlines() if ln.startswith(("FAIL", "todo"))]
    except subprocess.TimeoutExpired:
        bad = ["the account check hung; YouTube probably wants a browser login (post_youtube.py whoami)"]
    stamp.write_text(today)
    for ln in bad:
        log("account check: " + ln)
    if bad:
        notify("A login needs fixing before the next post: " + "; ".join(ln.split(None, 2)[1] if
               ln.startswith(("FAIL", "todo")) else ln for ln in bad) + f". See {LOG}.", urgent=True)


def git_commit(repo_dir, paths, msg, identity=None):
    ident = ["-c", f"user.name={identity[0]}", "-c", f"user.email={identity[1]}"] if identity else []
    paths = [p for p in paths if (Path(repo_dir) / p).exists()]
    if subprocess.run(["git", "add", "--", *paths], cwd=repo_dir).returncode != 0:
        return False
    r = subprocess.run(["git", *ident, "commit", "-q", "-m", msg, "--", *paths], cwd=repo_dir,
                       capture_output=True, text=True)
    return r.returncode == 0 or "nothing to commit" in r.stdout + r.stderr


CHANNEL = ("Chosen Maths", "chosenmaths3435@users.noreply.github.com")


def wrap_up(slug, plan, now, repo, dry):
    """Finish an episode whose every item is out. Returns True once it is wrapped up."""
    ep = ROOT / "episodes" / slug
    if any(parse(at) > now for at in plan["at"].values()):
        return False
    entries = published(slug)
    public = {(e["platform"], e["item"]) for e in entries if e.get("state") == "public"}
    shorts = [i for i in plan["at"] if i != "long"]
    if any((p, i) not in public for i in shorts for p in plan["platforms"]):
        return False
    yt = {e["item"]: e for e in entries if e["platform"] == "youtube" and e.get("id")}
    if any(i not in yt or not is_public_on_youtube(yt[i]["id"]) for i in plan["at"]):
        return False
    if dry:
        log(f"{slug}: would wrap up (status published, commit, push, idea README)")
        return True
    for e in entries:
        if e["platform"] == "youtube" and e["item"] in plan["at"]:
            e["state"] = "public"
    (ep / "published.yaml").write_text(yaml.safe_dump(entries, sort_keys=False, allow_unicode=True))
    epy = ep / "episode.yaml"
    epy.write_text(re.sub(r"(?m)^status:\s*\S+", "status: published", epy.read_text(), count=1))
    paths = [f"episodes/{slug}/{f}" for f in ("episode.yaml", "published.yaml", "release.yaml")]
    if not git_commit(ROOT, paths, f"Publish the {slug} episode", CHANNEL):
        notify(f"{slug}: everything is out, but committing the records failed. See {LOG}.", urgent=True)
    elif not push("main", repo, dry):
        notify(f"{slug}: everything is out, but pushing main failed. See {LOG}.", urgent=True)
    note_idea(slug, plan, yt)
    log(f"{slug}: fully released")
    notify(f"{slug} is fully released on every platform.")
    return True


def note_idea(slug, plan, yt):
    """Swap the idea README's "Scheduled" line for the links."""
    marker = f"videos/episodes/{slug}/"
    for readme in sorted((PRIVATE / "ideas").glob("*/README.md")):
        lines = readme.read_text().splitlines(keepends=True)
        hit = [i for i, ln in enumerate(lines) if ln.startswith("- Scheduled") and marker in ln]
        if not hit:
            continue
        meta = yaml.safe_load((ROOT / "episodes" / slug / "metadata.yaml").read_text())
        day = min(parse(at) for at in plan["at"].values()).astimezone().date()
        shorts = ", ".join(yt[i]["url"] for i in plan["at"] if i != "long" and i in yt)
        if "long" in yt:
            lines[hit[0]] = (f"- Published {day} as \"{meta['long']['title']}\": {yt['long']['url']}.\n"
                             f"  Shorts: {shorts}. All posts are in {marker}published.yaml.\n")
        else:
            title = next(iter(meta["shorts"].values()))["title"]
            lines[hit[0]] = (f"- Published {day} as the short \"{title}\": {shorts}.\n"
                             f"  All posts are in {marker}published.yaml.\n")
        readme.write_text("".join(lines))
        subprocess.run(["uv", "run", "scripts/build_index.py"], cwd=PRIVATE, capture_output=True)
        rel = str(readme.relative_to(PRIVATE))
        if not git_commit(PRIVATE, [rel, "ideas/INDEX.md"], f"Note the published {slug} episode"):
            notify(f"{slug}: could not commit the idea README note. See {LOG}.", urgent=True)
        return
    log(f"{slug}: no idea README has a Scheduled line for {marker}; add the links by hand")


def parse(at):
    when = at if isinstance(at, dt.datetime) else dt.datetime.fromisoformat(str(at).replace("Z", "+00:00"))
    return when if when.tzinfo else when.replace(tzinfo=dt.timezone.utc)  # PyYAML may drop the Z


def release(slug, now, repo, dry, done):
    plan = yaml.safe_load((ROOT / "episodes" / slug / "release.yaml").read_text())
    meta = yaml.safe_load((ROOT / "episodes" / slug / "metadata.yaml").read_text())
    title = (meta.get("long") or next(iter(meta["shorts"].values())))["title"]
    due = [(i, at) for i, at in sorted(plan["at"].items(), key=lambda kv: str(kv[1])) if parse(at) <= now]
    if due and plan.get("push") and not push(plan["push"], repo, dry):
        log(f"{slug}: push failed; will retry next run")
        notify(f"{slug}: pushing the source to GitHub failed. See {LOG}.", urgent=True)
    for item, at in due:
        if item == "long":
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
    wrap_up(slug, plan, now, repo, dry)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="say what is due; post nothing")
    ap.add_argument("--now", help="pretend it is this UTC time (for testing with --dry-run)")
    a = ap.parse_args()
    global DRY
    DRY = a.dry_run
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
    plans = [p for p in sorted((ROOT / "episodes").glob("*/release.yaml"))
             if (yaml.safe_load((p.parent / "episode.yaml").read_text()) or {}).get("status") != "published"]
    if not plans:
        return
    if not online():
        log("offline; will try next run")
        return
    check_accounts(a.dry_run)
    repo, done = repo_slug(), []
    for plan in plans:
        release(plan.parent.name, now, repo, a.dry_run, done)
    if done:
        log("posted: " + ", ".join(done))
        notify("Posted " + ", ".join(done) + ".")


if __name__ == "__main__":
    main()
