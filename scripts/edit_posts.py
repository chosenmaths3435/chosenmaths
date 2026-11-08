"""Bring an episode's live posts in line with its metadata.yaml.

    uv run scripts/edit_posts.py <slug> [--only youtube|facebook|instagram] [--dry-run]
    uv run scripts/edit_posts.py <slug> --reply threads|bluesky [--dry-run]

YouTube: the long-form gets the metadata's description and tags (keeping the chapter
list from its live description); each Short's description becomes the short's caption. Facebook: each reel's description becomes the caption. Instagram's API
cannot edit captions, so this prints them for pasting in the app. Threads and Bluesky
posts cannot be edited at all; --reply posts the link to the long-form as a reply under
each of them instead (once: replies are recorded in published.yaml as <item>-link).

Edits are public, so run it only with the user's go-ahead.
"""

import argparse
import re
import sys
from pathlib import Path

import requests
import yaml

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
from mathvid.publish import (POINTER, conf, env_or_conf, long_description, long_url, record,  # noqa: E402
                             short_caption)

CHAPTER = re.compile(r"^\d+:\d\d(:\d\d)? .+$", re.M)


def entries(slug, platform, links=False):
    """Latest published.yaml entry per item; link replies only when links=True."""
    data = yaml.safe_load((ROOT / "episodes" / slug / "published.yaml").read_text()) or []
    out = {}
    for e in data:
        if e.get("platform") == platform and e.get("id") and (links or not e["item"].endswith("-link")):
            out[e["item"]] = e  # the latest entry per item wins
    return out


def youtube(slug, meta, url, dry):
    from post_youtube import client

    yt = None if dry else client()
    for item, e in entries(slug, "youtube").items():
        if dry:
            print(f"youtube {item} {e['url']}: would update", "description and tags" if item == "long" else
                  f"description to:\n{short_caption(meta['shorts'][item], url)}\n")
            continue
        cur = yt.videos().list(part="snippet", id=e["id"]).execute()["items"][0]["snippet"]
        snip = {k: cur[k] for k in ("title", "categoryId", "defaultLanguage", "defaultAudioLanguage") if k in cur}
        if item == "long":
            chapters = "\n".join(m.group(0) for m in CHAPTER.finditer(cur["description"]))
            if not chapters:
                raise SystemExit(f"youtube long: no chapter list found in the live description of {e['url']}")
            snip.update(description=long_description(meta["long"], chapters, slug), tags=meta["long"].get("tags", []))
        else:
            snip.update(description=short_caption(meta["shorts"][item], url), tags=cur.get("tags", []))
        if snip.get("description") == cur.get("description") and snip.get("tags", []) == cur.get("tags", []):
            print(f"youtube {item}: already up to date")
            continue
        yt.videos().update(part="snippet", body={"id": e["id"], "snippet": snip}).execute()
        print(f"youtube {item}: updated {e['url']}")


def facebook(slug, meta, url, dry):
    c = conf("meta")
    g = f"https://graph.facebook.com/{c.get('graph_version', 'v24.0')}"
    for item, e in entries(slug, "facebook").items():
        cap = short_caption(meta["shorts"][item], url)
        if dry:
            print(f"facebook {item} {e['url']}: would set description to:\n{cap}\n")
            continue
        r = requests.post(f"{g}/{e['id']}", data={"description": cap, "access_token": c["page_token"]}, timeout=60)
        if not r.ok:
            print(f"facebook {item}: FAILED {r.status_code} {r.text[:300]}")
        else:
            print(f"facebook {item}: updated {e['url']}")


def instagram(slug, meta, url):
    for item, e in entries(slug, "instagram").items():
        print(f"--- instagram {item}: {e['url']}\n{short_caption(meta['shorts'][item], url)}\n")


def reply(slug, platform, url, dry):
    """Reply under each short's post with the link to the long-form, if not done already."""
    posts = entries(slug, platform, links=True)
    text = POINTER.format(url=url)
    for item, e in posts.items():
        if item.endswith("-link"):
            continue
        if f"{item}-link" in posts:
            print(f"{platform} {item}: link reply already posted ({posts[item + '-link']['url']})")
            continue
        if dry:
            print(f"{platform} {item} {e['url']}: would reply: {text}")
            continue
        rid, rurl = (threads_reply if platform == "threads" else bluesky_reply)(e, text, url)
        record(slug, platform, f"{item}-link", "public", id=rid, url=rurl)
        print(f"{platform} {item}: replied {rurl}")


def threads_reply(e, text, url):
    from post_meta import THREADS, get, post, threads_token, wait_until

    c = conf("meta", required=["threads_long_token"])
    tok = threads_token(c)
    cont = post(f"{THREADS}/me/threads", data={"media_type": "TEXT", "text": text, "reply_to_id": e["id"],
                                                "access_token": tok})
    wait_until(lambda: get(f"{THREADS}/{cont['id']}", fields="status", access_token=tok)["status"], "Threads")
    pub = post(f"{THREADS}/me/threads_publish", data={"creation_id": cont["id"], "access_token": tok})
    link = get(f"{THREADS}/{pub['id']}", fields="permalink", access_token=tok).get("permalink")
    return pub["id"], link


def bluesky_reply(e, text, url):
    from atproto import Client, client_utils, models

    c = env_or_conf("bluesky", {"handle": "BSKY_HANDLE", "app_password": "BSKY_PASSWORD"})
    client = Client()
    client.login(c["handle"], c["app_password"])
    parent = client.get_posts([e["id"]]).posts[0]
    ref = models.create_strong_ref(parent)
    pre, _, post = POINTER.partition("{url}")
    tb = client_utils.TextBuilder().text(pre).link(url, url).text(post)
    resp = client.send_post(tb, reply_to=models.AppBskyFeedPost.ReplyRef(root=ref, parent=ref))
    return resp.uri, f"https://bsky.app/profile/{c['handle']}/post/{resp.uri.rsplit('/', 1)[-1]}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("slug")
    ap.add_argument("--only", choices=["youtube", "facebook", "instagram"])
    ap.add_argument("--reply", choices=["threads", "bluesky"],
                    help="reply under each post with the long-form link instead of editing")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    meta = yaml.safe_load((ROOT / "episodes" / a.slug / "metadata.yaml").read_text())
    url = long_url(a.slug)
    if not url:
        raise SystemExit("No long-form YouTube video in published.yaml.")
    if a.reply:
        return reply(a.slug, a.reply, url, a.dry_run)
    if a.only in (None, "youtube"):
        youtube(a.slug, meta, url, a.dry_run)
    if a.only in (None, "facebook"):
        facebook(a.slug, meta, url, a.dry_run)
    if a.only in (None, "instagram"):
        instagram(a.slug, meta, url)


if __name__ == "__main__":
    main()
