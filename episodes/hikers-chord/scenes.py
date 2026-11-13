"""The hiker's chord: same height, half a loop apart. Long-form scenes."""

import numpy as np
from manim import *
from manim_voiceover import VoiceoverScene
from scipy.optimize import brentq

from mathvid import layout  # noqa: F401  must come before scene code runs
from mathvid.anim import rest, rt, wait_until
from mathvid.layout import FH, FW
from mathvid.orders import cross, tick
from mathvid.script import Script
from mathvid.style import (BAD, BG, FG, GOOD, MUTED, PRIMARY, SECONDARY, TERTIARY, math, text,
                           title_card)
from mathvid.voice import get_speech_service

N = Script(__file__)

TITLE = "Same height, half a loop apart"
HERE = PRIMARY  # the hiker
AHEAD = SECONDARY  # the spot half a loop ahead
LAKE = "#3D7FA8"
LEVY = "Paul L\u00e9vy, 1934"
DEG_C = "\u00b0C"

MATH_SCALE = 1.2


def mth(*s, size=44, **kw):
    return math(*s, size=int(size * MATH_SCALE), **kw)


# ---------------------------------------------------------------------------
# The math. Every curve, rod and zero on screen comes from these functions.
# ---------------------------------------------------------------------------

TAU_ = 2 * np.pi


def loop_h(t):
    """Height (m) along the loop trail, t = fraction of a lap. Period 1."""
    return (300 - 25 * np.cos(TAU_ * t) - 6 * np.sin(TAU_ * t) + 22 * np.cos(2 * TAU_ * t)
            - 14 * np.sin(2 * TAU_ * t) + 7 * np.sin(3 * TAU_ * t) + 5 * np.cos(4 * TAU_ * t))


def ahead_minus_here(t, L=0.5):
    return loop_h(t + L) - loop_h(t)


# d(0) = +50 and d(1/2) = -50 exactly; the single crossing on [0, 1/2]:
Z_HALF = brentq(ahead_minus_here, 0.0, 0.5)  # ~0.3077
# a rod a third of a lap long: d averages to zero over a lap; a crossing we show:
Z_THIRD = brentq(lambda t: ahead_minus_here(t, 1 / 3), 0.5, 0.66)  # ~0.6176


def open_g(x):
    """The open trail (lake to lake), x = fraction of the trail. g(0) = g(1) = 0."""
    return 100 * np.sin(np.pi * x) * (1 + 0.8 * x) + 15 * np.sin(4 * np.pi * x)


OPEN_HALF_Z = brentq(lambda x: open_g(x + 0.5) - open_g(x), 0.0, 0.5)  # ~0.294
OPEN_THIRD_Z = brentq(lambda x: open_g(x + 1 / 3) - open_g(x), 1 / 3, 2 / 3)  # ~0.413


def levy_f(x):
    """Levy's trail: a wave of period 2/5, tilted downhill. f(0) = f(1) = 0."""
    return np.sin(5 * np.pi * x / 2) ** 2 - x


def temp_eq(phi):
    """Temperature along the equator, phi = longitude in radians."""
    return 20 + 8 * np.cos(phi - 0.7) + 4 * np.sin(2 * phi) + 3 * np.cos(3 * phi + 1)


def _phi_star():
    g = lambda p: temp_eq(p + np.pi) - temp_eq(p)
    xs = np.linspace(0, np.pi, 400)
    v = g(xs)
    i = int(np.where(np.diff(np.sign(v)))[0][0])
    return brentq(g, xs[i], xs[i + 1])


PHI_STAR = _phi_star()


# ---------------------------------------------------------------------------
# Builders (shared with shorts.py)
# ---------------------------------------------------------------------------


def temp_color(T, lo=10.0, hi=32.0):
    a = float(np.clip((T - lo) / (hi - lo), 0, 1))
    if a < 0.5:
        return interpolate_color(ManimColor(SECONDARY), ManimColor(PRIMARY), a * 2)
    return interpolate_color(ManimColor(PRIMARY), ManimColor(BAD), (a - 0.5) * 2)


class Globe(VGroup):
    """A flat globe: disk, a few meridians, and an equator band colored by temperature.

    rot shifts which longitude faces the viewer. Screen angle a = phi + rot; the front of
    the equator is the lower half of the ellipse.
    """

    def __init__(self, R=2.4, tilt=0.2, rot=0.0, band=True, n=120, **kw):
        super().__init__(**kw)
        self.R, self.tilt, self.rot = R, tilt, rot
        disk = Circle(radius=R, color=MUTED, stroke_width=3, fill_color="#1B2028", fill_opacity=1)
        mer = VGroup(*[Ellipse(width=2 * R * w, height=2 * R, color=MUTED, stroke_width=1.5,
                               stroke_opacity=0.35) for w in (0.35, 0.75)])
        lat = VGroup(*[Ellipse(width=2 * R * np.cos(b), height=2 * R * self.tilt * np.cos(b), color=MUTED,
                               stroke_width=1.5, stroke_opacity=0.3).shift(UP * R * np.sin(b))
                       for b in (-0.75, 0.75)])
        self.disk, self.grid = disk, VGroup(mer, lat)
        self.add(disk, self.grid)
        self.band = VGroup()
        if band:
            for k in range(n):
                p0, p1 = TAU_ * k / n, TAU_ * (k + 1) / n
                a0, a1 = p0 + rot, p1 + rot
                seg = Line(self.eq_point_screen(a0), self.eq_point_screen(a1),
                           color=temp_color(temp_eq((p0 + p1) / 2)), stroke_width=9)
                if np.sin((a0 + a1) / 2) > 0:  # back half
                    seg.set_stroke(opacity=0.3, width=6)
                self.band.add(seg)
            self.add(self.band)

    def eq_point_screen(self, a):
        return np.array([self.R * np.cos(a), self.R * self.tilt * np.sin(a), 0])

    def eq_point(self, phi):
        a = phi + self.rot
        c = self.disk.get_center()
        return c + np.array([self.R * np.cos(a), self.R * self.tilt * np.sin(a), 0])

    def is_back(self, phi):
        return np.sin(phi + self.rot) > 0


