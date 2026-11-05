"""Check every publishing account can log in. Read-only: posts nothing.

    uv run scripts/check_accounts.py
"""

import json

import requests

from mathvid.publish import CONF, env_or_conf

OK, BAD, TODO = "ok  ", "FAIL", "todo"


def youtube():
    if not (CONF / "youtube_client_secret.json").exists():
        return BAD, "no youtube_client_secret.json"
    if not (CONF / "youtube_token.json").exists():
        return TODO, "credentials in place; log in once with: uv run scripts/post_youtube.py whoami"
    from post_youtube import client

    ch = client().channels().list(part="snippet", mine=True).execute()["items"][0]["snippet"]
    return OK, f"channel {ch['title']}"


def meta():
    if not (CONF / "meta.json").exists():
        return [(n, TODO, "run post_meta.py setup") for n in ("facebook", "instagram", "threads")]
    c = json.loads((CONF / "meta.json").read_text())
    rows = []
    g = f"https://graph.facebook.com/{c.get('graph_version', 'v24.0')}"
    if c.get("page_token"):
        page = requests.get(f"{g}/{c['page_id']}", params={"fields": "name", "access_token": c["page_token"]}).json()
        rows.append(("facebook", *((OK, f"Page {page['name']}") if "name" in page else (BAD, page.get("error")))))
        ig = requests.get(f"{g}/{c['ig_user_id']}", params={"fields": "username", "access_token": c["page_token"]}).json()
        rows.append(("instagram", *((OK, f"@{ig['username']}") if "username" in ig else (BAD, ig.get("error")))))
    else:
        rows += [("facebook", TODO, "run post_meta.py setup"), ("instagram", TODO, "run post_meta.py setup")]
    if c.get("threads_long_token"):
        th = requests.get("https://graph.threads.net/v1.0/me",
                          params={"fields": "username", "access_token": c["threads_long_token"]}).json()
        rows.append(("threads", *((OK, f"@{th['username']}") if "username" in th else (BAD, th.get("error")))))
    else:
        rows.append(("threads", TODO, "run post_meta.py setup"))
    return rows


def bluesky():
    from atproto import Client

    c = env_or_conf("bluesky", {"handle": "BSKY_HANDLE", "app_password": "BSKY_PASSWORD"})
    client = Client()
    prof = client.login(c["handle"], c["app_password"])
    sess = client.com.atproto.server.get_session()
    note = "" if getattr(sess, "email_confirmed", True) else " (email NOT verified: video posts will fail)"
    return OK, f"@{prof.handle}{note}"


def main():
    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).parent))
    rows = []
    for name, fn in (("youtube", youtube), ("bluesky", bluesky)):
        try:
            rows.append((name, *fn()))
        except SystemExit as e:
            rows.append((name, BAD, str(e)))
        except Exception as e:  # report every platform even if one breaks
            rows.append((name, BAD, f"{type(e).__name__}: {e}"))
    try:
        rows[1:1] = meta()
    except Exception as e:
        rows.insert(1, ("meta", BAD, f"{type(e).__name__}: {e}"))
    for name, status, detail in rows:
        print(f"{status}  {name:10} {detail}")
    print("tiktok      off the roster")


if __name__ == "__main__":
    main()
