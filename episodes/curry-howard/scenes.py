import sys
from pathlib import Path

import numpy as np
from manim import *
from manim_voiceover import VoiceoverScene

from mathvid import layout  # noqa: F401  must come before scene code runs
from mathvid.anim import rest, rt, wait_until
from mathvid.code import CodePanel, char_width, error_text, mono
from mathvid.layout import FH, FW
from mathvid.script import Script
from mathvid.style import BAD, BG, FG, GOOD, MUTED, PRIMARY, SECONDARY, TERTIARY, math, text
from mathvid.voice import get_speech_service

sys.path.insert(0, str(Path(__file__).parent))
from lean_code import CODE, ERR, OUT  # noqa: E402

N = Script(__file__)

TITLE = "Proofs are programs"
SUBTITLE = "the Curry-Howard correspondence"
LOF = "Martin-L\u00f6f"
ARR = "\u2192"


def frac_time(tr, f):
    return rt(tr.duration * f)


def until(tr, mark, minus=0.0):
    return rt(tr.time_until_bookmark(mark) - minus)


# ---------------------------------------------------------------------------
# Shared builders (also used by shorts.py)
# ---------------------------------------------------------------------------


def panel(key, size=26, **kw):
    return CodePanel(CODE[key], size=size, **kw)


def out_text(key, size=26):
    return mono(OUT[key], size, PRIMARY)


def err_text(key, size=22):
    return error_text(ERR[key], size)


def tag(s, size=28, color=MUTED, **kw):
    return text(s, size=size, color=color, **kw)


def tick(size=44):
    return math(r"\checkmark", size=size, color=GOOD)


def xout(mob, color=BAD, pad=0.12, width=7):
    ul, dr = mob.get_corner(UL) + np.array([-pad, pad, 0]), mob.get_corner(DR) + np.array([pad, -pad, 0])
    ur, dl = mob.get_corner(UR) + np.array([pad, pad, 0]), mob.get_corner(DL) + np.array([-pad, -pad, 0])
    return VGroup(Line(ul, dr, color=color, stroke_width=width), Line(ur, dl, color=color, stroke_width=width))


def hbox(mob, color=PRIMARY, buff=0.07):
    return SurroundingRectangle(mob, color=color, buff=buff, stroke_width=3, corner_radius=0.05)


def chars(p, i, a, b):
    """Glyphs a..b (exclusive) of line i of a CodePanel, by character index."""
    return p.lines[i].text[1 + a:1 + b]


def note(s, target, direction=DOWN, size=24, color=PRIMARY, buff=0.35):
    """A small label with a thin pointer to a glyph group."""
    t = text(s, size=size, color=color).next_to(target, direction, buff=buff)
    ln = Line(t.get_edge_center(-direction), target.get_edge_center(direction), color=color, stroke_width=2,
              buff=0.06)
    return VGroup(t, ln)


ROWS = [
    ("P implies Q", "function from P to Q"),
    ("P and Q", "pair"),
    ("P or Q", "tagged choice"),
    ("true", "a type with one value"),
    ("false", "a type with no values"),
    ("not P", "function from P to false"),
    ("for all x, P(x)", "dependent function"),
    ("there exists x, P(x)", "dependent pair"),
    ("induction", "recursion"),
    ("a = b", "a type with one constructor, refl"),
]


class DictTable(VGroup):
    """The logic | programs dictionary. All rows are laid out; scenes add the visible ones."""

    def __init__(self, size=28, row_h=None, gap=0.7, n=len(ROWS)):
        super().__init__()
        row_h = row_h or size / 48
        hl = text("logic", size=size, color=PRIMARY, weight="BOLD")
        hr = text("programs", size=size, color=SECONDARY, weight="BOLD")
        lefts = [text(l, size=size) for l, _ in ROWS[:n]]
        rights = [text(r, size=size) for _, r in ROWS[:n]]
        lw = max(m.width for m in lefts + [hl])
        rw = max(m.width for m in rights + [hr])
        x1 = lw + gap
        hl.move_to(ORIGIN, aligned_edge=LEFT)
        hr.move_to([x1, 0, 0], aligned_edge=LEFT)
        rule = Line([0, -0.35, 0], [x1 + rw, -0.35, 0], color=MUTED, stroke_width=2)
        self.header = VGroup(hl, hr, rule)
        self.rows = VGroup()
        for i, (l, r) in enumerate(zip(lefts, rights)):
            y = -0.35 - row_h * (i + 0.75)
            l.move_to([0, y, 0], aligned_edge=LEFT)
            r.move_to([x1, y, 0], aligned_edge=LEFT)
            self.rows.add(VGroup(l, r))
        self.add(self.header, self.rows)

    def upto(self, k):
        return VGroup(self.header, *self.rows[:k])

    def show_row(self, i, run_time=0.8):
        return FadeIn(self.rows[i], shift=RIGHT * 0.2, run_time=run_time)


RUNGS = [
    ("simple types", "functions, pairs, choices"),
    ("dependent types", "types that mention values"),
    ("inductive types", "each comes with a recursor"),
    ("identity types", "a = b as a type"),
    ("paths", "homotopy type theory"),
]


class Ladder(VGroup):
    """The type system, one rung per step, built bottom-up."""

    def __init__(self, w=3.6, h=0.95, buff=0.18):
        super().__init__()
        self.boxes = VGroup()
        self.labels = VGroup()
        for i, (a, b) in enumerate(RUNGS):
            box = RoundedRectangle(corner_radius=0.12, width=w, height=h, stroke_color=MUTED, stroke_width=2,
                                   stroke_opacity=0.5, fill_color=PRIMARY, fill_opacity=0)
            box.move_to(UP * i * (h + buff))
            la = text(a, size=26, color=FG)
            lb = text(b, size=19, color=MUTED)
            lab = VGroup(la, lb).arrange(DOWN, buff=0.08).move_to(box)
            self.boxes.add(box)
            self.labels.add(lab)
        self.title = text("the type system", size=26, color=SECONDARY).next_to(self.boxes, UP, 0.3)
        self.add(self.title, self.boxes, self.labels)

    def lit_state(self, k):
        for i, box in enumerate(self.boxes):
            if i < k:
                box.set_stroke(PRIMARY, 3, opacity=1).set_fill(PRIMARY, 0.12)
        return VGroup(self.title, self.boxes, *self.labels[:k])

    def light(self, i, run_time=0.8):
        return AnimationGroup(
            self.boxes[i].animate.set_stroke(PRIMARY, 3, opacity=1).set_fill(PRIMARY, 0.12),
            FadeIn(self.labels[i], shift=UP * 0.1), run_time=run_time)


def table_left(k, n=6, size=27):
    """The table parked on the left with its first k rows (laid out for n rows)."""
    t = DictTable(size=size, n=n)
    t.to_corner(UL, buff=0.5)
    return t, t.upto(k)


def ladder_right(k, scale=1.0):
    lad = Ladder().scale(scale)
    vis = lad.lit_state(k)
    lad.move_to(RIGHT * 4.6 + DOWN * 0.3)
    return lad, vis


# ---------------------------------------------------------------------------
# s01 Hook
# ---------------------------------------------------------------------------


class S01Hook(VoiceoverScene):
    def construct(self):
        self.set_speech_service(get_speech_service())
        tb = panel("toBinary", size=28).move_to(UP * 0.55)
        ev = panel("eval13", size=28).next_to(tb, DOWN, 0.4).align_to(tb, LEFT)
        out = out_text("eval13", 34).next_to(ev, RIGHT, 0.5)
        cap = math(r"13 = 1 + 0\cdot 2 + 1\cdot 4 + 1\cdot 8", size=40, color=MUTED)
        cap.next_to(out, RIGHT, 0.6)
        with self.voiceover(text=N("s01.b1")) as tr:
            self.play(FadeIn(tb.bg), run_time=0.4)
            self.play(LaggedStart(*[FadeIn(l, shift=RIGHT * 0.15) for l in tb.lines], lag_ratio=0.25),
                      run_time=min(3.0, until(tr, "run", 0.6)))
            wait_until(self, tr, "run")
            self.play(FadeIn(ev, shift=UP * 0.15), run_time=0.6)
            wait_until(self, tr, "thirteen")
            self.play(FadeIn(out, scale=1.3), run_time=0.6)
            self.play(Write(cap), run_time=1.0)
            rest(self, tr)

        tbox = tb.box_part(1, "{ ds : List (Fin 2) // value ds = n }")
        thm = text("Theorem: every natural number has a binary representation.", size=32, color=PRIMARY)
        thm.next_to(tb, UP, 0.25)
        br = Brace(VGroup(*tb.lines[2:]), RIGHT, color=GOOD)
        br.next_to(tb.bg, RIGHT, 0.12).match_y(VGroup(*tb.lines[2:]))
        prf = text("proof", size=32, color=GOOD).next_to(br, RIGHT, 0.15)
        with self.voiceover(text=N("s01.b2")) as tr:
            wait_until(self, tr, "theorem")
            self.play(Create(tbox), FadeIn(thm, shift=DOWN * 0.15), run_time=0.9)
            wait_until(self, tr, "proof")
            self.play(GrowFromCenter(br), FadeIn(prf, shift=LEFT * 0.15), run_time=0.8)
            rest(self, tr)
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.5)

        c1 = text("a proof is a program;", size=34)
        c2 = text("a statement is a type", size=34)
        cd = VGroup(c1, c2).arrange(DOWN, buff=0.2)
        cbox = SurroundingRectangle(cd, buff=0.35, corner_radius=0.15, color=MUTED, stroke_width=3)
        cardg = VGroup(cbox, cd).scale(0.8).move_to(UP * 2.2)
        lastt = tag("last time:", size=22).next_to(cardg, UP, 0.12).align_to(cardg, LEFT)
        title = text(TITLE, size=64, weight="BOLD")
        sub = text(SUBTITLE, size=32, color=MUTED).next_to(title, DOWN, 0.3)
        tg = VGroup(title, sub).move_to(UP * 0.2)
        with self.voiceover(text=N("s01.b3")) as tr:
            self.play(FadeIn(cardg, shift=DOWN * 0.3), FadeIn(lastt), run_time=0.8)
            wait_until(self, tr, "literally")
            self.play(FadeOut(lastt), cardg.animate.scale(1.6).move_to(ORIGIN), run_time=1.0)
            wait_until(self, tr, "correspondence")
            self.play(FadeOut(cardg, shift=UP * 0.3), FadeIn(tg, shift=UP * 0.2), run_time=0.8)
            rest(self, tr)
        self.wait(0.6)
        self.play(FadeOut(tg), run_time=0.5)


# ---------------------------------------------------------------------------
# s02 Implication is a function
# ---------------------------------------------------------------------------


