"""Vertical shorts. Render with MV_ASPECT=portrait."""

import sys
from pathlib import Path

from manim import *
from manim_voiceover import VoiceoverScene

from mathvid import layout  # noqa: F401  must come before scene code runs
from mathvid.anim import rest, rt, wait_until
from mathvid.code import CodePanel, error_text, mono
from mathvid.layout import FW, SAFE_BOTTOM, SAFE_TOP
from mathvid.script import Script
from mathvid.style import BAD, FG, GOOD, MUTED, PRIMARY, SECONDARY, TERTIARY, math, tex, text
from mathvid.voice import get_speech_service

sys.path.insert(0, str(Path(__file__).parent))
from lean_code import CODE, CODE_P, ERR, ERR_P, OUT  # noqa: E402
from scenes import bezier, frac_time, hbox, out_text, panel, ring, tick, xout  # noqa: E402

N = Script(__file__)

MID = (SAFE_TOP + SAFE_BOTTOM) / 2
TOP = SAFE_TOP - 0.5


def ppanel(key, size=22):
    return CodePanel(CODE_P[key], size=size)


def fit(m, w=FW - 1.0):
    if m.width > w:
        m.scale_to_fit_width(w)
    return m


# ---------------------------------------------------------------------------
# short1 P or not P
# ---------------------------------------------------------------------------


