from fractions import Fraction as Fr
from math import sqrt

import numpy as np
from manim import *
from manim_voiceover import VoiceoverScene

from mathvid import layout  # noqa: F401  must come before scene code runs
from mathvid.anim import rest, rt, strike, wait_until
from mathvid.layout import FH, FW
from mathvid.numberline import ZoomLine
from mathvid.orders import (
    LEFT_C,
    RIGHT_C,
    RatLine,
    cross,
    cut_mark,
    hollow_at,
    left_bar,
    rats,
    scissors,
    solid_line,
    tick,
    tips,
)
from mathvid.script import Script
from mathvid.style import BAD, BG, FG, GOOD, MUTED, PRIMARY, SECONDARY, TERTIARY, math, text
from mathvid.voice import get_speech_service

N = Script(__file__)

TITLE = ("The real numbers", "are just an order")
R2 = sqrt(2)
FACTS4 = ["no holes", "dense", "no ends", "a countable set of dots spread through it"]
FACTS4_SHORT = ["no holes", "dense", "no ends", "countable set\nspread through"]
SUSLIN_FACT = "no uncountable family of separate intervals"


def until(tr, mark, minus=0.0):
    return rt(tr.time_until_bookmark(mark) - minus)


def tag(s, size=30, color=MUTED, **kw):
    return text(s, size=size, color=color, **kw)


# ---------------------------------------------------------------------------
# Shared builders (also used by shorts.py)
# ---------------------------------------------------------------------------


def title_two_lines(size=58):
    a = text(TITLE[0], size=size, weight="BOLD")
    b = text(TITLE[1], size=size, weight="BOLD", color=PRIMARY)
    return VGroup(a, b).arrange(DOWN, buff=0.25)


def ruler(w=1.7, h=0.42):
    body = Rectangle(width=w, height=h, color=FG, stroke_width=3)
    marks = VGroup(*[Line(body.get_corner(UL) + RIGHT * (w * i / 8), body.get_corner(UL) + RIGHT * (w * i / 8)
                          + DOWN * (h * (0.5 if i % 2 == 0 else 0.3)), color=FG, stroke_width=2)
                     for i in range(1, 8)])
    return VGroup(body, marks)


def op_tags(size=96):
    """The three things the hook throws away: +, x, and distance (a ruler)."""
    plus = math("+", size=size)
    times = math(r"\times", size=size)
    dist = VGroup(ruler(), tag("distance", size=28, color=FG)).arrange(DOWN, buff=0.15)
    return VGroup(plus, times, dist)


def hook_line(y=-1.0, half=6.3, unit=2.0, x_zero=-3.6, size=46):
    """The real line with a few labelled numbers: (line, labels, marks)."""
    L = solid_line(-half, half, y)
    vals = [(0, "0"), (0.5, r"\frac12"), (1, "1"), (R2, r"\sqrt{2}"), (PI, r"\pi")]
    p = lambda v: np.array([x_zero + v * unit, y, 0])  # noqa: E731
    marks = VGroup(*[Line(p(v) + DOWN * 0.14, p(v) + UP * 0.14, color=FG, stroke_width=4) for v, _ in vals])
    labs = VGroup(*[math(s, size=size, color=FG).next_to(p(v), DOWN, buff=0.28) for v, s in vals])
    return L, labs, marks


def bar_for(v, y, x_of, height=0.22, color=LEFT_C):
    return left_bar(x_of(v), y, x_start=-6.6, color=color, height=height)


def checklist(items, size=30, buff=0.22):
    rows = VGroup(*[tag(s, size=size, color=FG) for s in items]).arrange(DOWN, aligned_edge=LEFT, buff=buff)
    return rows


class LongRay(VGroup):
    """The long ray drawn as a "matchstick" picture between x0 and x1 at height y.

    Position omega*k + n sits at x(k, n). Blocks k = 0, 1, 2, ... shrink by half, so
    omega squared lands at a finite spot; a fainter copy of the whole pattern runs past it
    to say "and it keeps going".
    """

    def __init__(self, x0, x1, y=0.0, blocks=7, per=10, main=0.8, tail=True, width=4, colors=(FG, TERTIARY)):
        super().__init__()
        self.x0, self.x1, self.y = x0, x1, y
        W = x1 - x0
        self.M = main * W
        self.blocks, self.per = blocks, per
        self.xw2 = x0 + self.M
        self.ticks, self.copies, self.starts = VGroup(), VGroup(), VGroup()
        self.tall = {}
        for k in range(blocks):
            for n in range(per):
                a, b = self.x(k, n), self.x(k, n + 1)
                h = 0.8 if n == 0 else 0.4 * 0.8 ** n
                h *= 0.75 ** k if n else 0.85 ** k
                t = Line([a, y - h / 2, 0], [a, y + h / 2, 0], color=FG, stroke_width=3 if n == 0 else 2)
                self.ticks.add(t)
                if n == 0:
                    self.tall[k] = t
                seg = Line([a, y, 0], [b, y, 0], color=colors[(k + n) % 2], stroke_width=width)
                self.copies.add(seg)
                self.starts.add(Dot([a, y, 0], radius=min(0.05, 0.25 * (b - a)), color=colors[(k + n) % 2]))
        self.w2 = Line([self.xw2, y - 0.5, 0], [self.xw2, y + 0.5, 0], color=FG, stroke_width=3)
        self.tail = VGroup()
        if tail:
            tw = x1 - self.xw2
            for k in range(5):
                for n in range(6):
                    a = self.xw2 + tw * self._u(k, n)
                    b = self.xw2 + tw * self._u(k, n + 1)
                    self.tail.add(Line([a, y, 0], [b, y, 0], color=colors[(k + n) % 2], stroke_width=width,
                                       stroke_opacity=0.55))
            self.tail.add(Line([self.xw2 + tw * self._u(5, 0), y, 0], [x1, y, 0], color=colors[0],
                               stroke_width=width, stroke_opacity=0.35))
            self.arrow = Triangle(color=FG, fill_opacity=0.6, stroke_width=0).scale(0.13).rotate(-PI / 2)
            self.arrow.move_to([x1 + 0.12, y, 0])
            self.tail.add(self.arrow)
        self.add(self.copies, self.starts, self.ticks, self.w2, self.tail)

    def _u(self, k, n):
        """Fraction of the omega^2 span used up before position omega*k + n."""
        blk = 1 - 0.5 ** k
        return blk + 0.5 ** (k + 1) * (1 - 0.5 ** n)

    def x(self, k, n=0):
        if k >= self.blocks:
            return self.xw2
        return self.x0 + self.M * self._u(k, n)

    def p(self, k, n=0):
        return np.array([self.x(k, n), self.y, 0])

    def copy_seg(self, k, n):
        return self.copies[k * self.per + n]

    def labels(self, size=40, finite=3):
        g = VGroup()
        for n in range(finite):
            g.add(math(str(n), size=size, color=FG).next_to(self.p(0, n), DOWN, buff=0.3))
        g.add(math(r"\cdots", size=size, color=MUTED).next_to(self.p(0, finite), DOWN, buff=0.3))
        g.add(math(r"\omega", size=size + 4, color=PRIMARY).next_to(self.p(1), DOWN, buff=0.3))
        g.add(math(r"\omega{+}1", size=size - 6, color=FG).next_to(self.p(1, 1), UP, buff=0.35))
        g.add(math(r"\omega{\cdot}2", size=size - 2, color=PRIMARY).next_to(self.p(2), DOWN, buff=0.3))
        g.add(math(r"\omega{\cdot}3", size=size - 8, color=PRIMARY).next_to(self.p(3), UP, buff=0.45))
        g.add(math(r"\omega^2", size=size + 4, color=PRIMARY).next_to([self.xw2, self.y, 0], DOWN, buff=0.5))
        return g


def long_line_both(x_mid, half, y, **kw):
    """The long line: a long ray to the right and its mirror image to the left, sharing x_mid."""
    r = LongRay(x_mid, x_mid + half, y, **kw)
    l = LongRay(x_mid, x_mid + half, y, **kw)
    l.flip(UP, about_point=np.array([x_mid, y, 0]))
    return VGroup(l, r)


def lens(center, r=1.2):
    """A magnifier view: what any stretch of the long line looks like up close."""
    c = Circle(radius=r, color=FG, stroke_width=3, fill_color=BG, fill_opacity=1).move_to(center)
    ln = Line(center + LEFT * r * 0.85, center + RIGHT * r * 0.85, color=FG, stroke_width=5)
    tk = VGroup(*[Line(center + RIGHT * x + DOWN * 0.08, center + RIGHT * x + UP * 0.08, color=FG, stroke_width=2)
                  for x in np.linspace(-0.6, 0.6, 5) * r])
    return VGroup(c, ln, tk)