def pair_marks(g, phi=None, size=34, label=True):
    """The two opposite equator points with equal temperature, with '? C' tags."""
    phi = PHI_STAR if phi is None else phi
    out = VGroup()
    for p, side in ((phi, LEFT), (phi + np.pi, RIGHT)):
        pt = g.eq_point(p)
        d = Dot(pt, radius=0.13, color=FG)
        if g.is_back(p):
            d.set_fill(opacity=0.5)
        ring = Circle(radius=0.24, color=FG, stroke_width=3).move_to(pt)
        grp = VGroup(ring, d)
        if label:
            tag = text("? " + DEG_C, size=size, color=FG)
            tag.next_to(pt, side + UP * 0.6, buff=0.15)
            grp.add(tag)
        out.add(grp)
    return out


def trail_points(R=1.5, n=1200):
    th = np.linspace(0, TAU_, n, endpoint=False)
    r = R * (1 + 0.18 * np.cos(2 * th) + 0.12 * np.sin(3 * th))
    pts = np.stack([r * np.cos(th), 0.8 * r * np.sin(th), np.zeros_like(th)], axis=1)
    seg = np.linalg.norm(np.diff(np.vstack([pts, pts[:1]]), axis=0), axis=1)
    s = np.concatenate([[0], np.cumsum(seg)])
    return pts, s / s[-1]


class TrailMap(VGroup):
    """The loop trail seen from above, parameterized by arc length (t = fraction of a lap)."""

    def __init__(self, R=1.5, width=7, **kw):
        super().__init__(**kw)
        self.pts, self.s = trail_points(R)
        path = VMobject(color=MUTED, stroke_width=width)
        path.set_points_smoothly([*self.pts, self.pts[0]])
        start = Line(UP * 0.18, DOWN * 0.18, color=FG, stroke_width=4)
        start.move_to(self.pts[0])
        self.path, self.start = path, start
        self.add(path, start)

    def at(self, t):
        t = t % 1.0
        x = np.interp(t, self.s, np.vstack([self.pts, self.pts[:1]])[:, 0])
        y = np.interp(t, self.s, np.vstack([self.pts, self.pts[:1]])[:, 1])
        return self.path.get_center() - self._c0() + np.array([x, y, 0])

    def _c0(self):
        p = np.vstack([self.pts, self.pts[:1]])
        return (p.max(axis=0) + p.min(axis=0)) / 2


def profile_axes(x_max=1.0, x_length=7.4, y_length=2.8, y_range=(240, 370, 40), xlabel=None,
                 ylabel=None, size=28):
    ax = Axes(x_range=[0, x_max, 0.25 if x_max <= 1 else 0.5], y_range=list(y_range), x_length=x_length,
              y_length=y_length, tips=False,
              axis_config={"color": MUTED, "stroke_width": 3, "include_ticks": False})
    g = VGroup(ax)
    if xlabel:
        xl = text(xlabel, size=size, color=MUTED).next_to(ax, DOWN, buff=0.18)
        g.add(xl)
    if ylabel:
        yl = text(ylabel, size=size, color=MUTED).rotate(PI / 2).next_to(ax.y_axis, LEFT, buff=0.15)
        g.add(yl)
    g.ax = ax
    return g


def plot(ax, f, x0, x1, color=FG, width=5, n=None, opacity=1.0):
    n = n or max(60, int(400 * (x1 - x0)))
    xs = np.linspace(x0, x1, n)
    pts = [ax.c2p(x, f(x)) for x in xs]
    m = VMobject(color=color, stroke_width=width, stroke_opacity=opacity)
    if len(pts) >= 2:
        m.set_points_smoothly(pts)
    return m


def rod(ax, f, x, L, color=FG, width=7, r=0.11):
    a, b = ax.c2p(x, f(x)), ax.c2p(x + L, f(x + L))
    ln = Line(a, b, color=color, stroke_width=width)
    return VGroup(ln, Dot(a, radius=r, color=color), Dot(b, radius=r, color=color))


def rod_color(f, x, L, tol=1e-6):
    return GOOD if abs(f(x + L) - f(x)) < tol else FG


def lake(at, w=0.7, h=0.22):
    return Ellipse(width=w, height=h, color=LAKE, fill_color=LAKE, fill_opacity=0.8, stroke_width=0).move_to(at)


def diff_arrow(ax, f, x, L, color=None, xoff=0.0, width=6):
    """A vertical arrow from height f(x) to height f(x + L), drawn at x + L (+ offset)."""
    y0, y1 = f(x), f(x + L)
    color = color or (GOOD if y1 > y0 else BAD)
    a, b = ax.c2p(x + L + xoff, y0), ax.c2p(x + L + xoff, y1)
    return Arrow(a, b, buff=0, color=color, stroke_width=width, max_tip_length_to_length_ratio=0.25,
                 max_stroke_width_to_length_ratio=12)


def fractions_line(width=10.0, nmax=12, size=34):
    """Rod lengths from 0 to 1: red everywhere, green ticks at 1/n."""
    nl = Line(LEFT * width / 2, RIGHT * width / 2, color=BAD, stroke_width=8)
    x = lambda v: nl.point_from_proportion(v)
    ticks = VGroup()
    labels = VGroup()
    for n in range(1, nmax + 1):
        tk = Line(UP * 0.28, DOWN * 0.28, color=GOOD, stroke_width=6).move_to(x(1 / n))
        ticks.add(tk)
        if n <= 4:
            lab = mth("1" if n == 1 else r"\tfrac{1}{%d}" % n, size=size * 1.3, color=GOOD).next_to(tk, UP, 0.15)
            labels.add(lab)
    zero = mth("0", size=size, color=MUTED).next_to(nl.get_left(), DOWN, 0.2)
    g = VGroup(nl, ticks, labels, zero)
    g.nl, g.ticks, g.labels, g.x, g.zero = nl, ticks, labels, x, zero
    return g


