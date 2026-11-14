"""Vertical shorts for the quines episode. Builders come from scenes.py."""

import sys
from pathlib import Path

import numpy as np
from manim import *
from manim_voiceover import VoiceoverScene

from mathvid import layout  # noqa: F401  must come before scene code runs
from mathvid.anim import clear, rest, wait_frac, wait_until
from mathvid.code import CodePanel, WrappedCode, mono
from mathvid.layout import FW, SAFE_BOTTOM, SAFE_TOP
from mathvid.script import Script
from mathvid.style import BAD, BG, FG, GOOD, MUTED, PRIMARY, SECONDARY, TERTIARY, math, text
from mathvid.voice import get_speech_service

sys.path.insert(0, str(Path(__file__).parent))
from scenes import (  # noqa: E402
    DATA_C,
    INSTR_C,
    LISP,
    QUERY,
    QUINE,
    TERM_BG,
    cross,
    e_lister,
    hl,
    part_box,
    prog_bar,
    star,
    steps_panel,
)

N = Script(__file__)

WRAP = 33          # characters per row of wrapped code
CODE_SIZE = 21


def quine_wrapped():
    return WrappedCode(QUINE, WRAP, size=CODE_SIZE)


def wrapped_terminal():
    """The terminal after running the quine: the prompt, then the same wrapped text."""
    out = WrappedCode(["$ python quine.py"] + QUINE, WRAP, size=CODE_SIZE, python=False, bg=TERM_BG)
    out.line(0).set_color(MUTED)
    return out


def title_text(s, size=46, y=None):
    t = text(s, size=size, weight="BOLD")
    if t.width > FW - 0.8:
        t.scale_to_fit_width(FW - 0.8)
    t.move_to([0, y if y is not None else SAFE_TOP - 0.4, 0])
    return t


def two_line(a, b, size, color):
    return VGroup(text(a, size=size, color=color), text(b, size=size, color=color)).arrange(
        DOWN, buff=0.15, aligned_edge=LEFT)


def sentence_parts(size=40):
    instr = two_line("Print two copies of the following,", "the second one in quotes:", size, INSTR_C)
    data = two_line('"Print two copies of the following,', 'the second one in quotes:"', size, DATA_C)
    return instr, data


