"""Compactness: solving infinitely many problems at once. Long-form scenes."""

from math import asin, cos, pi, sin, sqrt

import numpy as np
from manim import *
from manim_voiceover import VoiceoverScene

from mathvid import layout  # noqa: F401  must come before scene code runs
from mathvid.anim import rest, rt, strike, wait_until
from mathvid.layout import FH, FW
from mathvid.numberline import RealLine
from mathvid.orders import cross, tick
from mathvid.script import Script
from mathvid.style import (BAD, BG, FG, GOOD, MUTED, PRIMARY, SECONDARY, TERTIARY, math, text,
                           title_card)
from mathvid.voice import get_speech_service

N = Script(__file__)

TITLE = "Compactness"
WEIRD = TERTIARY  # the new world compactness hands us

# The four colors of a coloring attempt, and the seven of the hexagon tiling.
C4 = [BAD, SECONDARY, PRIMARY, GOOD]
C7 = ["#E06C75", "#F2B33D", "#7BC67B", "#4FB0C6", "#C678DD", "#D19A66", "#8A8FD8"]


# ---------------------------------------------------------------------------
# Shared builders (also used by shorts.py)
# ---------------------------------------------------------------------------


def column(lines, size=46, buff=0.26, dots=True, color=FG):
    """A column of formulas, left-aligned, with a vdots at the bottom."""
    g = VGroup(*[math(s, size=size, color=color) for s in lines])
    if dots:
        g.add(math(r"\vdots", size=size, color=color))
    g.arrange(DOWN, buff=buff, aligned_edge=LEFT)
    if dots:
        g[-1].shift(RIGHT * 0.35)
    return g


def drop_in(scene, mobs, total):
    """Fade mobjects in one after another over `total` seconds."""
    per = rt(total / max(1, len(mobs)))
    for m in mobs:
        scene.play(FadeIn(m, shift=DOWN * 0.25), run_time=per)


def side_brace(group, direction=RIGHT, color=PRIMARY):
    return Brace(group, direction=direction, color=color, buff=0.15)


def far_line(y=-2.4, left=-6.0, right=6.0, n=5, unit=0.8, color=WEIRD, c_at=None):
    """The new world's line: 1, 2, 3, ... then, far past all of them, c."""
    g = VGroup()
    line = Line([left, y, 0], [right, y, 0], color=color, stroke_width=4)
    g.add(line)
    g.ticks = VGroup()
    for k in range(1, n + 1):
        x = left + 0.6 + k * unit
        g.ticks.add(VGroup(Line([x, y + 0.1, 0], [x, y - 0.1, 0], color=color, stroke_width=3),
                           math(str(k), size=32, color=MUTED).move_to([x, y - 0.4, 0])))
    dots = math(r"\cdots", size=36, color=MUTED).move_to([left + 0.6 + (n + 1.2) * unit, y + 0.15, 0])
    cx = c_at if c_at is not None else right - 0.8
    g.c = Dot([cx, y, 0], radius=0.11, color=PRIMARY)
    g.clab = math("c", size=46, color=PRIMARY).next_to(g.c, UP, 0.18)
    g.add(g.ticks, dots, g.c, g.clab)
    return g


def region(w, h, center, label=None, color=MUTED, size=30):
    box = RoundedRectangle(width=w, height=h, corner_radius=0.35, color=color, stroke_width=3)
    box.move_to(center)
    g = VGroup(box)
    g.box = box
    if label:
        g.label = text(label, size=size, color=color).next_to(box, UP, 0.15)
        g.add(g.label)
    return g


def theorem_box(width=11.0, size=36):
    t = VGroup(text("If every finite part of a set of sentences has a model,", size=size),
               text("then the whole set has a model.", size=size)).arrange(DOWN, buff=0.18)
    box = SurroundingRectangle(t, color=PRIMARY, buff=0.35, corner_radius=0.15)
    return VGroup(box, t)


def hyper_cloud(center, scale=1.0):
    """Points c^2, c/2, c, 2c spread around zero in a zoomed-in view."""
    g = VGroup()
    labs = [(r"c^2", 0.35), (r"\tfrac{c}{2}", 1.1), (r"c", 2.0), (r"2c", 3.6)]
    for s, x in labs:
        p = center + RIGHT * x * scale
        d = Dot(p, radius=0.08, color=PRIMARY)
        lab = math(s, size=32, color=PRIMARY).next_to(d, UP, 0.18)
        g.add(VGroup(d, lab))
    return g


# --- plane coloring -----------------------------------------------------------


def hex_tiling(unit=1.0, side=0.45, center=ORIGIN, radius=7.5, opacity=0.85, ymax=None):
    """Pointy-top hexagons of the given side (in math units), colored (q + 3r) mod 7."""
    s = side * unit
    g = VGroup()
    g.cells = {}
    R = int(max(radius, ymax or 0) / (s * 1.5)) + 2
    for q in range(-R - 4, R + 5):
        for r in range(-R, R + 1):
            x = s * sqrt(3) * (q + r / 2)
            y = s * 1.5 * r
            if abs(x) > radius + s or abs(y) > (ymax if ymax is not None else radius * 0.62) + s:
                continue
            col = C7[(q + 3 * r) % 7]
            h = RegularPolygon(6, start_angle=PI / 2, color=BG, stroke_width=1.5)
            h.scale_to_fit_height(2 * s).move_to(center + np.array([x, y, 0]))
            h.set_fill(col, opacity=opacity)
            g.add(h)
            g.cells[(q, r)] = h
    return g


def hex_center(q, r, unit, side, center=ORIGIN):
    s = side * unit
    return center + np.array([s * sqrt(3) * (q + r / 2), s * 1.5 * r, 0])


SPINDLE_PHI = 2 * asin(1 / (2 * sqrt(3)))  # turn between the two diamonds


def spindle_points(unit=1.6, base=ORIGIN):
    """Moser spindle: A, then (B, C, D) for each diamond. Tops are D1 and D2."""
    def diamond(theta):
        u = lambda a: np.array([cos(a), sin(a), 0])
        return (base + unit * u(theta - PI / 6), base + unit * u(theta + PI / 6),
                base + unit * sqrt(3) * u(theta))
    d1 = diamond(PI / 2 + SPINDLE_PHI / 2)
    d2 = diamond(PI / 2 - SPINDLE_PHI / 2)
    return base, d1, d2


def vdot(p, color=FG, r=0.12):
    return Dot(p, radius=r, color=color).set_stroke(BG, width=2, background=True)


def edge(a, b, color=MUTED, width=4):
    return Line(a, b, color=color, stroke_width=width)


def unit_graph(unit=0.6, center=ORIGIN, rad=3.2, rots=(0.0,)):
    """A real unit-distance graph: triangular lattice points, rotated, joined at distance 1."""
    pts = []
    for ang in rots:
        for a in range(-6, 7):
            for b in range(-6, 7):
                v = np.array([a + b / 2, b * sqrt(3) / 2])
                v = np.array([v[0] * cos(ang) - v[1] * sin(ang), v[0] * sin(ang) + v[1] * cos(ang)])
                if np.linalg.norm(v) <= rad and all(np.linalg.norm(v - w) > 1e-6 for w in pts):
                    pts.append(v)
    pts = np.array(pts)
    edges = VGroup()
    for i in range(len(pts)):
        for j in range(i + 1, len(pts)):
            if abs(np.linalg.norm(pts[i] - pts[j]) - 1) < 1e-6:
                edges.add(Line(center + unit * np.append(pts[i], 0), center + unit * np.append(pts[j], 0),
                               color=MUTED, stroke_width=1.2, stroke_opacity=0.7))
    dots = VGroup(*[Dot(center + unit * np.append(p, 0), radius=0.035, color=FG) for p in pts])
    return VGroup(edges, dots)


def bounds_line(lo, hi, y=0.0, length=9.0, x0=0.0, marks=(), shade=None, size=34):
    """A number line from lo to hi with integer labels, used for 'between 4 and 7'."""
    rl = RealLine(lo - 0.5, hi + 0.5, length=length, y=y, x0=x0, size=size, color=MUTED,
                  labels={k: str(k) for k in range(lo, hi + 1)})
    g = VGroup(rl)
    g.rl = rl
    g.marks = VGroup()
    for k in marks:
        g.marks.add(Dot(rl.p(k), radius=0.13, color=PRIMARY))
    g.add(g.marks)
    if shade:
        a, b = shade
        g.shade = Rectangle(width=rl.p(b)[0] - rl.p(a)[0], height=0.4, color=PRIMARY,
                            fill_opacity=0.25, stroke_width=0).move_to((rl.p(a) + rl.p(b)) / 2)
        g.add(g.shade)
    return g


# ---------------------------------------------------------------------------
# s01 Hook
# ---------------------------------------------------------------------------


class S01Hook(VoiceoverScene):
    def construct(self):
        self.set_speech_service(get_speech_service())
        q = VGroup(text("How do you solve infinitely many problems", size=54),
                   text("at the same time?", size=54)).arrange(DOWN, buff=0.2)
        a = text("Just solve every finite number of them.", size=54, color=PRIMARY)
        VGroup(q, a).arrange(DOWN, buff=0.8).move_to(UP * 0.2)
        with self.voiceover(text=N("s01.b1")) as tr:
            self.play(FadeIn(q, shift=UP * 0.2), run_time=1.0)
            wait_until(self, tr, "answer")
            self.play(FadeIn(a, shift=UP * 0.2), run_time=0.8)
            rest(self, tr)

        col = column([r"x > 1", r"x > 2", r"x > 3", r"x > 4", r"x > 5"], size=62, buff=0.3)
        col.move_to([-4.6, 0.2, 0])
        batch = VGroup(*col[:4])
        br = side_brace(batch)
        sol = VGroup(math(r"x = 5", size=44, color=PRIMARY)).next_to(br, RIGHT, 0.2)
        ok = tick(sol, s=1.0).next_to(sol, RIGHT, 0.25)
        rl = RealLine(0, 10, length=8.4, y=-0.6, x0=2.6, size=32)
        mk = Triangle(color=PRIMARY, fill_opacity=1, stroke_width=0).scale(0.14).rotate(PI)
        mk.move_to(rl.p(1) + UP * 0.3)
        big_x = cross(col.get_center(), s=1.9, width=10)
        with self.voiceover(text=N("s01.b2")) as tr:
            self.play(FadeOut(q), FadeOut(a), run_time=0.5)
            drop_in(self, list(col), min(3.0, tr.time_until_bookmark("batch") - 0.6))
            wait_until(self, tr, "batch")
            self.play(GrowFromCenter(br), FadeIn(sol), run_time=0.6)
            self.play(Create(ok), run_time=0.3)
            wait_until(self, tr, "all")
            self.play(FadeOut(VGroup(br, sol, ok)), Create(rl), FadeIn(mk), run_time=0.7)
            self.play(mk.animate.move_to(rl.p(10) + UP * 0.3), run_time=1.3, rate_func=linear)
            self.play(mk.animate.shift(RIGHT * 1.0).set_opacity(0), Create(big_x), run_time=0.6)
            rest(self, tr)

        fl = far_line(y=-0.6, left=-1.6, right=6.8, n=5, unit=0.85)
        fl_q = text("a new world", size=36, color=WEIRD).next_to(fl, UP, 0.5).align_to(fl, LEFT)
        good = tick(at=col.get_right() + RIGHT * 1.1, s=3.0)
        with self.voiceover(text=N("s01.b3")) as tr:
            self.play(FadeOut(rl), FadeOut(mk), run_time=0.5)
            wait_until(self, tr, "world")
            self.play(FadeIn(fl, shift=LEFT * 1.0), FadeIn(fl_q), run_time=0.9)
            self.play(ReplacementTransform(big_x, good), run_time=0.6)
            rest(self, tr)
        self.wait(0.3)
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.6)
        title_card(self, TITLE)


