"""Secret sharing: split a secret so any three can open it. Long-form scenes."""

from itertools import combinations
from math import comb, cos, pi, sin

import numpy as np
from manim import *
from manim_voiceover import VoiceoverScene

from mathvid import layout  # noqa: F401  must come before scene code runs
from mathvid.anim import rest, rt, strike, wait_until
from mathvid.layout import FH, FW
from mathvid.orders import cross, tick
from mathvid.script import Script
from mathvid.style import (BAD, BG, FG, GOOD, MUTED, PRIMARY, SECONDARY, TERTIARY, math, text,
                           title_card)
from mathvid.voice import get_speech_service

N = Script(__file__)

MATH_SCALE = 1.2  # MathTex reads smaller than Text at the same font size


def mth(*s, size=44, **kw):
    return math(*s, size=int(size * MATH_SCALE), **kw)

TITLE = "Secret sharing"
ORANGE = "#D19A66"
C5 = [PRIMARY, SECONDARY, TERTIARY, GOOD, ORANGE]  # one color per manager, in seat order
SECRET = BAD  # the hidden value on the vertical axis
DOOR = "#2A2E36"

# The running examples. Everything drawn from these is computed, not hand-placed.
LINE_S, LINE_M = 5.0, 1.1  # s03: height = 5 + 1.1 x


def line_f(x):
    return LINE_S + LINE_M * x


def para_f(x):  # s04: height = 5 + 3x - x^2/2, so 7.5, 9, 9.5, 9, 7.5 at x = 1..5
    return 5.0 + 3.0 * x - 0.5 * x * x


P = 11  # the prime dial


# ---------------------------------------------------------------------------
# Shared builders (also used by shorts.py)
# ---------------------------------------------------------------------------


def person(color=FG, s=1.0):
    head = Circle(radius=0.17 * s, color=color, fill_opacity=1, stroke_width=0)
    body = RoundedRectangle(width=0.58 * s, height=0.36 * s, corner_radius=0.17 * s, color=color,
                            fill_opacity=1, stroke_width=0)
    body.next_to(head, DOWN, buff=0.05 * s)
    return VGroup(head, body)


def managers(n=5, s=1.0, buff=0.55, colors=C5):
    return VGroup(*[person(colors[i % len(colors)], s) for i in range(n)]).arrange(RIGHT, buff=buff)


def vault(size=2.6):
    """A vault: dark opening, a glowing inside, and a door with a dial that can swing open."""
    frame = RoundedRectangle(width=size + 0.36, height=size + 0.36, corner_radius=0.26, color=MUTED,
                             stroke_width=4, fill_color="#0D0F13", fill_opacity=1)
    inside = RoundedRectangle(width=size, height=size, corner_radius=0.2, stroke_width=0,
                              fill_color=PRIMARY, fill_opacity=0.3)
    plate = RoundedRectangle(width=size, height=size, corner_radius=0.2, color=FG, stroke_width=3,
                             fill_color=DOOR, fill_opacity=1)
    r = size * 0.26
    ring = Circle(radius=r, color=FG, stroke_width=4)
    ticks = VGroup(*[Line(r * 0.78 * np.array([cos(a), sin(a), 0]), r * np.array([cos(a), sin(a), 0]),
                          color=MUTED, stroke_width=2)
                     for a in np.linspace(0, TAU, 20, endpoint=False)])
    knob = Dot(radius=r * 0.18, color=FG)
    arrow = Line(ORIGIN, UP * r * 0.62, color=PRIMARY, stroke_width=5)
    dialg = VGroup(ring, ticks, arrow, knob)
    bolts = VGroup(*[Dot([size * 0.4, y, 0], radius=0.06, color=MUTED) for y in (-size * 0.3, size * 0.3)])
    door = VGroup(plate, dialg, bolts)
    g = VGroup(frame, inside, door)
    g.door, g.inside, g.frame = door, inside, frame
    return g


def open_door(v):
    v.door.save_state()
    return v.door.animate.stretch(0.07, 0, about_edge=LEFT)


def dial(n=10, r=1.4, size=34):
    """A combination dial with n positions; the needle starts at 0 and turns clockwise."""
    ring = Circle(radius=r, color=MUTED, stroke_width=4)
    nums = VGroup()
    for k in range(n):
        a = PI / 2 - TAU * k / n
        nums.add(mth(str(k), size=size).move_to(r * 0.76 * np.array([cos(a), sin(a), 0])))
    hub = Dot(radius=0.08, color=FG)
    needle = Line(ORIGIN, UP * r * 0.5, color=PRIMARY, stroke_width=6)
    g = VGroup(ring, nums, needle, hub)
    g.ring, g.nums, g.needle, g.hub, g.n = ring, nums, needle, hub, n
    return g


def turn(d, clicks, run_time=1.0):
    return Rotate(d.needle, angle=-TAU * clicks / d.n, about_point=d.hub.get_center(), run_time=run_time)


def padlock(label, color=SECRET, s=1.0):
    body = RoundedRectangle(width=1.1 * s, height=0.9 * s, corner_radius=0.12 * s, color=color,
                            fill_color=color, fill_opacity=0.2, stroke_width=4)
    shackle = Arc(radius=0.34 * s, start_angle=0, angle=PI, color=color, stroke_width=6)
    shackle.next_to(body, UP, buff=-0.02)
    lab = mth(label, size=48 * s, color=FG).move_to(body)
    return VGroup(shackle, body, lab)


def chip(s, color=FG, size=40):
    """A share: a number in a small rounded box."""
    t = mth(s, size=size, color=color)
    box = SurroundingRectangle(t, color=color, buff=0.14, corner_radius=0.1, stroke_width=3)
    return VGroup(box, t)


# --- the plane -------------------------------------------------------------

XMAX = 5.7


def plane(ymax=12.5, ystep=2, x_length=8.4, y_length=6.4, ylabels=True, size=32):
    ax = Axes(x_range=[0, XMAX, 1], y_range=[0, ymax, ystep], x_length=x_length, y_length=y_length,
              tips=False, axis_config={"color": MUTED, "stroke_width": 3, "include_ticks": True})
    labs = VGroup(*[mth(str(k), size=size, color=MUTED).next_to(ax.c2p(k, 0), DOWN, 0.18)
                    for k in range(1, 6)])
    ax.xl = labs
    g = VGroup(ax, labs)
    if ylabels:
        yl = VGroup(*[mth(str(k), size=size - 4, color=MUTED).next_to(ax.c2p(0, k), LEFT, 0.15)
                      for k in range(ystep, int(ymax) + 1, ystep)])
        g.add(yl)
        ax.yl = yl
    g.ax = ax
    return g


def curve(ax, f, color=FG, width=4, x0=0.0, x1=XMAX, ymin=0.0, ymax=None, n=160, opacity=1.0):
    """The graph of f over [x0, x1], cut where it leaves the plotting box."""
    ymax = ymax if ymax is not None else ax.y_range[1]
    runs, run = [], []
    for x in np.linspace(x0, x1, n):
        y = f(x)
        if ymin - 1e-9 <= y <= ymax + 1e-9:
            run.append(ax.c2p(x, y))
        else:
            if len(run) > 1:
                runs.append(run)
            run = []
    if len(run) > 1:
        runs.append(run)
    g = VGroup()
    for r in runs:
        g.add(VMobject(color=color, stroke_width=width, stroke_opacity=opacity).set_points_as_corners(r))
    return g


def pdot(ax, x, y, color=FG, r=0.11):
    return Dot(ax.c2p(x, y), radius=r, color=color).set_stroke(BG, width=2, background=True)