class Short1PrintItself(VoiceoverScene):
    def construct(self):
        self.set_speech_service(get_speech_service())
        title = title_text("Can a program print itself?", y=SAFE_TOP - 0.3)
        code = quine_wrapped()
        code.next_to(title, DOWN, buff=0.45)
        term = wrapped_terminal().scale(0.68)
        term.next_to(code, DOWN, buff=0.3)
        self.add(title, code)
        with self.voiceover(text=N("short1.b1")) as tr:
            wait_frac(self, tr, 0.35)
            self.play(FadeIn(term.bg), FadeIn(term.line(0)), run_time=0.5)
            wait_until(self, tr, "run")
            rows = [term.line(i) for i in range(1, 6)]
            self.play(LaggedStart(*[FadeIn(r) for r in rows], lag_ratio=0.2), FadeIn(term.markers), run_time=0.9)
            ok = text("identical", size=36, color=GOOD).next_to(term, DOWN, buff=0.15)
            if ok.get_bottom()[1] < SAFE_BOTTOM:
                ok.next_to(term.bg, RIGHT, buff=-1.6).align_to(term.bg, DOWN).shift(UP * 0.1)
            self.play(Indicate(term, color=GOOD, scale_factor=1.0), FadeIn(ok), run_time=0.7)
            rest(self, tr)

        instr, data = sentence_parts(36)
        sent = VGroup(instr, data).arrange(DOWN, buff=0.6, aligned_edge=LEFT).move_to([0, 3.3, 0])
        out1 = two_line("Print two copies of the following,", "the second one in quotes:", 36, DATA_C)
        out2 = two_line('"Print two copies of the following,', 'the second one in quotes:"', 36, DATA_C)
        outs = VGroup(out1, out2).arrange(DOWN, buff=0.3, aligned_edge=LEFT)
        outs.next_to(sent, DOWN, buff=0.9).align_to(sent, LEFT)
        with self.voiceover(text=N("short1.b2")) as tr:
            self.play(FadeOut(VGroup(code, term, ok, title)), run_time=0.5)
            self.play(FadeIn(instr, shift=UP * 0.1), run_time=0.6)
            wait_frac(self, tr, 0.3)
            self.play(FadeIn(data, shift=UP * 0.1), run_time=0.6)
            wait_frac(self, tr, 0.6)
            self.play(TransformFromCopy(data, out1), run_time=0.8)
            self.play(TransformFromCopy(data, out2), run_time=0.8)
            eq = math("=", size=70, color=GOOD).rotate(PI / 2).move_to(
                [0, (sent.get_bottom()[1] + outs.get_top()[1]) / 2, 0])
            self.play(FadeIn(eq), run_time=0.4)
            rest(self, tr)

        li = text("instructions", size=28, color=INSTR_C).next_to(instr, UP, buff=0.1).align_to(instr, LEFT)
        ld = text("data", size=28, color=DATA_C).next_to(data, UP, buff=0.1).align_to(data, LEFT)
        bd = hl(data, DATA_C, buff=0.08)
        b1 = hl(out1, DATA_C, buff=0.08)
        b2 = hl(out2, DATA_C, buff=0.08)
        a1, a2 = b1, b2
        with self.voiceover(text=N("short1.b3")) as tr:
            self.play(FadeIn(li), FadeIn(ld), run_time=0.6)
            wait_frac(self, tr, 0.45)
            self.play(Create(bd), run_time=0.4)
            self.play(TransformFromCopy(bd, b1), run_time=0.5)
            self.play(TransformFromCopy(bd, b2), run_time=0.5)
            rest(self, tr)

        code2 = quine_wrapped().move_to([0, 2.0, 0])
        box_d = hl(VGroup(code2.line(0), code2.line(1)), DATA_C)
        box_i = hl(VGroup(code2.line(2), code2.line(3)), INSTR_C)
        ld2 = text("data", size=34, color=DATA_C, weight="BOLD").next_to(box_d, UP, buff=0.12).align_to(box_d, RIGHT)
        li2 = text("instructions", size=34, color=INSTR_C, weight="BOLD").next_to(code2, DOWN, buff=0.15)
        li2.align_to(box_i, RIGHT)
        rpart = code2.part(3, "repr")
        with self.voiceover(text=N("short1.b4")) as tr:
            self.play(FadeOut(VGroup(sent, outs, eq, li, ld, a1, a2, bd)), run_time=0.5)
            self.play(FadeIn(code2), run_time=0.5)
            wait_frac(self, tr, 0.12)
            self.play(Create(box_d), FadeIn(ld2), run_time=0.6)
            wait_frac(self, tr, 0.4)
            self.play(Create(box_i), FadeIn(li2), run_time=0.6)
            wait_frac(self, tr, 0.6)
            self.play(Indicate(rpart, color=PRIMARY, scale_factor=1.4), run_time=0.9)
            wait_frac(self, tr, 0.85)
            self.play(Indicate(code2.line(4), color=PRIMARY, scale_factor=1.1), run_time=0.8)
            rest(self, tr)

        cpb = part_box("P B", DATA_C, 2.2, h=0.9, size=36)
        cb = part_box("B", INSTR_C, 2.2, h=0.9, size=36)
        VGroup(cpb, cb).arrange(RIGHT, buff=2.2).move_to([0, -2.0, 0])
        with self.voiceover(text=N("short1.b5")) as tr:
            self.play(FadeOut(li2), FadeOut(ld2), FadeIn(cpb), FadeIn(cb), run_time=0.5)
            arr = CurvedArrow(cpb.get_top() + UP * 0.05, cb.get_top() + UP * 0.05, angle=-PI / 2.5, color=DATA_C)
            lab = text("copy of", size=30, color=DATA_C).next_to(arr, UP, buff=0.08)
            self.play(Create(arr), FadeIn(lab), run_time=0.7)
            wait_frac(self, tr, 0.55)
            back = DashedVMobject(CurvedArrow(cb.get_bottom() + DOWN * 0.05, cpb.get_bottom() + DOWN * 0.05,
                                              angle=-PI / 2.5, color=MUTED), num_dashes=12)
            self.play(Create(back), run_time=0.5)
            self.play(Create(cross(Square(0.55).move_to(back.get_center()), width=6)), run_time=0.4)
            rest(self, tr)
        clear(self)