# ---------------------------------------------------------------------------
# s02 Worlds and sentences
# ---------------------------------------------------------------------------


LANG_Y = 3.25


def language_row(with_c=False):
    syms = [r"+", r"\times", r"<", r"0", r"1"] + ([r"c"] if with_c else [])
    g = VGroup(*[math(s, size=52, color=PRIMARY if s == "c" else FG) for s in syms]).arrange(RIGHT, buff=0.6)
    return g


class S02Worlds(VoiceoverScene):
    def construct(self):
        self.set_speech_service(get_speech_service())
        syms = language_row()
        lang_lab = text("language", size=30, color=MUTED)
        lang = VGroup(syms, lang_lab).arrange(RIGHT, buff=0.7).move_to([0, LANG_Y, 0])
        intro = VGroup(text("a problem = ?", size=48), text("a world = ?", size=48)).arrange(DOWN, buff=0.5)
        with self.voiceover(text=N("s02.b1")) as tr:
            self.play(FadeIn(intro[0], shift=UP * 0.2), run_time=0.6)
            self.wait(rt(tr.time_until_bookmark("syms") * 0.25))
            self.play(FadeIn(intro[1], shift=UP * 0.2), run_time=0.6)
            wait_until(self, tr, "syms")
            self.play(FadeOut(intro), run_time=0.4)
            self.play(LaggedStart(*[FadeIn(s, shift=DOWN * 0.2) for s in syms], lag_ratio=0.35),
                      run_time=rt(min(2.2, tr.get_remaining_duration() - 0.8)))
            self.play(FadeIn(lang_lab), run_time=0.5)
            rest(self, tr)

        # The two models.
        RY = -1.45
        left = region(6.2, 3.0, [-3.4, RY, 0], "the real numbers")
        right = region(6.2, 3.0, [3.4, RY, 0], "the integers")
        rl = RealLine(-1.5, 6.5, length=5.4, y=RY - 0.2, x0=-3.4, size=30,
                      labels={k: str(k) for k in range(-1, 7)})
        idots = VGroup(*[Dot([3.4 + 0.72 * k, RY - 0.2, 0], radius=0.1, color=FG) for k in range(-3, 4)])
        ilabs = VGroup(*[math(str(k), size=30, color=MUTED).next_to(d, DOWN, 0.2)
                         for k, d in zip(range(-3, 4), idots)])
        usual_l = text("usual + and x", size=26, color=MUTED).next_to(left.box, DOWN, 0.15)
        usual_r = usual_l.copy().next_to(right.box, DOWN, 0.15)
        with self.voiceover(text=N("s02.b2")) as tr:
            wait_until(self, tr, "reals")
            self.play(Create(left.box), FadeIn(left.label), Create(rl), FadeIn(usual_l), run_time=1.0)
            wait_until(self, tr, "ints")
            self.play(Create(right.box), FadeIn(right.label), FadeIn(idots), FadeIn(ilabs), FadeIn(usual_r),
                      run_time=1.0)
            rest(self, tr)

        sent = math(r"\forall x\ \exists y\ \ (y + y = x)", size=54).move_to([0, 1.95, 0])
        trans = text("every number has a half", size=34, color=PRIMARY).next_to(sent, DOWN, 0.25)
        key = VGroup(*[VGroup(math(s, size=36, color=PRIMARY), text(w, size=28, color=MUTED)).arrange(RIGHT, buff=0.12)
                       for s, w in [(r"\forall", "for every"), (r"\exists", "there exists"), (r"\land", "and"),
                                    (r"\lor", "or"), (r"\lnot", "not")]]).arrange(RIGHT, buff=0.5)
        key.move_to([0, -3.65, 0])
        with self.voiceover(text=N("s02.b3")) as tr:
            self.play(FadeOut(usual_l), FadeOut(usual_r), FadeIn(key), run_time=0.8)
            self.play(Write(sent), run_time=1.4)
            wait_until(self, tr, "half")
            self.play(FadeIn(trans, shift=UP * 0.15), run_time=0.6)
            rest(self, tr)

        half_r = math(r"3 = 1.5 + 1.5", size=32, color=GOOD).move_to([-3.4, RY + 0.85, 0])
        ok_l = tick(at=left.box.get_corner(UR) + LEFT * 0.45 + DOWN * 0.4, s=1.4)
        three = idots[6].copy().set_color(PRIMARY).scale(1.6)
        tries = math(r"1+1=2,\ \ 2+2=4", size=32, color=BAD).move_to([3.4, RY + 0.85, 0])
        no_r = cross(right.box.get_corner(UR) + LEFT * 0.5 + DOWN * 0.45, s=0.22)
        with self.voiceover(text=N("s02.b4")) as tr:
            self.play(Indicate(left.box, color=FG, scale_factor=1.02), Indicate(right.box, color=FG, scale_factor=1.02),
                      run_time=1.2)
            wait_until(self, tr, "reals")
            self.play(FadeIn(half_r), Create(ok_l), run_time=0.7)
            wait_until(self, tr, "ints")
            self.play(FadeIn(three), run_time=0.4)
            self.play(Indicate(idots[4], color=BAD), Indicate(idots[5], color=BAD), FadeIn(tries), run_time=0.8)
            self.play(Create(no_r), run_time=0.4)
            rest(self, tr)

        syms_c = language_row(True).move_to(syms.get_center() + RIGHT * 0.3)
        new_c = syms_c[-1]
        c_r = VGroup(Dot(rl.p(5), radius=0.11, color=PRIMARY))
        c_r.add(math("c", size=34, color=PRIMARY).next_to(c_r[0], UP, 0.15))
        c_i = VGroup(Dot(idots[1].get_center(), radius=0.11, color=PRIMARY))
        c_i.add(math("c", size=34, color=PRIMARY).next_to(c_i[0], UP, 0.15))
        s2 = math(r"c > 1", size=60).move_to(sent)
        ok2 = tick(at=left.box.get_corner(UR) + LEFT * 0.45 + DOWN * 0.4, s=1.4)
        no2 = cross(right.box.get_corner(UR) + LEFT * 0.5 + DOWN * 0.45, s=0.22)
        with self.voiceover(text=N("s02.b5")) as tr:
            self.play(FadeOut(VGroup(half_r, ok_l, three, tries, no_r, trans)), FadeOut(sent), run_time=0.6)
            wait_until(self, tr, "c")
            self.play(syms.animate.move_to(VGroup(*syms_c[:-1]).get_center()), lang_lab.animate.shift(RIGHT * 0.6),
                      FadeIn(new_c, scale=1.5), run_time=0.7)
            self.play(FadeIn(c_r, shift=DOWN * 0.3), FadeIn(c_i, shift=DOWN * 0.3), run_time=0.7)
            self.play(Write(s2), run_time=0.7)
            wait_until(self, tr, "five")
            self.play(Create(ok2), Indicate(c_r, color=PRIMARY), run_time=0.6)
            self.play(Create(no2), run_time=0.4)
            rest(self, tr)

        stack = column([r"c > 1", r"c + c > 1 + 1", r"\forall x\ (x \times 0 = 0)", r"\exists y\ (y < c)"], size=52)
        stack.move_to([-3.2, -0.2, 0])
        one = region(4.4, 3.2, [3.6, -0.4, 0], "one model")
        oned = far_line(y=-0.6, left=1.6, right=5.6, n=3, unit=0.65)
        ticks = VGroup(*[tick(m, s=0.9) for m in stack[:-1]])
        with self.voiceover(text=N("s02.b6")) as tr:
            self.play(FadeOut(VGroup(left, right, rl, idots, ilabs, c_r, c_i, ok2, no2, key)),
                      ReplacementTransform(s2, stack[0]), run_time=0.8)
            self.play(LaggedStart(*[FadeIn(m) for m in stack[1:]], lag_ratio=0.3), run_time=1.0)
            self.play(Create(one.box), FadeIn(one.label), FadeIn(oned), run_time=0.8)
            wait_until(self, tr, "all")
            self.play(LaggedStart(*[Create(t) for t in ticks], lag_ratio=0.4), run_time=1.2)
            rest(self, tr)
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.6)


# ---------------------------------------------------------------------------
# s03 The theorem
# ---------------------------------------------------------------------------


class S03Theorem(VoiceoverScene):
    def construct(self):
        self.set_speech_service(get_speech_service())
        box = theorem_box(size=42).move_to(DOWN * 0.1)
        name = text("the compactness theorem", size=34, color=PRIMARY).next_to(box, UP, 0.35)
        cred = text("Godel, 1930 (countably many sentences);  Malcev, 1936 (any number)", size=28,
                    color=MUTED).next_to(box, DOWN, 0.35)
        with self.voiceover(text=N("s03.b1")) as tr:
            self.play(FadeIn(name), run_time=0.6)
            wait_until(self, tr, "thm")
            self.play(Create(box[0]), FadeIn(box[1]), run_time=1.2)
            self.play(FadeIn(cred), run_time=0.6)
            rest(self, tr)

        col = column([r"c > 1", r"c > 2", r"c > 3", r"c > 4", r"c > 5"], size=56).move_to([-4.8, 0.7, 0])
        foot = text("2 means 1 + 1, and so on", size=26, color=MUTED).next_to(col, DOWN, 0.3).align_to(col, LEFT)
        batch = VGroup(*col[:4])
        br = side_brace(batch)
        rl = RealLine(0, 7, length=7.4, y=1.6, x0=2.6, size=32)
        rl_lab = math(r"\mathbb{R}", size=40).next_to(rl.line, LEFT, 0.3)
        c_r = VGroup(Dot(rl.p(5), radius=0.11, color=PRIMARY))
        c_r.add(math("c", size=34, color=PRIMARY).next_to(c_r[0], UP, 0.15))
        fl = far_line(y=-1.7, left=-1.1, right=6.6, n=5, unit=0.85)
        fl_lab = text("some model", size=34, color=WEIRD).next_to(fl, UP, 0.25).align_to(fl, LEFT)
        with self.voiceover(text=N("s03.b2")) as tr:
            self.play(FadeOut(VGroup(box, name, cred)), run_time=0.5)
            drop_in(self, list(col), 1.5)
            self.play(FadeIn(foot), run_time=0.4)
            wait_until(self, tr, "batch")
            self.play(GrowFromCenter(br), Create(rl), FadeIn(rl_lab), run_time=0.8)
            self.play(FadeIn(c_r, shift=DOWN * 0.3), run_time=0.5)
            wait_until(self, tr, "some")
            self.play(FadeIn(fl, shift=LEFT), FadeIn(fl_lab), run_time=0.9)
            rest(self, tr)

        rng = np.random.default_rng(4)
        scatter = VGroup(*[Dot([rng.uniform(-0.6, 5.6), -2.4 + rng.uniform(-0.9, 0.9), 0], radius=0.07, color=WEIRD)
                           for _ in range(26)])
        qm = text("?", size=80, color=WEIRD, weight="BOLD").move_to([6.3, -2.4, 0])
        with self.voiceover(text=N("s03.b3")) as tr:
            wait_until(self, tr, "weird")
            body = VGroup(fl[0], fl.ticks, fl[2])
            self.play(ReplacementTransform(body, scatter), FadeIn(qm), run_time=1.2)
            rest(self, tr)
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.6)