def align_x(dg, ax):
    """Shift dg so its x = 0 sits under ax's x = 0 (both plots then share an x scale)."""
    dg.shift(RIGHT * (ax.c2p(0, ax.y_range[0])[0] - dg.ax.c2p(0, dg.ax.y_range[0])[0]))
    return dg


def legend(size=32):
    a = VGroup(Dot(radius=0.12, color=HERE), text("you", size=size, color=HERE)).arrange(RIGHT, buff=0.15)
    b = VGroup(Dot(radius=0.12, color=AHEAD), text("half a loop ahead", size=size, color=AHEAD)).arrange(RIGHT, buff=0.15)
    return VGroup(a, b).arrange(DOWN, buff=0.18, aligned_edge=LEFT)


def same_label(ax, z, size=36):
    """'same height' under the middle of the level rod (the profile is above it there)."""
    return text("same height", size=size, color=GOOD).move_to(ax.c2p(z + 0.2, 268))


# Landscape layout anchors
MAP_C = np.array([-4.5, 1.35, 0])
PROF_C = np.array([2.3, 1.6, 0])
DPLOT_Y = -2.2


# ---------------------------------------------------------------------------
# s01 Hook
# ---------------------------------------------------------------------------


class S01Hook(VoiceoverScene):
    def construct(self):
        self.set_speech_service(get_speech_service())
        rot = ValueTracker(-PHI_STAR - 0.25)
        globe = always_redraw(lambda: Globe(R=2.5, rot=rot.get_value()).move_to(DOWN * 0.2))
        marks = always_redraw(lambda: pair_marks(Globe(R=2.5, rot=rot.get_value(), band=False).move_to(DOWN * 0.2)))
        with self.voiceover(text=N("s01.b1")) as tr:
            self.play(FadeIn(globe), run_time=0.8)
            self.play(rot.animate.set_value(-PHI_STAR - 0.08), run_time=rt(tr.time_until_bookmark("two") - 0.1),
                      rate_func=linear)
            self.add(marks)
            self.play(FadeIn(marks, scale=0.7), rot.animate.set_value(-PHI_STAR), run_time=0.8)
            self.play(rot.animate.set_value(-PHI_STAR + 0.06), run_time=rt(tr.get_remaining_duration()),
                      rate_func=linear)

        qs = VGroup(*[text("?", size=80, color=MUTED, weight="BOLD") for _ in range(3)])
        qs[0].move_to([-4.6, 1.8, 0])
        qs[1].move_to([4.6, 1.8, 0])
        qs[2].move_to([0, 3.3, 0])
        with self.voiceover(text=N("s01.b2")) as tr:
            self.play(LaggedStart(*[FadeIn(q, scale=0.6) for q in qs], lag_ratio=0.3), run_time=1.2)
            self.play(rot.animate.set_value(-PHI_STAR + 0.12), run_time=rt(tr.get_remaining_duration()),
                      rate_func=linear)
        globe.clear_updaters()
        marks.clear_updaters()
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.5)
        title_card(self, TITLE)


# ---------------------------------------------------------------------------
# s02 The loop trail
# ---------------------------------------------------------------------------


def walk_setup(scene, map_c=MAP_C, prof_c=PROF_C, R=1.5, x_length=7.0, y_length=2.8):
    tm = TrailMap(R=R).move_to(map_c)
    pg = profile_axes(1.0, x_length=x_length, y_length=y_length, xlabel="distance along the trail",
                      ylabel="height").move_to(prof_c)
    return tm, pg


class S02Loop(VoiceoverScene):
    def construct(self):
        self.set_speech_service(get_speech_service())
        tm, pg = walk_setup(self, map_c=np.array([-4.4, 0.0, 0]), prof_c=np.array([2.3, 0.1, 0]), R=1.7,
                            y_length=3.8)
        ax = pg.ax
        t = ValueTracker(0.0)
        hiker = always_redraw(lambda: Dot(tm.at(t.get_value()), radius=0.14, color=HERE))
        drawn = always_redraw(lambda: plot(ax, loop_h, 0, max(0.002, t.get_value()), FG, 5))
        pdot = always_redraw(lambda: Dot(ax.c2p(t.get_value(), loop_h(t.get_value())), radius=0.11, color=HERE))
        with self.voiceover(text=N("s02.b1")) as tr:
            self.play(Create(tm), FadeIn(pg), run_time=1.0)
            self.add(drawn, hiker, pdot)
            self.play(t.animate.set_value(1.0), run_time=rt(tr.time_until_bookmark("back") - 0.1), rate_func=linear)
            same = DashedLine(ax.c2p(0, loop_h(0)), ax.c2p(1, loop_h(1)), color=MUTED, stroke_width=3)
            self.play(Create(same), Flash(hiker, color=HERE), run_time=0.8)
            rest(self, tr)
        drawn.clear_updaters()
        prof = plot(ax, loop_h, 0, 1, FG, 5)
        self.remove(drawn)
        self.add(prof)
        t.set_value(0.0)

        ahead = always_redraw(lambda: Dot(tm.at(t.get_value() + 0.5), radius=0.14, color=AHEAD))
        r = always_redraw(lambda: rod(ax, loop_h, t.get_value(), 0.5,
                                      GOOD if abs(t.get_value() - Z_HALF) < 1e-3 else FG))
        with self.voiceover(text=N("s02.b2")) as tr:
            self.play(FadeOut(same), FadeIn(ahead), run_time=0.6)
            self.add(r)
            self.play(t.animate.set_value(0.12), run_time=1.0)
            wait_until(self, tr, "level")
            self.play(t.animate.set_value(Z_HALF), run_time=rt(min(1.4, tr.get_remaining_duration())))
            lab = same_label(ax, Z_HALF)
            self.play(FadeIn(lab, shift=UP * 0.15), run_time=0.5)
            rest(self, tr)
        for m in (hiker, pdot, ahead, r):
            m.clear_updaters()
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.6)


