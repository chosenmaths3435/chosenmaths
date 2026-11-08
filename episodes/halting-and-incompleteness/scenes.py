import numpy as np
from manim import *
from manim_voiceover import VoiceoverScene

from mathvid import layout  # noqa: F401  must come before scene code runs
from mathvid.anim import rest, rt, wait_until
from mathvid.layout import FH, FW
from mathvid.script import Script
from mathvid.style import (BAD, BG, FG, GOOD, MUTED, PRIMARY, SECONDARY, TERTIARY, math, text,
                           title_card)
from mathvid.voice import get_speech_service

N = Script(__file__)

TITLE = "The same theorem, twice"
GODEL = "G\u00f6del"
HALT_C = GOOD  # "halts"
LOOP_C = SECONDARY  # "loops"


def frac_time(tr, f):
    return rt(tr.duration * f)


# ---------------------------------------------------------------------------
# Shared builders (also used by shorts.py)
# ---------------------------------------------------------------------------


def tick(size=44):
    return math(r"\checkmark", size=size, color=GOOD)


def loop_icon(size=44, color=LOOP_C):
    return math(r"\circlearrowright", size=size * 1.5, color=color)


def halt_icon(v, size=44):
    return tick(size) if v else loop_icon(size)


def stop_icon(size=0.45, color=HALT_C):
    o = RegularPolygon(n=8, color=color, stroke_width=3).set_fill(color, 1).scale(size)
    o.rotate(PI / 8)
    return o


def xout(mob, color=BAD, pad=0.12, width=7):
    ul, dr = mob.get_corner(UL) + np.array([-pad, pad, 0]), mob.get_corner(DR) + np.array([pad, -pad, 0])
    ur, dl = mob.get_corner(UR) + np.array([pad, pad, 0]), mob.get_corner(DL) + np.array([-pad, -pad, 0])
    return VGroup(Line(ul, dr, color=color, stroke_width=width), Line(ur, dl, color=color, stroke_width=width))


def mbox(label, color=FG, w=2.0, h=1.3, size=52, tex=True):
    box = RoundedRectangle(corner_radius=0.18, width=w, height=h, color=color, stroke_width=4)
    lab = (math(label, size=size, color=color) if tex else text(label, size=size, color=color)).move_to(box)
    g = VGroup(box, lab)
    g.box, g.lab = box, lab
    return g


def tag(s, size=30, color=MUTED, **kw):
    return text(s, size=size, color=color, **kw)


def card(lines, size=32, color=FG, box_color=MUTED, buff=0.25, pad=0.4):
    body = VGroup(*[text(l, size=size, color=color) for l in lines]).arrange(DOWN, buff=buff)
    box = SurroundingRectangle(body, buff=pad, corner_radius=0.18, color=box_color, stroke_width=3)
    g = VGroup(box, body)
    g.box, g.body = box, body
    return g


class Tape(VGroup):
    """A strip of cells. Optional head (a triangle with a state label) over one cell."""

    def __init__(self, symbols, cell=0.72, size=36, head=None, state="q_0"):
        super().__init__()
        self.cell, self.size = cell, size
        self.cells = VGroup(*[Square(cell, color=MUTED, stroke_width=3) for _ in symbols]).arrange(RIGHT, buff=0)
        self.syms = VGroup(*[self.sym(s).move_to(c) for s, c in zip(symbols, self.cells)])
        self.add(self.cells, self.syms)
        self.head = None
        if head is not None:
            tri = Triangle(color=PRIMARY, stroke_width=0).set_fill(PRIMARY, 1).scale(0.16).rotate(PI)
            tri.next_to(self.cells[head], UP, 0.08)
            lab = math(state, size=30, color=PRIMARY).next_to(tri, UP, 0.08)
            self.head = VGroup(tri, lab)
            self.head_i = head
            self.add(self.head)

    def sym(self, s):
        if s == "_":
            return math(r"\sqcup", size=self.size, color=MUTED)
        return math(s, size=self.size)

    def write(self, i, s):
        return Transform(self.syms[i], self.sym(s).move_to(self.cells[i]))

    def move(self, d):
        self.head_i += d
        return self.head.animate.shift(RIGHT * self.cell * d)

    def state(self, s):
        return Transform(self.head[1], math(s, size=30, color=PRIMARY).move_to(self.head[1]))


RULES = [r"q_0,\ 1 \to 0,\ R,\ q_1", r"q_1,\ 1 \to 1,\ R,\ q_1", r"q_1,\ \sqcup \to 1,\ L,\ q_2"]


def rule_table(size=34):
    rows = VGroup(*[math(r, size=size) for r in RULES]).arrange(DOWN, buff=0.25, aligned_edge=LEFT)
    head = tag("rules", size=26)
    inner = VGroup(head, rows).arrange(DOWN, buff=0.2)
    box = SurroundingRectangle(inner, buff=0.3, corner_radius=0.15, color=MUTED, stroke_width=3)
    g = VGroup(box, inner)
    g.rows, g.box = rows, box
    return g


def rule_string(size=30):
    return math(r"q_0,1,0,R,q_1;\,q_1,1,1,R,q_1;\,q_1,\sqcup,1,L,q_2", size=size, color=PRIMARY)


def laptop(scale=1.0):
    screen = RoundedRectangle(corner_radius=0.08, width=2.2, height=1.4, color=MUTED, stroke_width=3)
    base = Polygon(screen.get_corner(DL) + LEFT * 0.25 + DOWN * 0.25, screen.get_corner(DR) + RIGHT * 0.25 + DOWN * 0.25,
                   screen.get_corner(DR), screen.get_corner(DL), color=MUTED, stroke_width=3)
    return VGroup(screen, base).scale(scale)


# The halting table: 1 = halts, 0 = loops. Row i is machine M_i, column j is input <M_j>.
GRID = [[1, 0, 1, 1, 0], [0, 0, 1, 0, 1], [1, 1, 1, 0, 0], [0, 1, 0, 0, 1], [1, 0, 0, 1, 1]]


class HaltGrid(VGroup):
    def __init__(self, cell=0.82, size=40, lab_size=32):
        super().__init__()
        n = len(GRID)
        self.cell = cell
        self.sq = [[Square(cell, color=MUTED, stroke_width=2).move_to(np.array([j * cell, -i * cell, 0]))
                    for j in range(n)] for i in range(n)]
        self.icons = [[halt_icon(GRID[i][j], size).move_to(self.sq[i][j]) for j in range(n)] for i in range(n)]
        self.rlabs = VGroup(*[math(f"M_{i + 1}", size=lab_size, color=FG).next_to(self.sq[i][0], LEFT, 0.25)
                              for i in range(n)])
        self.clabs = VGroup(*[math(rf"\langle M_{j + 1}\rangle", size=lab_size - 4, color=MUTED)
                              .next_to(self.sq[0][j], UP, 0.2) for j in range(n)])
        self.vd = math(r"\vdots", size=lab_size, color=MUTED).next_to(self.sq[n - 1][0], DOWN, 0.2)
        self.hd = math(r"\cdots", size=lab_size, color=MUTED).next_to(self.sq[0][n - 1], RIGHT, 0.2)
        self.add(*[s for r in self.sq for s in r], *[c for r in self.icons for c in r], self.rlabs, self.clabs,
                 self.vd, self.hd)

    def diag(self):
        return VGroup(*[self.icons[i][i] for i in range(len(GRID))])


def flipped_row(grid, size=40):
    """D's row: the flipped diagonal, under the grid."""
    n = len(GRID)
    y = grid.sq[n - 1][0].get_center()[1] - grid.cell * 1.55
    sq = VGroup(*[Square(grid.cell, color=PRIMARY, stroke_width=3).move_to(np.array([grid.sq[0][j].get_center()[0], y, 0]))
                  for j in range(n)])
    icons = VGroup(*[halt_icon(1 - GRID[j][j], size).move_to(sq[j]) for j in range(n)])
    lab = math("D", size=36, color=PRIMARY).next_to(sq[0], LEFT, 0.25)
    g = VGroup(sq, icons, lab)
    g.sq, g.icons, g.lab = sq, icons, lab
    return g


PROOF = [(r"\forall x\ \neg(S(x)=0)", "axiom"), (r"\forall x\ (x+0=x)", "axiom"),
         (r"\neg(S(0)=0)", "rule, from 1"), (r"S(0)+0=S(0)", "rule, from 2"),
         (r"\neg(S(0)+0=0)", "rule, from 3 and 4")]


def proof_card(size=34, dy=0.72, tags=True):
    rows = VGroup()
    for i, (f, t) in enumerate(PROOF):
        y = -i * dy
        num = text(f"{i + 1}.", size=size - 4, color=MUTED).move_to(np.array([0, y, 0]), aligned_edge=LEFT)
        fm = math(f, size=size)
        fm.move_to(np.array([0.6, y, 0]), aligned_edge=LEFT)
        row = VGroup(num, fm)
        if tags:
            tg = text(t, size=size - 10, color=MUTED)
            tg.move_to(np.array([5.0, y, 0]), aligned_edge=LEFT)
            row.add(tg)
        rows.add(row)
    return rows


SYMS = [(r"\forall", "1"), (r"\neg", "2"), ("=", "3"), ("S", "4"), ("x", "5"), ("(", "6"), (")", "7"), ("0", "8")]
SENT = r"\forall x\ \neg\,(S(x)=0)"
SENT_CODE = "1\\,5\\,2\\,6\\,4\\,6\\,5\\,7\\,3\\,8\\,7"
PROOF_CODE = r"15264657387\,0\,15659836587\,0\,264685387\,0\,\cdots"


def fork(size=34):
    q = text("What problems can we solve?", size=44, t2c={"problems": PRIMARY, "solve": PRIMARY})
    q.move_to(UP * 2.7)
    left = VGroup(text("problem = string", size=size), text("solve = machine", size=size),
                  text("the halting problem", size=size + 2, color=PRIMARY, weight="BOLD")).arrange(DOWN, buff=0.3)
    right = VGroup(text("problem = sentence", size=size), text("solve = proof", size=size),
                   text("incompleteness", size=size + 2, color=PRIMARY, weight="BOLD")).arrange(DOWN, buff=0.3)
    left.move_to(LEFT * 3.6 + DOWN * 0.9)
    right.move_to(RIGHT * 3.6 + DOWN * 0.9)
    j = q.get_bottom() + DOWN * 0.25
    ll = Line(j, left.get_top() + UP * 0.25, color=MUTED, stroke_width=4)
    rl = Line(j, right.get_top() + UP * 0.25, color=MUTED, stroke_width=4)
    g = VGroup(q, ll, rl, left, right)
    g.q, g.ll, g.rl, g.left, g.right = q, ll, rl, left, right
    return g