class Short1Excluded(VoiceoverScene):
    def construct(self):
        self.set_speech_service(get_speech_service())
        big = math(r"P \lor \neg P", size=110, color=PRIMARY).move_to(UP * (MID + 2.2))
        say = text("P or not P", size=40, color=MUTED).next_to(big, DOWN, 0.3)
        tt = VGroup(*[math(s, size=44) for s in [r"P", r"\neg P", r"P \lor \neg P"]]).arrange(RIGHT, buff=0.9)
        r1 = VGroup(*[math(r"\text{" + v + "}", size=44, color=(GOOD if i == 2 else FG)) for i, v in enumerate("TFT")])
        r2 = VGroup(*[math(r"\text{" + v + "}", size=44, color=(GOOD if i == 2 else FG)) for i, v in enumerate("FTT")])
        for r in (r1, r2):
            for c, h in zip(r, tt):
                c.match_x(h)
        r1.next_to(tt, DOWN, 0.4)
        r2.next_to(r1, DOWN, 0.3)
        for r in (r1, r2):
            for c, h in zip(r, tt):
                c.match_x(h)
        table = VGroup(tt, r1, r2).next_to(say, DOWN, 0.7)
        ref = text("Lean refuses to run it", size=40, color=BAD).next_to(table, DOWN, 0.7)
        with self.voiceover(text=N("short1.b1")) as tr:
            self.add(big, say)
            self.play(FadeIn(table), run_time=0.4)
            wait_until(self, tr, "refuse")
            self.play(FadeIn(ref, scale=1.2), run_time=0.5)
            rest(self, tr)
        self.play(FadeOut(VGroup(table, ref, say)), big.animate.scale(0.5).move_to(UP * TOP), run_time=0.5)

        root = text("a proof of P or Q", size=40).move_to(UP * (MID + 2.6))
        l = VGroup(text("left:", size=34, color=SECONDARY), text("a proof of P", size=34, color=SECONDARY)).arrange(DOWN, buff=0.1)
        r = VGroup(text("right:", size=34, color=TERTIARY), text("a proof of Q", size=34, color=TERTIARY)).arrange(DOWN, buff=0.1)
        l.move_to(root.get_bottom() + DOWN * 2.0 + LEFT * 1.9)
        r.move_to(root.get_bottom() + DOWN * 2.0 + RIGHT * 1.9)
        al = Arrow(root.get_bottom(), l.get_top(), buff=0.15, color=MUTED, stroke_width=4)
        ar = Arrow(root.get_bottom(), r.get_top(), buff=0.15, color=MUTED, stroke_width=4)
        wh = text("which one?", size=44, color=PRIMARY).next_to(VGroup(l, r), DOWN, 0.8)
        with self.voiceover(text=N("short1.b2")) as tr:
            self.play(FadeIn(root), run_time=0.5)
            self.play(GrowArrow(al), GrowArrow(ar), FadeIn(l), FadeIn(r), run_time=0.7)
            wait_until(self, tr, "which")
            self.play(FadeIn(wh, scale=1.2), run_time=0.5)
            rest(self, tr)
        self.play(FadeOut(VGroup(root, l, r, al, ar, wh)), run_time=0.4)

        inp = text("any statement P", size=38).move_to(UP * (MID + 2.8))
        box = RoundedRectangle(corner_radius=0.2, width=4.2, height=1.4, color=SECONDARY, stroke_width=4)
        bl = text("a program", size=38, color=SECONDARY).move_to(box)
        prog = VGroup(box, bl).move_to(UP * MID)
        outp = text("true or false", size=38, color=GOOD).move_to(UP * (MID - 2.8))
        a1 = Arrow(inp.get_bottom(), box.get_top(), buff=0.15, color=MUTED, stroke_width=4)
        a2 = Arrow(box.get_bottom(), outp.get_top(), buff=0.15, color=MUTED, stroke_width=4)
        with self.voiceover(text=N("short1.b3")) as tr:
            self.play(FadeIn(inp), GrowArrow(a1), FadeIn(prog), run_time=0.7)
            wait_until(self, tr, "tells")
            self.play(GrowArrow(a2), FadeIn(outp), run_time=0.6)
            rest(self, tr)

        halts = text("\"this program halts\"", size=38, color=PRIMARY).move_to(inp)
        hp = VGroup(text("the halting problem:", size=34, color=BAD),
                    text("no program solves it", size=34, color=BAD),
                    text("(Turing, 1936)", size=28, color=MUTED)).arrange(DOWN, buff=0.12)
        hp.next_to(outp, DOWN, 0.7)
        with self.voiceover(text=N("short1.b4")) as tr:
            self.play(ReplacementTransform(inp, halts), run_time=0.6)
            self.play(Transform(outp, text("halts or not", size=38, color=GOOD).move_to(outp)), run_time=0.5)
            wait_until(self, tr, "turing")
            self.play(Create(xout(prog, pad=0.25)), FadeIn(hp), run_time=0.7)
            rest(self, tr)
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.4)

        da = ppanel("decide_any", size=24).move_to(UP * (MID + 1.6))
        er = error_text(ERR_P["decide_any"], 26).next_to(da, DOWN, 0.5)
        ax = text("Lean gets P or not P from an axiom", size=32, color=MUTED).next_to(da, UP, 0.5)
        with self.voiceover(text=N("short1.b5")) as tr:
            self.play(FadeIn(ax), run_time=0.5)
            self.play(FadeIn(da, shift=UP * 0.2), run_time=0.6)
            self.wait(frac_time(tr, 0.15))
            self.play(FadeIn(er), run_time=0.6)
            wait_until(self, tr, "noncomputable")
            g = er[2][1:14]
            und = Line(g.get_corner(DL) + DOWN * 0.07, g.get_corner(DR) + DOWN * 0.07, color=PRIMARY, stroke_width=5)
            self.play(Create(und), g.animate.set_color(PRIMARY), run_time=0.5)
            rest(self, tr)
        big.scale(2.0).move_to(UP * (MID + 2.0))
        self.play(FadeOut(VGroup(da, er, und, ax)), FadeIn(big), run_time=0.5)

        t1 = VGroup(text("not false", size=44, color=GOOD), tick(56)).arrange(RIGHT, buff=0.3)
        t2 = text("can't run", size=44, color=PRIMARY)
        VGroup(t1, t2).arrange(DOWN, buff=0.6).next_to(big, DOWN, 1.0)
        with self.voiceover(text=N("short1.b6")) as tr:
            self.play(FadeIn(t1, shift=UP * 0.2), run_time=0.6)
            wait_until(self, tr, "run")
            self.play(FadeIn(t2, scale=1.2), run_time=0.5)
            rest(self, tr)
        self.wait(0.5)


# ---------------------------------------------------------------------------
# short2 Induction is recursion
# ---------------------------------------------------------------------------


