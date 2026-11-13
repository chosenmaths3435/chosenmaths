"""Vertical shorts. Render with MV_ASPECT=portrait."""

import sys
from pathlib import Path

from manim import *
from manim_voiceover import VoiceoverScene

from mathvid import layout  # noqa: F401  must come before scene code runs
from mathvid.anim import rest, rt, wait_until
from mathvid.code import CodePanel
from mathvid.layout import FW, SAFE_BOTTOM, SAFE_TOP
from mathvid.orders import cross, tick
from mathvid.script import Script
from mathvid.style import BAD, FG, GOOD, MUTED, PRIMARY, SECONDARY, math, text
from mathvid.voice import get_speech_service

sys.path.insert(0, str(Path(__file__).parent))
from scenes import (  # noqa: E402
    AckTable,
    DiagTable,
    Ladder,
    call_moves,
    dial_pair,
    frac_time,
    nested_loops,
    rules_block,
    tag,
)

N = Script(__file__)

MID = (SAFE_TOP + SAFE_BOTTOM) / 2
TOP = SAFE_TOP - 0.4
W = FW - 0.9


def fit(m, w=W):
    return m.scale_to_fit_width(min(m.width, w))


SHORT_LABELS = ["counting", "adds", "doubles", "powers of 2", "towers of 2s"]


def moves_portrait(size=32):
    """The three moves, each with its note underneath."""
    items = [(r"(m+1,\,0) \to (m,\,1)", "first drops", PRIMARY),
             (r"(m+1,\,n+1) \to (m+1,\,n)", "first stays, second drops", SECONDARY),
             (r"(m+1,\,n+1) \to (m,\,\ldots)", "first drops", PRIMARY)]
    order = [0, 2, 1]
    rows = [VGroup(math(e, size=size), tag(t_, size=size - 4, color=c)).arrange(DOWN, buff=0.12)
            for e, t_, c in items]
    g = VGroup(*rows).arrange(DOWN, buff=0.4)
    return g


