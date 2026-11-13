"""The popcorn function: continuous at every irrational, broken at every fraction.

Long-form scenes. Builders here are shared with shorts.py.
"""

from math import ceil, floor, gcd, log10, sqrt

import numpy as np
from manim import *
from manim_voiceover import VoiceoverScene

from mathvid import layout  # noqa: F401  must come before scene code runs
from mathvid.anim import rest, rt, wait_until
from mathvid.layout import FH, FW
from mathvid.numberline import ZoomLine
from mathvid.orders import cross, tick
from mathvid.script import Script
from mathvid.style import (BAD, BG, FG, GOOD, MUTED, PRIMARY, SECONDARY, TERTIARY, math, text,
                           title_card)
from mathvid.voice import get_speech_service

N = Script(__file__)

TITLE = "The popcorn function"
FRAC = SECONDARY   # the fractions (dots)
IRR = PRIMARY      # the irrationals (the glowing axis)
ROOT = 1 / sqrt(2)


# ---------------------------------------------------------------------------
# The popcorn plot
# ---------------------------------------------------------------------------


def freeze(scene):
    """Stop every updater on screen, so a final fade sees fixed shapes."""
    for m in scene.mobjects:
        m.clear_updaters()


def fractions_in(lo, hi, qmax):
    """Reduced fractions p/q in [lo, hi] (and in [0, 1]) with q <= qmax."""
    out = []
    lo, hi = max(lo, 0.0), min(hi, 1.0)
    for q in range(1, qmax + 1):
        p0 = max(0, ceil(lo * q - 1e-12))
        p1 = min(q, floor(hi * q + 1e-12))
        for p in range(p0, p1 + 1):
            if gcd(p, q) == 1:
                out.append((p, q))
    return out


UNIT_CIRCLE = Circle(radius=1.0).points.copy()


def disc_cloud(pts, color, opacity=1.0):
    """Many filled discs as one VMobject (fast to build and to draw).

    pts: list of (x, y, r)."""
    arr = np.array(pts, dtype=float)
    n = len(arr)
    base = np.repeat(UNIT_CIRCLE[None, :, :], n, axis=0)
    base = base * arr[:, 2][:, None, None]
    base[:, :, 0] += arr[:, 0][:, None]
    base[:, :, 1] += arr[:, 1][:, None]
    m = VMobject(stroke_width=0)
    m.set_points(base.reshape(-1, 3))
    m.set_fill(color, opacity=opacity)
    return m


def nice_step(span, max_labels=6):
    k = floor(log10(span)) - 1
    while True:
        for s in (1, 2, 5):
            step = s * 10.0 ** k
            if span / step <= max_labels:
                return step
        k += 1


