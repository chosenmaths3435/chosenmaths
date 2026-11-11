"""Vertical shorts. Render with MV_ASPECT=portrait."""

import sys
from pathlib import Path

from manim import *
from manim_voiceover import VoiceoverScene

from mathvid import layout  # noqa: F401  must come before scene code runs
from mathvid.anim import rest, rt, wait_until
from mathvid.code import CodePanel, mono
from mathvid.layout import FW, SAFE_BOTTOM, SAFE_TOP
from mathvid.orders import cross
from mathvid.script import Script
from mathvid.style import BAD, BG, FG, GOOD, MUTED, PRIMARY, SECONDARY, math, text
from mathvid.voice import get_speech_service

sys.path.insert(0, str(Path(__file__).parent))
from scenes import (  # noqa: E402
    RAND_C,
    OutputSlots,
    all_strings,
    berry_phrase,
    coin_strip,
    compressor,
    file_icon,
    frac_time,
    k_program,
    letter_count,
    length_bars,
    mt,
    proof_program,
    rand_bits,
    run_through,
    shorter_strings,
    spinner,
    str_col,
    tag,
)

N = Script(__file__)

MID = (SAFE_TOP + SAFE_BOTTOM) / 2  # center of the safe area
TOP = SAFE_TOP - 0.5
W = FW - 1.0


def fit(m, w=W):
    return m.scale_to_fit_width(min(m.width, w))


def compress_demo(scene, comp, items, total):
    """Run several (in, out, label) files through the compressor, one after another."""
    outs = []
    per = max(1.2, total / max(1, len(items)))
    for f_in, f_out in items:
        if outs:
            scene.play(FadeOut(outs[-1]), run_time=0.25)
        run_through(scene, comp, f_in, f_out, per - 0.3, gap=0.55)
        outs.append(f_out)
    return outs


def kdef_p(size=34):
    return VGroup(mt("$K(x) =", "length of the shortest", size=size),
                  mt("program that prints", "$x", size=size)).arrange(DOWN, buff=0.2)


def contra_vertical(prog_label, out_label, size=30):
    prog = CodePanel(["(the program)"], size=size, highlight=False)
    pl = mt(*prog_label, size=size, color=GOOD).next_to(prog, DOWN, 0.25)
    arr = Arrow(UP, DOWN, color=MUTED, stroke_width=5).next_to(pl, DOWN, 0.2)
    out = mono("0110100110010111", size + 2, PRIMARY).next_to(arr, DOWN, 0.25)
    ol = mt(*out_label, size=size, color=BAD).next_to(out, DOWN, 0.25)
    g = VGroup(prog, pl, arr, out, ol)
    g.prog, g.pl, g.arr, g.out, g.ol = prog, pl, arr, out, ol
    return g


# ---------------------------------------------------------------------------
# short1 Why no compressor shrinks everything
# ---------------------------------------------------------------------------


