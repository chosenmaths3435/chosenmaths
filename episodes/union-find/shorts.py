"""Vertical shorts. Render with MV_ASPECT=portrait."""

import sys
from pathlib import Path

from manim import *
from manim_voiceover import VoiceoverScene

from mathvid import layout  # noqa: F401  must come before scene code runs
from mathvid.anim import rest, rt, wait_until
from mathvid.layout import FW, SAFE_BOTTOM, SAFE_TOP
from mathvid.script import Script
from mathvid.style import BAD, FG, GOOD, MUTED, PRIMARY, SECONDARY, math, text
from mathvid.voice import get_speech_service

sys.path.insert(0, str(Path(__file__).parent))
from scenes import (  # noqa: E402
    AlphaLine,
    Forest,
    Projection,
    ack_diagonal,
    binomial,
    clear,
    counter_text,
    freeze,
    plane_icon,
    poly_icon,
    rules,
    sort_letters,
    tall_tree,
    walk,
    word,
)

N = Script(__file__)

MID = (SAFE_TOP + SAFE_BOTTOM) / 2
TOP_Y = SAFE_TOP - 0.55
LOW_Y = SAFE_BOTTOM + 0.35


class Short1Equality(VoiceoverScene):
    def construct(self):
        self.set_speech_service(get_speech_service())
        a = word("listen", size=96).move_to([0, 3.6, 0])
        b = word("silent", size=96).move_to([0, 1.2, 0])
        sim = math(r"\sim", size=96).move_to([0, 2.4, 0])
        lab = text("anagrams", size=36, color=MUTED).move_to([0, -0.3, 0])
        eq = math("=", size=96, color=GOOD).move_to(sim)
        with self.voiceover(text=N("short1.b1")) as tr:
            self.play(FadeIn(a), FadeIn(b), FadeIn(sim), FadeIn(lab), run_time=0.6)
            wait_until(self, tr, "sort")
            self.play(*sort_letters(a, "listen", size=96), *sort_letters(b, "silent", size=96), run_time=1.4)
            self.play(ReplacementTransform(sim, eq), FadeOut(lab), run_time=0.6)
            rest(self, tr)

        rs = rules(size=54)
        rs.scale_to_fit_width(min(rs.width, FW - 0.8)).move_to([0, 2.2, 0])
        icons = VGroup()
        card = rs
        head = text("a rule for \"the same\"", size=40, color=PRIMARY).move_to([0, 4.4, 0])
        with self.voiceover(text=N("short1.b2")) as tr:
            self.play(FadeOut(VGroup(a, b, eq)), run_time=0.4)
            self.play(FadeIn(head), FadeIn(rs[0]), run_time=0.6)
            wait_until(self, tr, "rules")
            self.play(FadeIn(rs[1]), run_time=0.6)
            self.play(FadeIn(rs[2]), run_time=0.6)
            rest(self, tr)

        pj = Projection()
        arrows = pj.arrows()
        pic = VGroup(pj, arrows)
        pic.scale_to_fit_width(FW - 0.6).move_to([0, 1.4, 0])
        stmt = math(r"x \sim y", r"\iff", r"f(x) = f(y)", size=52).move_to([0, 4.4, 0])
        cl = VGroup(math(r"f(x)", size=40), text("= the class of x", size=36)).arrange(RIGHT, buff=0.15)
        cl.move_to([0, -1.6, 0])
        with self.voiceover(text=N("short1.b3")) as tr:
            self.play(FadeOut(VGroup(head, card)), run_time=0.4)
            self.play(FadeIn(pj), run_time=0.6)
            wait_until(self, tr, "f")
            self.play(Write(stmt), LaggedStart(*[Create(x) for x in arrows], lag_ratio=0.06), run_time=1.4)
            self.wait(rt(tr.get_remaining_duration() - 1.2))
            self.play(FadeIn(cl), run_time=0.6)
            rest(self, tr)

        r1 = VGroup(math("19", size=60), math(r"\longmapsto", size=56, color=MUTED), math("7", size=60, color=PRIMARY)
                    ).arrange(RIGHT, buff=0.4)
        r1n = text("remainder after dividing by 12", size=32, color=MUTED).next_to(r1, DOWN, buff=0.25)
        top = VGroup(r1, r1n).move_to([0, 4.1, 0])
        pl = plane_icon(size=30).move_to([-2.0, 1.4, 0])
        po = poly_icon(size=30).move_to([2.0, 1.5, 0])
        two_a = math("2", size=64, color=PRIMARY).move_to([-2.0, -1.2, 0])
        two_b = math("2", size=64, color=PRIMARY).move_to([2.0, -1.2, 0])
        a1 = Arrow(pl.get_bottom(), two_a.get_top(), color=MUTED, buff=0.15)
        a2 = Arrow(po.get_bottom(), two_b.get_top(), color=MUTED, buff=0.15)
        fd = VGroup(math("f", size=48), text("= dimension", size=40)).arrange(RIGHT, buff=0.2).move_to([0, -2.4, 0])
        with self.voiceover(text=N("short1.b4")) as tr:
            freeze(self)
            self.play(FadeOut(VGroup(pic, stmt, cl)), run_time=0.4)
            bf = text("usually there's a better f", size=44, color=PRIMARY).move_to([0, MID + 0.6, 0])
            self.play(FadeIn(bf), run_time=0.5)
            self.wait(rt(tr.time_until_bookmark("rem") - 0.5))
            self.play(FadeOut(bf), run_time=0.4)
            wait_until(self, tr, "rem")
            self.play(FadeIn(top), run_time=0.6)
            self.play(FadeIn(pl), FadeIn(po), run_time=0.6)
            wait_until(self, tr, "dim")
            self.play(GrowArrow(a1), GrowArrow(a2), FadeIn(two_a), FadeIn(two_b), run_time=0.8)
            self.play(FadeIn(fd), run_time=0.5)
            rest(self, tr)

        fin = VGroup(text("every kind of \"same\"", size=48),
                     text("is equality,", size=48),
                     text("once you look at", size=48, color=PRIMARY),
                     text("the right thing", size=48, color=PRIMARY)).arrange(DOWN, buff=0.3).move_to([0, MID + 0.6, 0])
        with self.voiceover(text=N("short1.b5")) as tr:
            freeze(self)
            self.play(FadeOut(Group(*self.mobjects)), run_time=0.4)
            self.play(LaggedStart(*[FadeIn(x, shift=UP * 0.2) for x in fin], lag_ratio=0.25), run_time=1.4)
            rest(self, tr)
        self.wait(0.4)


