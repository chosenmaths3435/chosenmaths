"""Vertical shorts. Render with MV_ASPECT=portrait."""

import sys
from pathlib import Path

from manim import *
from manim_voiceover import VoiceoverScene

from mathvid import layout  # noqa: F401  must come before scene code runs
from mathvid.anim import rest, rt, wait_until
from mathvid.layout import SAFE_BOTTOM, SAFE_TOP
from mathvid.script import Script
from mathvid.style import BAD, FG, GOOD, MUTED, PRIMARY, SECONDARY, math, text
from mathvid.voice import get_speech_service

sys.path.insert(0, str(Path(__file__).parent))
from scenes import (  # noqa: E402
    ABOVE_STR,
    DEC,
    DEC_LIST,
    DEC_STR,
    ORB_LIST,
    SQ2,
    Z0,
    Z2,
    Z3,
    Z4,
    list_tex,
    make_zoomline,
    orbit_in,
    padic_defs,
    q2_symbol,
    refresh,
    ruler,
    set_of_lists,
    sum_tex,
    unit_square,
)

N = Script(__file__)

MID = (SAFE_TOP + SAFE_BOTTOM) / 2  # center of the safe area
LINE_Y = MID - 0.6


def short_row(size=38, n=5):
    terms = VGroup(*[math(t + ",", size=size) for t in DEC_STR[:n]] + [math(r"\dots", size=size)])
    return terms.arrange(RIGHT, buff=0.25, aligned_edge=DOWN)


# ---------------------------------------------------------------------------
# short1 A set of lists
# ---------------------------------------------------------------------------