class Short1Compress(VoiceoverScene):
    def construct(self):
        self.set_speech_service(get_speech_service())
        comp = compressor(w=2.4, h=1.4, size=30).move_to(UP * (MID + 1.4))
        nab = text("not a bug", size=48, weight="BOLD").move_to(UP * (MID - 1.0))
        sub = fit(tag("not enough short files to go around", size=30)).next_to(nab, DOWN, 0.3)
        with self.voiceover(text=N("short1.b1")) as tr:
            self.add(comp)
            tf = file_icon(1.0, 1.3, label="notes.txt")
            tf_out = file_icon(0.7, 0.9, label="smaller", label_size=20)
            run_through(self, comp, tf, tf_out, 1.6, gap=0.55)
            nf = file_icon(1.0, 1.3, noise=True, seed=3, label="noise")
            nf_out = file_icon(1.1, 1.42, noise=True, seed=3, color=BAD, label="bigger", label_size=20)
            self.play(FadeOut(tf_out), run_time=0.25)
            run_through(self, comp, nf, nf_out, 1.6, gap=0.55)
            plus = text("+1 byte", size=30, color=BAD).next_to(nf_out, UP, 0.2)
            self.play(FadeIn(plus), run_time=0.3)
            self.play(FadeIn(nab, scale=1.1), run_time=0.5)
            self.play(FadeIn(sub), run_time=0.5)
            rest(self, tr)

        right = str_col(all_strings(3), size=36, buff=0.14)
        left = str_col(shorter_strings(3), size=36, buff=0.14)
        VGroup(left, right).arrange(RIGHT, buff=2.4).move_to(UP * (MID - 0.2))
        left.align_to(right, UP)
        rl = tag("3-bit files", size=30).next_to(right, UP, 0.35)
        ll = tag("shorter files", size=30).next_to(left, UP, 0.35)
        ll.match_y(rl)
        with self.voiceover(text=N("short1.b2")) as tr:
            self.play(FadeOut(VGroup(comp, nf_out, plus, nab, sub)), run_time=0.4)
            wait_until(self, tr, "eight")
            self.play(FadeIn(rl), LaggedStart(*[FadeIn(s) for s in right], lag_ratio=0.1), run_time=0.9)
            n8 = math("8", size=64, color=PRIMARY).next_to(right, DOWN, 0.4)
            self.play(FadeIn(n8), run_time=0.3)
            self.play(FadeIn(ll), FadeIn(left[0]), run_time=0.4)
            self.play(FadeIn(left[1:3]), run_time=0.4)
            self.play(FadeIn(left[3:]), run_time=0.4)
            wait_until(self, tr, "seven")
            n7 = math("7", size=64, color=SECONDARY).next_to(left, DOWN, 0.4).match_y(n8)
            self.play(FadeIn(n7, scale=1.3), run_time=0.4)
            rest(self, tr)

        sl = OutputSlots(n=3, cell_w=0.86, cell_h=0.62, size=26, row_buff=0.7, col_buff=0.07, row_labels=False)
        sl.move_to(UP * (MID - 0.2))
        sl_lab = fit(tag("each file sits at its own output", size=30)).next_to(sl, UP, 0.5)
        with self.voiceover(text=N("short1.b3")) as tr:
            self.play(FadeOut(VGroup(left, right, ll, rl, n8, n7)), run_time=0.4)
            self.play(FadeIn(sl.rows), FadeIn(sl_lab), run_time=0.5)
            self.play(LaggedStart(*[FadeIn(c, scale=0.8) for c in sl.chip_group], lag_ratio=0.05), run_time=1.0)
            self.wait(frac_time(tr, 0.2))
            mover = sl.chips["101"]
            self.play(mover.box.animate.set_fill(PRIMARY, 1), mover.lab.animate.set_color(BG), run_time=0.4)
            self.play(mover.animate.move_to(sl.slots["01"].get_center() + UP * 0.12), run_time=0.7)
            upper = VGroup(*[sl.slots[s] for s in shorter_strings(3)])
            self.play(LaggedStart(*[Indicate(s, color=SECONDARY, scale_factor=1.08) for s in upper],
                                  lag_ratio=0.05), run_time=1.2)
            wait_until(self, tr, "pushed")
            bumped = sl.chips["01"]
            self.play(bumped.animate.move_to(sl.slots["101"]), mover.animate.move_to(sl.slots["01"]), run_time=0.7)
            self.play(bumped.box.animate.set_fill(BAD, 1), run_time=0.3)
            grew = text("grew", size=30, color=BAD).next_to(sl.slots["101"], DOWN, 0.15)
            self.play(FadeIn(grew), run_time=0.3)
            rest(self, tr)

        bar = Rectangle(width=W, height=0.8, stroke_color=RAND_C, stroke_width=3).set_fill(RAND_C, 0.25)
        bar.move_to(UP * (MID + 0.6))
        sliver = Rectangle(width=0.1, height=0.8, stroke_width=0).set_fill(PRIMARY, 1).align_to(bar, LEFT)
        bt = tag("all files of one length", size=30).next_to(bar, UP, 0.3)
        sll = VGroup(text("shrink by 10 bits:", size=32, color=PRIMARY),
                     text("fewer than 1 in 500", size=32, color=PRIMARY)).arrange(DOWN, buff=0.12)
        sll.next_to(bar, DOWN, 1.1).align_to(bar, LEFT).shift(RIGHT * 0.3)
        sa = Arrow(sll.get_corner(UL) + UP * 0.1, sliver.get_bottom(), buff=0.08, color=PRIMARY, stroke_width=3,
                   tip_length=0.15)
        with self.voiceover(text=N("short1.b4")) as tr:
            self.play(FadeOut(VGroup(sl, sl_lab, grew)), run_time=0.4)
            self.play(FadeIn(bt), GrowFromEdge(bar, LEFT), run_time=0.7)
            wait_until(self, tr, "frac")
            self.play(FadeIn(sliver), GrowArrow(sa), FadeIn(sll), run_time=0.7)
            rest(self, tr)

        comp2 = compressor(w=2.4, h=1.4, size=30).move_to(UP * (MID + 1.6))
        fin = VGroup(text("almost every file", size=40, weight="BOLD"),
                     text("is random", size=40, weight="BOLD", color=RAND_C)).arrange(DOWN, buff=0.15)
        fin.move_to(UP * (MID - 1.2))
        with self.voiceover(text=N("short1.b5")) as tr:
            self.play(FadeOut(VGroup(bar, sliver, bt, sll, sa)), FadeIn(comp2), run_time=0.5)
            items = [(file_icon(1.0, 1.3, label="essay.txt"), file_icon(0.7, 0.9, label="smaller", label_size=20)),
                     (file_icon(1.0, 1.3, label="table.csv"), file_icon(0.7, 0.9, label="smaller", label_size=20))]
            outs = compress_demo(self, comp2, items, max(2.4, tr.time_until_bookmark("coin") - 0.5))
            wait_until(self, tr, "coin")
            self.play(FadeOut(outs[-1]), run_time=0.25)
            nf = file_icon(1.0, 1.3, noise=True, seed=9, label="coin flips")
            nf_out = file_icon(1.08, 1.4, noise=True, seed=9, color=BAD, label="a bit bigger", label_size=20)
            run_through(self, comp2, nf, nf_out, 1.5, gap=0.55)
            self.play(FadeIn(fin, shift=UP * 0.2), run_time=0.6)
            rest(self, tr)


