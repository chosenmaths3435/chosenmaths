"""Vertical shorts. Render with MV_ASPECT=portrait."""

import sys
from pathlib import Path

import numpy as np
from manim import *
from manim_voiceover import VoiceoverScene

from mathvid import layout  # noqa: F401  must come before scene code runs
from mathvid.anim import rest, rt, wait_until
from mathvid.layout import SAFE_BOTTOM, SAFE_TOP
from mathvid.script import Script
from mathvid.style import BG, FG, GOOD, MUTED, PRIMARY, SECONDARY, text
from mathvid.voice import get_speech_service

sys.path.insert(0, str(Path(__file__).parent))
from scenes import (  # noqa: E402
    C5,
    LINE_S,
    P,
    SECRET,
    Y0,
    ModGrid,
    curve,
    interp,
    line_f,
    managers,
    mod_line,
    mod_para_through,
    mod_poly_dots,
    mth,
    open_door,
    para_f,
    pdot,
    plane,
    poly,
    vault,
)

N = Script(__file__)

MID = (SAFE_TOP + SAFE_BOTTOM) / 2  # center of the safe area


def lines(*ss, size=52, color=FG, buff=0.18):
    return VGroup(*[text(s, size=size, color=color) for s in ss]).arrange(DOWN, buff=buff)


def tall_plane():
    return plane(x_length=6.4, y_length=5.6, size=34).move_to([0.25, MID - 0.3, 0])


class Short1Line(VoiceoverScene):
    def construct(self):
        self.set_speech_service(get_speech_service())
        v = vault(3.0).move_to([0, MID + 2.4, 0])
        mg = managers(5, s=1.4, buff=0.45).move_to([0, MID - 0.6, 0])
        a, b = np.array([-2.2, MID - 2.6, 0]), np.array([2.2, MID - 1.2, 0])
        da, db = Dot(a, radius=0.16, color=PRIMARY), Dot(b, radius=0.16, color=SECONDARY)
        ln = Line(a + (a - b) * 0.35, b + (b - a) * 0.35, color=FG, stroke_width=6)
        with self.voiceover(text=N("short1.b1")) as tr:
            self.play(FadeIn(v), LaggedStart(*[FadeIn(m, shift=UP * 0.2) for m in mg], lag_ratio=0.15),
                      run_time=1.0)
            self.play(*[mg[i].animate.set_opacity(0.25) for i in (0, 2, 4)], run_time=0.5)
            self.play(open_door(v), run_time=0.7)
            wait_until(self, tr, "line")
            self.play(mg.animate.shift(UP * 0.6).set_opacity(0.0), FadeIn(da, scale=0.5), FadeIn(db, scale=0.5),
                      run_time=0.5)
            self.play(Create(ln), run_time=rt(min(0.9, tr.get_remaining_duration())))
            rest(self, tr)

        pg = tall_plane()
        ax = pg.ax
        sdot = pdot(ax, 0, LINE_S, SECRET, r=0.16)
        slab = text("secret", size=42, color=SECRET).next_to(sdot, DR, 0.12)
        line = curve(ax, line_f, FG, 5)
        pts = VGroup(*[pdot(ax, x, line_f(x), C5[x - 1], r=0.14) for x in range(1, 6)])
        with self.voiceover(text=N("short1.b2")) as tr:
            self.play(FadeOut(VGroup(v, mg, da, db, ln)), run_time=0.5)
            self.play(FadeIn(pg), FadeIn(sdot, scale=0.5), FadeIn(slab), run_time=0.8)
            wait_until(self, tr, "random")
            self.play(Create(line), run_time=0.8)
            self.play(LaggedStart(*[FadeIn(p, scale=0.5) for p in pts], lag_ratio=0.25),
                      run_time=rt(min(1.6, tr.get_remaining_duration())))
            rest(self, tr)

        keep = (1, 3)
        l2 = curve(ax, line_f, GOOD, 6)
        ring = Circle(radius=0.32, color=GOOD, stroke_width=6).move_to(sdot)
        with self.voiceover(text=N("short1.b3")) as tr:
            self.play(FadeOut(line), FadeOut(sdot), FadeOut(slab),
                      *[pts[i].animate.set_opacity(0.15) for i in range(5) if i not in keep], run_time=0.6)
            wait_until(self, tr, "draw")
            self.play(Create(l2), run_time=0.8)
            self.play(FadeIn(sdot, scale=0.5), Create(ring), run_time=0.5)
            rest(self, tr)

        px, py = 2, line_f(2)
        fan, hits = VGroup(), VGroup()
        for s in np.arange(0, 12.01, 1.0):
            m = (py - s) / px
            fan.add(curve(ax, lambda x, s=s, m=m: s + m * x, SECONDARY, 3, opacity=0.55))
            hits.add(pdot(ax, 0, s, SECRET, r=0.08))
        with self.voiceover(text=N("short1.b4")) as tr:
            self.play(FadeOut(l2), FadeOut(ring), FadeOut(sdot), pts[3].animate.set_opacity(0.15),
                      pts[1].animate.scale(1.5), run_time=0.6)
            wait_until(self, tr, "fan")
            self.play(LaggedStart(*[AnimationGroup(Create(f), FadeIn(h)) for f, h in zip(fan, hits)],
                                  lag_ratio=0.25), run_time=rt(min(3.0, tr.get_remaining_duration() - 0.2)))
            self.add_foreground_mobject(pts[1])
            rest(self, tr)

        G = ModGrid(center=[0.3, MID - 0.4, 0], step=0.58, size=28)
        clock = lines("clock that wraps at 11", size=44, color=PRIMARY).next_to(G, UP, 0.35)
        mdot = Dot(G.p(1, Y0), radius=0.15, color=PRIMARY).set_stroke(BG, 2, background=True)
        fan11 = [mod_line(G, m, (Y0 - m) % P, SECONDARY, 3, dot_r=0.1).dots for m in range(P)]
        hits11 = VGroup(*[Dot(G.p(0, (Y0 - m) % P), radius=0.12, color=SECRET) for m in range(P)])
        each = mth(r"\text{each secret: } \tfrac{1}{11}", size=48, color=SECRET).next_to(G, UP, 0.35)
        with self.voiceover(text=N("short1.b5")) as tr:
            self.remove_foreground_mobject(pts[1])
            self.play(FadeOut(Group(*self.mobjects)), run_time=0.5)
            self.play(FadeIn(G), FadeIn(clock), run_time=0.8)
            self.play(FadeIn(mdot, scale=0.5), run_time=0.3)
            self.add_foreground_mobject(mdot)
            t = tr.time_until_bookmark("equal") - 0.1
            per = max(0.3, min(0.9, t / P))
            for k in range(P):
                ln = fan11[k]
                self.play(FadeIn(ln, lag_ratio=0.08), run_time=per * 0.45)
                self.play(FadeIn(hits11[k], scale=0.4), Indicate(ln[0], color=SECRET, scale_factor=1.6),
                          run_time=per * 0.3)
                self.play(FadeOut(ln), run_time=per * 0.25)
            wait_until(self, tr, "equal")
            self.play(FadeOut(clock), run_time=0.3)
            self.play(FadeIn(each), LaggedStart(*[Indicate(h, color=SECRET, scale_factor=1.5) for h in hits11], lag_ratio=0.08), run_time=0.8)
            rest(self, tr)

        v2 = vault(2.0).move_to([0, MID + 3.2, 0])
        pg2 = plane(ylabels=False, x_length=6.0, y_length=3.0, size=30).move_to([0.2, MID + 0.3, 0])
        pc = curve(pg2.ax, para_f, FG, 5)
        three = VGroup(*[pdot(pg2.ax, x, para_f(x), C5[x - 1], r=0.14) for x in (1, 3, 5)])
        name = text("Shamir's secret sharing", size=44, color=PRIMARY, weight="BOLD").move_to([0, MID - 2.75, 0])
        with self.voiceover(text=N("short1.b6")) as tr:
            self.remove_foreground_mobject(mdot)
            self.play(FadeOut(Group(*self.mobjects)), run_time=0.5)
            self.play(FadeIn(v2), FadeIn(pg2), run_time=0.6)
            wait_until(self, tr, "para")
            self.play(Create(pc), LaggedStart(*[FadeIn(p, scale=0.5) for p in three], lag_ratio=0.3), run_time=0.9)
            self.play(FadeIn(name, shift=UP * 0.2), open_door(v2), run_time=0.7)
            rest(self, tr)
        self.wait(0.8)


