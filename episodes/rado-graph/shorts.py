"""Vertical shorts. Render with MV_ASPECT=portrait."""

import sys
from math import cos, sin
from pathlib import Path

import numpy as np
from manim import *
from manim_voiceover import VoiceoverScene

from mathvid import layout  # noqa: F401  must come before scene code runs
from mathvid.anim import rest, rt, wait_until
from mathvid.layout import SAFE_BOTTOM, SAFE_TOP
from mathvid.orders import cross, tick
from mathvid.script import Script
from mathvid.style import BAD, FG, GOOD, MUTED, PRIMARY, math, text
from mathvid.voice import get_speech_service

sys.path.insert(0, str(Path(__file__).parent))
from scenes import (  # noqa: E402
    MATCHED,
    Game,
    Net,
    bit_edges,
    binary_row,
    cloud_points,
    coin,
    coin_edges,
    face_mob,
    fill_anim,
    flip,
    key,
    pair_order,
    paley_edges,
    paley_pts,
    rim_points,
    wish_bubble,
)

N = Script(__file__)

MID = (SAFE_TOP + SAFE_BOTTOM) / 2  # center of the safe area


def portrait_net(center, n0=8, extra=6, seed=0, rx=2.3, ry=1.55, min_d=0.85):
    core = cloud_points(n0, center, rx, ry, seed=seed, min_d=min_d)
    rim = rim_points(extra, center, rx + 0.55, ry + 0.45, seed=seed + 1, phase=0.4)
    pts = core + rim
    net = Net(pts, coin_edges(len(pts), seed=seed + 2), r=0.12, ewidth=2.4, eopacity=0.7)
    for k in range(n0, len(pts)):
        net.ds[k].set_opacity(0.0)
    return net, n0