class Short1SetOfLists(VoiceoverScene):
    def construct(self):
        self.set_speech_service(get_speech_service())

        lead = math(r"\sqrt{2} =", size=80).move_to(UP * (MID + 3.0))
        st = set_of_lists(size=34).next_to(lead, DOWN, buff=0.6)
        with self.voiceover(text=N("short1.b1")) as tr:
            self.play(Write(lead), run_time=0.6)
            self.play(FadeIn(st[0]), FadeIn(st[3]), FadeIn(st[2]),
                      LaggedStart(*[Write(r) for r in st[1]], lag_ratio=0.4), run_time=rt(min(2.0, tr.duration - 0.7)))
            rest(self, tr)

        usq, diag = unit_square(2.6)
        sqg = VGroup(usq, diag).move_to(UP * (MID + 2.2))
        stamp = text("not a fraction", size=40, color=BAD, weight="BOLD").rotate(0.25).move_to(diag)
        row = short_row().move_to(UP * (MID - 1.2))
        with self.voiceover(text=N("short1.b2")) as tr:
            self.play(FadeOut(VGroup(lead, st)), run_time=0.4)
            self.play(Create(usq[0]), FadeIn(usq[1]), Create(diag), run_time=0.8)
            wait_until(self, tr, "greek")
            self.play(FadeIn(stamp, scale=1.4), run_time=0.5)
            wait_until(self, tr, "digits")
            self.play(LaggedStart(*[FadeIn(t, shift=UP * 0.2) for t in row], lag_ratio=0.4),
                      run_time=rt(min(2.5, tr.get_remaining_duration())))
            rest(self, tr)

        zl, ring, dec_dots, orb_dots, arcs = make_zoomline(Z0, length=7.2, center=UP * LINE_Y, label_size=26)
        zl.hole_r.set_value(0)
        no_frac = text("no fraction here", size=30, color=MUTED)
        no_frac.add_updater(lambda m: m.next_to(zl.p(SQ2), UP, buff=0.4))
        with self.voiceover(text=N("short1.b3")) as tr:
            self.play(FadeOut(VGroup(usq[0], usq[1], diag, stamp)), row.animate.move_to(UP * (SAFE_TOP - 1.0)),
                      Create(zl.line), FadeIn(zl.ticks), run_time=0.8)
            self.add(*dec_dots)
            anims = [AnimationGroup(t.animate.move_to(zl.p(x)).scale(0.4).set_opacity(0), d.show.animate.set_value(1))
                     for t, x, d in zip(row[:-1], DEC, dec_dots)]
            self.play(LaggedStart(*anims, lag_ratio=0.5), FadeOut(row[-1]),
                      run_time=rt(min(2.0, tr.time_until_bookmark("crowd") - 0.8)))
            wait_until(self, tr, "crowd")
            self.play(*zl.zoom_to(*Z2), run_time=1.2)
            refresh(ring)
            no_frac.update()
            self.play(Create(ring), FadeIn(no_frac), zl.hole_r.animate.set_value(0.16), run_time=0.6)
            self.play(FadeOut(no_frac), *zl.zoom_to(*Z0), run_time=0.8)
            self.add(*orb_dots, *arcs)
            per = max(0.2, tr.get_remaining_duration() / (len(orb_dots) + 2 * 1.4))
            orbit_in(self, zl, orb_dots, arcs, per, zooms={2: Z3, 4: Z4})
            rest(self, tr)

        lab = math(r"\sqrt{2} :=", size=60, color=PRIMARY).move_to(UP * (MID + 1.4))
        lst = math(DEC_LIST, size=38).next_to(lab, DOWN, buff=0.5)
        with self.voiceover(text=N("short1.b4")) as tr:
            self.play(FadeOut(VGroup(zl, ring, *dec_dots, *orb_dots, *arcs)), run_time=0.5)
            self.play(FadeIn(lst), run_time=0.6)
            wait_until(self, tr, "def")
            self.play(Write(lab), run_time=0.7)
            rest(self, tr)

        rows = VGroup(math(DEC_LIST, size=34), math(ORB_LIST, size=34), math(list_tex(ABOVE_STR), size=34))
        rows.arrange(DOWN, buff=0.45).move_to(UP * (MID + 0.4))
        gaps = text("gaps shrink to 0", size=32, color=MUTED).next_to(rows, DOWN, buff=0.5)
        st2 = set_of_lists(size=34, rows=(DEC_LIST, ORB_LIST, list_tex(ABOVE_STR))).move_to(rows).shift(DOWN * 0.25)
        lead2 = math(r"\sqrt{2} =", size=64, color=PRIMARY).next_to(st2, UP, buff=0.5)
        with self.voiceover(text=N("short1.b5")) as tr:
            self.play(FadeOut(lab), ReplacementTransform(lst, rows[0]), run_time=0.6)
            self.play(FadeIn(rows[1:], shift=DOWN * 0.2, lag_ratio=0.4), run_time=1.0)
            wait_until(self, tr, "group")
            self.play(FadeIn(gaps), run_time=0.5)
            self.play(FadeOut(gaps), ReplacementTransform(rows, st2[1]), FadeIn(st2[2]),
                      GrowFromCenter(st2[0]), GrowFromCenter(st2[3]), Write(lead2), run_time=1.0)
            rest(self, tr)

        ones = math(r"(1,\ 1,\ 1,\ 1,\ \dots)", size=44)
        nines = math(r"(0.9,\ 0.99,\ 0.999,\ \dots)", size=44)
        pair = VGroup(ones, nines).arrange(DOWN, buff=0.6).move_to(UP * (MID + 1.4))
        res = math(r"0.999\ldots = 1", size=72, color=PRIMARY).next_to(pair, DOWN, buff=1.0)
        with self.voiceover(text=N("short1.b6")) as tr:
            self.play(Indicate(st2[0], color=PRIMARY), Indicate(st2[3], color=PRIMARY), run_time=0.8)
            wait_until(self, tr, "nines")
            self.play(FadeOut(VGroup(st2, lead2)), run_time=0.4)
            self.play(FadeIn(pair, lag_ratio=0.3), run_time=0.8)
            self.play(Write(res), run_time=0.8)
            rest(self, tr)
        self.wait(0.6)


# ---------------------------------------------------------------------------
# short2 Change the ruler
# ---------------------------------------------------------------------------


