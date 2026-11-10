"""Post a short to Bluesky as a video post.

    uv run scripts/post_bluesky.py out/<slug>/publish/short1.json [--dry-run]

Publishes immediately: run only after the user approves this item for Bluesky.
Credentials: BSKY_HANDLE and BSKY_PASSWORD in videos/.env (or ~/.config/math-videos/
bluesky.json with handle and app_password). Use an app password (Settings -> Privacy
and security -> App passwords), never the account password. Video posts need a
verified email on the account.
"""

import argparse

from mathvid.publish import env_or_conf, load_payload, record, video_size

MAX_GRAPHEMES = 300


def text_for(p):
    """The shared caption (hook, link to the long-form, hashtags) as rich text, so the link
    and tags are clickable. Hashtags that would pass the length limit are dropped."""
    from atproto import client_utils

    from mathvid.publish import POINTER

    if p.get("long_url"):
        pre, _, post = POINTER.partition("{url}")
        tb = client_utils.TextBuilder().text(f"{p['hook']}\n\n{pre}").link(p["long_url"], p["long_url"])
        used = len(p["hook"]) + 2 + len(POINTER.format(url=p["long_url"]))
        if post:
            tb.text(post)
    elif p.get("caption", "").startswith(p["hook"]) and POINTER.split("{")[0] not in p["caption"]:
        tb, used = client_utils.TextBuilder().text(p["hook"]), len(p["hook"])  # shorts-only episode
    else:
        raise SystemExit("Payload has no long_url; rerun publish_prep.py after the YouTube upload.")
    sep = "\n\n"
    for t in p.get("hashtags", []):
        if used + len(sep) + len(t) > MAX_GRAPHEMES:
            break
        tb.text(sep).tag(t, t.lstrip("#"))
        used += len(sep) + len(t)
        sep = " "
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

    c = env_or_conf("bluesky", {"handle": "BSKY_HANDLE", "app_password": "BSKY_PASSWORD"})
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
