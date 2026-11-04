"""Post shorts to Instagram Reels, Facebook Reels, and Threads (Meta APIs).

    uv run scripts/post_meta.py setup                 # once, and when tokens expire
    uv run scripts/post_meta.py instagram out/<slug>/publish/short1.json [--dry-run]
    uv run scripts/post_meta.py facebook  out/<slug>/publish/short1.json [--dry-run]
    uv run scripts/post_meta.py threads   out/<slug>/publish/short1.json --video-url URL [--dry-run]

Every posting command publishes immediately, so run it only after the user has approved
that item for that platform. Threads cannot take a file upload; it fetches the video from
a public URL (the skill uses a GitHub release asset).

Config: ~/.config/math-videos/meta.json. You fill in app_id, app_secret, user_token
(short-lived, from Graph API Explorer) and threads_token (from the Threads use case's
token generator); `setup` exchanges them for long-lived tokens and finds the Page and
Instagram IDs.
"""

import argparse
import time

import requests

from mathvid.publish import conf, load_payload, record, save_conf

GRAPH = "https://graph.facebook.com/{v}"
RUPLOAD = "https://rupload.facebook.com"
THREADS = "https://graph.threads.net/v1.0"


def get(url, **params):
    r = requests.get(url, params=params, timeout=60)
    if not r.ok:
        raise SystemExit(f"GET {url.split('?')[0]} failed {r.status_code}: {r.text[:500]}")
    return r.json()


def post(url, data=None, **kw):
    r = requests.post(url, data=data, timeout=600, **kw)
    if not r.ok:
        raise SystemExit(f"POST {url.split('?')[0]} failed {r.status_code}: {r.text[:500]}")
    return r.json()


def setup():
    c = conf("meta", required=["app_id", "app_secret"])
    v = c.setdefault("graph_version", "v24.0")
    g = GRAPH.format(v=v)
    if c.get("user_token"):
        long = get(f"{g}/oauth/access_token", grant_type="fb_exchange_token", client_id=c["app_id"],
                   client_secret=c["app_secret"], fb_exchange_token=c["user_token"])["access_token"]
        pages = get(f"{g}/me/accounts", access_token=long)["data"]
        if not pages:
            raise SystemExit("No Facebook Pages found for this token. Check pages_show_list permission.")
        if len(pages) > 1 and not c.get("page_id"):
            names = ", ".join(f"{p['name']} ({p['id']})" for p in pages)
            raise SystemExit(f"Several Pages: {names}. Put the right one in meta.json as page_id and rerun.")
        page = next(p for p in pages if p["id"] == c.get("page_id", pages[0]["id"]))
        c["page_id"], c["page_token"] = page["id"], page["access_token"]  # non-expiring page token
        ig = get(f"{g}/{page['id']}", fields="instagram_business_account", access_token=page["access_token"])
        if "instagram_business_account" not in ig:
            raise SystemExit("The Page has no linked Instagram professional account. Link it, then rerun.")
        c["ig_user_id"] = ig["instagram_business_account"]["id"]
        del c["user_token"]
        print(f"Facebook Page {page['name']} and Instagram account {c['ig_user_id']} ready")
    if c.get("threads_token") and not c.get("threads_long_token"):
        r = get("https://graph.threads.net/access_token", grant_type="th_exchange_token",
                client_secret=c["app_secret"], access_token=c["threads_token"])
        c["threads_long_token"], c["threads_token_at"] = r["access_token"], int(time.time())
        del c["threads_token"]
        print("Threads token ready (refreshed automatically when used)")
    save_conf("meta", c)


def threads_token(c):
    """Threads long-lived tokens last 60 days; refresh once they are over 30 days old."""
    if time.time() - c.get("threads_token_at", 0) > 30 * 86400:
        r = get("https://graph.threads.net/refresh_access_token", grant_type="th_refresh_token",
                access_token=c["threads_long_token"])
        c["threads_long_token"], c["threads_token_at"] = r["access_token"], int(time.time())
        save_conf("meta", c)
    return c["threads_long_token"]


def rupload(url, token, path):
    data = open(path, "rb").read()
    return post(url, data=data, headers={"Authorization": f"OAuth {token}", "offset": "0",
                                         "file_size": str(len(data))})