class Short2Induction(VoiceoverScene):
    def construct(self):
        self.set_speech_service(get_speech_service())
        thm = VGroup(text("Theorem: every natural number", size=34, color=PRIMARY),
                     text("has a binary representation", size=34, color=PRIMARY)).arrange(DOWN, buff=0.1)
        tb = ppanel("toBinary", size=21)
        VGroup(thm, tb).arrange(DOWN, buff=0.5).move_to(UP * MID)
        with self.voiceover(text=N("short2.b1")) as tr:
            self.add(thm, tb)
            wait_until(self, tr, "run")
            self.play(Indicate(tb.bg, color=GOOD, scale_factor=1.03), run_time=0.7)
            rest(self, tr)

        book = VGroup(*[tex(l, size=34) for l in [r"If $n = 0$: the empty string.",
                                                   r"Otherwise $n = 2q + r$, $r = 0$ or $1$.",
                                                   r"$q < n$, so $q$ has one (induction).",
                                                   r"Add $r$ as the ones digit."]]).arrange(DOWN, buff=0.22, aligned_edge=LEFT)
        fit(book)
        book.move_to(UP * TOP).align_to(UP * TOP, UP)
        with self.voiceover(text=N("short2.b2")) as tr:
            self.play(FadeOut(thm), tb.animate.next_to(book, DOWN, 0.5), run_time=0.6)
            self.play(FadeIn(book[0]), run_time=0.4)
            self.wait(frac_time(tr, 0.15))
            self.play(FadeIn(book[1]), run_time=0.4)
            wait_until(self, tr, "smaller")
            self.play(FadeIn(book[2]), run_time=0.4)
            self.wait(frac_time(tr, 0.08))
            self.play(FadeIn(book[3]), run_time=0.4)
            rest(self, tr)

        call = tb.part(7, "toBinary (n / 2)")
        hyp = text("induction hypothesis", size=30, color=PRIMARY).next_to(tb, DOWN, 0.35)
        with self.voiceover(text=N("short2.b3")) as tr:
            pairs = [(0, 3), (1, 5), (3, 8)]
            for bi, li in pairs[:2]:
                self.play(Indicate(book[bi], color=SECONDARY, scale_factor=1.03),
                          Indicate(tb.line(li), color=SECONDARY, scale_factor=1.03), run_time=0.6)
            wait_until(self, tr, "call")
            self.play(Create(hbox(call)), Create(hbox(book[2])), FadeIn(hyp), run_time=0.7)
            rest(self, tr)
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.4)

        ev = CodePanel(CODE["eval13"], size=28).move_to(UP * TOP)
        rows = VGroup(*[math(a, r, size=56) for a, r in [(r"13 = 2 \cdot 6 + ", "1"), (r"6 = 2 \cdot 3 + ", "0"),
                                                        (r"3 = 2 \cdot 1 + ", "1"), (r"1 = 2 \cdot 0 + ", "1")]])
        rows.arrange(DOWN, buff=0.45, aligned_edge=RIGHT).next_to(ev, DOWN, 0.8)
        for r in rows:
            r[1].set_color(PRIMARY)
        outl = out_text("eval13", 60).next_to(rows, DOWN, 0.8)
        lab = text("13 in binary, ones digit first", size=30, color=MUTED).next_to(outl, DOWN, 0.3)
        with self.voiceover(text=N("short2.b4")) as tr:
            self.play(FadeIn(ev), run_time=0.4)
            t_each = rt((tr.time_until_bookmark("out") - 0.6) / 4)
            for r in rows:
                self.play(FadeIn(r, shift=UP * 0.1), run_time=min(0.5, t_each))
                if t_each > 0.6:
                    self.wait(t_each - 0.5)
            wait_until(self, tr, "out")
            digs = VGroup(*[r[1].copy() for r in rows])
            self.play(LaggedStart(*[d.animate.move_to(outl[1 + 3 * i]) for i, d in enumerate(digs)], lag_ratio=0.2),
                      run_time=0.8)
            self.play(FadeOut(digs), FadeIn(outl), FadeIn(lab), run_time=0.4)
            rest(self, tr)
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.4)

        head = VGroup(text("induction", size=72, weight="BOLD", color=PRIMARY), math("=", size=90),
                      text("recursion", size=72, weight="BOLD", color=SECONDARY)).arrange(DOWN, buff=0.3)
        head.move_to(UP * (MID + 1.4))
        p1 = text("base case = base case", size=34)
        p2 = text("hypothesis = recursive call", size=34)
        VGroup(p1, p2).arrange(DOWN, buff=0.35).next_to(head, DOWN, 0.9)
        with self.voiceover(text=N("short2.b5")) as tr:
            self.play(FadeIn(head, scale=1.1), run_time=0.6)
            self.wait(frac_time(tr, 0.15))
            self.play(FadeIn(p1), run_time=0.4)
            self.wait(frac_time(tr, 0.1))
            self.play(FadeIn(p2), run_time=0.4)
            rest(self, tr)
        self.wait(0.5)


