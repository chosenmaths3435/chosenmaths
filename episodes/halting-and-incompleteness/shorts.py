"""Vertical shorts. Render with MV_ASPECT=portrait."""

import sys
from pathlib import Path

import numpy as np
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
    GODEL,
    HALT_C,
    LOOP_C,
    PROOF_CODE,
    SENT,
    SENT_CODE,
    card,
    code_table,
    frac_time,
    g_box,
    loop_icon,
    mbox,
    proof_card,
    proof_stream,
    stop_icon,
    tag,
    tick,
    xout,
)

N = Script(__file__)

MID = (SAFE_TOP + SAFE_BOTTOM) / 2  # center of the safe area
TOP = SAFE_TOP - 0.6


def code_lines(size=26):
    lines = ["n = input()", "while n != 1:", "    if n % 2 == 0:", "        n = n // 2",
             "    else:", "        n = 3 * n + 1", "print(\"done\")"]
    body = VGroup(*[Text(l.strip(), font="DejaVu Sans Mono", font_size=size, color=FG) for l in lines])
    body.arrange(DOWN, buff=0.12, aligned_edge=LEFT)
    cw = Text("x", font="DejaVu Sans Mono", font_size=size).width * 1.25
    for t, l in zip(body, lines):
        t.shift(RIGHT * cw * (len(l) - len(l.lstrip())))
    box = SurroundingRectangle(body, buff=0.3, corner_radius=0.15, color=MUTED, stroke_width=3)
    return VGroup(box, body)


def d_machine_p():
    """Portrait D: H on top, the switch underneath."""
    h = mbox("H", color=PRIMARY, w=1.8, h=1.2)
    sw_h = text('"halts"', size=30, color=HALT_C)
    sw_l = text('"loops"', size=30, color=LOOP_C)
    VGroup(sw_h, sw_l).arrange(RIGHT, buff=1.6).next_to(h, DOWN, 1.0)
    a_h = Arrow(h.get_bottom(), sw_h.get_top(), buff=0.12, color=MUTED, stroke_width=3)
    a_l = Arrow(h.get_bottom(), sw_l.get_top(), buff=0.12, color=MUTED, stroke_width=3)
    loop = loop_icon(64).next_to(sw_h, DOWN, 0.7)
    stop = stop_icon(0.32).next_to(sw_l, DOWN, 0.75)
    ah2 = Arrow(sw_h.get_bottom(), loop.get_top(), buff=0.1, color=MUTED, stroke_width=3)
    al2 = Arrow(sw_l.get_bottom(), stop.get_top(), buff=0.1, color=MUTED, stroke_width=3)
    inner = VGroup(h, a_h, a_l, sw_h, sw_l, ah2, al2, loop, stop)
    d = SurroundingRectangle(inner, buff=0.45, corner_radius=0.25, color=SECONDARY, stroke_width=4)
    dl = math("D", size=52, color=SECONDARY).next_to(d, UP, 0.12).align_to(d, LEFT).shift(RIGHT * 0.2)
    g = VGroup(d, dl, inner)
    g.d, g.dl, g.h = d, dl, h
    g.parts = (a_h, sw_h, ah2, loop, a_l, sw_l, al2, stop)
    g.halts_branch = VGroup(a_h, sw_h, ah2, loop)
    g.loops_branch = VGroup(a_l, sw_l, al2, stop)
    g.loop, g.stop = loop, stop
    return g


# ---------------------------------------------------------------------------
# short1 The halting problem
# ---------------------------------------------------------------------------