# ---------------------------------------------------------------------------
# s03 One subtraction
# ---------------------------------------------------------------------------


def counter(value_fn, size=40):
    """'ahead - here = +50 m', live."""
    lab = text("ahead \u2212 here =", size=size, color=FG)
    num = DecimalNumber(0, num_decimal_places=0, include_sign=True, font_size=size * 1.25, color=FG)
    unit = text("m", size=size, color=FG)
    g = VGroup(lab, num, unit).arrange(RIGHT, buff=0.18)

    def upd(m):
        v = value_fn()
        m[1].set_value(v)
        m[1].set_color(GOOD if abs(v) < 0.5 else (AHEAD if v > 0 else BAD))
        m[1].next_to(m[0], RIGHT, 0.18)
        m[2].next_to(m[1], RIGHT, 0.14)

    g.add_updater(upd)
    upd(g)
    return g


def gap_bar(ax, f, x, L):
    """Dashed level line from 'here' to under 'ahead', and a bar up to 'ahead'."""
    y0, y1 = f(x), f(x + L)
    lvl = DashedLine(ax.c2p(x, y0), ax.c2p(x + L, y0), color=MUTED, stroke_width=2.5, dash_length=0.1)
    col = AHEAD if y1 > y0 else BAD
    bar = Line(ax.c2p(x + L, y0), ax.c2p(x + L, y1), color=col, stroke_width=7)
    return VGroup(lvl, bar)


class S03Subtraction(VoiceoverScene):
    def construct(self):
        self.set_speech_service(get_speech_service())
        tm, pg = walk_setup(self)
        ax = pg.ax
        prof = plot(ax, loop_h, 0, 1, FG, 5)
        t = ValueTracker(0.0)
        hiker = always_redraw(lambda: Dot(tm.at(t.get_value()), radius=0.14, color=HERE))
        ahead = always_redraw(lambda: Dot(tm.at(t.get_value() + 0.5), radius=0.14, color=AHEAD))
        ph = always_redraw(lambda: Dot(ax.c2p(t.get_value(), loop_h(t.get_value())), radius=0.12, color=HERE))
        pa = always_redraw(lambda: Dot(ax.c2p(t.get_value() + 0.5, loop_h(t.get_value() + 0.5)), radius=0.12,
                                       color=AHEAD))
        bar = always_redraw(lambda: gap_bar(ax, loop_h, t.get_value(), 0.5))
        lg = legend().next_to(tm, DOWN, 0.4)
        cnt = counter(lambda: ahead_minus_here(t.get_value()), size=36).next_to(lg, DOWN, 0.45)
        with self.voiceover(text=N("s03.b1")) as tr:
            self.play(FadeIn(tm), FadeIn(pg), Create(prof), run_time=1.0)
            self.add(bar, ph, pa, hiker, ahead)
            self.play(FadeIn(lg), run_time=0.6)
            wait_until(self, tr, "plus")
            self.play(FadeIn(cnt, shift=UP * 0.2), run_time=0.6)
            rest(self, tr)

        same = text("same spot", size=28, color=MUTED)
        ends = VGroup(Circle(radius=0.2, color=MUTED, stroke_width=3).move_to(ax.c2p(0, loop_h(0))),
                      Circle(radius=0.2, color=MUTED, stroke_width=3).move_to(ax.c2p(1, loop_h(1))))
        same.next_to(ends[1], DOWN, 0.15).align_to(ends[1], RIGHT)
        with self.voiceover(text=N("s03.b2")) as tr:
            self.play(FadeIn(ends), FadeIn(same), run_time=0.6)
            self.play(t.animate.set_value(0.5), run_time=rt(tr.time_until_bookmark("swap") - 0.2),
                      rate_func=smooth)
            self.play(Indicate(ph, color=HERE), Indicate(pa, color=AHEAD), Indicate(cnt[1]), run_time=0.9)
            rest(self, tr)
        self.play(FadeOut(same), FadeOut(ends), run_time=0.4)

        dg = profile_axes(0.5, x_length=3.5, y_length=2.4, y_range=(-60, 60, 50), xlabel="distance walked")
        dg.move_to([0, DPLOT_Y, 0])
        align_x(dg, ax)
        dax = dg.ax
        zl = mth("0", size=28, color=MUTED).next_to(dax.c2p(0, 0), LEFT, 0.12)
        p50 = mth("+50", size=26, color=AHEAD).next_to(dax.c2p(0, 50), LEFT, 0.12)
        m50 = mth("-50", size=26, color=BAD).next_to(dax.c2p(0, -50), LEFT, 0.12)
        dcurve = plot(dax, ahead_minus_here, 0, 0.5, TERTIARY, 5)
        cross_pt = Dot(dax.c2p(Z_HALF, 0), radius=0.13, color=GOOD)
        with self.voiceover(text=N("s03.b3")) as tr:
            self.play(FadeIn(dg), FadeIn(zl), FadeIn(p50), FadeIn(m50), run_time=0.7)
            self.play(t.animate.set_value(0.0), run_time=0.8)
            dtrace = always_redraw(lambda: plot(dax, ahead_minus_here, 0, max(0.002, t.get_value()), TERTIARY, 5))
            self.add(dtrace)
            self.play(t.animate.set_value(0.5), run_time=rt(min(4.0, tr.time_until_bookmark("zero") - 0.1)),
                      rate_func=linear)
            dtrace.clear_updaters()
            self.remove(dtrace)
            self.add(dcurve)
            self.play(FadeIn(cross_pt, scale=0.4), Flash(cross_pt, color=GOOD), run_time=0.8)
            ivt = VGroup(text("intermediate", size=34, color=GOOD), text("value theorem", size=34, color=GOOD))
            ivt.arrange(DOWN, buff=0.1, aligned_edge=LEFT).next_to(dax.c2p(0.5, 0), RIGHT, 0.6)
            self.play(FadeIn(ivt), run_time=0.5)
            rest(self, tr)

        level = always_redraw(lambda: rod(ax, loop_h, t.get_value(), 0.5,
                                          GOOD if abs(t.get_value() - Z_HALF) < 1e-3 else FG, width=6))
        vline = DashedLine(dax.c2p(Z_HALF, -60), ax.c2p(Z_HALF, 240), color=GOOD, stroke_width=2.5)
        samel = text("same height", size=36, color=GOOD)
        with self.voiceover(text=N("s03.b4")) as tr:
            self.add(level)
            self.play(t.animate.set_value(Z_HALF), run_time=1.2)
            self.play(Create(vline), run_time=0.5)
            wait_until(self, tr, "snap")
            samel = same_label(ax, Z_HALF)
            self.play(FadeIn(samel, shift=UP * 0.15), Flash(hiker, color=HERE), Flash(ahead, color=AHEAD),
                      run_time=0.8)
            rest(self, tr)
        for m in (hiker, ahead, ph, pa, bar, cnt, level):
            m.clear_updaters()
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.6)