def fork_icon(lit=None):
    root = Dot(radius=0.06, color=FG)
    a = Dot(LEFT * 0.55 + DOWN * 0.55, radius=0.06, color=FG)
    b = Dot(RIGHT * 0.55 + DOWN * 0.55, radius=0.06, color=FG)
    la = Line(root.get_center(), a.get_center(), color=MUTED, stroke_width=3)
    lb = Line(root.get_center(), b.get_center(), color=MUTED, stroke_width=3)
    ta = text("machines", size=20, color=MUTED).next_to(a, DOWN, 0.1)
    tb = text("proofs", size=20, color=MUTED).next_to(b, DOWN, 0.1)
    g = VGroup(la, lb, root, a, b, ta, tb)
    for side, (l, d, t) in (("left", (la, a, ta)), ("right", (lb, b, tb))):
        if lit == side:
            l.set_color(PRIMARY)
            d.set_color(PRIMARY)
            t.set_color(PRIMARY)
    return g.to_corner(UL, buff=0.45)


def dream_box(size=30):
    head = text("Hilbert's dream", size=34, color=PRIMARY, weight="BOLD")
    box = RoundedRectangle(corner_radius=0.2, width=4.6, height=1.3, color=PRIMARY, stroke_width=4)
    head.move_to(box)
    tags = VGroup(text("settles every sentence", size=size), text("never proves anything false", size=size),
                  text("a machine can check the proofs", size=size)).arrange(DOWN, buff=0.18, aligned_edge=LEFT)
    tags.next_to(box, DOWN, 0.35)
    g = VGroup(box, head, tags)
    g.box, g.head, g.tags = box, head, tags
    return g


def g_box(s="G has no proof in this system.", size=36, label="G", color=PRIMARY):
    body = text(s, size=size)
    box = SurroundingRectangle(body, buff=0.35, corner_radius=0.18, color=color, stroke_width=4)
    lab = math(label, size=48, color=color).next_to(box, LEFT, 0.3)
    arc = CurvedArrow(body.get_top() + UP * 0.35 + LEFT * 0.4, lab.get_top() + UP * 0.1, angle=PI / 3,
                      color=color, stroke_width=3, tip_length=0.18)
    g = VGroup(box, body, lab, arc)
    g.box, g.body, g.lab, g.arc = box, body, lab, arc
    return g


def corner_title(s):
    return text(s, size=30, color=MUTED).to_corner(UR, buff=0.45)


# ---------------------------------------------------------------------------
# s01 Hook
# ---------------------------------------------------------------------------


class S01Hook(VoiceoverScene):
    def construct(self):
        self.set_speech_service(get_speech_service())
        place = text("K\u00f6nigsberg, September 1930", size=36, color=MUTED).move_to(UP * 3.0)
        de = text("Wir m\u00fcssen wissen. Wir werden wissen.", size=54, color=PRIMARY, weight="BOLD").move_to(UP * 0.9)
        en = text("We must know. We will know.", size=40).next_to(de, DOWN, 0.4)
        who = text("David Hilbert", size=30, color=MUTED).next_to(en, DOWN, 0.35)
        who0 = text("David Hilbert", size=48).move_to(UP * 0.6)
        with self.voiceover(text=N("s01.b1")) as tr:
            self.play(FadeIn(place, shift=DOWN * 0.2), run_time=0.8)
            self.wait(frac_time(tr, 0.08))
            self.play(FadeIn(who0), run_time=0.7)
            wait_until(self, tr, "six")
            self.play(FadeIn(de, shift=UP * 0.2), ReplacementTransform(who0, who), run_time=0.9)
            self.play(FadeIn(en), run_time=0.8)
            rest(self, tr)

        quote = VGroup(de, en, who)
        qs = VGroup(*[text("?", size=60, color=FG) for _ in range(6)]).arrange(RIGHT, buff=0.9).move_to(DOWN * 0.6)
        cal = VGroup(RoundedRectangle(corner_radius=0.1, width=1.6, height=1.5, color=MUTED, stroke_width=3))
        day8 = VGroup(text("Sept", size=24, color=MUTED), text("8", size=48)).arrange(DOWN, buff=0.08)
        day7 = VGroup(text("Sept", size=24, color=MUTED), text("7", size=48, color=PRIMARY)).arrange(DOWN, buff=0.08)
        cal.move_to(DOWN * 2.6 + LEFT * 1.3)
        day8.move_to(cal)
        day7.move_to(cal)
        kg = text(f"Kurt {GODEL}, 24", size=34, color=PRIMARY).next_to(cal, RIGHT, 0.5)
        with self.voiceover(text=N("s01.b2")) as tr:
            self.play(FadeOut(place), quote.animate.scale(0.62).move_to(UP * 2.7), run_time=0.8)
            self.play(LaggedStart(*[FadeIn(q, shift=DOWN * 0.2) for q in qs], lag_ratio=0.15), run_time=1.0)
            t_each = max(0.25, (tr.time_until_bookmark("before") - 0.2) / 5)
            for q in qs[:5]:
                self.play(Transform(q, tick(64).move_to(q)), run_time=min(0.6, t_each))
                if t_each > 0.65:
                    self.wait(t_each - 0.6)
            wait_until(self, tr, "before")
            self.play(FadeIn(cal), FadeIn(day8), run_time=0.5)
            self.play(FadeOut(day8, shift=UP * 0.3), FadeIn(day7, shift=UP * 0.3), run_time=0.6)
            self.play(FadeIn(kg, shift=LEFT * 0.2), qs[5].animate.set_color(PRIMARY).scale(1.3), run_time=0.8)
            rest(self, tr)
        self.play(FadeOut(VGroup(quote, qs, cal, day7, kg)), run_time=0.6)

        tape = Tape(list("_1011_"), cell=0.62, size=32, head=2).move_to(RIGHT * 3.6 + DOWN * 0.1)
        tlab = text("Turing, 1936", size=34, color=SECONDARY).next_to(tape, DOWN, 0.5)
        pc = proof_card(size=26, dy=0.55, tags=False).move_to(LEFT * 3.6 + DOWN * 0.1)
        plab = text(f"{GODEL}, 1930", size=34, color=SECONDARY).next_to(pc, DOWN, 0.5)
        tlab.match_y(plab)
        with self.voiceover(text=N("s01.b3")) as tr:
            self.play(FadeIn(pc, shift=RIGHT * 0.3), FadeIn(plab), run_time=1.0)
            wait_until(self, tr, "machines")
            self.play(FadeIn(tape, shift=LEFT * 1.0), FadeIn(tlab), run_time=1.0)
            self.wait(frac_time(tr, 0.1))
            self.play(Indicate(pc, color=PRIMARY, scale_factor=1.05), run_time=0.8)
            self.play(Indicate(tape, color=PRIMARY, scale_factor=1.05), run_time=0.8)
            rest(self, tr)

        left = VGroup(pc, plab)
        right = VGroup(tape, tlab)
        with self.voiceover(text=N("s01.b4")) as tr:
            self.wait(frac_time(tr, 0.3))
            wait_until(self, tr, "same")
            eq = math("=", size=96, color=PRIMARY).move_to(DOWN * 0.1)
            self.play(left.animate.move_to(LEFT * 2.9 + DOWN * 0.1), right.animate.move_to(RIGHT * 3.1 + DOWN * 0.1),
                      run_time=0.8)
            self.play(FadeIn(eq, scale=1.4), run_time=max(0.5, tr.get_remaining_duration()))
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.5)
        title_card(self, TITLE)


# ---------------------------------------------------------------------------
# s02 The question
# ---------------------------------------------------------------------------


class S02Question(VoiceoverScene):
    def construct(self):
        self.set_speech_service(get_speech_service())
        lg = text("logic: proofs", size=44).move_to(LEFT * 3.3)
        cs = text("computer science: programs", size=44).move_to(RIGHT * 3.0)
        head = text("reasoning about reasoning", size=50, color=PRIMARY, weight="BOLD").move_to(UP * 1.4)
        with self.voiceover(text=N("s02.b1")) as tr:
            self.play(FadeIn(lg, shift=RIGHT * 0.2), run_time=0.7)
            self.play(FadeIn(cs, shift=LEFT * 0.2), run_time=0.7)
            wait_until(self, tr, "reason")
            self.play(FadeIn(head, shift=DOWN * 0.2), lg.animate.scale(0.8).move_to(LEFT * 2.8 + DOWN * 0.2),
                      cs.animate.scale(0.8).move_to(RIGHT * 2.6 + DOWN * 0.2), run_time=1.0)
            rest(self, tr)

        f = fork()
        plain = text("What problems can we solve?", size=56).move_to(UP * 0.3)
        lit = text("What problems can we solve?", size=56, t2c={"problems": PRIMARY, "solve": PRIMARY}).move_to(plain)
        with self.voiceover(text=N("s02.b2")) as tr:
            self.play(FadeOut(VGroup(head, lg, cs)), run_time=0.5)
            self.play(FadeIn(plain, shift=UP * 0.2), run_time=0.8)
            wait_until(self, tr, "two")
            self.play(Transform(plain, lit), run_time=0.8)
            self.play(Indicate(plain, color=PRIMARY, scale_factor=1.04), run_time=0.8)
            rest(self, tr)

        with self.voiceover(text=N("s02.b3")) as tr:
            self.play(Transform(plain, f.q), run_time=0.8)
            self.play(Create(f.ll), Create(f.rl), run_time=0.6)
            wait_until(self, tr, "machine")
            self.play(LaggedStart(*[FadeIn(m, shift=DOWN * 0.15) for m in f.left], lag_ratio=0.35), run_time=1.4)
            wait_until(self, tr, "proof")
            self.play(LaggedStart(*[FadeIn(m, shift=DOWN * 0.15) for m in f.right], lag_ratio=0.35), run_time=1.4)
            rest(self, tr)

        with self.voiceover(text=N("s02.b4")) as tr:
            self.play(f.ll.animate.set_color(PRIMARY), f.left[:2].animate.set_color(PRIMARY),
                      f.right.animate.set_opacity(0.4), f.rl.animate.set_opacity(0.4), run_time=0.8)
            rest(self, tr)
        self.remove(plain)
        self.add(f.q)
        f.left[:2].set_color(PRIMARY)
        self.play(ReplacementTransform(VGroup(f.q, f.ll, f.rl, f.left, f.right), fork_icon("left")), run_time=0.9)
        self.wait(0.2)