class Popcorn(VGroup):
    """Thomae's function drawn as dots over a horizontal axis, with a zoomable view.

    The view is three trackers: `c` (center of the x range), `s` (log10 of the x span)
    and `t` (log10 of the top of the y range). Zoom with `pc.view(c, span, ytop)`, which
    returns animations; zooming in log space keeps a deep zoom smooth.

    Screen box: x from `left` to `right`, the axis at screen height `y0`, the top of the
    y range at `y1`.
    """

    def __init__(self, left=-6.4, right=6.4, y0=-2.6, y1=2.9, c=0.5, span=1.08, ytop=1.1,
                 target=420, qcap=1600, show_ticks=True, tick_size=24):
        super().__init__()
        self.left, self.right, self.y0, self.y1 = left, right, y0, y1
        self.c = ValueTracker(c)
        self.s = ValueTracker(log10(span))
        self.t = ValueTracker(log10(ytop))
        self.qshow = ValueTracker(10_000)   # dots with q above this are hidden
        self.alpha = ValueTracker(1.0)      # overall dot opacity
        self.qhl = ValueTracker(0)          # dots with q <= qhl are "poking out"
        self.hl_on = ValueTracker(0.0)      # how strongly to color them
        self.win = None                     # (lo, hi) trackers of a window, if any
        self.win_on = ValueTracker(0.0)
        self.target, self.qcap = target, qcap
        self.tick_size = tick_size
        self.tick_alpha = ValueTracker(1.0 if show_ticks else 0.0)
        self.glow = ValueTracker(0.0)
        self.axis = Line([left, y0, 0], [right, y0, 0], color=MUTED, stroke_width=3)
        self.glow_line = always_redraw(self._draw_glow)
        self.dots = always_redraw(self._draw_dots)
        self.ticks = always_redraw(self._draw_ticks)
        self.add(self.axis, self.glow_line, self.ticks, self.dots)

    # coordinates
    @property
    def span(self):
        return 10 ** self.s.get_value()

    @property
    def ytop(self):
        return 10 ** self.t.get_value()

    def lo_hi(self):
        c, sp = self.c.get_value(), self.span
        return c - sp / 2, c + sp / 2

    def X(self, x):
        c, sp = self.c.get_value(), self.span
        return (self.left + self.right) / 2 + (x - c) / sp * (self.right - self.left)

    def Y(self, y):
        return self.y0 + y / self.ytop * (self.y1 - self.y0)

    def P(self, x, y=0.0):
        return np.array([self.X(x), self.Y(y), 0.0])

    def view(self, c, span, ytop=None):
        anims = [self.c.animate.set_value(c), self.s.animate.set_value(log10(span))]
        if ytop is not None:
            anims.append(self.t.animate.set_value(log10(ytop)))
        return anims

    def set_view(self, c, span, ytop=None):
        self.c.set_value(c)
        self.s.set_value(log10(span))
        if ytop is not None:
            self.t.set_value(log10(ytop))

    def qmax(self):
        q = int(sqrt(self.target / (0.304 * self.span)))
        return max(12, min(self.qcap, q))

    # drawing
    def dot_color(self, p, q):
        x = p / q
        if self.win is not None and self.win_on.get_value() > 0.01:
            a, b = self.win[0].get_value(), self.win[1].get_value()
            if a <= x <= b and q > self.qhl.get_value():
                return interpolate_color(ManimColor(FRAC), ManimColor(GOOD), self.win_on.get_value())
        if q <= self.qhl.get_value():
            return interpolate_color(ManimColor(FRAC), ManimColor(BAD), self.hl_on.get_value())
        return FRAC

    def _draw_dots(self):
        g = VGroup()
        a = self.alpha.get_value()
        if a <= 0.01:
            return g
        lo, hi = self.lo_hi()
        top = self.ytop * 1.03
        qs = self.qshow.get_value()
        groups = {}
        for p, q in fractions_in(lo, hi, self.qmax()):
            v = 1 / q
            if v > top or q > qs + 1:
                continue
            o = a * min(1.0, max(0.0, qs + 1 - q))
            if o <= 0.01:
                continue
            h = self.Y(v) - self.y0
            r = min(0.075, max(0.011, 0.16 * h))
            key = (str(self.dot_color(p, q)), round(o, 2))
            groups.setdefault(key, []).append((self.X(p / q), self.Y(v), r))
        for (col, o), pts in groups.items():
            g.add(disc_cloud(pts, col, o))
        return g

    def _draw_glow(self):
        g = self.glow.get_value()
        ln = Line([self.left, self.y0, 0], [self.right, self.y0, 0], color=IRR, stroke_width=7)
        return ln.set_stroke(opacity=g)

    def _draw_ticks(self):
        g = VGroup()
        al = self.tick_alpha.get_value()
        if al <= 0.01:
            return g
        lo, hi = self.lo_hi()
        step = nice_step(hi - lo)
        dec = max(0, -floor(log10(step) + 1e-9))
        for i in range(ceil(lo / step - 1e-9), floor(hi / step + 1e-9) + 1):
            x = i * step
            px = self.X(x)
            g.add(Line([px, self.y0 + 0.08, 0], [px, self.y0 - 0.08, 0], color=MUTED, stroke_width=2))
            g.add(text(f"{x:.{dec}f}", size=self.tick_size, color=MUTED)
                  .move_to([px, self.y0 - 0.32, 0]))
        return g.set_opacity(al)

    # overlays that follow the view
    def band(self, ya, yb, color=PRIMARY, opacity=0.16):
        """A horizontal band between heights ya and yb (trackers)."""
        on = ValueTracker(0.0)

        def draw():
            o = on.get_value()
            y_lo, y_hi = self.Y(ya.get_value()), self.Y(yb.get_value())
            floor_y = self.y0 - 0.5          # below the axis, show only a sliver of the band
            ys = [y for y in (y_lo, y_hi) if y >= floor_y]
            y_lo = max(y_lo, floor_y)
            r = Rectangle(width=self.right - self.left, height=max(0.001, y_hi - y_lo),
                          stroke_width=0, fill_color=color, fill_opacity=opacity * o)
            r.move_to([(self.left + self.right) / 2, (y_lo + y_hi) / 2, 0])
            edges = VGroup(*[DashedLine([self.left, y, 0], [self.right, y, 0], color=color,
                                        stroke_width=2, dash_length=0.12).set_stroke(opacity=o)
                             for y in ys])
            return VGroup(r, edges)

        m = always_redraw(draw)
        m.on = on
        return m

    def window(self, xa, xb, color=GOOD, opacity=0.13, bottom=None, tint=True):
        """A vertical window between x values xa and xb (trackers)."""
        on = ValueTracker(0.0)
        self.win = (xa, xb) if tint else None
        self.win_on = on
        bot = self.y0 - 0.55 if bottom is None else bottom

        def draw():
            o = on.get_value()
            xl, xr = self.X(xa.get_value()), self.X(xb.get_value())
            xl, xr = max(xl, self.left), min(xr, self.right)
            r = Rectangle(width=max(0.001, xr - xl), height=self.y1 - bot + 0.2, stroke_width=0,
                          fill_color=color, fill_opacity=opacity * o)
            r.move_to([(xl + xr) / 2, (self.y1 + 0.2 + bot) / 2, 0])
            sides = VGroup(*[Line([x, bot, 0], [x, self.y1 + 0.2, 0], color=color, stroke_width=2.5)
                             .set_stroke(opacity=o) for x in (xl, xr)])
            return VGroup(r, sides)

        m = always_redraw(draw)
        m.on = on
        return m

    def marker(self, x, label=None, color=IRR, size=30):
        """A small triangle under the axis at x, with an optional label below it."""
        def draw():
            p = self.P(x)
            tri = Triangle(color=color, fill_opacity=1, stroke_width=0).scale(0.11)
            tri.move_to(p + DOWN * 0.62)
            g = VGroup(tri)
            if label:
                g.add(math(label, size=size, color=color).next_to(tri, DOWN, 0.12))
            return g

        return always_redraw(draw)

    def axis_red(self, xa, xb, on):
        """The axis between two x trackers drawn red: the irrationals there, at height 0."""
        def draw():
            xl, xr = max(self.X(xa.get_value()), self.left), min(self.X(xb.get_value()), self.right)
            ln = Line([xl, self.y0, 0], [max(xl + 0.001, xr), self.y0, 0], color=BAD, stroke_width=9)
            return ln.set_stroke(opacity=on.get_value())

        return always_redraw(draw)


def y_labels(pc, qs=(1, 2, 3), size=30):
    """Height labels 1, 1/2, 1/3, ... on the left edge (for the full view only)."""
    g = VGroup()
    for q in qs:
        s = "1" if q == 1 else rf"\frac{{1}}{{{q}}}"
        y = pc.Y(1 / q)
        g.add(VGroup(Line([pc.left - 0.08, y, 0], [pc.left + 0.08, y, 0], color=MUTED, stroke_width=2),
                     math(s, size=size, color=MUTED).move_to([pc.left - 0.45, y, 0])))
    return g