class Short1OneRandomGraph(VoiceoverScene):
    def construct(self):
        self.set_speech_service(get_speech_service())
        top_c, bot_c = np.array([-0.3, 3.75, 0]), np.array([-0.3, -1.05, 0])
        A, n0 = portrait_net(top_c, seed=3)
        B, _ = portrait_net(bot_c, seed=17)
        A.hide_lines()
        B.hide_lines()
        cA = coin("H", r=0.36).move_to(top_c + RIGHT * 3.05 + UP * 1.3)
        cB = coin("H", r=0.36).move_to(bot_c + RIGHT * 3.05 + UP * 1.3)
        with self.voiceover(text=N("short1.b1")) as tr:
            self.add(A.lg, B.lg)
            self.play(FadeIn(VGroup(*A.ds[:n0]), lag_ratio=0.1), FadeIn(cA), run_time=0.6)
            t = tr.get_remaining_duration()
            self.play(fill_anim(A, pair_order(0, n0, seed=2), cA), run_time=rt(t * 0.5))
            self.play(FadeIn(VGroup(*B.ds[:n0]), lag_ratio=0.1), FadeIn(cB), run_time=0.5)
            self.play(fill_anim(B, pair_order(0, n0, seed=3), cB), run_time=rt(tr.get_remaining_duration()))

        eq = math("=", size=110, color=PRIMARY).move_to([-1.0, (top_c[1] + bot_c[1]) / 2, 0])
        prob = text("with probability 1", size=30, color=MUTED).next_to(eq, RIGHT, 0.35)
        with self.voiceover(text=N("short1.b2")) as tr:
            rims = [A.ds[k].animate.set_opacity(0.55) for k in range(n0, len(A.pts))]
            rims += [B.ds[k].animate.set_opacity(0.55) for k in range(n0, len(B.pts))]
            self.play(*rims, run_time=0.4)
            t = tr.time_until_bookmark("same")
            self.play(fill_anim(A, pair_order(n0, len(A.pts), seed=4), cA),
                      fill_anim(B, pair_order(n0, len(B.pts), seed=5), cB), run_time=rt(t - 0.4))
            wait_until(self, tr, "same")
            self.play(FadeIn(eq, scale=1.4), FadeIn(prob), run_time=0.5)
            rest(self, tr)

        # One graph, a wish.
        gc = np.array([0, 3.5, 0])
        G = Net(cloud_points(13, gc, 2.8, 1.7, seed=41, min_d=0.75), coin_edges(13, 42), r=0.12, ewidth=2,
                eopacity=0.5)
        g1, g2, r1 = 2, 6, 9
        wb = wish_bubble(size=34).move_to([0, 0.35, 0])
        with self.voiceover(text=N("short1.b3")) as tr:
            self.play(FadeOut(VGroup(A, B, cA, cB, eq, prob)), run_time=0.4)
            self.play(FadeIn(G), run_time=0.6)
            wait_until(self, tr, "colors")
            self.play(G.ds[g1].animate.set_color(GOOD).scale(1.6), G.ds[g2].animate.set_color(GOOD).scale(1.6),
                      G.ds[r1].animate.set_color(BAD).scale(1.6), run_time=0.6)
            self.play(FadeIn(wb, shift=UP * 0.2), run_time=0.6)
            rest(self, tr)

        P = [np.array([-2.6, 0.8, 0]), np.array([-2.6, -0.45, 0]), np.array([-2.6, -1.7, 0])]
        cols = [GOOD, GOOD, BAD]
        need = ["H", "H", "T"]
        panel = VGroup(*[Dot(p, radius=0.17, color=c) for p, c in zip(P, cols)])
        cand_p = np.array([2.3, -0.45, 0])
        cand = Dot(cand_p, radius=0.17, color=FG)
        paths = VGroup(*[DashedLine(cand_p, p, color=MUTED, stroke_width=2.5, dash_length=0.12) for p in P])
        coins = [coin("T", r=0.27).move_to(interpolate(cand_p, p, 0.45) + UP * 0.42) for p in P]
        each = math(r"\tfrac18 \text{ each}", size=44, color=PRIMARY).move_to([0, -2.65, 0])
        fails = [("T", "H", "H"), ("H", "T", "T"), ("T", "T", "T"), ("H", "H", "H"), ("T", "H", "T")]
        with self.voiceover(text=N("short1.b4")) as tr:
            self.play(FadeOut(wb), TransformFromCopy(VGroup(G.ds[g1], G.ds[g2], G.ds[r1]), panel),
                      FadeIn(cand), run_time=0.6)
            self.play(Create(paths), FadeIn(VGroup(*coins)), FadeIn(each), run_time=0.5)
            t = tr.time_until_bookmark("fail")
            per = max(0.3, (t - 0.2) / len(fails))
            marks = VGroup()
            for f in fails:
                for cn, ff in zip(coins, f):
                    cn[1].become(face_mob(ff, cn.r).move_to(cn[0]))
                res = VGroup(*[Line(cand_p, p, color=FG, stroke_width=4) for p, ff in zip(P, f) if ff == "H"])
                mk = cross(cand_p + DOWN * 0.6, s=0.16)
                self.add(res, mk)
                self.wait(per)
                self.remove(res, mk)
            wait_until(self, tr, "fail")
            for cn, ff in zip(coins, need):
                cn[1].become(face_mob(ff, cn.r).move_to(cn[0]))
            res = VGroup(*[Line(cand_p, p, color=FG, stroke_width=4) for p, ff in zip(P, need) if ff == "H"])
            tk = tick(at=cand_p + DOWN * 0.6, s=1.3)
            zero = VGroup(text("chance all fail:", size=32), math("0", size=48, color=PRIMARY)).arrange(RIGHT, buff=0.25)
            zero.move_to(each)
            self.play(FadeIn(res), Create(tk), ReplacementTransform(each, zero), run_time=0.6)
            rest(self, tr)

        g = Game(centers=((0, 3.55, 0), (0, -0.75, 0)), radius=1.55, label_size=22, titles=())
        with self.voiceover(text=N("short1.b5")) as tr:
            self.play(FadeOut(VGroup(G, panel, cand, paths, *coins, res, tk, zero)), run_time=0.4)
            self.play(FadeIn(g.base()), run_time=0.6)
            t = tr.time_until_bookmark("match")
            turns = g.turns
            g.quick_step(self, turns[0], run_time=0.6)
            self.wait(max(0, (t - 3.6) * 0.4))
            g.quick_step(self, turns[1], run_time=0.6)
            self.wait(max(0, (t - 3.6) * 0.3))
            # One turn in detail: color the matched dots, carry the colors, grant.
            side, a, b = turns[2]
            A_, B_ = g.nets[side], g.nets[1 - side]
            cols = g.colors_for(side, a)
            self.play(*[A_.ds[m].animate.set_color(c).scale(1.4) for m, c in cols.items()],
                      Flash(A_.ds[a], color=PRIMARY, flash_radius=0.3), run_time=0.6)
            self.play(*[B_.ds[g.matched[side][m]].animate.set_color(c).scale(1.4) for m, c in cols.items()],
                      run_time=0.5)
            wait_until(self, tr, "match")
            g.quick_step(self, turns[2], run_time=0.6)
            self.play(*[A_.ds[m].animate.set_color(MATCHED).scale(1 / 1.4) for m in cols],
                      *[B_.ds[g.matched[side][m]].animate.set_color(MATCHED).scale(1 / 1.4) for m in cols],
                      run_time=0.3)
            rest_turns = turns[3:]
            budget = tr.get_remaining_duration() - 0.2
            for t_ in rest_turns:
                g.quick_step(self, t_, run_time=max(0.15, budget / len(rest_turns)))
            rest(self, tr)

        one = Net(paley_pts(center=[0, 2.0, 0], rx=2.9, ry=2.9, seed=61), paley_edges(), r=0.13, ewidth=2.4,
                  eopacity=0.7)
        lab = VGroup(text("There's one.", size=48, weight="BOLD"),
                     text("the Rado graph", size=40, color=PRIMARY)).arrange(DOWN, buff=0.2).move_to([0, -2.0, 0])
        with self.voiceover(text=N("short1.b6")) as tr:
            self.play(FadeOut(g.threads), g.nets[0].animate.move_to([0, 2.0, 0]).set_opacity(0.0),
                      g.nets[1].animate.move_to([0, 2.0, 0]).set_opacity(0.0), FadeIn(one), run_time=1.0)
            wait_until(self, tr, "one")
            self.play(FadeIn(lab, shift=UP * 0.2), run_time=0.6)
            rest(self, tr)
        self.wait(0.5)