class S02Implication(VoiceoverScene):
    def construct(self):
        self.set_speech_service(get_speech_service())
        lp = panel("len", size=30).move_to(UP * 2.5 + LEFT * 1.3)
        lout = VGroup(tag("output:", size=26), out_text("len", 30)).arrange(RIGHT, buff=0.2)
        lout.next_to(lp, RIGHT, 0.4).match_y(lp.lines[1])
        larr = lp.part(0, ARR)
        with self.voiceover(text=N("s02.b1")) as tr:
            self.play(FadeIn(lp, shift=DOWN * 0.2), run_time=0.8)
            self.play(FadeIn(lout), run_time=0.5)
            wait_until(self, tr, "arrow")
            ba = hbox(larr)
            self.play(Create(ba), larr.animate.set_color(PRIMARY), run_time=0.6)
            rest(self, tr)

        mp = panel("mp", size=34).next_to(lp, DOWN, 0.6).align_to(lp, LEFT)
        stmt = mp.box_part(1, "(P \u2192 Q) \u2192 P \u2192 Q", color=SECONDARY)
        sl = tag("statement", size=30, color=SECONDARY).next_to(mp.bg, RIGHT, 0.3).match_y(stmt)
        prf = mp.box_part(2, "fun f p => f p", color=GOOD)
        pl = tag("proof", size=30, color=GOOD).next_to(mp.bg, RIGHT, 0.3).match_y(prf)
        with self.voiceover(text=N("s02.b2")) as tr:
            self.play(FadeOut(ba), FadeIn(mp, shift=UP * 0.2), run_time=0.8)
            self.play(Indicate(mp.part(0, "P Q : Prop"), color=PRIMARY), run_time=1.0)
            wait_until(self, tr, "statement")
            self.play(Create(stmt), FadeIn(sl), run_time=0.7)
            wait_until(self, tr, "proof")
            self.play(Create(prf), FadeIn(pl), run_time=0.7)
            rest(self, tr)

        marr = mp.part(1, ARR, 0)
        b1, b2 = hbox(larr), hbox(marr)
        same = tag("the same arrow", size=30, color=PRIMARY).next_to(mp.bg, RIGHT, 0.3).match_y(mp.lines[1])
        fn = text("a proof of P \u2192 Q is a function", size=36, color=PRIMARY).next_to(mp, DOWN, 0.6)
        with self.voiceover(text=N("s02.b3")) as tr:
            self.play(FadeOut(VGroup(stmt, sl, prf, pl)), run_time=0.4)
            self.play(Create(b1), Create(b2), marr.animate.set_color(PRIMARY), run_time=0.7)
            self.play(FadeIn(same), run_time=0.6)
            wait_until(self, tr, "function")
            self.play(FadeIn(fn, shift=UP * 0.15), run_time=0.7)
            rest(self, tr)

        # in "  fun f p => f p": f at 6, p at 8, "f p" at 13..16
        f_g, p_g, fp_g = chars(mp, 2, 6, 7), chars(mp, 2, 8, 9), chars(mp, 2, 13, 16)
        lf = text("proof of P \u2192 Q", size=30, color=SECONDARY)
        lpp = text("proof of P", size=30, color=SECONDARY)
        lq = text("proof of Q", size=30, color=GOOD)
        row = VGroup(lf, lpp, lq).arrange(RIGHT, buff=0.9).next_to(mp, DOWN, 0.9)
        def ptr(lab, g, col):
            return Line(lab.get_top() + UP * 0.06, g.get_bottom() + DOWN * 0.08, color=col, stroke_width=2)
        lab_f, lab_p, lab_fp = (VGroup(lf, ptr(lf, f_g, SECONDARY)), VGroup(lpp, ptr(lpp, p_g, SECONDARY)),
                                VGroup(lq, ptr(lq, fp_g, GOOD)))
        mpn = text("modus ponens = calling a function", size=36, color=PRIMARY).to_edge(DOWN, buff=0.5)
        with self.voiceover(text=N("s02.b4")) as tr:
            self.play(FadeOut(VGroup(fn, same, b1, b2)), run_time=0.4)
            self.play(FadeIn(lab_f), f_g.animate.set_color(SECONDARY), run_time=0.6)
            self.play(FadeIn(lab_p), p_g.animate.set_color(SECONDARY), run_time=0.6)
            wait_until(self, tr, "apply")
            pc = p_g.copy()
            self.play(pc.animate.move_to(fp_g[2]), run_time=0.8)
            self.play(FadeOut(pc), FadeIn(lab_fp), fp_g.animate.set_color(GOOD), run_time=0.6)
            self.wait(frac_time(tr, 0.1))
            self.play(FadeIn(mpn, shift=UP * 0.15), run_time=0.7)
            rest(self, tr)

        ch = panel("chain", size=32)
        co = panel("compose", size=32)
        VGroup(ch, co).arrange(DOWN, buff=0.5).move_to(DOWN * 0.8)
        with self.voiceover(text=N("s02.b5")) as tr:
            self.play(FadeOut(VGroup(lp, lout, lab_f, lab_p, lab_fp, mpn)),
                      mp.animate.scale(0.6).to_corner(UL, buff=0.4), run_time=0.8)
            self.play(FadeIn(ch, shift=UP * 0.2), run_time=0.8)
            gp = chars(ch, 2, 14, 21)
            self.play(Indicate(gp, color=PRIMARY), run_time=1.0)
            wait_until(self, tr, "same")
            self.play(FadeIn(co, shift=UP * 0.2), run_time=0.7)
            self.play(Create(hbox(ch.line(2))), Create(hbox(co.line(2))), run_time=0.8)
            rest(self, tr)
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.5)

        t = DictTable(size=36)
        t.shift(UP * (1.4 - t.header.get_center()[1]) + RIGHT * (0 - t.upto(1).get_center()[0]))
        cap = text("proposition = type,  proof = value of that type", size=38).move_to(UP * 2.8)
        with self.voiceover(text=N("s02.b6")) as tr:
            self.play(FadeIn(cap, shift=DOWN * 0.2), run_time=0.8)
            self.play(FadeIn(t.header), run_time=0.6)
            wait_until(self, tr, "row")
            self.play(t.show_row(0), run_time=0.8)
            rest(self, tr)
        self.play(FadeOut(cap), FadeOut(t.header), FadeOut(t.rows[0]), run_time=0.5)


# ---------------------------------------------------------------------------
# s03 And, or, true, false
# ---------------------------------------------------------------------------

RX = 3.05  # center x of the code area while the table sits on the left


