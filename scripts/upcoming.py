"""Print the release schedule of every episode that has a release.yaml, in local time.

    uv run scripts/upcoming.py          # items not yet out everywhere
    uv run scripts/upcoming.py --all    # also items already out

Each row is one item (long-form or short) with its planned time and title. The last column
says where it stands: YouTube from published.yaml (scheduled or public), the other
platforms as posted, failed, or waiting. Reads files only; contacts no platform.
"""

import argparse
import datetime as dt
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent


def parse(at):
    when = at if isinstance(at, dt.datetime) else dt.datetime.fromisoformat(str(at).replace("Z", "+00:00"))
    return when if when.tzinfo else when.replace(tzinfo=dt.timezone.utc)


def load(path, default):
    return yaml.safe_load(path.read_text()) if path.exists() else default


def rows():
    for plan_file in sorted(ROOT.glob("episodes/*/release.yaml")):
        ep = plan_file.parent
        plan = yaml.safe_load(plan_file.read_text())
        meta = load(ep / "metadata.yaml", {})
        entries = load(ep / "published.yaml", []) or []
        for item, at in plan["at"].items():
            when = parse(at)
            section = meta.get("long", {}) if item == "long" else meta.get("shorts", {}).get(item, {})
            state = {e["platform"]: e.get("state", "?") for e in entries if e["item"] == item}
            yt = state.get("youtube", "not uploaded")
            if yt == "scheduled" and when <= dt.datetime.now(dt.timezone.utc):
                yt = "public"  # YouTube flips it on its own; published.yaml catches up at wrap-up
            others = [] if item == "long" else plan.get("platforms", [])
            posted = [p for p in others if state.get(p) == "public"]
            failed = [p for p in others if state.get(p) == "failed"]
            parts = [f"youtube {yt}"]
            if others:
                parts.append("others posted" if len(posted) == len(others)
                             else f"{len(posted)}/{len(others)} others posted")
            if failed:
                parts.append("FAILED: " + ", ".join(failed))
            done = yt == "public" and len(posted) == len(others)
            yield when, ep.name, item, section.get("title", ""), "; ".join(parts), done


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--all", action="store_true", help="also list items already out everywhere")
    a = ap.parse_args()
    found = sorted(r for r in rows() if a.all or not r[5])
    if not found:
        print("nothing scheduled")
        return
    last_day = None
    for when, slug, item, title, status, _ in found:
        local = when.astimezone()
        day = local.strftime("%a %b %d")
        if day != last_day:
            print(f"\n{day}")
            last_day = day
        print(f"  {local:%H:%M}  {slug:<22} {item:<7} {status:<40} {title}")


if __name__ == "__main__":
    main()
