"""Aspect ratio setup. Import this module before defining scenes.

MV_ASPECT=landscape (default) renders 16:9 for YouTube long-form.
MV_ASPECT=portrait renders 9:16 for Shorts, Reels, and TikTok.

Landscape frames are 8 units tall; portrait frames are 8 units wide. So a mobject sized to
fit a landscape frame's height also fits across a portrait frame. Scenes that need
different layouts branch on PORTRAIT.
"""

import os

from manim import config

ASPECT = os.environ.get("MV_ASPECT", "landscape")
PORTRAIT = ASPECT == "portrait"

# Keep the resolution chosen by the quality flag (-ql, -qh, ...), just rotate it.
if PORTRAIT:
    if config.pixel_width > config.pixel_height:
        config.pixel_width, config.pixel_height = config.pixel_height, config.pixel_width
    config.frame_width = 8.0
    config.frame_height = 8.0 * 16 / 9
else:
    config.frame_height = 8.0
    config.frame_width = 8.0 * 16 / 9

FW, FH = config.frame_width, config.frame_height

# Safe area: platforms overlay UI on vertical video (captions, buttons, channel name).
# Keep important content inside these bounds in portrait.
SAFE_TOP = FH / 2 - (1.6 if PORTRAIT else 0.4)
SAFE_BOTTOM = -FH / 2 + (3.2 if PORTRAIT else 0.4)
SAFE_X = FW / 2 - (0.6 if PORTRAIT else 0.5)
