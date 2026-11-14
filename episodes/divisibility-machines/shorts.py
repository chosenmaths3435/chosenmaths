"""Vertical shorts. Render with MV_ASPECT=portrait."""

import sys
from pathlib import Path

import numpy as np
from manim import *
from manim_voiceover import VoiceoverScene

from mathvid import layout  # noqa: F401  must come before scene code runs
from mathvid.anim import rest, wait_until
from mathvid.automata import glow_dot
from mathvid.layout import FW, SAFE_BOTTOM, SAFE_TOP
from mathvid.orders import cross, tick
from mathvid.script import Script
from mathvid.style import BAD, FG, GOOD, MUTED, PRIMARY, SECONDARY, math, text
from mathvid.voice import get_speech_service

sys.path.insert(0, str(Path(__file__).parent))
from scenes import (  # noqa: E402
    I_IDX,
    J_IDX,
    LAND,
    StateBox,
    clear,
    digit_row,
    feed_strings,
    mod3_machine,
    mod7_machine,
    paren_pair,
    paren_strings,
    pulse,
    read_digit,
    rule_tex,
    run_digits,
    wait_frac,
)

N = Script(__file__)

NUM_Y = SAFE_TOP - 0.65
SUB_Y = NUM_Y - 0.95


def fit(m, w=FW - 0.8):
    if m.width > w:
        m.scale_to_fit_width(w)
    return m


class Short1DivisibleBy7(VoiceoverScene):
    def construct(self):
        self.set_speech_service(get_speech_service())
        m = mod7_machine(radius=2.2, r=0.4, center=np.array([0, 0.15, 0]))
        num = digit_row("1729", size=120).move_to([0, NUM_Y, 0])
        sub = text("divisible by 7?", size=50, color=MUTED).move_to([0, SUB_Y, 0])
        with self.voiceover(text=N("short1.b1")) as tr:
            self.play(FadeIn(sub), FadeIn(m.node_layer), run_time=0.6)
            wait_frac(self, tr, 0.45)
            self.play(Create(m.edge_layer, lag_ratio=0.03), run_time=2.0)
            rest(self, tr)

        steps = [math(s, size=48, color=PRIMARY) for s in
                 [r"3 \cdot 0 + 1 = 1", r"3 \cdot 1 + 7 = 10 \to 3", r"3 \cdot 3 + 2 = 11 \to 4",
                  r"3 \cdot 4 + 9 = 21 \to 0"]]
        for s in steps:
            fit(s).move_to([0, SUB_Y, 0])
        with self.voiceover(text=N("short1.b2")) as tr:
            self.play(FadeIn(num), *m.fade_edges(0.35), run_time=0.6)
            m.light(self, 0, run_time=0.3)
            shown = [sub]
            marks = ["d1", "d2", "d3", "d4"]
            states = [0, 1, 3, 4, 0]
            for i in range(4):
                wait_until(self, tr, marks[i])
                nxt = tr.time_until_bookmark(marks[i + 1]) if i < 3 else 1.2
                dt = min(1.0, max(0.4, nxt - 0.05))
                self.play(*read_digit(num, i), FadeOut(shown[-1]), FadeIn(steps[i]), run_time=0.2 * dt)
                shown.append(steps[i])
                m.hop(self, states[i], states[i + 1], run_time=0.8 * dt, note="1729"[i])
            pulse(self, m, 0)
            done = math(r"1729 = 7 \times 247", size=52, color=GOOD).move_to([0, SUB_Y, 0])
            self.play(FadeOut(shown[-1]), FadeIn(done), num.animate.set_color(FG), run_time=0.5)
            rest(self, tr)

        l1 = math(r"x", r"\;\longrightarrow\;", r"10x + d", size=72)
        l2 = math(r"10", r"\to", r"\text{remainder } 3", size=66)
        l3 = fit(rule_tex([r"3r", r"+ d"], size=64))
        col = VGroup(l1, l2, l3).arrange(DOWN, buff=0.6).move_to([0, -1.0, 0])
        with self.voiceover(text=N("short1.b3")) as tr:
            m.light(self, None, run_time=0.2)
            self.play(FadeOut(num), FadeOut(done), m.animate.scale(0.62).move_to([0, 3.2, 0]), run_time=0.8)
            wait_frac(self, tr, 0.3)
            self.play(FadeIn(l1, shift=UP * 0.1), run_time=0.5)
            wait_frac(self, tr, 0.55)
            self.play(FadeIn(l2, shift=UP * 0.1), run_time=0.5)
            wait_frac(self, tr, 0.72)
            self.play(FadeIn(l3, shift=UP * 0.1), run_time=0.5)
            rest(self, tr)

        anyn = text("any n:", size=48, color=PRIMARY)
        r10 = fit(rule_tex([r"10r", r"+ d"], size=64))
        tail = VGroup(anyn, r10).arrange(DOWN, buff=0.4).move_to([0, -0.8, 0])
        with self.voiceover(text=N("short1.b4")) as tr:
            self.play(FadeOut(col), run_time=0.4)
            self.play(FadeIn(tail, shift=UP * 0.1), run_time=0.6)
            rest(self, tr)
        clear(self)


