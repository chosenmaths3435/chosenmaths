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
from mathvid.style import BAD, BG, FG, GOOD, MUTED, PRIMARY, SECONDARY, math, text
from mathvid.voice import get_speech_service

sys.path.insert(0, str(Path(__file__).parent))
from scenes import (  # noqa: E402
    C_ROUNDS,
    CANTOR_ROWS,
    M_ROWS,
    Blob,
    RealLine,
    c_dust,
    decimal_list,
    diagonal,
    frac_time,
    list_card,
    m_universe,
    ops_tag,
    run_diagonal,
    stmt_box,
    tick,
)

N = Script(__file__)

MID = (SAFE_TOP + SAFE_BOTTOM) / 2  # center of the safe area


def grid_slots(n, top, cols=6, step=1.05, dy=0.95, x0=None, size=22):
    x0 = -(cols - 1) * step / 2 if x0 is None else x0
    pos = [np.array([x0 + (i % cols) * step, top - (i // cols) * dy, 0.0]) for i in range(n)]
    labs = VGroup(*[text(str(i + 1), size=size, color=MUTED).move_to(p + UP * 0.32) for i, p in enumerate(pos)])
    return pos, labs


def checked(s, size=34):
    return VGroup(text(s, size=size), tick(size + 4)).arrange(RIGHT, buff=0.2)


# ---------------------------------------------------------------------------
# short1 Uncountable from the inside
# ---------------------------------------------------------------------------


class Short1Inside(VoiceoverScene):
    def construct(self):
        self.set_speech_service(get_speech_service())
        line = Line(LEFT * 3.4, RIGHT * 3.4, color=FG, stroke_width=5).move_to(UP * (MID + 0.3))
        lab = math(r"\mathbb{R}", size=60).next_to(line.get_right(), UP, 0.25).shift(LEFT * 0.2)
        big = text("uncountable", size=60, color=PRIMARY, weight="BOLD").move_to(UP * (MID + 2.2))
        u = Blob(radius=2.6, center=UP * (MID + 0.2), seed=1, n=30, gap=0.5, squash=1.35)
        ri = u.nearest(UP * (MID + 0.6) + RIGHT * 0.6)
        rdot = u.dots[ri]
        rdot.set_color(PRIMARY).scale(1.6)
        rlab = math(r"\mathbb{R}", size=36, color=PRIMARY).next_to(rdot, UP, 0.12)
        rtag = text("uncountable", size=24, color=PRIMARY).next_to(rdot, DOWN, 0.14)
        others = VGroup(*[d for i, d in enumerate(u.dots) if i != ri])
        with self.voiceover(text=N("short1.b1")) as tr:
            self.add(line, lab, big)
            self.wait(frac_time(tr, 0.15))
            wait_until(self, tr, "unless")
            self.play(ReplacementTransform(line, rdot), Transform(lab, rlab), Transform(big, rtag),
                      Create(u.border), LaggedStart(*[FadeIn(d, scale=0.5) for d in others], lag_ratio=0.03),
                      run_time=max(1.4, tr.get_remaining_duration()))

        dl = decimal_list(CANTOR_ROWS[:4], size=44, top=MID + 3.3, x0=-1.7, dy=0.8, dx=0.36)
        with self.voiceover(text=N("short1.b2")) as tr:
            self.play(FadeOut(VGroup(u.border, others, rdot, lab, big)), run_time=0.5)
            self.play(FadeIn(dl), run_time=0.6)
            drow = run_diagonal(self, dl, MID + 0.0, 0.8, 0.9)
            wait_until(self, tr, "diag")
            neqs = VGroup(*[math(r"\neq", size=40, color=BAD).next_to(r, RIGHT, 0.2) for r in dl.rows])
            for i, r in enumerate(dl.rows):
                r[2 + i].set_color(BAD)
            nope = text("not on the list", size=40, color=BAD).next_to(drow, DOWN, 0.5)
            self.play(FadeIn(neqs), FadeIn(nope), run_time=0.7)
            rest(self, tr)

        m = m_universe(radius=2.1, center=UP * (MID + 1.6), n=22, seed=13, squash=1.3)
        m.label.next_to(m.border, LEFT, 0.15).shift(UP * 1.5)
        with self.voiceover(text=N("short1.b3")) as tr:
            self.play(FadeOut(VGroup(dl, drow, neqs, nope)), run_time=0.5)
            self.play(Create(m.border), FadeIn(m.dots), FadeIn(m.r_lab), FadeIn(m.label), run_time=1.0)
            cant = checked("Cantor's theorem", size=32).next_to(m.border, DOWN, 0.4)
            self.wait(frac_time(tr, 0.2))
            self.play(FadeIn(cant), run_time=0.6)
            wait_until(self, tr, "list")
            pos, nums = grid_slots(18, MID - 1.9, cols=6)
            copies = VGroup(*[d.copy() for d in m.dots[:18]])
            self.play(FadeOut(cant), *[c.animate.move_to(p) for c, p in zip(copies, pos)], FadeIn(nums),
                      run_time=max(1.2, tr.get_remaining_duration()))
            more = math(r"\cdots", size=40, color=MUTED).next_to(pos[-1], RIGHT, 0.3)
            self.add(more)

        card = list_card(4, title="our list", size=34).move_to(UP * (MID - 2.4))
        inside = text("no list in M", size=36).move_to(m.border.get_center() + DOWN * 1.2)
        inside = VGroup(BackgroundRectangle(inside, color=BG, fill_opacity=0.9, buff=0.12), inside)
        with self.voiceover(text=N("short1.b4")) as tr:
            self.play(FadeOut(VGroup(copies, nums, more)), run_time=0.5)
            self.play(FadeIn(inside), run_time=0.6)
            self.wait(frac_time(tr, 0.2))
            self.play(FadeIn(card), run_time=0.6)
            wait_until(self, tr, "notin")
            home = card.get_center()
            hit = m.border.get_bottom()[1] - card.height / 2 - 0.05
            self.play(card.animate.move_to([home[0], hit, 0]), run_time=0.5, rate_func=rush_into)
            self.play(card.animate.move_to(home), m.border.animate.set_color(BAD), run_time=0.5, rate_func=rush_from)
            self.play(m.border.animate.set_color(SECONDARY), run_time=0.3)
            rest(self, tr)

        dl2 = decimal_list(M_ROWS[:4], size=44, top=MID + 3.3, x0=-1.7, dy=0.8, dx=0.36)
        hdr = text("our list of M's reals", size=32, color=SECONDARY).next_to(dl2, UP, 0.35)
        rl = RealLine(0, 1, 6.6, y=MID - 2.2, size=28)
        dust = VGroup(*[Dot(rl.p(v), radius=0.03, color=SECONDARY)
                        for v in sorted({p / q for q in range(1, 11) for p in range(1, q)})])
        with self.voiceover(text=N("short1.b5")) as tr:
            self.play(FadeOut(VGroup(m.border, m.dots, m.r_lab, m.label, inside, card)), run_time=0.5)
            self.play(FadeIn(dl2), FadeIn(hdr), FadeIn(rl), FadeIn(dust), run_time=0.7)
            t1 = max(0.6, tr.time_until_bookmark("new") - 1.0)
            drow = run_diagonal(self, dl2, MID - 0.3, t1, 0.8)
            d = float("0." + diagonal(M_ROWS[:4]))
            dd = Dot(rl.p(d), radius=0.11, color=PRIMARY)
            ddl = text("not in M", size=30, color=PRIMARY).next_to(dd, DOWN, 0.55)
            self.play(TransformFromCopy(drow[2], dd), FadeIn(ddl), run_time=0.9)
            self.wait(frac_time(tr, 0.1))
            self.play(dust.animate.set_opacity(0.15), run_time=max(0.8, tr.get_remaining_duration() - 0.2))
            rest(self, tr)

        word = text("uncountable", size=60, color=PRIMARY, weight="BOLD").move_to(UP * (MID + 1.0))
        w1 = text("no list in M", size=46, color=SECONDARY).move_to(UP * (MID + 1.4))
        w2 = text("no list at all", size=46, color=PRIMARY).move_to(UP * (MID - 0.2))
        with self.voiceover(text=N("short1.b6")) as tr:
            self.play(FadeOut(VGroup(dl2, hdr, drow, rl, dust, dd, ddl)), FadeIn(word), run_time=0.7)
            wait_until(self, tr, "where")
            self.play(ReplacementTransform(word.copy(), w1), ReplacementTransform(word, w2), run_time=1.0)
            rest(self, tr)
        self.wait(1.2)


# ---------------------------------------------------------------------------
# short2 A countable copy of the reals
# ---------------------------------------------------------------------------


class Short2Copy(VoiceoverScene):
    def construct(self):
        self.set_speech_service(get_speech_service())
        rl = RealLine(-3.5, 3.5, 7.2, y=MID, size=28)
        ops = ops_tag().move_to(UP * (MID + 2.6))
        solid = Line(rl.p(-3.5), rl.p(3.5), color=FG, stroke_width=10)
        dust = c_dust(rl)
        with self.voiceover(text=N("short2.b1")) as tr:
            self.add(solid, rl.ticks, rl.labels, ops)
            wait_until(self, tr, "away")
            self.play(FadeOut(solid), FadeIn(rl.line), FadeIn(dust), run_time=max(1.0, tr.get_remaining_duration()))
        self.play(FadeOut(VGroup(*dust[1:])), rl.line.animate.set_stroke(opacity=0.35), run_time=0.6)

        r1 = VGroup(*[Dot(rl.p(v), radius=0.075, color=PRIMARY) for v in C_ROUNDS[1][:2]])
        stmts = [r"\exists y\,(y+1=0)", r"\exists y\,(y\cdot y=1+1)"]
        labs = [r"-1", r"\sqrt{2}"]
        cur = None
        lm = VGroup()
        with self.voiceover(text=N("short2.b2")) as tr:
            box = stmt_box(r"\exists y\,\big(\;\cdots\;\big)", size=46).move_to(UP * (MID + 2.6))
            self.play(ReplacementTransform(ops, box), run_time=0.8)
            cur = box
            slot = Square(0.45, color=PRIMARY, stroke_width=3)
            slot_g = VGroup(math("y=", size=40, color=PRIMARY), slot).arrange(RIGHT, buff=0.1).next_to(box, DOWN, 0.35)
            pop = Dot(slot.get_center(), radius=0.1, color=PRIMARY)
            self.wait(frac_time(tr, 0.35))
            self.play(FadeIn(slot_g), run_time=0.6)
            self.wait(frac_time(tr, 0.12))
            self.play(FadeIn(pop, scale=3), run_time=0.5)
            wait_until(self, tr, "drops")
            self.play(FadeOut(VGroup(slot_g, pop)), run_time=0.3)
            t = max(0.5, tr.get_remaining_duration() / 2 - 0.1)
            for k in range(2):
                nb = stmt_box(stmts[k], size=46).move_to(UP * (MID + 2.6))
                d = r1[k]
                tgt = d.get_center()
                d.move_to(nb.get_bottom() + DOWN * 0.3)
                l = math(labs[k], size=34, color=PRIMARY).next_to(tgt, UP, 0.25)
                self.play(ReplacementTransform(cur, nb), FadeIn(d), run_time=t * 0.4)
                self.play(d.animate.move_to(tgt), FadeIn(l), run_time=t * 0.6)
                cur = nb
                lm.add(l)
            rest(self, tr)

        rnd_dust = c_dust(rl, color_rounds=True)
        with self.voiceover(text=N("short2.b3")) as tr:
            self.play(FadeOut(cur), FadeOut(lm), run_time=0.5)
            wait_until(self, tr, "rounds")
            n_r = len(C_ROUNDS) - 2
            t = max(0.4, (tr.duration * 0.5) / n_r)
            for k in range(2, len(C_ROUNDS)):
                self.play(LaggedStart(*[FadeIn(d, scale=2.5) for d in rnd_dust[k]], lag_ratio=0.03), run_time=t)
            pos, nums = grid_slots(18, MID - 1.4, cols=6)
            all_dots = list(dust[0]) + list(r1) + [d for g in rnd_dust[2:] for d in g]
            copies = VGroup(*[d.copy().set_color(FG) for d in all_dots[:18]])
            clab = math("C", size=60, color=PRIMARY).next_to(rl.line.get_left(), UP, 0.35)
            more = math(r"\cdots", size=40, color=MUTED).next_to(pos[-1], RIGHT, 0.3)
            self.play(*[c.animate.move_to(p) for c, p in zip(copies, pos)], FadeIn(nums), FadeIn(more), Write(clab),
                      run_time=max(1.0, tr.get_remaining_duration() - 0.2))
            rest(self, tr)

        fact = math(r"1+1>1", size=56).move_to(UP * (MID + 2.6))
        tick_r = VGroup(text("true in", size=32), math(r"\mathbb{R}", size=38), tick(36)).arrange(RIGHT, buff=0.15)
        tick_c = VGroup(text("true in", size=32), math("C", size=38, color=PRIMARY), tick(36)).arrange(RIGHT, buff=0.15)
        ticks = VGroup(tick_r, tick_c).arrange(RIGHT, buff=0.6).next_to(fact, DOWN, 0.35)
        logic = math(r"\land\qquad\lnot", size=56).move_to(fact)
        ex = stmt_box(r"\exists y\,\big(\;\cdots\;\big)", size=46).move_to(UP * (MID + 2.6))
        w = Dot(rl.p(1.25), radius=0.12, color=PRIMARY)
        wl = text("in C", size=30, color=PRIMARY).next_to(w, DOWN, 0.55)
        with self.voiceover(text=N("short2.b4")) as tr:
            self.play(FadeOut(VGroup(copies, nums, more)), FadeIn(fact), run_time=0.6)
            self.play(FadeIn(ticks), run_time=0.6)
            self.wait(frac_time(tr, 0.15))
            self.play(FadeOut(fact), FadeIn(logic), run_time=0.6)
            self.wait(frac_time(tr, 0.1))
            self.play(FadeOut(logic), FadeOut(ticks), FadeIn(ex), run_time=0.6)
            wait_until(self, tr, "witness")
            self.play(FadeIn(w, scale=2.5), FadeIn(wl), run_time=0.7)
            rest(self, tr)

        c1 = VGroup(text("every positive number", size=34), text("has a square root", size=34)).arrange(DOWN, buff=0.1)
        c2 = VGroup(text("a number between any", size=34), text("two different numbers", size=34)).arrange(DOWN, buff=0.1)
        c1 = VGroup(c1, tick(42)).arrange(RIGHT, buff=0.3)
        c2 = VGroup(c2, tick(42)).arrange(RIGHT, buff=0.3)
        claims = VGroup(c1, c2).arrange(DOWN, buff=0.45).move_to(UP * (MID + 3.1))
        ls = text("Löwenheim-Skolem theorem", size=42, color=PRIMARY, weight="BOLD").move_to(UP * (MID - 2.3))
        with self.voiceover(text=N("short2.b5")) as tr:
            self.play(FadeOut(VGroup(ex, w, wl)), run_time=0.5)
            self.play(FadeIn(c1), run_time=0.6)
            self.play(FadeIn(c2), run_time=0.6)
            wait_until(self, tr, "ls")
            self.play(FadeIn(ls, shift=UP * 0.2), run_time=0.8)
            rest(self, tr)
        self.wait(1.5)