def fact_tags_grid(names, size=30, color=PRIMARY, y=3.0, dx=3.5, dy=0.7):
    tags = VGroup(*[text(s, size=size, color=color) for s in names])
    for i, t in enumerate(tags):
        t.move_to([(-dx if i % 2 == 0 else dx), y - (i // 2) * dy, 0])
    return tags


class FactTable(VGroup):
    """Rows of examples against the four facts, with ticks and crosses."""

    COLS = [-0.7, 1.35, 3.4, 5.55]
    ROWS = {"rationals": ("the rationals", [0, 1, 1, 1]),
            "segment": ("0 to 1, ends included", [1, 1, 0, 1]),
            "integers": ("the integers", [1, 0, 1, 0]),
            "long": ("the long line", [1, 1, 1, 0])}

    def __init__(self, keys, top=3.05, dy=1.32, size=32):
        super().__init__()
        self.head = VGroup(*[text(s, size=size - 2, color=PRIMARY) for s in FACTS4_SHORT])
        for h, x in zip(self.head, self.COLS):
            h.move_to([x, top, 0])
        self.rule = Line([-6.6, top - 0.55, 0], [6.9, top - 0.55, 0], color=MUTED, stroke_width=2)
        self.add(self.head, self.rule)
        self.rows, self.marks, self.pics = {}, {}, {}
        for i, k in enumerate(keys):
            y = top - 1.25 - i * dy
            name, ok = self.ROWS[k]
            lab = text(name, size=size, color=FG).move_to([-6.5, y + 0.22, 0], aligned_edge=LEFT)
            pic = self.picture(k, np.array([-4.95, y - 0.3, 0]))
            marks = VGroup(*[(tick(at=np.array([x, y, 0])) if o else cross(np.array([x, y, 0])))
                             for x, o in zip(self.COLS, ok)])
            self.rows[k], self.marks[k], self.pics[k] = lab, marks, pic
            self.add(lab, pic, marks)

    @staticmethod
    def picture(k, c, w=2.6):
        y = c[1]
        if k == "rationals":
            L = RatLine(0, 2, w / 2, y=y, x0=c[0], qmax=6, r=0.05)
            return VGroup(L, hollow_at(L.p(R2), r=0.07, color=BAD))
        if k == "segment":
            ln = Line(c + LEFT * w / 2, c + RIGHT * w / 2, color=FG, stroke_width=4)
            ends = VGroup(Dot(c + LEFT * w / 2, radius=0.08, color=BAD), Dot(c + RIGHT * w / 2, radius=0.08, color=BAD))
            return VGroup(ln, ends)
        if k == "integers":
            return VGroup(*[Dot(c + RIGHT * x, radius=0.07, color=FG) for x in np.linspace(-w / 2, w / 2, 5)])
        if k == "long":
            g = LongRay(c[0] - w / 2, c[0] + w / 2, y, blocks=5, per=6, width=3)
            for t in g.ticks:
                t.set_stroke(width=1.5)
            return g


def real_line_pair_eq(top_mob, y=-2.3, half=5.5):
    eq = math("=", size=60, color=PRIMARY)
    R = solid_line(-half, half, y)
    lab = tag("the real line", size=28, color=FG).next_to(R, DOWN, buff=0.25)
    return eq, R, lab


# ---------------------------------------------------------------------------
# s01 Hook
# ---------------------------------------------------------------------------


class S01Hook(VoiceoverScene):
    def construct(self):
        self.set_speech_service(get_speech_service())
        L, labs, marks = hook_line()
        ops = op_tags()
        for o, x in zip(ops, (-4.2, 0.0, 4.2)):
            o.move_to([x, 1.7, 0])
        less = math("<", size=150, color=PRIMARY).move_to(UP * 1.7)
        with self.voiceover(text=N("s01.b1")) as tr:
            self.play(Create(L), FadeIn(marks), FadeIn(labs), run_time=0.9)
            self.play(LaggedStart(*[FadeIn(o, shift=DOWN * 0.2) for o in ops], lag_ratio=0.3),
                      run_time=rt(min(1.2, tr.time_until_bookmark("add") - 0.1)))
            for mark, o in zip(("add", "mul", "dist"), ops):
                wait_until(self, tr, mark)
                s = cross(o.get_center(), s=max(o.width, o.height) * 0.6, width=8)
                self.play(Create(s), run_time=0.35)
                self.play(FadeOut(o), FadeOut(s), run_time=0.45)
            wait_until(self, tr, "less")
            self.play(FadeOut(labs), FadeOut(marks), FadeIn(less, scale=0.6), run_time=0.8)
            rest(self, tr)

        ttl = title_two_lines().move_to(UP * 0.2)
        with self.voiceover(text=N("s01.b2")) as tr:
            wait_until(self, tr, "one")
            self.play(L.animate.set_color(PRIMARY), run_time=0.4)
            self.play(L.animate.set_color(FG), run_time=0.5)
            wait_until(self, tr, "title")
            self.play(FadeOut(less), L.animate.shift(DOWN * 1.6), FadeIn(ttl, shift=UP * 0.2), run_time=0.8)
            rest(self, tr)
        self.wait(1.4)
        self.play(FadeOut(ttl), FadeOut(L), run_time=0.6)


# ---------------------------------------------------------------------------
# s02 Where we left off
# ---------------------------------------------------------------------------


def episode_card(title_parts, w=6.3, h=1.3):
    t = VGroup(*title_parts).arrange(RIGHT, buff=0.12) if not isinstance(title_parts, VGroup) else title_parts
    t.scale_to_fit_width(min(t.width, w - 0.4))
    box = RoundedRectangle(corner_radius=0.15, width=w, height=h, color=MUTED, stroke_width=2)
    t.move_to(box)
    return VGroup(box, t)


class S02Recap(VoiceoverScene):
    def construct(self):
        self.set_speech_service(get_speech_service())
        cardA = episode_card([text("So... what actually is", size=38), math(r"\sqrt{2}\,?", size=48)])
        cardA.move_to([-3.45, 2.9, 0])
        rows = [["1", "1.4", "1.41", "1.414", r"\dots"], ["2", "1.5", "1.42", "1.415", r"\dots"]]
        grid = VGroup()
        for i, r in enumerate(rows):
            for j, s in enumerate(r):
                grid.add(math(s, size=42).move_to([-6.0 + j * 1.3, 1.4 - i * 0.85, 0]))
        gaps = VGroup(*[math(s, size=38, color=PRIMARY).move_to([-6.0 + j * 1.3, -0.4, 0])
                        for j, s in enumerate(["1", "0.1", "0.01", "0.001", r"\dots"])])
        gap_lab = tag("gap", size=34, color=PRIMARY).next_to(gaps, LEFT, buff=0.3)
        gapf = math("|x", "-", "y|", size=56).move_to([-3.45, -1.8, 0])
        with self.voiceover(text=N("s02.b1")) as tr:
            self.play(FadeIn(cardA), run_time=0.6)
            wait_until(self, tr, "lists")
            self.play(FadeIn(grid, lag_ratio=0.08), run_time=1.2)
            self.play(FadeIn(gaps, lag_ratio=0.15), FadeIn(gap_lab), run_time=rt(min(1.2, tr.time_until_bookmark("minus"))))
            wait_until(self, tr, "minus")
            self.play(FadeIn(gapf), run_time=0.4)
            self.play(gapf[1].animate.set_color(PRIMARY).scale(1.3), run_time=0.5)
            rest(self, tr)

        cardB = episode_card(VGroup(text("What makes the rational", size=36), text("numbers so special?", size=36)).arrange(DOWN, buff=0.08))
        cardB.move_to([3.45, 2.9, 0])
        Q = RatLine(-1, 2, 1.95, y=1.2, x0=3.45, qmax=8, r=0.07)
        ftags = VGroup(tag("dense", 38, PRIMARY), tag("no ends", 38, PRIMARY), tag("can be listed", 38, PRIMARY))
        ftags.arrange(DOWN, aligned_edge=LEFT, buff=0.28).move_to([4.0, -0.6, 0])
        fticks = VGroup(*[tick(t) for t in ftags])
        with self.voiceover(text=N("s02.b2")) as tr:
            self.play(FadeIn(cardB), run_time=0.6)
            wait_until(self, tr, "order")
            self.play(FadeIn(Q.axis), FadeIn(Q.dots, lag_ratio=0.01), run_time=1.0)
            for mark, i in (("dense", 0), ("ends", 1), ("list", 2)):
                wait_until(self, tr, mark)
                self.play(FadeIn(ftags[i], shift=RIGHT * 0.2), Create(fticks[i]), run_time=0.5)
            rest(self, tr)

        left_stuff = VGroup(cardA, grid, gaps, gap_lab, gapf)
        top_tags = VGroup(ftags, fticks)
        claim = VGroup(text("any line with these three facts", size=36), math("=", size=46),
                       text("the rationals", size=36, color=PRIMARY)).arrange(RIGHT, buff=0.25)
        R = solid_line(-5.8, 5.8, -1.7)
        rlab = tag("the real numbers", 36, FG).next_to(R, DOWN, buff=0.3)
        rt3 = VGroup(tag("dense", 36, FG), tag("no ends", 36, FG), tag("can be listed", 36, FG))
        rt3.arrange(RIGHT, buff=1.1).move_to([0.4, -0.8, 0])
        rmarks = VGroup(tick(rt3[0]), tick(rt3[1]), cross(rt3[2].get_left() + LEFT * 0.4))
        with self.voiceover(text=N("s02.b3")) as tr:
            self.play(FadeOut(left_stuff), FadeOut(cardB), FadeOut(top_tags), run_time=0.6)
            self.play(Q.animate.move_to([0, 2.6, 0]), run_time=0.7)
            claim.next_to(Q, DOWN, buff=0.45)
            wait_until(self, tr, "same")
            self.play(FadeIn(claim), run_time=0.7)
            wait_until(self, tr, "real")
            self.play(Create(R), FadeIn(rlab), run_time=0.7)
            self.play(FadeIn(rt3), Create(rmarks[0]), Create(rmarks[1]), run_time=0.6)
            self.play(Create(rmarks[2]), rt3[2].animate.set_color(BAD), run_time=0.5)
            rest(self, tr)

        q = text("?", size=110, color=PRIMARY).move_to(UP * 1.2)
        R2l = solid_line(-5.8, 5.8, -0.6)
        da, db = Dot([-1.6, 2.0, 0], radius=0.16, color=LEFT_C), Dot([1.6, 2.0, 0], radius=0.16, color=RIGHT_C)
        lt = math("<", size=80).move_to([0, 2.0, 0])
        defn = tag("a line: for any two things, one is left of the other", 38, FG).move_to(DOWN * 2.2)
        with self.voiceover(text=N("s02.b4")) as tr:
            self.play(FadeOut(VGroup(Q, claim, rt3, rmarks, rlab)), ReplacementTransform(R, R2l), run_time=0.7)
            self.play(FadeIn(q, scale=0.7), run_time=0.5)
            self.wait(rt(min(1.2, tr.duration * 0.15)))
            self.play(FadeOut(q), FadeIn(da), FadeIn(db), FadeIn(lt), FadeIn(defn), run_time=0.8)
            rest(self, tr)
        self.play(FadeOut(VGroup(da, db, lt, defn, R2l)), run_time=0.6)


# ---------------------------------------------------------------------------
# s03 Holes
# ---------------------------------------------------------------------------


class S03Holes(VoiceoverScene):
    def construct(self):
        self.set_speech_service(get_speech_service())
        lo, hi, unit, y = -0.6, 2.4, 4.3, -0.4
        L = RatLine(lo, hi, unit, y=y, qmax=12, r=0.085)
        nums = L.numbers([0, Fr(1, 2), 1, Fr(3, 2), 2], size=42)
        sc = scissors().move_to(L.p(-0.4) + UP * 1.0)
        half = Fr(1, 2)
        with self.voiceover(text=N("s03.b1")) as tr:
            self.play(Create(L.axis), FadeIn(L.dots, lag_ratio=0.005), FadeIn(nums), run_time=1.0)
            self.play(FadeIn(sc), run_time=0.3)
            self.play(sc.animate.move_to([L.x(half) - 0.02, y + 1.0, 0]), run_time=rt(min(1.4, until(tr, "cut", 0.1))))
            wait_until(self, tr, "cut")
            lft, rgt = L.left_of(half), L.right_of(half)
            self.play(lft.animate.set_color(LEFT_C).shift(LEFT * 0.18), rgt.animate.set_color(RIGHT_C).shift(RIGHT * 0.18),
                      sc.animate.shift(DOWN * 0.35), run_time=0.6)
            wait_until(self, tr, "edge")
            ring = Circle(radius=0.2, color=RIGHT_C, stroke_width=4).move_to(L.by[half])
            self.play(L.by[half].animate.scale(1.8), Create(ring), run_time=0.6)
            rest(self, tr)

        lab_l = math(r"q<0 \text{ or } q^2<2", size=44, color=LEFT_C).move_to([L.x(0.3), y + 1.6, 0])
        lab_r = math(r"q>0 \text{ and } q^2>2", size=44, color=RIGHT_C).move_to([L.x(1.95), y + 1.6, 0])
        with self.voiceover(text=N("s03.b2")) as tr:
            L.by[half].scale(1 / 1.8)
            self.play(FadeOut(ring), lft.animate.shift(RIGHT * 0.18).set_color(FG),
                      rgt.animate.shift(LEFT * 0.18).set_color(FG), sc.animate.shift(UP * 0.35), run_time=0.6)
            self.play(sc.animate.move_to([L.x(R2), y + 1.0 - 0.35, 0]), run_time=0.9)
            wait_until(self, tr, "rule")
            l2, r2 = L.left_of(R2), L.right_of(R2)
            self.play(l2.animate.set_color(LEFT_C).shift(LEFT * 0.12), r2.animate.set_color(RIGHT_C).shift(RIGHT * 0.12),
                      FadeIn(lab_l), run_time=0.8)
            self.play(FadeIn(lab_r), run_time=0.6)
            rest(self, tr)

        # Zoom: hand the picture over to a ZoomLine with the same geometry.
        Z = ZoomLine(lo, hi, length=(hi - lo) * unit, center=np.array([L.x((lo + hi) / 2), y, 0]), label_size=26)
        Z.line.set_opacity(0)
        zdots = []
        for v in rats(0.9, 1.95, 14):
            col = LEFT_C if v < R2 else RIGHT_C
            d = Z.dot(float(v), color=col, radius=0.06, hole=R2)
            d.show.set_value(1)
            zdots.append(d)
        axis = Line(Z.p(lo) * 0 + np.array([-6.5, y, 0]), np.array([6.5, y, 0]), color=MUTED, stroke_width=3)
        blues = [1.4, 1.41, 1.414, 1.4142]
        golds = [1.5, 1.42, 1.415, 1.4143]
        bd = [Z.dot(v, color=LEFT_C, radius=0.11) for v in blues]
        gd = [Z.dot(v, color=RIGHT_C, radius=0.11) for v in golds]
        with self.voiceover(text=N("s03.b3")) as tr:
            Z.hole_r.set_value(0)
            self.add(axis, Z, *zdots, *bd, *gd)
            self.remove(L.axis)
            self.play(FadeOut(L.dots), FadeOut(nums), FadeOut(sc), lab_l.animate.move_to([-3.6, 2.6, 0]),
                      lab_r.animate.move_to([3.6, 2.6, 0]), run_time=0.6)
            self.play(*Z.zoom_to(1.3, 1.55), run_time=1.0)
            wait_until(self, tr, "left")
            T = tr.time_until_bookmark("right")
            step = max(0.5, (T - 0.6) / 4)
            ranges = [(1.3, 1.55), (1.39, 1.44), (1.405, 1.425), (1.4125, 1.4155)]
            for i, v in enumerate(blues):
                sq = math(f"{v}^2 = {v * v:.8f}".rstrip("0") + "<2", size=42, color=LEFT_C).move_to([-3.6, 1.6, 0])
                self.play(*Z.zoom_to(*ranges[i]), bd[i].show.animate.set_value(1), FadeIn(sq), run_time=step * 0.7)
                self.wait(step * 0.3)
                self.remove(sq)
            wait_until(self, tr, "right")
            T = tr.get_remaining_duration()
            step = max(0.5, (T - 0.3) / 4)
            for i, v in enumerate(golds):
                sq = math(f"{v}^2 = {v * v:.8f}".rstrip("0") + ">2", size=42, color=RIGHT_C).move_to([3.6, 1.6, 0])
                self.play(*Z.zoom_to(*ranges[i]), gd[i].show.animate.set_value(1),
                          FadeIn(sq), run_time=step * 0.7)
                self.wait(step * 0.3)
                self.remove(sq)
            rest(self, tr)

        ring = Z.ring(R2, radius=0.14, color=FG)
        hole_lab = tag("hole", 40, FG).move_to([0, y + 1.0, 0])
        with self.voiceover(text=N("s03.b4")) as tr:
            self.play(*Z.zoom_to(1.0, 1.85), Z.hole_r.animate.set_value(0.16), *[d.show.animate.set_value(0) for d in bd + gd], run_time=1.4)
            hole_lab.move_to(Z.p(R2) + UP * 0.85)
            wait_until(self, tr, "hole")
            self.play(Create(ring), FadeIn(hole_lab), run_time=0.7)
            rest(self, tr)

        less = math("<", size=110, color=PRIMARY).move_to(UP * 2.3)
        with self.voiceover(text=N("s03.b5")) as tr:
            self.play(FadeOut(lab_l), FadeOut(lab_r), run_time=0.6)
            wait_until(self, tr, "pure")
            self.play(FadeIn(less, scale=0.6), Indicate(ring, color=PRIMARY), run_time=0.9)
            rest(self, tr)
        self.wait(0.4)
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.6)


# ---------------------------------------------------------------------------
# s04 Let the cut be the number
# ---------------------------------------------------------------------------


class S04Cut(VoiceoverScene):
    def construct(self):
        self.set_speech_service(get_speech_service())
        y = -2.4
        L = RatLine(-1.2, 3.0, 3.2, y=y, qmax=10, r=0.08)
        l2, r2 = L.left_of(R2), L.right_of(R2)
        l2.set_color(LEFT_C)
        r2.set_color(RIGHT_C)
        piece = VGroup(Line(L.p(-1.2), L.p(R2), color=LEFT_C, stroke_width=3), l2.copy())
        lab = math(r"\sqrt{2}", ":=", size=56, color=LEFT_C)
        ded = tag("Dedekind, 1872", 32, MUTED).move_to([4.8, 3.2, 0])
        with self.voiceover(text=N("s04.b1")) as tr:
            self.play(FadeIn(L), run_time=0.8)
            wait_until(self, tr, "def")
            self.add(piece)
            self.play(piece.animate.shift(UP * 1.3), l2.animate.set_opacity(0.25), run_time=0.9)
            lab.next_to(piece, UP, buff=0.4).align_to(piece, LEFT).shift(RIGHT * 0.3)
            self.play(FadeIn(lab), FadeIn(ded), run_time=0.5)
            rest(self, tr)

        rules = checklist(["not empty", "not everything", "closed downward", "no largest dot"], size=40)
        rules.move_to([-2.2, 2.4, 0])
        rules.arrange_in_grid(rows=2, cols=2, buff=(1.2, 0.35), col_alignments="ll").move_to([0, 2.5, 0])
        rticks = VGroup(*[tick(r) for r in rules])
        mid = [v for v in L.by if 0.4 < v < 0.8][0]
        x_mid = L.x(mid)
        sweep = Arrow([x_mid, y + 1.75, 0], [-6.4, y + 1.75, 0], color=LEFT_C, stroke_width=4, buff=0,
                      max_tip_length_to_length_ratio=0.04)
        spot = Dot([x_mid, y + 1.3, 0], radius=0.13, color=PRIMARY)
        end_ring = hollow_at([L.x(R2), y + 1.3, 0], r=0.13, color=LEFT_C)
        with self.voiceover(text=N("s04.b2")) as tr:
            self.play(FadeOut(lab), FadeOut(ded), run_time=0.3)
            self.play(FadeIn(rules[0]), Create(rticks[0]), run_time=0.5)
            self.play(FadeIn(rules[1]), Create(rticks[1]), run_time=0.5)
            wait_until(self, tr, "down")
            self.play(FadeIn(rules[2]), Create(rticks[2]), FadeIn(spot), run_time=0.5)
            self.play(GrowArrow(sweep), run_time=0.9)
            wait_until(self, tr, "nomax")
            self.play(FadeIn(rules[3]), Create(rticks[3]), Create(end_ring), run_time=0.6)
            rest(self, tr)

        # The cut at 1/2, two ways.
        half = Fr(1, 2)
        A = RatLine(-0.5, 1.5, 5.0, y=1.4, x0=-0.9, qmax=9, r=0.09)
        B = RatLine(-0.5, 1.5, 5.0, y=-1.2, x0=-0.9, qmax=9, r=0.09)
        A.left_of(half, strict=False).set_color(LEFT_C)
        A.right_of(half, strict=True).set_color(RIGHT_C)
        B.left_of(half).set_color(LEFT_C)
        B.right_of(half).set_color(RIGHT_C)
        for M in (A, B):
            M.by[half].scale(1.7)
        na, nb = A.numbers([half], size=44), B.numbers([half], size=44)
        badA = cross(np.array([5.4, 1.4, 0]), s=0.3, width=8)
        goodB = math(r"\tfrac12", ":=", r"\text{everything below }\tfrac12", size=48, color=FG).move_to([0, -3.0, 0])
        with self.voiceover(text=N("s04.b3")) as tr:
            self.play(FadeOut(VGroup(L, piece, rules, rticks, sweep, spot, end_ring)), run_time=0.6)
            self.play(FadeIn(B), FadeIn(nb), run_time=0.7)
            wait_until(self, tr, "two")
            self.play(FadeIn(A), FadeIn(na), run_time=0.8)
            self.play(Create(badA), A.animate.set_opacity(0.35), run_time=0.6)
            wait_until(self, tr, "half")
            self.play(FadeIn(goodB), run_time=0.6)
            rest(self, tr)

        xs = lambda v: -4.6 + (float(v) - 0.0) * 3.4  # noqa: E731
        vals = [(Fr(1, 2), r"\frac12"), (Fr(1), "1"), (R2, r"\sqrt2"), (Fr(3, 2), r"\frac32")]
        bars = VGroup()
        blabs = VGroup()
        for i, (v, s) in enumerate(vals):
            yy = 2.2 - i * 0.95
            b = left_bar(xs(v), yy, x_start=-6.6, height=0.26)
            bars.add(b)
            blabs.add(math(s, size=46, color=LEFT_C).next_to(b, RIGHT, buff=0.25))
        guides = VGroup(*[DashedLine([b.x_end, 2.5, 0], [b.x_end, -2.6, 0], color=MUTED, stroke_width=2,
                                     dash_length=0.08) for b in bars])
        with self.voiceover(text=N("s04.b4")) as tr:
            self.play(FadeOut(VGroup(A, B, na, nb, badA, goodB)), run_time=0.5)
            self.play(LaggedStart(*[GrowFromEdge(b, LEFT) for b in bars], lag_ratio=0.25), FadeIn(blabs, lag_ratio=0.25),
                      run_time=1.4)
            wait_until(self, tr, "inside")
            self.play(Create(guides[0]), bars[0].animate.set_color(PRIMARY), run_time=0.6)
            self.play(bars[0].animate.set_color(LEFT_C), bars[1].animate.set_color(PRIMARY), Create(guides[1]), run_time=0.6)
            self.play(bars[1].animate.set_color(LEFT_C), run_time=0.4)
            rest(self, tr)

        line_y = -2.6
        R = solid_line(-6.4, 6.4, line_y)
        pts = VGroup(*[Dot([b.x_end, line_y, 0], radius=0.11, color=LEFT_C) for b in bars])
        rl = tag("the real line", 34, FG).move_to([-4.0, -3.3, 0])
        Qd = RatLine(-0.55, 3.15, 3.4, y=line_y, x0=-4.6 + 1.3 * 3.4, qmax=9, r=0.06, axis=False)
        with self.voiceover(text=N("s04.b5")) as tr:
            self.play(FadeOut(guides), FadeIn(Qd.dots, lag_ratio=0.01), run_time=0.7)
            self.play(*[ReplacementTransform(b, p) for b, p in zip(bars, pts)],
                      *[l.animate.next_to(p, UP if i < 3 else DOWN, buff=0.25) for i, (l, p) in enumerate(zip(blabs, pts))],
                      run_time=1.2)
            wait_until(self, tr, "line")
            self.play(Create(R), Qd.dots.animate.set_opacity(0.0), FadeIn(rl), run_time=1.0)
            rest(self, tr)
        self.play(FadeOut(VGroup(pts, blabs, rl, Qd.dots)), run_time=0.6)
        self.wait(0.2)


# ---------------------------------------------------------------------------
# s05 No holes left
# ---------------------------------------------------------------------------


class S05NoHoles(VoiceoverScene):
    def construct(self):
        self.set_speech_service(get_speech_service())
        y = -2.6
        xc = 1.1
        R = solid_line(-6.4, 6.4, y)
        sc = scissors().move_to([xc, y + 0.75, 0])
        q = tag("does this cut land on a point?", 40, FG).move_to(UP * 3.1)
        Lp = Line([-6.4, y, 0], [xc - 0.08, y, 0], color=LEFT_C, stroke_width=7)
        Rp = Line([xc + 0.08, y, 0], [6.4, y, 0], color=RIGHT_C, stroke_width=7)
        with self.voiceover(text=N("s05.b1")) as tr:
            self.add(R)
            self.play(FadeIn(q), run_time=0.6)
            wait_until(self, tr, "cut")
            self.play(FadeIn(sc, shift=DOWN * 0.3), run_time=0.5)
            self.play(FadeIn(Lp), FadeIn(Rp), run_time=0.6)
            rest(self, tr)

        ends = [-4.8, -3.0, -1.6, -0.5, 0.3, 0.75, 0.97]
        bars = VGroup(*[left_bar(x, 2.3 - i * 0.55, x_start=-6.6, height=0.2) for i, x in enumerate(ends)])
        feet = VGroup(*[Dot([x, y, 0], radius=0.09, color=LEFT_C) for x in ends])
        union = left_bar(xc, -1.3, x_start=-6.6, height=0.32, color=PRIMARY)
        with self.voiceover(text=N("s05.b2")) as tr:
            self.play(FadeIn(feet), FadeOut(q), run_time=0.4)
            wait_until(self, tr, "stack")
            self.play(LaggedStart(*[TransformFromCopy(f, b) for f, b in zip(feet, bars)], lag_ratio=0.15), run_time=1.6)
            wait_until(self, tr, "union")
            self.play(*[b.animate.move_to([b.get_center()[0], -1.3, 0]).set_opacity(0.5) for b in bars], run_time=0.8)
            self.play(FadeIn(union), FadeOut(bars), run_time=0.7)
            rest(self, tr)

        rules = checklist(["not empty", "not everything", "closed downward", "no largest dot"], size=40)
        rules.arrange_in_grid(rows=2, cols=2, buff=(1.2, 0.3), col_alignments="ll").move_to([0.4, 1.9, 0])
        rticks = VGroup(*[tick(r) for r in rules])
        with self.voiceover(text=N("s05.b3")) as tr:
            wait_until(self, tr, "rules")
            self.play(FadeIn(rules), run_time=0.4)
            self.play(LaggedStart(*[Create(t) for t in rticks], lag_ratio=0.3), run_time=1.2)
            rest(self, tr)

        P = Dot([xc, y, 0], radius=0.16, color=PRIMARY)
        glow = Circle(radius=0.3, color=PRIMARY, stroke_width=4).move_to(P)
        note_l = tag("at least as big as every blue point", 34, LEFT_C).move_to([-3.4, -0.4, 0])
        note_r = tag("inside every gold point", 34, RIGHT_C).move_to([3.9, -0.4, 0])
        arr_l = Arrow(note_l.get_bottom(), [-2.0, y + 0.15, 0], color=LEFT_C, stroke_width=3, buff=0.15)
        arr_r = Arrow(note_r.get_bottom(), [3.6, y + 0.15, 0], color=RIGHT_C, stroke_width=3, buff=0.15)
        with self.voiceover(text=N("s05.b4")) as tr:
            self.play(FadeOut(rules), FadeOut(rticks), ReplacementTransform(union, P), FadeOut(sc), run_time=0.8)
            wait_until(self, tr, "edge")
            self.play(Create(glow), FadeIn(note_l), GrowArrow(arr_l), run_time=0.7)
            self.play(FadeIn(note_r), GrowArrow(arr_r), run_time=0.7)
            wait_until(self, tr, "none")
            self.play(FadeOut(VGroup(note_l, note_r, arr_l, arr_r, Lp, Rp, feet)), P.animate.set_color(GOOD),
                      glow.animate.set_color(GOOD), run_time=0.7)
            rest(self, tr)

        # Zoom between two points until a fraction shows up.
        Z = ZoomLine(0.0, 3.0, length=12.8, center=np.array([0, y, 0]), label_size=24)
        a, b = R2, sqrt(2.005)
        da, db = Z.dot(a, color=FG, radius=0.12), Z.dot(b, color=FG, radius=0.12)
        qd = Z.dot(1.415, color=TERTIARY, radius=0.12)
        qlab = always_redraw(lambda: math(r"\frac{283}{200}", size=36, color=TERTIARY).next_to(Z.p(1.415), UP, buff=0.35)
                             .set_opacity(qd.show.get_value()))
        with self.voiceover(text=N("s05.b5")) as tr:
            self.play(FadeOut(P), FadeOut(glow), run_time=0.4)
            self.remove(R)
            self.add(Z, da, db, qd, qlab)
            self.play(da.show.animate.set_value(1), db.show.animate.set_value(1), run_time=0.5)
            wait_until(self, tr, "between")
            self.play(*Z.zoom_to(1.4128, 1.4168), run_time=rt(min(2.2, tr.get_remaining_duration() * 0.6)))
            self.play(qd.show.animate.set_value(1), run_time=0.5)
            rest(self, tr)

        ops = VGroup(math("+", size=70), math(r"\times", size=70)).arrange(RIGHT, buff=0.8).move_to([0, 1.5, 0])
        sts = VGroup(*[cross(o.get_center(), s=0.45, width=8) for o in ops])
        less = math("<", size=110, color=PRIMARY).move_to([0, 1.2, 0])
        with self.voiceover(text=N("s05.b6")) as tr:
            self.play(FadeIn(ops), run_time=0.5)
            self.play(Create(sts), run_time=0.6)
            wait_until(self, tr, "only")
            self.play(FadeOut(ops), FadeOut(sts), run_time=0.4)
            self.play(FadeIn(less, scale=0.6), run_time=0.5)
            rest(self, tr)
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.6)


# ---------------------------------------------------------------------------
# s06 Cut other lines
# ---------------------------------------------------------------------------


PIECES = [(0, 1), (2, 3)]


def two_piece(unit, y, x0=0.0, qmax=9, labels=True, r=0.08):
    line = RatLine(0, 3, unit, y=y, x0=x0, qmax=qmax, pieces=PIECES, r=r)
    line.holes = VGroup(*[line.hollow(v) for v in range(4)])
    line.add(line.holes)
    if labels:
        line.nums = line.numbers(range(4), size=32)
        line.add(line.nums)
    return line


def three_tags(names=("dense", "no ends", "can be listed"), size=32, y=3.1):
    ts = VGroup(*[tag(s, size, PRIMARY) for s in names]).arrange(RIGHT, buff=1.4).move_to([0.3, y, 0])
    return ts, VGroup(*[tick(t) for t in ts])


class S06Others(VoiceoverScene):
    def construct(self):
        self.set_speech_service(get_speech_service())
        y = 0.4
        T = two_piece(3.6, y, qmax=10)
        ts, tks = three_tags()
        with self.voiceover(text=N("s06.b1")) as tr:
            self.play(FadeIn(T.axis), FadeIn(T.dots), FadeIn(T.holes), run_time=1.0)
            wait_until(self, tr, "pieces")
            self.play(FadeIn(T.nums), Indicate(T.dots, color=PRIMARY, scale_factor=1.0), run_time=1.0)
            self.play(LaggedStart(*[AnimationGroup(FadeIn(t), Create(k)) for t, k in zip(ts, tks)], lag_ratio=0.4),
                      run_time=rt(min(1.8, tr.get_remaining_duration())))
            rest(self, tr)

        sc = scissors().move_to([T.x(0.618), y + 0.8, 0])
        fill_pt = Dot(T.p(0.618), radius=0.1, color=PRIMARY)
        seg1 = Line(T.p(0), T.p(1), color=FG, stroke_width=7)
        seg2 = Line(T.p(2), T.p(3), color=FG, stroke_width=7)
        with self.voiceover(text=N("s06.b2")) as tr:
            self.play(FadeIn(sc, shift=DOWN * 0.3), run_time=0.5)
            self.play(FadeIn(fill_pt, scale=2), run_time=0.4)
            wait_until(self, tr, "fill")
            self.play(Create(seg1), Create(seg2), T.dots.animate.set_opacity(0.3), FadeOut(fill_pt), FadeOut(sc),
                      T.holes.animate.set_z_index(5), run_time=rt(min(1.5, tr.get_remaining_duration())))
            rest(self, tr)

        sc2 = scissors().move_to([T.x(1.5), y + 0.8, 0])
        mid = T.p(1.5)
        ring = hollow_at(mid, r=0.16, color=PRIMARY)
        pt = Dot(mid, radius=0.13, color=PRIMARY)
        with self.voiceover(text=N("s06.b3")) as tr:
            self.play(FadeIn(sc2, shift=DOWN * 0.3), run_time=0.5)
            wait_until(self, tr, "break")
            self.play(seg1.animate.set_color(LEFT_C), seg2.animate.set_color(RIGHT_C), run_time=0.6)
            self.play(Create(ring), run_time=0.5)
            wait_until(self, tr, "heal")
            self.play(FadeIn(pt), FadeOut(ring), FadeOut(sc2), run_time=0.4)
            # Slide the two solid pieces together around the new point.
            gap = T.x(2) - T.x(1)
            hole1, hole2 = T.holes[1], T.holes[2]
            self.play(VGroup(seg1, T.holes[0]).animate.shift(RIGHT * gap / 2).set_stroke(color=FG),
                      VGroup(seg2, T.holes[3]).animate.shift(LEFT * gap / 2).set_stroke(color=FG),
                      FadeOut(hole1), FadeOut(hole2), FadeOut(T.dots), FadeOut(T.axis), FadeOut(T.nums),
                      pt.animate.set_color(FG).scale(0.8), run_time=1.2)
            rest(self, tr)

        healed = VGroup(seg1, seg2, pt, T.holes[0], T.holes[3])
        eq = math("=", size=60, color=PRIMARY)
        R = solid_line(-5.4, 5.4, -1.8)
        rlab = tag("the real line", 30, FG).next_to(R, DOWN, buff=0.25)
        with self.voiceover(text=N("s06.b4")) as tr:
            wait_until(self, tr, "equal")
            eq.move_to([0, (y + -1.8) / 2, 0])
            self.play(FadeIn(eq), Create(R), FadeIn(rlab), run_time=0.9)
            rest(self, tr)

        D = RatLine(-1.5, 1.5, 3.6, y=y, qmax=1, r=0.09, vals=[])
        levels = []
        for k in range(0, 6):
            vs = [Fr(p, 2 ** k) for p in range(-3 * 2 ** (k - 1) if k else -1, 3 * 2 ** (k - 1) + 1 if k else 2)
                  if Fr(p, 2 ** k).denominator == 2 ** k and -1.5 < Fr(p, 2 ** k) < 1.5]
            levels.append(VGroup(*[Dot(D.p(v), radius=0.09 * (2 ** k) ** -0.3, color=FG) for v in vs]))
        axisD = Line(D.p(-1.5), D.p(1.5), color=MUTED, stroke_width=3)
        dlabs = VGroup(*[math(s, size=30, color=MUTED).next_to(D.p(v), DOWN, buff=0.25)
                         for v, s in [(-1, "-1"), (Fr(-1, 2), r"-\frac12"), (0, "0"), (Fr(1, 4), r"\frac14"),
                                      (Fr(1, 2), r"\frac12"), (Fr(3, 4), r"\frac34"), (1, "1")]])
        dname = tag("fractions with a power of two on the bottom", 36, FG).move_to([0, y + 1.3, 0])
        segD = solid_line(-5.4, 5.4, y)
        with self.voiceover(text=N("s06.b5")) as tr:
            self.play(FadeOut(healed), FadeOut(ts), FadeOut(tks), run_time=0.5)
            self.play(Create(axisD), FadeIn(dname), FadeIn(dlabs), run_time=0.6)
            for lv in levels:
                self.play(FadeIn(lv, lag_ratio=0.05), run_time=0.35)
            wait_until(self, tr, "dyadic")
            self.play(FadeIn(segD), *[lv.animate.set_opacity(0.25) for lv in levels], FadeOut(axisD), run_time=0.9)
            rest(self, tr)

        # Threads: the rationals on top, the two-piece line below, an order-preserving match.
        self.play(FadeOut(VGroup(segD, dname, dlabs, eq, R, rlab, *levels)), run_time=0.5)
        top = RatLine(-3, 3, 2.0, y=1.6, qmax=5, r=0.06)
        bot = two_piece(3.6, -1.6, qmax=9, labels=False, r=0.05)

        def f(x):
            s = 1 / (1 + np.exp(-1.3 * x))
            return s * 2 if x < 0 else 2 + (s - 0.5) * 2

        tvals = [v for v in top.by if v != 0]
        threads = VGroup(*[Line(top.p(v), bot.p(f(float(v))), color=MUTED, stroke_width=1.6, stroke_opacity=0.7)
                           for v in tvals])
        c = 0.7
        scT = scissors(54).move_to([top.x(c), 2.35, 0])
        scB = scissors(54).move_to([bot.x(f(c)), -0.85, 0])
        tl = tag("the rationals", 30, MUTED).next_to(top, UP, buff=0.3).align_to(top, LEFT)
        bl = tag("two pieces", 30, MUTED).next_to(bot, DOWN, buff=0.3).align_to(bot, LEFT)
        with self.voiceover(text=N("s06.b6")) as tr:
            self.play(FadeIn(top), FadeIn(bot), FadeIn(tl), FadeIn(bl), run_time=0.7)
            wait_until(self, tr, "threads")
            self.play(LaggedStart(*[Create(t) for t in threads], lag_ratio=0.02), run_time=1.4)
            wait_until(self, tr, "carry")
            self.play(FadeIn(scT, shift=DOWN * 0.2), top.left_of(c).animate.set_color(LEFT_C),
                      top.right_of(c).animate.set_color(RIGHT_C), run_time=0.6)
            lefts = [t for t, v in zip(threads, tvals) if v < c]
            rights = [t for t, v in zip(threads, tvals) if v > c]
            self.play(*[t.animate.set_stroke(LEFT_C, opacity=0.9) for t in lefts],
                      *[t.animate.set_stroke(RIGHT_C, opacity=0.9) for t in rights], run_time=0.7)
            self.play(FadeIn(scB, shift=DOWN * 0.2), bot.left_of(f(c)).animate.set_color(LEFT_C),
                      bot.right_of(f(c)).animate.set_color(RIGHT_C), run_time=0.6)
            rest(self, tr)
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.6)