class S03Connectives(VoiceoverScene):
    def construct(self):
        self.set_speech_service(get_speech_service())
        t, vis = table_left(1)
        sw = panel("and_swap", size=27).move_to([RX, 0.6, 0])
        a_pq = sw.part(2, "\u27e8p, q\u27e9")
        a_qp = sw.part(2, "\u27e8q, p\u27e9")
        with self.voiceover(text=N("s03.b1")) as tr:
            self.play(FadeIn(vis), run_time=0.6)
            self.play(FadeIn(sw, shift=UP * 0.2), run_time=0.8)
            wait_until(self, tr, "pair")
            bx = VGroup(hbox(a_pq), hbox(a_qp))
            self.play(Create(bx), run_time=0.6)
            wait_until(self, tr, "swap")
            p_c, q_c = a_pq[1].copy(), a_pq[4].copy()
            self.play(p_c.animate.move_to(a_qp[4]).set_color(PRIMARY), q_c.animate.move_to(a_qp[1]).set_color(PRIMARY),
                      path_arc=PI / 2, run_time=1.0)
            self.remove(p_c, q_c)
            wait_until(self, tr, "and")
            self.play(t.show_row(1), run_time=0.7)
            rest(self, tr)

        orp = panel("or_swap", size=27).move_to([RX, 0.9, 0])
        inl, inr = orp.part(3, ".inl"), orp.part(3, ".inr")
        ll = text("left: a proof of P", size=26, color=SECONDARY)
        rl = text("right: a proof of Q", size=26, color=TERTIARY)
        VGroup(ll, rl).arrange(DOWN, buff=0.2, aligned_edge=LEFT).next_to(orp, DOWN, 0.45)
        with self.voiceover(text=N("s03.b2")) as tr:
            self.play(FadeOut(VGroup(sw, bx)), FadeIn(orp, shift=UP * 0.2), run_time=0.8)
            wait_until(self, tr, "which")
            self.play(inl.animate.set_color(SECONDARY), inr.animate.set_color(TERTIARY), FadeIn(ll), run_time=0.6)
            self.play(FadeIn(rl), run_time=0.5)
            wait_until(self, tr, "case")
            c1 = hbox(orp.line(3), color=PRIMARY)
            c2 = hbox(orp.line(4), color=PRIMARY)
            self.play(Create(c1), run_time=0.5)
            self.play(ReplacementTransform(c1, c2), run_time=0.6)
            rest(self, tr)

        under = Line(t.rows[2][1][:6].get_corner(DL) + DOWN * 0.06, t.rows[2][1][:6].get_corner(DR) + DOWN * 0.06,
                     color=PRIMARY, stroke_width=4)
        with self.voiceover(text=N("s03.b3")) as tr:
            wait_until(self, tr, "or")
            self.play(t.show_row(2), run_time=0.7)
            self.play(Create(under), run_time=0.6)
            rest(self, tr)

        tp = panel("true", size=27)
        fp = panel("false", size=27)
        VGroup(tp, fp).arrange(DOWN, buff=0.6, aligned_edge=LEFT).move_to([RX, 0.9, 0])
        dash = DashedVMobject(RoundedRectangle(corner_radius=0.1, width=2.6, height=0.6, color=MUTED), num_dashes=24)
        dash.next_to(fp, DOWN, 0.25).align_to(fp, LEFT).shift(RIGHT * 0.4)
        nolab = tag("(no constructors)", size=22).next_to(dash, RIGHT, 0.25)
        with self.voiceover(text=N("s03.b4")) as tr:
            self.play(FadeOut(VGroup(orp, ll, rl, c2)), run_time=0.5)
            self.play(FadeIn(tp, shift=UP * 0.2), run_time=0.6)
            wait_until(self, tr, "one")
            ob = hbox(tp.line(1), color=GOOD)
            self.play(Create(ob), run_time=0.6)
            self.play(FadeIn(fp, shift=UP * 0.2), run_time=0.6)
            wait_until(self, tr, "none")
            self.play(Create(dash), FadeIn(nolab), run_time=0.8)
            rest(self, tr)

        ex = panel("explode", size=27)
        ex.move_to([RX, 0.2, 0])
        cl_t = text("cases to handle:", size=28)
        cl_b = math(r"\{\ \}", size=44, color=MUTED)
        cl = VGroup(cl_t, cl_b).arrange(RIGHT, buff=0.3).next_to(ex, DOWN, 0.5)
        tk = tick(48).next_to(cl, RIGHT, 0.3)
        exf = tag("ex falso quodlibet", size=24).next_to(cl, DOWN, 0.35)
        with self.voiceover(text=N("s03.b5")) as tr:
            self.play(FadeOut(VGroup(tp, ob, dash, nolab)), fp.animate.move_to([RX, 2.5, 0]), run_time=0.7)
            self.play(FadeIn(ex, shift=UP * 0.2), run_time=0.7)
            self.play(Indicate(ex.part(2, "nomatch h"), color=PRIMARY), run_time=1.0)
            wait_until(self, tr, "cases")
            self.play(FadeIn(cl), run_time=0.6)
            self.play(FadeIn(tk, scale=1.4), FadeIn(exf), run_time=0.6)
            rest(self, tr)

        npn = panel("not", size=27).move_to([RX, 2.4, 0])
        fin = text("proof of P", size=28, color=SECONDARY)
        fbox = RoundedRectangle(corner_radius=0.12, width=1.9, height=0.8, color=MUTED, stroke_width=3)
        fbl = math(r"\neg P", size=40).move_to(fbox)
        fout = text("proof of False", size=28, color=BAD)
        flow = VGroup(fin, VGroup(fbox, fbl), fout).arrange(RIGHT, buff=0.8).move_to([RX, 0.75, 0])
        a1 = Arrow(fin.get_right(), fbox.get_left(), buff=0.1, color=MUTED, stroke_width=3)
        a2 = Arrow(fbox.get_right(), fout.get_left(), buff=0.1, color=MUTED, stroke_width=3)
        cp = panel("contra", size=27).move_to([RX, -1.7, 0])
        with self.voiceover(text=N("s03.b6")) as tr:
            self.play(FadeOut(VGroup(fp, ex, cl, tk, exf)), run_time=0.5)
            self.play(FadeIn(npn, shift=UP * 0.2), run_time=0.7)
            wait_until(self, tr, "never")
            self.play(FadeIn(fin), GrowArrow(a1), FadeIn(VGroup(fbox, fbl)), run_time=0.7)
            self.play(GrowArrow(a2), FadeIn(fout), run_time=0.6)
            self.play(Create(strike_through(fout)), run_time=0.4)
            self.play(Create(strike_through(fin)), run_time=0.4)
            self.play(FadeIn(cp, shift=UP * 0.2), run_time=0.7)
            # "  fun f nq p => nq (f p)": p at 11, "f p" at 19..22, "nq (f p)" at 15..23
            wait_until(self, tr, "through")
            b_fp = hbox(chars(cp, 2, 19, 22))
            self.play(Create(b_fp), run_time=0.5)
            self.play(ReplacementTransform(b_fp, hbox(chars(cp, 2, 15, 23), color=BAD)), run_time=0.6)
            rest(self, tr)
        keep = {id(vis), id(t.rows[1]), id(t.rows[2]), id(under)}
        self.play(*[FadeOut(m) for m in self.mobjects if id(m) not in keep], run_time=0.5)
        self.remove(vis, t.rows[1], t.rows[2])
        old3 = t.upto(3)
        self.add(old3)

        t2 = DictTable(size=30)
        vis6 = t2.upto(6)
        lad, ladv = ladder_right(0)
        t2.move_to(LEFT * 2.3 + UP * 0.0).align_to(UP * 3.2, UP)
        under2 = Line(t2.rows[2][1][:6].get_corner(DL) + DOWN * 0.06, t2.rows[2][1][:6].get_corner(DR) + DOWN * 0.06,
                      color=PRIMARY, stroke_width=4)
        lad.move_to(RIGHT * 4.6 + DOWN * 0.3)
        credit = tag("Curry 1934,  Howard 1969", size=24).to_edge(DOWN, buff=0.4).match_x(t2.upto(6))
        with self.voiceover(text=N("s03.b7")) as tr:
            self.play(ReplacementTransform(old3, t2.upto(3)), ReplacementTransform(under, under2), run_time=0.9)
            self.play(LaggedStart(*[t2.show_row(i) for i in (3, 4, 5)], lag_ratio=0.5), run_time=1.6)
            wait_until(self, tr, "simple")
            self.play(FadeIn(ladv), run_time=0.6)
            self.play(lad.light(0), run_time=0.8)
            wait_until(self, tr, "Howard")
            self.play(FadeIn(credit), run_time=0.6)
            rest(self, tr)
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.5)


def strike_through(mob, color=BAD):
    return Line(mob.get_left() + LEFT * 0.05, mob.get_right() + RIGHT * 0.05, color=color, stroke_width=5)


def table_and_ladder(k_rows, k_rungs, size=30):
    """The full dictionary on the left and the ladder on the right (s03 end, s05, s06, s08, s10)."""
    t = DictTable(size=size)
    t.move_to(LEFT * 2.3).align_to(UP * 3.2, UP)
    lad = Ladder()
    ladv = lad.lit_state(k_rungs)
    lad.move_to(RIGHT * 4.6 + DOWN * 0.3)
    return t, lad, VGroup(t.upto(k_rows), ladv)


def fork(root, left, right, size=30, lcol=SECONDARY, rcol=TERTIARY, spread=3.2, drop=1.6):
    """A root label with two arrows down to two end labels."""
    l = text(left, size=size, color=lcol) if isinstance(left, str) else left
    r = text(right, size=size, color=rcol) if isinstance(right, str) else right
    l.move_to(root.get_bottom() + DOWN * drop + LEFT * spread)
    r.move_to(root.get_bottom() + DOWN * drop + RIGHT * spread)
    al = Arrow(root.get_bottom(), l.get_top(), buff=0.15, color=MUTED, stroke_width=3)
    ar = Arrow(root.get_bottom(), r.get_top(), buff=0.15, color=MUTED, stroke_width=3)
    g = VGroup(al, ar, l, r)
    g.l, g.r, g.al, g.ar = l, r, al, ar
    return g


# ---------------------------------------------------------------------------
# s04 Classical vs intuitionistic
# ---------------------------------------------------------------------------


def truth_table(size=50):
    hdr = [math("P", size=size), math(r"\neg P", size=size), math(r"P \lor \neg P", size=size, color=PRIMARY)]
    rows = [["T", "F", "T"], ["F", "T", "T"]]
    cells = [hdr] + [[math(r"\text{" + v + "}", size=size, color=(GOOD if (j == 2) else FG)) for j, v in enumerate(r)]
                     for r in rows]
    xs = [-3.0, 0, 3.4]
    g = VGroup()
    for i, row in enumerate(cells):
        for j, c in enumerate(row):
            c.move_to([xs[j], -i * 1.0, 0])
            g.add(c)
    rule = Line([-4.0, -0.5, 0], [4.8, -0.5, 0], color=MUTED, stroke_width=2)
    g.add(rule)
    return g