# ---------------------------------------------------------------------------
# short2 The Berry paradox as a program
# ---------------------------------------------------------------------------


class Short2Berry(VoiceoverScene):
    def construct(self):
        self.set_speech_service(get_speech_service())
        ph = VGroup(text("the smallest number", size=44), text("that cannot be described", size=44),
                    text("in under sixty letters", size=44)).arrange(DOWN, buff=0.22)
        fit(ph).move_to(UP * (MID + 1.0))
        with self.voiceover(text=N("short2.b1")) as tr:
            self.play(FadeIn(ph), run_time=0.8)
            wait_until(self, tr, "count")
            cnt = letter_count(self, ph, UP * (MID - 1.2) + RIGHT * 0.2,
                               run_time=max(1.0, tr.get_remaining_duration() - 0.8), size=64)
            lt = math("< 60", size=56, color=BAD).next_to(cnt, DOWN, 0.3)
            self.play(FadeIn(lt), run_time=0.3)
            rest(self, tr)

        kd = fit(kdef_p(size=36)).move_to(UP * (MID + 0.5))
        sw = tag("words -> programs", size=34, color=PRIMARY).next_to(kd, UP, 0.8)
        with self.voiceover(text=N("short2.b2")) as tr:
            self.play(FadeOut(VGroup(ph, cnt, lt)), run_time=0.4)
            self.play(FadeIn(sw), run_time=0.5)
            wait_until(self, tr, "K")
            self.play(FadeIn(kd, shift=UP * 0.2), run_time=0.8)
            rest(self, tr)

        panel = fit(k_program(size=28)).move_to(UP * (MID + 0.6))
        with self.voiceover(text=N("short2.b3")) as tr:
            self.play(FadeOut(sw), FadeOut(kd), run_time=0.5)
            self.play(FadeIn(panel, shift=UP * 0.2), run_time=0.7)
            wait_until(self, tr, "first")
            hl = panel.box_part(3, "if K(x) > L:")
            self.play(Create(hl), run_time=0.5)
            rest(self, tr)

        lbox = SurroundingRectangle(panel.line(1), color=PRIMARY, buff=0.06, corner_radius=0.05)
        fixed = tag("everything else: a fixed size", size=30, color=FG).next_to(panel, DOWN, 0.35)
        ltx = mt("$L:\\ \\approx \\log_2 L", "bits", size=30, color=PRIMARY).next_to(fixed, DOWN, 0.25)
        bars = length_bars(prog_fixed=1.6, prog_l=0.3, l_len=7.6, size=28, l_label="L")
        bars.to_edge(LEFT, buff=0.3).next_to(ltx, DOWN, 0.8).to_edge(LEFT, buff=0.3)
        with self.voiceover(text=N("short2.b4")) as tr:
            self.play(FadeOut(hl), panel.animate.set_y(TOP - 0.3 - panel.height / 2), run_time=0.5)
            fixed.next_to(panel, DOWN, 0.35)
            ltx.next_to(fixed, DOWN, 0.25)
            bars.next_to(ltx, DOWN, 0.8).to_edge(LEFT, buff=0.3)
            lbox = SurroundingRectangle(panel.line(1), color=PRIMARY, buff=0.06, corner_radius=0.05)
            self.play(FadeIn(fixed), run_time=0.5)
            self.play(Create(lbox), FadeIn(ltx), run_time=0.6)
            self.play(FadeIn(bars.prog), FadeIn(bars.plab), run_time=0.5)
            self.play(GrowFromEdge(bars.lbar, LEFT), FadeIn(bars.llab), run_time=0.8)
            wait_until(self, tr, "short")
            sh = text("shorter", size=32, color=GOOD).next_to(bars.prog, RIGHT, 0.3)
            self.play(Indicate(bars.prog, color=GOOD), FadeIn(sh), run_time=0.8)
            rest(self, tr)
        bars.add(sh)

        cv = contra_vertical(("length", "$< L"), ("$K > L",), size=32).move_to(UP * (MID + 0.4))
        nk = VGroup(text("no program", size=44, color=BAD, weight="BOLD"),
                    text("computes K", size=44, color=BAD, weight="BOLD")).arrange(DOWN, buff=0.1)
        nk.next_to(cv, DOWN, 0.6)
        with self.voiceover(text=N("short2.b5")) as tr:
            self.play(FadeOut(VGroup(panel, lbox, fixed, ltx, bars)), run_time=0.4)
            self.play(FadeIn(cv.prog), GrowArrow(cv.arr), FadeIn(cv.out), run_time=0.8)
            self.play(FadeIn(cv.ol), run_time=0.4)
            self.wait(frac_time(tr, 0.12))
            self.play(FadeIn(cv.pl), run_time=0.4)
            x = cross(cv.arr.get_center() + RIGHT * 1.3, s=0.35, width=9)
            self.play(Create(x), run_time=0.4)
            wait_until(self, tr, "none")
            self.play(FadeIn(nk, shift=UP * 0.2), run_time=0.6)
            rest(self, tr)
        self.wait(0.3)