class Short2ChangeTheRuler(VoiceoverScene):
    def construct(self):
        self.set_speech_service(get_speech_service())

        s = sum_tex(50).move_to(UP * (MID + 2.4))
        with self.voiceover(text=N("short2.b1")) as tr:
            self.play(Write(s), run_time=rt(min(2.0, tr.duration)))
            rest(self, tr)

        cross = Cross(s, stroke_color=BAD, stroke_width=6)
        nl = NumberLine(x_range=[0, 16, 4], length=7, color=MUTED, include_numbers=True, font_size=30,
                        stroke_width=3).move_to(UP * (MID - 0.2))
        sums = [1, 3, 7, 15]
        dots = VGroup(*[Dot(nl.n2p(v), radius=0.09, color=PRIMARY) for v in sums])
        labs = VGroup(*[math(str(v), size=32, color=PRIMARY).next_to(d, UP, buff=0.25) for v, d in zip(sums, dots)])
        with self.voiceover(text=N("short2.b2")) as tr:
            wait_until(self, tr, "no")
            self.play(Create(cross), run_time=0.5)
            self.play(Create(nl), run_time=0.6)
            per = max(0.25, min(0.6, (tr.get_remaining_duration() - 0.5) / 4))
            for d, lab in zip(dots, labs):
                self.play(FadeIn(d, shift=RIGHT * 0.3), FadeIn(lab), run_time=per)
            rest(self, tr)

        nl2 = NumberLine(x_range=[-1, 3, 1], length=7, color=MUTED, include_numbers=True, font_size=30,
                         stroke_width=3).move_to(UP * (MID - 0.4))
        qm = math("?", size=90, color=MUTED).move_to(UP * (MID + 2.4))
        px, py = nl2.n2p(0.25), nl2.n2p(1.75)
        dx, dy = Dot(px, color=FG), Dot(py, color=FG)
        lx = math("x", size=40).next_to(dx, DOWN, buff=0.55)
        ly = math("y", size=40).next_to(dy, DOWN, buff=0.55)
        rl = ruler(px, py, r"|x - y|")
        with self.voiceover(text=N("short2.b3")) as tr:
            self.play(FadeOut(VGroup(s, cross, nl, dots, labs)), run_time=0.5)
            self.play(Create(nl2), FadeIn(qm), run_time=0.8)
            wait_until(self, tr, "ruler")
            self.play(FadeOut(qm), FadeIn(VGroup(dx, dy, lx, ly)), run_time=0.5)
            self.play(GrowFromCenter(rl[0]), FadeIn(rl[1]), Write(rl[2]), run_time=0.8)
            rest(self, tr)

        top = math(r"|x - y|", size=52, color=SECONDARY).move_to(UP * (SAFE_TOP - 0.6))
        zl, ring, dec_dots, _, _ = make_zoomline(Z3, length=7.2, center=UP * (MID + 0.6), label_size=26)
        filled = Dot(zl.p(SQ2), radius=0.13, color=PRIMARY)
        reals = math(r"\mathbb{R}", size=110, color=SECONDARY).move_to(UP * (MID - 1.8))
        with self.voiceover(text=N("short2.b4")) as tr:
            self.play(FadeOut(VGroup(nl2, dx, dy, lx, ly, rl[0], rl[1])), ReplacementTransform(rl[2], top),
                      run_time=0.6)
            self.play(Create(zl.line), FadeIn(zl.ticks), Create(ring), run_time=0.6)
            self.add(*dec_dots)
            self.play(LaggedStart(*[d.show.animate.set_value(1) for d in dec_dots], lag_ratio=0.4),
                      run_time=rt(min(2.0, tr.time_until_bookmark("reals") - 0.2)))
            wait_until(self, tr, "reals")
            self.play(FadeIn(filled, scale=0.3), Flash(filled, color=PRIMARY), run_time=0.6)
            self.play(Write(reals), run_time=0.6)
            rest(self, tr)

        defs = padic_defs(42).move_to(UP * (SAFE_TOP - 2.2))
        q2 = q2_symbol(130).move_to(UP * (MID - 1.2))
        with self.voiceover(text=N("short2.b5")) as tr:
            wait_until(self, tr, "swap")
            self.play(FadeOut(VGroup(zl, ring, filled, reals, *dec_dots)), FadeOut(top, shift=UP * 0.3),
                      run_time=0.5)
            self.play(FadeIn(defs, lag_ratio=0.2), FadeIn(q2), run_time=0.9)
            rest(self, tr)

        s2 = sum_tex(50)
        check = math(r"\checkmark", size=70, color=GOOD)
        q2_target = q2.copy().scale(0.9).move_to(UP * (SAFE_TOP - 1.4))
        s2.next_to(q2_target, DOWN, buff=0.9)
        check.next_to(s2, DOWN, buff=0.6)
        with self.voiceover(text=N("short2.b6")) as tr:
            self.play(FadeOut(defs), run_time=0.3)
            self.play(Transform(q2, q2_target), run_time=0.5)
            self.play(Write(s2), run_time=1.0)
            self.wait(rt(tr.get_remaining_duration() - 1.2))
            self.play(FadeIn(check, scale=1.5), run_time=0.5)
            rest(self, tr)
        self.wait(0.8)