class S04Classical(VoiceoverScene):
    def construct(self):
        self.set_speech_service(get_speech_service())
        tt = truth_table().move_to(UP * 1.7)
        em = panel("em", size=34).move_to(DOWN * 1.6)
        q3 = em.part(1, "???")
        with self.voiceover(text=N("s04.b1")) as tr:
            wait_until(self, tr, "missing")
            self.play(FadeIn(tt), run_time=0.8)
            self.play(Indicate(VGroup(*tt[8:9], tt[5]), color=GOOD), run_time=0.9)
            self.wait(frac_time(tr, 0.15))
            self.play(FadeIn(em, shift=UP * 0.2), run_time=0.8)
            q3.set_color(PRIMARY)
            for _ in range(3):
                self.play(q3.animate.set_opacity(0.2), run_time=0.35)
                self.play(q3.animate.set_opacity(1), run_time=0.35)
            rest(self, tr)

        root = mono("???", 36, PRIMARY)
        emt = panel("em", size=30)
        emt.move_to(UP * 2.6)
        root.move_to(UP * 1.2)
        fk = fork(root, mono(".inl (a proof of P)", 28, SECONDARY), mono(".inr (a proof of \u00acP)", 28, TERTIARY))
        tagl = text("the tag: left or right", size=26, color=PRIMARY).next_to(VGroup(fk.l, fk.r), DOWN, 0.5)
        tagu = Line(tagl.get_corner(DL) + DOWN * 0.08, tagl.get_corner(DR) + DOWN * 0.08, color=PRIMARY, stroke_width=4)
        which = text("which one?", size=40, color=PRIMARY).next_to(tagl, DOWN, 0.5)
        with self.voiceover(text=N("s04.b2")) as tr:
            self.play(FadeOut(tt), ReplacementTransform(em, emt), run_time=0.8)
            self.play(TransformFromCopy(emt.part(1, "???"), root), run_time=0.6)
            self.play(GrowArrow(fk.al), GrowArrow(fk.ar), FadeIn(fk.l), FadeIn(fk.r), run_time=0.9)
            self.play(FadeIn(tagl), Create(tagu), run_time=0.6)
            wait_until(self, tr, "pick")
            self.play(FadeIn(which, scale=1.2), run_time=0.6)
            rest(self, tr)

        halts = text("machine M halts on input w", size=36, color=FG).move_to(root)
        hl = text("halts", size=32, color=GOOD).move_to(fk.l)
        nh = text("never halts", size=32, color=BAD).move_to(fk.r)
        every = text("for every machine M and every input w", size=28, color=MUTED).next_to(halts, UP, 0.35)
        tm = VGroup(*[Square(0.4, color=MUTED, stroke_width=2) for _ in range(6)]).arrange(RIGHT, buff=0)
        head = Triangle(color=PRIMARY).set_fill(PRIMARY, 1).scale(0.12).rotate(PI).next_to(tm[2], UP, 0.05)
        tape = VGroup(tm, head).next_to(halts, LEFT, 0.5)
        hp = text("= the halting problem", size=34, color=BAD).move_to(DOWN * 2.6)
        with self.voiceover(text=N("s04.b3")) as tr:
            self.play(FadeOut(VGroup(emt, which, tagl, tagu)), ReplacementTransform(root, halts),
                      ReplacementTransform(fk.l, hl), ReplacementTransform(fk.r, nh), run_time=1.0)
            self.play(FadeIn(tape), run_time=0.6)
            self.play(FadeIn(every), run_time=0.7)
            wait_until(self, tr, "halting")
            grp = VGroup(halts, fk.al, fk.ar, hl, nh)
            self.play(Create(xout(grp, pad=0.2)), FadeIn(hp), run_time=0.8)
            rest(self, tr)
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.5)

        nn = panel("nn_em", size=34).move_to(UP * 1.2)
        # "  fun h => h (.inr (fun p => h (.inl p)))"
        inr = nn.part(1, ".inr")
        inl = nn.part(1, ".inl p")
        p_in = chars(nn, 1, 24, 25)
        h_lab = text("h: \"P or not P leads to a contradiction\"", size=28, color=MUTED).next_to(nn, DOWN, 1.0)
        first = text("answer: right, not P", size=30, color=TERTIARY)
        switch = text("h hands over a proof of P: switch to left, with that proof", size=30, color=SECONDARY)
        VGroup(first, switch).arrange(DOWN, buff=0.35).next_to(h_lab, DOWN, 0.5)
        noax = text("uses no axioms", size=32, color=GOOD).to_edge(DOWN, buff=0.5)
        with self.voiceover(text=N("s04.b4")) as tr:
            self.play(FadeIn(nn, shift=UP * 0.2), run_time=0.8)
            self.play(FadeIn(h_lab), Indicate(nn.part(1, "fun h"), color=PRIMARY), run_time=1.0)
            wait_until(self, tr, "first")
            self.play(Create(hbox(inr, TERTIARY)), FadeIn(first), run_time=0.7)
            wait_until(self, tr, "switch")
            arc = CurvedArrow(p_in.get_bottom() + DOWN * 0.08, inl.get_bottom() + DOWN * 0.12, angle=PI / 2,
                              color=SECONDARY, stroke_width=3)
            self.play(Create(hbox(inl, SECONDARY)), Create(arc), FadeIn(switch), run_time=0.9)
            wait_until(self, tr, "axioms")
            self.play(FadeIn(noax, shift=UP * 0.15), run_time=0.6)
            rest(self, tr)
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.5)

        cl = text("classical logic", size=40, color=SECONDARY)
        il = text("intuitionistic logic", size=40, color=PRIMARY)
        VGroup(cl, il).arrange(RIGHT, buff=2.5).move_to(UP * 2.0)
        e1 = math(r"P \lor \neg P", size=48).next_to(cl, DOWN, 0.8)
        e2 = math(r"P \lor \neg P", size=48).next_to(il, DOWN, 0.8)
        t1 = tick(56).next_to(e1, RIGHT, 0.4)
        b2 = Square(0.55, color=MUTED, stroke_width=3).next_to(e2, RIGHT, 0.4)
        say = text("to prove P or Q, say which", size=32, color=PRIMARY).next_to(VGroup(e2, b2), DOWN, 0.8)
        with self.voiceover(text=N("s04.b5")) as tr:
            self.play(FadeIn(cl), FadeIn(e1), FadeIn(t1), run_time=0.8)
            self.play(FadeIn(il), FadeIn(e2), Create(b2), run_time=0.8)
            wait_until(self, tr, "which")
            self.play(FadeIn(say, shift=UP * 0.15), run_time=0.7)
            rest(self, tr)
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.5)

        dp = panel("dec", size=32).move_to(UP * 2.0)
        dout = VGroup(tag("output:", size=26), out_text("dec", 32)).arrange(RIGHT, buff=0.2).next_to(dp, DOWN, 0.35)
        d91 = math(r"91 = 7 \cdot 13", size=40, color=MUTED).next_to(dout, RIGHT, 0.8)
        dbox = card_box(["Decidable P:", "a true-or-false answer,", "plus a proof that the answer is right"],
                        color=GOOD).next_to(dout, DOWN, 0.7).match_x(dp)
        with self.voiceover(text=N("s04.b6")) as tr:
            self.play(FadeIn(dp, shift=UP * 0.2), run_time=0.8)
            self.wait(frac_time(tr, 0.15))
            self.play(FadeIn(dout), FadeIn(d91), run_time=0.7)
            wait_until(self, tr, "decidable")
            self.play(FadeIn(dbox, shift=UP * 0.15), run_time=0.8)
            rest(self, tr)
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.5)

        ec = panel("emcheck", size=32).move_to(UP * 2.4)
        eco = out_text("emcheck", 32).next_to(ec, DOWN, 0.35)
        ax = card_box(["axiom Classical.choice"], color=BAD, mono_=True).move_to(DOWN * 1.4)
        ax_a = Arrow(ax.get_top(), eco.get_bottom(), buff=0.15, color=MUTED, stroke_width=3)
        nocode = tag("no code inside", size=28, color=BAD).next_to(ax, DOWN, 0.3)
        with self.voiceover(text=N("s04.b7")) as tr:
            self.play(FadeIn(ec, shift=UP * 0.2), run_time=0.7)
            self.play(FadeIn(eco), run_time=0.6)
            wait_until(self, tr, "axiom")
            self.play(FadeIn(ax), GrowArrow(ax_a), run_time=0.8)
            self.play(FadeIn(nocode), run_time=0.5)
            rest(self, tr)
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.5)

        da = panel("decide_any", size=32).move_to(UP * 1.9)
        er = err_text("decide_any", 26).next_to(da, DOWN, 0.5)
        nc = er[0][0][0]  # placeholder, replaced below
        word = mono("noncomputable", 26, BAD)
        with self.voiceover(text=N("s04.b8")) as tr:
            self.play(FadeIn(da, shift=UP * 0.2), run_time=0.8)
            wait_until(self, tr, "refuses")
            self.play(FadeIn(er, shift=DOWN * 0.1), run_time=0.8)
            wait_until(self, tr, "noncomputable")
            nc_g = er[1][4:17]  # "noncomputable" in "as 'noncomputable' because ..."
            und = Line(nc_g.get_corner(DL) + DOWN * 0.07, nc_g.get_corner(DR) + DOWN * 0.07, color=PRIMARY,
                       stroke_width=4)
            self.play(Create(und), nc_g.animate.set_color(PRIMARY), run_time=0.6)
            rest(self, tr)

        big = text("noncomputable", size=72, color=PRIMARY, weight="BOLD").move_to(UP * 1.6)
        l1 = text("classical proof: it's true", size=36, color=SECONDARY).move_to(DOWN * 0.6)
        l2 = text("constructive proof: it's true, and here it is", size=36, color=GOOD).next_to(l1, DOWN, 0.5)
        with self.voiceover(text=N("s04.b9")) as tr:
            self.play(FadeOut(VGroup(da, er, und)), FadeIn(big, scale=1.2), run_time=0.9)
            wait_until(self, tr, "true")
            self.play(FadeIn(l1, shift=UP * 0.15), run_time=0.6)
            wait_until(self, tr, "thing")
            self.play(FadeIn(l2, shift=UP * 0.15), run_time=0.6)
            rest(self, tr)
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.5)


def card_box(lines, color=MUTED, size=30, mono_=False):
    body = VGroup(*[(mono(l, size - 2, FG) if mono_ else text(l, size=size)) for l in lines])
    body.arrange(DOWN, buff=0.15)
    box = SurroundingRectangle(body, buff=0.3, corner_radius=0.15, color=color, stroke_width=3)
    return VGroup(box, body)


# ---------------------------------------------------------------------------
# s05 For all, there exists
# ---------------------------------------------------------------------------


class S05Quantifiers(VoiceoverScene):
    def construct(self):
        self.set_speech_service(get_speech_service())
        lad, ladv = ladder_right(1)
        st = math(r"\text{for every number } n,\quad n + 0 = n", size=50, substrings_to_isolate=["n"])
        st.move_to(LEFT * 2.2 + UP * 0.3)
        with self.voiceover(text=N("s05.b1")) as tr:
            self.play(FadeIn(ladv), run_time=0.6)
            self.play(Write(st), run_time=1.2)
            wait_until(self, tr, "mentions")
            ns = VGroup(*[m for m in st if m.get_tex_string() == "n"])
            self.play(ns.animate.set_color(PRIMARY), Indicate(ns, color=PRIMARY), run_time=0.8)
            rest(self, tr)

        az = panel("add_zero", size=30).move_to(UP * 2.3)
        mach = RoundedRectangle(corner_radius=0.15, width=2.6, height=1.2, color=SECONDARY, stroke_width=3)
        mlab = mono("add_zero'", 26, SECONDARY).move_to(mach)
        mg = VGroup(mach, mlab).move_to(DOWN * 0.9)
        def io(n):
            i = math(str(n), size=48).next_to(mach, LEFT, 1.4)
            o = text(f"proof that {n} + 0 = {n}", size=30, color=GOOD).next_to(mach, RIGHT, 0.7)
            return i, o
        i5, o5 = io(5)
        i12, o12 = io(12)
        a_in = Arrow(i5.get_right(), mach.get_left(), buff=0.15, color=MUTED, stroke_width=3)
        a_out = Arrow(mach.get_right(), o5.get_left(), buff=0.15, color=MUTED, stroke_width=3)
        with self.voiceover(text=N("s05.b2")) as tr:
            self.play(FadeOut(ladv), FadeOut(st), FadeIn(az, shift=UP * 0.2), run_time=0.8)
            self.play(FadeIn(mg), GrowArrow(a_in), GrowArrow(a_out), run_time=0.7)
            self.play(FadeIn(i5), run_time=0.4)
            self.play(i5.copy().animate.move_to(mach).set_opacity(0), FadeIn(o5, shift=RIGHT * 0.2), run_time=0.8)
            self.play(FadeOut(i5), FadeOut(o5), FadeIn(i12), run_time=0.4)
            self.play(i12.copy().animate.move_to(mach).set_opacity(0), FadeIn(o12, shift=RIGHT * 0.2), run_time=0.8)
            self.play(Create(hbox(az.part(1, "rfl"))), run_time=0.6)
            rest(self, tr)
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.5)

        t1 = mono("String \u2192 Nat", 40)
        t2 = mono("(n : Nat) \u2192 n + 0 = n", 40)
        VGroup(t1, t2).arrange(RIGHT, buff=1.6).move_to(UP * 1.6)
        l1 = text("always the same", size=28, color=MUTED).next_to(t1[-3:], DOWN, 0.4)
        n_in = t2[1:2]
        n_out = t2[-1:]
        dep = CurvedArrow(n_in.get_top() + UP * 0.1, t2[12:13].get_top() + UP * 0.1, angle=-PI / 3, color=PRIMARY,
                          stroke_width=4)
        dlab = text("the output type mentions the input", size=28, color=PRIMARY).next_to(t2, DOWN, 0.45)
        pe = panel("pi_eq", size=32).move_to(DOWN * 1.6)
        with self.voiceover(text=N("s05.b3")) as tr:
            self.play(FadeIn(t1), FadeIn(l1), run_time=0.7)
            self.play(FadeIn(t2), run_time=0.7)
            wait_until(self, tr, "depends")
            self.play(Create(dep), n_in.animate.set_color(PRIMARY), t2[12:13].animate.set_color(PRIMARY),
                      t2[-1:].animate.set_color(PRIMARY), FadeIn(dlab), run_time=0.9)
            wait_until(self, tr, "same")
            self.play(FadeIn(pe, shift=UP * 0.2), run_time=0.8)
            rest(self, tr)
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.5)

        sx = panel("six", size=36).move_to(UP * 1.8)
        three = sx.part(1, "3")
        rfl = sx.part(1, "rfl")
        wl = text("witness", size=30, color=SECONDARY).next_to(three, DOWN, 1.2).shift(LEFT * 1.0)
        pl = text("proof that 3 + 3 = 6", size=30, color=GOOD).next_to(rfl, DOWN, 1.2).shift(RIGHT * 1.6)
        wptr = Line(wl.get_top(), three.get_bottom() + DOWN * 0.08, color=SECONDARY, stroke_width=2)
        pptr = Line(pl.get_top(), rfl.get_bottom() + DOWN * 0.08, color=GOOD, stroke_width=2)
        four = mono("4", 36, PRIMARY).move_to(three)
        pl4 = text("proof that 4 + 4 = 6 ?", size=30, color=BAD).move_to(pl)
        with self.voiceover(text=N("s05.b4")) as tr:
            self.play(FadeIn(sx, shift=UP * 0.2), run_time=0.8)
            wait_until(self, tr, "pair")
            self.play(Create(hbox(sx.part(1, "\u27e83, rfl\u27e9"))), run_time=0.6)
            self.play(FadeIn(wl), Create(wptr), run_time=0.5)
            self.play(FadeIn(pl), Create(pptr), run_time=0.5)
            wait_until(self, tr, "second")
            dep2 = CurvedArrow(wl.get_right() + RIGHT * 0.1, pl.get_left() + LEFT * 0.1, angle=PI / 4, color=PRIMARY,
                               stroke_width=3)
            self.play(Create(dep2), run_time=0.6)
            wait_until(self, tr, "four")
            self.play(Transform(three, four), Transform(pl, pl4), run_time=0.7)
            rest(self, tr)
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.5)

        t, lad, vis = table_and_ladder(6, 1)
        credit = tag(f"Per {LOF}, 1970s", size=26).to_edge(DOWN, buff=0.4).match_x(t.upto(8))
        with self.voiceover(text=N("s05.b5")) as tr:
            self.play(FadeIn(vis), run_time=0.8)
            self.play(t.show_row(6), run_time=0.7)
            self.play(t.show_row(7), run_time=0.7)
            wait_until(self, tr, "dependent")
            self.play(lad.light(1), run_time=0.8)
            wait_until(self, tr, "Lof")
            self.play(FadeIn(credit), run_time=0.6)
            rest(self, tr)
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.5)