# ---------------------------------------------------------------------------
# s07 Only one line
# ---------------------------------------------------------------------------


class S07OnlyOne(VoiceoverScene):
    def construct(self):
        self.set_speech_service(get_speech_service())
        y = -0.6
        L = solid_line(-6.2, 6.2, y)
        name = tag("some line", 30, FG).next_to(L, DOWN, buff=0.3).shift(LEFT * 4.5)
        qm = text("?", size=70, color=PRIMARY).move_to([0, y + 1.1, 0])
        tags = fact_tags_grid(FACTS4, size=36, y=3.1, dx=3.4, dy=0.75)
        tags[0].move_to([-4.2, 3.1, 0])
        tags[1].move_to([-0.6, 3.1, 0])
        tags[2].move_to([3.0, 3.1, 0])
        tags[3].move_to([0, 2.25, 0])
        tks = VGroup(*[tick(t) for t in tags])
        with self.voiceover(text=N("s07.b1")) as tr:
            self.play(Create(L), FadeIn(name), FadeIn(qm), run_time=0.8)
            for mark, i in (("f1", 0), ("f2", 1), ("f3", 2), ("f4", 3)):
                wait_until(self, tr, mark)
                self.play(FadeIn(tags[i]), Create(tks[i]), run_time=0.5)
            rest(self, tr)

        box = SurroundingRectangle(VGroup(tags, tks), color=MUTED, buff=0.2, corner_radius=0.1)
        Rr = solid_line(-6.2, 6.2, -2.8)
        eq = math("=", size=56, color=PRIMARY).move_to([0, -1.7, 0])
        rlab = tag("the real line", 28, FG).next_to(Rr, DOWN, buff=0.2).shift(LEFT * 4.5)
        cantor = tag("Cantor, 1895", 30, MUTED).move_to([4.6, -1.7, 0])
        with self.voiceover(text=N("s07.b2")) as tr:
            self.play(Create(box), FadeOut(qm), run_time=0.5)
            wait_until(self, tr, "real")
            self.play(FadeIn(eq), Create(Rr), FadeIn(rlab), FadeIn(cantor), run_time=0.9)
            rest(self, tr)

        # The countable set D, drawn as gold dots on the line.
        ys = y
        Dv = rats(-3.2, 3.2, 6)
        unit = 1.9
        Dd = VGroup(*[Dot([float(v) * unit, ys, 0], radius=0.095 * Fr(v).denominator ** -0.3, color=PRIMARY) for v in Dv])
        Dcopy = Dd.copy()
        ylow = -2.6
        dl_axis = Line([-6.2, ylow, 0], [6.2, ylow, 0], color=MUTED, stroke_width=3)
        dtags = VGroup(tag("dense", 34, PRIMARY), tag("no ends", 34, PRIMARY), tag("can be listed", 34, PRIMARY))
        dtags.arrange(RIGHT, buff=1.0).move_to([0.3, -1.7, 0])
        dtk = VGroup(*[tick(t) for t in dtags])
        isq = tag("= the rationals", 36, PRIMARY).move_to([0, -3.4, 0])
        with self.voiceover(text=N("s07.b3")) as tr:
            self.play(FadeOut(VGroup(box, tags, tks, eq, Rr, rlab, cantor)), run_time=0.5)
            self.play(FadeIn(Dd, lag_ratio=0.01), run_time=0.8)
            self.add(Dcopy)
            self.play(Dcopy.animate.shift(DOWN * (ys - ylow)), FadeIn(dl_axis), run_time=0.8)
            wait_until(self, tr, "dots")
            self.play(LaggedStart(*[AnimationGroup(FadeIn(t), Create(k)) for t, k in zip(dtags, dtk)], lag_ratio=0.4),
                      run_time=1.4)
            wait_until(self, tr, "q")
            self.play(FadeIn(isq), run_time=0.5)
            rest(self, tr)

        xp = 0.83 * unit
        P = Dot([xp, ys, 0], radius=0.16, color=FG)
        left_D = VGroup(*[d for d, v in zip(Dd, Dv) if float(v) * unit < xp])
        plab = tag("the point", 34, FG).next_to(P, UP, buff=0.35)
        with self.voiceover(text=N("s07.b4")) as tr:
            self.play(FadeOut(VGroup(Dcopy, dl_axis, dtags, dtk, isq)), run_time=0.5)
            self.play(FadeIn(P, scale=2), FadeIn(plab), run_time=0.5)
            wait_until(self, tr, "left")
            self.play(left_D.animate.set_color(LEFT_C), run_time=0.9)
            rest(self, tr)

        xp2 = 1.32 * unit
        P2 = Dot([xp2, ys, 0], radius=0.16, color=FG)
        between = [d for d, v in zip(Dd, Dv) if xp < float(v) * unit < xp2]
        bdot = between[len(between) // 2]
        bring = Circle(radius=0.2, color=PRIMARY, stroke_width=4).move_to(bdot)
        skip = tag("(a small detail skipped)", 26, MUTED).move_to([0, -2.9, 0])
        every = tag("every cut of the dots  \u2192  some point", 38, FG).move_to([0, -2.1, 0])
        with self.voiceover(text=N("s07.b5")) as tr:
            wait_until(self, tr, "diff")
            self.play(FadeIn(P2, scale=2), plab.animate.set_opacity(0), run_time=0.5)
            self.play(Create(bring), bdot.animate.set_color(PRIMARY).scale(1.6), run_time=0.6)
            self.wait(rt(min(1.0, tr.get_remaining_duration() * 0.3)))
            self.play(FadeIn(every), FadeIn(skip), run_time=0.7)
            rest(self, tr)

        chain = VGroup(tag("the line", 34, FG), math("=", size=44), tag("cuts of the dots", 34, FG), math("=", size=44),
                       tag("cuts of the rationals", 34, FG), math("=", size=44), tag("the real line", 34, PRIMARY))
        chain.arrange(RIGHT, buff=0.22).move_to(UP * 1.6)
        chain.scale_to_fit_width(min(chain.width, FW - 0.8))
        with self.voiceover(text=N("s07.b6")) as tr:
            self.play(FadeOut(VGroup(every, skip, P2, bring)), FadeIn(chain[0]), run_time=0.5)
            for mark, i in (("c1", 1), ("c2", 3), ("c3", 5)):
                wait_until(self, tr, mark)
                self.play(FadeIn(chain[i]), FadeIn(chain[i + 1]), run_time=0.5)
            rest(self, tr)

        big = tag("a point  =  the dots to its left", 44, PRIMARY).move_to(UP * 2.0)
        with self.voiceover(text=N("s07.b7")) as tr:
            self.play(FadeOut(chain), run_time=0.4)
            wait_until(self, tr, "point")
            self.play(FadeIn(big), Indicate(P, color=PRIMARY), *[d.animate.scale(1.6) for d in left_D], run_time=0.9)
            rest(self, tr)
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.6)


