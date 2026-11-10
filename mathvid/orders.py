"""Pictures for orders: dotted lines of rationals, solid lines, cuts, left pieces, ticks.

    L = RatLine(-1, 3, unit=3.0, y=-1)     # rationals as dots, bigger denominators smaller
    L.p(Fraction(1, 2))                    # screen point of a value
    s = scissors().next_to(L.p(1.5), UP)   # a cut marker
    b = left_bar(x_end=1.2, y=0.5)         # a left piece drawn as a bar from the left edge
"""

from fractions import Fraction as Fr

import numpy as np
from manim import (
    DOWN,
    LEFT,
    PI,
    RIGHT,
    UP,
    Circle,
    Dot,
    Line,
    Rectangle,
    Text,
    Triangle,
    VGroup,
    VMobject,
)

from mathvid.style import BAD, BG, FG, GOOD, MUTED, math

LEFT_C = "#4FB0C6"  # the left piece of a cut (same hue as SECONDARY)
RIGHT_C = "#F2B33D"  # the right piece (same hue as PRIMARY)


def rats(lo, hi, qmax):
    """Rationals strictly between lo and hi with denominator at most qmax, sorted."""
    out = set()
    for q in range(1, qmax + 1):
        for p in range(int(np.floor(lo * q)) - 1, int(np.ceil(hi * q)) + 2):
            v = Fr(p, q)
            if lo < v < hi:
                out.add(v)
    return sorted(out)


def fr_tex(f):
    f = Fr(f)
    if f.denominator == 1:
        return str(f.numerator)
    sign = "-" if f < 0 else ""
    return rf"{sign}\frac{{{abs(f.numerator)}}}{{{f.denominator}}}"


class RatLine(VGroup):
    """A line of rational dots. Dots with bigger denominators are drawn smaller.

    `pieces` restricts the dots and the axis to a list of (a, b) spans. `vals` replaces
    the default set of rationals.
    """

    def __init__(self, lo, hi, unit, y=0.0, x0=0.0, qmax=8, pieces=None, r=0.085,
                 color=FG, axis_color=MUTED, vals=None, axis=True):
        super().__init__()
        self.mid, self.unit, self.y, self.x0 = (lo + hi) / 2, unit, y, x0
        self.lo, self.hi = lo, hi
        spans = pieces or [(lo, hi)]
        self.axis = VGroup(*[Line(self.p(a), self.p(b), color=axis_color, stroke_width=3)
                             for a, b in spans]) if axis else VGroup()
        if vals is None:
            vals = set()
            for a, b in spans:
                vals |= set(rats(a, b, qmax))
        self.by = {v: Dot(self.p(v), radius=r * Fr(v).denominator ** -0.35, color=color)
                   for v in sorted(vals)}
        self.dots = VGroup(*self.by.values())
        self.add(self.axis, self.dots)

    def p(self, v):
        return np.array([self.x0 + (float(v) - self.mid) * self.unit, self.y, 0.0])

    def x(self, v):
        return self.p(v)[0]

    def hollow(self, v, r=0.08):
        return hollow_at(self.p(v), r)

    def numbers(self, vals, size=30, color=MUTED, buff=0.26):
        return VGroup(*[math(fr_tex(v), size=size, color=color).next_to(self.p(v), DOWN, buff=buff)
                        for v in vals])

    def left_of(self, c, strict=True):
        return VGroup(*[d for v, d in self.by.items() if (v < c if strict else v <= c)])

    def right_of(self, c, strict=False):
        return VGroup(*[d for v, d in self.by.items() if (v > c if strict else v >= c)])


def hollow_at(p, r=0.08, color=FG):
    return Circle(radius=r, color=color, stroke_width=2.5, fill_color=BG, fill_opacity=1).move_to(p)


def tips(x_left, x_right, y, color=MUTED, size=0.13):
    """Arrowheads at both ends of a line: it keeps going."""
    tri = Triangle(color=color, fill_opacity=1, stroke_width=0).scale(size)
    return VGroup(tri.copy().rotate(PI / 2).move_to([x_left, y, 0]),
                  tri.copy().rotate(-PI / 2).move_to([x_right, y, 0]))


def solid_line(x0, x1, y=0.0, color=FG, width=6, arrows=True):
    """A real line: a solid stroke, with arrowheads if it runs on forever."""
    ln = Line([x0, y, 0], [x1, y, 0], color=color, stroke_width=width)
    g = VGroup(ln)
    g.line = ln
    if arrows:
        g.tips = tips(x0 - 0.12, x1 + 0.12, y, color=color, size=0.15)
        g.add(g.tips)
    return g


def scissors(size=64, color=FG):
    """A scissors glyph with the blades pointing down, for marking a cut."""
    s = Text("\u2702", font="DejaVu Sans", font_size=size, color=color)
    return s.rotate(-PI / 2)


def cut_mark(x, y, height=0.9, color=FG):
    """A short dashed vertical line through the axis at x: where the cut falls."""
    from manim import DashedLine
    return DashedLine([x, y - height / 2, 0], [x, y + height / 2, 0], color=color,
                      stroke_width=3, dash_length=0.08)


def left_bar(x_end, y, x_start=-6.9, color=LEFT_C, height=0.2, arrow=True):
    """A left piece drawn as a bar running off the left edge to x_end."""
    r = Rectangle(width=max(0.01, x_end - x_start), height=height, stroke_width=0,
                  fill_color=color, fill_opacity=0.9)
    r.move_to([(x_start + x_end) / 2, y, 0])
    g = VGroup(r)
    g.rect = r
    if arrow:
        tri = Triangle(color=color, fill_opacity=0.9, stroke_width=0).scale(0.16).rotate(PI / 2)
        tri.move_to([x_start - 0.1, y, 0])
        g.add(tri)
    g.x_end = x_end
    return g


def tick(mob=None, at=None, color=GOOD, s=1.0):
    """A check mark, left of mob or at a point."""
    p = at if at is not None else mob.get_left() + LEFT * 0.45
    pts = [p + s * np.array(v) for v in ([-0.16, 0.0, 0], [-0.04, -0.14, 0], [0.2, 0.18, 0])]
    return VMobject(color=color, stroke_width=6).set_points_as_corners(pts)


def cross(at, color=BAD, s=0.16, width=6):
    a = Line(at + s * (UP + LEFT), at + s * (DOWN + RIGHT), color=color, stroke_width=width)
    b = Line(at + s * (UP + RIGHT), at + s * (DOWN + LEFT), color=color, stroke_width=width)
    return VGroup(a, b)