def rule_card(size=40):
    """The rule: p/q in lowest terms -> 1/q, irrational -> 0."""
    a = math(r"\tfrac{p}{q}\ \text{(lowest terms)}", r"\ \longmapsto\ ", r"\tfrac{1}{q}", size=size)
    b = math(r"\text{irrational}", r"\ \longmapsto\ ", r"0", size=size)
    a[2].set_color(FRAC)
    b[2].set_color(IRR)
    g = VGroup(a, b).arrange(DOWN, buff=0.3, aligned_edge=LEFT)
    return g


def question(size=44):
    return VGroup(text("continuous at every fraction,", size=size),
                  text("broken at every irrational?", size=size)).arrange(DOWN, buff=0.18)


# ---------------------------------------------------------------------------
# The countdown: nested intervals that dodge a list of fractions
# ---------------------------------------------------------------------------

# The list of fractions in [0, 1], by denominator.
LIST = [(0, 1), (1, 1)] + [(p, q) for q in range(2, 13) for p in range(1, q) if gcd(p, q) == 1]

TARGET = sqrt(2) - 1   # where this run of the countdown happens to close in


def pick_inside(a, b):
    """The smallest-denominator fraction strictly inside (a, b) that sits well inside it
    and close to TARGET, so the next interval can wrap around TARGET."""
    for q in range(1, 200000):
        c = round(TARGET * q)
        for p in (c - 1, c, c + 1):
            if p < 0 or gcd(p, q) != 1:
                continue
            m = p / q
            if a < m < b and abs(m - TARGET) < 0.25 * min(m - a, b - m):
                return p, q
    raise ValueError((a, b))


def countdown(steps=8):
    """Simulate the countdown. Each step: (listed fraction, interval after leaving it out,
    picked fraction, tight interval). The tight interval is strictly inside the trimmed one,
    contains TARGET, and leaves out the listed fraction."""
    a, b = 0.0, 1.0
    out = []
    for k in range(steps):
        p, q = LIST[k]
        r = p / q
        trimmed = a <= r <= b
        if trimmed:
            if r < TARGET:
                a = r + 0.12 * (TARGET - r) if r > 0 else 0.035
            else:
                b = r - 0.12 * (r - TARGET) if r < 1 else 0.965
        pp, pq = pick_inside(a, b)
        m = pp / pq
        room = min(m - a, b - m)
        w = 0.62 * room
        assert m - w < TARGET < m + w and a < m - w and m + w < b, (k, a, b, m, w)
        out.append(dict(r=(p, q), trimmed=trimmed, cut=(a, b), pick=(pp, pq), tight=(m - w, m + w)))
        a, b = m - w, m + w
    return out


def frac_tex(p, q):
    return str(p) if q == 1 else rf"\frac{{{p}}}{{{q}}}"


def list_row(n=10, size=40, buff=0.34):
    items = VGroup(*[math(frac_tex(*LIST[k]), size=size) for k in range(n)])
    dots = math(r"\cdots", size=size, color=MUTED)
    row = VGroup(*items, dots).arrange(RIGHT, buff=buff)
    row.items = items
    return row


def interval_mark(zl, a, b, color=PRIMARY, lift=0.32, width=7):
    """A closed interval [a, b] drawn just above a ZoomLine, following its zoom."""
    on = ValueTracker(0.0)

    def draw():
        pa, pb = zl.p(a.get_value()), zl.p(b.get_value())
        pa = pa + UP * lift
        pb = pb + UP * lift
        g = VGroup(Line(pa, pb, color=color, stroke_width=width),
                   Line(pa + DOWN * 0.16, pa + UP * 0.16, color=color, stroke_width=width - 2),
                   Line(pb + DOWN * 0.16, pb + UP * 0.16, color=color, stroke_width=width - 2))
        return g.set_stroke(opacity=on.get_value())

    m = always_redraw(draw)
    m.on = on
    return m


def run_steps(scene, zl, cur, steps, row, k0, k1, per, lab_pos, show_pick=True, zoom=True,
              label_size=30, pick_size=34):
    """Animate countdown steps k0..k1-1 quickly: cross the listed fraction (trimming the
    interval if it was inside), drop in the pick, tighten, and zoom to keep it in view."""
    old = []
    lab = None
    for k in range(k0, k1):
        st = steps[k]
        a, b = st["tight"]
        anims = []
        if k < len(row.items):
            anims.append(Create(cross(row.items[k].get_center(), s=0.2, width=5)))
        ca, cb = st["cut"]
        scene.play(*anims, cur[0].animate.set_value(ca), cur[1].animate.set_value(cb),
                   run_time=rt(per * 0.35))
        span = (b - a) * 3.2
        mid = (a + b) / 2
        new_lab = text(f"within 1/{k + 1}" if k else "within 1", size=label_size, color=PRIMARY)
        new_lab.move_to(lab_pos)
        z = zl.zoom_to(mid - span / 2, mid + span / 2) if zoom else []
        anims2 = [cur[0].animate.set_value(a), cur[1].animate.set_value(b), *z]
        if lab is None:
            anims2.append(FadeIn(new_lab))
        else:
            anims2.append(ReplacementTransform(lab, new_lab))
        scene.play(*anims2, run_time=rt(per * 0.65))
        lab = new_lab
    return lab


# ---------------------------------------------------------------------------
# s01 Hook
# ---------------------------------------------------------------------------


class S01Hook(VoiceoverScene):
    def construct(self):
        self.set_speech_service(get_speech_service())
        pc = Popcorn(y0=-2.7, y1=2.9)
        pc.qshow.set_value(0)
        ylab = y_labels(pc)
        irr = text("irrationals: continuous", size=32, color=IRR).move_to([3.6, -3.55, 0])
        fr = text("fractions: broken", size=32, color=BAD).move_to([3.6, 3.4, 0])
        with self.voiceover(text=N("s01.b1")) as tr:
            self.add(pc)
            self.play(FadeIn(ylab), pc.qshow.animate.set_value(40), run_time=rt(min(3.0, tr.duration * 0.5)),
                      rate_func=linear)
            self.play(pc.glow.animate.set_value(0.9), FadeIn(irr), run_time=0.8)
            wait_until(self, tr, "broken")
            pc.qhl.set_value(40)
            self.play(pc.hl_on.animate.set_value(1.0), FadeIn(fr), run_time=0.8)
            rest(self, tr)
        q = question(size=50).move_to(UP * 0.3)
        with self.voiceover(text=N("s01.b2")) as tr:
            self.play(FadeOut(VGroup(pc, ylab, irr, fr)), run_time=0.6)
            self.play(FadeIn(q, shift=UP * 0.2), run_time=0.8)
            wait_until(self, tr, "cant")
            self.play(Create(cross(q.get_center(), s=1.3, width=10)), run_time=0.6)
            rest(self, tr)
        self.wait(0.3)
        freeze(self)
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.5)
        title_card(self, TITLE)