# ---------------------------------------------------------------------------
# s03 Problems as strings
# ---------------------------------------------------------------------------


def bin_strings():
    yes = ["10", "11", "101", "111", "1011", "1101"]
    no = ["100", "110", "1001"]
    return yes, no


class S03Strings(VoiceoverScene):
    def construct(self):
        self.set_speech_service(get_speech_service())
        icon = fork_icon("left")
        self.add(icon)
        q = text("is n prime?", size=50).move_to(UP * 2.5)
        seven = math("7", size=96).move_to(UP * 0.4)
        s7 = Tape(list("111"), cell=0.9, size=52).move_to(UP * 0.4)
        with self.voiceover(text=N("s03.b1")) as tr:
            self.play(FadeIn(q, shift=DOWN * 0.2), run_time=0.8)
            self.wait(frac_time(tr, 0.15))
            self.play(FadeIn(seven), run_time=0.6)
            wait_until(self, tr, "binary")
            self.play(ReplacementTransform(seven, s7), run_time=0.9)
            rest(self, tr)

        yes, no = bin_strings()
        bin_box = RoundedRectangle(corner_radius=0.2, width=7.6, height=2.0, color=GOOD, stroke_width=4).move_to(DOWN * 1.9)
        bin_lab = text("yes", size=34, color=GOOD).next_to(bin_box, LEFT, 0.3)
        slots = [bin_box.get_center() + np.array([-2.9 + 1.16 * k, 0, 0]) for k in range(6)]
        ylabs = VGroup(*[math(s, size=40) for s in yes])
        nlabs = VGroup(*[math(s, size=40, color=BAD) for s in no])
        prob = tag("a problem = a set of strings", size=34, color=PRIMARY).move_to(UP * 2.5)
        with self.voiceover(text=N("s03.b2")) as tr:
            self.play(s7.animate.scale(0.7).move_to(UP * 0.9), Create(bin_box), FadeIn(bin_lab), run_time=0.8)
            wait_until(self, tr, "yes")
            step = max(0.35, (tr.get_remaining_duration() - 2.4) / 9)
            order = [("y", 0), ("y", 1), ("n", 0), ("y", 2), ("n", 1), ("y", 3), ("n", 2), ("y", 4), ("y", 5)]
            for kind, i in order:
                if kind == "y":
                    m = ylabs[i].move_to(UP * 0.9 + RIGHT * 4.5)
                    self.play(FadeIn(m), m.animate.move_to(slots[i]), run_time=step)
                else:
                    m = nlabs[i].move_to(UP * 0.9 + RIGHT * 4.5)
                    self.play(FadeIn(m), run_time=step * 0.4)
                    self.play(m.animate.shift(DOWN * 0.6 + LEFT * 1.0).set_opacity(0), run_time=step * 0.6)
            self.play(ReplacementTransform(q, prob), run_time=0.7)
            rest(self, tr)
        self.play(FadeOut(VGroup(s7, bin_box, bin_lab, ylabs, prob)), *[FadeOut(n) for n in nlabs], run_time=0.5)

        tape = Tape(list("_1011__"), cell=0.85, size=42, head=1).move_to(UP * 1.2)
        rt_ = rule_table(size=34).move_to(DOWN * 1.9)
        with self.voiceover(text=N("s03.b3")) as tr:
            self.play(FadeIn(tape.cells), FadeIn(tape.syms), run_time=0.8)
            self.play(FadeIn(tape.head, shift=DOWN * 0.2), run_time=0.6)
            self.play(FadeIn(rt_), run_time=0.8)
            wait_until(self, tr, "rule")
            hl = SurroundingRectangle(rt_.rows[0], color=PRIMARY, buff=0.08, stroke_width=3)
            self.play(Create(hl), run_time=0.5)
            self.play(tape.write(1, "0"), run_time=0.6)
            self.play(tape.move(1), run_time=0.6)
            self.play(tape.state("q_1"), run_time=0.5)
            rest(self, tr)

        lap = laptop(1.2).move_to(RIGHT * 4.6 + DOWN * 0.2)
        mach = VGroup(tape, rt_, hl)
        eq = math("=", size=72, color=MUTED)
        with self.voiceover(text=N("s03.b4")) as tr:
            self.play(Transform(hl, SurroundingRectangle(rt_.rows[1], color=PRIMARY, buff=0.08, stroke_width=3)),
                      run_time=0.3)
            for _ in range(2):
                self.play(tape.move(1), run_time=0.35)
            self.play(Transform(hl, SurroundingRectangle(rt_.rows[2], color=PRIMARY, buff=0.08, stroke_width=3)),
                      run_time=0.3)
            self.play(tape.write(4, "1"), run_time=0.35)
            self.play(tape.move(-1), tape.state("q_2"), run_time=0.35)
            self.play(mach.animate.scale(0.62).move_to(LEFT * 2.6 + DOWN * 0.2), run_time=0.8)
            eq.move_to((mach.get_right() + lap.get_left()) / 2)
            self.play(FadeIn(lap), FadeIn(eq), run_time=0.7)
            wait_until(self, tr, "method")
            wide = DashedVMobject(SurroundingRectangle(VGroup(mach, lap), buff=0.45, corner_radius=0.2, color=PRIMARY),
                                  num_dashes=70)
            wl = text("any step-by-step method ?", size=34, color=PRIMARY).next_to(wide, UP, 0.2)
            self.play(Create(wide), FadeIn(wl), run_time=1.0)
            rest(self, tr)
        self.play(FadeOut(VGroup(mach, lap, eq, wide, wl)), run_time=0.5)

        m = mbox("M", w=2.4, h=1.6).move_to(ORIGIN)
        every = tag("solve = always stop, always right", size=36, color=PRIMARY).move_to(UP * 2.6)
        inputs = [("111", True), ("100", False), ("1011", True), ("1001", False)]
        with self.voiceover(text=N("s03.b5")) as tr:
            self.play(FadeIn(m), run_time=0.6)
            wait_until(self, tr, "every")
            self.play(FadeIn(every), run_time=0.6)
            step = max(0.5, (tr.get_remaining_duration() - 0.3) / len(inputs))
            for s, ok in inputs:
                w = math(s, size=40).move_to(LEFT * 5)
                light = text("yes" if ok else "no", size=40, color=GOOD if ok else BAD).move_to(RIGHT * 3.4)
                self.play(FadeIn(w), w.animate.move_to(m.get_left() + LEFT * 0.6), run_time=step * 0.35)
                self.play(FadeOut(w, scale=0.5), Indicate(m.box, color=PRIMARY), run_time=step * 0.25)
                self.play(FadeIn(light, shift=RIGHT * 0.2), run_time=step * 0.2)
                self.play(FadeOut(light), run_time=step * 0.2)
            rest(self, tr)
        self.play(FadeOut(VGroup(m, every)), run_time=0.4)

        rt2 = rule_table(size=34).move_to(LEFT * 3.5 + UP * 1.2)
        m1 = mbox("M", w=2.0, h=1.4).next_to(rt2, DOWN, 0.4)
        rs = rule_string(size=44).move_to(UP * 1.2)
        m2 = mbox("M'", w=2.4, h=1.6, color=SECONDARY).move_to(RIGHT * 0.5 + DOWN * 1.9)
        slot = Tape(["\\cdots"] * 1 + ["_"] * 6, cell=0.6, size=26).next_to(m2, LEFT, 0.0).shift(LEFT * 0.0)
        slot.next_to(m2, UP, 0.35)
        with self.voiceover(text=N("s03.b6")) as tr:
            self.play(FadeIn(rt2), FadeIn(m1), run_time=0.8)
            self.wait(frac_time(tr, 0.2))
            self.play(ReplacementTransform(rt2, rs), FadeOut(m1), run_time=1.0)
            wait_until(self, tr, "input")
            self.play(FadeIn(m2), FadeIn(slot), run_time=0.6)
            self.play(rs.animate.next_to(m2, UP, 0.45), FadeOut(slot), run_time=1.0)
            self.play(Indicate(m2.box, color=SECONDARY), run_time=0.6)
            rest(self, tr)
        self.play(FadeOut(VGroup(rs, m2, icon)), run_time=0.5)


# ---------------------------------------------------------------------------
# s04 The halting problem
# ---------------------------------------------------------------------------


def h_box(scale=1.0):
    return mbox("H", color=PRIMARY, w=2.0, h=1.4).scale(scale)


def d_machine(scale=1.0):
    """D with H inside, the copy step, and the switch. Returns a group with named parts."""
    d = RoundedRectangle(corner_radius=0.25, width=9.6, height=4.4, color=SECONDARY, stroke_width=4)
    dl = math("D", size=56, color=SECONDARY).next_to(d, UP, 0.15).align_to(d, LEFT).shift(RIGHT * 0.3)
    h = h_box().move_to(d.get_center() + LEFT * 1.0)
    sw_h = text('"halts"', size=30, color=HALT_C).move_to(d.get_center() + RIGHT * 2.0 + UP * 1.0)
    sw_l = text('"loops"', size=30, color=LOOP_C).move_to(d.get_center() + RIGHT * 2.0 + DOWN * 1.0)
    a_h = Arrow(h.get_right(), sw_h.get_left(), buff=0.15, color=MUTED, stroke_width=3)
    a_l = Arrow(h.get_right(), sw_l.get_left(), buff=0.15, color=MUTED, stroke_width=3)
    loop = loop_icon(64, color=LOOP_C).next_to(sw_h, RIGHT, 0.6)
    stop = stop_icon(0.32).next_to(sw_l, RIGHT, 0.75)
    ah2 = Arrow(sw_h.get_right(), loop.get_left(), buff=0.1, color=MUTED, stroke_width=3)
    al2 = Arrow(sw_l.get_right(), stop.get_left(), buff=0.1, color=MUTED, stroke_width=3)
    g = VGroup(d, dl, h, a_h, a_l, sw_h, sw_l, ah2, al2, loop, stop)
    g.d, g.dl, g.h, g.sw = d, dl, h, VGroup(a_h, a_l, sw_h, sw_l, ah2, al2, loop, stop)
    g.sw_h, g.sw_l, g.loop, g.stop = sw_h, sw_l, loop, stop
    g.halts_branch = VGroup(a_h, sw_h, ah2, loop)
    g.loops_branch = VGroup(a_l, sw_l, al2, stop)
    return g.scale(scale)