# ---------------------------------------------------------------------------
# s04 Infinitesimals
# ---------------------------------------------------------------------------


def truths_scroll(width=7.0, height=4.2, center=ORIGIN, size=32):
    box = RoundedRectangle(width=width, height=height, corner_radius=0.2, color=MUTED, stroke_width=3)
    box.move_to(center)
    title = text("every sentence true in", size=size, color=MUTED)
    title = VGroup(title, math(r"\mathbb{R}", size=size + 8, color=MUTED)).arrange(RIGHT, buff=0.15)
    title.next_to(box, UP, 0.15)
    lines = VGroup(text("every number has a half", size=size),
                   text("x times y = y times x", size=size),
                   text("every positive number has a square root", size=size),
                   text("there is no largest number", size=size),
                   text("0 < 1", size=size),
                   text("...", size=size, color=MUTED))
    lines.arrange(DOWN, buff=0.2, aligned_edge=LEFT)
    lines.move_to(box).align_to(box, LEFT).shift(RIGHT * 0.3)
    if lines.width > width - 0.5:
        lines.scale_to_fit_width(width - 0.5).align_to(box, LEFT).shift(RIGHT * 0.25)
    g = VGroup(box, title, lines)
    g.box, g.title, g.lines = box, title, lines
    return g


class S04Infinitesimals(VoiceoverScene):
    def construct(self):
        self.set_speech_service(get_speech_service())
        sc = truths_scroll(center=[-2.7, 0.2, 0])
        with self.voiceover(text=N("s04.b1")) as tr:
            wait_until(self, tr, "all")
            self.play(Create(sc.box), FadeIn(sc.title), run_time=0.8)
            self.play(LaggedStart(*[FadeIn(l, shift=UP * 0.2) for l in sc.lines], lag_ratio=0.5),
                      run_time=rt(min(3.0, tr.get_remaining_duration() - 0.3)))
            rest(self, tr)

        col = column([r"c > 0", r"c < 1", r"c < \tfrac{1}{2}", r"c < \tfrac{1}{3}"], size=50, dots=False)
        more = column([r"c < \tfrac{1}{7}"], size=50, dots=False)
        vd1, vd2 = math(r"\vdots", size=40), math(r"\vdots", size=40)
        full = VGroup(*col, vd1, more[0], vd2).arrange(DOWN, buff=0.16, aligned_edge=LEFT)
        vd1.shift(RIGHT * 0.35)
        vd2.shift(RIGHT * 0.35)
        full.move_to([2.6, 0.4, 0])
        foot = text("c < 1/n means c + c + ... + c (n times) < 1", size=28, color=MUTED)
        foot.move_to([0, -3.3, 0])
        with self.voiceover(text=N("s04.b2")) as tr:
            wait_until(self, tr, "new")
            drop_in(self, list(full), rt(min(2.6, tr.get_remaining_duration() - 0.5)))
            self.play(FadeIn(foot), run_time=0.4)
            rest(self, tr)

        br = Brace(VGroup(*full[:6]), direction=RIGHT, color=PRIMARY, buff=0.2)
        br_l = Brace(sc.box, direction=LEFT, color=PRIMARY, buff=0.15)
        last = full[5]
        rl = RealLine(0, 1, length=4.0, y=-2.9, x0=4.6, size=32, labels={0: "0", 1: "1"})
        c8 = VGroup(Dot(rl.p(1 / 8), radius=0.11, color=PRIMARY))
        c8.add(math(r"c = \tfrac{1}{8}", size=40, color=PRIMARY).next_to(c8[0], UR, 0.12).shift(RIGHT * 0.3))
        rl_lab = math(r"\mathbb{R}", size=40).next_to(rl.line, LEFT, 0.3)
        oks = VGroup(*[tick(m, s=0.7) for m in full[:6] if m not in (vd1,)])
        with self.voiceover(text=N("s04.b3")) as tr:
            self.play(FadeOut(foot), GrowFromCenter(br), GrowFromCenter(br_l), run_time=0.7)
            wait_until(self, tr, "stops")
            self.play(Indicate(last, color=PRIMARY, scale_factor=1.25), run_time=0.7)
            wait_until(self, tr, "smaller")
            self.play(Create(rl), FadeIn(rl_lab), FadeIn(c8, shift=DOWN * 0.2), run_time=0.8)
            self.play(LaggedStart(*[Create(t) for t in oks], lag_ratio=0.2), run_time=1.0)
            rest(self, tr)

        # The new model.
        hl = RealLine(-1.5, 3.5, length=9.6, y=-0.2, x0=-0.9, size=32, color=WEIRD,
                      labels={k: str(k) for k in range(-1, 4)})
        hl_lab = VGroup(text("a model of everything true in", size=30, color=WEIRD),
                        math(r"\mathbb{R}", size=38, color=WEIRD)).arrange(RIGHT, buff=0.15)
        hl_lab.next_to(hl, UP, 1.2)
        cdot = Dot(hl.p(0.07), radius=0.1, color=PRIMARY)
        clab = math("c", size=36, color=PRIMARY).next_to(cdot, UP, 0.18)
        tags = VGroup(math(r"c > 0", size=36), math(r"c < \tfrac{1}{n}\ \text{for every } n", size=36))
        tags.arrange(RIGHT, buff=0.9).move_to([0, -2.1, 0])
        inf = text("an infinitesimal", size=40, color=PRIMARY, weight="BOLD").move_to([0, -3.1, 0])
        with self.voiceover(text=N("s04.b4")) as tr:
            self.play(FadeOut(VGroup(sc, full, br, br_l, rl, rl_lab, c8, oks)), run_time=0.6)
            self.play(Create(hl), FadeIn(hl_lab), run_time=1.0)
            wait_until(self, tr, "c")
            self.play(FadeIn(cdot, scale=2), FadeIn(clab), FadeIn(tags), run_time=0.8)
            wait_until(self, tr, "inf")
            self.play(FadeIn(inf, scale=1.2), run_time=0.6)
            rest(self, tr)

        cards = VGroup(text("Leibniz, 1680s: infinitesimals", size=34),
                       text("Berkeley, 1734, attacking calculus: \"ghosts of departed quantities\"", size=26,
                            color=MUTED),
                       text("Robinson, 1960s: they're consistent", size=34, color=GOOD)).arrange(DOWN, buff=0.4)
        cards.move_to(UP * 2.3)
        with self.voiceover(text=N("s04.b5")) as tr:
            self.play(FadeOut(hl_lab), FadeOut(tags), FadeOut(inf), FadeIn(cards[0]), run_time=0.7)
            wait_until(self, tr, "ghosts")
            self.play(FadeIn(cards[1]), run_time=0.6)
            self.wait(rt(tr.get_remaining_duration() * 0.4))
            self.play(FadeIn(cards[2]), run_time=0.6)
            rest(self, tr)

        # Zoom on zero: an inset with the cloud.
        lens = Circle(radius=0.35, color=PRIMARY, stroke_width=3).move_to(hl.p(0))
        inset = RoundedRectangle(width=9.0, height=2.4, corner_radius=0.2, color=PRIMARY, stroke_width=3)
        inset.move_to([0, 2.2, 0])
        zl = Line(inset.get_left() + RIGHT * 0.4, inset.get_right() + LEFT * 0.4, color=WEIRD, stroke_width=4)
        zl.shift(DOWN * 0.3)
        z0 = zl.get_left() + RIGHT * 1.0
        zero = VGroup(Line(z0 + UP * 0.12, z0 + DOWN * 0.12, color=WEIRD, stroke_width=3),
                      math("0", size=28, color=MUTED).next_to(z0, DOWN, 0.2))
        cloud = hyper_cloud(z0, scale=1.0)
        conn = VGroup(Line(lens.get_top(), inset.get_bottom() + LEFT * 4.5, color=PRIMARY, stroke_width=2),
                      Line(lens.get_top(), inset.get_bottom() + RIGHT * 4.5, color=PRIMARY, stroke_width=2))
        note = math(r"c < \tfrac{1}{2n}\ \Rightarrow\ 2c < \tfrac{1}{n}", size=34)
        note.move_to(inset.get_top() + DOWN * 0.42 + RIGHT * 2.0)
        brk = math(r"\cdots", size=36, color=MUTED).move_to(hl.p(3.5) + RIGHT * 0.4 + UP * 0.12)
        recip = VGroup(Dot(hl.p(3.5) + RIGHT * 1.2, radius=0.11, color=PRIMARY))
        recip.add(math(r"\tfrac{1}{c}", size=42, color=PRIMARY).next_to(recip[0], UP, 0.18))
        with self.voiceover(text=N("s04.b6")) as tr:
            self.play(FadeOut(cards), run_time=0.5)
            wait_until(self, tr, "cloud")
            self.play(Create(lens), run_time=0.4)
            self.play(Create(conn), Create(inset), Create(zl), FadeIn(zero), run_time=0.8)
            self.play(LaggedStart(*[FadeIn(p, scale=1.5) for p in cloud], lag_ratio=0.3), run_time=1.2)
            wait_until(self, tr, "still")
            self.play(FadeIn(note), Indicate(cloud[3], color=PRIMARY), run_time=0.7)
            wait_until(self, tr, "big")
            self.play(FadeIn(brk), FadeIn(recip, shift=LEFT * 0.5), run_time=0.8)
            rest(self, tr)

        card1 = VGroup(text("every number is below some whole number", size=32)).move_to([0, -2.2, 0])
        card2 = VGroup(text("every set that's bounded above has a least upper bound", size=32)).move_to([0, -3.1, 0])
        q1 = text("?", size=48, color=BAD, weight="BOLD").next_to(recip, RIGHT, 0.15)
        zbrk = math(r"\cdots", size=34, color=MUTED).move_to(z0 + RIGHT * 4.6 + UP * 0.12)
        s_pt = z0 + RIGHT * 6.9
        sdot = VGroup(Dot(s_pt, radius=0.1, color=SECONDARY), math("s", size=36, color=SECONDARY).next_to(s_pt, UP, 0.18))
        s2_pt = z0 + RIGHT * 5.6
        s2dot = VGroup(Dot(s2_pt, radius=0.1, color=SECONDARY),
                       math(r"\tfrac{s}{2}", size=36, color=SECONDARY).next_to(s2_pt, UP, 0.18))
        sfoot = text("s isn't infinitesimal, so s/2 isn't either", size=26, color=MUTED)
        sfoot.move_to(inset.get_top() + DOWN * 0.4)
        w1 = Underline(card1[0][-11:], color=PRIMARY)
        w2 = Underline(card2[0][5:8], color=PRIMARY)
        with self.voiceover(text=N("s04.b7")) as tr:
            self.play(FadeOut(note), run_time=0.4)
            wait_until(self, tr, "below")
            self.play(FadeIn(card1), FadeIn(q1), recip.animate.set_color(BAD), run_time=0.7)
            wait_until(self, tr, "lub")
            self.play(FadeIn(card2), run_time=0.6)
            self.play(FadeIn(zbrk), FadeIn(sdot), run_time=0.5)
            wait_until(self, tr, "half")
            self.play(TransformFromCopy(sdot, s2dot), FadeIn(sfoot), run_time=0.7)
            wait_until(self, tr, "set")
            self.play(Create(w1), Create(w2), run_time=0.6)
            self.wait(rt(tr.get_remaining_duration() - 1.2))
            st = VGroup(strike(card1[0]), strike(card2[0]))
            self.play(Create(st), run_time=0.6)
            self.play(FadeOut(VGroup(card1, card2, w1, w2, q1, st)), run_time=0.5)
            rest(self, tr)
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.6)