class Short2DigitSum(VoiceoverScene):
    def construct(self):
        self.set_speech_service(get_speech_service())
        m = mod3_machine(center=np.array([0, 0, 0]))
        fit(m, FW - 0.5).move_to([0, 0.4, 0])
        num = digit_row("4812", size=120).move_to([0, NUM_Y, 0])
        sub = text("divisible by 3?", size=50, color=MUTED).move_to([0, SUB_Y, 0])
        with self.voiceover(text=N("short2.b1")) as tr:
            self.play(FadeIn(num), FadeIn(sub), run_time=0.6)
            wait_frac(self, tr, 0.3)
            self.play(FadeIn(m.node_layer), FadeIn(m.start), run_time=0.8)
            wait_frac(self, tr, 0.5)
            self.play(*[Indicate(m.nodes[q], color=PRIMARY) for q in range(3)], run_time=1.0)
            wait_until(self, tr, "one")
            self.play(Create(VGroup(*[e.arrow for e in m.one])),
                      FadeIn(VGroup(*[e.label for e in m.one])), run_time=0.9)
            wait_until(self, tr, "two")
            self.play(Create(VGroup(*[e.arrow for e in m.two])),
                      FadeIn(VGroup(*[e.label for e in m.two])), run_time=0.9)
            wait_until(self, tr, "loop")
            self.play(Create(VGroup(*[e.arrow for e in m.loops])),
                      FadeIn(VGroup(*[e.label for e in m.loops])), run_time=0.9)
            rest(self, tr)

        with self.voiceover(text=N("short2.b2")) as tr:
            m.light(self, 0)
            run_digits(self, tr, m, "4812", num, marks=["d1", "d2", "d3", "d4"], n=3)
            pulse(self, m, 0)
            yes = math(r"4812 = 3 \times 1604", size=52, color=GOOD).move_to([0, SUB_Y, 0])
            self.play(FadeOut(sub), FadeIn(yes), num.animate.set_color(FG), run_time=0.5)
            rest(self, tr)

        l1 = math(r"x", r"\;\longrightarrow\;", r"10x + d", size=72)
        l2 = math(r"10x", "=", r"9x", "+", "x", size=72)
        brace = Brace(l2[2], DOWN, buff=0.1, color=MUTED)
        blab = text("multiple of 3", size=34, color=MUTED).next_to(brace, DOWN, buff=0.1)
        l3 = fit(rule_tex([r"r + d"], size=64))
        col = VGroup(l1, VGroup(l2, brace, blab), l3).arrange(DOWN, buff=0.55).move_to([0, -1.0, 0])
        with self.voiceover(text=N("short2.b3")) as tr:
            m.light(self, None, run_time=0.2)
            self.play(FadeOut(num), FadeOut(yes), m.animate.scale(0.6).move_to([0, 3.3, 0]), run_time=0.8)
            wait_frac(self, tr, 0.3)
            self.play(FadeIn(l1, shift=UP * 0.1), run_time=0.5)
            wait_frac(self, tr, 0.55)
            self.play(FadeIn(l2, shift=UP * 0.1), run_time=0.5)
            self.play(GrowFromCenter(brace), FadeIn(blab), run_time=0.5)
            wait_frac(self, tr, 0.8)
            self.play(FadeIn(l3, shift=UP * 0.1), run_time=0.5)
            rest(self, tr)

        ds = VGroup(text("walking the arrows", size=50, color=MUTED), text("=", size=60, color=MUTED),
                    text("digit sum", size=72, color=PRIMARY)).arrange(DOWN, buff=0.3).move_to([0, -0.8, 0])
        with self.voiceover(text=N("short2.b4")) as tr:
            self.play(FadeOut(col), run_time=0.4)
            self.play(FadeIn(ds, shift=UP * 0.1), run_time=0.6)
            rest(self, tr)
        clear(self)


