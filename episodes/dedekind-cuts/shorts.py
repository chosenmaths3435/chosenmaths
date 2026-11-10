"""Vertical shorts. Render with MV_ASPECT=portrait."""

import sys
from fractions import Fraction as Fr
from pathlib import Path

import numpy as np
from manim import *
from manim_voiceover import VoiceoverScene

from mathvid import layout  # noqa: F401  must come before scene code runs
from mathvid.anim import rest, rt, wait_until
from mathvid.layout import FW, SAFE_BOTTOM, SAFE_TOP
from mathvid.numberline import ZoomLine
from mathvid.orders import LEFT_C, RIGHT_C, RatLine, cross, hollow_at, left_bar, rats, scissors, solid_line, tick
from mathvid.script import Script
from mathvid.style import BAD, FG, GOOD, MUTED, PRIMARY, SECONDARY, TERTIARY, math, text
from mathvid.voice import get_speech_service

sys.path.insert(0, str(Path(__file__).parent))
from scenes import R2, SUSLIN_FACT, op_tags, until  # noqa: E402

N = Script(__file__)

MID = (SAFE_TOP + SAFE_BOTTOM) / 2
TOP = SAFE_TOP - 0.5
HALF = 3.4


def fit(m, w=FW - 1.0):
    if m.width > w:
        m.scale_to_fit_width(w)
    return m


def tag(s, size=40, color=FG, **kw):
    return text(s, size=size, color=color, **kw)


def stack(lines, size=40, color=FG, buff=0.12):
    return VGroup(*[tag(s, size, color) for s in lines]).arrange(DOWN, buff=buff)


# ---------------------------------------------------------------------------
# short1 A real number is a cut
# ---------------------------------------------------------------------------