class Short2ShortTrees(VoiceoverScene):
    def construct(self):
        self.set_speech_service(get_speech_service())
        parent = {0: 0, 1: 0, 2: 1, 3: 3, 4: 3, 5: 5, 6: 6}
        fo = Forest(parent, order=[0, 1, 2, 3, 4, 5, 6], top=3.8, dx=1.0, dy=1.3, r=0.36, size=32)
        with self.voiceover(text=N("short2.b1")) as tr:
            self.add(fo)
            self.play(FadeIn(fo), run_time=0.6)
            wait_until(self, tr, "ptr")
            self.play(*[Circumscribe(fo.nodes[k], shape=Circle, color=GOOD, buff=0.08) for k in fo.roots()], run_time=0.8)
            self.wait(rt(tr.get_remaining_duration() * 0.25))
            path, ring = walk(self, fo, 2, step_time=0.4)
            self.play(FadeOut(ring), *[fo.color_node(k, FG) for k in path], run_time=0.3)
            fo.ptr_color[3] = PRIMARY
            fo.reparent(3, 0)
            self.play(*fo.moves(), run_time=0.9)
            rest(self, tr)

        n = 9
        chain = Forest({i: i for i in range(n)}, order=list(range(n)), labels=False, r=0.22, dx=0.8, dy=0.85,
                       top=4.6, tree_gap=0.2)
        cnt = ValueTracker(0)
        ctr = counter_text("steps:", cnt, [2.4, -1.8, 0], size=40)
        with self.voiceover(text=N("short2.b2")) as tr:
            freeze(self)
            self.play(FadeOut(fo), run_time=0.3)
            self.add(chain)
            self.play(FadeIn(VGroup(*chain.nodes.values())), run_time=0.3)
            wait_until(self, tr, "chain")
            for i in range(n - 1):
                chain.reparent(i, i + 1)
                self.play(*chain.moves(), run_time=0.18)
            self.add(ctr)
            walk(self, chain, 0, step_time=0.18, counter=cnt)
            rest(self, tr)

        _, p2, n2 = binomial(2, 0)
        _, p1, n1 = binomial(1, n2)
        par = {**p2, **p1}
        rk = {k: 0 for k in par}
        rk[0], rk[n2] = 2, 1
        f1 = Forest(par, labels=False, r=0.3, dx=1.0, dy=1.2, top=3.7, rank=rk, rank_on=1.0, tree_gap=1.4)
        rl = text("rank = height", size=36, color=MUTED).move_to([0, 5.1, 0])
        with self.voiceover(text=N("short2.b3")) as tr:
            freeze(self)
            self.play(FadeOut(Group(*self.mobjects)), run_time=0.3)
            self.add(f1)
            self.play(FadeIn(f1), FadeIn(rl), run_time=0.5)
            wait_until(self, tr, "short")
            f1.ptr_color[n2] = PRIMARY
            f1.reparent(n2, 0)
            self.play(*f1.moves(), run_time=0.9)
            wait_until(self, tr, "tie")
            _, a, na = binomial(2, 0)
            _, b, nb = binomial(2, na)
            pr = {**a, **b}
            rk2 = {k: 0 for k in pr}
            rk2[0], rk2[na] = 2, 2
            f2 = Forest(pr, labels=False, r=0.26, dx=0.8, dy=1.1, top=3.7, rank=rk2, rank_on=1.0, tree_gap=1.0)
            freeze(self)
            self.play(FadeOut(f1), run_time=0.3)
            self.add(f2)
            self.play(FadeIn(f2), run_time=0.4)
            f2.ptr_color[na] = PRIMARY
            f2.reparent(na, 0)
            self.play(*f2.moves(), run_time=0.8)
            f2.rank[0] = 3
            self.play(f2.nodes[0][0].animate.set_stroke(PRIMARY, width=6), run_time=0.4)
            rest(self, tr)

        trees = []
        spots = [(-2.3, 4.6), (1.6, 4.6), (-2.0, 1.4), (1.9, 1.4)]
        for k, (x, y) in zip(range(4), spots):
            _, pk, nk = binomial(k, 0)
            r_ = {i: 0 for i in pk}
            r_[0] = k
            trees.append(Forest(pk, labels=False, r=0.2, dx=0.62, dy=0.75, top=y, cx=x, rank=r_, rank_on=1.0,
                                loops=False))
        cnts = VGroup(*[text(f"at least {2 ** k}", size=32).move_to([x, y - (k + 1) * 0.75 - 0.1, 0])
                        for k, (x, y) in zip(range(4), spots)])
        with self.voiceover(text=N("short2.b4")) as tr:
            freeze(self)
            self.play(FadeOut(Group(*self.mobjects)), run_time=0.3)
            for t in trees:
                self.add(t)
            self.play(*[FadeIn(t) for t in trees], run_time=0.6)
            wait_until(self, tr, "nodes")
            self.play(LaggedStart(*[FadeIn(c) for c in cnts], lag_ratio=0.2), run_time=1.0)
            t3 = trees[3]
            self.play(*[t3.nodes[k][0].animate.set_stroke(SECONDARY) for k in t3.order if k >= 4],
                      *[t3.nodes[k][0].animate.set_stroke(PRIMARY) for k in t3.order if k < 4], run_time=0.6)
            plus = math(r"4 + 4 = 8", size=48, color=PRIMARY).move_to([0, -2.5, 0])
            self.play(FadeIn(plus), run_time=0.4)
            rest(self, tr)

        l1 = VGroup(text("n items", size=48), math(r"\Downarrow", size=52, color=MUTED),
                    VGroup(text("height at most", size=48), math(r"\log_2 n", size=56)).arrange(RIGHT, buff=0.25)
                    ).arrange(DOWN, buff=0.3)
        l2 = VGroup(math(r"1{,}000{,}000", size=56), text("items", size=44)).arrange(RIGHT, buff=0.25)
        l3 = text("at most 20 steps", size=52, color=PRIMARY)
        blk = VGroup(l1, l2, l3).arrange(DOWN, buff=0.7).move_to([0, MID + 0.6, 0])
        with self.voiceover(text=N("short2.b5")) as tr:
            freeze(self)
            self.play(FadeOut(Group(*self.mobjects)), run_time=0.3)
            self.play(FadeIn(l1), run_time=0.8)
            self.play(FadeIn(l2), run_time=0.6)
            wait_until(self, tr, "twenty")
            self.play(FadeIn(l3, scale=1.2), run_time=0.3)
            rest(self, tr)
        self.wait(1.5)