class Short3Parentheses(VoiceoverScene):
    def construct(self):
        self.set_speech_service(get_speech_service())
        good, bad = paren_pair(size=96)
        VGroup(good, bad).move_to([0.3, 1.2, 0])
        tk = tick(good, s=1.8)
        cr = cross(bad.get_left() + LEFT * 0.6, s=0.25)
        with self.voiceover(text=N("short3.b1")) as tr:
            self.play(FadeIn(good), FadeIn(bad), run_time=0.5)
            self.play(Create(tk), Create(cr), run_time=0.5)
            rest(self, tr)

        box = StateBox(w=6.4, h=2.4, size=40).move_to([0, 3.75, 0])
        strs = paren_strings(7, size=42).arrange(DOWN, buff=0.18, aligned_edge=LEFT).move_to([-1.6, -0.85, 0])
        slab = text("k + 1 inputs", size=40, color=MUTED).move_to([1.6, 0.6, 0])
        with self.voiceover(text=N("short3.b2")) as tr:
            self.play(FadeOut(VGroup(good, bad, tk, cr)), run_time=0.4)
            self.play(FadeIn(box), run_time=0.6)
            wait_frac(self, tr, 0.4)
            self.play(LaggedStart(*[FadeIn(s, shift=RIGHT * 0.1) for s in strs], lag_ratio=0.25),
                      FadeIn(slab), run_time=1.4)
            per = max(0.35, (tr.time_until_bookmark("same") - 0.2) / 6)
            feed_strings(self, box, strs, range(6), per)
            wait_until(self, tr, "same")
            feed_strings(self, box, strs, [6], 0.8)
            hit = box.dots[LAND[6]]
            il = text("i", size=46, color=PRIMARY).next_to(strs[I_IDX], RIGHT, buff=0.3)
            jl = text("j", size=46, color=PRIMARY).next_to(strs[J_IDX], RIGHT, buff=0.3)
            self.play(hit.animate.set_color(PRIMARY).scale(1.4),
                      strs[I_IDX].animate.set_color(PRIMARY), strs[J_IDX].animate.set_color(PRIMARY),
                      run_time=0.5)
            wait_frac(self, tr, 0.85)
            self.play(FadeIn(il), FadeIn(jl), run_time=0.4)
            rest(self, tr)

        si = text("(((" + ")))", size=60)
        sj = text("(((((((" + ")))", size=60)
        si[3:].set_color(SECONDARY)
        sj[7:].set_color(SECONDARY)
        si.move_to([0, 0.9, 0])
        sj.move_to([0, -1.3, 0])
        si.align_to(sj, LEFT)
        end_dot = box.dots[5]
        with self.voiceover(text=N("short3.b3")) as tr:
            rest_strs = [s for k_, s in enumerate(strs) if k_ not in (I_IDX, J_IDX)]
            self.play(*[FadeOut(s) for s in rest_strs], FadeOut(slab), FadeOut(il), FadeOut(jl),
                      ReplacementTransform(strs[I_IDX], si[:3]), ReplacementTransform(strs[J_IDX], sj[:7]),
                      *[d.animate.set_color(FG) for d in box.dots if d is not hit], run_time=0.7)
            self.play(FadeIn(si[3:], shift=LEFT * 0.2), FadeIn(sj[7:], shift=LEFT * 0.2), run_time=0.5)
            path = ArcBetweenPoints(hit.get_center(), end_dot.get_center(), angle=-0.8)
            trail = path.copy().set_stroke(SECONDARY, 4)
            g1, g2 = glow_dot(SECONDARY), glow_dot(SECONDARY)
            g1.move_to(hit)
            g2.move_to(hit)
            self.play(Create(trail), MoveAlongPath(g1, path), MoveAlongPath(g2, path.copy()), run_time=1.2)
            self.play(FadeOut(g1), FadeOut(g2), end_dot.animate.set_color(SECONDARY).scale(1.4), run_time=0.4)
            wait_frac(self, tr, 0.6)
            t1 = tick(si, s=1.5)
            l1 = text("balanced", size=40, color=GOOD).next_to(si, DOWN, buff=0.2).align_to(si, LEFT)
            c2 = cross(sj.get_left() + LEFT * 0.55, s=0.22)
            l2 = text("not balanced", size=40, color=BAD).next_to(sj, DOWN, buff=0.2).align_to(sj, LEFT)
            self.play(Create(t1), FadeIn(l1), run_time=0.4)
            wait_frac(self, tr, 0.72)
            self.play(Create(c2), FadeIn(l2), run_time=0.4)
            wait_frac(self, tr, 0.85)
            self.play(end_dot.animate.set_color(BAD), Flash(end_dot, color=BAD), run_time=0.6)
            rest(self, tr)

        msg = VGroup(text("count to any", size=60), text("fixed number,", size=60),
                     text("never without limit", size=60, color=PRIMARY)).arrange(DOWN, buff=0.25)
        msg.move_to([0, 1.2, 0])
        with self.voiceover(text=N("short3.b4")) as tr:
            clear(self, run_time=0.4)
            self.play(FadeIn(msg, shift=UP * 0.1), run_time=0.6)
            rest(self, tr)
        clear(self)