# ---------------------------------------------------------------------------
# s06 Induction is recursion
# ---------------------------------------------------------------------------


class S06Induction(VoiceoverScene):
    def construct(self):
        self.set_speech_service(get_speech_service())
        np_ = panel("nat", size=32).move_to(UP * 2.0)
        beads = VGroup(*[mono(s, 34) for s in ["zero", "succ zero", "succ (succ zero)"]], mono("...", 34, MUTED))
        beads.arrange(RIGHT, buff=0.9).move_to(DOWN * 1.0)
        nums = VGroup(*[math(str(i), size=48, color=PRIMARY).next_to(beads[i], DOWN, 0.4) for i in range(3)])
        with self.voiceover(text=N("s06.b1")) as tr:
            wait_until(self, tr, "defined")
            self.play(FadeIn(np_, shift=UP * 0.2), run_time=0.8)
            self.play(Indicate(np_.line(1), color=PRIMARY), run_time=0.8)
            self.play(Indicate(np_.line(2), color=PRIMARY), run_time=0.8)
            self.play(LaggedStart(*[FadeIn(VGroup(beads[i], nums[i]) if i < 3 else beads[i], shift=RIGHT * 0.2)
                                    for i in range(4)], lag_ratio=0.4), run_time=1.6)
            rest(self, tr)
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.5)

        dp = panel("double", size=32)
        za = panel("zero_add", size=32)
        VGroup(dp, za).arrange(DOWN, buff=0.7, aligned_edge=LEFT).move_to(UP * 0.4)
        za.align_to(dp, LEFT)
        dcall = dp.part(2, "double n")
        dname = dp.part(0, "double")
        with self.voiceover(text=N("s06.b2")) as tr:
            self.play(FadeIn(dp, shift=UP * 0.2), run_time=0.8)
            self.play(Indicate(dp.line(1), color=PRIMARY), run_time=0.8)
            self.play(Indicate(dp.line(2), color=PRIMARY), run_time=0.8)
            wait_until(self, tr, "calls")
            arc = tag("calls itself", size=28, color=PRIMARY).next_to(dp.bg, RIGHT, 0.35).match_y(dp.lines[2])
            self.play(Create(hbox(dcall)), Create(hbox(dname)), FadeIn(arc), run_time=0.8)
            rest(self, tr)

        zcall = za.part(2, "zero_add' n")
        zname = za.part(0, "zero_add'")
        hyp = text("induction hypothesis", size=30, color=PRIMARY).next_to(za, DOWN, 0.45).align_to(zcall, LEFT)
        hyp_l = Line(hyp.get_top(), zcall.get_bottom() + DOWN * 0.06, color=PRIMARY, stroke_width=2)
        why = text("Lean's + recurses on the second number", size=28, color=MUTED).next_to(za, DOWN, 0.45)
        with self.voiceover(text=N("s06.b3")) as tr:
            self.play(FadeIn(za, shift=UP * 0.2), run_time=0.8)
            self.play(FadeIn(why), run_time=0.6)
            self.wait(frac_time(tr, 0.12))
            self.play(FadeOut(why), run_time=0.4)
            self.play(Indicate(za.line(1), color=PRIMARY), Indicate(dp.line(1), color=PRIMARY), run_time=0.9)
            self.play(Indicate(za.line(2), color=PRIMARY), Indicate(dp.line(2), color=PRIMARY), run_time=0.9)
            wait_until(self, tr, "hypothesis")
            self.play(Create(hbox(zcall)), Create(hbox(zname)), FadeIn(hyp), Create(hyp_l), run_time=0.9)
            rest(self, tr)
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.5)

        nr = panel("natrec", size=28).move_to(LEFT * 1.3 + UP * 0.9)
        simp = tag("(simplified)", size=24).next_to(nr, UP, 0.2).align_to(nr, RIGHT)
        labs = [("base case", 1, "zero"), ("step", 2, "next"), ("for every n", 3, "every")]
        lab_m = {}
        for s_, i, mk in labs:
            lab_m[mk] = text(s_, size=30, color=PRIMARY).next_to(nr.bg, RIGHT, 0.35).match_y(nr.lines[i])
        with self.voiceover(text=N("s06.b4")) as tr:
            self.play(FadeIn(nr, shift=UP * 0.2), FadeIn(simp), run_time=0.9)
            for s_, i, mk in labs:
                wait_until(self, tr, mk)
                self.play(FadeIn(lab_m[mk], shift=LEFT * 0.15), Indicate(nr.line(i), color=PRIMARY), run_time=0.7)
            rest(self, tr)

        mot = nr.part(0, "motive")
        o1 = text("a proposition  \u2192  induction", size=32, color=GOOD)
        o2 = text("a type of data  \u2192  recursion", size=32, color=SECONDARY)
        VGroup(o1, o2).arrange(DOWN, buff=0.4, aligned_edge=LEFT).next_to(nr, DOWN, 0.8).align_to(nr, LEFT)
        a1 = Arrow(mot.get_bottom(), o1.get_left() + LEFT * 0.1, buff=0.1, color=GOOD, stroke_width=3)
        with self.voiceover(text=N("s06.b5")) as tr:
            self.play(Create(hbox(mot)), mot.animate.set_color(PRIMARY), run_time=0.7)
            wait_until(self, tr, "proposition")
            self.play(FadeIn(o1, shift=RIGHT * 0.2), run_time=0.6)
            wait_until(self, tr, "data")
            self.play(FadeIn(o2, shift=RIGHT * 0.2), run_time=0.6)
            rest(self, tr)
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.5)

        t, lad, vis = table_and_ladder(8, 2)
        icons = tag("lists, trees, ...", size=24).next_to(lad.boxes[2], LEFT, 0.3)
        with self.voiceover(text=N("s06.b6")) as tr:
            self.play(FadeIn(vis), run_time=0.8)
            self.play(t.show_row(8), run_time=0.7)
            self.wait(frac_time(tr, 0.2))
            wait_until(self, tr, "rung")
            self.play(lad.light(2), FadeIn(icons), run_time=0.8)
            rest(self, tr)
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.5)


# ---------------------------------------------------------------------------
# s07 A theorem you can run
# ---------------------------------------------------------------------------

BOOK = [
    [r"\textbf{Theorem.} Every natural number $n$", r"has a binary representation."],
    [r"\textit{Proof.} Strong induction on $n$."],
    [r"If $n = 0$, take the empty string."],
    [r"Otherwise, write $n = 2q + r$,", r"with $r = 0$ or $1$."],
    [r"Since $q < n$, $q$ has a representation."],
    [r"Add $r$ as the new ones digit."],
    [r"Its value is $r + 2q = n$. \qquad $\blacksquare$"],
]


def textbook(size=30):
    from mathvid.style import tex
    sents = VGroup()
    for lines in BOOK:
        g = VGroup(*[tex(l, size=size) for l in lines]).arrange(DOWN, buff=0.12, aligned_edge=LEFT)
        sents.add(g)
    sents.arrange(DOWN, buff=0.32, aligned_edge=LEFT)
    return sents