# ---------------------------------------------------------------------------
# short3 Two proofs of the same equation
# ---------------------------------------------------------------------------


class Short3Equality(VoiceoverScene):
    def construct(self):
        self.set_speech_service(get_speech_service())
        A, B = LEFT * 2.6 + UP * MID, RIGHT * 2.6 + UP * MID
        p = bezier(A, B, UP * 2.2).set_stroke(PRIMARY, 6)
        q = bezier(A, B, DOWN * 2.2).set_stroke(SECONDARY, 6)
        ends = VGroup(Dot(A, radius=0.11), Dot(B, radius=0.11), math("a", size=52).next_to(A, LEFT, 0.2),
                      math("b", size=52).next_to(B, RIGHT, 0.2))
        lp = math("p", size=52, color=PRIMARY).move_to(p.point_from_proportion(0.5) + UP * 0.45)
        lq = math("q", size=52, color=SECONDARY).move_to(q.point_from_proportion(0.5) + DOWN * 0.45)
        ques = math(r"p = q\ ?", size=80).move_to(UP * TOP)
        with self.voiceover(text=N("short3.b1")) as tr:
            self.add(ends, p, q, lp, lq, ques)
            wait_until(self, tr, "different")
            self.play(Indicate(ques, color=PRIMARY), run_time=0.6)
            rest(self, tr)
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.4)

        eq = CodePanel(CODE["eq"], size=22).move_to(UP * TOP + DOWN * 0.3)
        s1 = text("one way to build a proof:", size=32, color=MUTED)
        s1b = text("everything equals itself", size=36, color=GOOD)
        s2 = text("one rule for using a proof:", size=32, color=MUTED)
        s2b = VGroup(text("for every b and every proof of a = b,", size=30),
                     text("check b = a and refl", size=30, color=PRIMARY)).arrange(DOWN, buff=0.1)
        col = VGroup(s1, s1b, s2, s2b).arrange(DOWN, buff=0.3).next_to(eq, DOWN, 0.7)
        s2.shift(DOWN * 0.3)
        s2b.shift(DOWN * 0.3)
        with self.voiceover(text=N("short3.b2")) as tr:
            self.play(FadeIn(eq), run_time=0.5)
            wait_until(self, tr, "refl")
            self.play(FadeIn(s1), FadeIn(s1b), Create(hbox(eq.line(1), GOOD)), run_time=0.6)
            self.wait(frac_time(tr, 0.15))
            self.play(FadeIn(s2), FadeIn(s2b), run_time=0.6)
            rest(self, tr)
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.4)

        a0 = UP * (MID - 0.6)
        loop = CubicBezier(a0, a0 + UP * 2.4 + LEFT * 1.4, a0 + UP * 2.4 + RIGHT * 1.4, a0).set_stroke(PRIMARY, 6)
        da = VGroup(Dot(a0, radius=0.11), math("a", size=52).next_to(a0, DOWN, 0.2))
        lq_ = math(r"\text{loop} = \text{refl}\ ?", size=64).move_to(UP * TOP)
        hs = VGroup(text("Hofmann and Streicher, 1994:", size=32, color=PRIMARY),
                    text("the rule can't prove it", size=36, color=BAD)).arrange(DOWN, buff=0.15)
        hs.next_to(da, DOWN, 0.8)
        with self.voiceover(text=N("short3.b3")) as tr:
            self.play(FadeIn(da), Create(loop), FadeIn(lq_), run_time=0.8)
            wait_until(self, tr, "cant")
            self.play(FadeIn(hs, shift=UP * 0.2), run_time=0.5)
            rest(self, tr)
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.4)

        rg = ring(0.8, 2.6).move_to(UP * (MID + 0.6))
        C = rg.get_center()
        R = 1.7
        pa = C + R * DOWN
        dot = VGroup(Dot(pa, radius=0.1), math("a", size=48).next_to(pa, DOWN, 0.2))
        big = Circle(radius=R).move_to(C).rotate(-PI / 2).set_stroke(TERTIARY, 6)
        cap1 = text("type = space,  proof = path", size=34, color=SECONDARY).move_to(UP * TOP)
        cap2 = text("a loop around the hole can't shrink to refl", size=30, color=TERTIARY)
        fit(cap2).next_to(rg, DOWN, 0.9)
        with self.voiceover(text=N("short3.b4")) as tr:
            self.play(FadeIn(rg), FadeIn(cap1), FadeIn(dot), run_time=0.6)
            wait_until(self, tr, "hole")
            self.play(Create(big), run_time=0.8)
            self.play(big.animate.scale(0.8, about_point=pa), run_time=0.5)
            self.play(Wiggle(big, scale_value=1.03), FadeIn(cap2), run_time=0.7)
            rest(self, tr)
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.4)

        hdr = math(r"\mathrm{Bool} = \mathrm{Bool}", size=72).move_to(UP * TOP)

        def matching(y, swap):
            L = VGroup(*[VGroup(Dot(), text(s, size=32)) for s in ("true", "false")])
            Rr = VGroup(*[VGroup(Dot(), text(s, size=32)) for s in ("true", "false")])
            for g in L:
                g[1].next_to(g[0], LEFT, 0.15)
            for g in Rr:
                g[1].next_to(g[0], RIGHT, 0.15)
            L.arrange(DOWN, buff=0.7).move_to([-1.2, y, 0])
            Rr.arrange(DOWN, buff=0.7).move_to([1.2, y, 0])
            for g, x in ((L, -1.2), (Rr, 1.2)):
                for d in g:
                    d.shift(RIGHT * (x - d[0].get_center()[0]))
            col = TERTIARY if swap else GOOD
            t0, f0 = L[0][0].get_center(), L[1][0].get_center()
            t1, f1 = Rr[0][0].get_center(), Rr[1][0].get_center()
            ars = VGroup(Arrow(t0, f1 if swap else t1, buff=0.12, color=col, stroke_width=5),
                         Arrow(f0, t1 if swap else f1, buff=0.12, color=col, stroke_width=5))
            return VGroup(L, Rr, ars)
        m1 = matching(MID + 1.6, False)
        m2 = matching(MID - 1.9, True)
        l1 = text("do nothing", size=36, color=GOOD).next_to(m1, DOWN, 0.3)
        l2 = text("swap", size=36, color=TERTIARY).next_to(m2, DOWN, 0.3)
        uv = text("univalence", size=30, color=MUTED).next_to(hdr, DOWN, 0.3)
        with self.voiceover(text=N("short3.b5")) as tr:
            self.play(FadeIn(hdr), FadeIn(uv), run_time=0.5)
            self.play(FadeIn(m1), FadeIn(l1), run_time=0.6)
            wait_until(self, tr, "swap")
            self.play(FadeIn(m2), FadeIn(l2), run_time=0.6)
            rest(self, tr)
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.4)

        X, Y = LEFT * 2.6 + UP * (MID - 0.6), RIGHT * 2.6 + UP * (MID - 0.6)
        fam = VGroup(*[bezier(X, Y, UP * k).set_stroke(interpolate_color(ManimColor(PRIMARY), ManimColor(SECONDARY), (2.0 - k) / 4.0), 4)
                       for k in np.linspace(2.0, -2.0, 9)])
        ends2 = VGroup(Dot(X), Dot(Y), math("a", size=48).next_to(X, LEFT, 0.2), math("b", size=48).next_to(Y, RIGHT, 0.2))
        fin = VGroup(text("Equality has", size=56, weight="BOLD"),
                     text("a shape", size=56, weight="BOLD", color=PRIMARY)).arrange(DOWN, buff=0.15).move_to(UP * TOP + DOWN * 0.4)
        with self.voiceover(text=N("short3.b6")) as tr:
            self.play(FadeIn(ends2), LaggedStart(*[Create(c) for c in fam], lag_ratio=0.1), run_time=1.0)
            wait_until(self, tr, "shape")
            self.play(FadeIn(fin, shift=DOWN * 0.2), run_time=0.5)
            rest(self, tr)
        self.wait(0.5)