# The mod-11 parabola for short2: code 5, then 3x + 6x^2. Managers 2 and 4 hold its values there.
CODE = (5, 3, 6)
M2 = (2, sum(c * 2 ** i for i, c in enumerate(CODE)) % P)
M4 = (4, sum(c * 4 ** i for i, c in enumerate(CODE)) % P)


class Short2Nothing(VoiceoverScene):
    def construct(self):
        self.set_speech_service(get_speech_service())
        v = vault(3.0).move_to([0, MID + 2.2, 0])
        mg = managers(5, s=1.4, buff=0.45).move_to([0, MID - 1.2, 0])
        q = text("?", size=96, color=MUTED, weight="BOLD")
        with self.voiceover(text=N("short2.b1")) as tr:
            self.play(FadeIn(v), LaggedStart(*[FadeIn(m, shift=UP * 0.2) for m in mg], lag_ratio=0.15),
                      run_time=1.0)
            wait_until(self, tr, "three")
            self.play(*[mg[i].animate.set_opacity(0.25) for i in (1, 4)], run_time=0.4)
            self.play(open_door(v), run_time=0.6)
            wait_until(self, tr, "two")
            self.play(Restore(v.door), *[mg[i].animate.set_opacity(1 if i in (1, 3) else 0.25) for i in range(5)],
                      run_time=0.6)
            q.next_to(mg, DOWN, 0.4)
            self.play(FadeIn(q, scale=0.6), run_time=0.4)
            rest(self, tr)

        pg = tall_plane()
        ax = pg.ax
        sdot = pdot(ax, 0, para_f(0), SECRET, r=0.16)
        slab = text("code", size=42, color=SECRET).next_to(sdot, DR, 0.12)
        pc = curve(ax, para_f, FG, 5)
        pts = VGroup(*[pdot(ax, x, para_f(x), C5[x - 1], r=0.14) for x in range(1, 6)])
        with self.voiceover(text=N("short2.b2")) as tr:
            self.play(FadeOut(VGroup(v, mg, q)), run_time=0.5)
            self.play(FadeIn(pg), run_time=0.5)
            wait_until(self, tr, "para")
            self.play(Create(pc), FadeIn(sdot, scale=0.5), FadeIn(slab), run_time=0.9)
            self.play(LaggedStart(*[FadeIn(p, scale=0.5) for p in pts], lag_ratio=0.2),
                      run_time=rt(min(1.2, tr.get_remaining_duration())))
            rest(self, tr)

        keep = (0, 2, 4)
        c3 = interp([(x + 1, para_f(x + 1)) for x in keep])
        pc2 = curve(ax, poly(c3), GOOD, 6)
        ring = Circle(radius=0.32, color=GOOD, stroke_width=6).move_to(sdot)
        with self.voiceover(text=N("short2.b3")) as tr:
            self.play(FadeOut(pc), FadeOut(sdot), FadeOut(slab),
                      *[pts[i].animate.set_opacity(0.15) for i in range(5) if i not in keep], run_time=0.6)
            wait_until(self, tr, "fit")
            self.play(Create(pc2), run_time=0.8)
            self.play(FadeIn(sdot, scale=0.5), Create(ring), run_time=0.5)
            rest(self, tr)

        A, B = (2, para_f(2)), (4, para_f(4))
        hs = ValueTracker(2.0)
        third = always_redraw(lambda: pdot(ax, 0, hs.get_value(), SECRET, r=0.14))
        live = always_redraw(lambda: curve(ax, poly(interp([(0, hs.get_value()), A, B])), SECONDARY, 5))
        fan = VGroup(*[curve(ax, poly(interp([(0, s), A, B])), SECONDARY, 2.5, opacity=0.4)
                       for s in np.arange(0, 12.01, 1.0)])
        with self.voiceover(text=N("short2.b4")) as tr:
            self.play(FadeOut(pc2), FadeOut(ring), FadeOut(sdot),
                      *[pts[i].animate.set_opacity(1 if i in (1, 3) else 0.15) for i in range(5)], run_time=0.6)
            self.play(FadeIn(third, scale=0.5), run_time=0.4)
            wait_until(self, tr, "one")
            self.play(Create(live), run_time=0.7)
            t = tr.get_remaining_duration()
            self.play(hs.animate.set_value(10.0), run_time=rt(t * 0.35))
            self.play(LaggedStart(*[FadeIn(f) for f in fan], lag_ratio=0.15), hs.animate.set_value(6.0),
                      run_time=rt(t * 0.55))
            self.add_foreground_mobjects(pts[1], pts[3])
            rest(self, tr)

        G = ModGrid(center=[0.3, MID - 0.4, 0], step=0.58, size=28)
        clock = lines("clock that wraps at 11", size=44, color=PRIMARY).next_to(G, UP, 0.35)
        ma = Dot(G.p(*M2), radius=0.15, color=C5[1]).set_stroke(BG, 2, background=True)
        mb = Dot(G.p(*M4), radius=0.15, color=C5[3]).set_stroke(BG, 2, background=True)
        paras = [mod_poly_dots(G, mod_para_through(M2, M4, s), SECONDARY, r=0.09) for s in range(P)]
        hits = VGroup(*[Dot(G.p(0, s), radius=0.12, color=SECRET) for s in range(P)])
        each = mth(r"\text{each code: } \tfrac{1}{11}", size=48, color=SECRET).next_to(G, UP, 0.35)
        nothing = text("They know nothing.", size=52, color=PRIMARY, weight="BOLD").next_to(G, UP, 0.35)
        with self.voiceover(text=N("short2.b5")) as tr:
            self.remove_foreground_mobjects(pts[1], pts[3])
            self.play(FadeOut(Group(*self.mobjects)), run_time=0.5)
            self.play(FadeIn(G), FadeIn(clock), FadeIn(ma), FadeIn(mb), run_time=0.8)
            self.add_foreground_mobjects(ma, mb)
            t = tr.time_until_bookmark("equal") - 0.1
            per = max(0.2, min(0.55, t / P))
            for s in range(P):
                self.play(FadeIn(paras[s], lag_ratio=0.05), FadeIn(hits[s], scale=0.5), run_time=per * 0.75)
                self.play(paras[s].animate.set_opacity(0.15), run_time=per * 0.25)
            wait_until(self, tr, "equal")
            self.play(FadeOut(clock), run_time=0.3)
            self.play(FadeIn(each), LaggedStart(*[Indicate(h, color=SECRET, scale_factor=1.5) for h in hits], lag_ratio=0.08), run_time=0.8)
            self.wait(rt(tr.get_remaining_duration() - 1.4))
            self.play(FadeOut(each), FadeIn(nothing, shift=UP * 0.2), run_time=0.6)
            rest(self, tr)
        self.wait(0.8)