def wait_until(check, what, timeout=600):
    start = time.time()
    while time.time() - start < timeout:
        status = check()
        if status in ("FINISHED", "PUBLISHED", "ready"):
            return
        if status in ("ERROR", "EXPIRED", "error"):
            raise SystemExit(f"{what} processing failed: {status}")
        time.sleep(5)
    raise SystemExit(f"{what} still processing after {timeout}s")


def instagram(p, slug, item, c, ai):
    g = GRAPH.format(v=c.get("graph_version", "v24.0"))
    tok = c["page_token"]
    params = {"media_type": "REELS", "upload_type": "resumable", "caption": p["caption"],
              "share_to_feed": "true", "access_token": tok}
    if ai:
        params["is_ai_generated"] = "true"
    cont = post(f"{g}/{c['ig_user_id']}/media", data=params)
    rupload(f"{RUPLOAD}/ig-api-upload/{c.get('graph_version', 'v24.0')}/{cont['id']}", tok, p["video"])
    wait_until(lambda: get(f"{g}/{cont['id']}", fields="status_code", access_token=tok)["status_code"],
               "Instagram")
    media = post(f"{g}/{c['ig_user_id']}/media_publish", data={"creation_id": cont["id"], "access_token": tok})
    link = get(f"{g}/{media['id']}", fields="permalink", access_token=tok).get("permalink")
    record(slug, "instagram", item, "public", id=media["id"], url=link)
    print(f"Instagram Reel posted: {link}")


def facebook(p, slug, item, c, ai):
    v = c.get("graph_version", "v24.0")
    g = GRAPH.format(v=v)
    tok, page = c["page_token"], c["page_id"]
    start = post(f"{g}/{page}/video_reels", data={"upload_phase": "start", "access_token": tok})
    rupload(f"{RUPLOAD}/video-upload/{v}/{start['video_id']}", tok, p["video"])
    fin = {"upload_phase": "finish", "video_id": start["video_id"], "video_state": "PUBLISHED",
           "description": p["caption"], "access_token": tok}
    if ai:
        fin["is_ai_generated"] = "true"
    post(f"{g}/{page}/video_reels", data=fin)
    url = f"https://www.facebook.com/reel/{start['video_id']}"
    record(slug, "facebook", item, "public", id=start["video_id"], url=url)
    print(f"Facebook Reel posted: {url}")


def threads(p, slug, item, c, ai, video_url):
    tok = threads_token(c)
    params = {"media_type": "VIDEO", "video_url": video_url, "text": p["caption"][:500], "access_token": tok}
    if ai:
        params["is_made_with_ai"] = "true"
    cont = post(f"{THREADS}/me/threads", data=params)
    wait_until(lambda: get(f"{THREADS}/{cont['id']}", fields="status", access_token=tok)["status"], "Threads")
    pub = post(f"{THREADS}/me/threads_publish", data={"creation_id": cont["id"], "access_token": tok})
    link = get(f"{THREADS}/{pub['id']}", fields="permalink", access_token=tok).get("permalink")
    record(slug, "threads", item, "public", id=pub["id"], url=link)
    print(f"Threads post published: {link}")


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("setup")
    for name in ("instagram", "facebook", "threads"):
        s = sub.add_parser(name)
        s.add_argument("payload")
        s.add_argument("--dry-run", action="store_true")
        s.add_argument("--no-ai-label", action="store_true",
                       help="omit the AI-generated flag (only if the API rejects it)")
        if name == "threads":
            s.add_argument("--video-url", required=True, help="public URL of the video file")
    a = ap.parse_args()
    if a.cmd == "setup":
        return setup()

    p, slug, item = load_payload(a.payload)
    if p["kind"] != "short":
        raise SystemExit("Meta posting is for shorts; the long-form video goes to YouTube.")
    ai = p.get("ai_disclosure", True) and not a.no_ai_label
    if a.dry_run:
        print(f"{a.cmd}: {item} ({p['video']})\ncaption: {p['caption']}\nai label: {ai}")
        return
    c = conf("meta", required=["page_token", "page_id", "ig_user_id"] if a.cmd != "threads"
             else ["threads_long_token", "app_secret"])
    if a.cmd == "instagram":
        instagram(p, slug, item, c, ai)
    elif a.cmd == "facebook":
        facebook(p, slug, item, c, ai)
    else:
        threads(p, slug, item, c, ai, a.video_url)


if __name__ == "__main__":
    main()
