"""Channel profile picture and banners, as Manim stills.

Render everything with: uv run branding/render.py "Channel Name" ["tagline"]
(this file is the scene source; render.py picks the pixel sizes per platform).

Set MV_CHANNEL_NAME / MV_TAGLINE to change the text. The frame is always 8 units tall;
its width follows the pixel aspect ratio chosen on the command line.
"""

import os

import numpy as np
from manim import (
    DOWN,
    LEFT,
    RIGHT,
    UP,
    Axes,
    Polygon,
    Scene,
    VGroup,
    VMobject,
    config,
)

from mathvid.style import BG, MUTED, PRIMARY, SECONDARY, text

config.frame_height = 8.0
config.frame_width = 8.0 * config.pixel_width / config.pixel_height
config.background_color = BG

NAME = os.environ.get("MV_CHANNEL_NAME", "Channel Name")
TAGLINE = os.environ.get("MV_TAGLINE", "math and computer science, animated")


def mark(side=4.4, k=2.0, stroke=10):
    """The logo: a square split by y = t^k into the area under the curve and to its left."""
    ax = Axes(x_range=[0, 1], y_range=[0, 1], x_length=side, y_length=side, tips=False,
              axis_config={"stroke_opacity": 0})
    pts = [ax.c2p(t, t ** k) for t in np.linspace(0, 1, 120)]
    under = Polygon(ax.c2p(0, 0), *pts, ax.c2p(1, 0), stroke_width=0, fill_color=PRIMARY, fill_opacity=1)
    left = Polygon(ax.c2p(0, 0), *pts, ax.c2p(0, 1), stroke_width=0, fill_color=SECONDARY, fill_opacity=1)
    # The curve is a gap in the background color: it separates the pieces cleanly and
    # anything past the square's edge disappears into the background.
    curve = VMobject(stroke_color=BG, stroke_width=stroke).set_points_smoothly(pts)
    g = VGroup(left, under, curve)
    g.move_to(ax.get_center())
    return g


def curve_field(width, height, n=14):
    """Faint family of curves y = t^k across the whole frame, as background texture."""
    ax = Axes(x_range=[0, 1], y_range=[0, 1], x_length=width, y_length=height, tips=False,
              axis_config={"stroke_opacity": 0})
    curves = VGroup()
    for i, k in enumerate(np.geomspace(0.18, 5.5, n)):
        c = ax.plot(lambda t, k=k: t ** k, x_range=[0, 1], stroke_width=2.5, color=MUTED)
        c.set_stroke(opacity=0.10 + 0.06 * np.sin(np.pi * i / (n - 1)))
        curves.add(c)
    return curves


class ProfilePic(Scene):
    """Square; platforms crop it to a circle, so the mark stays inside the inscribed circle."""

    def construct(self):
        self.add(mark(side=5.0))  # corners at 3.54 units from center: inside the circle crop (r = 4)


def banner(scene, safe_w, safe_h):
    """Mark + name + tagline, fitted inside the centered safe box, over the curve field."""
    # Oversized so the point where the curves meet, (1, 1), falls off the top right.
    scene.add(curve_field(config.frame_width * 1.7, config.frame_height * 1.7).move_to([0, 0, 0]))
    m = mark(side=1.0, stroke=6)
    name = text(NAME, size=96, weight="BOLD")
    tag = text(TAGLINE, size=44, color=MUTED)
    words = VGroup(name, tag).arrange(DOWN, aligned_edge=LEFT, buff=0.18)
    m.scale_to_fit_height(words.height)
    lockup = VGroup(m, words).arrange(RIGHT, buff=0.45)
    lockup.scale_to_fit_width(min(lockup.width, safe_w * 0.92))
    if lockup.height > safe_h * 0.92:
        lockup.scale_to_fit_height(safe_h * 0.92)
    lockup.move_to([0, 0, 0])
    scene.add(lockup)


class BannerYouTube(Scene):
    """2560x1440. Every device shows at least the middle 1546x423 px."""

    def construct(self):
        banner(self, config.frame_width * 1546 / 2560, config.frame_height * 423 / 1440)


class BannerBluesky(Scene):
    """3000x1000. The avatar overlaps the lower left, so keep to the center."""

    def construct(self):
        banner(self, config.frame_width * 0.5, config.frame_height * 0.55)


class CoverFacebook(Scene):
    """1640x624. Phones crop the sides, and the avatar overlaps the lower left on desktop."""

    def construct(self):
        banner(self, config.frame_width * 0.55, config.frame_height * 0.5)