# ---------------------------------------------------------------------------
# s02 The definition
# ---------------------------------------------------------------------------


class S02Definition(VoiceoverScene):
    def construct(self):
        self.set_speech_service(get_speech_service())
        card = rule_card(size=58).move_to(UP * 1.9)
        ex1 = math(r"\tfrac{3}{4}", r"\ \longmapsto\ ", r"\tfrac{1}{4}", size=52)
        ex2 = math(r"\tfrac{2}{6}", r"=", r"\tfrac{1}{3}", r"\ \longmapsto\ ", r"\tfrac{1}{3}", size=52)
        ex3 = math(r"\tfrac{\sqrt{2}}{2}", r"\ \longmapsto\ ", r"0", size=52)
        for e in (ex1, ex2, ex3):
            e[-1].set_color(FRAC)
        ex3[-1].set_color(IRR)
        exs = VGroup(ex1, ex2, ex3).arrange(DOWN, buff=0.45).move_to(DOWN * 1.6)
        with self.voiceover(text=N("s02.b1")) as tr:
            self.play(FadeIn(card[0]), run_time=0.8)
            wait_until(self, tr, "q")
            self.play(Indicate(card[0][2], color=FRAC), run_time=0.6)
            self.play(FadeIn(ex1, shift=UP * 0.2), run_time=0.6)
            self.play(FadeIn(ex2, shift=UP * 0.2), run_time=0.7)
            t = tr.time_until_bookmark("zero") - 1.6
            if t > 0.05:
                self.wait(t)
            self.play(FadeIn(card[1]), FadeIn(ex3, shift=UP * 0.2), run_time=0.7)
            rest(self, tr)

        pc = Popcorn(left=-4.2, right=6.6, y0=-2.9, y1=2.6)
        pc.qshow.set_value(0)
        ylab = y_labels(pc)
        small = rule_card(size=34).to_corner(UL, buff=0.35)
        thomae = text("Carl Thomae, 1875", size=30, color=MUTED).move_to([4.6, 3.45, 0])
        with self.voiceover(text=N("s02.b2")) as tr:
            self.play(FadeOut(exs), ReplacementTransform(card, small), run_time=0.7)
            self.add(pc)
            self.play(FadeIn(ylab), run_time=0.4)
            wait_until(self, tr, "rows")
            total = tr.get_remaining_duration()
            self.play(pc.qshow.animate.set_value(1), run_time=rt(total * 0.18))
            self.play(pc.qshow.animate.set_value(2), run_time=rt(total * 0.14))
            self.play(pc.qshow.animate.set_value(3), run_time=rt(total * 0.12))
            self.play(pc.qshow.animate.set_value(40), run_time=rt(total * 0.3), rate_func=linear)
            self.play(FadeIn(thomae), run_time=0.6)
            rest(self, tr)
        self.wait(0.3)
        freeze(self)
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.6)


# ---------------------------------------------------------------------------
# s03 What continuous means
# ---------------------------------------------------------------------------


def smooth_f(x):
    return 1.2 + 0.7 * np.sin(1.1 * x) + 0.12 * x


def band_window_axes():
    ax = Axes(x_range=[-3.2, 3.2, 1], y_range=[-0.4, 2.6, 1], x_length=10.5, y_length=5.4,
              tips=False, axis_config=dict(color=MUTED, stroke_width=3, include_ticks=False))
    return ax.move_to(DOWN * 0.3)


def max_delta(f, x0, eps, lo=-3.1, hi=3.1):
    """Largest delta (on a grid) with |f(x) - f(x0)| < eps for |x - x0| < delta."""
    v = f(x0)
    d = 0.0
    for k in range(1, 4000):
        dd = k * 0.0015
        xs = (x0 - dd, x0 + dd)
        if any(not (lo <= x <= hi) or abs(f(x) - v) >= eps for x in xs):
            break
        d = dd
    return d * 0.9