class S04Halting(VoiceoverScene):
    def construct(self):
        self.set_speech_service(get_speech_service())
        m = mbox("M", w=1.6, h=1.2).move_to(LEFT * 5 + UP * 1.0)
        w = math("w", size=52).move_to(LEFT * 5 + DOWN * 0.6)
        qb = card(["does M halt on w?"], size=40, box_color=PRIMARY).move_to(RIGHT * 0.5 + UP * 0.2)
        a1 = Arrow(m.get_right(), qb.get_left(), buff=0.15, color=MUTED)
        a2 = Arrow(w.get_right(), qb.get_left(), buff=0.15, color=MUTED)
        oh = text("halts", size=38, color=HALT_C).move_to(LEFT * 1.4 + DOWN * 2.2)
        of = text("runs forever", size=38, color=LOOP_C).move_to(RIGHT * 2.6 + DOWN * 2.2)
        oa = VGroup(Arrow(qb.get_bottom(), oh.get_top(), buff=0.1, color=MUTED, stroke_width=3),
                    Arrow(qb.get_bottom(), of.get_top(), buff=0.1, color=MUTED, stroke_width=3))
        with self.voiceover(text=N("s04.b1")) as tr:
            self.play(FadeIn(m), FadeIn(w), run_time=0.6)
            self.play(GrowArrow(a1), GrowArrow(a2), FadeIn(qb), run_time=0.8)
            self.play(GrowArrow(oa[0]), FadeIn(oh), run_time=0.6)
            wait_until(self, tr, "forever")
            self.play(GrowArrow(oa[1]), FadeIn(of), run_time=0.6)
            rest(self, tr)
        self.play(FadeOut(VGroup(w, qb, a1, a2, oh, of, oa)), m.animate.move_to(LEFT * 2.5 + UP * 0.3), run_time=0.6)

        lab = text("steps:", size=40, color=MUTED).move_to(RIGHT * 1.0 + UP * 0.3)
        cnt = [math(s, size=52) for s in ("10", "1000", "1000000")]
        for c in cnt:
            c.next_to(lab, RIGHT, 0.3)
        qm = text("?", size=72, color=PRIMARY).next_to(cnt[2], RIGHT, 0.4)
        nxt = math("1000001", size=44, color=PRIMARY).next_to(cnt[2], DOWN, 0.4).align_to(cnt[2], LEFT).set_opacity(0.6)
        with self.voiceover(text=N("s04.b2")) as tr:
            self.play(FadeIn(lab), FadeIn(cnt[0]), run_time=0.5)
            spin = Indicate(m.box, color=PRIMARY, scale_factor=1.03)
            self.play(spin, run_time=0.5)
            self.play(Transform(cnt[0], cnt[1]), run_time=0.5)
            self.wait(frac_time(tr, 0.1))
            self.play(Transform(cnt[0], cnt[2]), run_time=0.5)
            wait_until(self, tr, "nothing")
            self.play(FadeIn(qm, scale=1.4), run_time=0.5)
            self.wait(frac_time(tr, 0.06))
            self.play(FadeIn(nxt, shift=DOWN * 0.1), run_time=0.7)
            rest(self, tr)
        self.play(FadeOut(VGroup(m, lab, cnt[0], qm, nxt)), run_time=0.5)

        h = h_box(1.1).move_to(ORIGIN)
        ins = VGroup(math("M", size=48), math("w", size=48)).arrange(DOWN, buff=0.5).move_to(LEFT * 4)
        ia = VGroup(*[Arrow(x.get_right(), h.get_left(), buff=0.15, color=MUTED, stroke_width=3) for x in ins])
        outs = [text('"halts"', size=40, color=HALT_C), text('"loops"', size=40, color=LOOP_C)]
        for o in outs:
            o.move_to(RIGHT * 3.8)
        oa = Arrow(h.get_right(), outs[0].get_left(), buff=0.15, color=MUTED, stroke_width=3)
        tk = tick(48).next_to(outs[0], RIGHT, 0.3)
        hq = mbox("?", color=PRIMARY, w=2.0, h=1.4, tex=False).scale(1.1).move_to(h)
        with self.voiceover(text=N("s04.b3")) as tr:
            self.wait(frac_time(tr, 0.15))
            self.play(FadeIn(hq), run_time=0.6)
            wait_until(self, tr, "h")
            self.play(ReplacementTransform(hq, h), run_time=0.6)
            self.play(FadeIn(ins), GrowArrow(ia[0]), GrowArrow(ia[1]), run_time=0.7)
            self.play(GrowArrow(oa), FadeIn(outs[0]), run_time=0.6)
            self.play(FadeIn(tk), run_time=0.4)
            self.wait(frac_time(tr, 0.08))
            self.play(Transform(outs[0], outs[1].copy()), run_time=0.6)
            rest(self, tr)
        self.play(FadeOut(VGroup(ins, ia, outs[0], oa, tk)), run_time=0.4)

        dm = d_machine(0.95).move_to(DOWN * 0.2 + RIGHT * 0.6)
        mi = math("M", size=50).move_to(LEFT * 6.2 + DOWN * 0.2)
        with self.voiceover(text=N("s04.b4")) as tr:
            self.play(ReplacementTransform(h, dm.h), run_time=0.7)
            self.play(Create(dm.d), FadeIn(dm.dl), run_time=0.8)
            self.play(FadeIn(mi), run_time=0.4)
            wait_until(self, tr, "own")
            c1 = math("M", size=40).move_to(dm.h.get_left() + LEFT * 1.2 + UP * 0.45)
            c2 = math(r"\langle M\rangle", size=40, color=PRIMARY).move_to(dm.h.get_left() + LEFT * 1.2 + DOWN * 0.45)
            self.play(TransformFromCopy(mi, c1), TransformFromCopy(mi, c2), run_time=0.9)
            note = text("M, run on M", size=30, color=PRIMARY).next_to(dm.d, DOWN, 0.25)
            self.play(FadeIn(note), run_time=0.5)
            rest(self, tr)

        with self.voiceover(text=N("s04.b5")) as tr:
            wait_until(self, tr, "opposite")
            self.play(GrowArrow(dm.sw[0]), FadeIn(dm.sw_h), run_time=0.5)
            self.play(GrowArrow(dm.sw[4]), FadeIn(dm.loop), run_time=0.5)
            self.play(Rotate(dm.loop, -TAU), run_time=0.6)
            self.play(GrowArrow(dm.sw[1]), FadeIn(dm.sw_l), run_time=0.5)
            self.play(GrowArrow(dm.sw[5]), FadeIn(dm.stop), run_time=0.6)
            rest(self, tr)

        dd = math(r"\langle D\rangle", size=50, color=SECONDARY).move_to(mi)
        with self.voiceover(text=N("s04.b6")) as tr:
            self.play(FadeOut(note), FadeOut(c1), FadeOut(c2), ReplacementTransform(mi, dd), run_time=0.6)
            c1 = math("D", size=40, color=SECONDARY).move_to(dm.h.get_left() + LEFT * 1.2 + UP * 0.45)
            c2 = math(r"\langle D\rangle", size=40, color=SECONDARY).move_to(dm.h.get_left() + LEFT * 1.2 + DOWN * 0.45)
            self.play(TransformFromCopy(dd, c1), TransformFromCopy(dd, c2), run_time=0.7)
            wait_until(self, tr, "loops")
            self.play(Indicate(dm.halts_branch, color=PRIMARY), Rotate(dm.loop, -TAU), run_time=0.9)
            x1 = xout(dm.halts_branch, pad=0.05, width=5)
            self.play(Create(x1), run_time=0.4)
            wait_until(self, tr, "halts")
            self.play(Indicate(dm.loops_branch, color=PRIMARY), run_time=0.8)
            x2 = xout(dm.loops_branch, pad=0.05, width=5)
            self.play(Create(x2), run_time=0.4)
            wait_until(self, tr, "wrong")
            xh = xout(dm.h)
            self.play(Create(xh), run_time=0.5)
            rest(self, tr)

        verdict = text("no machine solves the halting problem", size=42, color=PRIMARY, weight="BOLD")
        verdict.move_to(UP * 3.1)
        with self.voiceover(text=N("s04.b7")) as tr:
            self.play(FadeIn(verdict, shift=DOWN * 0.2), run_time=0.8)
            rest(self, tr)
        self.play(FadeOut(VGroup(dm, dd, c1, c2, x1, x2, xh, verdict)), run_time=0.5)

        grid = HaltGrid().move_to(UP * 0.55 + LEFT * 0.6)
        keyh = VGroup(tick(36), text("halts", size=28, color=MUTED)).arrange(RIGHT, buff=0.15)
        keyl = VGroup(loop_icon(36), text("loops", size=28, color=MUTED)).arrange(RIGHT, buff=0.15)
        key = VGroup(keyh, keyl).arrange(DOWN, buff=0.25, aligned_edge=LEFT).to_edge(RIGHT, buff=0.6).shift(UP * 1.5)
        with self.voiceover(text=N("s04.b8")) as tr:
            self.play(FadeIn(grid.rlabs, shift=RIGHT * 0.2), run_time=0.8)
            self.play(FadeIn(grid.clabs, shift=DOWN * 0.2), FadeIn(grid.vd), FadeIn(grid.hd), run_time=0.8)
            self.play(LaggedStart(*[FadeIn(VGroup(grid.sq[i][j], grid.icons[i][j]))
                                    for i in range(5) for j in range(5)], lag_ratio=0.03),
                      FadeIn(key), run_time=1.4)
            wait_until(self, tr, "diagonal")
            diag_sq = VGroup(*[grid.sq[i][i] for i in range(5)])
            self.play(diag_sq.animate.set_stroke(PRIMARY, width=5), run_time=0.6)
            self.play(*[Transform(grid.icons[i][i], halt_icon(1 - GRID[i][i], 40).move_to(grid.sq[i][i]))
                        for i in range(5)], run_time=0.8)
            rest(self, tr)

        fr = flipped_row(grid)
        hs = h_box(0.6).to_edge(RIGHT, buff=0.8).match_y(fr)
        cantor = tag("Cantor's diagonal", size=30).next_to(key, DOWN, 0.6).to_edge(RIGHT, buff=0.5)
        with self.voiceover(text=N("s04.b9")) as tr:
            self.play(*[Transform(grid.icons[i][i], halt_icon(GRID[i][i], 40).move_to(grid.sq[i][i])) for i in range(5)],
                      FadeIn(fr.sq), FadeIn(fr.lab),
                      *[TransformFromCopy(grid.icons[i][i], fr.icons[i]) for i in range(5)], run_time=1.0)
            step = max(0.25, (tr.time_until_bookmark("not") - 0.1) / 5)
            for i in range(5):
                hi = VGroup(grid.sq[i][i].copy().set_stroke(BAD, width=6), fr.sq[i].copy().set_stroke(BAD, width=6))
                self.play(FadeIn(hi), run_time=step * 0.5)
                self.play(FadeOut(hi), run_time=step * 0.5)
            wait_until(self, tr, "not")
            xr = xout(VGroup(fr.sq, fr.lab))
            self.play(Create(xr), run_time=0.5)
            wait_until(self, tr, "built")
            self.play(FadeIn(hs), run_time=0.4)
            ar = Arrow(fr.sq[-1].get_right(), hs.get_left(), buff=0.15, color=PRIMARY, stroke_width=4)
            self.play(GrowArrow(ar), run_time=0.5)
            xh = xout(hs)
            self.play(Create(xh), FadeIn(cantor), run_time=0.6)
            rest(self, tr)
        self.play(FadeOut(VGroup(grid, fr, hs, ar, xh, xr, key, cantor)), run_time=0.5)

        dbox = mbox("D", color=SECONDARY, w=2.6, h=1.8).move_to(RIGHT * 0.8)
        din = math(r"\langle D\rangle", size=48, color=SECONDARY).move_to(LEFT * 3.2)
        a_in = Arrow(din.get_right(), dbox.get_left(), buff=0.2, color=MUTED)
        back = CurvedArrow(dbox.get_top() + UP * 0.1, din.get_top() + UP * 0.15, angle=PI / 2.5, color=PRIMARY,
                           stroke_width=4)
        with self.voiceover(text=N("s04.b10")) as tr:
            self.play(FadeIn(dbox), FadeIn(din), GrowArrow(a_in), run_time=0.8)
            wait_until(self, tr, "read")
            self.play(Create(back), run_time=0.8)
            self.play(back.animate.set_stroke(width=8), din.animate.set_color(PRIMARY), run_time=0.6)
            rest(self, tr)
        self.play(FadeOut(VGroup(dbox, din, a_in, back)), run_time=0.6)


