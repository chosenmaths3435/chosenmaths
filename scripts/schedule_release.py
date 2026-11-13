"""Schedule a finished episode's whole release, so it goes out over the next free days.

    uv run scripts/schedule_release.py <slug> [--start 2026-11-20] [--time 10:00] [--idea <idea-slug>]
                                              [--share-days] [--dry-run]

Run it only after the user has approved the episode and said to schedule it. It:
- checks the accounts and runs publish_prep.py (stops on any problem)
- picks the days: the first free day on or after --start (default tomorrow) gets the
  long-form at --time and short1 15 minutes later; each later short gets the next free
  day. A day is free when no other episode's release.yaml has anything on it, unless
  --share-days (use it when the user names an exact day that is already taken). A
  shorts-only episode (no `long:` in metadata.yaml) starts with short1.
- uploads the long-form and the shorts to YouTube as private (skipping any already in
  published.yaml) and schedules each one to go public at its time
- writes episodes/<slug>/release.yaml, which scripts/release_due.py (the systemd timer)
  reads to post each short to the other platforms once its time has passed

--idea also notes the schedule in ../ideas/<idea>/README.md (private repo), so the
release job can add the published links there at the end. Times use the laptop's
timezone unless --tz says otherwise.
"""

import argparse
import datetime as dt
import json
import subprocess
import sys
from pathlib import Path
from zoneinfo import ZoneInfo

import yaml

ROOT = Path(__file__).resolve().parent.parent
IDEAS = ROOT.parent / "ideas"
PLATFORMS = ["instagram", "facebook", "threads", "bluesky"]
SHORT1_DELAY = dt.timedelta(minutes=15)  # the long-form is live before short1 links to it


def local_tz():
    try:
        return ZoneInfo(str(Path("/etc/localtime").resolve()).split("zoneinfo/")[1])
    except (IndexError, KeyError, ValueError):
        return dt.timezone.utc


def parse_at(v):
    t = v if isinstance(v, dt.datetime) else dt.datetime.fromisoformat(str(v).replace("Z", "+00:00"))
    return t if t.tzinfo else t.replace(tzinfo=dt.timezone.utc)


def taken_days(slug, tz):
    days = set()
    for plan in (ROOT / "episodes").glob("*/release.yaml"):
        if plan.parent.name == slug:
            continue
        for at in (yaml.safe_load(plan.read_text()).get("at") or {}).values():
            days.add(parse_at(at).astimezone(tz).date())
    return days


def plan_times(items, start, clock, tz, taken):
    """Map each item to an aware UTC datetime: long + short1 on day one, then a short a day."""
    out, day = {}, start
    for item in items:
        if item == "short1" and "long" in out:
            out[item] = out["long"] + SHORT1_DELAY
            continue
        while day in taken:
            day += dt.timedelta(days=1)
        out[item] = dt.datetime.combine(day, clock, tz).astimezone(dt.timezone.utc)
        day += dt.timedelta(days=1)
    return out


def sh(*cmd, check=True):
    r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    out = (r.stdout + r.stderr).strip()
    if check and r.returncode != 0:
        sys.exit(f"{' '.join(cmd)} failed:\n{out}")
    return out


def uploaded_line(out):
    return next((ln for ln in out.splitlines() if ln.startswith("uploaded")), out.splitlines()[-1])


def youtube_ids(slug):
    path = ROOT / "episodes" / slug / "published.yaml"
    data = (yaml.safe_load(path.read_text()) if path.exists() else None) or []
    return {e["item"]: e["id"] for e in data if e["platform"] == "youtube" and e.get("id")}


def mark_scheduled(slug, times):
    path = ROOT / "episodes" / slug / "published.yaml"
    data = yaml.safe_load(path.read_text())
    for e in data:
        if e["platform"] == "youtube" and e["item"] in times and e.get("state") == "private":
            e["state"], e["publish_at"] = "scheduled", iso(times[e["item"]])
    path.write_text(yaml.safe_dump(data, sort_keys=False, allow_unicode=True))


