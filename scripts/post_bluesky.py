"""Post a short to Bluesky as a video post.

    uv run scripts/post_bluesky.py out/<slug>/publish/short1.json [--dry-run]

Publishes immediately: run only after the user approves this item for Bluesky.
Config: ~/.config/math-videos/bluesky.json with handle and app_password (Settings ->
Privacy and security -> App passwords; never the account password). Video posts need a
verified email on the account.
"""

import argparse

from mathvid.publish import conf, load_payload, record, video_size

MAX_GRAPHEMES = 300


def text_for(p):
    """Title plus the caption's hashtags, as rich text so the tags are clickable."""
    from atproto import client_utils

    tags = [w.strip(".,!?") for w in p["caption"].split() if w.startswith("#")]
    tb = client_utils.TextBuilder().text(f"{p['title']}.")
    used = len(p["title"]) + 1
    for t in tags:
        if used + len(t) + 1 > MAX_GRAPHEMES:
            break
        tb.text(" ").tag(t, t.lstrip("#"))
        used += len(t) + 1
    return tb


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("payload")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    p, slug, item = load_payload(a.payload)
    if p["kind"] != "short":
        raise SystemExit("Bluesky is for shorts.")
    text = text_for(p)
    w, h = video_size(p["video"])
    if a.dry_run:
        print(f"bluesky: {item} ({p['video']}, {w}x{h})\ntext: {text.build_text()}")
        return

    from atproto import Client, models

    c = conf("bluesky", required=["handle", "app_password"])
    client = Client()
    client.login(c["handle"], c["app_password"])
    with open(p["video"], "rb") as f:
        resp = client.send_video(text=text, video=f.read(), video_alt=p["title"],
                                 video_aspect_ratio=models.AppBskyEmbedDefs.AspectRatio(width=w, height=h))
    rkey = resp.uri.rsplit("/", 1)[-1]
    url = f"https://bsky.app/profile/{c['handle']}/post/{rkey}"
    record(slug, "bluesky", item, "public", id=resp.uri, url=url)
    print(f"Bluesky post published: {url}")


if __name__ == "__main__":
    main()