def interp(points):
    """Coefficients (c0, c1, ...) of the polynomial through the given (x, y) points."""
    xs = np.array([p[0] for p in points], dtype=float)
    ys = np.array([p[1] for p in points], dtype=float)
    V = np.vander(xs, len(xs), increasing=True)
    return np.linalg.solve(V, ys)


def poly(c):
    return lambda x: sum(ci * x ** i for i, ci in enumerate(c))


# --- the prime grid ----------------------------------------------------------


class ModGrid(VGroup):
    """A P by P grid of dots: x = 0..P-1 to the right, height 0..P-1 up. Column 0 is the axis."""

    def __init__(self, p=P, step=0.5, center=ORIGIN, labels=True, size=22, **kw):
        super().__init__(**kw)
        self.pp, self.step, self.c = p, step, np.array(center, dtype=float)
        self.dots = {}
        self.col = RoundedRectangle(width=step * 0.8, height=step * (p - 0.2), corner_radius=step * 0.3,
                                    stroke_width=0, fill_color=SECRET, fill_opacity=0.14)
        self.col.move_to(self.p(0, (p - 1) / 2))
        self.add(self.col)
        self.grid = VGroup()
        for x in range(p):
            for y in range(p):
                d = Dot(self.p(x, y), radius=0.045 * step / 0.5, color=MUTED)
                self.dots[(x, y)] = d
                self.grid.add(d)
        self.add(self.grid)
        if labels:
            self.xl = VGroup(*[mth(str(x), size=size, color=MUTED).move_to(self.p(x, -1.1))
                               for x in range(p)])
            self.yl = VGroup(*[mth(str(y), size=size, color=MUTED).move_to(self.p(-1.2, y))
                               for y in range(p)])
            self.add(self.xl, self.yl)

    def p(self, x, y):
        return self.c + self.step * np.array([x - (self.pp - 1) / 2, y - (self.pp - 1) / 2, 0])


def mod_line(G, m, s, color=PRIMARY, width=4, dot_r=0.075):
    """height = m x + s, wrapping: segments that leave the top come back in at the bottom."""
    p = G.pp
    segs = VGroup()
    for x in range(p - 1):
        y = (m * x + s) % p
        yn = y + m
        if yn <= p - 1:
            segs.add(Line(G.p(x, y), G.p(x + 1, yn), color=color, stroke_width=width))
        else:
            t = (p - 0.5 - y) / m
            segs.add(Line(G.p(x, y), G.p(x + t, p - 0.5), color=color, stroke_width=width))
            segs.add(Line(G.p(x + t, -0.5), G.p(x + 1, yn - p), color=color, stroke_width=width))
    dots = VGroup(*[Dot(G.p(x, (m * x + s) % p), radius=dot_r * G.step / 0.5, color=color)
                    for x in range(p)])
    g = VGroup(segs, dots)
    g.segs, g.dots = segs, dots
    return g


def mod_line_steps(G, m, s, color=PRIMARY, width=4):
    """The same line as a list of per-step groups, for drawing it one step at a time."""
    p = G.pp
    steps = []
    for x in range(p - 1):
        y = (m * x + s) % p
        yn = y + m
        g = VGroup()
        if yn <= p - 1:
            g.add(Line(G.p(x, y), G.p(x + 1, yn), color=color, stroke_width=width))
        else:
            t = (p - 0.5 - y) / m
            g.add(Line(G.p(x, y), G.p(x + t, p - 0.5), color=color, stroke_width=width))
            g.add(Line(G.p(x + t, -0.5), G.p(x + 1, yn - p), color=color, stroke_width=width))
        g.add(Dot(G.p(x + 1, yn % p), radius=0.075 * G.step / 0.5, color=color))
        steps.append(g)
    return steps


def mod_poly_dots(G, c, color=PRIMARY, r=0.075):
    p = G.pp
    return VGroup(*[Dot(G.p(x, int(sum(ci * x ** i for i, ci in enumerate(c))) % p),
                        radius=r * G.step / 0.5, color=color) for x in range(p)])


def mod_para_through(a, b, s, p=P):
    """Coefficients (s, c1, c2) mod p of the parabola through (0, s) and the points a, b."""
    (x1, y1), (x2, y2) = a, b
    # y_i - s = c1 x_i + c2 x_i^2. Solve the 2x2 system mod p.
    det = (x1 * x2 * x2 - x2 * x1 * x1) % p
    inv = pow(det, p - 2, p)
    r1, r2 = (y1 - s) % p, (y2 - s) % p
    c1 = ((r1 * x2 * x2 - r2 * x1 * x1) * inv) % p
    c2 = ((x1 * r2 - x2 * r1) * inv) % p
    return (s, c1, c2)


def qr_like(n=21, cell=0.13, seed=3):
    """A QR-style grid of squares with three finder corners. Decorative, not a real code."""
    rng = np.random.default_rng(seed)
    g = VGroup()
    finder = set()
    for (cx, cy) in [(0, 0), (n - 7, 0), (0, n - 7)]:
        for i in range(7):
            for j in range(7):
                finder.add((cx + i, cy + j))
                edge = i in (0, 6) or j in (0, 6)
                core = 2 <= i <= 4 and 2 <= j <= 4
                if edge or core:
                    g.add(Square(cell, stroke_width=0, fill_color=FG, fill_opacity=1)
                          .move_to([(cx + i) * cell, -(cy + j) * cell, 0]))
    for i in range(n):
        for j in range(n):
            if (i, j) not in finder and rng.random() < 0.5:
                g.add(Square(cell, stroke_width=0, fill_color=FG, fill_opacity=1).move_to([i * cell, -j * cell, 0]))
    bg = Square(cell * (n + 2), stroke_width=0, fill_color=MUTED, fill_opacity=0.25).move_to(g.get_center())
    return VGroup(bg, g)


# ---------------------------------------------------------------------------
# s01 Hook
# ---------------------------------------------------------------------------


class S01Hook(VoiceoverScene):
    def construct(self):
        self.set_speech_service(get_speech_service())
        v = vault(3.2).move_to(UP * 1.35)
        mg = managers(5, s=1.6, buff=0.85).move_to(DOWN * 2.35)
        with self.voiceover(text=N("s01.b1")) as tr:
            self.play(FadeIn(v), run_time=0.8)
            self.play(LaggedStart(*[FadeIn(m, shift=UP * 0.2) for m in mg], lag_ratio=0.2), run_time=1.2)
            wait_until(self, tr, "three")
            self.play(*[mg[i].animate.scale(1.15) for i in (0, 2, 3)],
                      *[mg[i].animate.set_opacity(0.25) for i in (1, 4)], run_time=0.5)
            self.play(open_door(v), run_time=0.8)
            wait_until(self, tr, "two")
            qs = VGroup(*[text("?", size=72, color=MUTED, weight="BOLD").next_to(mg[i], UP, 0.25) for i in (1, 3)])
            self.play(Restore(v.door), run_time=0.6)
            self.play(mg[0].animate.scale(1 / 1.15).set_opacity(0.25), mg[2].animate.scale(1 / 1.15).set_opacity(0.25),
                      mg[3].animate.scale(1 / 1.15), mg[1].animate.set_opacity(1), mg[4].animate.set_opacity(0.25),
                      run_time=0.5)
            self.play(FadeIn(qs, scale=0.6), run_time=0.5)
            rest(self, tr)

        g1 = text("first digit?", size=48).move_to([-4.6, 1.35, 0])
        g2 = text("even?", size=48).move_to([4.6, 1.35, 0])
        stranger = person(MUTED, s=1.6)
        sq = text("?", size=72, color=MUTED, weight="BOLD")
        with self.voiceover(text=N("s01.b2")) as tr:
            self.play(FadeIn(g1, shift=UP * 0.2), run_time=0.5)
            self.play(Create(strike(g1)), run_time=0.4)
            self.play(FadeIn(g2, shift=UP * 0.2), run_time=0.5)
            self.play(Create(strike(g2)), run_time=0.4)
            self.play(VGroup(mg, qs).animate.shift(LEFT * 1.1), run_time=0.5)
            stranger.next_to(mg, RIGHT, 1.1)
            sq.next_to(stranger, UP, 0.25)
            self.play(FadeIn(stranger), FadeIn(sq), run_time=0.7)
            rest(self, tr)

        a, b = np.array([-2.5, -1.4, 0]), np.array([2.5, 1.4, 0])
        da, db = Dot(a, radius=0.14, color=PRIMARY), Dot(b, radius=0.14, color=SECONDARY)
        ln = Line(a + (a - b) * 0.6, b + (b - a) * 0.6, color=FG, stroke_width=5)
        with self.voiceover(text=N("s01.b3")) as tr:
            self.play(FadeOut(Group(*self.mobjects)), run_time=0.6)
            self.play(FadeIn(da, scale=0.5), FadeIn(db, scale=0.5), run_time=0.5)
            wait_until(self, tr, "line")
            self.play(Create(ln), run_time=rt(min(1.0, tr.get_remaining_duration())))
            rest(self, tr)
        self.wait(0.4)
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.5)
        title_card(self, TITLE)