# ---------------------------------------------------------------------------
# s05 Coloring the plane
# ---------------------------------------------------------------------------


U5 = 1.6  # screen units per unit of distance in the plane scenes
HEX_SIDE = 0.45


def labelled(mob, s, direction=UP, size=34, color=FG, buff=0.15):
    lab = math(s, size=size, color=color).next_to(mob, direction, buff)
    lab.add_background_rectangle(color=BG, opacity=0.85, buff=0.06)
    return lab


def dirv(a):
    return np.array([cos(a), sin(a), 0])


class S05Plane(VoiceoverScene):
    def construct(self):
        self.set_speech_service(get_speech_service())
        rng = np.random.default_rng(7)
        bg_pts = VGroup(*[Dot([rng.uniform(-6.6, 6.6), rng.uniform(-3.6, 3.6), 0], radius=0.05, color=MUTED)
                          for _ in range(70)])
        specs = [((-4.6, 1.4), 0.35, (BAD, SECONDARY)), ((0.6, 1.9), 2.4, (PRIMARY, GOOD)),
                 ((-2.4, -1.9), -0.5, (SECONDARY, PRIMARY)), ((3.4, -1.2), 1.2, (GOOD, BAD))]
        pairs = VGroup()
        for (x, y), ang, (c1, c2) in specs:
            a = np.array([x, y, 0])
            b = a + U5 * dirv(ang)
            pairs.add(VGroup(edge(a, b, color=FG, width=4), vdot(a, c1, 0.13), vdot(b, c2, 0.13)))
        one = labelled(pairs[0][0], "1", direction=UP, size=36)
        with self.voiceover(text=N("s05.b1")) as tr:
            self.play(LaggedStart(*[FadeIn(d) for d in bg_pts], lag_ratio=0.02), run_time=1.2)
            wait_until(self, tr, "one")
            self.play(Create(pairs[0][0]), FadeIn(pairs[0][1:]), FadeIn(one), run_time=0.8)
            self.play(LaggedStart(*[FadeIn(p) for p in pairs[1:]], lag_ratio=0.4), run_time=1.4)
            rest(self, tr)

        tiling = hex_tiling(unit=U5, side=HEX_SIDE, radius=7.6)
        h0, h1 = tiling.cells[(0, 0)], tiling.cells[(1, 2)]
        s = HEX_SIDE * U5
        c0, c1 = h0.get_center(), h1.get_center()
        across = edge(c0 + UP * s, c0 + DOWN * s, color=FG, width=5)
        lt1 = labelled(across, "< 1", direction=LEFT, size=44)
        d = (c1 - c0) / np.linalg.norm(c1 - c0)
        gap = edge(c0 + d * s * 0.92, c1 - d * s * 0.92, color=FG, width=5)
        gt1 = labelled(gap, "> 1", direction=RIGHT, size=44)
        foot = text("each border point goes to just one of its hexagons", size=30, color=FG)
        foot.add_background_rectangle(color=BG, opacity=0.85, buff=0.1)
        foot.move_to([0, -3.55, 0])
        seven = text("7 colors", size=64, color=PRIMARY, weight="BOLD")
        with self.voiceover(text=N("s05.b2")) as tr:
            self.play(FadeOut(VGroup(bg_pts, pairs, one)), FadeIn(seven), run_time=0.6)
            wait_until(self, tr, "hex")
            self.play(FadeOut(seven), run_time=0.3)
            self.play(LaggedStart(*[FadeIn(h, scale=0.6) for h in tiling], lag_ratio=0.01), run_time=1.6)
            wait_until(self, tr, "same")
            self.play(h0.animate.set_stroke(FG, width=5), Create(across), FadeIn(lt1), run_time=0.7)
            wait_until(self, tr, "far")
            self.play(h1.animate.set_stroke(FG, width=5), Create(gap), FadeIn(gt1), run_time=0.7)
            self.play(FadeIn(foot), run_time=0.4)
            rest(self, tr)

        US = 2.1
        tb = np.array([-1.05, -1.6, 0])
        tri_p = [tb, tb + US * RIGHT, tb + US * dirv(PI / 3)]
        tri = VGroup(*[edge(tri_p[i], tri_p[(i + 1) % 3], color=MUTED) for i in range(3)])
        tri_d = VGroup(*[vdot(p, c, 0.15) for p, c in zip(tri_p, [BAD, SECONDARY, PRIMARY])])
        with self.voiceover(text=N("s05.b3")) as tr:
            self.play(FadeOut(VGroup(tiling, across, lt1, gap, gt1, foot)), run_time=0.6)
            wait_until(self, tr, "tri")
            self.play(Create(tri), FadeIn(tri_d[0]), run_time=0.7)
            self.play(LaggedStart(*[FadeIn(x, scale=1.5) for x in tri_d[1:]], lag_ratio=0.4), run_time=0.8)
            rest(self, tr)

        A = np.array([0, -3.3, 0])
        def diamond(theta, cols=(BAD, SECONDARY, PRIMARY, MUTED)):
            Bp, Cp, Dp = A + US * dirv(theta - PI / 6), A + US * dirv(theta + PI / 6), A + US * sqrt(3) * dirv(theta)
            es = VGroup(edge(A, Bp), edge(A, Cp), edge(Bp, Cp), edge(Bp, Dp), edge(Cp, Dp))
            ds = VGroup(vdot(A, cols[0], 0.15), vdot(Bp, cols[1], 0.15), vdot(Cp, cols[2], 0.15), vdot(Dp, cols[3], 0.15))
            return VGroup(es, ds)
        dm = diamond(PI / 2)
        with self.voiceover(text=N("s05.b4")) as tr:
            wait_until(self, tr, "diamond")
            self.play(ReplacementTransform(tri, VGroup(*dm[0][:3])), ReplacementTransform(tri_d, VGroup(*dm[1][:3])),
                      run_time=0.8)
            self.play(Create(VGroup(*dm[0][3:])), FadeIn(dm[1][3]), run_time=0.7)
            wait_until(self, tr, "match")
            self.play(dm[1][3].animate.set_color(BAD).scale(1.3), run_time=0.5)
            self.play(dm[1][3].animate.scale(1 / 1.3), run_time=0.3)
            rest(self, tr)

        dm2 = dm.copy()
        half = SPINDLE_PHI / 2
        D1 = A + US * sqrt(3) * dirv(PI / 2 + half)
        D2 = A + US * sqrt(3) * dirv(PI / 2 - half)
        top = edge(D1, D2, color=FG, width=6)
        name = VGroup(text("Moser spindle, 1961", size=40, color=PRIMARY),
                      text("7 points, 4 colors", size=34, color=MUTED)).arrange(DOWN, buff=0.15)
        name.move_to([4.6, 1.2, 0])
        with self.voiceover(text=N("s05.b5")) as tr:
            wait_until(self, tr, "second")
            self.add(dm2)
            self.play(Rotate(dm, half, about_point=A), Rotate(dm2, -half, about_point=A),
                      run_time=rt(max(0.8, tr.time_until_bookmark("apart") - 0.1)))
            wait_until(self, tr, "apart")
            self.play(Create(top), run_time=0.5)
            wait_until(self, tr, "clash")
            self.play(top.animate.set_color(BAD), Indicate(dm[1][3], color=BAD, scale_factor=1.6),
                      Indicate(dm2[1][3], color=BAD, scale_factor=1.6), run_time=0.8)
            self.play(FadeIn(name), run_time=0.6)
            rest(self, tr)

        bl = bounds_line(1, 8, y=-0.6, length=10, marks=(4, 7), shade=(4, 7), size=40)
        qm = text("?", size=72, color=PRIMARY, weight="BOLD").next_to(bl.shade, UP, 0.4)
        yrs = text("1950 to 2018", size=34, color=MUTED).next_to(bl, DOWN, 0.6)
        with self.voiceover(text=N("s05.b6")) as tr:
            self.play(FadeOut(VGroup(dm, dm2, top, name)), run_time=0.5)
            self.play(Create(bl.rl), run_time=0.7)
            wait_until(self, tr, "range")
            self.play(FadeIn(bl.marks, scale=1.5), FadeIn(bl.shade), FadeIn(qm), FadeIn(yrs), run_time=0.8)
            rest(self, tr)

        # The coloring problem as sentences.
        rng = np.random.default_rng(11)
        P = np.array([-4.2, 0.2, 0])
        Q = P + U5 * dirv(0.4)
        R = np.array([-5.2, -1.8, 0])
        extra = [np.array([rng.uniform(-6.4, -1.4), rng.uniform(-3.0, 2.6), 0]) for _ in range(14)]
        extra = [e for e in extra if min(np.linalg.norm(e - z) for z in (P, Q, R)) > 0.6]
        pdots = VGroup(vdot(P, FG, 0.12), vdot(Q, FG, 0.12), vdot(R, FG, 0.12))
        plabs = VGroup(*[math(n, size=40).next_to(d, UL, 0.05) for n, d in zip("pqr", pdots)])
        edots = VGroup(*[vdot(e, FG, 0.09) for e in extra])
        pq = edge(P, Q, color=FG, width=4)
        sents = VGroup(text("p is red or blue or gold or green", size=36),
                       text("p is only one color", size=36),
                       text("p and q have different colors", size=36)).arrange(DOWN, buff=0.45, aligned_edge=LEFT)
        sents.move_to([2.9, 0.3, 0])
        lang = text("new language: a name for every point, a word for each color", size=30, color=MUTED)
        lang.move_to([0, 3.2, 0])
        brs = Brace(sents, direction=LEFT, color=PRIMARY, buff=0.2)
        with self.voiceover(text=N("s05.b7")) as tr:
            self.play(FadeOut(VGroup(bl, qm, yrs)), run_time=0.5)
            self.play(FadeIn(edots), FadeIn(pdots), FadeIn(plabs), FadeIn(lang), run_time=0.8)
            self.play(FadeIn(sents[0]), run_time=0.5)
            self.play(FadeIn(sents[1]), run_time=0.5)
            self.play(Create(pq), FadeIn(sents[2]), run_time=0.6)
            wait_until(self, tr, "finite")
            self.play(GrowFromCenter(brs), edots.animate.set_opacity(0.2), pdots[2].animate.set_opacity(0.2),
                      plabs[2].animate.set_opacity(0.2), run_time=0.8)
            rest(self, tr)

        l1 = VGroup(text("every finite set of points 4-colorable", size=36), math(r"\Rightarrow", size=44),
                    text("the plane is 4-colorable", size=36)).arrange(RIGHT, buff=0.3)
        l2 = VGroup(text("the plane needs 5", size=36), math(r"\Rightarrow", size=44),
                    text("some finite set of points needs 5", size=36, color=PRIMARY)).arrange(RIGHT, buff=0.3)
        l1.move_to(UP * 0.8)
        l2.move_to(DOWN * 0.6)
        with self.voiceover(text=N("s05.b8")) as tr:
            self.play(FadeOut(VGroup(edots, pdots, plabs, pq, sents, brs, lang)), run_time=0.5)
            self.play(FadeIn(l1[0]), run_time=0.5)
            wait_until(self, tr, "whole")
            self.play(FadeIn(l1[1:]), run_time=0.6)
            wait_until(self, tr, "some")
            self.play(FadeIn(l2, shift=DOWN * 0.2), run_time=0.7)
            self.play(Indicate(l2[2], color=PRIMARY, scale_factor=1.08), run_time=0.7)
            rest(self, tr)

        big = unit_graph(unit=0.52, center=[-3.2, 0.5, 0], rad=4.3, rots=(0.0, SPINDLE_PHI, 2 * SPINDLE_PHI))
        big_lab = text("de Grey, 2018: 1581 points", size=34, color=PRIMARY).next_to(big, UP, 0.2)
        small = unit_graph(unit=0.52, center=[3.4, 0.5, 0], rad=3.0, rots=(0.0, SPINDLE_PHI))
        small_lab = text("2020: 509 points", size=34, color=PRIMARY).next_to(small, UP, 0.2).align_to(big_lab, UP)
        illu = text("(sketches, not the real graphs)", size=24, color=MUTED).move_to([0, -2.3, 0])
        bl2 = bounds_line(1, 8, y=-3.1, length=8, marks=(5, 7), shade=(5, 7), size=34)
        with self.voiceover(text=N("s05.b9")) as tr:
            self.play(FadeOut(VGroup(l1, l2)), run_time=0.4)
            wait_until(self, tr, "grey")
            self.play(FadeIn(big[1]), Create(big[0]), FadeIn(big_lab), FadeIn(illu), run_time=1.4)
            wait_until(self, tr, "parts")
            self.play(TransformFromCopy(big, small), FadeIn(small_lab), run_time=1.0)
            self.play(FadeIn(bl2), run_time=0.6)
            rest(self, tr)
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.6)