class S07Binary(VoiceoverScene):
    def construct(self):
        self.set_speech_service(get_speech_service())
        bk = textbook(32)
        bk.to_edge(LEFT, buff=0.25).shift(UP * 0.1)
        for sgrp in bk:
            sgrp.set_opacity(0.35)
        with self.voiceover(text=N("s07.b1")) as tr:
            self.play(FadeIn(bk), run_time=0.8)
            self.play(bk[0].animate.set_opacity(1), run_time=0.6)
            self.wait(frac_time(tr, 0.15))
            self.play(bk[1].animate.set_opacity(1), run_time=0.6)
            wait_until(self, tr, "smaller")
            self.play(Indicate(bk[1], color=PRIMARY, scale_factor=1.05), run_time=0.8)
            rest(self, tr)

        with self.voiceover(text=N("s07.b2")) as tr:
            self.play(bk[2].animate.set_opacity(1), run_time=0.6)
            wait_until(self, tr, "remainder")
            self.play(bk[3].animate.set_opacity(1), run_time=0.6)
            self.wait(frac_time(tr, 0.12))
            self.play(bk[4].animate.set_opacity(1), run_time=0.6)
            self.wait(frac_time(tr, 0.12))
            self.play(bk[5].animate.set_opacity(1), run_time=0.6)
            self.play(bk[6].animate.set_opacity(1), run_time=0.6)
            rest(self, tr)

        vp = panel("value", size=21)
        tb = panel("toBinary", size=21)
        right = VGroup(vp, tb).arrange(DOWN, buff=0.3, aligned_edge=LEFT)
        right.to_edge(RIGHT, buff=0.2)
        gl = text("a digit, 0 or 1", size=22, color=MUTED).next_to(vp.bg, UP, 0.12).align_to(vp.bg, RIGHT)
        fin = vp.part(0, "Fin 2")
        with self.voiceover(text=N("s07.b3")) as tr:
            self.play(FadeIn(vp, shift=LEFT * 0.2), run_time=0.8)
            self.play(Create(hbox(fin, MUTED)), FadeIn(gl), run_time=0.6)
            wait_until(self, tr, "value")
            self.play(Indicate(vp.line(2), color=PRIMARY), run_time=0.9)
            rest(self, tr)

        pairs = [("zero", 2, [2]), ("less", 4, [4]), ("recurse", 5, [4]), ("front", 6, [5])]
        cols = [SECONDARY, TERTIARY, GOOD, PRIMARY]
        with self.voiceover(text=N("s07.b4")) as tr:
            self.play(FadeIn(tb.bg), FadeIn(tb.lines[0]), FadeIn(tb.lines[1]), run_time=0.7)
            for (mk, li, bis), col in zip(pairs, cols):
                wait_until(self, tr, mk)
                extra = [tb.lines[3]] if li == 4 else []
                extra += [tb.lines[7]] if li == 6 else []
                cl = tb.lines[li]
                bx = hbox(VGroup(cl.body(), *[e.body() for e in extra if li == 6]), color=col, buff=0.04)
                sb = hbox(bk[bis[0]], color=col, buff=0.06)
                con = Line(sb.get_right(), bx.get_left(), color=col, stroke_width=2)
                self.play(*[FadeIn(e) for e in extra], FadeIn(cl, shift=LEFT * 0.15), run_time=0.5)
                self.play(Create(bx), Create(sb), Create(con), run_time=0.5)
            rest(self, tr)

        bys = VGroup(tb.part(2, "by simp [value, h]"), tb.part(4, "by omega"), tb.part(6, "by omega"),
                     tb.part(7, "by simp [value, hds]; omega"))
        hv = tb.part(4, "have : n / 2 < n")
        why = text("why the induction is allowed  =  why the recursion stops", size=26, color=PRIMARY)
        why.to_edge(DOWN, buff=0.35)
        with self.voiceover(text=N("s07.b5")) as tr:
            boxes = [m for m in self.mobjects if isinstance(m, (SurroundingRectangle, Line))]
            self.play(*[FadeOut(b) for b in boxes], run_time=0.4)
            self.play(Indicate(bys, color=MUTED, scale_factor=1.02), run_time=0.8)
            wait_until(self, tr, "arith")
            self.play(bys.animate.set_opacity(0.35), Indicate(bk[6], color=PRIMARY, scale_factor=1.04), run_time=0.8)
            wait_until(self, tr, "allowed")
            self.play(Create(hbox(hv, PRIMARY)), Create(hbox(bk[4], PRIMARY)), run_time=0.6)
            wait_until(self, tr, "stops")
            self.play(FadeIn(why, shift=UP * 0.15), run_time=0.7)
            rest(self, tr)
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.5)

        ev = panel("eval13", size=32).move_to(UP * 2.8 + LEFT * 2.4)
        steps = [("six", r"13 = 2 \cdot 6 + ", "1"), ("three", r"6 = 2 \cdot 3 + ", "0"),
                 ("one", r"3 = 2 \cdot 1 + ", "1"), ("bottom", r"1 = 2 \cdot 0 + ", "1")]
        rows = VGroup(*[math(a, r, size=46) for _, a, r in steps]).arrange(DOWN, buff=0.35, aligned_edge=RIGHT)
        rows.next_to(ev, DOWN, 0.6).align_to(ev, LEFT).shift(RIGHT * 0.5)
        for r in rows:
            r[1].set_color(PRIMARY)
        done = text("0: done", size=30, color=MUTED).next_to(rows, DOWN, 0.3).align_to(rows, RIGHT)
        outl = out_text("eval13", 54).move_to(RIGHT * 3.6 + DOWN * 0.3)
        olab = tag("ones digit first", size=26).next_to(outl, DOWN, 0.3)
        with self.voiceover(text=N("s07.b6")) as tr:
            self.play(FadeIn(ev, shift=DOWN * 0.15), run_time=0.6)
            for (mk, _, _), r in zip(steps, rows):
                wait_until(self, tr, mk)
                self.play(FadeIn(r, shift=UP * 0.1), run_time=0.5)
            self.play(FadeIn(done), run_time=0.4)
            wait_until(self, tr, "off")
            digs = VGroup(*[r[1].copy() for r in rows])
            self.play(LaggedStart(*[d.animate.move_to(outl[1 + 3 * i]) for i, d in enumerate(digs)], lag_ratio=0.2),
                      run_time=1.0)
            self.play(FadeOut(digs), FadeIn(outl), FadeIn(olab), run_time=0.5)
            rest(self, tr)
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.5)

        hb = panel("has_binary", size=28).move_to(UP * 2.3)
        hbt = tick(48).next_to(hb, RIGHT, 0.3)
        dg = panel("digits", size=28).next_to(hb, DOWN, 0.5)
        der = err_text("digits", 26).next_to(dg, DOWN, 0.35)
        with self.voiceover(text=N("s07.b7")) as tr:
            self.play(FadeIn(hb, shift=UP * 0.2), run_time=0.8)
            self.play(FadeIn(hbt, scale=1.3), run_time=0.5)
            wait_until(self, tr, "back")
            self.play(FadeIn(dg, shift=UP * 0.2), run_time=0.7)
            self.play(FadeIn(der), run_time=0.6)
            rest(self, tr)
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.5)

        ty = mono("{ ds : List (Fin 2) // value ds = n }", 34, FG).move_to(UP * 2.4)
        tyb = hbox(ty, PRIMARY, buff=0.15)
        rd = text("a list ds, together with a proof that value ds = n", size=32, color=MUTED).next_to(tyb, DOWN, 0.4)
        c1 = VGroup(mono("\u2203 ds, value ds = n", 30, SECONDARY), text("there are digits", size=32, color=SECONDARY))
        c2 = VGroup(mono("{ ds // value ds = n }", 30, GOOD), text("here are the digits", size=32, color=GOOD))
        for c in (c1, c2):
            c.arrange(RIGHT, buff=0.8)
        c1[1].shift(RIGHT * (c2[1].get_left()[0] - c1[1].get_left()[0]))
        VGroup(c1, c2).arrange(DOWN, buff=0.55, aligned_edge=LEFT).move_to(DOWN * 1.4)
        c1[1].align_to(c2[1], LEFT)
        with self.voiceover(text=N("s07.b8")) as tr:
            self.play(FadeIn(ty), Create(tyb), run_time=0.8)
            self.play(FadeIn(rd), run_time=0.7)
            wait_until(self, tr, "are")
            self.play(FadeIn(c1, shift=UP * 0.15), run_time=0.6)
            wait_until(self, tr, "here")
            self.play(FadeIn(c2, shift=UP * 0.15), run_time=0.6)
            rest(self, tr)
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.5)


# ---------------------------------------------------------------------------
# s08 The equality type
# ---------------------------------------------------------------------------


def slide_picture(scale=1.0):
    """Point a, point b, and a curve h from a to b."""
    a = Dot(LEFT * 2.5, radius=0.1, color=FG)
    b = Dot(RIGHT * 2.5, radius=0.1, color=FG)
    la = math("a", size=44).next_to(a, DOWN, 0.2)
    lb = math("b", size=44).next_to(b, DOWN, 0.2)
    return a, b, la, lb