def iso(t):
    return t.astimezone(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def note_idea(idea, slug, times, tz):
    readme = IDEAS / idea / "README.md"
    if not readme.exists():
        print(f"warning: {readme} not found; not noting the schedule there")
        return
    days = sorted({t.astimezone(tz).date() for t in times.values()})
    line = (f"- Scheduled {days[0]} to {days[-1]} as videos/episodes/{slug}/ (release.yaml); "
            "the release job replaces this line with the links once everything is out.\n")
    text = readme.read_text()
    readme.write_text(text + ("" if text.endswith("\n") else "\n") + line)
    subprocess.run(["uv", "run", "scripts/build_index.py"], cwd=IDEAS.parent, capture_output=True)
    print(f"noted the schedule in {readme}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("slug")
    ap.add_argument("--start", type=dt.date.fromisoformat, help="first possible day (default tomorrow)")
    ap.add_argument("--time", default="10:00", help="local time of day to release (default 10:00)")
    ap.add_argument("--tz", help="IANA timezone (default the laptop's)")
    ap.add_argument("--idea", help="idea folder in ../ideas to note the schedule in")
    ap.add_argument("--share-days", action="store_true", help="allow days other episodes already use")
    ap.add_argument("--dry-run", action="store_true", help="print the plan; upload and write nothing")
    a = ap.parse_args()

    ep = ROOT / "episodes" / a.slug
    episode = yaml.safe_load((ep / "episode.yaml").read_text())
    if episode.get("status") != "publish":
        sys.exit(f"{a.slug} has status {episode.get('status')!r}; it must be 'publish' (finish approved)")
    if (ep / "release.yaml").exists():
        sys.exit(f"{ep / 'release.yaml'} already exists; edit it by hand to change the plan")
    if a.idea and not (IDEAS / a.idea / "README.md").exists():
        sys.exit(f"no idea folder {IDEAS / a.idea}")

    tz = ZoneInfo(a.tz) if a.tz else local_tz()
    start = a.start or (dt.datetime.now(tz).date() + dt.timedelta(days=1))
    clock = dt.time.fromisoformat(a.time)
    has_long = "long" in yaml.safe_load((ep / "metadata.yaml").read_text())
    items = (["long"] if has_long else []) + list(episode.get("shorts") or [])
    times = plan_times(items, start, clock, tz, set() if a.share_days else taken_days(a.slug, tz))
    if min(times.values()) <= dt.datetime.now(dt.timezone.utc) + dt.timedelta(minutes=30):
        sys.exit("the first release time is less than 30 minutes away; pick a later --start or --time")
    for item, t in times.items():
        print(f"{item:8} {t.astimezone(tz):%a %Y-%m-%d %H:%M %Z}")
    if a.dry_run:
        return

    accounts = sh("uv", "run", "scripts/check_accounts.py", check=False)
    bad = [ln for ln in accounts.splitlines() if ln.startswith(("FAIL", "todo"))]
    if bad:
        sys.exit("fix these accounts first:\n" + "\n".join(bad))

    have = youtube_ids(a.slug)
    if has_long and "long" not in have:
        print(sh("uv", "run", "scripts/publish_prep.py", a.slug).splitlines()[-1])
        print(uploaded_line(sh("uv", "run", "scripts/post_youtube.py", "upload", f"out/{a.slug}/publish/long.json")))
    # Rerun now that the long-form link exists, so the short payloads get it.
    prep = sh("uv", "run", "scripts/publish_prep.py", a.slug)
    if "all checks passed" not in prep:
        sys.exit(prep)
    for item in items:
        if item != "long" and item not in youtube_ids(a.slug):
            out = sh("uv", "run", "scripts/post_youtube.py", "upload", f"out/{a.slug}/publish/{item}.json")
            print(uploaded_line(out))
    ids = youtube_ids(a.slug)
    for item in items:
        print(sh("uv", "run", "scripts/post_youtube.py", "publish", "--at", iso(times[item]), "--", ids[item]))
    mark_scheduled(a.slug, times)

    plan = {"push": "main", "platforms": PLATFORMS, "at": {k: iso(v) for k, v in times.items()}}
    header = ("# Release plan written by scripts/schedule_release.py, read by scripts/release_due.py.\n"
              "# Times are UTC. YouTube publishes on its own schedule. Once each time has passed the\n"
              "# job does the rest: at the first time it pushes `push` (a commit, or main), and at\n"
              "# each short it posts to every platform in `platforms` that published.yaml lacks.\n")
    (ep / "release.yaml").write_text(header + yaml.safe_dump(plan, sort_keys=False))
    print(f"wrote {ep / 'release.yaml'}")
    if a.idea:
        note_idea(a.idea, a.slug, times, tz)
    print(json.dumps({"scheduled": a.slug, "first": iso(min(times.values())), "last": iso(max(times.values()))}))


if __name__ == "__main__":
    main()
