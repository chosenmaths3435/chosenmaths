"""Shared helpers for the platform upload scripts in scripts/post_*.py."""

import datetime as dt
import json
import stat
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
CONF = Path.home() / ".config" / "math-videos"


def load_payload(path):
    """Read a payload written by scripts/publish_prep.py. Returns (payload, slug, item)."""
    path = Path(path).resolve()
    return json.loads(path.read_text()), path.parent.parent.name, path.stem


def conf(name, required=()):
    """Load ~/.config/math-videos/<name>.json, refusing files other users can read."""
    path = CONF / f"{name}.json"
    if not path.exists():
        sys.exit(f"Missing {path}. See docs/publish-setup.md in the private repo.")
    if path.stat().st_mode & (stat.S_IRWXG | stat.S_IRWXO):
        sys.exit(f"{path} is readable by other users; run: chmod 600 {path}")
    data = json.loads(path.read_text())
    missing = [k for k in required if not data.get(k)]
    if missing:
        sys.exit(f"{path} is missing: {', '.join(missing)}")
    return data


def save_conf(name, data):
    CONF.mkdir(parents=True, exist_ok=True)
    CONF.chmod(0o700)
    path = CONF / f"{name}.json"
    path.write_text(json.dumps(data, indent=2) + "\n")
    path.chmod(0o600)


def record(slug, platform, item, state, id=None, url=None, note=None):
    """Append an entry to episodes/<slug>/published.yaml."""
    path = ROOT / "episodes" / slug / "published.yaml"
    data = (yaml.safe_load(path.read_text()) if path.exists() else None) or []
    entry = {"platform": platform, "item": item, "state": state, "id": id, "url": url,
             "at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")}
    if note:
        entry["note"] = note
    data.append({k: v for k, v in entry.items() if v is not None})
    path.write_text(yaml.safe_dump(data, sort_keys=False, allow_unicode=True))


def video_size(path):
    import subprocess

    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                          "stream=width,height", "-of", "csv=p=0", str(path)],
                         capture_output=True, text=True, check=True).stdout.strip()
    w, h = out.split(",")
    return int(w), int(h)


def env_or_conf(name, mapping):
    """Credentials from ~/.config/math-videos/<name>.json, else from videos/.env.

    mapping: {config_key: ENV_VAR}. Exits with a clear message if any are missing.
    """
    from dotenv import dotenv_values

    data = json.loads((CONF / f"{name}.json").read_text()) if (CONF / f"{name}.json").exists() else {}
    env = dotenv_values(ROOT / ".env")
    out = {k: data.get(k) or env.get(var) for k, var in mapping.items()}
    missing = [mapping[k] for k, v in out.items() if not v]
    if missing:
        sys.exit(f"Missing {', '.join(missing)} in videos/.env (or {CONF / (name + '.json')}).")
    return out


POINTER = "Full video on YouTube: {url}"


def long_url(slug):
    """The long-form video's YouTube link from published.yaml, or None before it is uploaded."""
    path = ROOT / "episodes" / slug / "published.yaml"
    data = (yaml.safe_load(path.read_text()) if path.exists() else None) or []
    urls = [e["url"] for e in data if e.get("platform") == "youtube" and e.get("item") == "long"]
    return urls[-1] if urls else None


def short_caption(short, url):
    """A short's caption on every platform: the hook, a link to the long-form, the hashtags."""
    parts = [short["caption"].strip(), POINTER.format(url=url), short.get("hashtags", "").strip()]
    return "\n\n".join(p for p in parts if p)