class Short1Loops(VoiceoverScene):
    def construct(self):
        self.set_speech_service(get_speech_service())
        lad = Ladder(n_rungs=7, gap=0.95, width=1.1, size=34, label_buff=0.3)
        fit(lad, FW - 1.4).move_to([0, MID - 0.2, 0])
        with self.voiceover(text=N("short1.b1")) as tr:
            self.play(Create(lad.rails), run_time=0.4)
            per = rt(min(1.6, tr.duration * 0.16))
            for i in range(3):
                self.play(Create(lad.rungs[i]), FadeIn(lad.labels[i]), run_time=per)
            self.play(LaggedStart(*[AnimationGroup(Create(lad.rungs[i]), FadeIn(lad.labels[i]))
                                    for i in range(3, 7)], lag_ratio=0.3), run_time=1.2)
            wait_until(self, tr, "ack")
            name = text("the Ackermann function", size=40, color=PRIMARY, weight="BOLD")
            name.move_to([0, TOP, 0])
            self.play(FadeIn(name, shift=DOWN * 0.2), run_time=0.6)
            rest(self, tr)

        tbl = AckTable(rows=5, cols=3, size=38, labels=SHORT_LABELS, label_size=32, max_col_w=2.2, row_h=0.85)
        fit(tbl).move_to([0, MID + 0.9, 0])
        atoms = VGroup(math("A(4, 3)", size=40, color=PRIMARY),
                       text("more digits than atoms\nin the universe", size=30, color=BAD, line_spacing=0.8)
                       ).arrange(DOWN, buff=0.25).next_to(tbl, DOWN, 0.6)
        with self.voiceover(text=N("short1.b2")) as tr:
            self.play(FadeOut(lad), name.animate.scale(0.8), run_time=0.5)
            self.play(FadeIn(tbl.grid), FadeIn(tbl.col_hdr), FadeIn(tbl.row_hdr), FadeIn(tbl.row(0)),
                      FadeIn(tbl.labels[0]), run_time=0.6)
            t_tow = tr.time_until_bookmark("towers")
            per = rt(max(0.4, (t_tow - 0.3) / 4))
            for m in range(1, 5):
                self.play(FadeIn(tbl.row(m)), FadeIn(tbl.labels[m]), run_time=per)
            wait_until(self, tr, "towers")
            self.play(Indicate(tbl.labels[4], color=PRIMARY), run_time=0.6)
            self.play(FadeIn(atoms, shift=UP * 0.2), run_time=0.7)
            rest(self, tr)

        fl = CodePanel(["repeat n times:", "    ..."], size=34).move_to([0, TOP - 0.9, 0])
        fixed = tag("count fixed before it starts", size=28, color=PRIMARY).next_to(fl, DOWN, 0.3)
        nest = nested_loops(3, size=28, core="...")
        nest.next_to(fixed, DOWN, 0.6)
        rows = VGroup(*[tag(f"+1 row", size=28, color=nest.boxes[i].get_color()) for i in range(3)])
        for i in range(3):
            rows[i].next_to(nest.boxes[-1], RIGHT, 0.25).match_y(nest.heads[i])
        grp = VGroup(nest, rows)
        grp.move_to([0, grp.get_center()[1], 0])
        stuck = text("stuck below some row m", size=34, color=PRIMARY).next_to(grp, DOWN, 0.6)
        with self.voiceover(text=N("short1.b3")) as tr:
            self.play(FadeOut(VGroup(tbl, atoms, name)), run_time=0.5)
            self.play(FadeIn(fl, shift=UP * 0.2), FadeIn(fixed), run_time=0.6)
            self.play(FadeIn(nest.core), *[Create(b) for b in nest.boxes], *[FadeIn(h) for h in nest.heads],
                      run_time=0.8)
            wait_until(self, tr, "row")
            for i in range(3):
                self.play(Indicate(nest.boxes[i], color=nest.boxes[i].get_color(), scale_factor=1.03),
                          FadeIn(rows[i]), run_time=0.5)
            self.play(FadeIn(stuck, shift=UP * 0.15), run_time=0.6)
            rest(self, tr)

        tb = AckTable(rows=4, cols=4, size=34)
        fit(tb).move_to([0, MID + 1.6, 0])
        dboxes = VGroup(*[SurroundingRectangle(tb.cell(k, k), buff=0.1, color=PRIMARY, stroke_width=4)
                          for k in range(4)])
        l1 = math(r"\text{diag}(m) < A(m, m)", size=44).next_to(tb, DOWN, 0.8)
        l2 = math(r"\text{diag}(m) = A(m, m)", size=44).next_to(l1, DOWN, 0.4)
        x = cross(VGroup(l1, l2).get_right() + RIGHT * 0.55, s=0.35, width=8)
        with self.voiceover(text=N("short1.b4")) as tr:
            self.play(FadeOut(VGroup(fl, fixed, grp, stuck)), run_time=0.5)
            self.play(FadeIn(tb), run_time=0.5)
            self.play(LaggedStart(*[Create(b) for b in dboxes], lag_ratio=0.35), run_time=1.4)
            t_less = tr.time_until_bookmark("less")
            self.play(FadeIn(l2), run_time=0.6)
            wait_until(self, tr, "less")
            self.play(FadeIn(l1), run_time=0.6)
            self.play(Create(x), run_time=0.5)
            rest(self, tr)

        msg = VGroup(text("always stops", size=46, color=GOOD), text("computable", size=46, color=GOOD),
                     text("no for-loop", size=46, color=BAD)).arrange(DOWN, buff=0.45).move_to([0, MID, 0])
        with self.voiceover(text=N("short1.b5")) as tr:
            self.play(FadeOut(VGroup(tb, dboxes, l1, l2, x)), run_time=0.5)
            per = rt(min(1.2, tr.duration * 0.22))
            for m_ in msg:
                self.play(FadeIn(m_, shift=UP * 0.2), run_time=per)
            rest(self, tr)
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.4)


class Short2Stops(VoiceoverScene):
    def construct(self):
        self.set_speech_service(get_speech_service())
        rb = rules_block(size=40, numbered=False)
        fit(rb).move_to([0, TOP - 0.8, 0])
        with self.voiceover(text=N("short2.b1")) as tr:
            self.play(FadeIn(rb, shift=DOWN * 0.2), run_time=0.8)
            wait_until(self, tr, "stop")
            q = text("always stops?", size=46, color=PRIMARY).next_to(rb, DOWN, 1.0)
            self.play(FadeIn(q, scale=1.2), run_time=0.6)
            rest(self, tr)

        mv = moves_portrait(size=36)
        fit(mv).next_to(rb, DOWN, 0.7)
        with self.voiceover(text=N("short2.b2")) as tr:
            self.play(FadeOut(q), run_time=0.3)
            wait_until(self, tr, "first")
            self.play(FadeIn(mv[0]), FadeIn(mv[2]), run_time=0.7)
            self.wait(frac_time(tr, 0.15))
            self.play(FadeIn(mv[1]), run_time=0.6)
            rest(self, tr)

        dm, dn = dial_pair(size=72, gap=0.8)
        dials = VGroup(dm, dn).move_to([0, MID + 0.6, 0])
        huge = tag("however huge", size=32, color=SECONDARY).next_to(dn, DOWN, 0.4)
        with self.voiceover(text=N("short2.b3")) as tr:
            self.play(FadeOut(VGroup(rb, mv)), run_time=0.4)
            self.play(FadeIn(dials), run_time=0.5)
            t_jump = tr.time_until_bookmark("jump")
            self.play(dn.tr.animate.set_value(0), run_time=rt(min(2.0, t_jump * 0.6)), rate_func=linear)
            wait_until(self, tr, "jump")
            self.play(dm.tr.animate.set_value(1), dn.tr.animate.set_value(61), run_time=0.6)
            self.play(FadeIn(huge), run_time=0.4)
            self.play(dn.tr.animate.set_value(30), run_time=rt(tr.get_remaining_duration()), rate_func=linear)

        ends = text("every chain of calls ends", size=38, color=FG).next_to(dials, DOWN, 1.3)
        with self.voiceover(text=N("short2.b4")) as tr:
            self.play(dn.tr.animate.set_value(0), run_time=rt(tr.duration * 0.3), rate_func=linear)
            self.play(dm.tr.animate.set_value(0), dn.tr.animate.set_value(9), run_time=0.5)
            self.play(dn.tr.animate.set_value(0), run_time=rt(tr.duration * 0.2), rate_func=linear)
            wait_until(self, tr, "ends")
            self.play(FadeOut(huge), FadeIn(ends, shift=UP * 0.15), run_time=0.6)
            stops = VGroup(tick(at=ORIGIN, s=1.2), text("always stops", size=40, color=GOOD)).arrange(RIGHT, 0.3)
            stops.next_to(ends, DOWN, 0.5)
            self.play(FadeIn(stops), run_time=0.5)
            rest(self, tr)

        fl = CodePanel(["repeat n times:", "    ..."], size=34).next_to(dials, UP, 0.9)
        fx = cross(fl.get_center(), s=0.6, width=8)
        with self.voiceover(text=N("short2.b5")) as tr:
            self.play(FadeIn(fl), run_time=0.6)
            self.wait(frac_time(tr, 0.4))
            self.play(Create(fx), run_time=0.5)
            rest(self, tr)
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.4)