# ---------------------------------------------------------------------------
# short3 You can't prove a string is random
# ---------------------------------------------------------------------------


class Short3Chaitin(VoiceoverScene):
    def construct(self):
        self.set_speech_service(get_speech_service())
        strip = coin_strip(240, seed=5, size=34)
        strip.move_to(UP * (MID + 0.6)).set_x(-FW / 2 + strip.width / 2 - 0.3)
        lab = tag("a million coin flips", size=34).next_to(strip, UP, 0.5).set_x(0)
        rnd = text("almost surely random", size=38, color=RAND_C).next_to(strip, DOWN, 0.5).set_x(0)
        nv = VGroup(text("but you'll never", size=44, color=PRIMARY, weight="BOLD"),
                    text("prove it", size=44, color=PRIMARY, weight="BOLD")).arrange(DOWN, buff=0.1)
        nv.next_to(rnd, DOWN, 1.0)
        with self.voiceover(text=N("short3.b1")) as tr:
            self.add(strip)
            strip.add_updater(lambda m, dt: m.shift(LEFT * dt * 1.4))
            self.play(FadeIn(lab), run_time=0.5)
            self.wait(frac_time(tr, 0.15))
            self.play(FadeIn(rnd, shift=UP * 0.15), run_time=0.6)
            wait_until(self, tr, "never")
            self.play(FadeIn(nv, shift=UP * 0.2), run_time=0.6)
            rest(self, tr)
            strip.clear_updaters()

        panel = fit(proof_program(size=24)).move_to(UP * (TOP - 1.6))
        with self.voiceover(text=N("short3.b2")) as tr:
            self.play(FadeOut(VGroup(strip, lab, rnd, nv)), run_time=0.4)
            self.play(FadeIn(panel, shift=UP * 0.2), run_time=0.7)
            wait_until(self, tr, "claim")
            hl = panel.box_part(3, "if p proves K(x) > L:")
            self.play(Create(hl), run_time=0.5)
            rest(self, tr)

        fixed = VGroup(tag("axioms + proof checker:", size=30, color=FG),
                       tag("a fixed size", size=30, color=FG)).arrange(DOWN, buff=0.1).next_to(panel, DOWN, 0.4)
        lbox = SurroundingRectangle(panel.line(1), color=PRIMARY, buff=0.06, corner_radius=0.05)
        ltx = mt("$L:\\ \\approx \\log_2 L", "bits", size=30, color=PRIMARY).next_to(fixed, DOWN, 0.3)
        bars = length_bars(prog_fixed=1.9, prog_l=0.3, l_len=7.6, size=28, l_label="L bits")
        bars.next_to(ltx, DOWN, 0.8).to_edge(LEFT, buff=0.3)
        with self.voiceover(text=N("short3.b3")) as tr:
            self.play(FadeOut(hl), FadeIn(fixed), run_time=0.6)
            self.play(Create(lbox), FadeIn(ltx), run_time=0.6)
            self.play(FadeIn(bars.prog), FadeIn(bars.plab), run_time=0.5)
            self.play(GrowFromEdge(bars.lbar, LEFT), FadeIn(bars.llab), run_time=0.8)
            wait_until(self, tr, "short")
            sh = text("shorter", size=32, color=GOOD).next_to(bars.prog, RIGHT, 0.3)
            self.play(Indicate(bars.prog, color=GOOD), FadeIn(sh), run_time=0.8)
            rest(self, tr)
        bars.add(sh)

        cv = contra_vertical(("fewer than", "$L", "bits"), ("proven: needs more than", "$L"), size=30)
        fit(cv).move_to(UP * (MID + 0.9))
        wr = text("the proof would be wrong", size=40, color=BAD, weight="BOLD")
        fit(wr).next_to(cv, DOWN, 0.6)
        with self.voiceover(text=N("short3.b4")) as tr:
            self.play(FadeOut(VGroup(panel, fixed, lbox, ltx, bars)), run_time=0.4)
            self.play(FadeIn(cv.prog), FadeIn(cv.pl), run_time=0.6)
            self.play(GrowArrow(cv.arr), FadeIn(cv.out), FadeIn(cv.ol), run_time=0.7)
            wait_until(self, tr, "wrong")
            x = cross(cv.arr.get_center() + RIGHT * 1.3, s=0.35, width=9)
            self.play(Create(x), FadeIn(wr, shift=UP * 0.2), run_time=0.6)
            rest(self, tr)

        win = Rectangle(width=3.4, height=3.4, stroke_color=MUTED, stroke_width=2).move_to(UP * (MID + 1.6))
        stream = VGroup(*[text(f"proof #{i}", size=30, color=MUTED) for i in range(1, 15)]).arrange(DOWN, buff=0.22)
        stream.move_to(win.get_top() + DOWN * 0.2, aligned_edge=UP)
        mask_t = Rectangle(width=4.0, height=6.0, stroke_width=0).set_fill(BG, 1).next_to(win, UP, 0)
        mask_b = Rectangle(width=4.0, height=9.0, stroke_width=0).set_fill(BG, 1).next_to(win, DOWN, 0)
        mask_t.set_z_index(4)
        mask_b.set_z_index(4)
        win.set_z_index(5)
        sp = spinner(64).next_to(win, RIGHT, 0.25)
        sp.set_z_index(5)
        fin = VGroup(text("past about the size", size=36), text("of the axioms,", size=36),
                     text("no string can be", size=36), text("proven random", size=36, color=RAND_C)
                     ).arrange(DOWN, buff=0.12)
        fin.next_to(win, DOWN, 0.6).set_z_index(6)
        with self.voiceover(text=N("short3.b5")) as tr:
            self.play(FadeOut(VGroup(cv, wr, x)), run_time=0.4)
            sp.add_updater(lambda m, dt: m.rotate(-dt * 2.5))
            self.add(stream, mask_t, mask_b, win, sp)
            self.play(stream.animate.shift(UP * 2.0), FadeIn(fin), run_time=rt(tr.duration * 0.45), rate_func=linear)
            wait_until(self, tr, "almost")
            al = text("your coin flips: random, no proof", size=34, color=PRIMARY)
            fit(al).next_to(fin, DOWN, 0.4).set_z_index(6)
            self.play(stream.animate.shift(UP * 1.6), FadeIn(al), run_time=rt(tr.get_remaining_duration()),
                      rate_func=linear)
            sp.clear_updaters()
        self.wait(0.3)