class S08Equality(VoiceoverScene):
    def construct(self):
        self.set_speech_service(get_speech_service())
        lad, ladv = ladder_right(3)
        eqp = panel("eq", size=32).move_to(LEFT * 2.7 + UP * 1.2)
        nt = text("a = b  is notation for  Eq a b", size=30, color=MUTED).next_to(eqp, DOWN, 0.4)
        nr = text("no other way to build a proof of a = b", size=30, color=PRIMARY).next_to(nt, DOWN, 0.5)
        with self.voiceover(text=N("s08.b1")) as tr:
            self.play(FadeIn(ladv), run_time=0.6)
            self.play(FadeIn(eqp, shift=UP * 0.2), FadeIn(nt), run_time=0.8)
            wait_until(self, tr, "one")
            self.play(Create(hbox(eqp.line(1), GOOD)), run_time=0.6)
            self.wait(frac_time(tr, 0.2))
            self.play(FadeIn(nr), run_time=0.6)
            rest(self, tr)
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.5)

        tt = panel("twotwo", size=36).move_to(UP * 2.2)
        e1 = math("2 + 2", "=", "4", size=60).move_to(UP * 0.2)
        e2 = math("4", "=", "4", size=60).move_to(e1)
        tk = tick(60).next_to(e2, RIGHT, 0.5)
        rl = text("refl", size=34, color=GOOD).next_to(tk, RIGHT, 0.2)
        q = text("how do you use a proof of a = b?", size=40, color=PRIMARY).move_to(DOWN * 2.2)
        with self.voiceover(text=N("s08.b2")) as tr:
            self.play(FadeIn(tt, shift=UP * 0.2), run_time=0.7)
            self.play(Write(e1), run_time=0.8)
            wait_until(self, tr, "same")
            self.play(TransformMatchingTex(e1, e2), run_time=0.8)
            self.play(FadeIn(tk), FadeIn(rl), run_time=0.5)
            wait_until(self, tr, "use")
            self.play(FadeIn(q, shift=UP * 0.15), run_time=0.7)
            rest(self, tr)
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.5)

        nr_ = panel("natrec", size=26)
        er_ = panel("eqrec", size=26)
        n_lab = text("Nat: 2 constructors, so 2 cases", size=28, color=SECONDARY)
        e_lab = text("Eq: 1 constructor, so 1 case", size=28, color=PRIMARY)
        VGroup(nr_, n_lab, er_, e_lab).arrange(DOWN, buff=0.3, aligned_edge=LEFT).move_to(ORIGIN)
        er_.shift(DOWN * 0.3)
        e_lab.shift(DOWN * 0.3)
        simp = tag("(simplified)", size=22).next_to(er_, UP, 0.12).align_to(er_, RIGHT)
        with self.voiceover(text=N("s08.b3")) as tr:
            self.play(FadeIn(nr_), run_time=0.6)
            self.play(Create(hbox(nr_.line(1), SECONDARY)), Create(hbox(nr_.line(2), SECONDARY)), FadeIn(n_lab),
                      run_time=0.7)
            self.play(FadeIn(er_, shift=UP * 0.2), FadeIn(simp), run_time=0.7)
            wait_until(self, tr, "case")
            self.play(Create(hbox(er_.line(1), PRIMARY)), FadeIn(e_lab), run_time=0.7)
            rest(self, tr)
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.5)

        a, b, la, lb = slide_picture()
        A, B = a.get_center(), b.get_center()
        bt = ValueTracker(1.0)

        def hcurve():
            t = bt.get_value()
            P = A + (B - A) * t
            k = 1.4 * t
            c = CubicBezier(A, A + (P - A) / 3 + UP * k, A + 2 * (P - A) / 3 + UP * k, P)
            return c.set_stroke(PRIMARY, 5)
        h = always_redraw(hcurve)
        b.add_updater(lambda m: m.move_to(A + (B - A) * bt.get_value()))
        lb.add_updater(lambda m: m.next_to(b, DOWN, 0.2))
        hl = math("h", size=44, color=PRIMARY).move_to(UP * 1.6)
        rule = text("to prove it for every b and every h : a = b,", size=32).move_to(UP * 3.0)
        rule2 = text("prove it for b = a and h = refl", size=32, color=PRIMARY).next_to(rule, DOWN, 0.2)
        jt = text("J  (path induction)", size=34, color=SECONDARY).move_to(DOWN * 2.3)
        refl = text("refl", size=34, color=GOOD).next_to(a, UP, 0.3)
        with self.voiceover(text=N("s08.b4")) as tr:
            self.play(FadeIn(a), FadeIn(la), FadeIn(b), FadeIn(lb), run_time=0.6)
            self.play(Create(h), FadeIn(hl), run_time=0.8)
            self.play(FadeIn(rule), run_time=0.7)
            self.play(FadeIn(rule2), run_time=0.7)
            wait_until(self, tr, "J")
            self.play(FadeIn(jt), run_time=0.6)
            wait_until(self, tr, "slide")
            self.play(FadeOut(hl), bt.animate.set_value(0.0), run_time=1.6)
            self.play(FadeIn(refl), FadeOut(lb), run_time=0.5)
            rest(self, tr)
        b.clear_updaters()
        lb.clear_updaters()
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.5)

        sy = panel("symm", size=30).move_to(UP * 1.8)
        need = math(r"\text{when } b \text{ is } a:\quad a = a", size=44).next_to(sy, DOWN, 0.8)
        nb = text("refl", size=36, color=GOOD).next_to(need, RIGHT, 0.5)
        ntk = tick(52).next_to(nb, RIGHT, 0.2)
        with self.voiceover(text=N("s08.b5")) as tr:
            self.play(FadeIn(sy, shift=UP * 0.2), run_time=0.8)
            self.play(Indicate(sy.part(2, "Eq.rec"), color=PRIMARY), run_time=0.8)
            wait_until(self, tr, "need")
            self.play(FadeIn(need), run_time=0.6)
            self.play(FadeIn(nb), FadeIn(ntk), Create(hbox(sy.part(2, "rfl"), GOOD)), run_time=0.6)
            rest(self, tr)
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.5)

        tr_ = panel("trans", size=26)
        cg = panel("congr", size=26)
        sb = panel("subst", size=28).move_to(UP * 1.2)
        VGroup(tr_, cg).arrange(DOWN, buff=0.5, aligned_edge=LEFT).move_to(UP * 0.3)
        sub_tag = text("equals can be substituted for equals", size=32, color=PRIMARY)
        sub_tag.next_to(sb, DOWN, 0.45)
        noax = text("no axioms: one constructor and its induction principle", size=30, color=GOOD)
        noax.next_to(sub_tag, DOWN, 0.8)
        with self.voiceover(text=N("s08.b6")) as tr:
            self.play(FadeIn(tr_, shift=UP * 0.2), run_time=0.6)
            self.play(FadeIn(cg, shift=UP * 0.2), run_time=0.6)
            wait_until(self, tr, "substitute")
            self.play(FadeOut(tr_), FadeOut(cg), FadeIn(sb, shift=UP * 0.2), run_time=0.7)
            self.play(Create(hbox(sb.line(1), PRIMARY)), FadeIn(sub_tag), run_time=0.6)
            self.wait(frac_time(tr, 0.1))
            self.play(FadeIn(noax), run_time=0.6)
            rest(self, tr)
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.5)

        t, lad, vis = table_and_ladder(9, 3)
        with self.voiceover(text=N("s08.b7")) as tr:
            self.play(FadeIn(vis), run_time=0.8)
            self.play(t.show_row(9), run_time=0.7)
            wait_until(self, tr, "strange")
            self.play(lad.light(3), run_time=0.8)
            rest(self, tr)
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.5)


# ---------------------------------------------------------------------------
# s09 Are all proofs of a = b the same?
# ---------------------------------------------------------------------------


def bezier(A, B, up, k_end=True):
    return CubicBezier(A, A + (B - A) / 3 + up, A + 2 * (B - A) / 3 + up, B)


def ring(r_in=0.9, r_out=2.3):
    return Annulus(inner_radius=r_in, outer_radius=r_out, color=SECONDARY, fill_opacity=0.15, stroke_width=2,
                   stroke_color=SECONDARY)