# ---------------------------------------------------------------------------
# s02 When everyone is needed
# ---------------------------------------------------------------------------


class S02Everyone(VoiceoverScene):
    def construct(self):
        self.set_speech_service(get_speech_service())
        d = dial(10, r=1.9, size=40).move_to([0, 0.3, 0])
        lock = padlock("7", s=1.25).move_to([-4.6, 0.6, 0])
        lock_lab = text("secret", size=36, color=SECRET).next_to(lock, DOWN, 0.3)
        pa, pb = person(PRIMARY, 1.6), person(SECONDARY, 1.6)
        VGroup(pa, pb).arrange(RIGHT, buff=1.6).move_to([4.4, 1.6, 0])
        with self.voiceover(text=N("s02.b1")) as tr:
            self.play(FadeIn(d), run_time=0.8)
            self.play(FadeIn(pa), FadeIn(pb), run_time=0.6)
            wait_until(self, tr, "seven")
            self.play(FadeIn(lock, scale=0.8), FadeIn(lock_lab), run_time=0.6)
            rest(self, tr)

        ca = chip("9", PRIMARY, 60).next_to(pa, DOWN, 0.4)
        cb = chip("8", SECONDARY, 60).next_to(pb, DOWN, 0.4)
        sum_t = mth(r"9 + 8 = 1", r"7", size=60).move_to([4.4, -1.7, 0])
        sum_t[1].set_color(SECRET)
        with self.voiceover(text=N("s02.b2")) as tr:
            wait_until(self, tr, "nine")
            self.play(FadeIn(ca, shift=DOWN * 0.2), run_time=0.5)
            wait_until(self, tr, "eight")
            self.play(FadeIn(cb, shift=DOWN * 0.2), run_time=0.5)
            self.play(FadeIn(sum_t), run_time=0.5)
            self.play(Indicate(sum_t[1], color=SECRET), run_time=0.7)
            wait_until(self, tr, "dial")
            total = tr.get_remaining_duration()
            self.play(turn(d, 9, run_time=rt(total * 0.35)), Indicate(ca, color=PRIMARY, run_time=rt(total * 0.35)))
            self.play(turn(d, 8, run_time=rt(total * 0.35)), Indicate(cb, color=SECONDARY, run_time=rt(total * 0.35)))
            self.play(Indicate(d.nums[7], color=SECRET, scale_factor=1.6), run_time=0.6)
            rest(self, tr)

        # B alone: every secret fits some first digit.
        cards = VGroup()
        for s in range(10):
            a = (s - 8) % 10
            row = VGroup(mth(str(a), size=46, color=PRIMARY), mth(r"+\,8 \to", size=46),
                         mth(str(s), size=46, color=SECRET)).arrange(RIGHT, buff=0.18)
            cards.add(row)
        cards.arrange_in_grid(rows=5, cols=2, buff=(1.3, 0.32), flow_order="dr").move_to([-0.1, -0.45, 0])
        hdr = VGroup(text("first digit", size=34, color=PRIMARY), text("secret", size=34, color=SECRET))
        hdr[0].next_to(cards, UP, 0.4).align_to(cards, LEFT)
        hdr[1].next_to(cards, UP, 0.4).align_to(cards, RIGHT)
        each = text("each first digit: 1 in 10", size=36, color=MUTED).next_to(cards, DOWN, 0.4)
        unknown = mth(r"\text{secret} = \,?", size=48, color=SECRET).move_to([5.2, -1.5, 0])
        with self.voiceover(text=N("s02.b3")) as tr:
            self.play(FadeOut(VGroup(ca, sum_t, lock, lock_lab, pa)),
                      d.animate.scale(0.6).move_to([-5.0, 1.2, 0]), run_time=0.8)
            self.play(VGroup(pb, cb).animate.move_to([5.2, 0.6, 0]), run_time=0.6)
            self.play(FadeIn(unknown), run_time=0.5)
            wait_until(self, tr, "any")
            self.play(FadeIn(hdr), LaggedStart(*[FadeIn(c, shift=RIGHT * 0.2) for c in cards], lag_ratio=0.15),
                      run_time=rt(min(2.5, tr.get_remaining_duration() - 1.2)))
            self.play(FadeIn(each), run_time=0.5)
            rest(self, tr)

        # Any number of people, and longer secrets.
        four = VGroup(*[person(c, 1.4) for c in (PRIMARY, SECONDARY, TERTIARY, GOOD)]).arrange(RIGHT, buff=1.0)
        four.move_to([-3.0, 1.9, 0])
        digs = ["3", "9", "4", "1"]
        fchips = VGroup(*[chip(dg, c, 56).next_to(p, DOWN, 0.35) for dg, c, p in
                          zip(digs, (PRIMARY, SECONDARY, TERTIARY, GOOD), four)])
        fsum = mth(r"3 + 9 + 4 + 1 = 1", r"7", size=54).next_to(fchips, DOWN, 0.6)
        fsum[1].set_color(SECRET)
        fix = text("fixes the sum", size=34, color=GOOD).next_to(fchips[3], RIGHT, 0.3)
        sec = "7305"
        a_d, b_d = "4819", "".join(str((int(s) - int(a)) % 10) for s, a in zip(sec, "4819"))
        long_s = VGroup(text("secret", size=36, color=SECRET), mth(r"\;\;".join(sec), size=60, color=SECRET))
        long_a = VGroup(text("first", size=36, color=PRIMARY), mth(r"\;\;".join(a_d), size=60, color=PRIMARY))
        long_b = VGroup(text("second", size=36, color=SECONDARY), mth(r"\;\;".join(b_d), size=60, color=SECONDARY))
        for g in (long_s, long_a, long_b):
            g.arrange(RIGHT, buff=0.4)
        rows = VGroup(long_s, long_a, long_b).arrange(DOWN, buff=0.4, aligned_edge=RIGHT).move_to([3.4, -1.6, 0])
        with self.voiceover(text=N("s02.b4")) as tr:
            self.play(FadeOut(VGroup(cards, hdr, each, pb, cb, d, unknown)), run_time=0.6)
            self.play(FadeIn(four), run_time=0.5)
            self.play(LaggedStart(*[FadeIn(c, shift=DOWN * 0.2) for c in fchips[:3]], lag_ratio=0.3), run_time=0.9)
            self.play(FadeIn(fchips[3], shift=DOWN * 0.2), FadeIn(fix), run_time=0.5)
            self.play(FadeIn(fsum), run_time=0.5)
            t = tr.get_remaining_duration()
            self.play(VGroup(four, fchips, fsum, fix).animate.scale(0.8).to_corner(UL, buff=0.5), run_time=0.6)
            self.play(FadeIn(long_s), run_time=0.4)
            self.play(FadeIn(long_a), FadeIn(long_b), run_time=rt(min(1.0, t - 1.2)))
            rest(self, tr)

        mg = managers(5, s=1.3, buff=1.4).move_to([0, 2.6, 0])
        labs = VGroup(*[mth(str(i + 1), size=36, color=MUTED).next_to(m, DOWN, 0.15) for i, m in enumerate(mg)])
        groups = list(combinations(range(5), 3))
        tri = VGroup()
        for g in groups:
            dots = VGroup(*[Dot(radius=0.17, color=C5[i]) for i in g]).arrange(RIGHT, buff=0.14)
            tri.add(VGroup(SurroundingRectangle(dots, color=MUTED, buff=0.12, corner_radius=0.12, stroke_width=2),
                           dots))
        tri.arrange_in_grid(rows=2, cols=5, buff=(0.55, 0.45)).move_to([0, 0.1, 0])
        stacks = VGroup()
        for i, m in enumerate(mg):
            st = VGroup(*[RoundedRectangle(width=0.6, height=0.15, corner_radius=0.05, stroke_width=0,
                                           fill_color=C5[i], fill_opacity=0.9) for _ in range(6)])
            st.arrange(UP, buff=0.05)
            lab = mth(r"\times 6", size=38, color=C5[i])
            stacks.add(VGroup(st, lab).arrange(RIGHT, buff=0.12))
        for st, m in zip(stacks, mg):
            st.move_to([m.get_x() + 0.15, -2.4, 0])
        with self.voiceover(text=N("s02.b5")) as tr:
            self.play(FadeOut(VGroup(four, fchips, fsum, fix, rows)), run_time=0.6)
            self.play(FadeIn(mg), FadeIn(labs), run_time=0.6)
            wait_until(self, tr, "groups")
            self.play(LaggedStart(*[FadeIn(t, scale=0.8) for t in tri], lag_ratio=0.12), run_time=1.6)
            self.play(LaggedStart(*[FadeIn(s, shift=UP * 0.2) for s in stacks], lag_ratio=0.15),
                      run_time=rt(min(1.4, tr.get_remaining_duration())))
            rest(self, tr)

        n100 = text("any 51 of 100", size=60).move_to(UP * 1.5)
        ex = ValueTracker(1)
        cnt = always_redraw(lambda: VGroup(text("about", size=52, color=MUTED),
                                           mth(r"10^{%d}" % int(round(ex.get_value())), size=80, color=BAD),
                                           text("splits", size=52, color=MUTED))
                            .arrange(RIGHT, buff=0.3).move_to(DOWN * 0.3))
        check = mth(r"\tbinom{100}{51} \approx %.1f \times 10^{28}" % (comb(100, 51) / 1e28), size=40,
                     color=MUTED).move_to(DOWN * 1.9)
        with self.voiceover(text=N("s02.b6")) as tr:
            self.play(FadeOut(VGroup(mg, labs, tri, stacks)), run_time=0.6)
            self.play(FadeIn(n100), FadeIn(cnt), run_time=0.5)
            wait_until(self, tr, "big")
            self.play(ex.animate.set_value(29), run_time=1.2, rate_func=linear)
            self.play(FadeIn(check), run_time=0.5)
            rest(self, tr)
        self.wait(0.3)
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.6)