class Short1Cut(VoiceoverScene):
    def construct(self):
        self.set_speech_service(get_speech_service())
        y = 0.6
        lo, hi, unit = -0.2, 2.2, 2.8
        L = RatLine(lo, hi, unit, y=y, qmax=12, r=0.07)
        nums = L.numbers([0, 1, 2], size=44)
        big = math(r"\sqrt{2}", size=110).move_to([0, 4.0, 0])
        q = text("?", size=80, color=PRIMARY).move_to([L.x(R2), y + 1.1, 0])
        ring = hollow_at(L.p(R2), r=0.13, color=PRIMARY)
        with self.voiceover(text=N("short1.b1")) as tr:
            self.play(FadeIn(big), FadeIn(L), FadeIn(nums), run_time=0.8)
            self.play(FadeIn(q), run_time=0.4)
            wait_until(self, tr, "gap")
            self.play(Create(ring), run_time=0.5)
            rest(self, tr)

        sc = scissors(70).move_to([L.x(R2), y + 0.9, 0])
        lab_l = fit(math(r"q<0 \text{ or } q^2<2", size=50, color=LEFT_C)).move_to([0, 2.6, 0])
        lab_r = fit(math(r"q>0 \text{ and } q^2>2", size=50, color=RIGHT_C)).move_to([0, -1.2, 0])
        with self.voiceover(text=N("short1.b2")) as tr:
            self.play(FadeOut(q), FadeOut(big), FadeOut(ring), FadeIn(sc, shift=DOWN * 0.3), run_time=0.6)
            wait_until(self, tr, "rule")
            self.play(L.left_of(R2).animate.set_color(LEFT_C), FadeIn(lab_l), run_time=0.7)
            self.wait(rt(min(1.5, tr.get_remaining_duration() - 0.8)))
            self.play(L.right_of(R2).animate.set_color(RIGHT_C), FadeIn(lab_r), run_time=0.7)
            rest(self, tr)

        Z = ZoomLine(lo, hi, length=(hi - lo) * unit, center=np.array([L.x((lo + hi) / 2), y, 0]), label_size=30,
                     max_labels=4)
        Z.line.set_opacity(0)
        axis = Line([-HALF - 0.3, y, 0], [HALF + 0.3, y, 0], color=MUTED, stroke_width=3)
        blues, golds = [1.4, 1.41, 1.414, 1.4142], [1.5, 1.42, 1.415, 1.4143]
        bd = [Z.dot(v, color=LEFT_C, radius=0.12) for v in blues]
        gd = [Z.dot(v, color=RIGHT_C, radius=0.12) for v in golds]
        ranges = [(1.3, 1.55), (1.39, 1.44), (1.405, 1.425), (1.4128, 1.4152)]
        with self.voiceover(text=N("short1.b3")) as tr:
            self.add(axis, Z, *bd, *gd)
            self.play(FadeOut(L), FadeOut(nums), FadeOut(sc), lab_l.animate.move_to([0, 4.3, 0]),
                      lab_r.animate.move_to([0, -2.0, 0]), *Z.zoom_to(*ranges[0]), run_time=0.8)
            wait_until(self, tr, "nomax")
            T = tr.time_until_bookmark("nomin")
            step = max(0.45, T / 4)
            for i, v in enumerate(blues):
                sq = fit(math(f"{v}^2 = {v * v:.8f}".rstrip("0") + "<2", size=46, color=LEFT_C)).move_to([0, 3.0, 0])
                self.play(*Z.zoom_to(*ranges[i]), bd[i].show.animate.set_value(1), FadeIn(sq), run_time=step * 0.7)
                self.wait(step * 0.3)
                self.remove(sq)
            wait_until(self, tr, "nomin")
            step = max(0.45, (tr.get_remaining_duration() - 0.2) / 4)
            for i, v in enumerate(golds):
                sq = fit(math(f"{v}^2 = {v * v:.8f}".rstrip("0") + ">2", size=46, color=RIGHT_C)).move_to([0, -0.8, 0])
                self.play(*Z.zoom_to(*ranges[i]), gd[i].show.animate.set_value(1), FadeIn(sq), run_time=step * 0.7)
                self.wait(step * 0.3)
                self.remove(sq)
            rest(self, tr)

        zd = []
        for v in rats(0.9, 1.95, 12):
            d = Z.dot(float(v), color=LEFT_C if v < R2 else RIGHT_C, radius=0.055, hole=R2)
            zd.append(d)
        zring = Z.ring(R2, radius=0.14, color=FG)
        hole = tag("hole", 46).move_to([0, y + 1.0, 0])
        with self.voiceover(text=N("short1.b4")) as tr:
            self.add(*zd)
            self.play(*Z.zoom_to(1.05, 1.8), *[d.show.animate.set_value(1) for d in zd],
                      *[d.show.animate.set_value(0) for d in bd + gd], run_time=1.2)
            wait_until(self, tr, "hole")
            hole.move_to(Z.p(R2) + UP * 0.9)
            self.play(Create(zring), FadeIn(hole), run_time=0.6)
            rest(self, tr)

        # Back to the dotted line, lift the left piece.
        L2 = RatLine(lo, hi, unit, y=-1.0, qmax=12, r=0.07)
        L2.left_of(R2).set_color(LEFT_C)
        L2.right_of(R2).set_color(RIGHT_C)
        piece = VGroup(Line(L2.p(lo), L2.p(R2), color=LEFT_C, stroke_width=3), L2.left_of(R2).copy())
        dlab = math(r"\sqrt{2}", ":=", size=70, color=LEFT_C).move_to([-1.6, 2.7, 0])
        ded = tag("Dedekind, 1872", 36, MUTED).move_to([0, 4.6, 0])
        with self.voiceover(text=N("short1.b5")) as tr:
            self.play(FadeOut(VGroup(lab_l, lab_r, hole, zring, axis)), FadeOut(Z), *[FadeOut(d) for d in zd],
                      FadeIn(L2), FadeIn(ded), run_time=0.8)
            wait_until(self, tr, "def")
            self.add(piece)
            self.play(piece.animate.shift(UP * 2.4), L2.left_of(R2).animate.set_opacity(0.25), FadeIn(dlab), run_time=0.7)
            rest(self, tr)

        xs = lambda v: -2.6 + float(v) * 1.5  # noqa: E731
        vals = [(Fr(1, 2), r"\tfrac12"), (Fr(1), "1"), (R2, r"\sqrt2"), (PI, r"\pi")]
        bars, blabs = VGroup(), VGroup()
        for i, (v, s) in enumerate(vals):
            yy = 4.0 - i * 1.0
            b = left_bar(xs(v), yy, x_start=-3.9, height=0.3)
            bars.add(b)
            blabs.add(math(s, size=50, color=LEFT_C).next_to(b, RIGHT, buff=0.2))
        R = solid_line(-HALF, HALF, -1.2)
        pts = VGroup(*[Dot([b.x_end, -1.2, 0], radius=0.12, color=LEFT_C) for b in bars])
        with self.voiceover(text=N("short1.b6")) as tr:
            self.play(FadeOut(VGroup(piece, dlab, ded, L2)), run_time=0.5)
            self.play(LaggedStart(*[GrowFromEdge(b, LEFT) for b in bars], lag_ratio=0.25), FadeIn(blabs, lag_ratio=0.25),
                      run_time=1.3)
            wait_until(self, tr, "line")
            self.play(*[ReplacementTransform(b, p) for b, p in zip(bars, pts)],
                      *[l.animate.next_to(p, UP if i % 2 == 0 else DOWN, buff=0.3) for i, (l, p) in enumerate(zip(blabs, pts))],
                      Create(R), run_time=1.2)
            rest(self, tr)

        fin = VGroup(math(r"\sqrt{2}", "=", size=80, color=FG),
                     math(r"\{\, q : q<0 \text{ or } q^2<2 \,\}", size=56, color=LEFT_C)).arrange(DOWN, buff=0.35)
        fit(fin).move_to([0, 2.6, 0])
        with self.voiceover(text=N("short1.b7")) as tr:
            self.play(FadeOut(VGroup(pts, blabs)), R.animate.shift(DOWN * 0.6), run_time=0.5)
            wait_until(self, tr, "end")
            self.play(FadeIn(fin), run_time=0.8)
            rest(self, tr)
        self.wait(1.0)