# ---------------------------------------------------------------------------
# s04 The equator
# ---------------------------------------------------------------------------


class S04Equator(VoiceoverScene):
    def construct(self):
        self.set_speech_service(get_speech_service())
        rot = -PHI_STAR
        globe = Globe(R=2.2, rot=rot).move_to([-4.2, 0.2, 0])
        marks = pair_marks(Globe(R=2.2, rot=rot, band=False).move_to([-4.2, 0.2, 0]), label=False)
        tax = profile_axes(1.0, x_length=7.0, y_length=2.8, y_range=(8, 34, 10), xlabel="around the equator",
                           ylabel="temperature").move_to([2.9, 0.4, 0])
        ax = tax.ax
        T = lambda u: temp_eq(TAU_ * u + PHI_STAR)  # start the profile at the first marked point
        tprof = VGroup(*[Line(ax.c2p(u0, T(u0)), ax.c2p(u1, T(u1)), color=temp_color(T((u0 + u1) / 2)),
                              stroke_width=7) for u0, u1 in zip(np.linspace(0, 1, 120)[:-1],
                                                                np.linspace(0, 1, 120)[1:])])
        with self.voiceover(text=N("s04.b1")) as tr:
            self.play(FadeIn(globe), run_time=0.8)
            wait_until(self, tr, "loop")
            self.play(Indicate(globe.band, scale_factor=1.04, color=PRIMARY), run_time=0.8)
            self.play(FadeIn(tax), ReplacementTransform(globe.band.copy(), tprof), run_time=1.6)
            r = rod(ax, T, 0.0, 0.5, GOOD, width=6)
            self.play(FadeIn(marks), Create(r), run_time=0.9)
            lab = text("same number, same flip", size=34, color=GOOD).next_to(tax, UP, 0.3)
            self.play(FadeIn(lab), run_time=0.5)
            rest(self, tr)
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.6)

        # whole-globe version: temperature bands and pressure contours
        R = 2.6
        c = np.array([-2.2, -0.2, 0])
        disk = Circle(radius=R, color=MUTED, stroke_width=3, fill_color="#1B2028", fill_opacity=1).move_to(c)
        bands = VGroup()
        nb = 9
        for k in range(nb):
            y0 = -R + 2 * R * k / nb
            strip = Rectangle(width=2 * R + 0.2, height=2 * R / nb + 0.01).move_to(c + UP * (y0 + R / nb))
            lat = abs(y0 + R / nb) / R
            col = temp_color(31 - 18 * lat)
            band = Intersection(strip, Circle(radius=R - 0.02).move_to(c), color=col, fill_color=col,
                                fill_opacity=0.35, stroke_width=0)
            bands.add(band)
        iso = VGroup()
        for k, (dx, dy, w, h) in enumerate([(-0.9, 0.8, 1.6, 1.0), (-0.9, 0.8, 2.6, 1.7), (1.0, -0.7, 1.4, 0.9),
                                            (1.0, -0.7, 2.4, 1.5)]):
            e = Ellipse(width=w, height=h, color=FG, stroke_width=2, stroke_opacity=0.7).move_to(c + [dx, dy, 0])
            e.rotate(0.4 * (1 if k < 2 else -1))
            iso.add(e)
        p = c + np.array([-1.2, 1.25, 0])
        q = 2 * c - p
        dp = Dot(p, radius=0.15, color=FG)
        dq = Dot(q, radius=0.15, color=FG).set_fill(opacity=0.45)
        thru = DashedLine(p, q, color=MUTED, stroke_width=2.5)
        info = VGroup(text("Borsuk-Ulam", size=48, color=PRIMARY, weight="BOLD"),
                      text("same temperature", size=36), text("and same pressure", size=36))
        info.arrange(DOWN, buff=0.25, aligned_edge=LEFT).move_to([4.2, 0.6, 0])
        with self.voiceover(text=N("s04.b2")) as tr:
            self.play(FadeIn(disk), FadeIn(bands), run_time=0.8)
            self.play(Create(iso), run_time=1.0)
            self.play(FadeIn(dp, scale=0.5), FadeIn(dq, scale=0.5), Create(thru), run_time=0.8)
            self.play(FadeIn(info[1]), run_time=0.4)
            wait_until(self, tr, "both")
            self.play(FadeIn(info[2]), Flash(dp, color=FG), run_time=0.7)
            self.play(FadeIn(info[0], shift=DOWN * 0.15), run_time=0.6)
            rest(self, tr)
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.6)


# ---------------------------------------------------------------------------
# s05 Any distance on a loop
# ---------------------------------------------------------------------------


