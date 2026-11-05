"""Render the profile picture and banners at each platform's size.

    uv run branding/render.py "Channel Name" ["tagline"]

Writes PNGs to out/branding/.
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TARGETS = {
    "ProfilePic": (1024, 1024, "profile.png"),
    "BannerYouTube": (2560, 1440, "banner-youtube.png"),
    "BannerBluesky": (3000, 1000, "banner-bluesky.png"),
    "CoverFacebook": (1640, 624, "cover-facebook.png"),
}


def main():
    env = {**os.environ}
    if len(sys.argv) > 1:
        env["MV_CHANNEL_NAME"] = sys.argv[1]
    if len(sys.argv) > 2:
        env["MV_TAGLINE"] = sys.argv[2]
    out = ROOT / "out" / "branding"
    out.mkdir(parents=True, exist_ok=True)
    media = ROOT / "media" / "branding"
    for scene, (w, h, name) in TARGETS.items():
        subprocess.run(["uv", "run", "manim", "-v", "WARNING", "-s", "-r", f"{w},{h}", "--media_dir", str(media),
                        str(ROOT / "branding" / "brand.py"), scene], check=True, env=env, cwd=ROOT)
        png = sorted((media / "images" / "brand").glob(f"{scene}*.png"))[-1]
        shutil.copy(png, out / name)
        print(out / name)


if __name__ == "__main__":
    main()