class Short1Halting(VoiceoverScene):
    def construct(self):
        self.set_speech_service(get_speech_service())
        code = code_lines().move_to(UP * (MID + 1.2))
        q = text("does it ever stop?", size=44, color=PRIMARY).next_to(code, DOWN, 0.6)
        with self.voiceover(text=N("short1.b1")) as tr:
            self.add(code)
            wait_until(self, tr, "stop")
            self.play(FadeIn(q, shift=UP * 0.2), run_time=0.6)
            rest(self, tr)

        lab = text("steps:", size=38, color=MUTED)
        cnt = [math(s, size=50) for s in ("10", "1000", "1000000")]
        row = VGroup(lab, cnt[0]).arrange(RIGHT, buff=0.3).move_to(UP * (MID - 1.6))
        for c in cnt[1:]:
            c.move_to(cnt[0], aligned_edge=LEFT)
        qm = text("?", size=72, color=PRIMARY).next_to(row, DOWN, 0.4)
        nxt = math("1000001", size=40, color=PRIMARY).set_opacity(0.6).next_to(qm, DOWN, 0.3)
        with self.voiceover(text=N("short1.b2")) as tr:
            self.play(FadeOut(q), code.animate.shift(UP * 0.6), FadeIn(row), run_time=0.6)
            self.play(Transform(cnt[0], cnt[1]), run_time=0.5)
            self.wait(frac_time(tr, 0.08))
            self.play(Transform(cnt[0], cnt[2]), run_time=0.5)
            wait_until(self, tr, "nothing")
            self.play(FadeIn(qm, scale=1.4), run_time=0.5)
            self.wait(frac_time(tr, 0.05))
            self.play(FadeIn(nxt), run_time=0.6)
            rest(self, tr)
        self.play(FadeOut(VGroup(code, row, qm, nxt)), run_time=0.5)

        h = mbox("H", color=PRIMARY, w=2.0, h=1.4).move_to(UP * (MID + 0.4))
        ins = VGroup(text("a program", size=32), text("an input", size=32)).arrange(RIGHT, buff=0.8)
        ins.next_to(h, UP, 1.0)
        ia = VGroup(*[Arrow(x.get_bottom(), h.get_top(), buff=0.12, color=MUTED, stroke_width=3) for x in ins])
        outs = [text('"halts"', size=40, color=HALT_C), text('"loops"', size=40, color=LOOP_C)]
        for o in outs:
            o.next_to(h, DOWN, 1.0)
        oa = Arrow(h.get_bottom(), outs[0].get_top(), buff=0.12, color=MUTED, stroke_width=3)
        tk = tick(48).next_to(outs[0], RIGHT, 0.3)
        with self.voiceover(text=N("short1.b3")) as tr:
            self.play(FadeIn(h), FadeIn(ins), GrowArrow(ia[0]), GrowArrow(ia[1]), run_time=0.8)
            wait_until(self, tr, "h")
            self.play(GrowArrow(oa), FadeIn(outs[0]), run_time=0.5)
            self.play(Transform(outs[0], outs[1].copy().move_to(outs[0])), FadeIn(tk), run_time=0.6)
            rest(self, tr)
        self.play(FadeOut(VGroup(ins, ia, outs[0], oa, tk)), run_time=0.4)

        dm = d_machine_p().move_to(UP * (MID - 0.3))
        prog = math(r"P", size=50).next_to(dm.d, UP, 0.9)
        pa = Arrow(prog.get_bottom(), dm.h.get_top(), buff=0.12, color=MUTED, stroke_width=3)
        with self.voiceover(text=N("short1.b4")) as tr:
            self.play(ReplacementTransform(h, dm.h), run_time=0.6)
            self.play(Create(dm.d), FadeIn(dm.dl), FadeIn(prog), GrowArrow(pa), run_time=0.8)
            wait_until(self, tr, "opposite")
            a_h, sw_h, ah2, loop, a_l, sw_l, al2, stop = dm.parts
            self.play(GrowArrow(a_h), FadeIn(sw_h), GrowArrow(ah2), FadeIn(loop), run_time=0.7)
            self.play(Rotate(loop, -TAU), run_time=0.7)
            self.play(GrowArrow(a_l), FadeIn(sw_l), GrowArrow(al2), FadeIn(stop), run_time=0.7)
            rest(self, tr)

        dd = math(r"\langle D\rangle", size=50, color=SECONDARY).move_to(prog)
        with self.voiceover(text=N("short1.b5")) as tr:
            self.play(ReplacementTransform(prog, dd), run_time=0.6)
            self.wait(frac_time(tr, 0.1))
            self.play(Indicate(dm.halts_branch, color=PRIMARY), Rotate(dm.loop, -TAU), run_time=0.8)
            x1 = xout(dm.halts_branch, pad=0.05, width=5)
            self.play(Create(x1), run_time=0.3)
            self.play(Indicate(dm.loops_branch, color=PRIMARY), run_time=0.7)
            x2 = xout(dm.loops_branch, pad=0.05, width=5)
            self.play(Create(x2), run_time=0.3)
            wait_until(self, tr, "wrong")
            xh = xout(dm.h)
            self.play(Create(xh), run_time=0.5)
            rest(self, tr)

        res = VGroup(text("the halting problem:", size=40, color=PRIMARY, weight="BOLD"),
                     text("no program solves it", size=40, color=PRIMARY)).arrange(DOWN, buff=0.2)
        res.move_to(UP * (MID + 2.6))
        db = mbox("D", color=SECONDARY, w=2.2, h=1.6).move_to(UP * (MID - 0.8))
        din = math(r"\langle D\rangle", size=48, color=SECONDARY).next_to(db, LEFT, 1.0)
        back = CurvedArrow(db.get_bottom() + DOWN * 0.1, din.get_bottom() + DOWN * 0.15, angle=-PI / 2,
                           color=PRIMARY, stroke_width=4)
        a_in = Arrow(din.get_right(), db.get_left(), buff=0.15, color=MUTED, stroke_width=3)
        with self.voiceover(text=N("short1.b6")) as tr:
            self.play(FadeOut(VGroup(dm, dd, x1, x2, xh, pa)), run_time=0.5)
            self.play(FadeIn(res), run_time=0.7)
            self.play(FadeIn(db), FadeIn(din), GrowArrow(a_in), run_time=0.6)
            wait_until(self, tr, "read")
            self.play(Create(back), run_time=0.7)
            self.play(back.animate.set_stroke(width=8), din.animate.set_color(PRIMARY), run_time=0.5)
            rest(self, tr)
        self.wait(0.6)