# ---------------------------------------------------------------------------
# s03 Two points make a line
# ---------------------------------------------------------------------------


PL_C = [-1.7, -0.15, 0]  # where the plane sits in s03/s04


def share_panel(f, colors=C5, size=40):
    """The five managers in a column, each with their share (x, height)."""
    rows = VGroup()
    for i in range(5):
        x = i + 1
        rows.add(VGroup(person(colors[i], 0.95),
                        mth(r"(%d,\ %s)" % (x, ("%.1f" % f(x)).rstrip("0").rstrip(".")), size=size,
                             color=colors[i])).arrange(RIGHT, buff=0.3))
    rows.arrange(DOWN, buff=0.38, aligned_edge=LEFT)
    return rows


class S03Line(VoiceoverScene):
    def construct(self):
        self.set_speech_service(get_speech_service())
        pg = plane().move_to(PL_C)
        ax = pg.ax
        sdot = pdot(ax, 0, LINE_S, SECRET, r=0.14)
        slab = text("secret", size=36, color=SECRET).next_to(sdot, DR, 0.12)
        ln = curve(ax, line_f, FG, 4)
        with self.voiceover(text=N("s03.b1")) as tr:
            self.play(Create(pg), run_time=1.0)
            wait_until(self, tr, "secret")
            self.play(FadeIn(sdot, scale=0.5), FadeIn(slab), run_time=0.6)
            wait_until(self, tr, "random")
            self.play(Create(ln), run_time=1.0)
            rest(self, tr)

        pts = VGroup(*[pdot(ax, x, line_f(x), C5[x - 1]) for x in range(1, 6)])
        panel = share_panel(line_f).move_to([4.9, -0.2, 0])
        with self.voiceover(text=N("s03.b2")) as tr:
            wait_until(self, tr, "points")
            self.play(LaggedStart(*[FadeIn(p, scale=0.5) for p in pts], lag_ratio=0.25), run_time=1.2)
            self.play(LaggedStart(*[FadeIn(r, shift=LEFT * 0.2) for r in panel], lag_ratio=0.2),
                      run_time=rt(min(1.4, tr.get_remaining_duration())))
            rest(self, tr)

        keep = (1, 3)  # managers 2 and 4
        ln2 = curve(ax, line_f, GOOD, 5)
        ring = Circle(radius=0.28, color=GOOD, stroke_width=5).move_to(sdot)
        with self.voiceover(text=N("s03.b3")) as tr:
            self.play(FadeOut(ln), FadeOut(sdot), FadeOut(slab),
                      *[pts[i].animate.set_opacity(0.15) for i in range(5) if i not in keep],
                      *[panel[i].animate.set_opacity(0.25) for i in range(5) if i not in keep], run_time=0.8)
            wait_until(self, tr, "draw")
            self.play(Create(ln2), run_time=0.9)
            self.play(FadeIn(sdot, scale=0.5), Create(ring), run_time=0.6)
            rest(self, tr)

        one = 1  # manager 2 alone, at (2, 7.2)
        px, py = 2, line_f(2)
        fan = VGroup()
        hits = VGroup()
        for s in np.arange(0, 12.01, 1.0):
            m = (py - s) / px
            fan.add(curve(ax, lambda x, s=s, m=m: s + m * x, SECONDARY, 2.5, opacity=0.55))
            hits.add(pdot(ax, 0, s, SECRET, r=0.07))
        how = text("how many lines?", size=40, color=SECONDARY).move_to([-1.6, 3.55, 0])
        with self.voiceover(text=N("s03.b4")) as tr:
            self.play(FadeOut(ln2), FadeOut(ring), FadeOut(sdot), pts[3].animate.set_opacity(0.15),
                      panel[3].animate.set_opacity(0.25), run_time=0.7)
            self.play(pts[one].animate.scale(1.6), run_time=0.5)
            self.play(FadeIn(how), run_time=0.5)
            wait_until(self, tr, "fan")
            self.play(LaggedStart(*[AnimationGroup(Create(f), FadeIn(h)) for f, h in zip(fan, hits)],
                                  lag_ratio=0.25), run_time=rt(min(3.0, tr.get_remaining_duration() - 0.3)))
            self.add_foreground_mobject(pts[one])
            rest(self, tr)

        nothing = text("one point: nothing?", size=38, color=SECONDARY)
        every = text("two points: everything", size=38, color=GOOD)
        VGroup(nothing, every).arrange(DOWN, buff=0.35, aligned_edge=LEFT).move_to([4.2, 0.6, 0])
        with self.voiceover(text=N("s03.b5")) as tr:
            self.play(FadeOut(panel), FadeOut(how), run_time=0.6)
            self.play(FadeIn(nothing), run_time=0.5)
            self.play(FadeIn(every), run_time=0.5)
            rest(self, tr)
        self.wait(0.3)
        self.remove_foreground_mobject(pts[one])
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.6)