# ---------------------------------------------------------------------------
# s06 Why it's true
# ---------------------------------------------------------------------------


VOTE = {"<": GOOD, ">": BAD, "=": MUTED}


def seq_row(entries, y, x0=-3.2, dx=1.15, size=40, color=FG, label=None, dots=True):
    cells = VGroup(*[math(e, size=size, color=color).move_to([x0 + i * dx, y, 0]) for i, e in enumerate(entries)])
    g = VGroup(cells)
    g.cells = cells
    if dots:
        g.add(math(r"\cdots", size=size, color=color).move_to([x0 + len(entries) * dx, y, 0]))
    if label:
        g.lab = math(label, size=size + 4, color=color).move_to([x0 - 1.6, y, 0])
        g.add(g.lab)
    return g


def vote_row(votes, y, x0=-3.2, dx=1.15, size=44):
    return VGroup(*[math(v, size=size, color=VOTE[v]).move_to([x0 + i * dx, y, 0]) for i, v in enumerate(votes)])


def index_row(n, y, x0=-3.2, dx=1.15):
    return VGroup(*[text(str(i + 1), size=26, color=MUTED).move_to([x0 + i * dx, y, 0]) for i in range(n)])


def rules_card(width=10.5):
    title = text("ultrafilter: which sets of positions count as \"most\"", size=34, color=PRIMARY)
    rules = VGroup(text("1.  a set or the rest counts, never both", size=32),
                   text("2.  if two sets count, so does their overlap", size=32),
                   text("3.  finite sets never count", size=32)).arrange(DOWN, buff=0.3, aligned_edge=LEFT)
    g = VGroup(title, rules).arrange(DOWN, buff=0.45)
    box = SurroundingRectangle(g, color=PRIMARY, buff=0.35, corner_radius=0.15)
    out = VGroup(box, g)
    out.title, out.rules, out.box = title, rules, box
    return out


def los_card(size=32):
    t = VGroup(text("Los's theorem (Jerzy Los, 1955):", size=size, color=PRIMARY),
               text("a sentence is true in the glued world exactly when", size=size),
               text("the positions where it's true count as most", size=size)).arrange(DOWN, buff=0.18)
    box = SurroundingRectangle(t, color=PRIMARY, buff=0.3, corner_radius=0.15)
    return VGroup(box, t)


