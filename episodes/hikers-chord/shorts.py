"""Vertical shorts. Render with MV_ASPECT=portrait."""

import sys
from pathlib import Path

import numpy as np
from manim import *
from manim_voiceover import VoiceoverScene

from mathvid import layout  # noqa: F401  must come before scene code runs
from mathvid.anim import rest, rt, wait_until
from mathvid.layout import SAFE_BOTTOM, SAFE_TOP
from mathvid.orders import cross, tick
from mathvid.script import Script
from mathvid.style import BAD, FG, GOOD, MUTED, PRIMARY, SECONDARY, TERTIARY, text
from mathvid.voice import get_speech_service

sys.path.insert(0, str(Path(__file__).parent))
from scenes import (  # noqa: E402
    AHEAD,
    HERE,
    LEVY,
    OPEN_HALF_Z,
    OPEN_THIRD_Z,
    PHI_STAR,
    Z_HALF,
    Globe,
    TrailMap,
    ahead_minus_here,
    align_x,
    counter,
    diff_arrow,
    drop_label,
    fractions_line,
    gap_bar,
    lake,
    levy_f,
    loop_h,
    mth,
    open_g,
    open_trail,
    pair_marks,
    plot,
    profile_axes,
    rod,
    same_label,
)

N = Script(__file__)

MID = (SAFE_TOP + SAFE_BOTTOM) / 2  # center of the safe area, about 1.2


def globe_at(rot, y=MID + 0.6, R=2.7, band=True):
    return Globe(R=R, rot=rot, band=band).move_to([0, y, 0])


class Short1Loop(VoiceoverScene):
    def construct(self):
        self.set_speech_service(get_speech_service())
        rot = ValueTracker(-PHI_STAR - 0.2)
        g = always_redraw(lambda: globe_at(rot.get_value()))
        marks = always_redraw(lambda: pair_marks(globe_at(rot.get_value(), band=False), size=40))
        with self.voiceover(text=N("short1.b1")) as tr:
            self.add(g)
            self.play(FadeIn(g), run_time=0.5)
            self.play(rot.animate.set_value(-PHI_STAR), run_time=1.2)
            self.add(marks)
            self.play(FadeIn(marks, scale=0.7), run_time=0.6)
            wait_until(self, tr, "trail")
            self.play(rot.animate.set_value(-PHI_STAR + 0.05), run_time=rt(tr.get_remaining_duration()))
        g.clear_updaters()
        marks.clear_updaters()
        self.play(FadeOut(g), FadeOut(marks), run_time=0.4)

        tm = TrailMap(R=1.25).move_to([0, 4.35, 0])
        pg = profile_axes(1.0, x_length=6.8, y_length=2.6, xlabel="distance along the trail", size=30)
        pg.move_to([0.25, 1.55, 0])
        ax = pg.ax
        prof = plot(ax, loop_h, 0, 1, FG, 5)
        t = ValueTracker(0.0)
        hiker = always_redraw(lambda: Dot(tm.at(t.get_value()), radius=0.15, color=HERE))
        ahead = always_redraw(lambda: Dot(tm.at(t.get_value() + 0.5), radius=0.15, color=AHEAD))
        ph = always_redraw(lambda: Dot(ax.c2p(t.get_value(), loop_h(t.get_value())), radius=0.12, color=HERE))
        pa = always_redraw(lambda: Dot(ax.c2p(t.get_value() + 0.5, loop_h(t.get_value() + 0.5)), radius=0.12,
                                       color=AHEAD))
        bar = always_redraw(lambda: gap_bar(ax, loop_h, t.get_value(), 0.5))
        cnt = counter(lambda: ahead_minus_here(t.get_value()), size=40).move_to([0, -0.3, 0])
        with self.voiceover(text=N("short1.b2")) as tr:
            self.play(Create(tm), FadeIn(pg), Create(prof), run_time=1.0)
            self.add(bar, ph, pa, hiker, ahead)
            self.play(FadeIn(hiker), FadeIn(ahead), run_time=0.4)
            wait_until(self, tr, "plus")
            self.play(FadeIn(cnt, shift=UP * 0.2), run_time=0.6)
            rest(self, tr)

        with self.voiceover(text=N("short1.b3")) as tr:
            self.play(t.animate.set_value(0.5), run_time=rt(tr.time_until_bookmark("swap") - 0.1))
            self.play(Indicate(cnt[1]), Indicate(ph, color=HERE), Indicate(pa, color=AHEAD), run_time=0.8)
            rest(self, tr)

        dg = profile_axes(0.5, x_length=3.4, y_length=1.7, y_range=(-60, 60, 50), xlabel="distance walked", size=28)
        dg.move_to([0, -1.85, 0])
        align_x(dg, ax)
        dax = dg.ax
        dcurve = plot(dax, ahead_minus_here, 0, 0.5, TERTIARY, 5)
        cp = Dot(dax.c2p(Z_HALF, 0), radius=0.12, color=GOOD)
        level = always_redraw(lambda: rod(ax, loop_h, t.get_value(), 0.5,
                                          GOOD if abs(t.get_value() - Z_HALF) < 1e-3 else FG, width=6))
        with self.voiceover(text=N("short1.b4")) as tr:
            self.play(FadeIn(dg), t.animate.set_value(0.0), run_time=0.7)
            trace = always_redraw(lambda: plot(dax, ahead_minus_here, 0, max(0.002, t.get_value()), TERTIARY, 5))
            self.add(trace)
            self.play(t.animate.set_value(0.5), run_time=rt(min(2.2, tr.time_until_bookmark("zero") - 0.1)),
                      rate_func=linear)
            trace.clear_updaters()
            self.remove(trace)
            self.add(dcurve)
            self.play(FadeIn(cp, scale=0.4), Flash(cp, color=GOOD), run_time=0.6)
            self.add(level)
            self.play(t.animate.set_value(Z_HALF), run_time=1.0)
            sl = same_label(ax, Z_HALF, size=38)
            self.play(FadeIn(sl), run_time=0.5)
            rest(self, tr)
        for m in (hiker, ahead, ph, pa, bar, cnt, level):
            m.clear_updaters()
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.5)

        g2 = globe_at(-PHI_STAR)
        m2 = pair_marks(globe_at(-PHI_STAR, band=False), size=40)
        same = text("same temperature", size=48, color=GOOD).next_to(g2, DOWN, 0.5)
        with self.voiceover(text=N("short1.b5")) as tr:
            self.play(FadeIn(g2), run_time=0.6)
            self.play(Indicate(g2.band, scale_factor=1.05, color=PRIMARY), run_time=1.0)
            self.play(FadeIn(m2, scale=0.7), run_time=0.6)
            wait_until(self, tr, "same")
            self.play(FadeIn(same, shift=UP * 0.2), run_time=0.6)
            rest(self, tr)
        self.wait(0.4)