class S03Continuity(VoiceoverScene):
    def construct(self):
        self.set_speech_service(get_speech_service())
        ax = band_window_axes()
        graph = ax.plot(smooth_f, x_range=[-3.1, 3.1], color=FG, stroke_width=4)
        x0 = 0.4
        pt = Dot(ax.c2p(x0, smooth_f(x0)), radius=0.09, color=PRIMARY)
        eps = ValueTracker(0.45)
        dl = ValueTracker(max_delta(smooth_f, x0, 0.45))
        band_on, win_on = ValueTracker(0.0), ValueTracker(0.0)

        def band():
            v = smooth_f(x0)
            a, b = ax.c2p(-3.2, v - eps.get_value()), ax.c2p(3.2, v + eps.get_value())
            r = Rectangle(width=b[0] - a[0], height=b[1] - a[1], stroke_width=0, fill_color=PRIMARY,
                          fill_opacity=0.16 * band_on.get_value()).move_to((a + b) / 2)
            e = VGroup(*[DashedLine(ax.c2p(-3.2, y), ax.c2p(3.2, y), color=PRIMARY, stroke_width=2)
                         .set_stroke(opacity=band_on.get_value())
                         for y in (v - eps.get_value(), v + eps.get_value())])
            return VGroup(r, e)

        def window():
            d = dl.get_value()
            a, b = ax.c2p(x0 - d, -0.4), ax.c2p(x0 + d, 2.6)
            r = Rectangle(width=b[0] - a[0], height=b[1] - a[1], stroke_width=0, fill_color=GOOD,
                          fill_opacity=0.13 * win_on.get_value()).move_to((a + b) / 2)
            seg = ax.plot(smooth_f, x_range=[x0 - d, x0 + d], color=GOOD, stroke_width=7)
            seg.set_stroke(opacity=win_on.get_value())
            return VGroup(r, seg)

        bd, wd = always_redraw(band), always_redraw(window)
        lab_b = text("band", size=32, color=PRIMARY)
        lab_w = text("window", size=32, color=GOOD)
        lab_b.add_updater(lambda m: m.move_to(ax.c2p(-2.6, smooth_f(x0) + eps.get_value() + 0.22)))
        lab_w.add_updater(lambda m: m.move_to(ax.c2p(x0, 2.45)))
        with self.voiceover(text=N("s03.b1")) as tr:
            self.play(Create(ax), Create(graph), run_time=1.2)
            self.play(FadeIn(pt, scale=1.5), run_time=0.5)
            wait_until(self, tr, "band")
            self.add(bd)
            self.play(band_on.animate.set_value(1.0), FadeIn(lab_b), run_time=0.8)
            wait_until(self, tr, "window")
            self.add(wd)
            self.play(win_on.animate.set_value(1.0), FadeIn(lab_w), run_time=0.8)
            rest(self, tr)
        with self.voiceover(text=N("s03.b2")) as tr:
            for e in (0.25, 0.12):
                self.play(eps.animate.set_value(e), run_time=rt(tr.duration * 0.2))
                self.play(dl.animate.set_value(max_delta(smooth_f, x0, e)), run_time=rt(tr.duration * 0.18))
            self.play(Indicate(lab_w, color=GOOD), run_time=0.6)
            rest(self, tr)

        # a light switch
        def step_f(x):
            return 0.0 if x < 0 else 1.0

        left = Line(ax.c2p(-3.1, 0), ax.c2p(0, 0), color=FG, stroke_width=4)
        right = Line(ax.c2p(0, 1), ax.c2p(3.1, 1), color=FG, stroke_width=4)
        filled = Dot(ax.c2p(0, 1), radius=0.09, color=PRIMARY)
        hollow = Circle(radius=0.09, color=FG, stroke_width=3).move_to(ax.c2p(0, 0))
        lab_one = math("1", size=36, color=MUTED).next_to(ax.c2p(-3.2, 1), LEFT, 0.15)
        lab_zero = math("0", size=36, color=MUTED).next_to(ax.c2p(-3.2, 0), LEFT, 0.15)
        b_on, w_on = ValueTracker(0.0), ValueTracker(0.0)
        dw = ValueTracker(1.2)

        def band2():
            a, b = ax.c2p(-3.2, 0.5), ax.c2p(3.2, 1.5)
            r = Rectangle(width=b[0] - a[0], height=b[1] - a[1], stroke_width=0, fill_color=PRIMARY,
                          fill_opacity=0.16 * b_on.get_value()).move_to((a + b) / 2)
            e = VGroup(*[DashedLine(ax.c2p(-3.2, y), ax.c2p(3.2, y), color=PRIMARY, stroke_width=2)
                         .set_stroke(opacity=b_on.get_value()) for y in (0.5, 1.5)])
            return VGroup(r, e)

        def window2():
            d = dw.get_value()
            a, b = ax.c2p(-d, -0.4), ax.c2p(d, 2.6)
            r = Rectangle(width=b[0] - a[0], height=b[1] - a[1], stroke_width=0, fill_color=GOOD,
                          fill_opacity=0.13 * w_on.get_value()).move_to((a + b) / 2)
            bad = Line(ax.c2p(-d, 0), ax.c2p(0, 0), color=BAD, stroke_width=9)
            bad.set_stroke(opacity=w_on.get_value())
            return VGroup(r, bad)

        b2, w2 = always_redraw(band2), always_redraw(window2)
        switch = text("a light switch", size=34, color=MUTED).move_to(ax.c2p(-1.7, 2.2))
        verdict = text("not continuous at 0", size=36, color=BAD).move_to(ax.c2p(1.8, 2.2))
        with self.voiceover(text=N("s03.b3")) as tr:
            self.play(FadeOut(VGroup(graph, pt, lab_b, lab_w)), band_on.animate.set_value(0),
                      win_on.animate.set_value(0), run_time=0.6)
            self.remove(bd, wd)
            self.play(Create(left), Create(right), FadeIn(filled), FadeIn(hollow), FadeIn(lab_one),
                      FadeIn(lab_zero), FadeIn(switch), run_time=1.0)
            self.add(b2, w2)
            self.play(b_on.animate.set_value(1.0), run_time=rt(min(1.0, tr.time_until_bookmark("left") * 0.5)))
            wait_until(self, tr, "left")
            self.play(w_on.animate.set_value(1.0), run_time=0.6)
            self.play(dw.animate.set_value(0.35), run_time=1.2)
            self.play(dw.animate.set_value(0.12), run_time=0.8)
            self.play(FadeIn(verdict), run_time=0.6)
            rest(self, tr)
        self.wait(0.3)
        freeze(self)
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.6)


# ---------------------------------------------------------------------------
# s04 Broken at every fraction
# ---------------------------------------------------------------------------