class S05AnyDistance(VoiceoverScene):
    def construct(self):
        self.set_speech_service(get_speech_service())
        pg = profile_axes(2.0, x_length=11.0, y_length=2.6, xlabel="two laps of the trail").move_to([0, 1.7, 0])
        ax = pg.ax
        prof = plot(ax, loop_h, 0, 2, FG, 5)
        lap = DashedLine(ax.c2p(1, 245), ax.c2p(1, 368), color=MUTED, stroke_width=2)
        lapl = text("lap 2", size=26, color=MUTED).next_to(ax.c2p(1.5, 368), UP, 0.05)
        t = ValueTracker(0.05)
        L = ValueTracker(1 / 3)
        r = always_redraw(lambda: rod(ax, loop_h, t.get_value(), L.get_value(),
                                      GOOD if abs(ahead_minus_here(t.get_value(), L.get_value())) < 1e-3 else FG,
                                      width=6))
        with self.voiceover(text=N("s05.b1")) as tr:
            self.play(FadeIn(pg), Create(prof), FadeIn(lap), FadeIn(lapl), run_time=1.0)
            wait_until(self, tr, "third")
            self.add(r)
            self.play(t.animate.set_value(0.4), run_time=1.0)
            self.play(L.animate.set_value(0.18), run_time=0.7)
            self.play(L.animate.set_value(0.62), run_time=0.8)
            self.play(L.animate.set_value(1 / 3), t.animate.set_value(0.0), run_time=rt(min(0.8, tr.get_remaining_duration())))
            rest(self, tr)

        dg = profile_axes(1.0, x_length=5.5, y_length=2.4, y_range=(-80, 80, 40),
                          xlabel="where you are on the lap").move_to([0, -2.1, 0])
        align_x(dg, ax)
        dax = dg.ax
        d3 = lambda u: ahead_minus_here(u, 1 / 3)
        trace = always_redraw(lambda: plot(dax, d3, 0, max(0.002, t.get_value()), TERTIARY, 5))
        dl = text("ahead \u2212 here", size=30, color=TERTIARY).move_to(dax.c2p(0.62, 62))
        zero = DashedLine(dax.c2p(0, 0), dax.c2p(1, 0), color=GOOD, stroke_width=3)
        avg = text("average over a lap = 0", size=34, color=GOOD).next_to(dax.c2p(1, 0), RIGHT, 0.5)
        with self.voiceover(text=N("s05.b2")) as tr:
            self.play(FadeIn(dg), FadeIn(dl), run_time=0.6)
            self.add(trace)
            self.play(t.animate.set_value(1.0), run_time=rt(tr.time_until_bookmark("average") - 0.3), rate_func=linear)
            self.play(Create(zero), FadeIn(avg), run_time=0.8)
            rest(self, tr)
        trace.clear_updaters()

        cp = Dot(dax.c2p(Z_THIRD, 0), radius=0.13, color=GOOD)
        vline = DashedLine(dax.c2p(Z_THIRD, 0), ax.c2p(Z_THIRD, 245), color=GOOD, stroke_width=2.5)
        with self.voiceover(text=N("s05.b3")) as tr:
            self.play(FadeIn(cp, scale=0.4), Flash(cp, color=GOOD), run_time=0.8)
            wait_until(self, tr, "snap")
            self.play(t.animate.set_value(Z_THIRD), Create(vline), run_time=1.0)
            ok = text("every distance works", size=40, color=GOOD).next_to(avg, DOWN, 0.45).align_to(avg, LEFT)
            self.play(FadeIn(ok), run_time=0.6)
            rest(self, tr)
        r.clear_updaters()
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.6)


# ---------------------------------------------------------------------------
# s06 A trail that isn't a loop
# ---------------------------------------------------------------------------


def open_axes(x_length=11.0, y_length=3.4):
    return profile_axes(1.0, x_length=x_length, y_length=y_length, y_range=(-40, 220, 50),
                        xlabel="distance along the trail")


def open_trail(ax, color=FG):
    prof = plot(ax, open_g, 0, 1, color, 5)
    l0, l1 = lake(ax.c2p(0, 0)), lake(ax.c2p(1, 0))
    s = text("start", size=30, color=LAKE).next_to(l0, DOWN, 0.15)
    e = text("end", size=30, color=LAKE).next_to(l1, DOWN, 0.15)
    lvl = DashedLine(ax.c2p(0, 0), ax.c2p(1, 0), color=MUTED, stroke_width=2.5)
    return VGroup(prof, lvl, l0, l1, s, e)