# ---------------------------------------------------------------------------
# short2 Only one line
# ---------------------------------------------------------------------------


class Short2OnlyOne(VoiceoverScene):
    def construct(self):
        self.set_speech_service(get_speech_service())
        y = 0.2
        L = solid_line(-HALF, HALF, y)
        ops = op_tags(size=110)
        ops.arrange(RIGHT, buff=0.9).move_to([0, 3.2, 0])
        fit(ops)
        less = math("<", size=180, color=PRIMARY).move_to([0, 3.2, 0])
        with self.voiceover(text=N("short2.b1")) as tr:
            self.play(Create(L), FadeIn(ops), run_time=0.7)
            for mark, o in zip(("add", "mul", "dist"), ops):
                wait_until(self, tr, mark)
                c = cross(o.get_center(), s=0.45, width=9)
                self.play(Create(c), run_time=0.3)
                self.play(FadeOut(o), FadeOut(c), run_time=0.35)
            wait_until(self, tr, "less")
            self.play(FadeIn(less, scale=0.6), run_time=0.6)
            rest(self, tr)

        tags = VGroup(tag("no holes", 44, PRIMARY), tag("dense", 44, PRIMARY), tag("no ends", 44, PRIMARY),
                      stack(["a countable set", "spread through it"], 44, PRIMARY))
        for t in tags[3]:
            t.set_color(PRIMARY)
        tags[3].arrange(DOWN, aligned_edge=LEFT, buff=0.08)
        tags.arrange(DOWN, aligned_edge=LEFT, buff=0.3).move_to([0.4, 3.6, 0])
        tks = VGroup(*[tick(t) for t in tags])
        sc = scissors(60).move_to([0.7, y + 0.8, 0])
        P = Dot([0.7, y, 0], radius=0.13, color=GOOD)
        Dv = rats(-1.8, 1.8, 5)
        unit = 1.85
        Dd = VGroup(*[Dot([float(v) * unit, y, 0], radius=0.09 * Fr(v).denominator ** -0.3, color=PRIMARY) for v in Dv])
        with self.voiceover(text=N("short2.b2")) as tr:
            self.play(FadeOut(less), L.animate.shift(DOWN * 0.9), run_time=0.5)
            y2 = y - 0.9
            sc.move_to([0.7, y2 + 0.8, 0])
            P.move_to([0.7, y2, 0])
            Dd.shift(DOWN * 0.9)
            wait_until(self, tr, "f1")
            self.play(FadeIn(tags[0]), Create(tks[0]), FadeIn(sc, shift=DOWN * 0.3), run_time=0.5)
            self.play(FadeIn(P, scale=2), run_time=0.4)
            wait_until(self, tr, "f2")
            self.play(FadeIn(tags[1]), Create(tks[1]), FadeOut(sc), FadeOut(P), run_time=0.5)
            wait_until(self, tr, "f3")
            self.play(FadeIn(tags[2]), Create(tks[2]), Indicate(L.tips, color=PRIMARY), run_time=0.6)
            wait_until(self, tr, "f4")
            self.play(FadeIn(tags[3]), Create(tks[3]), FadeIn(Dd, lag_ratio=0.02), run_time=1.0)
            rest(self, tr)

        Dc = Dd.copy()
        ylow = -1.9
        ax = Line([-HALF, ylow, 0], [HALF, ylow, 0], color=MUTED, stroke_width=3)
        isq = tag("= the rationals", 44, PRIMARY).move_to([0, -1.5 + 0.0, 0])
        cantor = tag("(Cantor)", 34, MUTED)
        with self.voiceover(text=N("short2.b3")) as tr:
            self.add(Dc)
            self.play(Dc.animate.shift(DOWN * (y - 0.9 - ylow)), FadeIn(ax), run_time=0.8)
            wait_until(self, tr, "q")
            VGroup(isq, cantor).arrange(RIGHT, buff=0.3).move_to([0, ylow - 0.65, 0])
            self.play(FadeIn(isq), FadeIn(cantor), run_time=0.6)
            rest(self, tr)

        xp = 0.45 * unit
        yl = y - 0.9
        Pt = Dot([xp, yl, 0], radius=0.16, color=FG)
        leftD = VGroup(*[d for d, v in zip(Dd, Dv) if float(v) * unit < xp])
        caption = stack(["a point =", "the dots to its left"], 46, PRIMARY).move_to([0, 3.4, 0])
        with self.voiceover(text=N("short2.b4")) as tr:
            self.play(FadeOut(VGroup(Dc, ax, isq, cantor, tags, tks)), run_time=0.5)
            self.play(FadeIn(Pt, scale=2), run_time=0.4)
            wait_until(self, tr, "left")
            self.play(leftD.animate.set_color(LEFT_C), FadeIn(caption), run_time=0.9)
            rest(self, tr)

        chain = VGroup(tag("the line", 46), math("=", size=56), tag("cuts of the rationals", 46), math("=", size=56),
                       tag("the real line", 50, PRIMARY)).arrange(DOWN, buff=0.25).move_to([0, 3.0, 0])
        with self.voiceover(text=N("short2.b5")) as tr:
            self.play(FadeOut(caption), run_time=0.4)
            self.play(FadeIn(chain[:3], lag_ratio=0.3), run_time=0.9)
            wait_until(self, tr, "end")
            self.play(FadeIn(chain[3:]), run_time=0.6)
            rest(self, tr)
        self.wait(1.0)


