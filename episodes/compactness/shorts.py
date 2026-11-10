"""Vertical shorts. Render with MV_ASPECT=portrait."""

import sys
from math import sqrt
from pathlib import Path

import numpy as np
from manim import *
from manim_voiceover import VoiceoverScene

from mathvid import layout  # noqa: F401  must come before scene code runs
from mathvid.anim import rest, rt, wait_until
from mathvid.layout import SAFE_BOTTOM, SAFE_TOP
from mathvid.numberline import RealLine
from mathvid.orders import cross, tick
from mathvid.script import Script
from mathvid.style import BAD, BG, FG, GOOD, MUTED, PRIMARY, SECONDARY, math, text
from mathvid.voice import get_speech_service

sys.path.insert(0, str(Path(__file__).parent))
from scenes import (  # noqa: E402
    SPINDLE_PHI,
    WEIRD,
    bounds_line,
    column,
    dirv,
    drop_in,
    edge,
    hex_tiling,
    hyper_cloud,
    labelled,
    unit_graph,
    vdot,
)

N = Script(__file__)

MID = (SAFE_TOP + SAFE_BOTTOM) / 2  # center of the safe area


def lines(*ss, size=52, color=FG, buff=0.18):
    return VGroup(*[text(s, size=size, color=color) for s in ss]).arrange(DOWN, buff=buff)


