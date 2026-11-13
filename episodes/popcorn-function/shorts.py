"""Vertical shorts. Render with MV_ASPECT=portrait."""

import sys
from pathlib import Path

from manim import *
from manim_voiceover import VoiceoverScene

from mathvid import layout  # noqa: F401  must come before scene code runs
from mathvid.anim import rest, rt, wait_until
from mathvid.layout import SAFE_BOTTOM, SAFE_TOP
from mathvid.numberline import ZoomLine
from mathvid.orders import cross
from mathvid.script import Script
from mathvid.style import BAD, FG, GOOD, MUTED, PRIMARY, math, text
from mathvid.voice import get_speech_service

sys.path.insert(0, str(Path(__file__).parent))
from scenes import (  # noqa: E402
    FRAC,
    IRR,
    ROOT,
    TARGET,
    Popcorn,
    countdown,
    interval_mark,
    list_row,
    question,
    rule_card,
    run_steps,
    scale_bar,
    y_labels,
)

N = Script(__file__)

MID = (SAFE_TOP + SAFE_BOTTOM) / 2  # center of the safe area
TOP_Y = SAFE_TOP - 0.55              # a line of text at the top of the safe area
LOW_Y = SAFE_BOTTOM + 0.35           # a line of text at the bottom of the safe area


def portrait_plot():
    return Popcorn(left=-3.3, right=3.5, y0=-1.0, y1=3.7, target=320, tick_size=22)