# ---------------------------------------------------------------------------
# s04 Three points make a parabola
# ---------------------------------------------------------------------------


class S04Parabola(VoiceoverScene):
    def construct(self):
        self.set_speech_service(get_speech_service())
        pg = plane().move_to(PL_C)
        ax = pg.ax
        sdot = pdot(ax, 0, para_f(0), SECRET, r=0.14)
        slab = text("secret", size=36, color=SECRET).next_to(sdot, DR, 0.12)
        pc = curve(ax, para_f, FG, 4)
        pts = VGroup(*[pdot(ax, x, para_f(x), C5[x - 1]) for x in range(1, 6)])
        panel = share_panel(para_f).move_to([4.9, -0.2, 0])
        with self.voiceover(text=N("s04.b1")) as tr:
            self.play(FadeIn(pg), run_time=0.6)
            wait_until(self, tr, "para")
            self.play(FadeIn(sdot, scale=0.5), FadeIn(slab), run_time=0.5)
            self.play(Create(pc), run_time=1.0)
            self.play(LaggedStart(*[FadeIn(p, scale=0.5) for p in pts], lag_ratio=0.2), run_time=1.0)
            self.play(LaggedStart(*[FadeIn(r, shift=LEFT * 0.2) for r in panel], lag_ratio=0.2),
                      run_time=rt(min(1.2, tr.get_remaining_duration())))
            rest(self, tr)

        keep = (0, 2, 4)
        c3 = interp([(x + 1, para_f(x + 1)) for x in keep])
        pc2 = curve(ax, poly(c3), GOOD, 5)
        ring = Circle(radius=0.28, color=GOOD, stroke_width=5).move_to(sdot)
        with self.voiceover(text=N("s04.b2")) as tr:
            self.play(FadeOut(pc), FadeOut(sdot), FadeOut(slab),
                      *[pts[i].animate.set_opacity(0.15) for i in range(5) if i not in keep],
                      *[panel[i].animate.set_opacity(0.25) for i in range(5) if i not in keep], run_time=0.8)
            wait_until(self, tr, "fit")
            self.play(Create(pc2), run_time=0.9)
            self.play(FadeIn(sdot, scale=0.5), Create(ring), run_time=0.6)
            rest(self, tr)

        two = (1, 3)  # managers 2 and 4, at (2, 9) and (4, 9)
        A, B = (2, para_f(2)), (4, para_f(4))
        hs = ValueTracker(2.0)
        third = always_redraw(lambda: pdot(ax, 0, hs.get_value(), SECRET, r=0.12))
        live = always_redraw(lambda: curve(ax, poly(interp([(0, hs.get_value()), A, B])), SECONDARY, 4))
        fan = VGroup()
        for s in np.arange(0, 12.01, 1.0):
            fan.add(curve(ax, poly(interp([(0, s), A, B])), SECONDARY, 2.2, opacity=0.4))
        with self.voiceover(text=N("s04.b3")) as tr:
            self.play(FadeOut(pc2), FadeOut(ring), FadeOut(sdot),
                      *[pts[i].animate.set_opacity(1 if i in two else 0.15) for i in range(5)],
                      *[panel[i].animate.set_opacity(1 if i in two else 0.25) for i in range(5)], run_time=0.7)
            self.play(FadeIn(third, scale=0.5), run_time=0.4)
            self.play(Create(live), run_time=0.8)
            t = tr.time_until_bookmark("fan")
            self.play(hs.animate.set_value(10.0), run_time=rt(t))
            self.play(LaggedStart(*[Create(f) for f in fan], lag_ratio=0.15),
                      hs.animate.set_value(6.0), run_time=rt(min(2.4, tr.get_remaining_duration() - 0.2)))
            self.add_foreground_mobjects(pts[1], pts[3])
            rest(self, tr)

        rows = [("2 people", "line"), ("3 people", "parabola"), ("4 people", "cubic"),
                ("k people", "degree k - 1")]
        tab = VGroup(*[m for a, b in rows for m in (text(a, size=46), text(b, size=46, color=PRIMARY))])
        tab.arrange_in_grid(rows=4, cols=2, buff=(1.0, 0.32), col_alignments="ll").move_to([0, 1.5, 0])
        tab_rows = [VGroup(tab[2 * i], tab[2 * i + 1]) for i in range(4)]
        hundred = VGroup(*[person(C5[i % 5], 0.48) for i in range(100)])
        hundred.arrange_in_grid(rows=4, cols=25, buff=(0.14, 0.12)).move_to([0, -2.6, 0])
        one_n = text("each holds one number", size=38, color=PRIMARY).next_to(hundred, UP, 0.3)
        with self.voiceover(text=N("s04.b4")) as tr:
            self.remove_foreground_mobjects(pts[1], pts[3])
            self.play(FadeOut(Group(*self.mobjects)), run_time=0.6)
            self.play(LaggedStart(*[FadeIn(r, shift=RIGHT * 0.2) for r in tab_rows], lag_ratio=0.35),
                      run_time=rt(min(2.4, tr.time_until_bookmark("one") - 0.8)))
            wait_until(self, tr, "one")
            self.play(FadeIn(hundred, lag_ratio=0.01), FadeIn(one_n), run_time=0.9)
            rest(self, tr)
        self.wait(0.3)
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.6)


# ---------------------------------------------------------------------------
# s05 The catch
# ---------------------------------------------------------------------------


GRID_C = [-2.5, -0.05, 0]
Y0 = 7  # the manager at x = 1 holds height 7 on the prime grid (the line 4x + 3 goes through it)