# ---------------------------------------------------------------------------
# s05 Problems as sentences
# ---------------------------------------------------------------------------


def goldbach(size=40):
    return VGroup(text("Every even number bigger than 2", size=size),
                  text("is the sum of two primes.", size=size)).arrange(DOWN, buff=0.2)


def alphabet(size=44):
    syms = [r"\forall", r"\exists", r"\neg", r"\wedge", "=", "+", r"\times", "0", "S", "(", ")", "x", "y"]
    cells = VGroup(*[Square(0.8, color=MUTED, stroke_width=2) for _ in syms]).arrange(RIGHT, buff=0.08)
    ms = VGroup(*[math(s, size=size).move_to(c) for s, c in zip(syms, cells)])
    return VGroup(cells, ms)


class S05Sentences(VoiceoverScene):
    def construct(self):
        self.set_speech_service(get_speech_service())
        icon = fork_icon("right")
        gb = goldbach(44).move_to(UP * 0.3)
        with self.voiceover(text=N("s05.b1")) as tr:
            self.play(FadeIn(icon), run_time=0.6)
            wait_until(self, tr, "goldbach")
            self.play(FadeIn(gb, shift=UP * 0.2), run_time=1.0)
            rest(self, tr)

        al = alphabet().move_to(UP * 1.8)
        fs = math(SENT, size=64).move_to(DOWN * 0.6)
        gloss = text("0 is not the next number after anything", size=32, color=MUTED).next_to(fs, DOWN, 0.4)
        with self.voiceover(text=N("s05.b2")) as tr:
            self.play(gb.animate.scale(0.6).move_to(UP * 3.1), run_time=0.6)
            self.play(LaggedStart(*[FadeIn(VGroup(al[0][i], al[1][i]), shift=UP * 0.1) for i in range(len(al[0]))],
                                  lag_ratio=0.12), run_time=2.0)
            wait_until(self, tr, "grammar")
            self.play(Write(fs), run_time=1.2)
            self.play(FadeIn(gloss), run_time=0.6)
            rest(self, tr)

        tt = text("true", size=36, color=GOOD).next_to(fs, RIGHT, 0.5)
        tb = card(["true"], size=40, color=GOOD, box_color=GOOD).move_to(DOWN * 2.3 + LEFT * 1.2)
        pb = card(["proved"], size=40, color=PRIMARY, box_color=PRIMARY).move_to(DOWN * 2.3 + RIGHT * 1.5)
        with self.voiceover(text=N("s05.b3")) as tr:
            self.play(FadeOut(al), FadeOut(gb), FadeOut(gloss), fs.animate.move_to(UP * 1.0), run_time=0.6)
            tt.next_to(fs, RIGHT, 0.5)
            self.play(FadeIn(tt, shift=LEFT * 0.2), run_time=0.6)
            self.play(FadeIn(tb), FadeIn(pb), run_time=0.6)
            wait_until(self, tr, "another")
            self.play(tb.animate.shift(LEFT * 2.0), pb.animate.shift(RIGHT * 2.0), run_time=0.9)
            rest(self, tr)
        self.play(FadeOut(VGroup(fs, tt, tb, pb)), run_time=0.5)

        pc = proof_card(size=36).move_to(DOWN * 0.3)
        with self.voiceover(text=N("s05.b4")) as tr:
            self.wait(frac_time(tr, 0.15))
            self.play(LaggedStart(*[FadeIn(VGroup(r[0], r[1]), shift=RIGHT * 0.2) for r in pc], lag_ratio=0.25),
                      run_time=1.6)
            wait_until(self, tr, "rules")
            for r in pc:
                self.play(FadeIn(r[2], shift=LEFT * 0.1), run_time=0.35)
            rest(self, tr)

        scan = SurroundingRectangle(pc[0], color=PRIMARY, buff=0.1, stroke_width=3)
        mech = tag("checking a proof is mechanical", size=36, color=PRIMARY).move_to(UP * 2.9)
        with self.voiceover(text=N("s05.b5")) as tr:
            self.play(Create(scan), run_time=0.4)
            step = max(0.3, (tr.time_until_bookmark("machine") - 0.5) / 5)
            for i, r in enumerate(pc):
                if i:
                    self.play(scan.animate.move_to(r), run_time=step * 0.5)
                self.play(FadeIn(tick(32).next_to(r[0], LEFT, 0.3)), run_time=step * 0.5)
            wait_until(self, tr, "machine")
            self.play(FadeIn(mech, shift=DOWN * 0.2), run_time=0.6)
            rest(self, tr)
        self.play(FadeOut(Group(*[m for m in self.mobjects if m is not icon])), run_time=0.5)

        db = dream_box(30).move_to(LEFT * 3.3 + UP * 0.6)
        db.tags.next_to(db.box, DOWN, 0.35)
        sin = math(r"\varphi", size=56).next_to(db.box, LEFT, 0.8)
        o1 = text("a proof of it", size=32, color=GOOD)
        o2 = text("or a proof of its opposite", size=32, color=GOOD)
        outs = VGroup(o1, o2).arrange(DOWN, buff=0.2, aligned_edge=LEFT).next_to(db.box, RIGHT, 0.9)
        a_in = Arrow(sin.get_right(), db.box.get_left(), buff=0.1, color=MUTED, stroke_width=3)
        a_out = Arrow(db.box.get_right(), outs.get_left(), buff=0.1, color=MUTED, stroke_width=3)
        cheat = VGroup(text("axioms:", size=30, color=MUTED), text("every true sentence", size=30))
        cheat.arrange(RIGHT, buff=0.2).move_to(RIGHT * 3.4 + DOWN * 1.9)
        quote = text("We will know.", size=34, color=PRIMARY).move_to(UP * 3.1).set_opacity(0.6)
        with self.voiceover(text=N("s05.b6")) as tr:
            self.play(FadeIn(db.box), FadeIn(db.head), run_time=0.7)
            self.play(FadeIn(sin), GrowArrow(a_in), run_time=0.5)
            self.play(GrowArrow(a_out), FadeIn(outs), run_time=0.7)
            self.play(FadeIn(db.tags[0]), run_time=0.5)
            self.wait(frac_time(tr, 0.05))
            self.play(FadeIn(db.tags[1]), run_time=0.5)
            wait_until(self, tr, "check")
            self.play(FadeIn(db.tags[2]), run_time=0.5)
            wait_until(self, tr, "cheat")
            self.play(FadeIn(cheat), run_time=0.5)
            self.play(Create(xout(cheat)), run_time=0.5)
            wait_until(self, tr, "know")
            self.play(FadeIn(quote), run_time=0.6)
            rest(self, tr)
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.6)


# ---------------------------------------------------------------------------
# s06 Incompleteness
# ---------------------------------------------------------------------------


def code_table(size=42):
    cols = VGroup()
    for s, n in SYMS:
        cols.add(VGroup(math(s, size=size), math(r"\downarrow", size=size - 12, color=MUTED),
                        math(n, size=size, color=PRIMARY)).arrange(DOWN, buff=0.12))
    return cols.arrange(RIGHT, buff=0.55)