# ---------------------------------------------------------------------------
# s08 Each fact has a job
# ---------------------------------------------------------------------------


class S08Jobs(VoiceoverScene):
    def construct(self):
        self.set_speech_service(get_speech_service())
        T = FactTable(["rationals", "segment", "integers", "long"])
        rowk = ["rationals", "segment", "integers"]
        with self.voiceover(text=N("s08.b1")) as tr:
            self.play(FadeIn(T.head), Create(T.rule), run_time=0.7)
            for mark, k in zip(("q", "seg", "z"), rowk):
                wait_until(self, tr, mark)
                self.play(FadeIn(T.rows[k]), FadeIn(T.pics[k]), run_time=0.4)
                self.play(LaggedStart(*[Create(m) for m in T.marks[k]], lag_ratio=0.15), run_time=0.7)
            rest(self, tr)

        qbox = text("?", size=50, color=PRIMARY).move_to(T.pics["long"])
        with self.voiceover(text=N("s08.b2")) as tr:
            wait_until(self, tr, "long")
            self.play(FadeIn(T.rows["long"]), FadeIn(qbox), run_time=0.5)
            self.play(LaggedStart(*[Create(m) for m in T.marks["long"][:3]], lag_ratio=0.2), run_time=0.8)
            rest(self, tr)

        # Counting past infinity.
        y = -0.2
        LR = LongRay(-6.3, 6.4, y)
        labs = LR.labels()
        k0 = VGroup(*[LR.ticks[n] for n in range(LR.per)])
        k1 = VGroup(*[LR.ticks[LR.per + n] for n in range(1, LR.per)])
        rest_ticks = VGroup(*[LR.ticks[k * LR.per + n] for k in range(2, LR.blocks) for n in range(LR.per)])
        axis = Line([-6.3, y, 0], [LR.xw2, y, 0], color=MUTED, stroke_width=2)
        with self.voiceover(text=N("s08.b3")) as tr:
            self.play(FadeOut(VGroup(T.head, T.rule, qbox, *T.rows.values(), *[T.pics[k] for k in rowk],
                                     *T.marks.values())), run_time=0.5)
            self.play(FadeIn(axis), LaggedStart(*[Create(t) for t in k0], lag_ratio=0.15), FadeIn(labs[:4]), run_time=1.4)
            wait_until(self, tr, "omega")
            self.play(Create(LR.tall[1]), FadeIn(labs[4]), run_time=0.6)
            wait_until(self, tr, "o1")
            self.play(LaggedStart(*[Create(t) for t in k1], lag_ratio=0.1), FadeIn(labs[5]), run_time=0.9)
            wait_until(self, tr, "o2")
            self.play(Create(rest_ticks), FadeIn(labs[6]), FadeIn(labs[7]), run_time=1.0)
            wait_until(self, tr, "o3")
            self.play(Create(LR.w2), FadeIn(labs[8]), run_time=0.6)
            rest(self, tr)

        before = Rectangle(width=LR.xw2 - LR.x0 + 0.1, height=0.9, stroke_width=0, fill_color=PRIMARY,
                           fill_opacity=0.18).move_to([(LR.x0 + LR.xw2) / 2, y, 0])
        cnt = tag("only countably many positions before it", 38, PRIMARY).move_to([0, 2.3, 0])
        with self.voiceover(text=N("s08.b4")) as tr:
            wait_until(self, tr, "before")
            self.play(FadeIn(before), Indicate(LR.w2, color=PRIMARY), FadeIn(cnt), run_time=0.9)
            self.wait(rt(min(1.5, tr.get_remaining_duration() * 0.5)))
            self.play(FadeIn(LR.tail), run_time=0.8)
            rest(self, tr)

        picks = [(0, 3), (1, 2), (2, 1), (3, 0), (4, 3)]
        pdots = VGroup(*[Dot(LR.p(k, n), radius=0.11, color=RIGHT_C) for k, n in picks])
        marker = Triangle(color=GOOD, fill_opacity=1, stroke_width=0).scale(0.18).rotate(PI)
        marker.move_to([LR.x0, y + 0.75, 0])
        after = tag("after all of them", 36, GOOD).move_to([LR.xw2 - 0.6, y + 1.5, 0])
        nolist = tag("so no list holds every position", 38, FG).move_to([0, -2.6, 0])
        with self.voiceover(text=N("s08.b5")) as tr:
            self.play(FadeOut(before), FadeOut(cnt), FadeIn(pdots, lag_ratio=0.2), run_time=0.9)
            wait_until(self, tr, "after")
            self.play(FadeIn(marker), run_time=0.3)
            self.play(marker.animate.move_to([LR.xw2, y + 0.75, 0]), run_time=1.4)
            self.play(FadeIn(after), Indicate(LR.w2, color=GOOD), run_time=0.6)
            self.wait(rt(min(2.0, tr.get_remaining_duration() - 1.2)))
            self.play(FadeIn(nolist), run_time=0.6)
            rest(self, tr)

        cap = tag("shrunk to fit on screen; every copy is the same length", 30, MUTED).move_to([0, -3.3, 0])
        with self.voiceover(text=N("s08.b6")) as tr:
            self.play(FadeOut(VGroup(pdots, marker, after, nolist)), run_time=0.4)
            wait_until(self, tr, "lay")
            self.play(FadeOut(axis), LaggedStart(*[Create(c) for c in LR.copies], lag_ratio=0.01),
                      FadeIn(LR.starts), FadeIn(cap), run_time=1.6)
            wait_until(self, tr, "nohole")
            pw = LR.p(1)
            zoomables = VGroup(LR.copies, LR.ticks, LR.w2, LR.tail)
            self.play(FadeOut(labs), FadeOut(LR.starts), zoomables.animate.scale(4.0, about_point=pw), run_time=1.0)
            ring = Circle(radius=0.3, color=GOOD, stroke_width=4).move_to(pw)
            self.play(Create(ring), run_time=0.4)
            self.wait(0.6)
            self.play(FadeOut(ring), zoomables.animate.scale(0.25, about_point=pw), run_time=0.9)
            self.play(FadeIn(LR.starts), run_time=0.3)
            rest(self, tr)

        # Squeeze into the right half, then mirror.
        ray = VGroup(LR.copies, LR.starts, LR.ticks, LR.w2, LR.tail)
        x_mid = 0.0
        with self.voiceover(text=N("s08.b7")) as tr:
            self.play(FadeOut(cap), run_time=0.3)
            target = ray.copy()
            target.stretch(6.5 / (LR.x1 + 0.25 - LR.x0), 0, about_point=np.array([LR.x0, y, 0]))
            target.shift(RIGHT * (x_mid - LR.x0))
            self.play(Transform(ray, target), run_time=1.0)
            nolast = tag("no last point", 34, FG).move_to([5.0, y + 1.0, 0])
            self.play(FadeIn(nolast), run_time=0.4)
            wait_until(self, tr, "mirror")
            mirror = ray.copy().flip(UP, about_point=np.array([x_mid, y, 0]))
            self.play(TransformFromCopy(ray, mirror), run_time=1.1)
            nofirst = tag("no first point", 34, FG).move_to([-5.0, y + 1.0, 0])
            name = tag("the long line", 48, PRIMARY).move_to([0, 2.4, 0])
            self.play(FadeIn(nofirst), FadeIn(name), run_time=0.6)
            rest(self, tr)

        both = VGroup(ray, mirror)
        spots = [-3.3, 0.9, 2.6]
        L0 = lens(np.array([spots[0], 1.9, 0]))
        stalk = always_redraw(lambda: Line(L0.get_bottom(), [L0.get_center()[0], y + 0.12, 0], color=FG, stroke_width=2))
        spot = always_redraw(lambda: Circle(radius=0.16, color=FG, stroke_width=3).move_to([L0.get_center()[0], y, 0]))
        ordinary = tag("between any two points: an ordinary interval", 38, FG).move_to([0, -2.3, 0])
        with self.voiceover(text=N("s08.b8")) as tr:
            self.play(FadeOut(VGroup(nofirst, nolast, name)), run_time=0.4)
            wait_until(self, tr, "zoom")
            self.add(stalk, spot)
            self.play(FadeIn(L0), run_time=0.5)
            for x in spots[1:]:
                self.play(L0.animate.move_to([x, 1.9, 0]), run_time=1.0)
            self.play(FadeIn(ordinary), run_time=0.6)
            rest(self, tr)

        # No countable set spreads through it.
        gpicks = [(0, 0), (0, 2), (0, 5), (1, 0), (1, 3), (0, 7), (1, 1)]
        gd = VGroup(*[Dot((LR.copies[k * LR.per + n].get_start() + LR.copies[k * LR.per + n].get_end()) / 2,
                          radius=0.09, color=RIGHT_C) for k, n in gpicks])
        mgd = VGroup(*[d.copy().move_to([-d.get_center()[0], y, 0]) for d in gd])
        empty = LR.copies[2 * LR.per]
        marker2 = Triangle(color=GOOD, fill_opacity=1, stroke_width=0).scale(0.16).rotate(PI).move_to([0.0, y + 0.5, 0])
        nodot = tag("no dot in this copy", 36, GOOD).move_to([empty.get_center()[0] + 0.8, y + 1.4, 0])
        with self.voiceover(text=N("s08.b9")) as tr:
            self.play(FadeOut(VGroup(L0, ordinary)), run_time=0.3)
            self.remove(stalk, spot)
            self.play(FadeIn(gd, lag_ratio=0.1), FadeIn(mgd, lag_ratio=0.1), run_time=1.0)
            wait_until(self, tr, "empty")
            self.play(FadeIn(marker2), run_time=0.3)
            self.play(marker2.animate.move_to([empty.get_center()[0], y + 0.5, 0]), run_time=1.0)
            self.play(empty.animate.set_stroke(GOOD, width=10), FadeIn(nodot), run_time=0.6)
            rest(self, tr)

        T2 = FactTable(["rationals", "segment", "integers", "long"])
        with self.voiceover(text=N("s08.b10")) as tr:
            self.play(FadeOut(VGroup(both, gd, mgd, marker2, nodot)), run_time=0.5)
            self.play(FadeIn(VGroup(T2.head, T2.rule, *T2.rows.values(), *T2.pics.values(),
                                    *[T2.marks[k] for k in rowk], T2.marks["long"][:3])), run_time=0.8)
            wait_until(self, tr, "cross")
            self.play(Create(T2.marks["long"][3]), Indicate(T2.rows["long"], color=PRIMARY), run_time=0.7)
            rest(self, tr)
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.6)


