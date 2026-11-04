"""Send a short to your TikTok drafts (inbox). You finish and publish it in the TikTok app.

    uv run scripts/post_tiktok.py auth-url               # once; prints a login link
    uv run scripts/post_tiktok.py auth-code '<redirected URL>'
    uv run scripts/post_tiktok.py draft out/<slug>/publish/short1.json [--dry-run]
    uv run scripts/post_tiktok.py status <publish_id>

TikTok only allows public API posts from apps it has audited, so this uses the "upload
to inbox" flow (scope video.upload): the video appears as a notification in the TikTok
app, where you add the caption, turn on the AI-generated label, and post.

Config: ~/.config/math-videos/tiktok.json with client_key, client_secret, redirect_uri
(exactly as registered in the TikTok developer portal). Tokens are added by auth-code
and refreshed automatically (access tokens last 24h, refresh tokens a year).
"""

import argparse
import base64
import hashlib
import os
import secrets
import time
import urllib.parse

import requests

from mathvid.publish import conf, load_payload, record, save_conf

API = "https://open.tiktokapis.com/v2"
SCOPES = "user.info.basic,video.upload"


def auth_url():
    c = conf("tiktok", required=["client_key", "redirect_uri"])
    verifier = base64.urlsafe_b64encode(os.urandom(48)).decode().rstrip("=")
    c["pkce_verifier"], c["oauth_state"] = verifier, secrets.token_urlsafe(16)
    save_conf("tiktok", c)
    q = {"client_key": c["client_key"], "scope": SCOPES, "response_type": "code",
         "redirect_uri": c["redirect_uri"], "state": c["oauth_state"],
         # TikTok's PKCE uses a hex-encoded SHA-256 of the verifier.
         "code_challenge": hashlib.sha256(verifier.encode()).hexdigest(), "code_challenge_method": "S256"}
    print("Open this link, log in with the channel's TikTok account, and approve.")
    print("Then copy the full URL you land on (even if the page fails to load) and run")
    print("  uv run scripts/post_tiktok.py auth-code '<that URL>'\n")
    print("https://www.tiktok.com/v2/auth/authorize/?" + urllib.parse.urlencode(q))


def auth_code(redirected):
    c = conf("tiktok", required=["client_key", "client_secret", "redirect_uri", "pkce_verifier"])
    q = urllib.parse.parse_qs(urllib.parse.urlparse(redirected).query)
    if q.get("state", [""])[0] != c.get("oauth_state"):
        raise SystemExit("State mismatch: run auth-url again and use the newest link.")
    if "code" not in q:
        raise SystemExit(f"No code in that URL: {q.get('error_description', q)}")
    tok = token_request(c, grant_type="authorization_code", code=q["code"][0], redirect_uri=c["redirect_uri"],
                        code_verifier=c["pkce_verifier"])
    for k in ("pkce_verifier", "oauth_state"):
        c.pop(k, None)
    store(c, tok)
    print("TikTok connected.")


def token_request(c, **data):
    r = requests.post(f"{API}/oauth/token/", data={"client_key": c["client_key"],
                                                   "client_secret": c["client_secret"], **data},
                      headers={"Content-Type": "application/x-www-form-urlencoded"}, timeout=60)
    body = r.json()
    if not r.ok or "access_token" not in body:
        raise SystemExit(f"TikTok token request failed: {body}")
    return body


def store(c, tok):
    now = int(time.time())
    c.update(access_token=tok["access_token"], refresh_token=tok["refresh_token"],
             access_expires=now + int(tok["expires_in"]) - 300,
             refresh_expires=now + int(tok["refresh_expires_in"]) - 300)
    save_conf("tiktok", c)


def access_token():
    c = conf("tiktok", required=["client_key", "client_secret", "refresh_token"])
    if time.time() > c.get("refresh_expires", 0):
        raise SystemExit("TikTok login expired; run auth-url and auth-code again.")
    if time.time() > c.get("access_expires", 0):
        store(c, token_request(c, grant_type="refresh_token", refresh_token=c["refresh_token"]))
    return c["access_token"]


def api(path, token, body):
    r = requests.post(f"{API}{path}", json=body, timeout=60,
                      headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json; charset=UTF-8"})
    data = r.json()
    if data.get("error", {}).get("code") not in (None, "ok"):
        raise SystemExit(f"TikTok {path} failed: {data['error']}")
    return data["data"]


def draft(p, slug, item):
    tok = access_token()
    size = os.path.getsize(p["video"])
    # Files up to 64 MB may go in one chunk; larger ones in 10 MB chunks (last one absorbs the rest).
    chunk = size if size <= 64 * 2**20 else 10 * 2**20
    count = max(1, size // chunk)
    init = api("/post/publish/inbox/video/init/", tok, {"source_info": {
        "source": "FILE_UPLOAD", "video_size": size, "chunk_size": chunk, "total_chunk_count": count}})
    with open(p["video"], "rb") as f:
        for i in range(count):
            start = i * chunk
            end = size - 1 if i == count - 1 else start + chunk - 1
            f.seek(start)
            part = f.read(end - start + 1)
            r = requests.put(init["upload_url"], data=part, timeout=600, headers={
                "Content-Type": "video/mp4", "Content-Length": str(len(part)),
                "Content-Range": f"bytes {start}-{end}/{size}"})
            if r.status_code not in (200, 201, 206):
                raise SystemExit(f"TikTok upload chunk {i} failed {r.status_code}: {r.text[:300]}")
    record(slug, "tiktok", item, "draft", id=init["publish_id"], note="finish in the TikTok app")
    print(f"Sent to TikTok drafts (publish_id {init['publish_id']}).")
    print("Now in the TikTok app: open the notification, paste the caption, turn on the AI-generated "
          "label (More options), and post.")
    print(f"Caption:\n{p['caption']}")


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("auth-url")
    s = sub.add_parser("auth-code")
    s.add_argument("url")
    s = sub.add_parser("draft")
    s.add_argument("payload")
    s.add_argument("--dry-run", action="store_true")
    s = sub.add_parser("status")
    s.add_argument("publish_id")
    a = ap.parse_args()

    if a.cmd == "auth-url":
        auth_url()
    elif a.cmd == "auth-code":
        auth_code(a.url)
    elif a.cmd == "status":
        print(api("/post/publish/status/fetch/", access_token(), {"publish_id": a.publish_id}))
    else:
        p, slug, item = load_payload(a.payload)
        if p["kind"] != "short":
            raise SystemExit("TikTok is for shorts.")
        if a.dry_run:
            print(f"tiktok draft: {item} ({p['video']}, {os.path.getsize(p['video']) / 2**20:.1f} MB)")
            print(f"caption to paste in the app:\n{p['caption']}")
            return
        draft(p, slug, item)


if __name__ == "__main__":
    main()