class S06Incompleteness(VoiceoverScene):
    def construct(self):
        self.set_speech_service(get_speech_service())
        ct = code_table().move_to(UP * 2.0)
        fs = math(SENT, size=56).move_to(DOWN * 0.4)
        sc = math(SENT_CODE, size=56, color=PRIMARY).move_to(fs)
        pc = proof_card(size=26, dy=0.5, tags=False).move_to(DOWN * 2.2)
        pcode = math(PROOF_CODE, size=38, color=PRIMARY).move_to(DOWN * 2.2)
        with self.voiceover(text=N("s06.b1")) as tr:
            self.play(LaggedStart(*[FadeIn(c, shift=DOWN * 0.15) for c in ct], lag_ratio=0.15), run_time=1.6)
            self.play(FadeIn(fs), run_time=0.6)
            wait_until(self, tr, "sentence")
            self.play(ReplacementTransform(fs, sc), run_time=1.0)
            self.play(FadeIn(pc), run_time=0.5)
            wait_until(self, tr, "proof")
            self.play(ReplacementTransform(pc, pcode), run_time=1.0)
            rest(self, tr)
        self.play(FadeOut(VGroup(ct, sc, pcode)), run_time=0.5)

        st = VGroup(text("p is the code of a proof", size=44),
                    text("of the sentence with code s", size=44)).arrange(DOWN, buff=0.2).move_to(UP * 0.6)
        stag = tag("a statement about numbers", size=36, color=PRIMARY).next_to(st, DOWN, 0.6)
        with self.voiceover(text=N("s06.b2")) as tr:
            self.play(FadeIn(st, shift=UP * 0.2), run_time=0.8)
            wait_until(self, tr, "numbers")
            self.play(FadeIn(stag), run_time=0.6)
            rest(self, tr)
        self.play(FadeOut(VGroup(st, stag)), run_time=0.5)

        lt = rule_table(28).move_to(LEFT * 3.6 + UP * 1.1)
        ls = rule_string(22).move_to(LEFT * 3.6 + DOWN * 0.9)
        rp = proof_card(size=24, dy=0.45, tags=False).move_to(RIGHT * 3.6 + UP * 1.1)
        rn = math(PROOF_CODE, size=26, color=PRIMARY).move_to(RIGHT * 3.6 + DOWN * 0.9)
        eq = math("=", size=80, color=MUTED).move_to(DOWN * 0.9)
        ltag = tag("machines as strings", size=28).next_to(ls, DOWN, 0.4)
        rtag = tag("proofs as numbers", size=28).next_to(rn, DOWN, 0.4)
        with self.voiceover(text=N("s06.b3")) as tr:
            self.play(FadeIn(lt), FadeIn(rp), run_time=0.6)
            self.play(TransformFromCopy(lt, ls), TransformFromCopy(rp, rn), run_time=1.0)
            self.play(FadeIn(eq), FadeIn(ltag), FadeIn(rtag), run_time=0.5)
            wait_until(self, tr, "describe")
            self.play(Indicate(ls, color=PRIMARY), Indicate(rn, color=PRIMARY), run_time=1.0)
            rest(self, tr)
        self.play(FadeOut(VGroup(lt, ls, rp, rn, eq, ltag, rtag)), run_time=0.5)

        g = g_box().move_to(UP * 1.4 + RIGHT * 0.4)
        din = VGroup(math(r"\langle D\rangle", size=36, color=SECONDARY), math(r"\to", size=36, color=MUTED),
                     mbox("D", color=SECONDARY, w=1.1, h=0.8, size=36)).arrange(RIGHT, buff=0.2)
        gin = VGroup(math(r"\ulcorner G \urcorner", size=36, color=PRIMARY), math(r"\to", size=36, color=MUTED),
                     mbox("G", color=PRIMARY, w=1.1, h=0.8, size=36)).arrange(RIGHT, buff=0.2)
        inset = VGroup(din, gin).arrange(RIGHT, buff=1.4).move_to(DOWN * 1.8)
        with self.voiceover(text=N("s06.b4")) as tr:
            self.play(FadeIn(g.lab, scale=1.3), run_time=0.6)
            wait_until(self, tr, "g")
            self.play(FadeIn(g.box), FadeIn(g.body), run_time=0.8)
            self.play(Create(g.arc), run_time=0.6)
            wait_until(self, tr, "feed")
            self.play(FadeIn(din), run_time=0.6)
            self.play(FadeIn(gin), run_time=0.6)
            rest(self, tr)

        sup = text("suppose G has a proof", size=38).move_to(LEFT * 3.0 + DOWN * 0.9)
        bad = text("the system proved something false", size=34, color=BAD).next_to(sup, DOWN, 0.6).align_to(sup, LEFT)
        ab = Arrow(sup.get_bottom(), bad.get_top(), buff=0.1, color=MUTED, stroke_width=3)
        np_ = VGroup(text("G has no proof", size=40), tick(44)).arrange(RIGHT, buff=0.25).move_to(RIGHT * 3.6 + DOWN * 1.6)
        with self.voiceover(text=N("s06.b5")) as tr:
            self.play(FadeOut(inset), run_time=0.4)
            self.play(FadeIn(sup), run_time=0.6)
            wait_until(self, tr, "false")
            self.play(GrowArrow(ab), FadeIn(bad), run_time=0.7)
            self.play(Create(xout(bad, width=5)), run_time=0.4)
            self.wait(frac_time(tr, 0.1))
            self.play(VGroup(sup, ab, bad).animate.set_opacity(0.3), run_time=0.5)
            self.play(FadeIn(np_, shift=UP * 0.2), run_time=0.6)
            rest(self, tr)

        gtrue = text("true", size=40, color=GOOD).next_to(g.box, RIGHT, 0.4)
        with self.voiceover(text=N("s06.b6")) as tr:
            self.play(FadeOut(Group(*[m for m in self.mobjects if m not in (g, np_)])), run_time=0.4)
            self.add(g)
            self.play(np_.animate.next_to(g.box, DOWN, 0.6), run_time=0.8)
            self.play(Indicate(g.body, color=PRIMARY), Indicate(np_[0], color=PRIMARY), run_time=0.8)
            wait_until(self, tr, "true")
            self.play(FadeIn(gtrue, shift=LEFT * 0.2), run_time=0.6)
            rest(self, tr)

        opp = VGroup(text("G has a proof", size=38), text("false, so no proof either", size=30, color=BAD))
        opp.arrange(DOWN, buff=0.2).move_to(DOWN * 1.9)
        ns = SurroundingRectangle(VGroup(g, gtrue, np_, opp), buff=0.3, corner_radius=0.2, color=MUTED, stroke_width=3)
        nsl = text("not settled", size=32, color=MUTED).next_to(ns, UP, 0.15).align_to(ns, LEFT)
        inc = text("incomplete", size=40, color=PRIMARY, weight="BOLD").next_to(ns, UP, 0.15).align_to(ns, LEFT)
        with self.voiceover(text=N("s06.b7")) as tr:
            self.play(FadeOut(np_[1]), FadeIn(opp), run_time=0.8)
            self.play(Create(ns), FadeIn(nsl), run_time=0.7)
            wait_until(self, tr, "incomplete")
            self.play(ReplacementTransform(nsl, inc), ns.animate.set_color(PRIMARY), run_time=0.7)
            rest(self, tr)
        self.play(FadeOut(VGroup(ns, inc, opp, np_, gtrue)), g.animate.scale(0.7).move_to(UP * 2.6 + RIGHT * 2.6),
                  run_time=0.6)

        ax = VGroup(text("axioms", size=30, color=MUTED), math(r"A_1", size=36), math(r"A_2", size=36),
                    math(r"\vdots", size=36)).arrange(DOWN, buff=0.2)
        axbox = SurroundingRectangle(ax, buff=0.3, corner_radius=0.15, color=MUTED, stroke_width=3)
        axg = VGroup(axbox, ax).move_to(LEFT * 4.8 + UP * 0.8)
        gn = math("G", size=36, color=PRIMARY).next_to(axg, DOWN, 0.2)
        g1 = text("G' has no proof in the new system", size=34).move_to(RIGHT * 1.6 + UP * 0.9)
        g2 = text("G'' has no proof in the next one", size=34).next_to(g1, DOWN, 0.35)
        g3 = math(r"\vdots", size=40).next_to(g2, DOWN, 0.3)
        tags3 = VGroup(text("a machine checks the proofs", size=30), text("never proves anything false", size=30),
                       text("does arithmetic with + and \u00d7", size=30)).arrange(DOWN, buff=0.15, aligned_edge=LEFT)
        tags3.set_color(PRIMARY).move_to(DOWN * 2.4 + RIGHT * 1.6)
        with self.voiceover(text=N("s06.b8")) as tr:
            self.play(FadeIn(axg), run_time=0.5)
            self.play(ReplacementTransform(g, gn), run_time=0.8)
            axbox2 = SurroundingRectangle(VGroup(ax, gn), buff=0.3, corner_radius=0.15, color=MUTED, stroke_width=3)
            self.play(Transform(axbox, axbox2), run_time=0.4)
            wait_until(self, tr, "new")
            self.play(FadeIn(g1, shift=LEFT * 0.2), run_time=0.6)
            self.play(FadeIn(g2, shift=LEFT * 0.2), FadeIn(g3), run_time=0.7)
            wait_until(self, tr, "every")
            self.play(LaggedStart(*[FadeIn(t) for t in tags3], lag_ratio=0.4), run_time=1.4)
            rest(self, tr)
        self.play(FadeOut(VGroup(axg, gn, g1, g2, g3, tags3)), run_time=0.5)

        n1 = card(["assumed: never proves anything false"], size=38).move_to(UP * 0.3)
        n2 = card(["Rosser, 1936: never contradicting itself is enough"], size=38, color=PRIMARY,
                  box_color=PRIMARY).move_to(UP * 0.3)
        with self.voiceover(text=N("s06.b9")) as tr:
            self.play(FadeIn(n1), run_time=0.7)
            wait_until(self, tr, "less")
            self.play(ReplacementTransform(n1, n2), run_time=0.9)
            rest(self, tr)
        self.play(FadeOut(n2), run_time=0.6)


# ---------------------------------------------------------------------------
# s07 Side by side
# ---------------------------------------------------------------------------


ROWS7 = [("a string", "a sentence"), ("a machine stops\nwith the answer", "a proof of it\nor its opposite"),
         ("machines read\nmachines", "sentences talk about\ncodes of sentences"),
         ("D: do the opposite of\nwhat H says about me", "G: I have no proof")]


def cell_text(s, size=32, color=FG):
    return VGroup(*[text(l, size=size, color=color) for l in s.split("\n")]).arrange(DOWN, buff=0.1)