# ---------------------------------------------------------------------------
# s09 A question with no answer
# ---------------------------------------------------------------------------


def four_tags_column(names, size=32, x=-6.4, y=2.9, buff=0.3, color=PRIMARY):
    g = VGroup(*[tag(s, size, color) for s in names]).arrange(DOWN, aligned_edge=LEFT, buff=buff)
    g.move_to([x, y, 0], aligned_edge=UL)
    return g


class S09Suslin(VoiceoverScene):
    def construct(self):
        self.set_speech_service(get_speech_service())
        tags = four_tags_column(FACTS4, size=36, x=-6.3, y=3.4)
        new = tag(SUSLIN_FACT, 36, GOOD).move_to(tags[3], aligned_edge=LEFT)
        with self.voiceover(text=N("s09.b1")) as tr:
            self.play(FadeIn(tags, lag_ratio=0.2), run_time=0.9)
            wait_until(self, tr, "swap")
            self.play(tags[3].animate.shift(RIGHT * 9).set_opacity(0), run_time=0.6)
            self.play(FadeIn(new, shift=RIGHT * 0.5), run_time=0.6)
            rest(self, tr)

        y = -0.8
        R = solid_line(-6.3, 6.3, y)
        ivs = [(-5.6, -4.4), (-3.9, -3.1), (-2.6, -1.0), (-0.6, 0.1), (0.5, 1.9), (2.4, 3.0), (3.5, 5.6)]
        cols = [PRIMARY, SECONDARY, TERTIARY, GOOD]
        bars = VGroup(*[Rectangle(width=b - a, height=0.32, stroke_width=0, fill_color=cols[i % 4], fill_opacity=0.55)
                        .move_to([(a + b) / 2, y, 0]) for i, (a, b) in enumerate(ivs)])
        qs = VGroup(*[Dot([a + (b - a) * 0.37, y, 0], radius=0.09, color=FG) for a, b in ivs])
        listed = VGroup(*[math(f"q_{{{i + 1}}}", size=42).move_to([-4.8 + i * 1.3, y - 1.5, 0]) for i in range(len(ivs))])
        dots = math(r"\dots", size=42).next_to(listed, RIGHT, buff=0.3)
        with self.voiceover(text=N("s09.b2")) as tr:
            self.play(Create(R), run_time=0.6)
            self.play(LaggedStart(*[GrowFromCenter(b) for b in bars], lag_ratio=0.12), run_time=1.2)
            wait_until(self, tr, "frac")
            self.play(FadeIn(qs, lag_ratio=0.1), run_time=0.7)
            self.play(*[TransformFromCopy(q, l) for q, l in zip(qs, listed)], FadeIn(dots), run_time=1.0)
            rest(self, tr)

        LL = long_line_both(0.0, 6.2, y, blocks=6, per=8)
        hl = VGroup()
        for half in LL:
            for i, c in enumerate(half.copies):
                hl.add(c)
        xx = cross(np.array([0, y + 1.3, 0]), s=0.35, width=9)
        with self.voiceover(text=N("s09.b3")) as tr:
            self.play(FadeOut(VGroup(R, bars, qs, listed, dots)), FadeIn(LL), run_time=0.8)
            wait_until(self, tr, "copies")
            self.play(*[c.animate.set_stroke(cols[i % 4], width=9) for i, c in enumerate(hl)], run_time=0.9)
            self.play(Create(xx), run_time=0.5)
            rest(self, tr)

        box = VGroup(tags[:3], new)
        eq = math("=", size=64, color=PRIMARY)
        R2l = solid_line(-6.0, 6.0, y)
        big_q = text("?", size=90, color=PRIMARY)
        suslin = tag("Suslin (published 1920)", 36, MUTED)
        with self.voiceover(text=N("s09.b4")) as tr:
            self.play(FadeOut(LL), FadeOut(xx), run_time=0.5)
            self.play(box.animate.move_to([0, 2.4, 0]), run_time=0.7)
            eq.move_to([0, 0.75, 0])
            big_q.next_to(eq, RIGHT, buff=0.3)
            suslin.move_to([0, -2.0, 0])
            self.play(FadeIn(eq), FadeIn(R2l), FadeIn(suslin), run_time=0.7)
            wait_until(self, tr, "ask")
            self.play(FadeIn(big_q, scale=0.6), run_time=0.5)
            rest(self, tr)

        l1 = tag("can't be proved: Jech, Tennenbaum (1967-68)", 34, FG)
        l2 = tag("can't be disproved: Solovay, Tennenbaum (1971)", 34, FG)
        l3 = tag("from the usual axioms of math (ZFC)", 34, PRIMARY)
        lines = VGroup(l1, l2, l3).arrange(DOWN, buff=0.25).move_to([0, -2.4, 0])
        with self.voiceover(text=N("s09.b5")) as tr:
            self.play(FadeOut(suslin), R2l.animate.shift(UP * 0.4), run_time=0.5)
            wait_until(self, tr, "yes")
            self.play(FadeIn(l1), run_time=0.6)
            wait_until(self, tr, "no")
            self.play(FadeIn(l2), run_time=0.6)
            self.play(FadeIn(l3), run_time=0.6)
            rest(self, tr)

        rows = VGroup()
        Q = RatLine(-2, 2, 2.2, y=1.9, x0=1.2, qmax=8, r=0.06)
        Rl = solid_line(-3.2, 5.6, 0.0)
        F = Line([-3.2, -1.9, 0], [5.6, -1.9, 0], color=MUTED, stroke_width=4, stroke_opacity=0.5)
        names = VGroup(tag("3 facts", 34, PRIMARY).move_to([-5.2, 1.9, 0]), tag("4 facts", 34, PRIMARY).move_to([-5.2, 0, 0]),
                       text("?", size=60, color=PRIMARY).move_to([-5.2, -1.9, 0]))
        with self.voiceover(text=N("s09.b6")) as tr:
            self.play(FadeOut(VGroup(box, eq, big_q, R2l, lines)), run_time=0.6)
            self.play(FadeIn(Q), FadeIn(names[0]), run_time=0.6)
            self.play(FadeIn(Rl), FadeIn(names[1]), run_time=0.6)
            wait_until(self, tr, "end")
            self.play(FadeIn(F), FadeIn(names[2]), run_time=0.7)
            rest(self, tr)
        self.wait(1.5)
        self.play(FadeOut(Group(*self.mobjects)), run_time=1.0)


# ---------------------------------------------------------------------------
# Thumbnail
# ---------------------------------------------------------------------------


class Thumbnail(Scene):
    def construct(self):
        y = -1.6
        L = RatLine(-0.4, 3.2, 3.7, y=y, qmax=12, r=0.1)
        L.left_of(R2).set_color(LEFT_C)
        L.right_of(R2).set_color(RIGHT_C)
        L.left_of(R2).shift(LEFT * 0.12)
        L.right_of(R2).shift(RIGHT * 0.12)
        sc = scissors(150).move_to([L.x(R2), y + 1.35, 0])
        ring = hollow_at(L.p(R2), r=0.17, color=FG)
        lab = math(r"\sqrt{2}", size=80, color=FG).next_to(ring, DOWN, buff=0.45)
        t1 = text("A real number", size=96, weight="BOLD").move_to([0, 2.7, 0])
        t2 = text("is a cut", size=96, weight="BOLD", color=PRIMARY).next_to(t1, DOWN, buff=0.2)
        self.add(L, ring, sc, lab, t1, t2)