class Short2TwoFifths(VoiceoverScene):
    def construct(self):
        self.set_speech_service(get_speech_service())
        pg = profile_axes(1.0, x_length=7.0, y_length=4.0, y_range=(-40, 220, 50), xlabel="distance along the trail",
                          size=30).move_to([0, 2.6, 0])
        ax = pg.ax
        trl = open_trail(ax)
        x = ValueTracker(0.0)
        r = always_redraw(lambda: rod(ax, open_g, x.get_value(), 0.5,
                                      GOOD if abs(open_g(x.get_value() + 0.5) - open_g(x.get_value())) < 1e-3 else FG,
                                      width=6))
        with self.voiceover(text=N("short2.b1")) as tr:
            self.play(FadeIn(pg), Create(trl[0]), FadeIn(trl[1:]), run_time=1.2)
            self.add(r)
            self.play(FadeIn(r), run_time=0.4)
            wait_until(self, tr, "half")
            self.play(x.animate.set_value(OPEN_HALF_Z), run_time=rt(min(1.6, tr.get_remaining_duration())))
            rest(self, tr)

        a1 = diff_arrow(ax, open_g, 0.0, 0.5, xoff=-0.02)
        a2 = diff_arrow(ax, open_g, 0.5, 0.5, xoff=-0.02)
        eq = VGroup(VGroup(text("up", size=44, color=GOOD), text("+", size=44), text("down", size=44, color=BAD))
                    .arrange(RIGHT, buff=0.2),
                    text("= end \u2212 start = 0", size=44)).arrange(DOWN, buff=0.2).move_to([0, -0.85, 0])
        with self.voiceover(text=N("short2.b2")) as tr:
            self.play(x.animate.set_value(0.0), run_time=0.6)
            self.play(GrowArrow(a1), run_time=0.5)
            self.play(x.animate.set_value(0.5), GrowArrow(a2), run_time=0.8)
            self.play(FadeIn(eq, shift=UP * 0.2), run_time=0.6)
            wait_until(self, tr, "one")
            self.play(x.animate.set_value(0.0), run_time=0.6)
            self.play(x.animate.set_value(OPEN_HALF_Z), run_time=rt(min(1.4, tr.get_remaining_duration())))
            rest(self, tr)
        r.clear_updaters()

        arrs = VGroup(*[diff_arrow(ax, open_g, k / 3, 1 / 3, xoff=-0.02) for k in range(3)])
        ghosts = VGroup(*[rod(ax, open_g, k / 3, 1 / 3, MUTED, width=4, r=0.08) for k in range(3)])
        fr = VGroup(*[mth(s, size=62) for s in (r"\tfrac{1}{2}", r"\tfrac{1}{3}", r"\tfrac{1}{4}", r"\tfrac{1}{5}",
                                                 r"\cdots")]).arrange(RIGHT, buff=0.95).move_to([0, -1.9, 0])
        tk = VGroup(*[tick(at=f.get_right() + RIGHT * 0.32, color=GOOD, s=1.2) for f in fr[:4]])
        with self.voiceover(text=N("short2.b3")) as tr:
            self.play(FadeOut(r), FadeOut(a1), FadeOut(a2), FadeOut(eq), run_time=0.4)
            self.play(FadeIn(ghosts), LaggedStart(*[GrowArrow(a) for a in arrs], lag_ratio=0.4), run_time=1.2)
            wait_until(self, tr, "any")
            self.play(LaggedStart(*[FadeIn(f) for f in fr], lag_ratio=0.15), run_time=0.8)
            self.play(LaggedStart(*[FadeIn(k, scale=0.5) for k in tk], lag_ratio=0.15), run_time=0.8)
            rest(self, tr)
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.5)

        lg = profile_axes(1.0, x_length=7.0, y_length=3.4, y_range=(-1.05, 1.05, 0.5), xlabel="distance along the trail",
                          size=30).move_to([0, 2.5, 0])
        lax = lg.ax
        lprof = plot(lax, levy_f, 0, 1, FG, 5, n=500)
        l0, l1 = lake(lax.c2p(0, 0), w=0.55), lake(lax.c2p(1, 0), w=0.55)
        title = text("a rod 2/5 of the trail long", size=42, color=BAD).move_to([0, 5.05, 0])
        y = ValueTracker(0.0)
        lr = always_redraw(lambda: rod(lax, levy_f, y.get_value(), 0.4, BAD, width=6))
        dl = drop_label(lambda: levy_f(y.get_value() + 0.4) - levy_f(y.get_value()), size=44).move_to([0, -0.15, 0])
        wl = text("a wave, tilted downhill", size=36, color=SECONDARY).move_to([0, -1.1, 0])
        with self.voiceover(text=N("short2.b4")) as tr:
            self.play(FadeIn(lg), FadeIn(title), Create(lprof), FadeIn(l0), FadeIn(l1), run_time=1.2)
            self.add(lr)
            self.play(FadeIn(lr), FadeIn(dl), run_time=0.5)
            self.play(FadeIn(wl), run_time=0.4)
            wait_until(self, tr, "lower")
            self.play(y.animate.set_value(0.6), run_time=rt(tr.get_remaining_duration()), rate_func=linear)
        lr.clear_updaters()
        dl.clear_updaters()

        fl = fractions_line(width=7.0, size=32).move_to([0, -1.55, 0])
        two5x = cross(fl.x(0.4), color=BAD, s=0.2, width=7)
        legend = VGroup(text("always works", size=34, color=GOOD), text("can fail", size=34, color=BAD))
        legend.arrange(RIGHT, buff=0.8).move_to([0, -2.75, 0])
        levy = text(LEVY, size=44, color=PRIMARY, weight="BOLD").move_to([0, -0.15, 0])
        with self.voiceover(text=N("short2.b5")) as tr:
            self.play(FadeOut(wl), FadeOut(dl), run_time=0.4)
            self.play(Create(fl.nl), FadeIn(fl.zero), FadeIn(two5x), run_time=0.7)
            wait_until(self, tr, "fails")
            self.play(LaggedStart(*[FadeIn(t_) for t_ in fl.ticks], lag_ratio=0.1), FadeIn(fl.labels), run_time=1.2)
            self.play(FadeIn(legend), FadeIn(levy), run_time=0.6)
            rest(self, tr)
        self.wait(0.4)
