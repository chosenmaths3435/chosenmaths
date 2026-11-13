"""Upload to YouTube and publish when approved.

    uv run scripts/post_youtube.py upload out/<slug>/publish/long.json [--dry-run]
    uv run scripts/post_youtube.py publish <video_id> [--at 2026-11-10T15:00:00Z]

`upload` always creates a PRIVATE video (plus thumbnail and captions for long-form) and
records it in episodes/<slug>/published.yaml. Nothing is visible until `publish`, which
makes it public now or schedules it with --at. Check the private upload in YouTube Studio
in between.

Credentials live outside the repo, in ~/.config/math-videos/:
    youtube_client_secret.json   OAuth client (Desktop app) from Google Cloud Console
    youtube_token.json           written on first run after you approve in the browser
"""

import argparse
import datetime as dt
import json
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
CONF = Path.home() / ".config" / "math-videos"
SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube.force-ssl",  # captions.insert needs this
]
EDUCATION = "27"


def client():
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build

    secret, token = CONF / "youtube_client_secret.json", CONF / "youtube_token.json"
    creds = Credentials.from_authorized_user_file(token, SCOPES) if token.exists() else None
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    if not creds or not creds.valid:
        if not secret.exists():
            sys.exit(f"Missing {secret}. See the video-publish skill for one-time setup.")
        creds = InstalledAppFlow.from_client_secrets_file(secret, SCOPES).run_local_server(port=0)
    CONF.mkdir(parents=True, exist_ok=True)
    token.write_text(creds.to_json())
    token.chmod(0o600)
    return build("youtube", "v3", credentials=creds)


def body_for(p):
    if p["kind"] == "long":
        snippet = {"title": p["title"], "description": p["description"], "tags": p.get("tags", []),
                   "categoryId": EDUCATION, "defaultLanguage": "en", "defaultAudioLanguage": "en"}
    else:
        snippet = {"title": p["title"], "description": p["caption"], "categoryId": EDUCATION,
                   "defaultLanguage": "en", "defaultAudioLanguage": "en"}
    # YouTube does not require disclosure for a clone of the creator's own voice
    # (support.google.com/youtube/answer/14328491), so the flag stays off unless the
    # payload says otherwise via youtube_synthetic.
    status = {"privacyStatus": "private", "selfDeclaredMadeForKids": bool(p.get("made_for_kids", False)),
              "containsSyntheticMedia": bool(p.get("youtube_synthetic", False)), "embeddable": True}
    return {"snippet": snippet, "status": status}


def record(slug, entry):
    path = ROOT / "episodes" / slug / "published.yaml"
    data = yaml.safe_load(path.read_text()) if path.exists() else []
    data = data or []
    data.append(entry)
    path.write_text(yaml.safe_dump(data, sort_keys=False, allow_unicode=True))


def upload(payload_path, dry_run):
    from googleapiclient.http import MediaFileUpload

    payload_path = Path(payload_path).resolve()
    p = json.loads(payload_path.read_text())
    slug = payload_path.parent.parent.name
    name = payload_path.stem
    body = body_for(p)
    if dry_run:
        print(json.dumps(body, indent=2, ensure_ascii=False))
        print("files:", p["video"], p.get("thumbnail"), p.get("captions"))
        return

    yt = client()
    req = yt.videos().insert(part="snippet,status", body=body,
                             media_body=MediaFileUpload(p["video"], chunksize=8 * 1024 * 1024, resumable=True))
    resp = None
    while resp is None:
        status, resp = req.next_chunk()
        if status:
            print(f"uploading {name}: {status.progress() * 100:.0f}%", flush=True)
    vid = resp["id"]
    print(f"uploaded {name} as private: https://youtu.be/{vid}")

    if p.get("thumbnail"):
        yt.thumbnails().set(videoId=vid, media_body=MediaFileUpload(p["thumbnail"])).execute()
        print("thumbnail set")
    if p.get("captions"):
        yt.captions().insert(part="snippet", body={"snippet": {"videoId": vid, "language": "en", "name": "English"}},
                             media_body=MediaFileUpload(p["captions"], mimetype="application/octet-stream")).execute()
        print("captions uploaded")

    record(slug, {"platform": "youtube", "item": name, "id": vid, "url": f"https://youtu.be/{vid}",
                  "state": "private", "at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")})


def publish(video_id, at):
    yt = client()
    cur = yt.videos().list(part="status", id=video_id).execute()["items"][0]["status"]
    status = {"privacyStatus": "private" if at else "public",
              "selfDeclaredMadeForKids": cur.get("selfDeclaredMadeForKids", False),
              "containsSyntheticMedia": cur.get("containsSyntheticMedia", False)}
    # An update replaces the whole status, so carry over what we don't mean to change.
    status.update({k: cur[k] for k in ("embeddable", "license", "publicStatsViewable") if k in cur})
    if at:
        status["publishAt"] = at
    yt.videos().update(part="status", body={"id": video_id, "status": status}).execute()
    print(f"https://youtu.be/{video_id} " + (f"scheduled for {at}" if at else "is now public"))


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    u = sub.add_parser("upload")
    u.add_argument("payload")
    u.add_argument("--dry-run", action="store_true")
    sub.add_parser("whoami", help="log in (first time opens a browser) and print the channel")
    pb = sub.add_parser("publish")
    pb.add_argument("video_id")
    pb.add_argument("--at", help="ISO 8601 UTC time to go public, e.g. 2026-11-10T15:00:00Z")
    a = ap.parse_args()
    if a.cmd == "whoami":
        ch = client().channels().list(part="snippet", mine=True).execute()["items"][0]["snippet"]
        print(f"logged in to YouTube channel: {ch['title']}")
    elif a.cmd == "upload":
        upload(a.payload, a.dry_run)
    else:
        publish(a.video_id, a.at)


if __name__ == "__main__":
    main()
