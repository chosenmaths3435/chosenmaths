"""A number line that zooms smoothly, for "zoom in on this point" animations.

The visible range is two ValueTrackers, so animating them zooms and pans:

    zl = ZoomLine(1.0, 1.5, length=12, center=DOWN * 0.5)
    d = zl.dot(1.414, color=SECONDARY)          # starts hidden
    self.add(zl, d)
    self.play(d.show.animate.set_value(1))      # drop the dot in
    self.play(zl.zoom_to(1.41, 1.42))           # everything follows

Tick spacing and labels adapt to the range. Do not move a ZoomLine after building it;
place it with `center`.
"""

import math as _m

import numpy as np
from manim import (
    DOWN,
    LEFT,
    RIGHT,
    UP,
    PI,
    ArcBetweenPoints,
    Circle,
    Dot,
    Line,
    ValueTracker,
    VGroup,
    VMobject,
    always_redraw,
)

from mathvid.style import FG, MUTED, text

_STEPS = (1, 2, 5)


def _step_for(span, max_labels):
    k = _m.floor(_m.log10(span)) - 1
    while True:
        for s in _STEPS:
            step = s * 10.0**k
            if span / step <= max_labels:
                return step, s
        k += 1


class ZoomLine(VGroup):
    def __init__(self, lo, hi, length=12.0, center=np.zeros(3), label_size=24,
                 max_labels=7, color=MUTED):
        super().__init__()
        self.lo, self.hi = ValueTracker(lo), ValueTracker(hi)
        self.length = length
        self.origin = np.array(center, dtype=float)
        self.label_size = label_size
        self.max_labels = max_labels
        self.color = color
        self._labels = {}
        # Dots made with `hole=` vanish within this screen distance of the hole.
        # Set it to 0 to show every dot, then animate it up when the hole appears.
        self.hole_r = ValueTracker(0.16)
        self.line = Line(self.origin + LEFT * length / 2, self.origin + RIGHT * length / 2,
                         color=color, stroke_width=3)
        self.ticks = always_redraw(self._draw_ticks)
        self.add(self.line, self.ticks)

    # coordinates -------------------------------------------------------------

    def u(self, x):
        """Screen offset of x from the line's center, in scene units."""
        lo, hi = self.lo.get_value(), self.hi.get_value()
        return ((x - lo) / (hi - lo) - 0.5) * self.length

    def p(self, x):
        return self.origin + RIGHT * self.u(x)

    def on_screen(self, x, margin=0.0):
        return abs(self.u(x)) <= self.length / 2 + margin

    def zoom_to(self, lo, hi):
        """Animations that move the visible range to [lo, hi]. Use in self.play(*...)."""
        return [self.lo.animate.set_value(lo), self.hi.animate.set_value(hi)]

    def set_range(self, lo, hi):
        self.lo.set_value(lo)
        self.hi.set_value(hi)

    # ticks -------------------------------------------------------------------

    def _label(self, s):
        if s not in self._labels:
            self._labels[s] = text(s, size=self.label_size, color=self.color)
        return self._labels[s].copy()

    def _draw_ticks(self):
        lo, hi = self.lo.get_value(), self.hi.get_value()
        span = hi - lo
        step, lead = _step_for(span, self.max_labels)
        decimals = max(0, -_m.floor(_m.log10(step) + 1e-9))
        minor = step / (5 if lead in (2, 5) else 10)
        g = VGroup()
        i0, i1 = _m.ceil(lo / minor - 1e-9), _m.floor(hi / minor + 1e-9)
        for i in range(i0, i1 + 1):
            x = i * minor
            major = abs(x / step - round(x / step)) < 1e-6
            h = 0.22 if major else 0.1
            p = self.p(x)
            g.add(Line(p + DOWN * h / 2, p + UP * h / 2, color=self.color,
                       stroke_width=3 if major else 2))
            if major:
                g.add(self._label(f"{x:.{decimals}f}").next_to(p, DOWN, buff=0.22))
        return g

    # things on the line --------------------------------------------------------

    def dot(self, x, color=FG, radius=0.08, hole=None, lift=0.6):
        """A dot at x that follows the zoom. Starts hidden: animate `.show` to 1.

        If `hole` is given, the dot shrinks as it nears that point on screen and
        disappears within `self.hole_r` of it, so a hollow ring there stays empty.
        """
        show = ValueTracker(0)

        def draw():
            d = Dot(radius=radius, color=color)
            a = show.get_value()
            r = radius
            hr = self.hole_r.get_value()
            if hole is not None and hr > 0:
                dist = abs(self.u(x) - self.u(hole))
                if dist < hr:
                    a = 0
                r = min(radius, max(0.012, 0.45 * (dist - 0.6 * hr)))
            d.scale(r / radius).move_to(self.p(x) + UP * (1 - show.get_value()) * lift)
            if not self.on_screen(x, 0.05) or a <= 0:
                d.set_opacity(0)
            else:
                d.set_opacity(min(1, a))
            return d

        m = always_redraw(draw)
        m.show = show
        return m

    def arc(self, x1, x2, up=True, color=FG, angle=0.75 * PI, width=2, opacity=0.5):
        """A faint arc from x1 to x2 above (or below) the line. Hidden while either end
        is off screen. Animate `.show` from 0 to 1 to draw it."""
        show = ValueTracker(0)

        def draw():
            a, b = self.p(x1), self.p(x2)
            s = show.get_value()
            if s <= 0 or not (self.on_screen(x1) and self.on_screen(x2)) or np.linalg.norm(b - a) < 0.08:
                return VMobject()
            arc = ArcBetweenPoints(a, b, angle=-angle if up == (x2 > x1) else angle,
                                   color=color, stroke_width=width, stroke_opacity=opacity)
            if s < 1:
                arc.pointwise_become_partial(arc, 0, s)
            return arc

        m = always_redraw(draw)
        m.show = show
        return m

    def ring(self, x, radius=0.13, color=FG, width=3):
        """A hollow circle marking a point (a hole) on the line; follows the zoom."""
        return always_redraw(lambda: Circle(radius=radius, color=color, stroke_width=width)
                             .move_to(self.p(x)))


class RealLine(VGroup):
    """A plain, static number line with integer ticks.

    Place it with `y` and `x0` (screen x of the middle of the range) and do not move it
    afterward: `p(v)` maps a value to its screen point. `labels` maps a value to a TeX
    label; by default every integer in range is labelled.
    """

    def __init__(self, lo=-3.5, hi=3.5, length=12.0, y=0.0, x0=0.0, ticks=True, size=26,
                 color=FG, stroke=4, labels=None, label_color=MUTED):
        from mathvid.style import math

        super().__init__()
        self.lo, self.hi, self.length, self.y, self.x0 = lo, hi, length, y, x0
        self.line = Line(self.p(lo), self.p(hi), color=color, stroke_width=stroke)
        self.ticks, self.labels = VGroup(), VGroup()
        if ticks:
            if labels is None:
                labels = {k: str(k) for k in range(_m.ceil(lo), _m.floor(hi) + 1)}
            for v, s in labels.items():
                self.ticks.add(Line(self.p(v) + UP * 0.1, self.p(v) + DOWN * 0.1, color=color,
                                    stroke_width=3))
                self.labels.add(math(s, size=size, color=label_color).next_to(self.p(v), DOWN, 0.2))
        self.add(self.line, self.ticks, self.labels)

    def p(self, v):
        x = self.x0 + (v - (self.lo + self.hi) / 2) / (self.hi - self.lo) * self.length
        return np.array([x, self.y, 0.0])
