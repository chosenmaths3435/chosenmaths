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

# Safe area: platforms overlay UI on vertical video (buttons, channel name, description).
# Keep important content inside these bounds in portrait.
#
# Portrait, top to bottom (frame is 14.2 units tall):
#   top 1.6 units      platform UI (search, tabs)
#   content            between SAFE_TOP and SAFE_BOTTOM
#   caption band       burned-in captions, centered at CAPTION_FROM_BOTTOM
#   bottom ~2.8 units  platform UI (description, music, buttons)
SAFE_TOP = FH / 2 - (1.6 if PORTRAIT else 0.4)
SAFE_BOTTOM = -FH / 2 + (4.0 if PORTRAIT else 0.4)
SAFE_X = FW / 2 - (0.6 if PORTRAIT else 0.5)

# Fraction of the frame height from the bottom edge to the caption center (portrait).
# scripts/finish.py reads this to place burned-in captions.
CAPTION_FROM_BOTTOM = 0.24