class Short1Infinitesimals(VoiceoverScene):
    def construct(self):
        self.set_speech_service(get_speech_service())
        q = lines("How do you solve", "infinitely many", "problems at the", "same time?", size=56)
        a = lines("Just solve every", "finite number", "of them.", size=56, color=PRIMARY)
        VGroup(q, a).arrange(DOWN, buff=0.9).move_to([0, MID + 0.4, 0])
        with self.voiceover(text=N("short1.b1")) as tr:
            self.play(FadeIn(q, shift=UP * 0.2), run_time=0.8)
            wait_until(self, tr, "answer")
            self.play(FadeIn(a, shift=UP * 0.2), run_time=0.6)
            rest(self, tr)

        col = column([r"c > 0", r"c < 1", r"c < \tfrac{1}{2}", r"c < \tfrac{1}{3}"], size=66, dots=False)
        more = math(r"c < \tfrac{1}{7}", size=66)
        vd1, vd2 = math(r"\vdots", size=56), math(r"\vdots", size=56)
        full = VGroup(*col, vd1, more, vd2).arrange(DOWN, buff=0.2, aligned_edge=LEFT)
        vd1.shift(RIGHT * 0.45)
        vd2.shift(RIGHT * 0.45)
        full.move_to([-1.6, SAFE_TOP - 0.3 - full.height / 2, 0])
        rl = RealLine(0, 1, length=6.4, y=SAFE_BOTTOM + 1.0, x0=0, size=44, labels={0: "0", 1: "1"})
        cd = Dot(rl.p(0.5), radius=0.14, color=PRIMARY)
        cl = math("c", size=56, color=PRIMARY).next_to(cd, UP, 0.2)
        cl.add_updater(lambda m: m.next_to(cd, UP, 0.2))
        big_x = cross(full.get_center(), s=1.4, width=12)
        with self.voiceover(text=N("short1.b2")) as tr:
            self.play(FadeOut(q), FadeOut(a), run_time=0.4)
            drop_in(self, list(full), rt(min(3.0, tr.time_until_bookmark("never") - 0.3)))
            wait_until(self, tr, "never")
            self.play(Create(rl), FadeIn(cd), FadeIn(cl), run_time=0.6)
            for v in (0.3, 0.15, 0.06, 0.02):
                self.play(cd.animate.move_to(rl.p(v)), run_time=0.35)
            self.play(Create(big_x), run_time=0.4)
            rest(self, tr)

        br = Brace(VGroup(*full[:6]), direction=RIGHT, color=PRIMARY, buff=0.25)
        c8 = math(r"c = \tfrac{1}{8}", size=56, color=PRIMARY).next_to(br, RIGHT, 0.2)
        ok = tick(at=c8.get_bottom() + DOWN * 0.55 + RIGHT * 0.2, s=1.6)
        with self.voiceover(text=N("short1.b3")) as tr:
            self.play(FadeOut(big_x), run_time=0.3)
            wait_until(self, tr, "batch")
            self.play(GrowFromCenter(br), cd.animate.move_to(rl.p(1 / 8)), run_time=0.6)
            self.play(FadeIn(c8), Create(ok), run_time=0.5)
            rest(self, tr)

        thm = VGroup(text("the compactness theorem", size=46, color=PRIMARY),
                     lines("every finite batch", "has a model", size=44),
                     math(r"\Downarrow", size=60),
                     lines("all of them", "have one at once", size=44)).arrange(DOWN, buff=0.3)
        box = SurroundingRectangle(VGroup(*thm[1:]), color=PRIMARY, buff=0.35, corner_radius=0.15)
        thm[0].next_to(box, UP, 0.35)
        T = VGroup(thm, box).move_to([0, MID + 0.4, 0])
        with self.voiceover(text=N("short1.b4")) as tr:
            cl.clear_updaters()
            self.play(FadeOut(VGroup(full, br, c8, ok, rl, cd, cl)), run_time=0.5)
            self.play(FadeIn(thm[0]), FadeIn(thm[1]), Create(box), run_time=0.8)
            wait_until(self, tr, "all")
            self.play(FadeIn(thm[2:]), run_time=0.6)
            rest(self, tr)

        scroll = VGroup(lines("every statement", size=44), VGroup(text("true in", size=44),
                        math(r"\mathbb{R}", size=50)).arrange(RIGHT, buff=0.15)).arrange(DOWN, buff=0.15)
        sbox = SurroundingRectangle(scroll, color=MUTED, buff=0.3, corner_radius=0.15)
        plus = math("+", size=70)
        cs = column([r"c > 0", r"c < 1", r"c < \tfrac{1}{2}"], size=56)
        S = VGroup(VGroup(sbox, scroll), plus, cs).arrange(DOWN, buff=0.4).move_to([0, MID + 0.3, 0])
        with self.voiceover(text=N("short1.b5")) as tr:
            self.play(FadeOut(T), run_time=0.4)
            wait_until(self, tr, "every")
            self.play(FadeIn(VGroup(sbox, scroll), shift=DOWN * 0.3), run_time=0.7)
            self.play(FadeIn(plus), FadeIn(cs), run_time=0.6)
            rest(self, tr)

        nl = RealLine(-1.5, 2.5, length=7.0, y=MID - 2.6, x0=0, size=44, color=WEIRD,
                      labels={k: str(k) for k in range(-1, 3)})
        lens = Circle(radius=0.4, color=PRIMARY, stroke_width=4).move_to(nl.p(0))
        inset = RoundedRectangle(width=7.2, height=3.0, corner_radius=0.2, color=PRIMARY, stroke_width=4)
        inset.move_to([0, MID + 1.6, 0])
        zl = Line(inset.get_left() + RIGHT * 0.3, inset.get_right() + LEFT * 0.3, color=WEIRD, stroke_width=5)
        zl.shift(DOWN * 0.4)
        z0 = zl.get_left() + RIGHT * 0.8
        zero = VGroup(Line(z0 + UP * 0.15, z0 + DOWN * 0.15, color=WEIRD, stroke_width=4),
                      math("0", size=40, color=MUTED).next_to(z0, DOWN, 0.2))
        cloud = hyper_cloud(z0, scale=1.45)
        for p in cloud:
            p[0].scale(1.4)
            p[1].scale(1.4).next_to(p[0], UP, 0.2)
        conn = VGroup(Line(lens.get_top(), inset.get_corner(DL), color=PRIMARY, stroke_width=2),
                      Line(lens.get_top(), inset.get_corner(DR), color=PRIMARY, stroke_width=2))
        lab = text("an infinitesimal", size=56, color=PRIMARY, weight="BOLD").next_to(inset, UP, 0.4)
        with self.voiceover(text=N("short1.b6")) as tr:
            newsys = text("a new number system", size=46, color=WEIRD).next_to(nl, UP, 0.6)
            self.play(FadeOut(S), run_time=0.4)
            self.play(Create(nl), FadeIn(newsys), run_time=0.7)
            wait_until(self, tr, "c")
            self.play(FadeOut(newsys), run_time=0.3)
            wait_until(self, tr, "c")
            self.play(Create(lens), Create(conn), Create(inset), Create(zl), FadeIn(zero), run_time=0.8)
            self.play(LaggedStart(*[FadeIn(p, scale=1.5) for p in cloud], lag_ratio=0.25), run_time=1.0)
            self.play(FadeIn(lab), run_time=0.5)
            rest(self, tr)

        l1 = text("Leibniz, 1680s", size=52).move_to([0, SAFE_BOTTOM + 1.9, 0])
        l2 = text("\"ghosts\"", size=46, color=MUTED).next_to(l1, DOWN, 0.3)
        with self.voiceover(text=N("short1.b7")) as tr:
            self.play(FadeOut(nl), FadeOut(lens), FadeOut(conn), FadeIn(l1), run_time=0.6)
            wait_until(self, tr, "ghosts")
            self.play(FadeIn(l2), run_time=0.5)
            self.wait(rt(tr.get_remaining_duration() * 0.4))
            l3 = text("logic, 1960s", size=46, color=GOOD).move_to(l2)
            self.play(ReplacementTransform(l2, l3), run_time=0.6)
            rest(self, tr)
        self.wait(0.8)