class S05Catch(VoiceoverScene):
    def construct(self):
        self.set_speech_service(get_speech_service())
        # Real numbers: a manager at 1 holding 50.
        pg = plane(ymax=100, ystep=20, x_length=7.4, y_length=6.4).move_to([-2.4, -0.15, 0])
        ax = pg.ax
        P1 = pdot(ax, 1, 50, PRIMARY, r=0.13)
        p1lab = mth(r"(1,\ 50)", size=40, color=PRIMARY).next_to(P1, UR, 0.1)
        fan = VGroup()
        for s in np.arange(0, 100.01, 6.25):
            fan.add(curve(ax, lambda x, s=s: s + (50 - s) * x, SECONDARY, 2.2, opacity=0.5))
        with self.voiceover(text=N("s05.b1")) as tr:
            self.play(FadeIn(pg), FadeIn(P1), FadeIn(p1lab), run_time=0.8)
            self.play(LaggedStart(*[Create(f) for f in fan], lag_ratio=0.12), run_time=1.8)
            self.add_foreground_mobjects(P1)
            sl = text("slope: any real number,", size=40).move_to([4.4, 1.6, 0])
            sl2 = text("all equally likely?", size=40).next_to(sl, DOWN, 0.2)
            no = cross(sl2.get_right() + RIGHT * 0.4, s=0.2)
            self.play(FadeIn(sl), FadeIn(sl2), run_time=0.6)
            self.wait(rt(tr.get_remaining_duration() - 1.0))
            self.play(Create(no), run_time=0.4)
            rest(self, tr)

        narrow = VGroup()
        for m in np.arange(-10, 10.01, 2.5):
            narrow.add(curve(ax, lambda x, m=m: 50 - m + m * x, PRIMARY, 3))
        band = Rectangle(width=0.3, height=ax.c2p(0, 60)[1] - ax.c2p(0, 40)[1], stroke_width=0,
                         fill_color=SECRET, fill_opacity=0.5).move_to(ax.c2p(0, 50))
        b_lab = VGroup(mth("40", size=40, color=SECRET), text("to", size=34, color=SECRET),
                       mth("60", size=40, color=SECRET)).arrange(DOWN, buff=0.1)
        b_lab.next_to(band, LEFT, 0.25).shift(LEFT * 0.35)
        rng = VGroup(text("slope between", size=40), mth(r"-10 \text{ and } 10", size=46)).arrange(DOWN, buff=0.2)
        rng.move_to([4.4, 0.4, 0])
        leak = text("a leak", size=52, color=BAD, weight="BOLD").next_to(rng, DOWN, 0.6)
        with self.voiceover(text=N("s05.b2")) as tr:
            self.play(FadeOut(VGroup(sl, sl2, no)), run_time=0.4)
            wait_until(self, tr, "ten")
            self.play(fan.animate.set_opacity(0.08), FadeIn(rng), run_time=0.6)
            self.play(LaggedStart(*[Create(f) for f in narrow], lag_ratio=0.1), run_time=1.2)
            self.play(FadeIn(band), FadeIn(b_lab), pg.ax.yl.animate.set_opacity(0.2), run_time=0.6)
            self.wait(rt(tr.get_remaining_duration() - 0.9))
            self.play(FadeIn(leak, scale=0.8), run_time=0.5)
            rest(self, tr)

        d11 = dial(11, r=2.1, size=40).move_to([0, 0.3, 0])
        with self.voiceover(text=N("s05.b3")) as tr:
            self.remove_foreground_mobjects(P1)
            self.play(FadeOut(Group(*self.mobjects)), run_time=0.6)
            d10 = dial(10, r=2.1, size=40).move_to([0, 0.3, 0])
            self.play(FadeIn(d10), run_time=0.6)
            self.play(turn(d10, 13, run_time=rt(min(1.5, tr.time_until_bookmark("eleven") - 0.3))))
            wait_until(self, tr, "eleven")
            self.play(ReplacementTransform(d10, d11), run_time=0.8)
            p_lab = text("11 positions (a prime)", size=40, color=PRIMARY).next_to(d11, DOWN, 0.4)
            self.play(FadeIn(p_lab), run_time=0.4)
            rest(self, tr)

        G = ModGrid(center=GRID_C, step=0.56, size=24)
        ylab = text("secret", size=32, color=SECRET).rotate(PI / 2).next_to(G.yl, LEFT, 0.2)
        form = mth(r"\text{height} = 4x + 3", size=48).move_to([4.4, 1.6, 0])
        wrapnote = text("past 10, wrap to 0", size=36, color=MUTED).next_to(form, DOWN, 0.4)
        steps = mod_line_steps(G, 4, 3, PRIMARY)
        start = Dot(G.p(0, 3), radius=0.075 * G.step / 0.5, color=PRIMARY)
        with self.voiceover(text=N("s05.b4")) as tr:
            self.play(FadeOut(d11), FadeOut(p_lab), run_time=0.5)
            self.play(FadeIn(G), FadeIn(ylab), run_time=0.8)
            self.play(FadeIn(form), run_time=0.5)
            wait_until(self, tr, "wrap")
            self.play(FadeIn(start), FadeIn(wrapnote), run_time=0.3)
            per = rt(min(0.35, (tr.get_remaining_duration() - 0.2) / len(steps)))
            for st in steps:
                self.play(Create(st), run_time=per)
            rest(self, tr)

        # Eleven lines through the manager at (1, 7).
        line43 = VGroup(*steps, start)
        mdot = Dot(G.p(1, Y0), radius=0.12, color=PRIMARY).set_stroke(BG, 2, background=True)
        mlab = mth(r"(1,\ 7)", size=36, color=PRIMARY).next_to(mdot, UR, 0.05)
        cnt = VGroup(text("11 slopes", size=44, color=SECONDARY), mth(r"\downarrow", size=44),
                     text("11 different secrets", size=44, color=SECRET)).arrange(DOWN, buff=0.15).move_to([4.4, 1.4, 0])
        each = mth(r"\text{each slope: } \tfrac{1}{11}", size=46).move_to([4.4, -0.6, 0])
        lines = []
        hits = VGroup()
        for m in range(P):
            s = (Y0 - m) % P
            lines.append(mod_line(G, m, s, SECONDARY, 3))
            hits.add(Dot(G.p(0, s), radius=0.1, color=SECRET))
        with self.voiceover(text=N("s05.b5")) as tr:
            self.play(FadeOut(line43), FadeOut(form), FadeOut(wrapnote), run_time=0.5)
            self.play(FadeIn(mdot, scale=0.5), FadeIn(mlab), FadeIn(cnt), run_time=0.6)
            self.add_foreground_mobjects(mdot)
            t = tr.time_until_bookmark("each") - 0.2
            # Before the bookmark: show the first few lines one by one.
            shown = 0
            per = 0.55
            while shown < P and t > per + 0.15:
                ln = lines[shown]
                self.play(Create(ln.segs), FadeIn(ln.dots), FadeIn(hits[shown], scale=0.5), run_time=per)
                self.play(ln.animate.set_opacity(0.12), run_time=0.15)
                t -= per + 0.15
                shown += 1
            wait_until(self, tr, "each")
            rem = P - shown
            if rem:
                per = rt(min(0.45, (tr.get_remaining_duration() - 1.4) / rem))
                for k in range(shown, P):
                    ln = lines[k]
                    self.play(Create(ln.segs), FadeIn(ln.dots), FadeIn(hits[k], scale=0.5), run_time=per)
                    self.play(ln.animate.set_opacity(0.12), run_time=0.1)
            self.play(FadeIn(each), LaggedStart(*[Indicate(h, color=SECRET, scale_factor=1.5) for h in hits], lag_ratio=0.08), run_time=0.8)
            rest(self, tr)

        # Why a prime: dividing.
        a, b = (1, 7), (3, 4)
        pa = Dot(G.p(*a), radius=0.12, color=PRIMARY).set_stroke(BG, 2, background=True)
        pb = Dot(G.p(*b), radius=0.12, color=SECONDARY).set_stroke(BG, 2, background=True)
        lab_a = mth(r"(1,\ 7)", size=36, color=PRIMARY).next_to(pa, UR, 0.05)
        lab_b = mth(r"(3,\ 4)", size=36, color=SECONDARY).next_to(pb, DR, 0.05)
        ln = mod_line(G, 4, 3, FG, 3)
        div = mth(r"\text{slope} = \frac{4 - 7}{3 - 1} = \frac{-3}{2}", size=46).move_to([4.4, 2.3, 0])
        okp = VGroup(text("11 positions:", size=38, color=GOOD),
                     text("divide by anything but 0", size=38, color=GOOD)).arrange(DOWN, buff=0.12)
        okp.move_to([4.4, 0.6, 0])
        bad10 = VGroup(text("10 positions:", size=38, color=BAD),
                       mth(r"2 \times 0 = 0", size=46), mth(r"2 \times 5 = 10 \to 0", size=46))
        bad10.arrange(DOWN, buff=0.2).move_to([4.4, -1.7, 0])
        with self.voiceover(text=N("s05.b6")) as tr:
            self.remove_foreground_mobjects(mdot)
            self.play(FadeOut(VGroup(*lines, hits, mdot, mlab, cnt, each)), run_time=0.5)
            self.play(FadeIn(pa), FadeIn(pb), FadeIn(lab_a), FadeIn(lab_b), run_time=0.5)
            self.play(Create(ln.segs), FadeIn(ln.dots), run_time=0.9)
            self.add_foreground_mobjects(pa, pb)
            self.play(FadeIn(div), run_time=0.6)
            wait_until(self, tr, "divide")
            self.play(FadeIn(okp), run_time=0.5)
            self.wait(rt(min(1.0, tr.get_remaining_duration() - 1.8)))
            self.play(FadeIn(bad10, shift=UP * 0.2), run_time=0.7)
            rest(self, tr)

        # The leak on a ten-position dial.
        self.remove_foreground_mobjects(pa, pb)
        hold = mth(r"\text{height} = \text{secret} + 2 \times \text{slope}", size=48).move_to([0, 2.2, 0])
        seat = text("manager at 2, on a ten-position dial", size=38, color=MUTED).next_to(hold, UP, 0.3)
        dbl = VGroup()
        for m in range(10):
            dbl.add(VGroup(mth(r"2 \times %d" % m, size=42), mth(r"\to %d" % ((2 * m) % 10), size=42, color=PRIMARY))
                    .arrange(RIGHT, buff=0.15))
        dbl.arrange_in_grid(rows=2, cols=5, buff=(0.55, 0.4)).move_to([0, 0.55, 0])
        evens = VGroup(*[d[1] for d in dbl])
        all_even = text("always even", size=44, color=PRIMARY).next_to(dbl, DOWN, 0.4)
        same = text("so the secret is even exactly when the height is", size=40).next_to(all_even, DOWN, 0.35)
        ev = text("even?", size=50).move_to([-0.8, -3.15, 0])
        ev_x = strike(ev)
        ev_bad = text("leaked", size=50, color=BAD, weight="BOLD").next_to(ev, RIGHT, 0.4)
        with self.voiceover(text=N("s05.b7")) as tr:
            self.play(FadeOut(Group(*self.mobjects)), run_time=0.5)
            self.play(FadeIn(seat), FadeIn(hold), run_time=0.6)
            self.play(LaggedStart(*[FadeIn(d) for d in dbl], lag_ratio=0.1),
                      run_time=rt(min(1.6, tr.time_until_bookmark("even") - 0.2)))
            wait_until(self, tr, "even")
            self.play(Indicate(evens, color=PRIMARY), FadeIn(all_even), run_time=0.8)
            self.play(FadeIn(same), run_time=0.6)
            self.play(FadeIn(ev), Create(ev_x), run_time=0.5)
            self.wait(rt(tr.get_remaining_duration() - 1.2))
            self.play(FadeOut(ev_x), FadeIn(ev_bad, scale=0.8), ev.animate.set_color(BAD), run_time=0.6)
            rest(self, tr)

        big = 2 ** 127 - 1
        digits = str(big)
        bigp = VGroup(mth(digits[:20], size=64, color=PRIMARY), mth(digits[20:], size=64, color=PRIMARY))
        bigp.arrange(DOWN, buff=0.25, aligned_edge=LEFT).move_to(UP * 0.7)
        bl = mth(r"= 2^{127} - 1 \text{, a prime}", size=44, color=MUTED).next_to(bigp, DOWN, 0.5)
        with self.voiceover(text=N("s05.b8")) as tr:
            self.play(FadeOut(Group(*self.mobjects)), run_time=0.6)
            wait_until(self, tr, "huge")
            self.play(Write(bigp), run_time=1.2)
            self.play(FadeIn(bl), run_time=0.5)
            rest(self, tr)
        self.wait(0.3)
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.6)