class S06Proof(VoiceoverScene):
    def construct(self):
        self.set_speech_service(get_speech_service())
        ys = [3.0, 2.15, 1.3, 0.45, -0.4]
        X0, L = -2.0, 5.6
        copies = VGroup()
        cdots = VGroup()
        for n, y in enumerate(ys, start=1):
            rl = RealLine(0, 1, length=L, y=y, x0=X0, size=28, labels={0: "0", 1: "1"})
            rl.labels.set_opacity(0 if n > 1 else 1)
            lab = text(f"copy {n}", size=28, color=MUTED).move_to([X0 - L / 2 - 1.0, y, 0])
            cd = Dot(rl.p(1 / n), radius=0.1, color=PRIMARY)
            ct = math(r"c = " + ("1" if n == 1 else r"\tfrac{1}{%d}" % n), size=38, color=PRIMARY)
            ct.move_to([X0 + L / 2 + 1.1, y, 0])
            copies.add(VGroup(rl, lab, ct))
            cdots.add(cd)
        vd = math(r"\vdots", size=40, color=MUTED).move_to([X0 - L / 2 - 1.0, -1.05, 0])
        why = text("why is it true?", size=56, color=PRIMARY, weight="BOLD")
        with self.voiceover(text=N("s06.b1")) as tr:
            self.play(FadeIn(why), run_time=0.6)
            wait_until(self, tr, "copies")
            self.play(FadeOut(why), run_time=0.3)
            self.play(LaggedStart(*[FadeIn(c, shift=DOWN * 0.2) for c in copies], lag_ratio=0.25), FadeIn(vd),
                      run_time=1.6)
            self.play(LaggedStart(*[FadeIn(d, scale=1.6) for d in cdots], lag_ratio=0.2), run_time=1.0)
            rest(self, tr)

        rng = np.random.default_rng(5)
        avals = [0.62, 0.35, 0.8, 0.15, 0.5]
        adots = VGroup(*[Dot(copies[i][0].p(v), radius=0.1, color=SECONDARY) for i, v in enumerate(avals)])
        arow = math(r"a = (a_1,\ a_2,\ a_3,\ a_4,\ a_5,\ \dots)", size=40, color=SECONDARY).move_to([-0.6, -1.9, 0])
        crow = math(r"c = \left(1,\ \tfrac{1}{2},\ \tfrac{1}{3},\ \tfrac{1}{4},\ \tfrac{1}{5},\ \dots\right)", size=40,
                    color=PRIMARY).move_to([-0.6, -2.8, 0])
        sumrow = math(r"a + c = \left(a_1 + 1,\ a_2 + \tfrac{1}{2},\ a_3 + \tfrac{1}{3},\ \dots\right)", size=36)
        sumrow.move_to([-0.6, -3.62, 0])
        with self.voiceover(text=N("s06.b2")) as tr:
            wait_until(self, tr, "seq")
            self.play(LaggedStart(*[FadeIn(d, scale=1.5) for d in adots], lag_ratio=0.2), run_time=0.8)
            self.play(FadeIn(arow, shift=DOWN * 0.2), run_time=0.8)
            wait_until(self, tr, "cseq")
            self.play(*[Indicate(d, color=PRIMARY) for d in cdots], FadeIn(crow), run_time=0.9)
            self.wait(rt(tr.get_remaining_duration() * 0.3))
            self.play(FadeIn(sumrow), run_time=0.6)
            rest(self, tr)

        # Voting.
        idx = index_row(8, 2.2)
        a_e = ["1", "4", "0", "2", "3", "2", "0", "2"]
        b_e = ["2", "3", "1", "5", "4", "2", "1", "3"]
        ra = seq_row(a_e, 1.3, label="a", color=SECONDARY)
        rb = seq_row(b_e, 0.3, label="b", color=FG)
        votes = vote_row(["<", ">", "<", "<", "<", "=", "<", "<"], -0.75)
        vlab = text("votes", size=28, color=MUTED).move_to([-4.8, -0.75, 0])
        verdict = math(r"\text{most say } <\ \ \Rightarrow\ \ a < b", size=42).move_to([0, -2.0, 0])
        most_q = text("what does \"most\" mean?", size=40, color=PRIMARY).move_to([0, -3.1, 0])
        with self.voiceover(text=N("s06.b3")) as tr:
            self.play(FadeOut(VGroup(copies, cdots, adots, vd, arow, crow, sumrow)), run_time=0.5)
            wait_until(self, tr, "vote")
            self.play(FadeIn(idx), FadeIn(ra), FadeIn(rb), run_time=0.7)
            self.play(LaggedStart(*[FadeIn(v, shift=DOWN * 0.2) for v in votes], lag_ratio=0.15), FadeIn(vlab),
                      run_time=1.2)
            self.play(FadeIn(verdict), run_time=0.6)
            self.wait(rt(tr.get_remaining_duration() - 0.8))
            self.play(FadeIn(most_q), run_time=0.5)
            rest(self, tr)

        c_e = ["1", r"\tfrac{1}{2}", r"\tfrac{1}{3}", r"\tfrac{1}{4}", r"\tfrac{1}{5}", r"\tfrac{1}{6}",
               r"\tfrac{1}{7}", r"\tfrac{1}{8}"]
        rc = seq_row(c_e, 1.3, label="c", color=PRIMARY)
        r5 = seq_row([r"\tfrac{1}{5}"] * 8, 0.3, label=r"\tfrac{1}{5}", color=FG)
        v5 = vote_row([">", ">", ">", ">", "=", "<", "<", "<"], -0.75)
        fin = Brace(VGroup(*v5[:5]), direction=DOWN, color=MUTED, buff=0.15)
        fin_t = text("finitely many", size=28, color=MUTED).next_to(fin, DOWN, 0.1)
        cof = text("all but finitely many say <", size=34, color=GOOD).move_to([0, -2.5, 0])
        ralt = seq_row(["1", "-1", "1", "-1", "1", "-1", "1", "-1"], 1.3, label="x", color=SECONDARY)
        r0 = seq_row(["0"] * 8, 0.3, label="0", color=FG)
        valt = vote_row([">", "<", ">", "<", ">", "<", ">", "<"], -0.75)
        tie = text("neither side wins", size=36, color=BAD).move_to([0, -2.1, 0])
        tri = VGroup(text("in", size=30, color=MUTED), math(r"\mathbb{R}", size=36, color=MUTED),
                     text(": positive, negative or zero", size=30, color=MUTED)).arrange(RIGHT, buff=0.12)
        tri.move_to([0, -3.0, 0])
        with self.voiceover(text=N("s06.b4")) as tr:
            self.play(FadeOut(VGroup(ra, rb, votes, vlab, verdict, most_q)), run_time=0.5)
            self.play(FadeIn(rc), FadeIn(r5), run_time=0.6)
            wait_until(self, tr, "cless")
            self.play(LaggedStart(*[FadeIn(v, shift=DOWN * 0.2) for v in v5], lag_ratio=0.12), run_time=1.0)
            self.play(GrowFromCenter(fin), FadeIn(fin_t), FadeIn(cof), run_time=0.6)
            wait_until(self, tr, "alt")
            self.play(FadeOut(VGroup(rc, r5, v5, fin, fin_t, cof)), FadeIn(ralt), FadeIn(r0), run_time=0.6)
            self.play(LaggedStart(*[FadeIn(v, shift=DOWN * 0.2) for v in valt], lag_ratio=0.12), run_time=1.0)
            self.play(FadeIn(tie), run_time=0.4)
            self.wait(rt(tr.get_remaining_duration() * 0.3))
            self.play(FadeIn(tri), run_time=0.5)
            rest(self, tr)

        card = rules_card().move_to(UP * 0.2)
        with self.voiceover(text=N("s06.b5")) as tr:
            self.play(FadeOut(VGroup(idx, ralt, r0, valt, tie, tri)), run_time=0.5)
            self.play(Create(card.box), run_time=0.6)
            wait_until(self, tr, "uf")
            self.play(FadeIn(card.title), run_time=0.6)
            for k, m in enumerate(["r1", "r2", "r3"]):
                wait_until(self, tr, m)
                self.play(FadeIn(card.rules[k], shift=RIGHT * 0.2), run_time=0.5)
            rest(self, tr)

        strips = VGroup(*[Rectangle(width=6.0, height=0.9, color=c, fill_opacity=0.3, stroke_width=3).move_to(p)
                          for c, p in [(SECONDARY, [-1.2, 1.0, 0]), (PRIMARY, [0.6, 0.6, 0]), (GOOD, [-0.2, 0.2, 0])]])
        grow = text("any sets that always overlap grow into an ultrafilter", size=34).move_to([0, -1.2, 0])
        choice = text("uses the axiom of choice", size=26, color=MUTED).next_to(grow, DOWN, 0.25)
        pos = VGroup(*[Circle(radius=0.32, color=SECONDARY if i % 2 == 0 else PRIMARY, fill_opacity=0.35,
                              stroke_width=3).move_to([-4.0 + i * 1.15, 1.2, 0]) for i in range(8)])
        nums = VGroup(*[text(str(i + 1), size=28).move_to(p) for i, p in enumerate(pos)])
        teams = VGroup(text("odd positions", size=32, color=SECONDARY), text("even positions", size=32, color=PRIMARY))
        teams.arrange(RIGHT, buff=2.0).move_to([0, 0.1, 0])
        curtain = VGroup(Rectangle(width=3.6, height=1.0, color=MUTED, fill_color=MUTED, fill_opacity=0.9))
        curtain.add(text("winner: ?", size=32, color=BG, weight="BOLD")).move_to([0, -1.3, 0])
        with self.voiceover(text=N("s06.b6")) as tr:
            self.play(card.animate.scale(0.55).to_corner(UR, buff=0.3), run_time=0.7)
            self.play(LaggedStart(*[FadeIn(s) for s in strips], lag_ratio=0.3), run_time=0.9)
            wait_until(self, tr, "grow")
            self.play(FadeOut(strips, scale=0.4, target_position=card.get_center()), FadeIn(grow), FadeIn(choice),
                      run_time=0.9)
            self.play(Indicate(card, color=PRIMARY, scale_factor=1.05), run_time=0.6)
            self.wait(rt(tr.time_until_bookmark("hidden") - 2.4))
            self.play(FadeOut(grow), FadeOut(choice), FadeIn(pos), FadeIn(nums), run_time=0.6)
            self.play(FadeIn(teams), run_time=0.5)
            wait_until(self, tr, "hidden")
            self.play(FadeIn(curtain, shift=DOWN * 0.3), run_time=0.6)
            rest(self, tr)

        lc = los_card().move_to(UP * 0.6)
        arrows = VGroup(math(r"\text{and} \rightarrow \text{overlap rule}", size=34),
                        math(r"\text{not} \rightarrow \text{either-or rule}", size=34)).arrange(RIGHT, buff=1.2)
        arrows.next_to(lc, DOWN, 0.6)
        with self.voiceover(text=N("s06.b7")) as tr:
            self.play(FadeOut(VGroup(pos, nums, teams, curtain)), run_time=0.5)
            wait_until(self, tr, "los")
            self.play(Create(lc[0]), FadeIn(lc[1]), run_time=1.0)
            self.wait(rt(tr.get_remaining_duration() * 0.35))
            self.play(FadeIn(arrows[0]), run_time=0.5)
            self.wait(rt(tr.get_remaining_duration() * 0.4))
            self.play(FadeIn(arrows[1]), run_time=0.5)
            rest(self, tr)

        # Every copy votes on two sentences.
        rows = VGroup()
        for n in range(1, 9):
            rows.add(text(f"copy {n}", size=28, color=MUTED).move_to([-4.6, 2.5 - (n - 1) * 0.6, 0]))
        rvd = math(r"\vdots", size=34, color=MUTED).move_to([-4.6, 2.5 - 8 * 0.6 + 0.1, 0])
        h1 = VGroup(text("true facts about", size=28), math(r"\mathbb{R}", size=32)).arrange(RIGHT, buff=0.1)
        h1.move_to([-2.3, 3.25, 0])
        h2 = math(r"c < \tfrac{1}{5}", size=38).move_to([0.6, 3.25, 0])
        t1 = VGroup(*[tick(at=np.array([-2.3, r.get_y(), 0]), s=0.9) for r in rows])
        t2 = VGroup(*[(cross(np.array([0.6, r.get_y(), 0]), s=0.13) if n <= 5 else
                       tick(at=np.array([0.6, r.get_y(), 0]), s=0.9)) for n, r in enumerate(rows, start=1)])
        finb = Brace(VGroup(*t2[:5]), direction=RIGHT, color=MUTED, buff=0.3)
        fint = text("finite, so the rest counts", size=26, color=MUTED).next_to(finb, RIGHT, 0.15)
        gl = Line([1.4, -2.9, 0], [6.6, -2.9, 0], color=WEIRD, stroke_width=4)
        g0 = Dot([2.2, -2.9, 0], radius=0.07, color=WEIRD)
        g0l = math("0", size=26, color=MUTED).next_to(g0, DOWN, 0.15)
        gcl = hyper_cloud(np.array([2.2, -2.9, 0]), scale=0.8)
        hyper = text("the hyperreal numbers", size=38, color=WEIRD).move_to([4.0, -1.5, 0])
        with self.voiceover(text=N("s06.b8")) as tr:
            self.play(FadeOut(VGroup(lc, arrows)), card.animate.set_opacity(0), run_time=0.5)
            self.remove(card)
            self.play(FadeIn(rows), FadeIn(rvd), FadeIn(h1), run_time=0.6)
            self.play(LaggedStart(*[Create(t) for t in t1], lag_ratio=0.1), run_time=1.0)
            self.play(FadeIn(h2), run_time=0.4)
            wait_until(self, tr, "few")
            self.play(LaggedStart(*[Create(t) for t in t2], lag_ratio=0.1), run_time=1.0)
            self.play(GrowFromCenter(finb), FadeIn(fint), run_time=0.6)
            self.play(Create(gl), FadeIn(g0), FadeIn(g0l), FadeIn(gcl), run_time=0.8)
            wait_until(self, tr, "hyper")
            self.play(FadeIn(hyper), run_time=0.6)
            rest(self, tr)

        # General case: one model per finite batch.
        batches = [r"\{\varphi_1\}", r"\{\varphi_1, \varphi_2\}", r"\{\varphi_2, \varphi_7\}",
                   r"\{\varphi_1, \varphi_3, \varphi_4\}", r"\{\varphi_3\}", r"\{\varphi_1, \varphi_7\}",
                   r"\{\varphi_4, \varphi_5\}"]
        layers = VGroup()
        for k, b in enumerate(batches):
            y = 2.9 - k * 0.78
            box = RoundedRectangle(width=4.6, height=0.62, corner_radius=0.12, color=MUTED, stroke_width=2)
            box.move_to([-2.6, y, 0])
            lab = math(b, size=32).move_to(box)
            mlab = text(f"model {k + 1}", size=24, color=MUTED).next_to(box, LEFT, 0.2)
            layers.add(VGroup(box, lab, mlab))
        lvd = math(r"\vdots", size=34, color=MUTED).next_to(layers, DOWN, 0.1)
        has1 = [0, 1, 3, 5]
        lit1 = VGroup(*[layers[k][0] for k in has1])
        sets = VGroup(text("batches containing", size=34), math(r"\varphi_1", size=40, color=PRIMARY)).arrange(RIGHT, buff=0.12)
        sets3 = VGroup(text("batches containing", size=34), math(r"\varphi_3", size=40, color=SECONDARY)).arrange(RIGHT, buff=0.12)
        sets4 = VGroup(text("batches containing", size=34), math(r"\varphi_4", size=40, color=GOOD)).arrange(RIGHT, buff=0.12)
        sv = VGroup(sets, sets3, sets4).arrange(DOWN, buff=0.35, aligned_edge=LEFT).move_to([3.9, 1.8, 0])
        most = text("count as most", size=34, color=PRIMARY).next_to(sv, DOWN, 0.4).align_to(sv, LEFT)
        with self.voiceover(text=N("s06.b9")) as tr:
            self.play(FadeOut(VGroup(rows, rvd, h1, h2, t1, t2, finb, fint, gl, g0, g0l, gcl, hyper)), run_time=0.5)
            wait_until(self, tr, "layers")
            self.play(LaggedStart(*[FadeIn(l, shift=DOWN * 0.15) for l in layers], lag_ratio=0.15), FadeIn(lvd),
                      run_time=1.4)
            wait_until(self, tr, "contain")
            self.play(FadeIn(sets), *[b.animate.set_stroke(PRIMARY, width=4) for b in lit1], run_time=0.7)
            self.play(FadeIn(most), run_time=0.4)
            wait_until(self, tr, "overlap")
            self.play(FadeIn(sets3), FadeIn(sets4), run_time=0.6)
            self.play(layers[3][0].animate.set_fill(PRIMARY, opacity=0.3), Indicate(layers[3][1], color=PRIMARY),
                      run_time=0.8)
            rest(self, tr)

        ticks9 = VGroup(*[tick(at=layers[k][0].get_right() + RIGHT * 0.45, s=0.9) for k in has1])
        glued = RoundedRectangle(width=4.2, height=1.0, corner_radius=0.15, color=WEIRD, stroke_width=4)
        glued.move_to([3.9, -2.0, 0])
        glab = text("glued model", size=30, color=WEIRD).move_to(glued)
        gtick = tick(at=glued.get_right() + RIGHT * 0.5, s=1.2)
        sentlist = VGroup(*[math(r"\varphi_%d" % i, size=34) for i in range(1, 6)], math(r"\cdots", size=34))
        sentlist.arrange(RIGHT, buff=0.45).move_to([3.9, -3.3, 0])
        sticks = VGroup(*[tick(at=m.get_center() + UP * 0.45 + LEFT * 0.0, s=0.6) for m in sentlist[:-1]])
        with self.voiceover(text=N("s06.b10")) as tr:
            self.play(FadeOut(VGroup(sets3, sets4)), LaggedStart(*[Create(t) for t in ticks9], lag_ratio=0.2),
                      run_time=0.9)
            wait_until(self, tr, "glued")
            self.play(Create(glued), FadeIn(glab), run_time=0.6)
            self.play(Create(gtick), run_time=0.4)
            self.play(FadeIn(sentlist), run_time=0.5)
            self.play(LaggedStart(*[Create(t) for t in sticks], lag_ratio=0.2), run_time=0.9)
            rest(self, tr)
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.6)