class Short2Plane(VoiceoverScene):
    def construct(self):
        self.set_speech_service(get_speech_service())
        U = 1.9
        a = np.array([-1.6, MID + 1.0, 0])
        b = a + U * dirv(0.35)
        pair = VGroup(edge(a, b, color=FG, width=5), vdot(a, BAD, 0.17), vdot(b, SECONDARY, 0.17))
        one = labelled(pair[0], "1", direction=UP, size=52)
        q = lines("How many colors?", size=58, color=PRIMARY).move_to([0, MID - 1.8, 0])
        with self.voiceover(text=N("short2.b1")) as tr:
            self.play(Create(pair[0]), FadeIn(pair[1:]), FadeIn(one), run_time=0.6)
            wait_until(self, tr, "one")
            self.play(Indicate(pair[0], color=PRIMARY), run_time=0.6)
            self.wait(rt(tr.get_remaining_duration() - 1.2))
            self.play(FadeIn(q), run_time=0.5)
            rest(self, tr)

        tiling = hex_tiling(unit=U, side=0.45, radius=4.6, ymax=7.4)
        seven = text("7 is enough", size=60, color=FG, weight="BOLD")
        seven.add_background_rectangle(color=BG, opacity=0.85, buff=0.2)
        seven.move_to([0, MID, 0])
        with self.voiceover(text=N("short2.b2")) as tr:
            self.play(FadeOut(VGroup(pair, one, q)),
                      LaggedStart(*[FadeIn(h, scale=0.6) for h in tiling], lag_ratio=0.01), run_time=1.2)
            self.play(FadeIn(seven), run_time=0.4)
            rest(self, tr)

        A = np.array([0, MID - 3.0, 0])
        tri_p = [A, A + U * dirv(PI / 3), A + U * dirv(2 * PI / 3)]
        tri = VGroup(*[edge(tri_p[i], tri_p[(i + 1) % 3]) for i in range(3)])
        tri_d = VGroup(*[vdot(p, c, 0.17) for p, c in zip(tri_p, [BAD, SECONDARY, PRIMARY])])

        def diamond(theta):
            Bp, Cp, Dp = A + U * dirv(theta - PI / 6), A + U * dirv(theta + PI / 6), A + U * sqrt(3) * dirv(theta)
            es = VGroup(edge(A, Bp), edge(A, Cp), edge(Bp, Cp), edge(Bp, Dp), edge(Cp, Dp))
            ds = VGroup(vdot(A, BAD, 0.17), vdot(Bp, SECONDARY, 0.17), vdot(Cp, PRIMARY, 0.17), vdot(Dp, MUTED, 0.17))
            return VGroup(es, ds)
        dm = diamond(PI / 2)
        half = SPINDLE_PHI / 2
        D1 = A + U * sqrt(3) * dirv(PI / 2 + half)
        D2 = A + U * sqrt(3) * dirv(PI / 2 - half)
        top = edge(D1, D2, color=FG, width=7)
        four = text("at least 4", size=60, color=PRIMARY, weight="BOLD").move_to([0, SAFE_TOP - 0.6, 0])
        with self.voiceover(text=N("short2.b3")) as tr:
            self.play(FadeOut(tiling), FadeOut(seven), run_time=0.5)
            self.play(Create(tri), FadeIn(tri_d), run_time=0.8)
            wait_until(self, tr, "diamond")
            self.play(ReplacementTransform(tri, VGroup(*dm[0][:3])), ReplacementTransform(tri_d, VGroup(*dm[1][:3])),
                      run_time=0.6)
            self.play(Create(VGroup(*dm[0][3:])), FadeIn(dm[1][3]), run_time=0.5)
            self.play(dm[1][3].animate.set_color(BAD), run_time=0.4)
            wait_until(self, tr, "tops")
            dm2 = dm.copy()
            self.add(dm2)
            self.play(Rotate(dm, half, about_point=A), Rotate(dm2, -half, about_point=A), run_time=1.0)
            self.play(Create(top), run_time=0.4)
            self.play(top.animate.set_color(BAD), Indicate(dm[1][3], color=BAD, scale_factor=1.6),
                      Indicate(dm2[1][3], color=BAD, scale_factor=1.6), run_time=0.7)
            self.play(FadeIn(four), run_time=0.5)
            rest(self, tr)

        claim = VGroup(lines("the plane needs 5", size=48), math(r"\Downarrow", size=64),
                       lines("some finite set", "of points needs 5", size=48, color=PRIMARY)).arrange(DOWN, buff=0.35)
        claim.move_to([0, MID + 0.6, 0])
        name = text("the compactness theorem", size=40, color=MUTED).next_to(claim, DOWN, 0.6)
        with self.voiceover(text=N("short2.b4")) as tr:
            self.play(FadeOut(VGroup(dm, dm2, top, four)), run_time=0.5)
            self.play(FadeIn(claim[0]), run_time=0.5)
            wait_until(self, tr, "finite")
            self.play(FadeIn(claim[1:]), run_time=0.6)
            self.play(FadeIn(name), run_time=0.5)
            rest(self, tr)

        g = unit_graph(unit=0.62, center=[0, MID + 0.6, 0], rad=4.3, rots=(0.0, SPINDLE_PHI, 2 * SPINDLE_PHI))
        g_lab = text("1581 points, 2018", size=50, color=PRIMARY).next_to(g, UP, 0.35)
        g_note = text("(sketch)", size=30, color=MUTED).next_to(g, DOWN, 0.25)
        g2 = unit_graph(unit=0.62, center=[0, MID + 0.6, 0], rad=3.0, rots=(0.0, SPINDLE_PHI))
        g2_lab = text("509 points, 2020", size=50, color=PRIMARY).move_to(g_lab)
        with self.voiceover(text=N("short2.b5")) as tr:
            self.play(FadeOut(VGroup(claim, name)), run_time=0.4)
            wait_until(self, tr, "grey")
            self.play(Create(g[0]), FadeIn(g[1]), FadeIn(g_lab), FadeIn(g_note), run_time=1.2)
            wait_until(self, tr, "parts")
            self.play(ReplacementTransform(g, g2), ReplacementTransform(g_lab, g2_lab), run_time=1.0)
            rest(self, tr)

        bl = bounds_line(4, 8, y=MID - 0.4, length=7.0, marks=(5, 6, 7), shade=(5, 7), size=52)
        qm = text("?", size=110, color=PRIMARY, weight="BOLD").next_to(bl.shade, UP, 0.5)
        with self.voiceover(text=N("short2.b6")) as tr:
            self.play(FadeOut(VGroup(g2, g2_lab, g_note)), run_time=0.4)
            self.play(FadeIn(bl), run_time=0.6)
            self.play(FadeIn(qm, scale=1.3), run_time=0.5)
            rest(self, tr)
        self.wait(0.8)