class S06Open(VoiceoverScene):
    def construct(self):
        self.set_speech_service(get_speech_service())
        pg = open_axes().move_to([0, 0.9, 0])
        ax = pg.ax
        tr_ = open_trail(ax)
        with self.voiceover(text=N("s06.b1")) as tr:
            self.play(FadeIn(pg), run_time=0.5)
            wait_until(self, tr, "open")
            self.play(Create(tr_[0]), FadeIn(tr_[2:]), run_time=1.4)
            self.play(Create(tr_[1]), run_time=0.6)
            rest(self, tr)

        x = ValueTracker(0.0)
        r = always_redraw(lambda: rod(ax, open_g, x.get_value(), 0.5,
                                      GOOD if abs(open_g(x.get_value() + 0.5) - open_g(x.get_value())) < 1e-3 else FG,
                                      width=6))
        a1 = diff_arrow(ax, open_g, 0.0, 0.5, xoff=-0.02)
        a2 = diff_arrow(ax, open_g, 0.5, 0.5, xoff=-0.02)
        eq = VGroup(text("up", size=36, color=GOOD), text("+", size=36), text("down", size=36, color=BAD),
                    text("=", size=36), text("end \u2212 start = 0", size=36)).arrange(RIGHT, buff=0.2)
        eq.move_to([0, -2.6, 0])
        with self.voiceover(text=N("s06.b2")) as tr:
            self.add(r)
            self.play(GrowFromCenter(r), run_time=0.5)
            self.play(GrowArrow(a1), run_time=0.6)
            self.play(x.animate.set_value(0.5), run_time=0.9)
            self.play(GrowArrow(a2), run_time=0.6)
            wait_until(self, tr, "add")
            self.play(FadeIn(eq, shift=UP * 0.2), run_time=0.8)
            self.play(x.animate.set_value(0.0), run_time=0.8)
            self.wait(max(0.0, tr.get_remaining_duration() - 2.2))
            self.play(x.animate.set_value(OPEN_HALF_Z), run_time=1.4)
            lv = text("level", size=36, color=GOOD).next_to(ax.c2p(OPEN_HALF_Z + 0.25, open_g(OPEN_HALF_Z)), UP, 0.3)
            self.play(FadeIn(lv), run_time=0.4)
            rest(self, tr)
        r.clear_updaters()
        self.play(FadeOut(r), FadeOut(a1), FadeOut(a2), FadeOut(eq), FadeOut(lv), run_time=0.5)

        x.set_value(0.0)
        r3 = always_redraw(lambda: rod(ax, open_g, x.get_value(), 1 / 3,
                                       GOOD if abs(open_g(x.get_value() + 1 / 3) - open_g(x.get_value())) < 1e-3 else FG,
                                       width=6))
        ghosts = VGroup(*[rod(ax, open_g, k / 3, 1 / 3, MUTED, width=4, r=0.08) for k in range(3)])
        arrs = VGroup(*[diff_arrow(ax, open_g, k / 3, 1 / 3, xoff=-0.02) for k in range(3)])
        sum0 = text("the three add up to 0", size=36).move_to([0, -2.6, 0])
        with self.voiceover(text=N("s06.b3")) as tr:
            self.play(FadeIn(ghosts), run_time=0.6)
            self.play(LaggedStart(*[GrowArrow(a) for a in arrs], lag_ratio=0.5), run_time=1.6)
            wait_until(self, tr, "three")
            self.play(FadeIn(sum0, shift=UP * 0.2), run_time=0.6)
            self.play(arrs[0].animate.set_opacity(0.25), ghosts[0].animate.set_opacity(0.2),
                      Indicate(arrs[1]), Indicate(arrs[2]), run_time=0.9)
            x.set_value(1 / 3)
            self.add(r3)
            self.play(FadeIn(r3), run_time=0.4)
            self.wait(max(0.0, tr.get_remaining_duration() - 1.8))
            self.play(x.animate.set_value(OPEN_THIRD_Z), run_time=1.3)
            rest(self, tr)
        r3.clear_updaters()

        fr = VGroup(*[mth(s, size=60) for s in (r"\tfrac{1}{2}", r"\tfrac{1}{3}", r"\tfrac{1}{4}", r"\tfrac{1}{5}",
                                                 r"\cdots")]).arrange(RIGHT, buff=1.35).move_to([0, -2.6, 0])
        tk = VGroup(*[tick(at=f.get_right() + RIGHT * 0.42, color=GOOD, s=1.5) for f in fr[:4]])
        with self.voiceover(text=N("s06.b4")) as tr:
            self.play(FadeOut(sum0), FadeOut(arrs), FadeOut(ghosts), run_time=0.5)
            self.play(LaggedStart(*[FadeIn(f) for f in fr], lag_ratio=0.2), run_time=1.0)
            wait_until(self, tr, "all")
            self.play(LaggedStart(*[FadeIn(k, scale=0.5) for k in tk], lag_ratio=0.2), run_time=1.0)
            rest(self, tr)
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.6)


# ---------------------------------------------------------------------------
# s07 Two fifths
# ---------------------------------------------------------------------------


def levy_axes(x_length=11.0, y_length=3.6):
    return profile_axes(1.0, x_length=x_length, y_length=y_length, y_range=(-1.05, 1.05, 0.5),
                        xlabel="distance along the trail")


def drop_label(value_fn, size=36):
    lab = text("far end:", size=size, color=FG)
    num = DecimalNumber(0.4, num_decimal_places=1, font_size=size * 1.25, color=BAD)
    unit = text("lower", size=size, color=BAD)
    g = VGroup(lab, num, unit).arrange(RIGHT, buff=0.18)

    def upd(m):
        m[1].set_value(abs(value_fn()))
        m[1].next_to(m[0], RIGHT, 0.18)
        m[2].next_to(m[1], RIGHT, 0.14)

    g.add_updater(upd)
    upd(g)
    return g