# ---------------------------------------------------------------------------
# s06 What goes wrong
# ---------------------------------------------------------------------------


class S06Wrong(VoiceoverScene):
    def construct(self):
        self.set_speech_service(get_speech_service())
        pg = plane().move_to(PL_C)
        ax = pg.ax
        ln = curve(ax, line_f, MUTED, 3)
        pts = VGroup(*[pdot(ax, x, line_f(x), C5[x - 1]) for x in range(1, 6)])
        zero = pdot(ax, 0, LINE_S, SECRET, r=0.15)
        zlab = text("seat 0 = the secret", size=42, color=SECRET).move_to([4.6, 2.2, 0])
        walker = person(PRIMARY, 1.3).move_to([4.6, 0.4, 0])
        wl = mth(r"\text{manager } \#0", size=40, color=PRIMARY).next_to(walker, DOWN, 0.2)
        with self.voiceover(text=N("s06.b1")) as tr:
            self.play(FadeIn(pg), Create(ln), FadeIn(pts), run_time=0.9)
            wait_until(self, tr, "zero")
            self.play(FadeIn(zero, scale=0.4), FadeIn(zlab), run_time=0.6)
            self.wait(rt(tr.get_remaining_duration() - 2.0))
            self.play(FadeIn(walker), FadeIn(wl), run_time=0.5)
            self.play(walker.animate.scale(0.7).next_to(zero, DR, 0.1), FadeOut(wl), run_time=1.0)
            rest(self, tr)

        pg2 = plane().move_to(PL_C)
        ax2 = pg2.ax
        q = pdot(ax2, 1, 9, PRIMARY, r=0.13)
        qlab = mth(r"(1,\ 9)", size=40, color=PRIMARY).next_to(q, DR, 0.1)
        l1 = curve(ax2, lambda x: 8 + 1 * x, SECONDARY, 4)
        l2 = curve(ax2, lambda x: 7 + 2 * x, SECONDARY, 4)
        h1, h2 = pdot(ax2, 0, 8, SECRET, r=0.12), pdot(ax2, 0, 7, SECRET, r=0.12)
        h1l = mth("8", size=40, color=SECRET).next_to(h1, LEFT, 0.45)
        h2l = mth("7", size=40, color=SECRET).next_to(h2, LEFT, 0.45)
        sl = text("slope: 1 or 2", size=44).move_to([4.6, 1.4, 0])
        verdict = text("secret: 8 or 7", size=46, color=BAD).next_to(sl, DOWN, 0.5)
        with self.voiceover(text=N("s06.b2")) as tr:
            self.play(FadeOut(VGroup(ln, pts, zero, zlab, walker)), run_time=0.5)
            self.remove(pg)
            self.add(pg2)
            wait_until(self, tr, "random")
            self.play(FadeIn(q, scale=0.5), FadeIn(qlab), FadeIn(sl), run_time=0.6)
            self.play(Create(l1), Create(l2), run_time=0.8)
            self.add_foreground_mobjects(q)
            wait_until(self, tr, "two")
            self.play(FadeIn(h1), FadeIn(h2), FadeIn(h1l), FadeIn(h2l), pg2.ax.yl.animate.set_opacity(0.2),
                      run_time=0.5)
            self.play(FadeIn(verdict), run_time=0.5)
            rest(self, tr)

        G = ModGrid(center=[-3.5, -0.4, 0], step=0.5, labels=False)
        even_fan = VGroup(*[mod_line(G, m, (Y0 - m) % P, SECONDARY, 2).set_opacity(0.3) for m in range(P)])
        even_hits = VGroup(*[Dot(G.p(0, s), radius=0.11, color=SECRET) for s in range(P)])
        md = Dot(G.p(1, Y0), radius=0.12, color=PRIMARY)
        G2 = ModGrid(center=[3.5, -0.4, 0], step=0.5, labels=False)
        lop_fan = VGroup(*[mod_line(G2, m, (Y0 - m) % P, BAD, 3) for m in (1, 2)])
        lop_hits = VGroup(*[Dot(G2.p(0, (Y0 - m) % P), radius=0.11, color=SECRET) for m in (1, 2)])
        md2 = Dot(G2.p(1, Y0), radius=0.12, color=PRIMARY)
        t1 = text("every slope equally likely", size=38, color=GOOD).next_to(G, UP, 0.35)
        t2 = text("only two slopes", size=38, color=BAD).next_to(G2, UP, 0.35)
        with self.voiceover(text=N("s06.b3")) as tr:
            self.remove_foreground_mobjects(q)
            self.play(FadeOut(Group(*self.mobjects)), run_time=0.5)
            self.play(FadeIn(G), FadeIn(t1), run_time=0.5)
            self.add_foreground_mobjects(md, md2)
            self.play(LaggedStart(*[Create(l.segs) for l in even_fan], lag_ratio=0.1),
                      FadeIn(md), FadeIn(even_hits), run_time=1.4)
            self.play(FadeIn(G2), FadeIn(t2), FadeIn(md2), run_time=0.5)
            self.play(Create(lop_fan[0].segs), Create(lop_fan[1].segs), FadeIn(lop_hits), run_time=0.8)
            rest(self, tr)
        self.wait(0.3)
        self.remove_foreground_mobjects(md, md2)
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.6)


