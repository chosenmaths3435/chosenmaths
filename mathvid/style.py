"""Shared visual style. Every episode imports from here so videos look like one channel.

Change the palette here, not in episode code.
"""

from manim import (
    DOWN,
    UP,
    FadeIn,
    FadeOut,
    MathTex,
    Tex,
    TexTemplate,
    Text,
    VGroup,
    config,
)

# Palette: dark background, warm accents. Named by role, not hue, so episodes say
# what a color means ("the thing we are tracking") rather than which color it is.
BG = "#14161B"
FG = "#E8E6E3"  # default text and strokes
MUTED = "#8A8F98"  # secondary text, axes, grid
PRIMARY = "#F2B33D"  # the main object of attention
SECONDARY = "#4FB0C6"  # the second object, or the "other side"
TERTIARY = "#C678DD"
GOOD = "#7BC67B"  # true, accepted, converges
BAD = "#E06C75"  # false, rejected, diverges

FONT = "Source Sans 3"

config.background_color = BG

TEX = TexTemplate()
TEX.add_to_preamble(r"\usepackage{amsmath,amssymb,mathtools}")


def text(s, size=36, color=FG, weight="NORMAL", **kw):
    return Text(s, font=FONT, font_size=size, color=color, weight=weight, **kw)


def math(*s, size=44, color=FG, **kw):
    return MathTex(*s, font_size=size, color=color, tex_template=TEX, **kw)


def tex(*s, size=40, color=FG, **kw):
    return Tex(*s, font_size=size, color=color, tex_template=TEX, **kw)


def title_card(scene, title, subtitle=None):
    """Opening title. Keep it under 2 seconds: the hook comes before it, not after."""
    t = text(title, size=56, weight="BOLD")
    group = VGroup(t)
    if subtitle:
        group.add(text(subtitle, size=30, color=MUTED).next_to(t, DOWN))
    group.move_to(UP * 0.3)
    scene.play(FadeIn(group, shift=UP * 0.2), run_time=0.8)
    scene.wait(0.8)
    scene.play(FadeOut(group), run_time=0.4)