class S07TwoFifths(VoiceoverScene):
    def construct(self):
        self.set_speech_service(get_speech_service())
        pg = levy_axes().move_to([0, 0.55, 0])
        ax = pg.ax
        prof = plot(ax, levy_f, 0, 1, FG, 5, n=500)
        l0, l1 = lake(ax.c2p(0, 0)), lake(ax.c2p(1, 0))
        x = ValueTracker(0.0)
        r = always_redraw(lambda: rod(ax, levy_f, x.get_value(), 0.4, BAD, width=6))
        dl = drop_label(lambda: levy_f(x.get_value() + 0.4) - levy_f(x.get_value())).move_to([0, -2.55, 0])
        title = text("a rod 2/5 of the trail long", size=40, color=BAD).to_edge(UP, buff=0.35)
        with self.voiceover(text=N("s07.b1")) as tr:
            self.play(FadeIn(pg), FadeIn(title), run_time=0.6)
            self.play(Create(prof), FadeIn(l0), FadeIn(l1), run_time=1.2)
            wait_until(self, tr, "fails")
            self.add(r)
            self.play(FadeIn(r), FadeIn(dl), run_time=0.5)
            self.play(x.animate.set_value(0.6), run_time=rt(tr.get_remaining_duration()), rate_func=there_and_back)
            rest(self, tr)

        wave = plot(ax, lambda u: np.sin(5 * np.pi * u / 2) ** 2, 0, 1, SECONDARY, 3, n=500, opacity=0.6)
        tilt = plot(ax, lambda u: -u, 0, 1, TERTIARY, 3, opacity=0.6)
        wl = text("a wave that repeats every 2/5", size=30, color=SECONDARY).next_to(dl, DOWN, 0.3)
        tl = text("tilted downhill", size=30, color=TERTIARY).move_to(ax.c2p(0.2, -0.42))
        crest = Dot(ax.c2p(1, 1), radius=0.12, color=SECONDARY)
        endp = Dot(ax.c2p(1, 0), radius=0.14, color=GOOD)
        cl = text("crest + tilt = start height", size=30, color=GOOD).next_to(crest, LEFT, 0.3)
        carrow = Arrow(crest.get_center(), endp.get_center(), buff=0.12, color=GOOD, stroke_width=5)
        with self.voiceover(text=N("s07.b2")) as tr:
            self.play(Create(wave), FadeIn(wl), run_time=1.0)
            self.play(Create(tilt), FadeIn(tl), run_time=0.8)
            wait_until(self, tr, "lower")
            self.play(x.animate.set_value(0.6), run_time=1.6, rate_func=linear)
            self.play(x.animate.set_value(0.0), run_time=1.2, rate_func=linear)
            wait_until(self, tr, "crest")
            self.play(FadeIn(crest), GrowArrow(carrow), FadeIn(endp), FadeIn(cl), run_time=0.9)
            rest(self, tr)
        r.clear_updaters()
        dl.clear_updaters()
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.6)

        fl = fractions_line(width=11.0).move_to([0, -0.6, 0])
        lab = text("rod length", size=30, color=MUTED).next_to(fl.x(0.75), DOWN, 0.45)
        two5 = mth(r"\tfrac{2}{5}", size=40, color=BAD).next_to(fl.x(0.4), DOWN, 0.35)
        two5x = cross(fl.x(0.4), color=BAD, s=0.2, width=7)
        levy = text(LEVY, size=48, color=PRIMARY, weight="BOLD").move_to([0, 2.4, 0])
        legend = VGroup(text("always works", size=30, color=GOOD), text("can fail", size=30, color=BAD))
        legend.arrange(RIGHT, buff=1.2).next_to(fl, DOWN, 1.5)
        with self.voiceover(text=N("s07.b3")) as tr:
            self.play(FadeIn(levy, shift=DOWN * 0.15), run_time=0.7)
            self.play(Create(fl.nl), FadeIn(fl.zero), FadeIn(lab), run_time=0.8)
            self.play(FadeIn(two5), FadeIn(two5x), run_time=0.5)
            wait_until(self, tr, "every")
            self.play(LaggedStart(*[FadeIn(t_) for t_ in fl.ticks], lag_ratio=0.12), FadeIn(fl.labels), run_time=1.4)
            self.play(FadeIn(legend), run_time=0.5)
            rest(self, tr)
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.6)

        loop = TrailMap(R=1.6).move_to([-3.6, 0.3, 0])
        opn = TrailMap(R=1.6).move_to([3.6, 0.3, 0])
        # cut the second loop open: drop a short arc around its start, put lakes at the cut
        pts = opn.pts
        k = int(0.04 * len(pts))
        c0 = opn._c0()
        sh = opn.path.get_center() - c0
        arc = VMobject(color=MUTED, stroke_width=7)
        arc.set_points_smoothly([p + sh for p in pts[k:len(pts) - k]])
        la = lake(pts[k] + sh, w=0.45, h=0.18)
        lb = lake(pts[len(pts) - k - 1] + sh, w=0.45, h=0.18)
        gap = VGroup(arc, la, lb)
        t1 = text("every length", size=36, color=GOOD).next_to(loop, UP, 0.45)
        t2 = VGroup(text("only", size=36, color=PRIMARY),
                    mth(r"\tfrac{1}{2},\ \tfrac{1}{3},\ \tfrac{1}{4},\ \dots", size=40, color=PRIMARY))
        t2.arrange(RIGHT, buff=0.2).next_to(opn, UP, 0.4)
        with self.voiceover(text=N("s07.b4")) as tr:
            self.play(Create(loop), FadeIn(t1), run_time=1.0)
            self.play(FadeIn(opn), run_time=0.6)
            self.play(FadeOut(opn), FadeIn(gap), FadeIn(t2), run_time=1.0)
            wait_until(self, tr, "wrap")
            self.play(Indicate(loop.start, scale_factor=2.0, color=GOOD), Indicate(la, scale_factor=1.6),
                      Indicate(lb, scale_factor=1.6), run_time=1.0)
            rest(self, tr)
        self.wait(0.6)
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.8)


# ---------------------------------------------------------------------------
# Thumbnail
# ---------------------------------------------------------------------------


class Thumbnail(Scene):
    def construct(self):
        pg = profile_axes(1.0, x_length=12.0, y_length=3.6).move_to([0.3, -1.65, 0])
        ax = pg.ax
        pg.set_opacity(0.0)
        prof = plot(ax, loop_h, 0, 1, FG, 8)
        r = rod(ax, loop_h, Z_HALF, 0.5, GOOD, width=10, r=0.2)
        d1 = Dot(ax.c2p(Z_HALF, loop_h(Z_HALF)), radius=0.24, color=HERE)
        d2 = Dot(ax.c2p(Z_HALF + 0.5, loop_h(Z_HALF + 0.5)), radius=0.24, color=AHEAD)
        t1 = text("Same height,", size=92, weight="BOLD")
        t2 = text("half a loop apart", size=92, weight="BOLD", color=PRIMARY)
        tt = VGroup(t1, t2).arrange(DOWN, buff=0.2, aligned_edge=LEFT).to_corner(UL, buff=0.5)
        self.add(prof, r, d1, d2, tt)