class S04Broken(VoiceoverScene):
    def construct(self):
        self.set_speech_service(get_speech_service())
        pc = Popcorn(y0=-2.8, y1=2.7)
        ylab = y_labels(pc)
        self.add(pc, ylab)
        self.play(*pc.view(0.5, 0.16), FadeOut(ylab), run_time=1.4)
        ya, yb = ValueTracker(0.25), ValueTracker(0.75)
        bd = pc.band(ya, yb)
        xa, xb = ValueTracker(0.46), ValueTracker(0.54)
        wd = pc.window(xa, xb, color=GOOD, tint=False)
        red_on = ValueTracker(0.0)
        red = pc.axis_red(xa, xb, red_on)
        half = Dot(pc.P(0.5, 0.5), radius=0.1, color=PRIMARY)
        hl = math(r"f\!\left(\tfrac12\right) = \tfrac12", size=40, color=PRIMARY).move_to([-3.6, 2.15, 0])
        irr_lab = text("irrationals, at 0", size=30, color=BAD).move_to([0, -3.65, 0])
        with self.voiceover(text=N("s04.b1")) as tr:
            self.play(FadeIn(half, scale=1.6), FadeIn(hl), run_time=0.7)
            self.add(bd)
            self.play(bd.on.animate.set_value(1.0), run_time=0.8)
            wait_until(self, tr, "window")
            self.add(wd, red)
            self.play(wd.on.animate.set_value(1.0), run_time=0.6)
            wait_until(self, tr, "zero")
            self.play(red_on.animate.set_value(1.0), FadeIn(irr_lab), run_time=0.6)
            self.play(xa.animate.set_value(0.49), xb.animate.set_value(0.51), run_time=1.2)
            self.play(xa.animate.set_value(0.4975), xb.animate.set_value(0.5025), run_time=1.0)
            rest(self, tr)
        verdict = text("broken at 1/2", size=40, color=BAD).move_to([3.6, 2.15, 0])
        every = text("broken at every fraction", size=40, color=BAD).move_to([0, 3.55, 0])
        with self.voiceover(text=N("s04.b2")) as tr:
            self.play(FadeIn(verdict), run_time=0.6)
            self.wait(rt(tr.duration * 0.25))
            self.play(FadeOut(VGroup(half, hl, verdict, irr_lab)), bd.on.animate.set_value(0),
                      wd.on.animate.set_value(0), red_on.animate.set_value(0), run_time=0.6)
            self.remove(bd, wd, red)
            pc.win = None
            pc.qhl.set_value(60)
            self.play(*pc.view(0.5, 1.08), run_time=1.4)
            self.play(pc.hl_on.animate.set_value(1.0), pc.glow.animate.set_value(0.6), FadeIn(every),
                      run_time=0.9)
            rest(self, tr)
        self.wait(0.3)
        freeze(self)
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.6)


# ---------------------------------------------------------------------------
# s05 Continuous at every irrational
# ---------------------------------------------------------------------------


def scale_bar(pc, pos, size=26):
    """A short bar that shows the current x scale (a round length on screen)."""
    def draw():
        span = pc.span
        step = nice_step(span, max_labels=6)
        w = step / span * (pc.right - pc.left)
        dec = max(0, -floor(log10(step) + 1e-9))
        bar = Line(ORIGIN, RIGHT * w, color=MUTED, stroke_width=4)
        ends = VGroup(*[Line(UP * 0.1, DOWN * 0.1, color=MUTED, stroke_width=3).move_to(p)
                        for p in (bar.get_start(), bar.get_end())])
        lab = text(f"{step:.{dec}f}", size=size, color=MUTED).next_to(bar, UP, 0.08)
        return VGroup(bar, ends, lab).move_to(pos)
    return always_redraw(draw)


class S05Continuous(VoiceoverScene):
    def construct(self):
        self.set_speech_service(get_speech_service())
        pc = Popcorn(y0=-2.6, y1=2.6)
        ylab = y_labels(pc)
        mk = pc.marker(ROOT, r"\tfrac{1}{\sqrt2} \approx 0.7071", size=32)
        ya, yb = ValueTracker(-0.1), ValueTracker(0.1)
        bd = pc.band(ya, yb)
        blab = math(r"\text{band: below } \tfrac{1}{10}", size=36, color=PRIMARY).move_to([-3.9, 3.35, 0])
        self.add(pc, ylab)
        with self.voiceover(text=N("s05.b1")) as tr:
            self.play(FadeIn(mk), pc.glow.animate.set_value(0.5), run_time=0.8)
            wait_until(self, tr, "band")
            self.add(bd)
            self.play(bd.on.animate.set_value(1.0), FadeIn(blab), run_time=0.8)
            rest(self, tr)
        pc.qhl.set_value(10)
        cnt = text("denominators up to 10: 33 dots", size=34, color=BAD).move_to([3.4, 3.35, 0])
        with self.voiceover(text=N("s05.b2")) as tr:
            self.play(pc.hl_on.animate.set_value(1.0), run_time=0.9)
            wait_until(self, tr, "few")
            self.play(FadeIn(cnt), run_time=0.6)
            rest(self, tr)

        # deep zoom near 1/sqrt(2): 7/10 and 5/7 are the nearest dots that poke out
        sb = scale_bar(pc, [5.3, -3.55, 0])
        n7 = always_redraw(lambda: math(r"\tfrac{7}{10}", size=36, color=BAD)
                           .next_to(pc.P(0.7, 0.1), UP, 0.15))
        n5 = always_redraw(lambda: math(r"\tfrac{5}{7}", size=36, color=BAD)
                           .next_to(pc.P(5 / 7, 1 / 7), UP, 0.15))
        xa, xb = ValueTracker(ROOT - 0.011), ValueTracker(ROOT + 0.011)
        wd = pc.window(xa, xb, color=GOOD)
        good = text("everything in the window: inside the band", size=32, color=GOOD).move_to([0, 3.35, 0])
        with self.voiceover(text=N("s05.b3")) as tr:
            self.play(FadeOut(ylab), FadeOut(cnt), run_time=0.4)
            self.add(sb)
            self.play(*pc.view(0.7075, 0.03, 0.17), run_time=rt(min(3.0, tr.time_until_bookmark("dodge") - 0.9)))
            self.play(FadeIn(n7), FadeIn(n5), run_time=0.5)
            wait_until(self, tr, "dodge")
            self.add(wd)
            self.play(wd.on.animate.set_value(0.6), run_time=0.5)
            self.play(xa.animate.set_value(0.7015), xb.animate.set_value(0.7128), run_time=1.2)
            self.play(wd.on.animate.set_value(1.0), FadeOut(blab), FadeIn(good), run_time=0.8)
            rest(self, tr)

        blab2 = math(r"\text{band: below } \tfrac{1}{100}", size=36, color=PRIMARY).move_to([-3.9, 3.35, 0])
        n70 = always_redraw(lambda: math(r"\tfrac{70}{99}", size=34, color=BAD)
                            .next_to(pc.P(70 / 99, 1 / 99), UP, 0.15))
        n29 = always_redraw(lambda: math(r"\tfrac{29}{41}", size=34, color=BAD)
                            .next_to(pc.P(29 / 41, 1 / 41), UP, 0.15))
        fin = text("continuous at every irrational", size=40, color=IRR).move_to([0, 3.35, 0])
        with self.voiceover(text=N("s05.b4")) as tr:
            self.play(FadeOut(good), wd.on.animate.set_value(0), FadeOut(n7), FadeOut(n5), run_time=0.5)
            pc.qhl.set_value(100)
            xa.set_value(ROOT - 0.0002)
            xb.set_value(ROOT + 0.0002)
            self.play(ya.animate.set_value(-0.01), yb.animate.set_value(0.01), *pc.view(0.70712, 0.0006, 0.03),
                      FadeIn(blab2), run_time=rt(min(3.2, tr.time_until_bookmark("finite") - 0.2)))
            self.play(FadeIn(n70), FadeIn(n29), run_time=0.5)
            self.play(wd.on.animate.set_value(0.6), run_time=0.4)
            self.play(xa.animate.set_value(ROOT - 0.000028), xb.animate.set_value(ROOT + 0.000028), run_time=1.1)
            self.play(wd.on.animate.set_value(1.0), run_time=0.4)
            self.play(FadeOut(blab2), FadeIn(fin), run_time=0.7)
            rest(self, tr)
        self.wait(0.3)
        freeze(self)
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.6)