def spiral_points(n, center, r0=0.75, dr=0.17, dtheta=0.78):
    c = np.array(center, dtype=float)
    return [c + (r0 + dr * k) * np.array([cos(PI / 2 - dtheta * k), sin(PI / 2 - dtheta * k), 0]) for k in range(n)]


def bit_spiral(center, n=16):
    pts = spiral_points(n, center)
    net = Net(pts, bit_edges(n), r=0.11, ewidth=2.0, eopacity=0.55, labels=True, label_size=22,
              label_center=center, label_buff=0.32)
    return net


class Short2NoCoins(VoiceoverScene):
    def construct(self):
        self.set_speech_service(get_speech_service())
        sc = np.array([0, 2.0, 0])
        S = bit_spiral(sc)
        last = S.pts[-1]
        more = text("...", size=48, color=MUTED).move_to(last + (last - sc) / np.linalg.norm(last - sc) * 0.75
                                                          + RIGHT * 0.2)
        with self.voiceover(text=N("short2.b1")) as tr:
            self.play(FadeIn(S.ds, lag_ratio=0.05), FadeIn(S.lab, lag_ratio=0.05), run_time=0.8)
            self.play(Create(S.lg, lag_ratio=0.02), FadeIn(more), run_time=rt(min(2.0, tr.duration - 1.2)))
            rest(self, tr)

        rule = VGroup(text("k joins a bigger m when m,", size=34),
                      text("in binary, has a 1 in position k", size=34)).arrange(DOWN, buff=0.1)
        rule.move_to([0, SAFE_TOP - 0.75, 0])
        b13 = binary_row("1101", size=60).move_to([0.9, -2.45, 0])
        lhs = math("13", "=", size=64).next_to(b13.digs, LEFT, 0.35)
        hl = VGroup(*[S.make_line(13, k, color=PRIMARY, width=5, opacity=1) for k in (0, 2, 3)])
        with self.voiceover(text=N("short2.b2")) as tr:
            self.play(S.animate.shift(DOWN * 0.6), more.animate.shift(DOWN * 0.6), FadeIn(rule), run_time=0.6)
            hl = VGroup(*[S.make_line(13, k, color=PRIMARY, width=5, opacity=1) for k in (0, 2, 3)])
            wait_until(self, tr, "bin")
            self.play(FadeIn(lhs), FadeIn(b13), S.ds[13].animate.set_color(PRIMARY).scale(1.5), run_time=0.7)
            hi = [0, 1, 3]
            self.play(*[b13.digs[k].animate.set_color(PRIMARY) for k in hi],
                      *[b13.pos[k].animate.set_color(PRIMARY) for k in hi], run_time=0.6)
            t = tr.get_remaining_duration()
            self.play(Create(hl, lag_ratio=0.3), *[S.ds[k].animate.set_color(PRIMARY) for k in (0, 2, 3)],
                      run_time=rt(min(1.4, t * 0.6)))
            rest(self, tr)

        gc = np.array([0, 3.4, 0])
        G = Net(cloud_points(13, gc, 2.8, 1.8, seed=44, min_d=0.75), coin_edges(13, 45), r=0.12, ewidth=2,
                eopacity=0.5)
        greens, reds = (1, 7), (4, 10)
        wb = wish_bubble(size=34).move_to([0, 0.1, 0])
        with self.voiceover(text=N("short2.b3")) as tr:
            self.play(FadeOut(VGroup(S, more, rule, b13, lhs, hl)), run_time=0.4)
            self.play(FadeIn(G), run_time=0.6)
            self.play(*[G.ds[i].animate.set_color(GOOD).scale(1.6) for i in greens],
                      *[G.ds[i].animate.set_color(BAD).scale(1.6) for i in reds], run_time=0.6)
            wait_until(self, tr, "wish")
            self.play(FadeIn(wb, shift=UP * 0.2), run_time=0.5)
            # Try candidates until one works.
            cands = [i for i in range(13) if i not in greens + reds]
            good = [i for i in cands if all(G.adj(i, x) for x in greens) and not any(G.adj(i, x) for x in reds)]
            order = [i for i in cands if i not in good][:4] + good[:1]
            t = tr.get_remaining_duration()
            per = max(0.3, (t - 0.4) / len(order))
            for i in order:
                ok = i in good
                mk = tick(at=G.pts[i] + RIGHT * 0.35, s=1.0) if ok else cross(G.pts[i] + RIGHT * 0.3, s=0.13)
                self.play(Flash(G.ds[i], color=GOOD if ok else BAD, flash_radius=0.3), Create(mk), run_time=rt(per * 0.6))
                self.wait(per * 0.4)
                if not ok:
                    self.remove(mk)
            rest(self, tr)

        rxs = [-2.7, -1.5, -0.3, 0.9, 2.1]
        ry = -2.1
        rdots = VGroup(*[Dot([x, ry, 0], radius=0.15, color=c) for x, c in zip(rxs, [GOOD, BAD, BAD, BAD, MUTED])])
        rnums = VGroup(*[text(str(k), size=30, color=MUTED).next_to(rdots[k], DOWN, 0.22) for k in range(5)])
        slot_x = [-2.6 + k * 1.0 for k in range(5)]
        sy = 4.4
        slots = VGroup(*[Line([x - 0.37, sy - 0.45, 0], [x + 0.37, sy - 0.45, 0], color=MUTED, stroke_width=4)
                         for x in slot_x])
        spos = VGroup(*[text(str(4 - k), size=26, color=MUTED).move_to([slot_x[k], sy - 0.85, 0]) for k in range(5)])
        dcol = [PRIMARY, BAD, BAD, BAD, GOOD]
        dmobs = VGroup(*[math(d, size=64, color=c).move_to([slot_x[k], sy, 0])
                         for k, (d, c) in enumerate(zip("10001", dcol))])
        eq17 = math("=", "17", size=60, color=PRIMARY).next_to(dmobs[4], DOWN, 0.9).set_x(0)
        d17 = Dot([0.6, 1.0, 0], radius=0.16, color=PRIMARY)
        l17 = text("17", size=32, color=PRIMARY).next_to(d17, RIGHT, 0.2)
        e0 = Line(d17.get_center(), rdots[0].get_center(), color=GOOD, stroke_width=5)
        e4 = Line(d17.get_center(), rdots[4].get_center(), color=MUTED, stroke_width=3)
        with self.voiceover(text=N("short2.b4")) as tr:
            self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.4)
            self.play(FadeIn(rdots[:4]), FadeIn(rnums[:4]), FadeIn(slots[1:]), FadeIn(spos[1:]), run_time=0.5)
            wait_until(self, tr, "fill")
            self.play(LaggedStart(*[FadeIn(dmobs[k], shift=DOWN * 0.2) for k in (4, 1, 2, 3)], lag_ratio=0.35),
                      run_time=1.2)
            t = tr.get_remaining_duration()
            self.play(FadeIn(slots[0]), FadeIn(spos[0]), FadeIn(dmobs[0], shift=DOWN * 0.2), run_time=0.6)
            self.wait(max(0, t * 0.25))
            self.play(FadeIn(eq17), run_time=0.5)
            self.play(FadeIn(rdots[4]), FadeIn(rnums[4]), FadeIn(d17), FadeIn(l17), Create(e0), Create(e4),
                      run_time=0.8)
            rest(self, tr)

        top = bit_spiral(np.array([0, 3.6, 0]))
        top.scale(0.6).move_to([0, 3.35, 0])
        bot = Net(cloud_points(13, [0, -1.1, 0], 2.6, 1.5, seed=46, min_d=0.7), coin_edges(13, 47), r=0.1, ewidth=1.8,
                  eopacity=0.55)
        eq = math("=", size=90, color=PRIMARY).move_to([-1.0, 1.25, 0])
        prob = text("with probability 1", size=26, color=MUTED).next_to(eq, RIGHT, 0.3)
        granted = text("every wish, granted", size=40, color=GOOD).move_to([0, SAFE_TOP - 0.15, 0])
        bot_lab = text("coin flips", size=28, color=MUTED).next_to(bot, LEFT, 0.1).shift(UP * 1.2)
        top_lab = text("the recipe", size=28, color=MUTED).next_to(top, LEFT, 0.1).shift(UP * 1.0)
        with self.voiceover(text=N("short2.b5")) as tr:
            self.play(FadeOut(VGroup(rdots, rnums, slots, spos, dmobs, eq17, d17, l17, e0, e4)), run_time=0.4)
            self.play(FadeIn(top), FadeIn(top_lab), FadeIn(granted), run_time=0.7)
            t = tr.time_until_bookmark("same")
            self.wait(max(0, t * 0.3))
            self.play(FadeIn(bot), FadeIn(bot_lab), run_time=0.7)
            wait_until(self, tr, "same")
            self.play(FadeIn(eq, scale=1.4), FadeIn(prob), run_time=0.6)
            rest(self, tr)
        self.wait(0.5)