# ---------------------------------------------------------------------------
# s07 Compact spaces
# ---------------------------------------------------------------------------


def closed_bar(x0, x1, y, color, h=0.18):
    bar = Line([x0, y, 0], [x1, y, 0], color=color, stroke_width=10)
    ends = VGroup(Dot([x0, y, 0], radius=0.1, color=color), Dot([x1, y, 0], radius=0.1, color=color))
    return VGroup(bar, ends)


def switches(center, on=None, size=0.26):
    """Four color switches in a row; `on` is the index that is filled."""
    g = VGroup()
    for i, c in enumerate(C4):
        sq = RoundedRectangle(width=size, height=size, corner_radius=0.05, color=c, stroke_width=3)
        if on == i:
            sq.set_fill(c, opacity=1)
        g.add(sq)
    g.arrange(RIGHT, buff=0.07).move_to(center)
    return g


class S07Topology(VoiceoverScene):
    def construct(self):
        self.set_speech_service(get_speech_service())
        seg = RealLine(0, 1, length=10, y=-1.0, x0=0, size=34, labels={0: "0", 1: "1"})
        sx = lambda v: seg.p(v)[0]
        bars = VGroup(closed_bar(sx(0.1), sx(0.55), 1.4, SECONDARY), closed_bar(sx(0.3), sx(0.8), 0.8, PRIMARY),
                      closed_bar(sx(0.4), sx(0.95), 0.2, GOOD))
        note = text("closed set: includes its edge points", size=34, color=MUTED).move_to([0, -2.4, 0])
        pt = Dot([sx(0.47), -1.0, 0], radius=0.13, color=FG)
        guide = DashedLine([sx(0.47), 1.6, 0], [sx(0.47), -1.0, 0], color=FG, stroke_width=2)
        with self.voiceover(text=N("s07.b1")) as tr:
            self.play(Create(seg), run_time=0.8)
            wait_until(self, tr, "closed")
            self.play(LaggedStart(*[FadeIn(b) for b in bars], lag_ratio=0.3), FadeIn(note), run_time=1.0)
            wait_until(self, tr, "inall")
            self.play(Create(guide), FadeIn(pt, scale=1.5), run_time=0.7)
            rest(self, tr)

        defn = VGroup(text("compact:", size=40, color=PRIMARY, weight="BOLD"),
                      text("if every finite bunch of closed sets has a common point,", size=34),
                      text("then all of them do", size=34)).arrange(DOWN, buff=0.2)
        defn.move_to([0, 2.6, 0])
        with self.voiceover(text=N("s07.b2")) as tr:
            self.play(FadeOut(VGroup(bars, note, pt, guide)), seg.animate.shift(DOWN * 1.2), run_time=0.6)
            self.play(FadeIn(defn[0]), run_time=0.4)
            wait_until(self, tr, "finite")
            self.play(FadeIn(defn[1]), run_time=0.6)
            wait_until(self, tr, "all")
            self.play(FadeIn(defn[2]), run_time=0.6)
            rest(self, tr)

        sx = lambda v: seg.p(v)[0] + 0.0
        y0 = seg.line.get_y()
        nest = VGroup(*[closed_bar(sx(0), sx(1 / n), y0 + 0.5 + 0.38 * (n - 1), C7[(n - 1) % 7]) for n in range(1, 7)])
        nlabs = VGroup(*[math(r"[0, \tfrac{1}{%d}]" % n if n > 1 else r"[0, 1]", size=34, color=C7[(n - 1) % 7])
                         .next_to(nest[n - 1], RIGHT, 0.2) for n in range(1, 7)])
        zero = Dot(seg.p(0), radius=0.16, color=PRIMARY)
        with self.voiceover(text=N("s07.b3")) as tr:
            self.play(LaggedStart(*[AnimationGroup(FadeIn(b), FadeIn(l)) for b, l in zip(nest, nlabs)], lag_ratio=0.3),
                      run_time=2.0)
            wait_until(self, tr, "zero")
            self.play(FadeIn(zero, scale=2), Flash(zero, color=PRIMARY), run_time=0.8)
            rest(self, tr)

        rl = RealLine(-0.5, 9.5, length=12.6, y=-2.6, x0=0, size=30, labels={k: str(k) for k in range(0, 10)})
        rays = VGroup()
        for n in range(1, 6):
            y = -1.9 + 0.48 * (n - 1)
            x = rl.p(n)[0]
            r = VGroup(Line([x, y, 0], [6.6, y, 0], color=C7[(n - 1) % 7], stroke_width=10),
                       Dot([x, y, 0], radius=0.1, color=C7[(n - 1) % 7]),
                       Triangle(color=C7[(n - 1) % 7], fill_opacity=1, stroke_width=0).scale(0.12).rotate(-PI / 2)
                       .move_to([6.75, y, 0]))
            rays.add(r)
        hook = column([r"x > 1", r"x > 2", r"x > 3"], size=34, color=MUTED).to_corner(UL, buff=0.5).shift(DOWN * 2.2)
        nox = cross(np.array([3.5, -0.9, 0]), s=0.5, width=9)
        with self.voiceover(text=N("s07.b4")) as tr:
            self.play(FadeOut(VGroup(nest, nlabs, zero, seg)), run_time=0.5)
            self.play(Create(rl), run_time=0.6)
            self.play(LaggedStart(*[FadeIn(r, shift=RIGHT * 0.3) for r in rays], lag_ratio=0.3), FadeIn(hook),
                      run_time=1.4)
            wait_until(self, tr, "nothing")
            self.play(*[r.animate.shift(RIGHT * 14) for r in rays], run_time=1.4, rate_func=rush_into)
            self.play(Create(nox), run_time=0.4)
            rest(self, tr)

        # Switches.
        P = np.array([-3.0, 0.4, 0])
        Q = P + U5 * RIGHT * 1.6
        pd, qd = vdot(P, FG, 0.14), vdot(Q, FG, 0.14)
        pl = math("p", size=40).next_to(pd, DOWN, 0.15)
        ql = math("q", size=40).next_to(qd, DOWN, 0.15)
        psw = switches(P + UP * 0.75, on=0, size=0.42)
        qsw = switches(Q + UP * 0.75, on=1, size=0.42)
        pq = edge(P, Q, color=MUTED)
        rng = np.random.default_rng(2)
        grid = VGroup()
        for i in range(7):
            for j in range(12):
                grid.add(switches([-6.0 + j * 1.1, 2.8 - i * 0.62, 0], on=int(rng.integers(0, 4)), size=0.17))
        gl = text("every way to set the switches", size=34, color=PRIMARY).move_to([0, -2.0, 0])
        with self.voiceover(text=N("s07.b5")) as tr:
            self.remove(rays)
            self.play(FadeOut(VGroup(rl, hook, nox, defn)), run_time=0.5)
            self.play(FadeIn(pd), FadeIn(qd), FadeIn(pl), FadeIn(ql), Create(pq), run_time=0.6)
            wait_until(self, tr, "sw")
            self.play(FadeIn(psw, shift=UP * 0.2), FadeIn(qsw, shift=UP * 0.2), run_time=0.6)
            wait_until(self, tr, "space")
            self.play(FadeOut(VGroup(pd, qd, pl, ql, pq, psw, qsw)), LaggedStart(*[FadeIn(g) for g in grid],
                                                                              lag_ratio=0.005), run_time=1.2)
            self.play(FadeIn(gl), run_time=0.5)
            rest(self, tr)

        rule = text("p and q have different colors", size=36).move_to([0, 3.2, 0])
        def setting(center, other_seed):
            r2 = np.random.default_rng(other_seed)
            g = VGroup(math("p", size=28).move_to(center + LEFT * 1.1 + UP * 0.35),
                       switches(center + LEFT * 0.2 + UP * 0.35, on=0, size=0.2),
                       math("q", size=28).move_to(center + LEFT * 1.1 + DOWN * 0.05),
                       switches(center + LEFT * 0.2 + DOWN * 0.05, on=0, size=0.2))
            others = VGroup(*[switches(center + LEFT * 0.2 + DOWN * (0.45 + 0.3 * k), on=int(r2.integers(0, 4)), size=0.2)
                              for k in range(2)])
            box = RoundedRectangle(width=2.8, height=2.0, corner_radius=0.15, color=MUTED, stroke_width=2).move_to(center + DOWN * 0.1)
            return VGroup(box, g, others)
        sets_ = VGroup(*[setting(np.array([x, 1.2, 0]), k) for k, x in enumerate([-3.6, 0, 3.6])])
        xs = VGroup(*[cross(s.get_corner(UR) + LEFT * 0.3 + DOWN * 0.3, s=0.16) for s in sets_])
        space = Ellipse(width=10.0, height=3.0, color=MUTED, stroke_width=3).move_to([0, -1.9, 0])
        blob = Ellipse(width=4.6, height=1.9, color=PRIMARY, fill_opacity=0.25, stroke_width=3).move_to([-1.2, -1.9, 0])
        blab = text("obeys the rule: closed", size=28, color=PRIMARY).move_to(blob)
        foot = text("close = agree on any given finite set of switches", size=24, color=MUTED).move_to([0, -3.65, 0])
        tych = text("Tychonoff: this space is compact", size=34, color=GOOD).move_to([2.9, -0.2, 0])
        with self.voiceover(text=N("s07.b6")) as tr:
            self.play(FadeOut(VGroup(grid, gl)), FadeIn(rule), run_time=0.6)
            wait_until(self, tr, "few")
            self.play(FadeIn(sets_[0]), run_time=0.5)
            wait_until(self, tr, "breaks")
            self.play(Create(xs[0]), run_time=0.4)
            self.play(FadeIn(sets_[1:]), run_time=0.5)
            self.play(Create(xs[1:]), run_time=0.5)
            self.play(Create(space), FadeIn(blob), FadeIn(blab), FadeIn(foot), run_time=0.8)
            wait_until(self, tr, "tych")
            self.play(FadeIn(tych), run_time=0.6)
            rest(self, tr)

        blobs = VGroup(*[Ellipse(width=w, height=h, color=c, fill_opacity=0.2, stroke_width=3).move_to(p)
                         for w, h, c, p in [(5.0, 2.6, PRIMARY, [-1.4, 0.4, 0]), (4.6, 3.0, SECONDARY, [1.2, 0.6, 0]),
                                            (4.4, 2.4, GOOD, [0.0, -0.6, 0]), (3.6, 3.4, TERTIARY, [-0.2, 0.3, 0])]])
        frame = RoundedRectangle(width=11.5, height=6.0, corner_radius=0.3, color=MUTED, stroke_width=3)
        common = Dot([-0.2, 0.1, 0], radius=0.14, color=FG)
        cov = hex_tiling(unit=U5, side=HEX_SIDE, radius=7.6)
        with self.voiceover(text=N("s07.b7")) as tr:
            self.play(FadeOut(VGroup(rule, sets_, xs, space, blob, blab, foot, tych)), run_time=0.5)
            self.play(Create(frame), LaggedStart(*[FadeIn(b) for b in blobs], lag_ratio=0.3), run_time=1.4)
            wait_until(self, tr, "one")
            self.play(FadeIn(common, scale=2), Flash(common, color=FG), run_time=0.7)
            self.play(FadeOut(VGroup(blobs, frame)), common.animate.scale(4), run_time=0.6)
            self.play(FadeOut(common), LaggedStart(*[FadeIn(h, scale=0.5) for h in cov], lag_ratio=0.004), run_time=1.2)
            rest(self, tr)

        # Descriptions.
        rng = np.random.default_rng(9)
        pts = []
        while len(pts) < 16:
            p = np.array([rng.uniform(-5.6, 5.6), rng.uniform(-2.2, 1.8), 0])
            if all(np.linalg.norm(p - q) > 1.2 for q in pts):
                pts.append(p)
        truth = [bool(rng.integers(0, 2)) for _ in pts]
        dd = VGroup(*[Dot(p, radius=0.11, color=FG) for p in pts])
        tf = lambda t: r"\mathrm{T}" if t else r"\mathrm{F}"
        callouts = VGroup()
        for k in (0, 5, 9):
            s = r"\varphi_1\!: %s,\ \varphi_2\!: %s,\ \varphi_3\!: %s,\ \dots" % (tf(truth[k]), tf(rng.integers(0, 2)),
                                                                                tf(rng.integers(0, 2)))
            callouts.add(math(s, size=32).next_to(dd[k], UP, 0.12).add_background_rectangle(color=BG, opacity=0.8))
        dtitle = text("complete descriptions", size=36, color=PRIMARY).move_to([0, 3.2, 0])
        carve = VGroup(*[d.copy().set_color(PRIMARY).scale(1.5) for d, t in zip(dd, truth) if t])
        clab = math(r"\{\text{descriptions that say } \varphi_1 \text{ is true}\}", size=32, color=PRIMARY)
        clab.move_to([0, -3.3, 0])
        with self.voiceover(text=N("s07.b8")) as tr:
            self.play(FadeOut(cov), run_time=0.6)
            wait_until(self, tr, "desc")
            self.play(FadeIn(dtitle), LaggedStart(*[FadeIn(d) for d in dd], lag_ratio=0.05), run_time=1.0)
            self.play(FadeIn(callouts), run_time=0.7)
            wait_until(self, tr, "carve")
            self.play(FadeOut(callouts), FadeIn(carve), FadeIn(clab), run_time=0.8)
            rest(self, tr)

        eq1 = VGroup(text("a set of sentences has a model", size=32), math("=", size=40),
                     text("their closed sets share a point", size=32)).arrange(RIGHT, buff=0.3)
        eq2 = VGroup(text("every finite batch has a model", size=32), math("=", size=40),
                     text("every finite bunch shares a point", size=32)).arrange(RIGHT, buff=0.3)
        eqs = VGroup(eq1, eq2).arrange(DOWN, buff=0.45).move_to([0, 2.2, 0])
        over = text("every closed set is an overlap of carved ones", size=28, color=MUTED).next_to(eqs, DOWN, 0.35)
        tb = theorem_box(size=34).move_to([0, -1.9, 0])
        compact = text("this space is compact", size=44, color=PRIMARY, weight="BOLD").move_to(tb)
        with self.voiceover(text=N("s07.b9")) as tr:
            self.play(FadeOut(VGroup(dd, carve, clab, dtitle)), run_time=0.5)
            self.play(FadeIn(eq1), run_time=0.7)
            wait_until(self, tr, "share")
            self.play(FadeIn(eq2), run_time=0.7)
            self.play(FadeIn(over), run_time=0.5)
            self.play(FadeIn(tb), run_time=0.6)
            wait_until(self, tr, "compact")
            self.play(ReplacementTransform(tb, compact), run_time=0.9)
            rest(self, tr)

        cards = VGroup()
        for s in ["compactness\ntheorem", "Tychonoff's\ntheorem", "overlapping sets grow\ninto ultrafilters"]:
            t = VGroup(*[text(line, size=32) for line in s.split("\n")]).arrange(DOWN, buff=0.12)
            box = SurroundingRectangle(t, color=PRIMARY, buff=0.3, corner_radius=0.15)
            cards.add(VGroup(box, t))
        cards[0].move_to([-4.3, 0.9, 0])
        cards[1].move_to([4.3, 0.9, 0])
        cards[2].move_to([0, -1.9, 0])
        arr = VGroup(DoubleArrow(cards[0].get_right(), cards[1].get_left(), buff=0.2, color=MUTED),
                     DoubleArrow(cards[0].get_bottom(), cards[2].get_left(), buff=0.2, color=MUTED),
                     DoubleArrow(cards[1].get_bottom(), cards[2].get_right(), buff=0.2, color=MUTED))
        hf = text("Tychonoff for compact Hausdorff spaces; all equivalent over ZF", size=24, color=MUTED)
        hf.move_to([0, -3.5, 0])
        with self.voiceover(text=N("s07.b10")) as tr:
            self.play(FadeOut(VGroup(eqs, over, compact)), run_time=0.5)
            self.play(LaggedStart(*[FadeIn(c) for c in cards], lag_ratio=0.4), run_time=1.4)
            wait_until(self, tr, "equiv")
            self.play(Create(arr), FadeIn(hf), run_time=1.0)
            rest(self, tr)
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.6)