class Short1Popcorn(VoiceoverScene):
    def construct(self):
        self.set_speech_service(get_speech_service())
        pc = portrait_plot()
        pc.qshow.set_value(0)
        ylab = y_labels(pc, size=32)
        card = rule_card(size=34).move_to([0, 4.85, 0])
        with self.voiceover(text=N("short1.b1")) as tr:
            self.add(pc)
            self.play(FadeIn(ylab), pc.qshow.animate.set_value(30), run_time=2.2, rate_func=linear)
            pc.qshow.set_value(10_000)
            self.play(pc.glow.animate.set_value(0.7), run_time=0.6)
            wait_until(self, tr, "rule")
            self.play(FadeIn(card[0]), run_time=0.7)
            self.wait(rt(tr.get_remaining_duration() - 1.6))
            self.play(FadeIn(card[1]), run_time=0.6)
            rest(self, tr)

        # broken at 1/2
        ya, yb = ValueTracker(0.25), ValueTracker(0.75)
        bd = pc.band(ya, yb)
        xa, xb = ValueTracker(0.465), ValueTracker(0.535)
        wd = pc.window(xa, xb, color=GOOD, tint=False)
        red_on = ValueTracker(0.0)
        red = pc.axis_red(xa, xb, red_on)
        verdict = text("broken at 1/2", size=40, color=BAD).move_to([0, LOW_Y, 0])
        with self.voiceover(text=N("short1.b2")) as tr:
            self.play(FadeOut(ylab), pc.glow.animate.set_value(0), *pc.view(0.5, 0.16), run_time=1.2)
            self.add(bd)
            self.play(bd.on.animate.set_value(1.0), run_time=0.6)
            self.add(wd, red)
            self.play(wd.on.animate.set_value(1.0), run_time=0.5)
            wait_until(self, tr, "zero")
            self.play(red_on.animate.set_value(1.0), run_time=0.5)
            self.play(xa.animate.set_value(0.495), xb.animate.set_value(0.505), run_time=1.0)
            self.play(FadeIn(verdict), run_time=0.5)
            rest(self, tr)

        # continuous at 1/sqrt(2)
        mk = pc.marker(ROOT, r"\tfrac{1}{\sqrt2}", size=34)
        ya2, yb2 = ValueTracker(-0.1), ValueTracker(0.1)
        bd2 = pc.band(ya2, yb2)
        blab = math(r"\text{under } \tfrac{1}{10}", size=40, color=PRIMARY).move_to([0, LOW_Y, 0])
        with self.voiceover(text=N("short1.b3")) as tr:
            self.play(FadeOut(verdict), bd.on.animate.set_value(0), wd.on.animate.set_value(0),
                      red_on.animate.set_value(0), run_time=0.5)
            self.remove(bd, wd, red)
            pc.win = None
            self.play(*pc.view(0.5, 1.08), FadeIn(ylab), run_time=1.0)
            self.play(FadeIn(mk), pc.glow.animate.set_value(0.5), run_time=0.5)
            self.add(bd2)
            self.play(bd2.on.animate.set_value(1.0), FadeIn(blab), run_time=0.6)
            wait_until(self, tr, "poke")
            pc.qhl.set_value(10)
            self.play(pc.hl_on.animate.set_value(1.0), run_time=0.8)
            rest(self, tr)

        sb = scale_bar(pc, [2.3, -2.4, 0], size=22)
        n7 = always_redraw(lambda: math(r"\tfrac{7}{10}", size=34, color=BAD).next_to(pc.P(0.7, 0.1), UP, 0.12))
        n5 = always_redraw(lambda: math(r"\tfrac{5}{7}", size=34, color=BAD).next_to(pc.P(5 / 7, 1 / 7), UP, 0.12))
        n70 = always_redraw(lambda: math(r"\tfrac{70}{99}", size=32, color=BAD).next_to(pc.P(70 / 99, 1 / 99), UP, 0.12))
        n29 = always_redraw(lambda: math(r"\tfrac{29}{41}", size=32, color=BAD).next_to(pc.P(29 / 41, 1 / 41), UP, 0.12))
        xa2, xb2 = ValueTracker(ROOT - 0.011), ValueTracker(ROOT + 0.011)
        wd2 = pc.window(xa2, xb2, color=GOOD)
        blab2 = math(r"\text{under } \tfrac{1}{100}", size=40, color=PRIMARY).move_to([0, LOW_Y, 0])
        with self.voiceover(text=N("short1.b4")) as tr:
            self.play(FadeOut(ylab), run_time=0.3)
            self.add(sb)
            self.play(*pc.view(0.7075, 0.03, 0.17), run_time=1.6)
            self.play(FadeIn(n7), FadeIn(n5), run_time=0.4)
            self.add(wd2)
            wait_until(self, tr, "dodge")
            self.play(wd2.on.animate.set_value(1.0), xa2.animate.set_value(0.7015),
                      xb2.animate.set_value(0.7128), run_time=1.0)
            self.wait(rt(tr.get_remaining_duration() * 0.25))
            self.play(wd2.on.animate.set_value(0), FadeOut(n7), FadeOut(n5), run_time=0.3)
            pc.qhl.set_value(100)
            xa2.set_value(ROOT - 0.0002)
            xb2.set_value(ROOT + 0.0002)
            self.play(ya2.animate.set_value(-0.01), yb2.animate.set_value(0.01),
                      *pc.view(0.70712, 0.0006, 0.03), ReplacementTransform(blab, blab2),
                      run_time=rt(min(2.2, tr.get_remaining_duration() - 1.6)))
            self.play(FadeIn(n70), FadeIn(n29), wd2.on.animate.set_value(1.0),
                      xa2.animate.set_value(ROOT - 0.000028), xb2.animate.set_value(ROOT + 0.000028),
                      run_time=1.0)
            rest(self, tr)

        fin = VGroup(text("continuous at every irrational,", size=36, color=IRR),
                     text("broken at every fraction", size=36, color=BAD)).arrange(DOWN, buff=0.15)
        fin.move_to([0, 4.8, 0])
        with self.voiceover(text=N("short1.b5")) as tr:
            self.play(FadeOut(VGroup(n70, n29, blab2)), wd2.on.animate.set_value(0),
                      bd2.on.animate.set_value(0), FadeOut(mk), FadeOut(card), run_time=0.5)
            self.remove(sb, wd2, bd2)
            pc.win = None
            self.play(*pc.view(0.5, 1.08, 1.1), run_time=rt(min(2.0, tr.time_until_bookmark("tiny"))))
            pc.qhl.set_value(40)
            self.play(pc.glow.animate.set_value(1.0), FadeIn(fin), run_time=0.8)
            rest(self, tr)
        self.wait(0.4)