class S07Side(VoiceoverScene):
    def construct(self):
        self.set_speech_service(get_speech_service())
        xl, xr = -1.3, 4.1
        ht = text("Turing", size=40, color=SECONDARY, weight="BOLD").move_to(np.array([xl, 3.2, 0]))
        hg = text(GODEL, size=40, color=SECONDARY, weight="BOLD").move_to(np.array([xr, 3.2, 0]))
        names = ["problem", "solve", "self-description", "self-reference"]
        ys = [2.1, 0.9, -0.6, -2.3]
        lab = [text(n, size=28, color=MUTED).move_to(np.array([-6.2, y, 0]), aligned_edge=LEFT) for n, y in zip(names, ys)]
        cells = [(cell_text(a).move_to(np.array([xl, y, 0])), cell_text(b).move_to(np.array([xr, y, 0])))
                 for (a, b), y in zip(ROWS7, ys)]
        div = Line(np.array([1.4, 3.5, 0]), np.array([1.4, -3.3, 0]), color=MUTED, stroke_width=2)

        def row(i):
            return [FadeIn(lab[i]), FadeIn(cells[i][0], shift=RIGHT * 0.15), FadeIn(cells[i][1], shift=LEFT * 0.15)]

        with self.voiceover(text=N("s07.b1")) as tr:
            self.play(FadeIn(ht), FadeIn(hg), Create(div), run_time=0.7)
            wait_until(self, tr, "problem")
            self.play(*row(0), run_time=0.7)
            wait_until(self, tr, "solve")
            self.play(*row(1), run_time=0.7)
            rest(self, tr)
        with self.voiceover(text=N("s07.b2")) as tr:
            wait_until(self, tr, "reads")
            self.play(*row(2), run_time=0.8)
            rest(self, tr)
        with self.voiceover(text=N("s07.b3")) as tr:
            wait_until(self, tr, "d")
            self.play(*row(3), run_time=0.8)
            wait_until(self, tr, "against")
            self.play(Indicate(cells[3][0], color=PRIMARY), Indicate(cells[3][1], color=PRIMARY), run_time=1.0)
            rest(self, tr)
        left = VGroup(ht, *[c[0] for c in cells])
        right = VGroup(hg, *[c[1] for c in cells])
        with self.voiceover(text=N("s07.b4")) as tr:
            sims = VGroup(*[math(r"\approx", size=56, color=PRIMARY).move_to(np.array([1.4, y, 0])) for y in ys])
            self.play(FadeOut(VGroup(*lab)), FadeOut(div), left.animate.shift(LEFT * 1.4), right.animate.shift(LEFT * 0.4),
                      run_time=1.0)
            self.play(LaggedStart(*[FadeIn(x, scale=1.4) for x in sims], lag_ratio=0.2), run_time=1.0)
            wait_until(self, tr, "other")
            arr = CurvedArrow(np.array([-2.7, -3.2, 0]), np.array([3.7, -3.2, 0]), angle=PI / 6, color=PRIMARY,
                              stroke_width=5)
            al = text("one from the other", size=30, color=PRIMARY).next_to(arr, DOWN, 0.05)
            self.play(Create(arr), FadeIn(al), run_time=0.8)
            rest(self, tr)
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.6)


# ---------------------------------------------------------------------------
# s08 One from the other
# ---------------------------------------------------------------------------


def proof_stream(n=7, size=26):
    return VGroup(*[card([f"proof {i + 1}"], size=size, box_color=MUTED, pad=0.2) for i in range(n)])


class S08OneFromOther(VoiceoverScene):
    def construct(self):
        self.set_speech_service(get_speech_service())
        ps = mbox("proof search", w=4.2, h=1.6, size=36, tex=False).move_to(DOWN * 0.3)
        phi = math(r"\varphi", size=56).next_to(ps, LEFT, 0.9)
        pa = Arrow(phi.get_right(), ps.get_left(), buff=0.1, color=MUTED, stroke_width=3)
        light = Circle(radius=0.25, color=MUTED, stroke_width=3).next_to(ps, RIGHT, 0.6)
        cards = proof_stream(6).arrange(RIGHT, buff=0.25).next_to(ps, UP, 0.7).align_to(ps, LEFT).shift(LEFT * 4.5)
        with self.voiceover(text=N("s08.b1")) as tr:
            self.play(FadeIn(ps), FadeIn(phi), GrowArrow(pa), FadeIn(light), run_time=0.8)
            step = max(0.3, (tr.time_until_bookmark("stops") - 1.0) / 5)
            for i in range(5):
                c = cards[i].move_to(ps.get_top() + UP * 0.9)
                self.play(FadeIn(c, shift=RIGHT * 2.5), run_time=step * 0.5)
                self.play(FadeOut(c, shift=DOWN * 0.3), Indicate(ps.box, color=BAD, scale_factor=1.02), run_time=step * 0.5)
            wait_until(self, tr, "stops")
            c = cards[5].move_to(ps.get_top() + UP * 0.9)
            self.play(FadeIn(c), run_time=0.3)
            self.play(c.box.animate.set_color(GOOD), light.animate.set_fill(GOOD, 1).set_color(GOOD), run_time=0.6)
            stp = text("stop", size=32, color=GOOD).next_to(light, DOWN, 0.2)
            self.play(FadeIn(stp), run_time=0.4)
            rest(self, tr)
        self.play(FadeOut(VGroup(ps, phi, pa, light, cards[5], stp)), run_time=0.5)

        eq = VGroup(text("provable", size=50), math("=", size=60, color=MUTED),
                    text("the proof search", size=50), text("halts", size=50)).arrange(RIGHT, buff=0.35)
        eq.move_to(UP * 0.3)
        with self.voiceover(text=N("s08.b2")) as tr:
            self.play(FadeIn(eq), run_time=0.9)
            wait_until(self, tr, "halting")
            self.play(eq[3].animate.set_color(PRIMARY).scale(1.15), run_time=0.6)
            rest(self, tr)
        self.play(FadeOut(eq), run_time=0.5)

        mh = text("M halts on w", size=48).move_to(UP * 2.0)
        mh2 = VGroup(text("there is a number that codes", size=40),
                     text("a finished run of M on w", size=40)).arrange(DOWN, buff=0.15).move_to(UP * 0.5)
        mtag = tag("a sentence of arithmetic", size=34, color=PRIMARY).next_to(mh2, DOWN, 0.4)
        run = Tape(list("_1011_"), cell=0.6, size=30, head=1).move_to(DOWN * 2.2)
        rnum = math("4\\,7\\,1\\,0\\,0\\,9\\,3\\,8\\,2\\,6\\,5", size=44, color=PRIMARY).move_to(DOWN * 2.2)
        with self.voiceover(text=N("s08.b3")) as tr:
            self.play(FadeIn(mh), run_time=0.6)
            self.play(TransformFromCopy(mh, mh2), run_time=0.9)
            self.play(FadeIn(mtag), run_time=0.5)
            wait_until(self, tr, "run")
            self.play(FadeIn(run), run_time=0.4)
            self.play(run.write(1, "0"), run_time=0.3)
            self.play(run.move(1), run_time=0.3)
            self.play(run.move(1), run_time=0.3)
            self.play(ReplacementTransform(run, rnum), run_time=0.7)
            rest(self, tr)
        self.play(FadeOut(VGroup(mh, mh2, mtag, rnum)), run_time=0.5)

        db = dream_box(28).scale(0.9).to_corner(UL, buff=0.4)
        s1 = card(["search for a proof of", "M halts on w"], size=32, box_color=MUTED).move_to(LEFT * 1.2 + DOWN * 1.5)
        s2 = card(["search for a proof of", "M never halts on w"], size=32, box_color=MUTED).move_to(RIGHT * 3.9 + DOWN * 1.5)
        mw = VGroup(math("M", size=44), math("w", size=44)).arrange(RIGHT, buff=0.4).move_to(RIGHT * 1.35 + UP * 0.4)
        a1 = Arrow(mw.get_bottom(), s1.get_top(), buff=0.15, color=MUTED, stroke_width=3)
        a2 = Arrow(mw.get_bottom(), s2.get_top(), buff=0.15, color=MUTED, stroke_width=3)
        with self.voiceover(text=N("s08.b4")) as tr:
            self.play(FadeIn(db), run_time=0.8)
            self.wait(frac_time(tr, 0.2))
            self.play(FadeIn(mw), run_time=0.5)
            wait_until(self, tr, "same")
            self.play(GrowArrow(a1), GrowArrow(a2), FadeIn(s1), FadeIn(s2), run_time=0.8)
            self.play(Indicate(s1.box, color=PRIMARY), Indicate(s2.box, color=PRIMARY), run_time=0.8)
            rest(self, tr)

        found = text("found one", size=34, color=GOOD).next_to(s1, DOWN, 0.3)
        ans = VGroup(text("answer: right", size=34, color=GOOD), tick(40)).arrange(RIGHT, buff=0.2).next_to(found, DOWN, 0.2)
        allg = VGroup(mw, a1, a2, s1, s2, found, ans)
        solver = SurroundingRectangle(allg, buff=0.3, corner_radius=0.2, color=PRIMARY, stroke_width=4)
        sl = text("a machine that solves the halting problem", size=32, color=PRIMARY).next_to(solver, UP, 0.12)
        with self.voiceover(text=N("s08.b5")) as tr:
            wait_until(self, tr, "one")
            self.play(s1.box.animate.set_color(GOOD), FadeIn(found), run_time=0.6)
            wait_until(self, tr, "right")
            self.play(FadeIn(ans), run_time=0.6)
            self.play(Create(solver), FadeIn(sl), run_time=0.8)
            rest(self, tr)

        incl = text("incompleteness", size=44, color=PRIMARY, weight="BOLD").to_corner(UR, buff=0.5)
        with self.voiceover(text=N("s08.b6")) as tr:
            wait_until(self, tr, "impossible")
            self.play(Create(xout(VGroup(solver, sl))), run_time=0.6)
            self.play(Create(xout(db)), run_time=0.5)
            self.play(FadeIn(incl), run_time=0.6)
            rest(self, tr)
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.5)

        hl = text("halts", size=40, color=HALT_C).move_to(LEFT * 3.5 + UP * 2.7)
        nl = text("never halts", size=40, color=LOOP_C).move_to(RIGHT * 3.5 + UP * 2.7)
        t1 = Tape(list("_10_"), cell=0.6, size=30).move_to(LEFT * 3.5 + UP * 1.3)
        stop = stop_icon(0.25).next_to(t1, RIGHT, 0.3)
        pr = VGroup(text("proof: the run,", size=30), text("step by step", size=30), tick(36)).arrange(DOWN, buff=0.1)
        pr.next_to(t1, DOWN, 0.6)
        t2 = Tape(list("_1011"), cell=0.6, size=30).move_to(RIGHT * 3.2 + UP * 1.3)
        dots = math(r"\cdots", size=44, color=MUTED).next_to(t2, RIGHT, 0.2)
        nop = text("sometimes no proof", size=34, color=PRIMARY).next_to(t2, DOWN, 0.8).shift(RIGHT * 0.3)
        with self.voiceover(text=N("s08.b7")) as tr:
            self.play(FadeIn(hl), FadeIn(nl), run_time=0.5)
            self.wait(frac_time(tr, 0.15))
            self.play(FadeIn(t1), FadeIn(stop), run_time=0.6)
            self.play(FadeIn(pr, shift=UP * 0.2), run_time=0.7)
            wait_until(self, tr, "never")
            self.play(FadeIn(t2), FadeIn(dots), run_time=0.6)
            self.play(FadeIn(nop), run_time=0.6)
            rest(self, tr)
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.5)

        gb = goldbach(36).move_to(UP * 2.8)
        checks = [r"4=2+2", r"6=3+3", r"8=3+5", r"10=3+7", r"12=5+7", r"14=3+11", r"16=3+13"]
        cm = VGroup(*[math(c, size=40) for c in checks]).arrange_in_grid(rows=2, buff=(0.7, 0.35)).move_to(DOWN * 0.1)
        ctag = tag("stops if it finds an even number that fails", size=32, color=PRIMARY).move_to(DOWN * 2.2)
        qmark = text("?", size=96, color=PRIMARY).move_to(RIGHT * 5.4 + DOWN * 0.1)
        with self.voiceover(text=N("s08.b8")) as tr:
            self.play(FadeIn(gb), run_time=0.7)
            self.wait(frac_time(tr, 0.08))
            step = max(0.25, (tr.time_until_bookmark("nobody") - 2.0) / len(cm))
            for c in cm:
                self.play(FadeIn(c, shift=DOWN * 0.1), run_time=step)
            self.play(FadeIn(ctag), run_time=0.6)
            wait_until(self, tr, "nobody")
            self.play(FadeIn(qmark, scale=1.4), run_time=0.6)
            rest(self, tr)
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.6)


