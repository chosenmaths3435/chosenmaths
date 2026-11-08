"""Bring an episode's live posts in line with its metadata.yaml.

    uv run scripts/edit_posts.py <slug> [--only youtube|facebook|instagram] [--dry-run]

YouTube: the long-form gets the metadata's tags and its live description minus any
production lines (narration, source links); each Short's description becomes the
short's caption. Facebook: each reel's description becomes the caption. Instagram's API
cannot edit captions, so this prints them for pasting in the app. Threads and Bluesky
posts cannot be edited at all.

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
from mathvid.publish import conf, long_url, short_caption  # noqa: E402

PRODUCTION = re.compile(r"^(Animation source and script|Narration):.*$\n?", re.M)


def entries(slug, platform):
    data = yaml.safe_load((ROOT / "episodes" / slug / "published.yaml").read_text()) or []
    out = {}
    for e in data:
        if e.get("platform") == platform and e.get("id"):
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
            desc = re.sub(r"\n{3,}", "\n\n", PRODUCTION.sub("", cur["description"])).strip()
            snip.update(description=desc, tags=meta["long"].get("tags", []))
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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("slug")
    ap.add_argument("--only", choices=["youtube", "facebook", "instagram"])
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    meta = yaml.safe_load((ROOT / "episodes" / a.slug / "metadata.yaml").read_text())
    url = long_url(a.slug)
    if not url:
        raise SystemExit("No long-form YouTube video in published.yaml.")
    if a.only in (None, "youtube"):
        youtube(a.slug, meta, url, a.dry_run)
    if a.only in (None, "facebook"):
        facebook(a.slug, meta, url, a.dry_run)
    if a.only in (None, "instagram"):
        instagram(a.slug, meta, url)


if __name__ == "__main__":
    main()