# ---------------------------------------------------------------------------
# s08 Ending
# ---------------------------------------------------------------------------


class S08Ending(VoiceoverScene):
    def construct(self):
        self.set_speech_service(get_speech_service())
        bl = bounds_line(1, 8, y=-1.2, length=10, marks=(5, 6, 7), shade=(5, 7), size=40)
        bl.marks[1].set_color(PRIMARY).scale(1.4)
        six = text("6?", size=60, color=PRIMARY, weight="BOLD").next_to(bl.marks[1], UP, 0.5)
        g = unit_graph(unit=0.6, center=[0, 1.9, 0], rad=2.6, rots=(0.0, SPINDLE_PHI)).set_opacity(0.25)
        with self.voiceover(text=N("s08.b1")) as tr:
            self.play(FadeIn(bl), run_time=0.8)
            self.play(FadeIn(six), run_time=0.5)
            wait_until(self, tr, "promise")
            self.play(FadeIn(g), run_time=0.8)
            self.play(g.animate.set_opacity(0.05), run_time=0.6)
            self.play(g.animate.set_opacity(0.25), run_time=0.6)
            self.play(g.animate.set_opacity(0.0), run_time=rt(tr.get_remaining_duration()))
        self.wait(1.2)
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.8)


class Thumbnail(Scene):
    def construct(self):
        tiling = hex_tiling(unit=U5, side=HEX_SIDE, radius=7.6, opacity=0.75)
        band = Rectangle(width=FW + 0.2, height=3.6, color=BG, fill_color=BG, fill_opacity=0.88, stroke_width=0)
        t1 = text("Solve every finite piece,", size=84, weight="BOLD")
        t2 = text("solve the infinite whole", size=84, weight="BOLD", color=PRIMARY)
        VGroup(t1, t2).arrange(DOWN, buff=0.3)
        self.add(tiling, band, t1, t2)