# ---------------------------------------------------------------------------
# short2 A true statement with no proof
# ---------------------------------------------------------------------------


class Short2Godel(VoiceoverScene):
    def construct(self):
        self.set_speech_service(get_speech_service())
        rules = card(["your rules", "axiom 1", "axiom 2", "axiom 3", "..."], size=30)
        rules.body[0].set_color(PRIMARY)
        rules.move_to(UP * (MID + 2.0))
        hidden = RoundedRectangle(corner_radius=0.18, width=4.6, height=1.0, color=PRIMARY, stroke_width=4)
        hlab = math("G", size=48, color=PRIMARY).next_to(hidden, LEFT, 0.3)
        hq = text("?", size=44, color=PRIMARY).move_to(hidden)
        gg = VGroup(hidden, hlab, hq).move_to(UP * (MID - 1.2))
        tg = VGroup(text("true", size=34, color=GOOD), text("no proof", size=34, color=BAD)).arrange(RIGHT, buff=0.8)
        tg.next_to(gg, DOWN, 0.4)
        with self.voiceover(text=N("short2.b1")) as tr:
            self.add(rules, gg)
            self.play(FadeIn(tg), run_time=0.5)
            rest(self, tr)
        self.play(FadeOut(VGroup(rules, tg)), gg.animate.move_to(UP * (SAFE_TOP - 0.8)).scale(0.7), run_time=0.5)

        pc = proof_card(size=30, dy=0.62, tags=False).move_to(UP * (MID + 0.3))
        mech = tag("a machine can check it", size=34, color=PRIMARY).next_to(pc, DOWN, 0.6)
        with self.voiceover(text=N("short2.b2")) as tr:
            self.play(LaggedStart(*[FadeIn(r, shift=RIGHT * 0.2) for r in pc], lag_ratio=0.2), run_time=1.2)
            wait_until(self, tr, "mech")
            for r in pc:
                self.play(FadeIn(tick(30).next_to(r[0], LEFT, 0.25)), run_time=0.25)
            self.play(FadeIn(mech), run_time=0.4)
            rest(self, tr)
        self.play(FadeOut(Group(*[m for m in self.mobjects if m is not gg])), run_time=0.4)

        ct = code_table(34).scale_to_fit_width(FW - 1.2).move_to(UP * (MID + 2.0))
        fs = math(SENT, size=50).move_to(UP * (MID + 0.2))
        sc = math(SENT_CODE, size=48, color=PRIMARY).move_to(fs)
        st = VGroup(text("this number codes a proof", size=32), text("of that statement", size=32)).arrange(DOWN, buff=0.1)
        st.move_to(UP * (MID - 1.6))
        stag = tag("a statement about numbers", size=32, color=PRIMARY).next_to(st, DOWN, 0.35)
        with self.voiceover(text=N("short2.b3")) as tr:
            self.play(LaggedStart(*[FadeIn(c) for c in ct], lag_ratio=0.12), run_time=1.2)
            self.play(FadeIn(fs), run_time=0.4)
            wait_until(self, tr, "code")
            self.play(ReplacementTransform(fs, sc), run_time=0.8)
            self.wait(frac_time(tr, 0.05))
            self.play(FadeIn(st), run_time=0.6)
            self.play(FadeIn(stag), run_time=0.5)
            rest(self, tr)
        self.play(FadeOut(VGroup(ct, sc, st, stag)), FadeOut(gg), run_time=0.4)

        g = g_box("G has no proof.", size=40).move_to(UP * (MID + 2.2))
        with self.voiceover(text=N("short2.b4")) as tr:
            wait_until(self, tr, "g")
            self.play(FadeIn(g.box), FadeIn(g.body), FadeIn(g.lab), run_time=0.6)
            self.play(Create(g.arc), run_time=0.5)
            rest(self, tr)

        sup = text("suppose G has a proof", size=34).move_to(UP * (MID + 0.5))
        bad = text("the rules proved something false", size=30, color=BAD).next_to(sup, DOWN, 0.6)
        ab = Arrow(sup.get_bottom(), bad.get_top(), buff=0.1, color=MUTED, stroke_width=3)
        np_ = VGroup(text("G has no proof", size=36), tick(40)).arrange(RIGHT, buff=0.2).next_to(bad, DOWN, 0.9)
        gtrue = text("G is true", size=44, color=GOOD, weight="BOLD").next_to(np_, DOWN, 0.5)
        with self.voiceover(text=N("short2.b5")) as tr:
            self.play(FadeIn(sup), run_time=0.5)
            self.play(GrowArrow(ab), FadeIn(bad), run_time=0.6)
            self.play(Create(xout(bad, width=5)), run_time=0.4)
            self.play(FadeIn(np_, shift=UP * 0.2), run_time=0.6)
            self.play(Indicate(g.body, color=PRIMARY), Indicate(np_[0], color=PRIMARY), run_time=0.8)
            wait_until(self, tr, "true")
            self.play(FadeIn(gtrue, scale=1.2), run_time=0.6)
            rest(self, tr)

        ax = card(["axioms", "+ G"], size=34).move_to(UP * (MID + 1.4))
        g1 = text("G' has no proof", size=36).next_to(ax, DOWN, 0.6)
        g2 = text("G'' has no proof", size=36).next_to(g1, DOWN, 0.3)
        g3 = math(r"\vdots", size=40).next_to(g2, DOWN, 0.25)
        with self.voiceover(text=N("short2.b6")) as tr:
            self.play(FadeOut(Group(*[m for m in self.mobjects if m is not g])), run_time=0.4)
            self.play(FadeOut(g), FadeIn(ax), run_time=0.7)
            wait_until(self, tr, "new")
            self.play(FadeIn(g1), run_time=0.5)
            self.play(FadeIn(g2), FadeIn(g3), run_time=0.6)
            rest(self, tr)
        self.wait(0.6)