# ---------------------------------------------------------------------------
# s06 The reverse is impossible
# ---------------------------------------------------------------------------


class S06Reverse(VoiceoverScene):
    def construct(self):
        self.set_speech_service(get_speech_service())
        q = question(size=48).move_to(UP * 0.2)
        with self.voiceover(text=N("s06.b1")) as tr:
            self.play(FadeIn(q, shift=UP * 0.2), run_time=0.8)
            rest(self, tr)

        steps = countdown(9)
        row = list_row(10, size=44, buff=0.42).move_to(UP * 2.85)
        rlabs = VGroup(*[text(f"r{k + 1}", size=24, color=MUTED).next_to(row.items[k], DOWN, 0.15)
                         for k in range(len(row.items))])
        brace_note = text("every fraction from 0 to 1 is on the list", size=30, color=MUTED)
        brace_note.next_to(rlabs, DOWN, 0.3)
        zl = ZoomLine(-0.06, 1.06, length=12.4, center=DOWN * 1.4, label_size=26, max_labels=6)
        cur = (ValueTracker(0.0), ValueTracker(1.0))
        im = interval_mark(zl, *cur)
        with self.voiceover(text=N("s06.b2")) as tr:
            self.play(FadeOut(q), run_time=0.5)
            self.play(FadeIn(zl), run_time=0.6)
            self.add(im)
            self.play(im.on.animate.set_value(1.0), run_time=0.5)
            wait_until(self, tr, "list")
            self.play(LaggedStart(*[FadeIn(m, shift=DOWN * 0.15) for m in row], lag_ratio=0.15),
                      FadeIn(rlabs), run_time=rt(min(2.4, tr.get_remaining_duration() * 0.5)))
            self.play(FadeIn(brace_note), run_time=0.6)
            rest(self, tr)

        # step 1, slowly
        st = steps[0]
        r0 = zl.dot(0.0, color=BAD, radius=0.1)
        lab_pos = [0, 0.3, 0]
        pick = zl.dot(st["pick"][0] / st["pick"][1], color=GOOD, radius=0.11)
        pick_lab = always_redraw(lambda: math(r"\tfrac{1}{2}", size=40, color=GOOD)
                                 .next_to(zl.p(0.5), UP, 0.75))
        within = text("f moves within 1 here", size=32, color=PRIMARY).move_to(lab_pos)
        with self.voiceover(text=N("s06.b3")) as tr:
            self.play(FadeOut(brace_note), run_time=0.4)
            self.add(r0)
            self.play(r0.show.animate.set_value(1), Indicate(row.items[0], color=BAD), run_time=0.7)
            wait_until(self, tr, "skip")
            self.play(cur[0].animate.set_value(st["cut"][0]), run_time=0.8)
            zx = cross(zl.p(0.0), s=0.16, width=5)
            self.play(Create(cross(row.items[0].get_center(), s=0.2, width=5)), Create(zx), run_time=0.5)
            wait_until(self, tr, "pick")
            self.add(pick)
            self.play(pick.show.animate.set_value(1), FadeIn(pick_lab), run_time=0.6)
            wait_until(self, tr, "tight")
            a, b = st["tight"]
            self.play(cur[0].animate.set_value(a), cur[1].animate.set_value(b), FadeIn(within), run_time=1.2)
            rest(self, tr)

        with self.voiceover(text=N("s06.b4")) as tr:
            self.play(FadeOut(pick_lab), pick.show.animate.set_value(0), r0.show.animate.set_value(0),
                      FadeOut(zx), FadeOut(within), run_time=0.4)
            per = (tr.get_remaining_duration() - 0.3) / 8
            lab = run_steps(self, zl, cur, steps, row, 1, 9, per, lab_pos, label_size=32)
            rest(self, tr)

        with self.voiceover(text=N("s06.b5")) as tr:
            a, b = cur[0].get_value(), cur[1].get_value()
            m = (a + b) / 2
            self.play(cur[0].animate.set_value(TARGET - 1e-7), cur[1].animate.set_value(TARGET + 1e-7),
                      *zl.zoom_to(TARGET - 3e-6, TARGET + 3e-6), FadeOut(lab),
                      run_time=rt(min(2.5, tr.time_until_bookmark("point") + 0.6)))
            pt = Dot(zl.p(TARGET) + UP * 0.32, radius=0.13, color=IRR)
            glow = Circle(radius=0.3, color=IRR, stroke_width=4).move_to(pt)
            self.play(FadeIn(pt, scale=2), Create(glow), run_time=0.7)
            rest(self, tr)

        allx = VGroup(*[cross(row.items[k].get_center(), s=0.2, width=5) for k in range(9, len(row.items))])
        verdict = text("not on the list: irrational", size=38, color=IRR).next_to(pt, UP, 0.9)
        with self.voiceover(text=N("s06.b6")) as tr:
            for k in range(3):
                self.play(Indicate(row.items[k], color=BAD), run_time=rt(min(0.7, tr.duration * 0.12)))
            wait_until(self, tr, "any")
            self.play(LaggedStart(*[Create(x) for x in allx], lag_ratio=0.2), run_time=0.9)
            self.play(FadeIn(verdict), run_time=0.6)
            rest(self, tr)

        # schematic: nested intervals wrapped around the point, with room on both sides
        cx, cy = 0.0, -1.0
        nest = VGroup()
        widths = [8.4, 6.4, 4.6, 3.2, 2.0, 1.2]
        labs = ["within 1", "within 1/2", "within 1/3", "within 1/4", "within 1/5", ""]
        offs = [0.35, -0.6, 0.25, -0.45, 0.15, -0.1]
        for k, (w, s, o) in enumerate(zip(widths, labs, offs)):
            y = cy + 0.38 * (len(widths) - k)
            c = cx + o * w * 0.12
            seg = VGroup(Line([c - w / 2, y, 0], [c + w / 2, y, 0], color=PRIMARY, stroke_width=6),
                         Line([c - w / 2, y - 0.13, 0], [c - w / 2, y + 0.13, 0], color=PRIMARY, stroke_width=5),
                         Line([c + w / 2, y - 0.13, 0], [c + w / 2, y + 0.13, 0], color=PRIMARY, stroke_width=5))
            seg.set_opacity(0.35 + 0.65 * k / (len(widths) - 1))
            nest.add(seg)
            if s:
                nest.add(text(s, size=24, color=PRIMARY).next_to(seg, RIGHT, 0.2).set_opacity(seg[0].get_stroke_opacity()))
        base = Line([-6.4, cy, 0], [6.4, cy, 0], color=MUTED, stroke_width=3)
        ptc = Dot([cx, cy, 0], radius=0.13, color=IRR)
        guide = DashedLine([cx, cy, 0], [cx, cy + 0.38 * 6.6, 0], color=IRR, stroke_width=2)
        cont = text("continuous here", size=40, color=GOOD).move_to([0, 2.6, 0])
        claim = text("broken at every irrational", size=40, color=FG).move_to([0, 3.4, 0])
        with self.voiceover(text=N("s06.b7")) as tr:
            freeze(self)
            self.play(FadeOut(Group(*self.mobjects)), run_time=0.6)
            self.play(Create(base), FadeIn(ptc), Create(guide), run_time=0.6)
            self.play(LaggedStart(*[FadeIn(m) for m in nest], lag_ratio=0.25),
                      run_time=rt(min(3.0, tr.time_until_bookmark("cont") - 0.4)))
            wait_until(self, tr, "cont")
            self.play(FadeIn(cont), FadeIn(claim), run_time=0.6)
            self.play(Create(cross(claim.get_center(), s=0.5, width=8).stretch_to_fit_width(claim.width + 0.3)),
                      run_time=0.6)
            rest(self, tr)
        self.wait(0.3)
        freeze(self)
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.6)


