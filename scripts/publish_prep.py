"""Turn an episode's metadata into ready-to-post payloads, and check platform limits.

    uv run scripts/publish_prep.py <slug>

Reads episodes/<slug>/metadata.yaml and out/<slug>/ (chapters.txt, videos, captions,
thumbnail). Writes out/<slug>/publish/<name>.json, one per upload, and prints any limit
violations. Exits non-zero if a payload is invalid, so nothing gets posted half-checked.

Short captions link to the long-form video, so the short payloads are only written once
the long-form is uploaded (it is in published.yaml): run this, upload long.json, run it
again.
"""

import argparse
import json
import re
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from mathvid.publish import long_url, short_caption  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent

# Platform limits (characters unless noted). Checked 2026-11; adjust if platforms change.
LIMITS = {
    "youtube_title": 100,
    "youtube_description": 5000,
    "youtube_tags_total": 500,
    "short_caption": 2200,  # TikTok and Instagram
    "threads_text": 500,
    "bluesky_text": 300,  # graphemes; hashtags that do not fit are dropped, the rest must fit
    "short_hashtags": 30,  # Instagram
    "short_seconds": 60,  # our target; platforms allow more
}


def duration(path):
    import subprocess

    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                          str(path)], capture_output=True, text=True, check=True).stdout
    return float(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("slug")
    ap.add_argument("--repo-url", default="", help="fills {repo_url} if the description uses it")
    ap.add_argument("--out-dir", help="read finished files from here instead of out/<slug> (for testing)")
    a = ap.parse_args()

    ep = ROOT / "episodes" / a.slug
    out = Path(a.out_dir).resolve() if a.out_dir else ROOT / "out" / a.slug
    meta = yaml.safe_load((ep / "metadata.yaml").read_text())
    episode = yaml.safe_load((ep / "episode.yaml").read_text())
    pub = out / "publish"
    pub.mkdir(parents=True, exist_ok=True)
    problems = []

    def need(path):
        if not path.exists():
            problems.append(f"missing file: {path}")
        return str(path)

    # Long-form
    long = meta["long"]
    chapters = (out / "chapters.txt").read_text().strip() if (out / "chapters.txt").exists() else ""
    if not chapters:
        problems.append("missing chapters.txt (run scripts/finish.py first)")
    desc = long["description"].replace("{chapters}", chapters).replace("{repo_url}", a.repo_url).strip()
    if "{" in desc:
        problems.append(f"unfilled placeholder in description: {re.findall(r'{\\w+}', desc)}")
    for name in episode.get("coauthors") or []:
        if name not in desc:
            problems.append(f"coauthor {name!r} not credited in the description")
    if len(long["title"]) > LIMITS["youtube_title"]:
        problems.append(f"youtube title is {len(long['title'])} chars (max {LIMITS['youtube_title']})")
    if len(desc) > LIMITS["youtube_description"]:
        problems.append(f"youtube description is {len(desc)} chars (max {LIMITS['youtube_description']})")
    if any(c in desc for c in "<>"):
        problems.append("youtube description contains < or >, which the API rejects")
    tags = long.get("tags", [])
    if sum(len(t) + (2 if " " in t else 0) + 1 for t in tags) > LIMITS["youtube_tags_total"]:
        problems.append("youtube tags exceed 500 characters in total")

    payloads = {"long": {
        "kind": "long",
        "title": long["title"],
        "description": desc,
        "tags": tags,
        "category": long.get("category", "Education"),
        "made_for_kids": bool(long.get("made_for_kids", False)),
        "ai_disclosure": bool(long.get("ai_disclosure", True)),
        "video": need(out / f"{a.slug}.mp4"),
        "thumbnail": need(out / "thumbnail.png"),
        "captions": need(out / f"{a.slug}.srt"),
    }}

    # Shorts
    url = long_url(a.slug)
    shorts = meta.get("shorts") or {}
    if shorts and not url:
        for name in shorts:
            (pub / f"{name}.json").unlink(missing_ok=True)
        print("shorts: waiting for the long-form, since their captions link to it. Upload long.json"
              " to YouTube, then run this again.")
        shorts = {}
    for name, s in shorts.items():
        if "#" in s["caption"]:
            problems.append(f"{name}: hashtags go in hashtags:, not in the caption")
        cap = short_caption(s, url)
        hook_and_link = short_caption({**s, "hashtags": ""}, url)
        if len(cap) > LIMITS["threads_text"]:
            problems.append(f"{name}: caption is {len(cap)} chars (Threads max {LIMITS['threads_text']})")
        if len(hook_and_link) > LIMITS["bluesky_text"]:
            problems.append(f"{name}: hook plus link is {len(hook_and_link)} chars (Bluesky max {LIMITS['bluesky_text']})")
        video = out / f"{name}.mp4"
        if len(cap) > LIMITS["short_caption"]:
            problems.append(f"{name}: caption is {len(cap)} chars (max {LIMITS['short_caption']})")
        if len(re.findall(r"#\w+", cap)) > LIMITS["short_hashtags"]:
            problems.append(f"{name}: more than {LIMITS['short_hashtags']} hashtags")
        if video.exists() and duration(video) > LIMITS["short_seconds"] + 0.5:
            problems.append(f"{name}: {duration(video):.0f}s is over the {LIMITS['short_seconds']}s target")
        payloads[name] = {
            "kind": "short",
            "title": s["title"],
            "caption": cap,
            "hook": s["caption"].strip(),
            "long_url": url,
            "hashtags": s.get("hashtags", "").split(),
            "ai_disclosure": bool(long.get("ai_disclosure", True)),
            "video": need(video),
            "captions": need(out / f"{name}.srt"),
        }
        cover = s.get("cover")
        if not cover or "at" not in cover:
            problems.append(f"{name}: no cover (set cover: at/text in metadata.yaml, then finish.py --only covers)")
        else:
            payloads[name]["cover"] = need(out / f"{name}-cover.jpg")
            payloads[name]["cover_at"] = float(cover["at"])

    for name, p in payloads.items():
        (pub / f"{name}.json").write_text(json.dumps(p, indent=2, ensure_ascii=False) + "\n")
    print(f"wrote {len(payloads)} payloads to {pub}/")
    if problems:
        print("PROBLEMS:")
        for p in problems:
            print("  -", p)
        sys.exit(1)
    print("all checks passed")


if __name__ == "__main__":
    main()