# ---------------------------------------------------------------------------
# short3 The same theorem
# ---------------------------------------------------------------------------


class Short3Same(VoiceoverScene):
    def construct(self):
        self.set_speech_service(get_speech_service())
        gl = VGroup(text(f"{GODEL}:", size=40, color=SECONDARY), text("incompleteness", size=44, weight="BOLD"))
        gl.arrange(DOWN, buff=0.15)
        tl = VGroup(text("Turing:", size=40, color=SECONDARY), text("the halting problem", size=44, weight="BOLD"))
        tl.arrange(DOWN, buff=0.15)
        gl.move_to(UP * (MID + 1.8))
        tl.move_to(UP * (MID - 1.2))
        with self.voiceover(text=N("short3.b1")) as tr:
            self.add(gl, tl)
            wait_until(self, tr, "disguise")
            self.play(gl.animate.move_to(tl).set_opacity(0.85), tl.animate.set_opacity(0.35), run_time=0.9)
            rest(self, tr)
        self.play(FadeOut(VGroup(gl, tl)), run_time=0.4)

        p = mbox("program", w=3.0, h=1.2, size=34, tex=False).move_to(UP * (MID + 1.8))
        q = text("does it ever stop?", size=38, color=PRIMARY).next_to(p, DOWN, 0.4)
        h = mbox("H", color=PRIMARY, w=1.6, h=1.2).move_to(UP * (MID - 1.2))
        with self.voiceover(text=N("short3.b2")) as tr:
            self.play(FadeIn(p), FadeIn(q), run_time=0.6)
            wait_until(self, tr, "stop")
            self.play(FadeIn(h), run_time=0.5)
            self.play(Create(xout(h)), run_time=0.5)
            rest(self, tr)
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.4)

        ps = mbox("proof checker", w=4.4, h=1.4, size=34, tex=False).move_to(UP * (MID - 0.8))
        cards = proof_stream(5, size=32)
        with self.voiceover(text=N("short3.b3")) as tr:
            self.play(FadeIn(ps), run_time=0.5)
            wait_until(self, tr, "search")
            step = max(0.3, tr.get_remaining_duration() / 5)
            for c in cards:
                c.move_to(ps.get_top() + UP * 1.0)
                self.play(FadeIn(c, shift=RIGHT * 2.0), run_time=step * 0.5)
                self.play(FadeOut(c, shift=DOWN * 0.4), Indicate(ps.box, color=PRIMARY, scale_factor=1.02),
                          run_time=step * 0.5)
        self.play(FadeOut(ps), run_time=0.3)

        a = text('"this program halts"', size=40).move_to(UP * (MID + 1.4))
        b = VGroup(text("a statement", size=40, color=PRIMARY), text("about numbers", size=40, color=PRIMARY))
        b.arrange(DOWN, buff=0.12).move_to(UP * (MID - 0.8))
        ar = Arrow(a.get_bottom(), b.get_top(), buff=0.2, color=MUTED, stroke_width=4)
        with self.voiceover(text=N("short3.b4")) as tr:
            self.play(FadeIn(a), run_time=0.5)
            wait_until(self, tr, "sentence")
            self.play(GrowArrow(ar), FadeIn(b), run_time=0.7)
            rest(self, tr)
        self.play(FadeOut(VGroup(a, b, ar)), run_time=0.4)

        s1 = card(["proof that", "it halts?"], size=34).move_to(UP * (MID + 1.8))
        s2 = card(["proof that", "it never halts?"], size=34).move_to(UP * (MID - 0.6))
        found = VGroup(text("found", size=34, color=GOOD), tick(40)).arrange(RIGHT, buff=0.2).next_to(s2, DOWN, 0.5)
        with self.voiceover(text=N("short3.b5")) as tr:
            self.play(FadeIn(s1), FadeIn(s2), run_time=0.7)
            self.play(Indicate(s1.box, color=PRIMARY), Indicate(s2.box, color=PRIMARY), run_time=0.8)
            wait_until(self, tr, "one")
            self.play(s2.box.animate.set_color(GOOD), FadeIn(found), run_time=0.6)
            rest(self, tr)

        allg = VGroup(s1, s2, found)
        res = VGroup(text("some statements", size=44, color=PRIMARY), text("have no proof", size=44, color=PRIMARY),
                     text("either way", size=44, color=PRIMARY)).arrange(DOWN, buff=0.15).move_to(UP * MID)
        with self.voiceover(text=N("short3.b6")) as tr:
            xa = xout(allg)
            self.play(Create(xa), run_time=0.6)
            wait_until(self, tr, "either")
            self.play(FadeOut(VGroup(allg, xa)), run_time=0.4)
            self.play(FadeIn(res), run_time=0.6)
            rest(self, tr)
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.4)

        m = mbox("a machine", w=3.4, h=1.3, size=36, tex=False, color=SECONDARY).move_to(UP * (MID + 1.5))
        pr = mbox("a proof", w=3.4, h=1.3, size=36, tex=False, color=PRIMARY).move_to(UP * (MID - 1.0))
        same = text("same theorem", size=48, color=PRIMARY, weight="BOLD").move_to(UP * (MID + 0.25))
        with self.voiceover(text=N("short3.b7")) as tr:
            self.play(FadeIn(m), FadeIn(pr), run_time=0.6)
            wait_until(self, tr, "same")
            self.play(m.animate.move_to(UP * (MID + 0.25)).set_opacity(0.4),
                      pr.animate.move_to(UP * (MID + 0.25)).set_opacity(0.4), run_time=0.7)
            self.play(FadeIn(same, scale=1.2), run_time=0.5)
            rest(self, tr)
        self.wait(0.6)