class S09Paths(VoiceoverScene):
    def construct(self):
        self.set_speech_service(get_speech_service())
        A, B = LEFT * 3.2 + DOWN * 0.5, RIGHT * 3.2 + DOWN * 0.5
        a = Dot(A, radius=0.1)
        b = Dot(B, radius=0.1)
        la = math("a", size=44).next_to(a, LEFT, 0.25)
        lb = math("b", size=44).next_to(b, RIGHT, 0.25)
        p = bezier(A, B, UP * 2.4).set_stroke(PRIMARY, 5)
        q = bezier(A, B, DOWN * 1.8).set_stroke(SECONDARY, 5)
        lp = math("p", size=48, color=PRIMARY).move_to(p.point_from_proportion(0.5) + UP * 0.4)
        lq = math("q", size=48, color=SECONDARY).move_to(q.point_from_proportion(0.5) + DOWN * 0.4)
        ques = math("p = q\\ ?", size=56).to_edge(UP, buff=0.6)
        with self.voiceover(text=N("s09.b1")) as tr:
            self.play(FadeIn(a), FadeIn(b), FadeIn(la), FadeIn(lb), run_time=0.6)
            self.play(Create(p), FadeIn(lp), run_time=0.8)
            self.play(Create(q), FadeIn(lq), run_time=0.8)
            wait_until(self, tr, "q")
            self.play(Write(ques), run_time=0.7)
            rest(self, tr)

        bt = ValueTracker(1.0)

        def pos():
            return A + (B - A) * bt.get_value()

        def pcurve():
            P = pos()
            c = CubicBezier(A, A + UP * 2.4 + LEFT * 1.3 * (1 - bt.get_value()) + (P - A) / 3,
                            A + 2 * (P - A) / 3 + UP * 2.4 + RIGHT * 1.3 * (1 - bt.get_value()), P)
            return c.set_stroke(PRIMARY, 5)

        def qcurve():
            P = pos()
            k = 1.8 * bt.get_value()
            return bezier(A, P, DOWN * k).set_stroke(SECONDARY, 5)
        p2, q2 = always_redraw(pcurve), always_redraw(qcurve)
        self.remove(p, q)
        self.add(p2, q2)
        b.add_updater(lambda m: m.move_to(pos()))
        lb.add_updater(lambda m: m.next_to(b, RIGHT, 0.25))
        lq.add_updater(lambda m: m.move_to(q2.point_from_proportion(0.5) + DOWN * 0.4))
        lp.add_updater(lambda m: m.move_to(p2.point_from_proportion(0.5) + UP * 0.4))
        ques2 = math(r"\text{loop} = \text{refl}\ ?", size=56).to_edge(UP, buff=0.6)
        with self.voiceover(text=N("s09.b2")) as tr:
            self.play(bt.animate.set_value(0.0), run_time=2.0)
            self.play(FadeOut(lb), FadeOut(b), FadeOut(lq), run_time=0.4)
            wait_until(self, tr, "loop")
            self.play(Transform(ques, ques2), run_time=0.7)
            rest(self, tr)
        for m in (b, lb, lq, lp):
            m.clear_updaters()
        self.remove(q2)

        loop = pcurve()
        self.remove(p2)
        self.add(loop)
        pins = VGroup(*[Triangle(color=BAD).set_fill(BAD, 1).scale(0.12).rotate(PI).move_to(A + DOWN * 0.25 + s)
                        for s in (LEFT * 0.12, RIGHT * 0.12)])
        stuck = text("both ends pinned at a", size=32, color=BAD).move_to(DOWN * 2.6)
        with self.voiceover(text=N("s09.b3")) as tr:
            self.play(FadeIn(pins), run_time=0.5)
            wait_until(self, tr, "free")
            self.play(Wiggle(loop, scale_value=1.05, rotation_angle=0.04 * TAU), run_time=1.0)
            self.play(loop.animate.set_stroke(BAD), FadeIn(stuck), run_time=0.6)
            self.play(loop.animate.set_stroke(PRIMARY), run_time=0.5)
            rest(self, tr)
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.5)

        hs = text("Hofmann and Streicher, 1994", size=40, color=PRIMARY).move_to(UP * 2.4)
        X, Y = LEFT * 2.0 + DOWN * 0.4, RIGHT * 2.0 + DOWN * 0.4
        dots = VGroup(Dot(X), Dot(Y))
        arcs = VGroup(*[bezier(X, Y, UP * k).set_stroke(c, 4) for k, c in ((1.3, PRIMARY), (0, FG), (-1.3, SECONDARY))])
        mdl = text("a model where p and q differ", size=32, color=MUTED).move_to(DOWN * 2.4)
        with self.voiceover(text=N("s09.b4")) as tr:
            self.play(FadeIn(hs), run_time=0.7)
            wait_until(self, tr, "model")
            self.play(FadeIn(dots), LaggedStart(*[Create(c) for c in arcs], lag_ratio=0.3), run_time=1.2)
            self.play(FadeIn(mdl), run_time=0.6)
            rest(self, tr)
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.5)

        rg = ring().move_to(LEFT * 2.3 + DOWN * 0.2)
        C = rg.get_center()
        R = 1.6
        pa = C + R * DOWN
        pb = C + R * RIGHT
        da, db = Dot(pa, radius=0.09), Dot(pb, radius=0.09)
        lpa = math("a", size=40).next_to(da, DOWN, 0.15)
        lpb = math("b", size=40).next_to(db, RIGHT, 0.15)
        path = Arc(radius=R, start_angle=-PI / 2, angle=PI / 2, arc_center=C).set_stroke(PRIMARY, 5)
        big = Circle(radius=R).move_to(C).rotate(-PI / 2).set_stroke(TERTIARY, 5)
        small = Circle(radius=0.35).move_to(pa + RIGHT * 0.35 + UP * 0.0).set_stroke(GOOD, 4)
        t_space = text("a type = a space", size=32, color=SECONDARY)
        t_path = text("a proof of a = b = a path", size=32, color=PRIMARY)
        t_refl = text("a small loop shrinks to refl", size=30, color=GOOD)
        t_hole = text("a loop around the hole can't", size=30, color=TERTIARY)
        right_txt = VGroup(t_space, t_path, t_refl, t_hole).arrange(DOWN, buff=0.45, aligned_edge=LEFT)
        right_txt.move_to(RIGHT * 3.6)
        with self.voiceover(text=N("s09.b5")) as tr:
            wait_until(self, tr, "space")
            self.play(FadeIn(rg), FadeIn(t_space), run_time=0.8)
            self.play(FadeIn(da), FadeIn(db), FadeIn(lpa), FadeIn(lpb), run_time=0.5)
            wait_until(self, tr, "path")
            self.play(Create(path), FadeIn(t_path), run_time=0.8)
            self.play(Create(small), run_time=0.6)
            self.play(small.animate.scale(0.05).move_to(pa), FadeIn(t_refl), run_time=0.9)
            self.remove(small)
            wait_until(self, tr, "around")
            self.play(FadeOut(path), FadeOut(db), FadeOut(lpb), Create(big), run_time=1.0)
            self.play(big.animate.scale(0.75, about_point=pa), run_time=0.7)
            self.play(Wiggle(big, scale_value=1.03), FadeIn(t_hole), run_time=0.9)
            rest(self, tr)
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.5)

        A2, B2 = LEFT * 3.0 + DOWN * 0.6, RIGHT * 3.0 + DOWN * 0.6
        pp = bezier(A2, B2, UP * 1.8).set_stroke(PRIMARY, 5)
        qq = bezier(A2, B2, DOWN * 1.2).set_stroke(SECONDARY, 5)
        mids = VGroup(*[bezier(A2, B2, UP * (1.8 - 3.0 * k / 8)).set_stroke(MUTED, 2, opacity=0.6) for k in range(1, 8)])
        sheet = text("a proof of p = q", size=34, color=FG).move_to(UP * 2.6)
        more = text("and proofs about those, and so on up ...", size=30, color=MUTED).move_to(DOWN * 2.8)
        ends = VGroup(Dot(A2), Dot(B2), math("a", size=40).next_to(A2, LEFT, 0.2), math("b", size=40).next_to(B2, RIGHT, 0.2))
        with self.voiceover(text=N("s09.b6")) as tr:
            self.play(FadeIn(ends), Create(pp), Create(qq), run_time=0.8)
            wait_until(self, tr, "deform")
            mover = pp.copy()
            self.play(LaggedStart(*[Create(m) for m in mids], lag_ratio=0.15),
                      Transform(mover, qq.copy()), run_time=1.6)
            self.play(FadeIn(sheet), run_time=0.6)
            self.wait(frac_time(tr, 0.15))
            self.play(FadeIn(more), run_time=0.7)
            rest(self, tr)
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.5)

        def booldots(x, left=False):
            d = LEFT if left else RIGHT
            tdot = VGroup(Dot(color=FG), text("true", size=30).shift(d))
            fdot = VGroup(Dot(color=FG), text("false", size=30).shift(d))
            for g_ in (tdot, fdot):
                g_[1].next_to(g_[0], d, 0.15)
            g = VGroup(tdot, fdot).arrange(DOWN, buff=0.8, aligned_edge=LEFT).move_to([x, 0, 0])
            return g
        bool_l = booldots(-1.2)
        hdr = math(r"\mathrm{Bool} = \mathrm{Bool}", size=56).to_edge(UP, buff=0.6)
        def matching(shift, swap):
            L = booldots(-1.0, left=True).shift(shift)
            Rr = booldots(1.2).shift(shift)
            tl, fl = L[0][0].get_center(), L[1][0].get_center()
            tr_, fr = Rr[0][0].get_center(), Rr[1][0].get_center()
            col = TERTIARY if swap else GOOD
            ars = VGroup(Arrow(tl, fr if swap else tr_, buff=0.12, color=col, stroke_width=4),
                         Arrow(fl, tr_ if swap else fr, buff=0.12, color=col, stroke_width=4))
            return VGroup(L, Rr, ars)
        m1 = matching(LEFT * 3.4 + DOWN * 0.6, False)
        m2 = matching(RIGHT * 3.2 + DOWN * 0.6, True)
        l1 = text("do nothing", size=32, color=GOOD).next_to(m1, DOWN, 0.4)
        l2 = text("swap", size=32, color=TERTIARY).next_to(m2, DOWN, 0.4)
        uv = text("univalence (Voevodsky)", size=28, color=MUTED).to_edge(DOWN, buff=0.4)
        uvs = text("each one-to-one matching of two types is a proof that they're equal", size=30, color=FG)
        uvs.next_to(hdr, DOWN, 0.4)
        with self.voiceover(text=N("s09.b7")) as tr:
            self.play(FadeIn(uv), run_time=0.6)
            self.play(FadeIn(uvs), run_time=0.8)
            self.play(Write(hdr), run_time=0.7)
            wait_until(self, tr, "itself")
            self.play(FadeIn(m1), FadeIn(l1), run_time=0.8)
            wait_until(self, tr, "swaps")
            self.play(FadeIn(m2), FadeIn(l2), run_time=0.8)
            rest(self, tr)
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.5)

        pi = panel("pirr", size=28).move_to(UP * 2.3 + LEFT * 0.4)
        pit = tick(52).next_to(pi, RIGHT, 0.3)
        lean_says = text("in Lean: any two proofs of the same proposition are equal", size=30, color=PRIMARY)
        lean_says.next_to(pi, DOWN, 0.5)
        contra = math(r"\text{swap} = \text{do nothing}", size=52).move_to(DOWN * 1.6)
        with self.voiceover(text=N("s09.b8")) as tr:
            self.play(FadeIn(pi, shift=UP * 0.2), run_time=0.7)
            wait_until(self, tr, "equal")
            self.play(FadeIn(pit, scale=1.3), FadeIn(lean_says), run_time=0.7)
            self.wait(frac_time(tr, 0.2))
            self.play(FadeIn(contra), run_time=0.6)
            wait_until(self, tr, "contradiction")
            self.play(Create(xout(contra)), run_time=0.6)
            rest(self, tr)
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.5)


# ---------------------------------------------------------------------------
# s10 Ending
# ---------------------------------------------------------------------------


class S10Ending(VoiceoverScene):
    def construct(self):
        self.set_speech_service(get_speech_service())
        t, lad, vis = table_and_ladder(10, 4)
        groups = [(0, 6), (6, 8), (8, 9), (9, 10)]
        with self.voiceover(text=N("s10.b1")) as tr:
            self.play(FadeIn(vis), run_time=0.8)
            wait_until(self, tr, "grow")
            for (i, j), k in zip(groups, range(4)):
                self.play(Indicate(VGroup(*t.rows[i:j]), color=PRIMARY, scale_factor=1.03),
                          Indicate(lad.boxes[k], color=PRIMARY), run_time=0.7)
            wait_until(self, tr, "shape")
            self.play(lad.light(4), run_time=0.8)
            rest(self, tr)

        e1 = text("P or not P", size=40)
        e2 = text("univalence", size=40)
        for e in (e1, e2):
            e.add(text("(axiom)", size=28, color=MUTED).next_to(e, RIGHT, 0.2))
        ents = VGroup(e1, e2).arrange(DOWN, buff=1.4).move_to(LEFT * 2.5)
        circ = VGroup(*[SurroundingRectangle(e, color=PRIMARY, buff=0.25, corner_radius=0.3) for e in ents])
        cub = VGroup(text("cubical type theory", size=30, color=GOOD),
                     text("Cohen, Coquand, Huber, M\u00f6rtberg", size=22, color=MUTED)).arrange(DOWN, buff=0.1)
        cub.next_to(circ[1], RIGHT, 0.6)
        rew = VGroup(text("programs that can rewind", size=30, color=GOOD),
                     text("Griffin, 1990", size=22, color=MUTED)).arrange(DOWN, buff=0.1)
        rew.next_to(circ[0], RIGHT, 0.6)
        rarrow = math(r"\circlearrowleft", size=60, color=GOOD).next_to(rew, RIGHT, 0.3)
        with self.voiceover(text=N("s10.b2")) as tr:
            self.play(FadeOut(vis), FadeOut(lad.labels[4]), FadeOut(lad.boxes), run_time=0.6)
            self.play(FadeIn(ents), run_time=0.7)
            self.play(Create(circ), run_time=0.7)
            wait_until(self, tr, "runs")
            self.play(FadeIn(cub, shift=LEFT * 0.2), run_time=0.7)
            wait_until(self, tr, "changes")
            self.play(FadeIn(rew, shift=LEFT * 0.2), FadeIn(rarrow), run_time=0.7)
            rest(self, tr)

        nn = panel("nn_em", size=24).move_to(DOWN * 2.9)
        title = text(TITLE, size=64, weight="BOLD")
        with self.voiceover(text=N("s10.b3")) as tr:
            self.play(FadeIn(nn, shift=UP * 0.2), run_time=0.7)
            self.play(Indicate(nn.line(1), color=GOOD), run_time=1.0)
            wait_until(self, tr, "do")
            self.play(FadeOut(Group(*self.mobjects)), run_time=0.8)
            self.play(FadeIn(title), run_time=0.8)
            rest(self, tr)
        self.wait(1.0)
        self.play(FadeOut(title), run_time=0.8)


class Thumbnail(Scene):
    def construct(self):
        p = panel("mp", size=40)
        p.scale_to_fit_width(6.6).move_to(LEFT * 3.5)
        b = hbox(p.part(2, "fun f p => f p"), GOOD, buff=0.1)
        out = VGroup(b)
        words = VGroup(text("Proofs", size=110, weight="BOLD", color=PRIMARY), math("=", size=130),
                       text("Programs", size=110, weight="BOLD", color=SECONDARY)).arrange(DOWN, buff=0.3)
        words.scale(min(6.2 / words.height, 6.2 / words.width)).move_to(RIGHT * 3.6)
        self.add(p, out, words)