class Short2Backwards(VoiceoverScene):
    def construct(self):
        self.set_speech_service(get_speech_service())
        title = title_text("Run a program backwards?", y=SAFE_TOP - 0.3)
        box = RoundedRectangle(width=4.2, height=1.4, corner_radius=0.15, color=FG, stroke_width=3)
        blab = text("interpreter", size=44).move_to(box)
        expr = mono("(list 'a 'b)", 40, FG)
        val = mono("(a b)", 40, FG)
        col = VGroup(expr, box, val).arrange(DOWN, buff=1.1).move_to([0, 1.2, 0])
        blab.move_to(box)
        a1 = Arrow(expr.get_bottom(), box.get_top(), buff=0.12, color=MUTED)
        a2 = Arrow(box.get_bottom(), val.get_top(), buff=0.12, color=MUTED)
        self.add(title, box, blab, expr, a1)
        with self.voiceover(text=N("short2.b1")) as tr:
            wait_frac(self, tr, 0.55)
            self.play(GrowArrow(a2), FadeIn(val, shift=DOWN * 0.2), run_time=0.8)
            rest(self, tr)

        lab2 = text("evalo", size=48).move_to(box)
        le = text("expression", size=42).move_to(expr)
        rv = text("value", size=42).move_to(val)
        d1 = DoubleArrow(le.get_bottom(), box.get_top(), buff=0.12, color=PRIMARY, tip_length=0.25)
        d2 = DoubleArrow(box.get_bottom(), rv.get_top(), buff=0.12, color=PRIMARY, tip_length=0.25)
        q1 = text("?", size=64, color=PRIMARY).next_to(le, RIGHT, buff=0.3)
        q2 = text("?", size=64, color=PRIMARY).next_to(rv, RIGHT, buff=0.3)
        with self.voiceover(text=N("short2.b2")) as tr:
            self.play(Transform(blab, lab2), run_time=0.6)
            self.play(Transform(expr, le), Transform(val, rv), ReplacementTransform(a1, d1),
                      ReplacementTransform(a2, d2), run_time=0.9)
            wait_frac(self, tr, 0.62)
            self.play(FadeIn(q1, scale=1.4), run_time=0.4)
            self.play(FadeIn(q2, scale=1.4), run_time=0.4)
            rest(self, tr)

        qp = CodePanel([QUERY], size=26, highlight=False).move_to([0, 3.9, 0])
        with self.voiceover(text=N("short2.b3")) as tr:
            self.play(FadeOut(VGroup(box, blab, expr, val, d1, d2, q1, q2)), title.animate.set_opacity(0),
                      run_time=0.5)
            self.play(FadeIn(qp), run_time=0.5)
            qa, qb = qp.part(0, "q", 1), qp.part(0, "q", 2)
            self.play(qa.animate.set_color(PRIMARY), qb.animate.set_color(PRIMARY), run_time=0.4)
            self.play(Indicate(qa, color=PRIMARY, scale_factor=1.5), Indicate(qb, color=PRIMARY, scale_factor=1.5),
                      run_time=0.8)
            rest(self, tr)

        ans = CodePanel(LISP, size=19, highlight=False, pad=0.25).move_to([0, 1.7, 0])
        note = text("variable renamed: _.0 is shown as x", size=24, color=MUTED).next_to(ans, DOWN, buff=0.15)
        with self.voiceover(text=N("short2.b4")) as tr:
            self.play(FadeIn(ans.bg), run_time=0.3)
            self.play(Write(ans.line(0)), Write(ans.line(1)), run_time=1.0)
            self.play(FadeIn(note), run_time=0.3)
            rest(self, tr)

        bx1 = hl(ans.line(0), INSTR_C, buff=0.04)
        bx2 = hl(ans.line(1), DATA_C, buff=0.04)
        l1 = text("instructions", size=32, color=INSTR_C).next_to(ans, UP, buff=0.12).align_to(ans, LEFT)
        l2 = text("data", size=32, color=DATA_C).next_to(ans, DOWN, buff=0.12).align_to(ans, RIGHT)
        valp = CodePanel(LISP, size=19, highlight=False, pad=0.25, stroke=GOOD).move_to([0, -1.2, 0])
        vlab = text("value", size=32, color=GOOD).next_to(valp, UP, buff=0.12).align_to(valp, LEFT)
        ok = text("= the expression", size=32, color=GOOD).next_to(valp, DOWN, buff=0.15).align_to(valp, RIGHT)
        with self.voiceover(text=N("short2.b5")) as tr:
            self.play(FadeOut(note), Create(bx1), FadeIn(l1), run_time=0.6)
            wait_frac(self, tr, 0.22)
            self.play(Create(bx2), FadeIn(l2), run_time=0.6)
            wait_frac(self, tr, 0.42)
            for k in range(2):
                fly = ans.line(1).copy()
                extra = [FadeIn(valp.bg), FadeIn(vlab)] if k == 0 else []
                self.play(*extra, fly.animate.move_to(valp.lines[k].body()).set_opacity(0),
                          FadeIn(valp.lines[k]), run_time=0.9)
                self.remove(fly)
            self.play(FadeIn(ok), run_time=0.4)
            rest(self, tr)
        clear(self)