class Short3Alpha(VoiceoverScene):
    def construct(self):
        self.set_speech_service(get_speech_service())
        parent, order = tall_tree()
        fo = Forest(parent, order=order, labels=False, r=0.26, dx=0.72, dy=1.0, top=4.6)
        with self.voiceover(text=N("short3.b1")) as tr:
            self.add(fo)
            self.play(FadeIn(fo), run_time=0.6)
            self.wait(rt(tr.time_until_bookmark("flat") - 2.6))
            path, ring = walk(self, fo, 5, step_time=0.4)
            wait_until(self, tr, "flat")
            for k in path[:-1]:
                if fo.parent[k] != 0:
                    fo.ptr_color[k] = PRIMARY
                fo.reparent(k, 0)
            self.play(*fo.moves(), ring.animate.move_to(fo.layout()[0]), run_time=1.0)
            self.play(FadeOut(ring), *[fo.color_node(k, FG) for k in path], run_time=0.3)
            rest(self, tr)

        s1 = text("m operations on n items:", size=40)
        s2 = text("time at most proportional to", size=40)
        s3 = math(r"m \cdot \alpha(n)", size=72, color=PRIMARY)
        s4 = VGroup(math(r"\alpha", size=52, color=PRIMARY), text("= inverse Ackermann", size=40)).arrange(RIGHT, buff=0.2)
        stmt = VGroup(s1, s2, s3, s4).arrange(DOWN, buff=0.4).move_to([0, MID + 0.6, 0])
        with self.voiceover(text=N("short3.b2")) as tr:
            freeze(self)
            self.play(FadeOut(fo), FadeIn(s1), FadeIn(s2), run_time=0.6)
            wait_until(self, tr, "bound")
            self.play(FadeIn(s3, scale=1.2), run_time=0.6)
            self.play(FadeIn(s4), run_time=0.6)
            rest(self, tr)

        diag = ack_diagonal(size=52).move_to([0, 2.0, 0])
        dh = text("Ackermann's function", size=40, color=MUTED).next_to(diag, UP, buff=0.5)
        with self.voiceover(text=N("short3.b3")) as tr:
            self.play(FadeOut(stmt), run_time=0.4)
            self.play(FadeIn(dh), run_time=0.4)
            for row in diag[:4]:
                self.play(FadeIn(row), run_time=0.45)
            wait_until(self, tr, "tower")
            self.play(FadeIn(diag[4], scale=1.2), run_time=0.8)
            rest(self, tr)

        df = VGroup(math(r"\alpha(n) = \text{the smallest } k", size=48),
                    math(r"\text{with } A(k, k) \ge n", size=48)).arrange(DOWN, buff=0.2).move_to([0, 4.4, 0])
        al = AlphaLine(xs=(-3.6, -3.0, -2.4, -1.75, -1.0, 3.2), y=1.4, size=32, big=56)
        atoms_x = al.xs[4] + 0.45
        atoms = VGroup(Line([atoms_x, 1.25, 0], [atoms_x, 1.55, 0], color=SECONDARY, stroke_width=3),
                       VGroup(math(r"10^{80}", size=34, color=SECONDARY),
                              text("atoms in the universe", size=30, color=SECONDARY)).arrange(DOWN, buff=0.1))
        atoms[1].move_to([0.9, -0.2, 0])
        lead = Line(atoms[1].get_top(), [atoms_x, 1.2, 0], color=SECONDARY, stroke_width=2)
        with self.voiceover(text=N("short3.b4")) as tr:
            freeze(self)
            self.play(FadeOut(VGroup(diag, dh)), run_time=0.4)
            self.play(FadeIn(df), run_time=0.8)
            self.play(Create(al.segs[:4]), FadeIn(al.ticks[:5]), FadeIn(al.nums[:5]), FadeIn(al.vals[:4]), run_time=1.0)
            wait_until(self, tr, "four")
            self.play(Create(al.segs[4]), FadeIn(al.ticks[5]), FadeIn(al.nums[5]), run_time=1.2)
            self.play(FadeIn(al.vals[4], scale=1.4), run_time=0.5)
            self.play(FadeIn(atoms), Create(lead), run_time=0.6)
            rest(self, tr)

        more = Line([al.xs[5], 1.4, 0], [FW / 2 + 0.5, 1.4, 0], color=BAD, stroke_width=6)
        five = math("5", size=44, color=BAD).next_to(more, UP, buff=0.25)
        inf = math(r"\alpha(n) \to \infty", size=60, color=BAD).move_to([0, -1.4, 0])
        fs = VGroup(text("no data structure does better,", size=36),
                    text("beyond a constant factor", size=36)).arrange(DOWN, buff=0.15).move_to([0, -2.6, 0])
        with self.voiceover(text=N("short3.b5")) as tr:
            self.play(FadeOut(VGroup(atoms, lead)), run_time=0.3)
            wait_until(self, tr, "grows")
            self.play(Create(more), FadeIn(five), run_time=0.7)
            self.play(Write(inf), run_time=0.8)
            self.wait(rt(tr.get_remaining_duration() * 0.3))
            self.play(FadeIn(fs), run_time=0.6)
            rest(self, tr)
        self.wait(0.4)