# ---------------------------------------------------------------------------
# s07 Ending
# ---------------------------------------------------------------------------


class S07Ending(VoiceoverScene):
    def construct(self):
        self.set_speech_service(get_speech_service())
        pc = Popcorn(y0=-2.6, y1=2.8)
        pc.qshow.set_value(0)
        baire = text("the Baire category theorem", size=40, color=FG).move_to([0, 3.45, 0])
        big = text("the irrationals: big", size=36, color=IRR).move_to([0, -3.55, 0])
        with self.voiceover(text=N("s07.b1")) as tr:
            self.add(pc)
            self.play(pc.qshow.animate.set_value(40), pc.glow.animate.set_value(0.4), run_time=1.6)
            self.play(FadeIn(baire), run_time=0.7)
            wait_until(self, tr, "big")
            self.play(pc.glow.animate.set_value(1.0), FadeIn(big), run_time=0.8)
            rest(self, tr)
        thin = text("everywhere, yet thin", size=40, color=FRAC).move_to([0, 3.45, 0])
        with self.voiceover(text=N("s07.b2")) as tr:
            self.play(FadeOut(baire), FadeIn(thin), run_time=0.6)
            wait_until(self, tr, "thin")
            self.play(pc.alpha.animate.set_value(0.0), pc.dots.animate.shift(DOWN * 0.0),
                      run_time=rt(min(2.5, tr.get_remaining_duration())))
            rest(self, tr)
        self.wait(0.6)
        freeze(self)
        self.play(FadeOut(Group(*self.mobjects)), run_time=1.0)


# ---------------------------------------------------------------------------
# Thumbnail
# ---------------------------------------------------------------------------


class Thumbnail(Scene):
    def construct(self):
        pc = Popcorn(left=-6.7, right=6.7, y0=-3.5, y1=1.5, target=900, show_ticks=False)
        pc.glow.set_value(1.0)
        for m in (pc.glow_line, pc.ticks, pc.dots):
            m.update()
        t1 = text("Broken at every fraction.", size=70, weight="BOLD", color=FRAC)
        t2 = text("Continuous everywhere else.", size=70, weight="BOLD", color=IRR)
        VGroup(t1, t2).arrange(DOWN, buff=0.25).move_to(UP * 2.75)
        self.add(pc, t1, t2)