class Short3Shortest(VoiceoverScene):
    def construct(self):
        self.set_speech_service(get_speech_service())
        t1 = text("No program can list", size=50, weight="BOLD")
        t2 = text("every shortest program.", size=50, weight="BOLD")
        title = VGroup(t1, t2).arrange(DOWN, buff=0.15).move_to([0, SAFE_TOP - 0.7, 0])
        long_p = prog_bar(5.6, MUTED)
        short_p = prog_bar(2.2, FG)
        pair = VGroup(long_p, short_p).arrange(DOWN, buff=0.6, aligned_edge=LEFT).move_to([-0.6, 1.6, 0])
        same = text("same behavior", size=32, color=MUTED).next_to(pair, UP, buff=0.3).align_to(pair, LEFT)
        stc = star().next_to(short_p, RIGHT, buff=0.3)
        stl = text("shortest", size=34, color=PRIMARY).next_to(stc, RIGHT, buff=0.2)
        self.add(title, long_p, short_p, same)
        with self.voiceover(text=N("short3.b1")) as tr:
            wait_frac(self, tr, 0.45)
            self.play(FadeIn(stc, scale=1.5), FadeIn(stl), run_time=0.6)
            rest(self, tr)

        ebox = part_box("E", FG, 1.4, h=1.4, size=48).move_to([-2.9, 2.0, 0])
        bars = e_lister(n=9, x0=-2.0, top=2.6, gap=0.46, longest=6, seed=5)
        for b in bars:
            b.scale(0.85, about_edge=LEFT)
        mark_x = 1.6
        mline = DashedLine([mark_x, 2.9, 0], [mark_x, -1.5, 0], color=PRIMARY, dash_length=0.12)
        mlab = text("any length", size=30, color=PRIMARY).next_to(mline, DOWN, buff=0.1)
        with self.voiceover(text=N("short3.b2")) as tr:
            self.play(FadeOut(VGroup(long_p, short_p, same, stc, stl)), run_time=0.4)
            self.play(FadeIn(ebox), run_time=0.4)
            per = max(0.2, (0.6 * tr.duration - 0.8) / 6)
            for i in range(6):
                self.play(GrowFromEdge(bars[i], LEFT), run_time=min(0.5, per * 0.7))
                self.wait(max(0.05, per * 0.3))
            wait_frac(self, tr, 0.72)
            self.play(Create(mline), FadeIn(mlab), run_time=0.5)
            self.play(GrowFromEdge(bars[6], LEFT), run_time=0.5)
            self.play(bars[6].bar.animate.set_fill(PRIMARY), run_time=0.3)
            self.play(LaggedStart(*[GrowFromEdge(b, LEFT) for b in bars[7:]], lag_ratio=0.5), run_time=0.5)
            rest(self, tr)

        size = 34
        r1 = text("1. Get your own source code.", size=size)
        r2 = VGroup(text("2. Run E until it lists a", size=size),
                    text("program D longer than C.", size=size)).arrange(DOWN, buff=0.1, aligned_edge=LEFT)
        r2[1].shift(RIGHT * 0.35)
        r3 = text("3. Do what D does.", size=size)
        cs = steps_panel("C", PRIMARY, [r1, r2, r3], size=size, width=FW - 0.9).move_to([0, 1.2, 0])
        tag = text("by the recursion theorem", size=28, color=TERTIARY).next_to(r1, DOWN, buff=0.08)
        tag.align_to(r1, LEFT).shift(RIGHT * 0.35)
        with self.voiceover(text=N("short3.b3")) as tr:
            self.play(FadeOut(VGroup(bars, mline, mlab)), ebox.animate.scale(0.6).move_to([-3.0, 4.2, 0]),
                      title.animate.set_opacity(0), run_time=0.6)
            # make room for the tag under step 1
            VGroup(r2, r3).shift(DOWN * 0.35)
            cs.bg.stretch_to_fit_height(cs.bg.height + 0.35).shift(DOWN * 0.175)
            self.play(FadeIn(cs.bg), FadeIn(cs[1][0]), run_time=0.4)
            for i, (mk, row) in enumerate(zip(["one", "two", "three"], [r1, r2, r3])):
                wait_until(self, tr, mk)
                self.play(FadeIn(row, shift=RIGHT * 0.2), run_time=0.5)
                if i == 0:
                    self.play(FadeIn(tag), run_time=0.4)
            rest(self, tr)

        cbar = prog_bar(2.2, PRIMARY, label="C", size=32)
        dbar = prog_bar(4.6, FG, label="D", size=32)
        cd = VGroup(cbar, dbar).arrange(DOWN, buff=0.45, aligned_edge=LEFT).move_to([0.1, -1.6, 0])
        dstar = star().next_to(dbar.bar, RIGHT, buff=0.2)
        same2 = text("same behavior", size=30, color=MUTED).next_to(cd, UP, buff=0.2).align_to(cd, LEFT)
        with self.voiceover(text=N("short3.b4")) as tr:
            self.play(FadeOut(tag), cs.animate.scale(0.85).move_to([0, 2.1, 0]),
                      ebox.animate.move_to([-3.0, 4.6, 0]), run_time=0.5)
            self.play(GrowFromEdge(cbar.bar, LEFT), FadeIn(cbar[1]), GrowFromEdge(dbar.bar, LEFT), FadeIn(dbar[1]),
                      FadeIn(dstar), FadeIn(same2), run_time=0.8)
            wait_frac(self, tr, 0.35)
            crack = VMobject(color=BG, stroke_width=5).set_points_as_corners(
                [dstar.get_top(), dstar.get_center() + LEFT * 0.08, dstar.get_center() + RIGHT * 0.06,
                 dstar.get_bottom()])
            self.play(dstar.animate.set_fill(BAD).set_stroke(BAD), Create(crack), run_time=0.6)
            wait_frac(self, tr, 0.7)
            self.play(Create(cross(ebox, width=7)), run_time=0.5)
            rest(self, tr)
        clear(self)