# ---------------------------------------------------------------------------
# short3 A question math can't answer
# ---------------------------------------------------------------------------


class Short3Suslin(VoiceoverScene):
    def construct(self):
        self.set_speech_service(get_speech_service())
        t0 = stack(["no holes", "(every cut lands on a point)"], 40, PRIMARY)
        t0[1].scale(0.8).set_color(MUTED)
        tags = VGroup(t0, tag("dense", 42, PRIMARY), tag("no ends", 42, PRIMARY),
                      stack(["a countable set", "spread through it"], 42, PRIMARY))
        for t in (tags[0], tags[3]):
            t.arrange(DOWN, aligned_edge=LEFT, buff=0.06)
        tags.arrange(DOWN, aligned_edge=LEFT, buff=0.28).move_to([0, 3.6, 0])
        eq = math("=", size=70, color=PRIMARY).move_to([0, 0.8, 0])
        y = -0.5
        R = solid_line(-HALF, HALF, y)
        rl = tag("the real line", 40).move_to([0, -1.4, 0])
        hook = stack(["a question", "math can't settle"], 54, PRIMARY).move_to([0, 3.4, 0])
        with self.voiceover(text=N("short3.b1")) as tr:
            self.play(FadeIn(hook), Create(R), FadeIn(rl), run_time=0.7)
            wait_until(self, tr, "facts")
            self.play(FadeOut(hook), run_time=0.3)
            self.play(LaggedStart(*[FadeIn(t, shift=RIGHT * 0.2) for t in tags], lag_ratio=0.5), FadeIn(eq),
                      run_time=rt(min(3.0, tr.get_remaining_duration())))
            rest(self, tr)

        new = stack(["no uncountable family", "of separate intervals"], 42, GOOD)
        for t in new:
            t.set_color(GOOD)
        new.arrange(DOWN, aligned_edge=LEFT, buff=0.06).move_to(tags[3], aligned_edge=LEFT)
        with self.voiceover(text=N("short3.b2")) as tr:
            wait_until(self, tr, "swap")
            self.play(tags[3].animate.shift(RIGHT * 6).set_opacity(0), run_time=0.6)
            self.play(FadeIn(new, shift=RIGHT * 0.4), run_time=0.6)
            rest(self, tr)

        ivs = [(-3.1, -2.4), (-2.1, -1.5), (-1.2, -0.2), (0.1, 0.6), (0.9, 1.9), (2.2, 3.1)]
        cols = [PRIMARY, SECONDARY, TERTIARY, GOOD]
        bars = VGroup(*[Rectangle(width=b - a, height=0.34, stroke_width=0, fill_color=cols[i % 4], fill_opacity=0.55)
                        .move_to([(a + b) / 2, y, 0]) for i, (a, b) in enumerate(ivs)])
        qs = VGroup(*[Dot([a + (b - a) * 0.4, y, 0], radius=0.1, color=FG) for a, b in ivs])
        with self.voiceover(text=N("short3.b3")) as tr:
            self.play(FadeOut(rl), FadeOut(eq), LaggedStart(*[GrowFromCenter(b) for b in bars], lag_ratio=0.15), run_time=1.0)
            wait_until(self, tr, "frac")
            self.play(FadeIn(qs, lag_ratio=0.15), run_time=0.8)
            rest(self, tr)

        box = VGroup(tags[:3], new)
        eq2 = VGroup(math("=", size=80, color=PRIMARY), text("?", size=90, color=PRIMARY)).arrange(RIGHT, buff=0.3)
        eq2.move_to([0, 0.7, 0])
        sus = tag("Suslin (published 1920)", 38, MUTED).move_to([0, -1.6, 0])
        with self.voiceover(text=N("short3.b4")) as tr:
            self.play(FadeOut(bars), FadeOut(qs), run_time=0.5)
            self.play(FadeIn(eq2[0]), run_time=0.4)
            wait_until(self, tr, "ask")
            self.play(FadeIn(eq2[1], scale=0.6), FadeIn(sus), run_time=0.6)
            rest(self, tr)

        l1 = tag("can't be proved (1967-68)", 40)
        l2 = tag("can't be disproved (1971)", 40)
        l3 = tag("from the usual axioms of math", 40, PRIMARY)
        lines = VGroup(l1, l2, l3).arrange(DOWN, buff=0.25).move_to([0, -1.9, 0])
        with self.voiceover(text=N("short3.b5")) as tr:
            self.play(FadeOut(sus), R.animate.shift(UP * 0.0), run_time=0.4)
            self.play(R.animate.set_opacity(0.0), run_time=0.3)
            wait_until(self, tr, "yes")
            self.play(FadeIn(l1), run_time=0.5)
            wait_until(self, tr, "no")
            self.play(FadeIn(l2), run_time=0.5)
            self.play(FadeIn(l3), run_time=0.5)
            rest(self, tr)

        with self.voiceover(text=N("short3.b6")) as tr:
            self.play(FadeOut(box), FadeOut(lines), FadeOut(eq2[0]), run_time=0.6)
            wait_until(self, tr, "end")
            self.play(eq2[1].animate.scale(2.4).move_to([0, MID, 0]), run_time=1.0)
            rest(self, tr)
        self.wait(1.0)