# ---------------------------------------------------------------------------
# s07 Ending
# ---------------------------------------------------------------------------


LIE_X, LIE_Y = 4, 5.0


class S07Ending(VoiceoverScene):
    def construct(self):
        self.set_speech_service(get_speech_service())
        name = text("Adi Shamir, 1979", size=72, weight="BOLD").move_to(UP * 0.4)
        rsa = text("the S in RSA", size=44, color=MUTED).next_to(name, DOWN, 0.45)
        with self.voiceover(text=N("s07.b1")) as tr:
            self.play(FadeIn(name, shift=UP * 0.2), run_time=0.7)
            self.wait(rt(tr.get_remaining_duration() - 1.2))
            self.play(FadeIn(rsa), run_time=0.5)
            rest(self, tr)

        pg = plane(x_length=7.2).move_to([-2.9, -0.15, 0])
        ax = pg.ax
        pc = curve(ax, para_f, MUTED, 3)
        pts = VGroup(*[pdot(ax, x, para_f(x), C5[x - 1], r=0.13) for x in range(1, 6)])
        liar = pts[LIE_X - 1]
        with self.voiceover(text=N("s07.b2")) as tr:
            self.play(FadeOut(name), FadeOut(rsa), run_time=0.5)
            self.play(FadeIn(pg), Create(pc), run_time=0.9)
            self.play(LaggedStart(*[FadeIn(p, scale=0.5) for p in pts], lag_ratio=0.15), run_time=0.8)
            wait_until(self, tr, "liar")
            self.play(liar.animate.move_to(ax.c2p(LIE_X, LIE_Y)).set_color(BAD), run_time=0.8)
            rest(self, tr)

        honest = [(x, para_f(x)) for x in (1, 2, 3, 5)]
        # Other parabolas through the liar and two honest points: three of five, never more.
        tries = [[(1, para_f(1)), (2, para_f(2))], [(3, para_f(3)), (5, para_f(5))], [(1, para_f(1)), (5, para_f(5))]]
        others = VGroup(*[curve(ax, poly(interp(t + [(LIE_X, LIE_Y)])), BAD, 2.5, opacity=0.7) for t in tries])
        true_c = curve(ax, para_f, GOOD, 5)
        c4 = text("true parabola: 4 of 5", size=38, color=GOOD).move_to([4.5, 1.6, 0])
        c3 = text("any other: at most 3", size=38, color=BAD).next_to(c4, DOWN, 0.4)
        qr = qr_like().scale(0.95).move_to([4.6, -1.5, 0])
        smudge = Ellipse(width=1.1, height=0.8, stroke_width=0, fill_color="#5A5F68", fill_opacity=0.9)
        smudge.move_to(qr.get_corner(DR) + UL * 0.65)
        ok = tick(at=qr.get_bottom() + DOWN * 0.45, s=1.6)
        with self.voiceover(text=N("s07.b3")) as tr:
            self.play(FadeOut(pc), Create(true_c), run_time=0.8)
            self.add_foreground_mobjects(*pts)
            self.play(*[Indicate(pts[x - 1], color=GOOD) for x in (1, 2, 3, 5)], FadeIn(c4), run_time=0.8)
            self.play(LaggedStart(*[Create(o) for o in others], lag_ratio=0.4), FadeIn(c3), run_time=1.6)
            wait_until(self, tr, "qr")
            self.play(FadeOut(others), FadeOut(c3), FadeOut(c4), FadeIn(qr), run_time=0.6)
            self.play(FadeIn(smudge), run_time=0.4)
            self.play(Create(ok), run_time=0.5)
            rest(self, tr)

        seven = managers(7, s=1.4, buff=0.6).move_to([0, 2.7, 0])
        ask = text("how many can lie?", size=56, color=PRIMARY).move_to([0, -2.6, 0])
        pg3 = plane(ylabels=False, x_length=7.0, y_length=3.4).move_to([0, -0.1, 0])
        pc3 = curve(pg3.ax, para_f, MUTED, 3)
        with self.voiceover(text=N("s07.b4")) as tr:
            self.remove_foreground_mobjects(*pts)
            self.play(FadeOut(Group(*self.mobjects)), run_time=0.5)
            self.play(FadeIn(seven), FadeIn(pg3), Create(pc3), run_time=0.9)
            self.play(FadeIn(ask), run_time=0.5)
            rest(self, tr)
        self.wait(1.2)
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.8)


# ---------------------------------------------------------------------------
# Thumbnail
# ---------------------------------------------------------------------------


class Thumbnail(Scene):
    def construct(self):
        pg = plane(ylabels=False, x_length=9.6, y_length=4.6).move_to([1.6, -1.45, 0])
        ax = pg.ax
        pc = curve(ax, para_f, FG, 7)
        pts = VGroup(*[pdot(ax, x, para_f(x), C5[x - 1], r=0.22) for x in range(1, 6)])
        sd = pdot(ax, 0, para_f(0), SECRET, r=0.24)
        q = text("?", size=90, color=SECRET, weight="BOLD").next_to(sd, LEFT, 0.25)
        pg.set_opacity(0.6)
        t1 = text("Any 3 open it.", size=88, weight="BOLD")
        t2 = text("Any 2 learn nothing.", size=88, weight="BOLD", color=PRIMARY)
        tt = VGroup(t1, t2).arrange(DOWN, buff=0.25, aligned_edge=LEFT).to_corner(UL, buff=0.45)
        self.add(pg, pc, pts, sd, q, tt)