# ---------------------------------------------------------------------------
# s09 Reasoning about reasoning
# ---------------------------------------------------------------------------


class S09Reasoning(VoiceoverScene):
    def construct(self):
        self.set_speech_service(get_speech_service())
        head = text("reasoning about reasoning", size=50, color=PRIMARY, weight="BOLD").move_to(UP * 3.0)
        m = mbox("M'", w=1.8, h=1.3, color=SECONDARY).move_to(LEFT * 2.6 + DOWN * 0.2)
        ms = rule_string(28).next_to(m, UP, 0.9)
        msa = Arrow(ms.get_bottom(), m.get_top(), buff=0.1, color=MUTED, stroke_width=3)
        ml = tag("machines read machines", size=30).next_to(m, DOWN, 0.4)
        ar = mbox("arithmetic", w=3.0, h=1.3, size=34, tex=False, color=SECONDARY).move_to(RIGHT * 3.6 + DOWN * 0.2)
        an = math("15264657387\\cdots", size=36, color=PRIMARY).next_to(ar, UP, 0.9)
        ana = Arrow(an.get_bottom(), ar.get_top(), buff=0.1, color=MUTED, stroke_width=3)
        al = tag("arithmetic talks about proofs", size=30).next_to(ar, DOWN, 0.4)
        with self.voiceover(text=N("s09.b1")) as tr:
            self.play(FadeIn(head), run_time=0.8)
            self.wait(frac_time(tr, 0.3))
            self.play(FadeIn(m), FadeIn(ms), run_time=0.6)
            self.play(GrowArrow(msa), FadeIn(ml), run_time=0.8)
            wait_until(self, tr, "talk")
            self.play(FadeIn(ar), FadeIn(an), run_time=0.6)
            self.play(GrowArrow(ana), FadeIn(al), run_time=0.8)
            rest(self, tr)
        self.play(FadeOut(VGroup(m, ms, msa, ml, ar, an, ana, al)), run_time=0.5)

        d = mbox("D", color=SECONDARY, w=1.6, h=1.2)
        g = mbox("G", color=PRIMARY, w=1.6, h=1.2)
        row = VGroup(*[Square(0.6, color=PRIMARY, stroke_width=3) for _ in range(5)]).arrange(RIGHT, buff=0)
        for k, s in enumerate(row):
            s.add(halt_icon(1 - GRID[k][k], 30).move_to(s))
        trio = VGroup(d, g, row).arrange(RIGHT, buff=1.6).move_to(DOWN * 0.8)
        names = VGroup(tag("Turing", 28).next_to(d, DOWN, 0.6), tag(GODEL, 28).next_to(g, DOWN, 0.6),
                       tag("Cantor", 28).next_to(row, DOWN, 0.6))
        loops = VGroup(*[CurvedArrow(x.get_right() + UP * 0.25 + RIGHT * 0.1, x.get_left() + UP * 0.25 + LEFT * 0.1,
                                     angle=PI * 0.9, color=PRIMARY, stroke_width=3, tip_length=0.18) for x in trio])
        opp = text('"do the opposite of whatever you say about me"', size=40, color=PRIMARY).move_to(UP * 1.7)
        with self.voiceover(text=N("s09.b2")) as tr:
            self.wait(frac_time(tr, 0.1))
            self.play(FadeIn(opp, shift=UP * 0.2), run_time=0.8)
            wait_until(self, tr, "dg")
            self.play(FadeIn(d), FadeIn(names[0]), run_time=0.5)
            self.play(Create(loops[0]), run_time=0.5)
            self.play(FadeIn(g), FadeIn(names[1]), Create(loops[1]), run_time=0.7)
            self.wait(frac_time(tr, 0.05))
            self.play(FadeIn(row), FadeIn(names[2]), Create(loops[2]), run_time=0.8)
            rest(self, tr)

        law = text("Lawvere's fixed point theorem, 1969", size=40, color=PRIMARY).move_to(UP * 1.6)
        with self.voiceover(text=N("s09.b3")) as tr:
            self.play(FadeOut(loops), FadeOut(head), FadeOut(opp), trio.animate.move_to(DOWN * 1.4),
                      names.animate.shift(DOWN * 1.2),
                      run_time=0.7)
            self.play(FadeIn(law), run_time=0.7)
            arws = [Arrow(law.get_bottom(), x.get_top(), buff=0.2, color=PRIMARY, stroke_width=4) for x in trio]
            self.play(GrowArrow(arws[2]), GrowArrow(arws[1]), run_time=0.8)
            wait_until(self, tr, "later")
            arws[0].set_opacity(0.5)
            self.play(GrowArrow(arws[0]), run_time=0.8)
            rest(self, tr)
        self.play(FadeOut(VGroup(law, trio, names, *arws)), run_time=0.5)

        f = fork()
        wall = Rectangle(width=12.5, height=0.35, color=BAD, stroke_width=0).set_fill(BAD, 0.85).move_to(DOWN * 3.1)
        wl = VGroup(Line(f.left.get_bottom() + DOWN * 0.1, wall.get_top() + LEFT * 3.6, color=PRIMARY, stroke_width=4),
                    Line(f.right.get_bottom() + DOWN * 0.1, wall.get_top() + RIGHT * 3.6, color=PRIMARY, stroke_width=4))
        f.ll.set_color(PRIMARY)
        f.rl.set_color(PRIMARY)
        with self.voiceover(text=N("s09.b4")) as tr:
            self.play(FadeIn(f), run_time=0.9)
            wait_until(self, tr, "wall")
            self.play(Create(wl), FadeIn(wall, shift=UP * 0.2), run_time=0.8)
            rest(self, tr)
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.6)


# ---------------------------------------------------------------------------
# s10 Ending
# ---------------------------------------------------------------------------


class S10Ending(VoiceoverScene):
    def construct(self):
        self.set_speech_service(get_speech_service())
        m = Tape(list("_1011_"), cell=0.72, size=36, head=2).move_to(LEFT * 4.0 + UP * 0.6)
        p = proof_card(size=30, dy=0.55, tags=False).move_to(RIGHT * 3.8 + UP * 0.6)
        arr = DoubleArrow(m.get_right() + RIGHT * 0.3, p.get_left() + LEFT * 0.3, color=MUTED, stroke_width=4)
        arr = DashedVMobject(arr, num_dashes=14)
        l1 = text("a proof checker is a machine", size=34, color=MUTED).move_to(UP * 2.8)
        l2 = text("halting is a sentence", size=34, color=MUTED).move_to(DOWN * 1.6)
        eqs = VGroup(text("a proof = a program", size=40, color=PRIMARY),
                     text("a statement = a type", size=40, color=PRIMARY)).arrange(RIGHT, buff=1.2).move_to(DOWN * 1.6)
        with self.voiceover(text=N("s10.b1")) as tr:
            self.play(FadeIn(m), FadeIn(p), run_time=0.8)
            self.play(Create(arr), FadeIn(l1), FadeIn(l2), run_time=0.8)
            wait_until(self, tr, "program")
            self.play(m.animate.shift(RIGHT * 1.6), p.animate.shift(LEFT * 1.4), FadeOut(arr),
                      FadeOut(l1), FadeOut(l2), run_time=1.0)
            self.play(FadeIn(eqs[0]), run_time=0.5)
            self.play(FadeIn(eqs[1]), run_time=0.5)
            rest(self, tr)
        solid = DoubleArrow(m.get_right() + RIGHT * 0.2, p.get_left() + LEFT * 0.2, color=PRIMARY, stroke_width=6)
        ch = text("the Curry\u2013Howard correspondence", size=44, color=PRIMARY, weight="BOLD").move_to(DOWN * 2.9)
        with self.voiceover(text=N("s10.b2")) as tr:
            self.play(GrowFromCenter(solid), run_time=0.6)
            wait_until(self, tr, "ch")
            self.play(FadeIn(ch, shift=UP * 0.2), run_time=0.8)
            rest(self, tr)
        self.wait(0.5)
        self.play(FadeOut(Group(*self.mobjects)), run_time=1.5)
        self.wait(0.5)


# ---------------------------------------------------------------------------
# Thumbnail
# ---------------------------------------------------------------------------


class Thumbnail(Scene):
    def construct(self):
        g = g_box("G has no proof.", size=48)
        dbox = mbox("D", color=SECONDARY, w=2.2, h=1.6, size=80)
        din = math(r"\langle D\rangle", size=64, color=SECONDARY).next_to(dbox, LEFT, 0.9)
        a_in = Arrow(din.get_right(), dbox.get_left(), buff=0.15, color=MUTED, stroke_width=5)
        back = CurvedArrow(dbox.get_bottom() + DOWN * 0.1, din.get_bottom() + DOWN * 0.15, angle=-PI / 2,
                           color=PRIMARY, stroke_width=6)
        d = VGroup(din, a_in, dbox, back)
        left = VGroup(g, d).arrange(DOWN, buff=1.2).move_to(LEFT * 3.4)
        t1 = text(GODEL, size=110, weight="BOLD", color=PRIMARY)
        t2 = math("=", size=130, color=FG)
        t3 = text("Turing", size=110, weight="BOLD", color=SECONDARY)
        words = VGroup(t1, t2, t3).arrange(DOWN, buff=0.3)
        words.scale(min(6.2 / words.height, 6.2 / words.width)).move_to(RIGHT * 3.6)
        self.add(left, words)