class Short2Countdown(VoiceoverScene):
    def construct(self):
        self.set_speech_service(get_speech_service())
        q = question(size=40).move_to([0, MID + 1.0, 0])
        no = text("No.", size=72, color=BAD, weight="BOLD").next_to(q, DOWN, 0.6)
        with self.voiceover(text=N("short2.b1")) as tr:
            self.play(FadeIn(q, shift=UP * 0.2), run_time=0.8)
            wait_until(self, tr, "no")
            self.play(FadeIn(no, scale=1.3), run_time=0.5)
            rest(self, tr)

        steps = countdown(9)
        row = list_row(8, size=38, buff=0.3).move_to([0, 4.7, 0])
        row.scale_to_fit_width(min(row.width, 7.3))
        rlabs = VGroup(*[text(f"r{k + 1}", size=20, color=MUTED).next_to(row.items[k], DOWN, 0.15)
                         for k in range(len(row.items))])
        zl = ZoomLine(-0.06, 1.06, length=7.2, center=[0, 0.4, 0], label_size=22, max_labels=4)
        cur = (ValueTracker(0.0), ValueTracker(1.0))
        im = interval_mark(zl, *cur)
        with self.voiceover(text=N("short2.b2")) as tr:
            self.play(FadeOut(q), FadeOut(no), run_time=0.4)
            self.play(LaggedStart(*[FadeIn(m, shift=DOWN * 0.15) for m in row], lag_ratio=0.12),
                      FadeIn(rlabs), run_time=1.4)
            self.play(FadeIn(zl), run_time=0.5)
            self.add(im)
            self.play(im.on.animate.set_value(1.0), run_time=0.5)
            rest(self, tr)

        st = steps[0]
        r0 = zl.dot(0.0, color=BAD, radius=0.09)
        pick = zl.dot(0.5, color=GOOD, radius=0.1)
        pick_lab = always_redraw(lambda: math(r"\tfrac{1}{2}", size=38, color=GOOD).next_to(zl.p(0.5), UP, 0.7))
        lab_pos = [0, 2.2, 0]
        within = text("f moves within 1 here", size=32, color=PRIMARY).move_to(lab_pos)
        with self.voiceover(text=N("short2.b3")) as tr:
            self.add(r0)
            self.play(r0.show.animate.set_value(1), run_time=0.4)
            wait_until(self, tr, "skip")
            zx = cross(zl.p(0.0), s=0.14, width=5)
            self.play(cur[0].animate.set_value(st["cut"][0]), Create(zx),
                      Create(cross(row.items[0].get_center(), s=0.18, width=5)), run_time=0.7)
            self.add(pick)
            self.play(pick.show.animate.set_value(1), FadeIn(pick_lab), run_time=0.5)
            self.wait(rt(tr.get_remaining_duration() - 1.6))
            a, b = st["tight"]
            self.play(cur[0].animate.set_value(a), cur[1].animate.set_value(b), FadeIn(within), run_time=1.0)
            rest(self, tr)

        with self.voiceover(text=N("short2.b4")) as tr:
            self.play(FadeOut(pick_lab), pick.show.animate.set_value(0), r0.show.animate.set_value(0),
                      FadeOut(zx), FadeOut(within), run_time=0.4)
            per = (tr.time_until_bookmark("point") - 0.6) / 8
            lab = run_steps(self, zl, cur, steps, row, 1, 9, per, lab_pos, label_size=32)
            self.play(cur[0].animate.set_value(TARGET - 1e-7), cur[1].animate.set_value(TARGET + 1e-7),
                      *zl.zoom_to(TARGET - 3e-6, TARGET + 3e-6), FadeOut(lab), run_time=1.0)
            pt = Dot(zl.p(TARGET) + UP * 0.32, radius=0.12, color=IRR)
            glow = Circle(radius=0.28, color=IRR, stroke_width=4).move_to(pt)
            self.play(FadeIn(pt, scale=2), Create(glow), run_time=0.5)
            rest(self, tr)

        v1 = text("missed every fraction: irrational", size=32, color=IRR).move_to([0, 2.6, 0])
        v2 = text("and continuous here", size=36, color=GOOD).move_to([0, 1.85, 0])
        with self.voiceover(text=N("short2.b5")) as tr:
            self.play(FadeIn(v1), run_time=0.6)
            wait_until(self, tr, "cont")
            self.play(FadeIn(v2), Indicate(pt, color=GOOD, scale_factor=1.6), run_time=0.8)
            rest(self, tr)
        self.wait(0.4)