class Short3Diagonal(VoiceoverScene):
    def construct(self):
        self.set_speech_service(get_speech_service())
        box = RoundedRectangle(corner_radius=0.25, width=W, height=2.2, color=SECONDARY, stroke_width=4)
        bt = text("a language where\nevery program stops", size=38, color=SECONDARY, line_spacing=0.8).move_to(box)
        bx = VGroup(box, bt).move_to([0, MID + 1.0, 0])
        miss = text("missing something", size=40, color=PRIMARY).next_to(bx, DOWN, 0.6)
        with self.voiceover(text=N("short3.b1")) as tr:
            self.play(Create(box), FadeIn(bt), run_time=0.8)
            wait_until(self, tr, "miss")
            self.play(FadeIn(miss, shift=UP * 0.15), run_time=0.6)
            rest(self, tr)

        dt = DiagTable(k=4, size=40, cw=1.25, rh=0.85)
        fit(dt).move_to([0, MID, 0]).align_to([0, SAFE_TOP - 1.0, 0], UP)
        with self.voiceover(text=N("short3.b2")) as tr:
            self.play(FadeOut(VGroup(bx, miss)), run_time=0.4)
            self.play(FadeIn(dt.cols), FadeIn(dt.inp), run_time=0.4)
            wait_until(self, tr, "list")
            self.play(LaggedStart(*[FadeIn(r) for r in dt.rows], lag_ratio=0.3), FadeIn(dt.vdots),
                      FadeIn(dt.hdots), run_time=1.4)
            rest(self, tr)

        with self.voiceover(text=N("short3.b3")) as tr:
            self.play(LaggedStart(*[Create(b) for b in dt.diag], lag_ratio=0.3), run_time=1.2)
            wait_until(self, tr, "plus")
            self.play(FadeIn(dt.d_lab),
                      LaggedStart(*[TransformFromCopy(dt.vals[j][j], dt.d_vals[j]) for j in range(4)],
                                  lag_ratio=0.25), run_time=1.4)
            p1 = tag("diagonal + 1", size=30, color=PRIMARY).next_to(dt, DOWN, 0.4)
            self.play(FadeIn(p1), run_time=0.4)
            rest(self, tr)

        with self.voiceover(text=N("short3.b4")) as tr:
            per = rt(min(0.8, tr.time_until_bookmark("every") / 3))
            for j in range(4):
                self.play(FadeIn(dt.neq[j]), Indicate(dt.diag[j], color=BAD), Indicate(dt.d_vals[j], color=BAD),
                          run_time=per)
            notin = text("not in the language", size=40, color=BAD).move_to([0, SAFE_TOP - 0.35, 0])
            self.play(FadeIn(notin), run_time=0.5)
            rest(self, tr)

        msg = text("to compute everything\ncomputable, programs must\nbe allowed to run forever", size=40,
                   color=FG, line_spacing=0.8).move_to([0, MID, 0])
        fit(msg)
        with self.voiceover(text=N("short3.b5")) as tr:
            self.play(FadeOut(Group(*self.mobjects)), run_time=0.5)
            self.play(FadeIn(msg, shift=UP * 0.2), run_time=0.8)
            wait_until(self, tr, "forever")
            self.play(Indicate(msg, color=PRIMARY, scale_factor=1.03), run_time=0.8)
            rest(self, tr)
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.4)
