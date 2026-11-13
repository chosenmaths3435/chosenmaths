"""The function no for-loop can compute: the Ackermann function."""

import sys

import numpy as np
from manim import *
from manim_voiceover import VoiceoverScene

from mathvid import layout  # noqa: F401  must come before scene code runs
from mathvid.anim import rest, rt, wait_until
from mathvid.code import CodePanel, mono
from mathvid.layout import FH, FW
from mathvid.orders import cross, tick
from mathvid.script import Script
from mathvid.style import (BAD, BG, FG, GOOD, MUTED, PRIMARY, SECONDARY, TERTIARY, math, text,
                           title_card)
from mathvid.voice import get_speech_service

N = Script(__file__)

TITLE = "The Ackermann function"
GODEL = "G\u00f6del"


def frac_time(tr, f):
    return rt(tr.duration * f)


def tag(s, size=30, color=MUTED, **kw):
    return text(s, size=size, color=color, **kw)


# ---------------------------------------------------------------------------
# The numbers. Everything on screen comes from here, not from typed constants.
# ---------------------------------------------------------------------------


def ack_small(m, n):
    """A(m, n) by the three rules, with an explicit stack. Only for small inputs."""
    st = [m]
    while st:
        m = st.pop()
        if m == 0:
            n += 1
        elif n == 0:
            st.append(m - 1)
            n = 1
        else:
            st += [m - 1, m]
            n -= 1
    return n


def ack_trace(m, n):
    """States (stack, n) of the stack program computing A(m, n)."""
    st = [m]
    out = [(list(st), n)]
    while st:
        mm = st.pop()
        if mm == 0:
            n += 1
        elif n == 0:
            st.append(mm - 1)
            n = 1
        else:
            st += [mm - 1, mm]
            n -= 1
        out.append((list(st), n))
    return out


def row3(n):
    return 2 ** (n + 3) - 3


# Closed forms, checked against the rules where that is feasible.
for _m, _f in ((0, lambda n: n + 1), (1, lambda n: n + 2), (2, lambda n: 2 * n + 3), (3, row3)):
    for _n in range(6):
        assert ack_small(_m, _n) == _f(_n)
A40 = ack_small(4, 0)            # = A(3, 1)
A41 = row3(A40)                  # A(4, 1) = A(3, A(4, 0))
assert A40 == 13 and A41 == 65533
_old = sys.get_int_max_str_digits()
sys.set_int_max_str_digits(0)
A42_DIGITS = len(str(2 ** (A41 + 3) - 3))   # A(4, 2) = A(3, A(4, 1)) = 2^65536 - 3
sys.set_int_max_str_digits(_old)
assert A42_DIGITS == 19729
DIAG = [ack_small(k, k) for k in range(4)]  # 1, 3, 7, 61


def cell_tex(m, n):
    """TeX for the table entry A(m, n)."""
    if m <= 3:
        return str(ack_small(m, n))
    if m == 4:
        if n == 0:
            return str(A40)
        if n == 1:
            return str(A41)
        if n == 2:
            return r"2^{%d}\!-\!3" % (A41 + 3)
        return r"\text{huge}"
    if n == 0:
        return str(A41)  # A(5, 0) = A(4, 1)
    return "?"


def fmt_int(k):
    return f"{k:,}"


# ---------------------------------------------------------------------------
# Shared builders (also used by shorts.py)
# ---------------------------------------------------------------------------

LADDER_ROWS = [
    (r"3 + 4 = 3 + 1 + 1 + 1 + 1", "add"),
    (r"3 \times 4 = 3 + 3 + 3 + 3", "mult"),
    (r"3^4 = 3 \times 3 \times 3 \times 3", "pow"),
]


class Ladder(VGroup):
    """Two rails and rungs, built from the bottom. rung(i) and label(i) give the parts."""

    def __init__(self, n_rungs=8, gap=1.0, width=1.4, size=36, label_buff=0.45):
        super().__init__()
        h = gap * (n_rungs + 0.5)
        self.rails = VGroup(Line(ORIGIN, UP * h, color=MUTED, stroke_width=5),
                            Line(ORIGIN, UP * h, color=MUTED, stroke_width=5).shift(RIGHT * width))
        self.rungs = VGroup(*[Line(UP * gap * (i + 0.5), UP * gap * (i + 0.5) + RIGHT * width,
                                   color=FG, stroke_width=6) for i in range(n_rungs)])
        self.labels = VGroup()
        for i in range(n_rungs):
            if i < len(LADDER_ROWS):
                lab = math(LADDER_ROWS[i][0], size=size)
            else:
                lab = math("?", size=size + 6, color=MUTED)
            lab.next_to(self.rungs[i], RIGHT, label_buff)
            self.labels.add(lab)
        n_known = len(LADDER_ROWS)
        for i in range(n_known, n_rungs):
            k = (i - n_known + 1) / (n_rungs - n_known + 1)
            op = max(0.15, 1 - 0.85 * k)
            self.rungs[i].set_stroke(opacity=op)
            self.labels[i].set_opacity(op)
        self.add(self.rails, self.rungs, self.labels)


def rules_block(size=40, numbered=True):
    """The three rules, aligned at the equals sign. Returns a group with .rows and .nums."""
    srcs = [("A(0, n)", "= n + 1"), ("A(m + 1, 0)", "= A(m, 1)"),
            ("A(m + 1, n + 1)", "= A(m, A(m + 1, n))")]
    rows = VGroup()
    for lhs, rhs in srcs:
        rows.add(math(lhs, rhs, size=size))
    rows.arrange(DOWN, buff=0.35)
    for r in rows[1:]:
        r.shift(RIGHT * (rows[0][1].get_left()[0] - r[1].get_left()[0]))
    g = VGroup(rows)
    g.rows = rows
    g.nums = VGroup()
    if numbered:
        for i, r in enumerate(rows):
            num = tag(f"rule {i + 1}", size=int(size * 0.7)).next_to(rows, LEFT, 0.5).match_y(r)
            g.nums.add(num)
        g.add(g.nums)
    return g


class AckTable(VGroup):
    """Rows m, columns n of A(m, n). cell(m, n) gives an entry; right labels optional."""

    def __init__(self, rows=5, cols=6, size=34, hsize=None, col_pad=0.35, row_h=0.72,
                 labels=None, label_size=None, max_col_w=None):
        super().__init__()
        hsize = hsize or int(size * 0.85)
        label_size = label_size or int(size * 0.85)
        self.nr, self.nc = rows, cols
        self.cells = [[math(cell_tex(m, n), size=size) for n in range(cols)] for m in range(rows)]
        for m in range(rows):
            for n in range(cols):
                if max_col_w and self.cells[m][n].width > max_col_w:
                    self.cells[m][n].scale_to_fit_width(max_col_w)
        col_w = [max(self.cells[m][n].width for m in range(rows)) + col_pad for n in range(cols)]
        col_w = [max(w, 0.9) for w in col_w]
        hdr_w = 1.25
        xs = []
        x = hdr_w
        for w in col_w:
            xs.append(x + w / 2)
            x += w
        self.total_w = x
        self.col_hdr = VGroup(*[math(f"n={n}", size=hsize, color=MUTED).move_to([xs[n], 0, 0])
                                for n in range(cols)])
        self.row_hdr = VGroup(*[math(f"m={m}", size=hsize, color=MUTED).move_to([hdr_w / 2, -(m + 1) * row_h, 0])
                                for m in range(rows)])
        for m in range(rows):
            for n in range(cols):
                self.cells[m][n].move_to([xs[n], -(m + 1) * row_h, 0])
        self.grid = VGroup(
            Line([hdr_w - 0.1, -row_h / 2, 0], [x, -row_h / 2, 0], color=MUTED, stroke_width=2),
            Line([hdr_w - 0.05, row_h / 2 - 0.1, 0], [hdr_w - 0.05, -(rows + 0.5) * row_h, 0], color=MUTED,
                 stroke_width=2))
        self.row_groups = VGroup(*[VGroup(*self.cells[m]) for m in range(rows)])
        self.add(self.grid, self.col_hdr, self.row_hdr, self.row_groups)
        self.labels = VGroup()
        if labels:
            for m, s in enumerate(labels[:rows]):
                lab = tag(s, size=label_size, color=PRIMARY if m else MUTED)
                lab.move_to([x + 0.4, -(m + 1) * row_h, 0], aligned_edge=LEFT)
                self.labels.add(lab)
            self.add(self.labels)
        self.row_h = row_h
        self.xs = xs

    def cell(self, m, n):
        return self.cells[m][n]

    def row(self, m):
        return self.row_groups[m]


ROW_LABELS = ["counting", "adds", "roughly doubles", "powers of 2", "towers of 2s"]


def for_loop_panel(size=34):
    return CodePanel(["repeat n times:", "    ..."], size=size)


def nested_loops(depth=3, size=30, labels=None, core="x = x + 1", colors=None, pad=0.4):
    """Concentric boxes: a core statement wrapped by `depth` loops, each with a header."""
    core_m = mono(core, size)
    g = VGroup(core_m)
    boxes = VGroup()
    heads = VGroup()
    inner = core_m
    colors = colors or [SECONDARY, TERTIARY, PRIMARY, GOOD]
    for i in range(depth):
        head = mono("repeat %s times:" % ("b" if labels else "k"), size, colors[i % len(colors)])
        head.next_to(inner, UP, 0.22).align_to(inner, LEFT).shift(LEFT * 0.0)
        content = VGroup(head, inner)
        box = SurroundingRectangle(content, buff=pad, corner_radius=0.12, color=colors[i % len(colors)],
                                   stroke_width=3)
        inner_shift = RIGHT * 0.0
        heads.add(head)
        boxes.add(box)
        g.add(head, box)
        inner = VGroup(content, box)
    out = VGroup(*g)
    out.core, out.boxes, out.heads = core_m, boxes, heads
    if labels:
        out.labels = VGroup()
        for i, s in enumerate(labels):
            lab = tag(s, size=int(size * 0.95), color=colors[i % len(colors)])
            lab.next_to(boxes[i], RIGHT, 0.3).align_to(boxes[i], UP).shift(DOWN * 0.1)
            out.labels.add(lab)
    return out


def build_chain(size=26, gap=0.9):
    """add, mult and pow as bounded-loop programs, each using the one before."""
    srcs = [
        ["add(a, b):", "  repeat b times:", "    a = a + 1", "  return a"],
        ["mult(a, b):", "  x = 0", "  repeat b times:", "    x = add(x, a)", "  return x"],
        ["pow(a, b):", "  x = 1", "  repeat b times:", "    x = mult(x, a)", "  return x"],
    ]
    panels = VGroup(*[CodePanel(s_, size=size) for s_ in srcs]).arrange(RIGHT, buff=gap, aligned_edge=UP)
    names = VGroup(*[tag(n_, size=30, color=PRIMARY).next_to(p_, DOWN, 0.3)
                     for n_, p_ in zip(("addition", "multiplication", "powers"), panels)])
    arrows = VGroup(*[Arrow(panels[i].get_right(), panels[i + 1].get_left(), buff=0.1, color=MUTED,
                            stroke_width=4, max_tip_length_to_length_ratio=0.3) for i in range(2)])
    g = VGroup(panels, names, arrows)
    g.panels, g.names, g.arrows = panels, names, arrows
    g.scale_to_fit_width(min(g.width, FW - 0.8))
    return g


def stack_program(size=26):
    return CodePanel([
        "stack = [m]",
        "while stack:",
        "    m = stack.pop()",
        "    if m == 0: n = n + 1",
        "    elif n == 0: stack += [m - 1]; n = 1",
        "    else: stack += [m - 1, m]; n = n - 1",
        "return n",
    ], size=size)


class Dial(VGroup):
    """A labelled counter box whose number follows a ValueTracker."""

    def __init__(self, label, value=0, color=FG, w=2.4, h=1.6, size=64):
        super().__init__()
        self.tr = ValueTracker(value)
        self.box = RoundedRectangle(corner_radius=0.2, width=w, height=h, color=color, stroke_width=4)
        self.box.set_fill("#1C1F26", 1)
        self.lab = math(label, size=int(size * 0.7), color=color).next_to(self.box, UP, 0.2)
        self.num = always_redraw(lambda: Integer(int(round(self.tr.get_value())), font_size=size,
                                                 color=FG).move_to(self.box))
        self.add(self.box, self.lab, self.num)


def dial_pair(size=64, gap=1.0):
    dm = Dial("m", 2, color=PRIMARY, size=size)
    dn = Dial("n", 3, color=SECONDARY, size=size)
    VGroup(dm, dn).arrange(RIGHT, buff=gap)
    return dm, dn


def run_dials(scene, dm, dn, total, script=None):
    """Count the n dial down; when it hits 0 drop m and jump n. Takes about `total` s."""
    script = script or [(2, 3), (1, 61), (0, 9)]
    steps = len(script)
    per = total / steps
    for i, (m, start) in enumerate(script):
        if i:
            scene.play(dm.tr.animate.set_value(m), dn.tr.animate.set_value(start),
                       Flash(dm.box, color=PRIMARY, line_length=0.25), run_time=rt(min(0.8, per * 0.3)))
        scene.play(dn.tr.animate.set_value(0), run_time=rt(per * (0.7 if i else 0.95)), rate_func=linear)


def note_card(lines, size=34, w=None):
    t = VGroup(*[text(s, size=size, color=FG, slant=ITALIC) for s in lines]).arrange(DOWN, buff=0.2,
                                                                                       aligned_edge=LEFT)
    card = RoundedRectangle(corner_radius=0.12, width=(w or t.width + 0.9), height=t.height + 0.8,
                            color=PRIMARY, stroke_width=3).set_fill("#232018", 1)
    t.move_to(card)
    g = VGroup(card, t)
    g.rotate(-2 * DEGREES)
    return g


def func_loop_panel(size=30):
    return CodePanel(["f = add_one", "repeat m times:", "    f = repeat_it(f)", "return f(n)"], size=size)


DIAG_VALUES = [[3, 1, 4, 1], [0, 2, 7, 5], [6, 6, 1, 8], [2, 9, 0, 3]]


class DiagTable(VGroup):
    """Programs P1..Pk by inputs 1..k, plus a D row of diagonal + 1."""

    def __init__(self, k=4, size=34, cw=1.05, rh=0.75, prog_label="P", show_dots=True):
        super().__init__()
        self.k = k
        self.cols = VGroup(*[math(str(j + 1), size=size, color=MUTED).move_to([cw * (j + 1), 0, 0])
                             for j in range(k)])
        self.inp = tag("input", size=int(size * 0.8)).next_to(self.cols, UP, 0.2)
        self.rows = VGroup()
        self.vals = []
        for i in range(k):
            lab = math(r"%s_{%d}" % (prog_label, i + 1), size=size, color=SECONDARY).move_to([0, -rh * (i + 1), 0])
            vs = [math(str(DIAG_VALUES[i][j]), size=size).move_to([cw * (j + 1), -rh * (i + 1), 0])
                  for j in range(k)]
            self.vals.append(vs)
            self.rows.add(VGroup(lab, *vs))
        self.add(self.cols, self.inp, self.rows)
        if show_dots:
            self.vdots = math(r"\vdots", size=size, color=MUTED).move_to([0, -rh * (k + 0.85), 0])
            self.hdots = math(r"\cdots", size=size, color=MUTED).move_to([cw * (k + 1), -rh * 1, 0])
            self.add(self.vdots, self.hdots)
        self.diag = VGroup(*[SurroundingRectangle(self.vals[i][i], buff=0.12, color=PRIMARY, stroke_width=3)
                             for i in range(k)])
        y_d = -rh * (k + 1.9)
        self.d_lab = math("D", size=size, color=PRIMARY).move_to([0, y_d, 0])
        self.d_vals = VGroup(*[math(str(DIAG_VALUES[j][j] + 1), size=size, color=PRIMARY).move_to([cw * (j + 1), y_d, 0])
                               for j in range(k)])
        self.d_row = VGroup(self.d_lab, self.d_vals)
        self.neq = VGroup(*[math(r"\neq", size=int(size * 1.1), color=BAD).rotate(PI / 2).move_to(
            [cw * (j + 1), y_d + rh * 0.62, 0]) for j in range(k)])
        self.add(self.diag, self.d_row, self.neq)
        self.rh, self.cw = rh, cw

    def base(self):
        parts = [self.cols, self.inp, self.rows]
        if hasattr(self, "vdots"):
            parts += [self.vdots, self.hdots]
        return VGroup(*parts)


def halting_inset(scale=1.0):
    box = RoundedRectangle(corner_radius=0.15, width=4.6, height=2.0, color=SECONDARY, stroke_width=3)
    prog = CodePanel(["while ...:", "    ..."], size=22).scale(0.9)
    q = text("halts?", size=34, color=PRIMARY)
    inner = VGroup(prog, q).arrange(RIGHT, buff=0.3).move_to(box)
    cap = tag("the halting problem", size=26).next_to(box, DOWN, 0.15)
    x = cross(q.get_center(), s=0.3)
    return VGroup(box, inner, cap, x).scale(scale)


def tower(height, size=60, color=PRIMARY, minus3=True):
    """2^2^...^2 (height twos), built from nested exponents."""
    s = "2"
    for _ in range(height - 1):
        s = "2^{" + s + "}"
    if minus3:
        s += r"\,-\,3"
    return math(s, size=size, color=color)


# ---------------------------------------------------------------------------
# s01 Hook
# ---------------------------------------------------------------------------


class S01Hook(VoiceoverScene):
    def construct(self):
        self.set_speech_service(get_speech_service())
        lad = Ladder(n_rungs=7, gap=0.85, size=46)
        lad.move_to(ORIGIN).shift(LEFT * 2.2)
        with self.voiceover(text=N("s01.b1")) as tr:
            self.play(Create(lad.rails), run_time=0.6)
            for i, mark in enumerate(("add", "mult", "pow")):
                wait_until(self, tr, mark)
                self.play(Create(lad.rungs[i]), FadeIn(lad.labels[i], shift=RIGHT * 0.2), run_time=0.6)
            rest(self, tr)

        with self.voiceover(text=N("s01.b2")) as tr:
            wait_until(self, tr, "keep")
            extra = list(range(3, 7))
            self.play(LaggedStart(*[AnimationGroup(Create(lad.rungs[i]), FadeIn(lad.labels[i]))
                                    for i in extra], lag_ratio=0.35),
                      run_time=rt(min(2.0, tr.get_remaining_duration())))
            rest(self, tr)

        a42 = math("A(4, 2)", size=60, color=PRIMARY)
        cnt = ValueTracker(0)
        digits = always_redraw(lambda: VGroup(
            Text(fmt_int(int(round(cnt.get_value()))), font="Source Sans 3", font_size=52, color=FG),
            text("digits", size=40, color=MUTED)).arrange(RIGHT, buff=0.25))
        a43 = math("A(4, 3)", size=60, color=PRIMARY)
        atoms = text("more digits than atoms in the universe", size=38, color=BAD)
        with self.voiceover(text=N("s01.b3")) as tr:
            self.play(lad.animate.scale(0.6).to_edge(LEFT, buff=0.9), run_time=0.9)
            a42.move_to(RIGHT * 2.0 + UP * 1.8)
            digits.next_to(a42, DOWN, 0.4)
            self.play(FadeIn(a42, shift=UP * 0.2), run_time=0.6)
            wait_until(self, tr, "digits")
            self.add(digits)
            self.play(cnt.animate.set_value(A42_DIGITS), run_time=1.6, rate_func=rush_from)
            a43.next_to(digits, DOWN, 0.9).match_x(a42)
            atoms.next_to(a43, DOWN, 0.35).match_x(a42)
            wait_until(self, tr, "atoms")
            self.play(FadeIn(a43, shift=UP * 0.2), run_time=0.5)
            self.play(FadeIn(atoms), run_time=0.6)
            rest(self, tr)

        fl = for_loop_panel(size=40).move_to(RIGHT * 2.0)
        with self.voiceover(text=N("s01.b4")) as tr:
            self.remove(digits)
            self.play(FadeOut(VGroup(a42, a43, atoms, digits)), run_time=0.5)
            self.play(FadeIn(fl, shift=UP * 0.2), run_time=0.6)
            wait_until(self, tr, "loop")
            x = cross(fl.get_center(), s=0.9, width=10)
            self.play(Create(x), run_time=0.6)
            rest(self, tr)
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.5)
        title_card(self, TITLE)


# ---------------------------------------------------------------------------
# s02 Bounded loops
# ---------------------------------------------------------------------------


class S02Loops(VoiceoverScene):
    def construct(self):
        self.set_speech_service(get_speech_service())
        p = CodePanel(["repeat n times:", "    x = x + 1"], size=42).move_to(UP * 0.6)
        fixed = tag("n is fixed before the loop starts", size=36, color=PRIMARY).next_to(p, DOWN, 0.6)
        with self.voiceover(text=N("s02.b1")) as tr:
            self.play(FadeIn(p, shift=UP * 0.2), run_time=0.7)
            wait_until(self, tr, "fixed")
            self.play(FadeIn(fixed, shift=UP * 0.15), Indicate(p.part(0, "n"), color=PRIMARY), run_time=0.8)
            rest(self, tr)

        w = CodePanel(["while x != 0:", "    ..."], size=34)
        r = CodePanel(["def f(n):", "    return f(n - 1)"], size=34)
        bad = VGroup(w, r).arrange(RIGHT, buff=1.2).move_to(DOWN * 0.4)
        wl = tag("no while-loops", size=30, color=BAD).next_to(w, DOWN, 0.3)
        rl = tag("no calling itself", size=30, color=BAD).next_to(r, DOWN, 0.3)
        with self.voiceover(text=N("s02.b2")) as tr:
            self.play(VGroup(p, fixed).animate.scale(0.75).to_edge(UP, buff=0.5), run_time=0.6)
            self.play(FadeIn(w), run_time=0.5)
            self.play(Create(cross(w.get_center(), s=0.55)), FadeIn(wl), run_time=0.5)
            self.wait(frac_time(tr, 0.1))
            self.play(FadeIn(r), run_time=0.5)
            self.play(Create(cross(r.get_center(), s=0.55)), FadeIn(rl), run_time=0.5)
            rest(self, tr)

        panels = build_chain(size=32)
        allg = panels.move_to(DOWN * 0.2)
        plus1 = math("x + 1", size=56, color=PRIMARY).move_to(panels.panels[0])
        with self.voiceover(text=N("s02.b3")) as tr:
            self.play(FadeOut(Group(*self.mobjects)), run_time=0.5)
            self.play(FadeIn(plus1, scale=1.2), run_time=0.5)
            for i, mark in enumerate(("add", "mult", "pow")):
                wait_until(self, tr, mark)
                anims = [FadeIn(panels.panels[i], shift=UP * 0.2), FadeIn(panels.names[i])]
                if i == 0:
                    anims = [ReplacementTransform(plus1, panels.panels[i]), FadeIn(panels.names[i])]
                if i:
                    anims.append(GrowArrow(panels.arrows[i - 1]))
                self.play(*anims, run_time=0.7)
            rest(self, tr)

        box = RoundedRectangle(corner_radius=0.3, width=10.5, height=4.0, color=SECONDARY, stroke_width=4)
        box.move_to(DOWN * 0.1)
        btitle = text("bounded loops", size=40, color=SECONDARY).next_to(box, UP, 0.2).align_to(box, LEFT)
        ex_src = [r"n!", r"\text{is } n \text{ prime?}", r"a < b", r"\text{the } n\text{-th prime}", r"\gcd(a, b)",
                  r"a^b"]
        exs = VGroup(*[math(s, size=46) for s in ex_src]).arrange_in_grid(rows=2, buff=(1.0, 0.8)).move_to(box)
        with self.voiceover(text=N("s02.b4")) as tr:
            self.play(FadeOut(allg), run_time=0.4)
            self.play(Create(box), FadeIn(btitle), run_time=0.7)
            self.play(LaggedStart(*[FadeIn(e, scale=0.8) for e in exs], lag_ratio=0.3),
                      run_time=rt(min(2.5, tr.time_until_bookmark("box") - 0.2)))
            wait_until(self, tr, "box")
            self.play(Indicate(box, color=SECONDARY, scale_factor=1.02), run_time=0.8)
            rest(self, tr)

        stops = VGroup(tick(at=ORIGIN, s=1.3), text("every program stops", size=40, color=GOOD)).arrange(RIGHT, 0.3)
        stops.next_to(box, DOWN, 0.35)
        pr = text("primitive recursive", size=40, color=PRIMARY).next_to(box, UP, 0.2).align_to(box, RIGHT)
        with self.voiceover(text=N("s02.b5")) as tr:
            wait_until(self, tr, "stops")
            self.play(FadeIn(stops, shift=UP * 0.15), run_time=0.6)
            self.wait(frac_time(tr, 0.15))
            self.play(FadeIn(pr), run_time=0.6)
            rest(self, tr)

        q = text("everything a computer can compute\nthat always gives an answer?", size=34, color=FG,
                 line_spacing=0.8)
        with self.voiceover(text=N("s02.b6")) as tr:
            self.play(FadeOut(stops), VGroup(box, btitle, exs, pr).animate.scale(0.55).to_edge(LEFT, buff=0.5),
                      run_time=0.8)
            q.to_edge(RIGHT, buff=0.5).shift(DOWN * 0.4)
            qm = text("?", size=120, color=PRIMARY).next_to(q, UP, 0.3)
            self.play(FadeIn(q), FadeIn(qm, scale=1.3), run_time=0.8)
            rest(self, tr)
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.5)


# ---------------------------------------------------------------------------
# s03 The Ackermann function
# ---------------------------------------------------------------------------


class S03Ackermann(VoiceoverScene):
    def construct(self):
        self.set_speech_service(get_speech_service())
        rb = rules_block(size=50).move_to(DOWN * 0.4)
        amn = math("A(m, n)", size=72, color=PRIMARY).move_to(UP * 0.4)
        with self.voiceover(text=N("s03.b1")) as tr:
            self.play(FadeIn(amn, scale=1.1), run_time=0.7)
            wait_until(self, tr, "rules")
            self.play(amn.animate.scale(0.7).next_to(rb, UP, 0.7), run_time=0.5)
            self.play(LaggedStart(*[FadeIn(VGroup(rb.nums[i], rb.rows[i]), shift=RIGHT * 0.2) for i in range(3)],
                                  lag_ratio=0.4), run_time=1.6)
            rest(self, tr)

        hl = SurroundingRectangle(rb.rows[0], buff=0.15, color=PRIMARY, corner_radius=0.08)
        cnt = tag("just counting", size=34, color=PRIMARY).next_to(hl, RIGHT, 0.4)
        with self.voiceover(text=N("s03.b2")) as tr:
            wait_until(self, tr, "r1")
            self.play(Create(hl), FadeIn(cnt), run_time=0.7)
            rest(self, tr)

        small = rules_block(size=34).to_corner(UL, buff=0.45)
        lines_src = [
            (r"A(1, 1)", r"= A(0, A(1, 0))", "rule 3"),
            (None, r"= A(0, A(0, 1))", "rule 2"),
            (None, r"= A(0, 2)", "rule 1"),
            (None, r"= 3", "rule 1"),
        ]
        rows = VGroup()
        for lhs, rhs, rl in lines_src:
            l = math(lhs or "A(1, 1)", size=48)
            rr = math(rhs, size=48)
            if lhs is None:
                l.set_opacity(0)
            row = VGroup(l, rr).arrange(RIGHT, buff=0.2)
            rows.add(row)
        rows.arrange(DOWN, buff=0.35, aligned_edge=LEFT)
        for r in rows[1:]:
            r.shift(RIGHT * (rows[0][1].get_left()[0] - r[1].get_left()[0]))
        rows.move_to(DOWN * 0.7 + RIGHT * 1.0)
        rtags = VGroup(*[tag(lines_src[i][2], size=28, color=SECONDARY).next_to(rows[i], RIGHT, 0.6)
                         for i in range(4)])
        rtags.align_to(rtags[0], LEFT)
        for t_ in rtags:
            t_.set_x(rows.get_right()[0] + 1.2, direction=LEFT)
        with self.voiceover(text=N("s03.b3")) as tr:
            self.play(FadeOut(hl), FadeOut(cnt), FadeOut(amn), ReplacementTransform(rb, small), run_time=0.8)
            self.play(FadeIn(rows[0][0]), run_time=0.4)
            wait_until(self, tr, "r3")
            self.play(FadeIn(rows[0][1]), FadeIn(rtags[0]), run_time=0.6)
            wait_until(self, tr, "r2")
            self.play(FadeIn(rows[1]), FadeIn(rtags[1]), run_time=0.6)
            self.wait(frac_time(tr, 0.06))
            self.play(FadeIn(rows[2]), FadeIn(rtags[2]), run_time=0.6)
            wait_until(self, tr, "three")
            self.play(FadeIn(rows[3]), FadeIn(rtags[3]), run_time=0.5)
            self.play(Circumscribe(rows[3][1], color=PRIMARY), run_time=0.8)
            rest(self, tr)

        tbl = AckTable(rows=5, cols=6, size=36, labels=ROW_LABELS, label_size=30, max_col_w=1.9)
        tbl.move_to(DOWN * 0.3)
        with self.voiceover(text=N("s03.b4")) as tr:
            self.play(FadeOut(VGroup(rows, rtags, small)), run_time=0.5)
            self.play(FadeIn(tbl.grid), FadeIn(tbl.col_hdr), FadeIn(tbl.row_hdr), run_time=0.6)
            self.play(LaggedStart(*[FadeIn(c) for c in tbl.row(0)], lag_ratio=0.15), FadeIn(tbl.labels[0]),
                      run_time=0.9)
            wait_until(self, tr, "row")
            # row 1: entry n is row 0 applied to entry n - 1 (entry 0 is row 0 applied to 1)
            per = rt(min(0.9, (tr.get_remaining_duration() - 0.6) / 6))
            for n in range(6):
                src_col = 1 if n == 0 else ack_small(1, n - 1)
                anims = [FadeIn(tbl.cell(1, n), scale=1.2)]
                arr = None
                if src_col < 6:
                    arr = CurvedArrow(tbl.cell(0, src_col).get_bottom() + DOWN * 0.05,
                                      tbl.cell(1, n).get_top() + UP * 0.05, angle=-0.6, color=SECONDARY,
                                      stroke_width=3, tip_length=0.15)
                    anims.append(Create(arr))
                self.play(*anims, run_time=per)
                if arr:
                    self.play(FadeOut(arr), run_time=rt(per * 0.3))
            self.play(FadeIn(tbl.labels[1]), run_time=0.4)
            rest(self, tr)

        with self.voiceover(text=N("s03.b5")) as tr:
            self.play(Indicate(tbl.labels[1], color=PRIMARY), run_time=0.6)
            for m, mark in ((2, "r2"), (3, "r3"), (4, "r4")):
                wait_until(self, tr, mark)
                self.play(LaggedStart(*[FadeIn(c) for c in tbl.row(m)], lag_ratio=0.12), FadeIn(tbl.labels[m]),
                          run_time=0.9)
            rest(self, tr)

        tw = tower(5, size=80).move_to(UP * 0.6)
        dg = text(f"{fmt_int(A42_DIGITS)} digits", size=44, color=FG).next_to(tw, DOWN, 0.6)
        eq = math("A(4, 2) =", size=56).next_to(tw, LEFT, 0.4)
        tw6 = tower(6, size=80).move_to(tw)
        eq6 = math("A(4, 3) =", size=56).next_to(tw6, LEFT, 0.4)
        taller = tag("one taller", size=36, color=PRIMARY).next_to(tw6, RIGHT, 0.5)
        with self.voiceover(text=N("s03.b6")) as tr:
            self.play(FadeOut(tbl), run_time=0.5)
            self.play(FadeIn(eq), Write(tw), run_time=1.2)
            wait_until(self, tr, "twenty")
            self.play(FadeIn(dg, shift=UP * 0.15), run_time=0.6)
            self.wait(frac_time(tr, 0.15))
            self.play(FadeOut(dg), ReplacementTransform(tw, tw6), ReplacementTransform(eq, eq6),
                      FadeIn(taller), run_time=1.0)
            rest(self, tr)

        tbl6 = AckTable(rows=6, cols=6, size=36, labels=ROW_LABELS + ["towers of towers"], label_size=30,
                        max_col_w=1.9)
        tbl6.move_to(DOWN * 0.2)
        tbl6.scale_to_fit_height(min(tbl6.height, FH - 1.0))
        with self.voiceover(text=N("s03.b7")) as tr:
            self.play(FadeOut(VGroup(tw6, eq6, taller)), run_time=0.5)
            self.play(FadeIn(VGroup(tbl6.grid, tbl6.col_hdr, *tbl6.row_hdr[:5], *[tbl6.row(m) for m in range(5)],
                                    *tbl6.labels[:5])), run_time=0.6)
            self.play(FadeIn(tbl6.row_hdr[5]), LaggedStart(*[FadeIn(c) for c in tbl6.row(5)], lag_ratio=0.15),
                      FadeIn(tbl6.labels[5]), run_time=1.2)
            self.play(Indicate(tbl6.cell(5, 0), color=PRIMARY), run_time=0.8)
            rest(self, tr)
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.5)


# ---------------------------------------------------------------------------
# s04 Why no loop keeps up
# ---------------------------------------------------------------------------


def row_column(n=6, size=34, gap=0.75):
    labs = ["row 0: counting", "row 1: adds", "row 2: doubles", "row 3: powers", "row 4: towers",
            "row 5: ..."]
    return VGroup(*[tag(labs[i], size=size, color=FG if i else MUTED) for i in range(n)]).arrange(
        DOWN, buff=gap - 0.45, aligned_edge=LEFT)


def growth_plot(w=8.0, h=4.6, m_label="row m", p_label="your loop program"):
    ax = Axes(x_range=[0, 6, 1], y_range=[0, 10, 2], x_length=w, y_length=h,
              axis_config={"color": MUTED, "stroke_width": 3, "include_ticks": False}, tips=False)
    xl = tag("input n", size=28).next_to(ax.x_axis, DOWN, 0.2).align_to(ax.x_axis, RIGHT)
    yl = tag("output", size=28).next_to(ax.y_axis, UP, 0.15)
    f_row = lambda x: 1.3 + 0.2 * np.exp(0.75 * x)
    f_prog = lambda x: 0.25 + 0.55 * x + 0.35 * np.sin(2.2 * x) + 0.05 * np.exp(0.7 * x)
    xs_ = np.linspace(0, 5.9, 300)
    assert all(f_row(v) > f_prog(v) + 0.3 for v in xs_)
    x_top = float(np.log((9.6 - 1.3) / 0.2) / 0.75)
    rowm = ax.plot(f_row, x_range=[0, min(5.9, x_top)], color=PRIMARY, stroke_width=5)
    prog = ax.plot(f_prog, x_range=[0, 5.9], color=SECONDARY, stroke_width=5)
    rl = tag(m_label, size=30, color=PRIMARY).next_to(ax.c2p(min(5.9, x_top), 9.4), LEFT, 0.3)
    pl = tag(p_label, size=30, color=SECONDARY).move_to(ax.c2p(4.9, f_prog(4.9) - 1.6))
    g = VGroup(ax, xl, yl, rowm, prog, rl, pl)
    g.ax, g.rowm, g.prog, g.rl, g.pl = ax, rowm, prog, rl, pl
    return g


class S04NoLoop(VoiceoverScene):
    def construct(self):
        self.set_speech_service(get_speech_service())
        nest = nested_loops(3, size=28, core="...")
        nest.move_to(LEFT * 3.6)
        rc = row_column(5, size=34).move_to(RIGHT * 3.3)
        with self.voiceover(text=N("s04.b1")) as tr:
            self.play(FadeIn(nest.core), *[Create(b) for b in nest.boxes], *[FadeIn(h) for h in nest.heads],
                      run_time=1.0)
            self.play(FadeIn(rc), run_time=0.6)
            wait_until(self, tr, "climb")
            per = rt(min(0.9, (tr.get_remaining_duration() - 0.3) / 3))
            for i in range(3):
                ln = DashedLine(nest.boxes[i].get_right(), rc[i + 1].get_left() + LEFT * 0.1,
                                color=nest.boxes[i].get_color(), stroke_width=3)
                self.play(Create(ln), Indicate(rc[i + 1], color=nest.boxes[i].get_color(), scale_factor=1.05),
                          run_time=per)
            rest(self, tr)

        gp = growth_plot().move_to(DOWN * 0.3)
        beat = text("every loop program is beaten by some row m", size=36, color=PRIMARY).to_edge(UP, buff=0.5)
        with self.voiceover(text=N("s04.b2")) as tr:
            self.play(FadeOut(Group(*self.mobjects)), run_time=0.5)
            self.play(Create(gp.ax), FadeIn(gp[1]), FadeIn(gp[2]), run_time=0.7)
            self.play(Create(gp.prog), FadeIn(gp.pl), run_time=1.2)
            wait_until(self, tr, "beat")
            self.play(Create(gp.rowm), FadeIn(gp.rl), run_time=1.2)
            self.play(FadeIn(beat), run_time=0.6)
            rest(self, tr)

        tbl = AckTable(rows=5, cols=5, size=36, max_col_w=1.9).move_to(DOWN * 0.1 + LEFT * 1.6)
        diag_boxes = VGroup(*[SurroundingRectangle(tbl.cell(k, k), buff=0.1, color=PRIMARY, stroke_width=4)
                              for k in range(5)])
        dlab = math(r"D(n) = A(n, n)", size=46, color=PRIMARY).next_to(tbl, RIGHT, 0.7).shift(UP * 0.5)
        with self.voiceover(text=N("s04.b3")) as tr:
            self.play(FadeOut(Group(*self.mobjects)), run_time=0.5)
            self.play(FadeIn(tbl), run_time=0.7)
            wait_until(self, tr, "diag")
            for k in range(5):
                self.play(Create(diag_boxes[k]), run_time=rt(min(0.5, tr.get_remaining_duration() / 7)))
            self.play(FadeIn(dlab, shift=LEFT * 0.2), run_time=0.6)
            rest(self, tr)

        pbox = VGroup(RoundedRectangle(corner_radius=0.15, width=6.4, height=1.3, color=SECONDARY, stroke_width=3),
                      text("loop program computing D", size=30, color=SECONDARY))
        pbox[1].move_to(pbox[0])
        pbox.move_to(UP * 2.6)
        l1 = math(r"D(n) < A(m, n)", r"\text{ for every } n", size=46).next_to(pbox, DOWN, 0.6)
        lt = math(r"D(m) < A(m, m)", size=50)
        rt_ = math(r"D(m) = A(m, m)", size=50)
        pair = VGroup(lt, rt_).arrange(RIGHT, buff=1.4).next_to(l1, DOWN, 0.8)
        with self.voiceover(text=N("s04.b4")) as tr:
            self.play(FadeOut(VGroup(tbl, diag_boxes, dlab)), run_time=0.5)
            self.play(FadeIn(pbox, shift=DOWN * 0.2), run_time=0.6)
            wait_until(self, tr, "m")
            self.play(FadeIn(l1), run_time=0.8)
            wait_until(self, tr, "plug")
            self.play(TransformFromCopy(l1[0], lt), run_time=0.8)
            self.wait(frac_time(tr, 0.08))
            self.play(FadeIn(rt_), run_time=0.6)
            self.play(Create(cross(pair.get_center(), s=0.5, width=8)), run_time=0.5)
            rest(self, tr)

        s1 = text("no loop program computes D", size=40, color=FG)
        s2 = VGroup(math(r"A", size=46, color=SECONDARY), math(r"(n, n)", size=46),
                    math(r"\;\to\;", size=46, color=MUTED), math("D(n)", size=46, color=PRIMARY)).arrange(RIGHT, 0.12)
        s3 = text("no loop program computes the Ackermann function", size=40, color=PRIMARY)
        col = VGroup(s1, s2, s3).arrange(DOWN, buff=0.7).move_to(ORIGIN)
        with self.voiceover(text=N("s04.b5")) as tr:
            self.play(FadeOut(Group(*self.mobjects)), run_time=0.5)
            self.play(FadeIn(s1), run_time=0.6)
            self.wait(frac_time(tr, 0.12))
            self.play(FadeIn(s2), run_time=0.7)
            wait_until(self, tr, "none")
            self.play(FadeIn(s3, shift=UP * 0.15), run_time=0.7)
            rest(self, tr)
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.5)


# ---------------------------------------------------------------------------
# s05 But it always stops
# ---------------------------------------------------------------------------


def stack_view(stack, n, size=34, cell=0.75):
    boxes = VGroup()
    for v in stack:
        b = VGroup(Square(cell, color=SECONDARY, stroke_width=3), math(str(v), size=size))
        b[1].move_to(b[0])
        boxes.add(b)
    if len(boxes):
        boxes.arrange(RIGHT, buff=0.08)
    lab = tag("stack", size=28)
    nn = math(f"n = {n}", size=size + 4, color=PRIMARY)
    g = VGroup(lab, boxes if len(boxes) else tag("(empty)", size=28), nn)
    g.arrange(RIGHT, buff=0.4)
    return g


def call_moves(rules, size=30):
    """Annotations under the rules: which number drops."""
    r2 = math(r"(m+1,\,0) \to (m,\,1)", size=size, color=FG)
    r3a = math(r"(m+1,\,n+1) \to (m+1,\,n)", size=size, color=FG)
    r3b = math(r"(m+1,\,n+1) \to (m,\,\ldots)", size=size, color=FG)
    t2 = tag("first drops", size=size - 2, color=PRIMARY)
    t3a = tag("first stays, second drops", size=size - 2, color=SECONDARY)
    t3b = tag("first drops", size=size - 2, color=PRIMARY)
    rows = VGroup(VGroup(r2, t2).arrange(RIGHT, 0.5), VGroup(r3a, t3a).arrange(RIGHT, 0.5),
                  VGroup(r3b, t3b).arrange(RIGHT, 0.5)).arrange(DOWN, buff=0.3, aligned_edge=LEFT)
    return rows


class S05Stops(VoiceoverScene):
    def construct(self):
        self.set_speech_service(get_speech_service())
        prog = stack_program(size=28).move_to(UP * 1.3)
        trace = ack_trace(2, 1)
        SV = DOWN * 2.2 + RIGHT * 0.8
        title = math("A(2, 1)", size=48, color=PRIMARY).move_to(DOWN * 2.2 + LEFT * 4.6)
        with self.voiceover(text=N("s05.b1")) as tr:
            wait_until(self, tr, "while")
            self.play(FadeIn(prog, shift=RIGHT * 0.2), run_time=0.7)
            self.play(FadeIn(title), run_time=0.4)
            sv = stack_view(*trace[0]).move_to(SV)
            self.play(FadeIn(sv), run_time=0.4)
            budget = max(1.0, tr.get_remaining_duration() - 0.8)
            per = budget / (len(trace) - 1)
            for st, n in trace[1:]:
                nv = stack_view(st, n).move_to(SV)
                self.play(Transform(sv, nv), run_time=rt(per))
            res = math(f"= {trace[-1][1]}", size=48, color=GOOD).next_to(title, DOWN, 0.3)
            self.play(FadeIn(res), run_time=0.4)
            rest(self, tr)

        rb = rules_block(size=40).to_edge(UP, buff=0.5)
        mv = call_moves(rb, size=32).next_to(rb, DOWN, 0.7)
        key = text("first number drops, or first stays and second drops", size=34, color=FG)
        key.next_to(mv, DOWN, 0.6)
        with self.voiceover(text=N("s05.b2")) as tr:
            self.play(FadeOut(Group(*self.mobjects)), run_time=0.5)
            self.play(FadeIn(rb), run_time=0.6)
            wait_until(self, tr, "first")
            self.play(FadeIn(mv[0]), run_time=0.5)
            self.play(FadeIn(mv[2]), run_time=0.5)
            wait_until(self, tr, "second")
            self.play(FadeIn(mv[1]), run_time=0.5)
            self.play(FadeIn(key, shift=UP * 0.15), run_time=0.6)
            rest(self, tr)

        dm, dn = dial_pair(size=72, gap=1.2)
        dials = VGroup(dm, dn).move_to(DOWN * 0.2)
        with self.voiceover(text=N("s05.b3")) as tr:
            self.play(FadeOut(VGroup(rb, mv, key)), run_time=0.5)
            self.play(FadeIn(dials), run_time=0.6)
            t_jump = tr.time_until_bookmark("jump")
            self.play(dn.tr.animate.set_value(0), run_time=rt(min(2.0, t_jump * 0.5)), rate_func=linear)
            wait_until(self, tr, "jump")
            self.play(dm.tr.animate.set_value(1), dn.tr.animate.set_value(61), run_time=0.6)
            huge = tag("however huge", size=32, color=SECONDARY).next_to(dn, DOWN, 0.4)
            self.play(FadeIn(huge), run_time=0.4)
            rem = tr.get_remaining_duration()
            self.play(dn.tr.animate.set_value(0), run_time=rt(rem * 0.4), rate_func=linear)
            self.play(dm.tr.animate.set_value(0), dn.tr.animate.set_value(9), run_time=0.5)
            self.play(dn.tr.animate.set_value(0), run_time=rt(rem * 0.25), rate_func=linear)
            rest(self, tr)

        chain_pairs = [(2, 1), (2, 0), (1, 1), (1, 0), (0, 1)]
        chain = VGroup()
        for i, (a, b) in enumerate(chain_pairs):
            chain.add(math(f"({a}, {b})", size=44))
            if i < len(chain_pairs) - 1:
                chain.add(math(r"\to", size=44, color=MUTED))
        chain.add(math(r"\to", size=44, color=MUTED), tag("end", size=36, color=GOOD))
        chain.arrange(RIGHT, buff=0.25).move_to(UP * 1.6)
        ends = text("every chain of calls ends", size=40, color=FG).next_to(chain, DOWN, 0.6)
        tree = self.call_tree().next_to(ends, DOWN, 0.5)
        stops = VGroup(tick(at=ORIGIN, s=1.3), text("always stops", size=44, color=GOOD)).arrange(RIGHT, 0.3)
        stops.next_to(tree, DOWN, 0.4)
        with self.voiceover(text=N("s05.b4")) as tr:
            self.play(FadeOut(VGroup(dials, huge)), run_time=0.5)
            self.play(LaggedStart(*[FadeIn(c) for c in chain], lag_ratio=0.15), run_time=1.6)
            self.play(FadeIn(ends), run_time=0.5)
            self.play(FadeIn(tree), run_time=0.8)
            wait_until(self, tr, "halts")
            self.play(FadeIn(stops, shift=UP * 0.15), run_time=0.6)
            rest(self, tr)
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.5)

    @staticmethod
    def call_tree(depth=3, w=5.0, h=1.6):
        dots = VGroup()
        edges = VGroup()
        pos = {(0, 0): np.array([0, 0, 0])}
        for d in range(1, depth + 1):
            for i in range(2 ** d):
                if d == depth and i % 3 == 2:
                    continue
                parent = (d - 1, i // 2)
                if parent not in pos:
                    continue
                x = (i + 0.5) / 2 ** d * w - w / 2
                pos[(d, i)] = np.array([x, -d * h / depth, 0])
                edges.add(Line(pos[parent], pos[(d, i)], color=MUTED, stroke_width=3))
        for p in pos.values():
            dots.add(Dot(p, radius=0.08, color=FG))
        return VGroup(edges, dots)


# ---------------------------------------------------------------------------
# s06 Ending
# ---------------------------------------------------------------------------


class S06Ending(VoiceoverScene):
    def construct(self):
        self.set_speech_service(get_speech_service())
        card = note_card(["Does this mean the Ackermann function", "can't be defined with only these loops?"],
                         size=36).move_to(UP * 0.2)
        with self.voiceover(text=N("s06.b1")) as tr:
            self.play(FadeIn(card, shift=DOWN * 0.2), run_time=0.8)
            rest(self, tr)

        fp = func_loop_panel(size=34).move_to(UP * 0.8)
        note = tag("repeat_it(g) = the function that starts at 1 and applies g, n + 1 times", size=28)
        note.next_to(fp, DOWN, 0.5)
        cred = tag(GODEL + "'s System T", size=26).to_corner(DR, buff=0.5)
        with self.voiceover(text=N("s06.b2")) as tr:
            self.play(FadeOut(card), run_time=0.5)
            self.play(FadeIn(fp, shift=UP * 0.2), run_time=0.7)
            wait_until(self, tr, "functions")
            hl = fp.box_part(2, "f = repeat_it(f)")
            self.play(Create(hl), run_time=0.6)
            self.play(FadeIn(note), run_time=0.6)
            self.wait(frac_time(tr, 0.15))
            ok = VGroup(tick(at=ORIGIN, s=1.2), text("Ackermann fits", size=36, color=GOOD)).arrange(RIGHT, 0.3)
            ok.next_to(note, DOWN, 0.5)
            self.play(FadeIn(ok), FadeIn(cred), run_time=0.6)
            rest(self, tr)

        big = RoundedRectangle(corner_radius=0.3, width=7.0, height=3.6, color=SECONDARY, stroke_width=4)
        big.move_to(LEFT * 1.6)
        bl = text("loops over functions", size=38, color=SECONDARY).move_to(big)
        esc = Arrow(big.get_right() + LEFT * 0.6, big.get_right() + RIGHT * 2.4, color=PRIMARY, stroke_width=6,
                    buff=0)
        escq = text("?", size=72, color=PRIMARY).next_to(esc, RIGHT, 0.2)
        real = tag("real: a computer can list its programs and run them", size=30).to_edge(DOWN, buff=0.7)
        with self.voiceover(text=N("s06.b3")) as tr:
            self.play(FadeOut(Group(*self.mobjects)), run_time=0.5)
            self.play(Create(big), FadeIn(bl), run_time=0.7)
            self.play(GrowArrow(esc), FadeIn(escq), run_time=0.7)
            wait_until(self, tr, "every")
            every = text("every always-stopping language misses something", size=36, color=PRIMARY)
            every.to_edge(UP, buff=0.6)
            self.play(FadeIn(every), run_time=0.6)
            self.play(FadeIn(real), run_time=0.6)
            rest(self, tr)

        dt = DiagTable(k=4, size=40, cw=1.3, rh=0.82).move_to(ORIGIN + DOWN * 0.1)
        with self.voiceover(text=N("s06.b4")) as tr:
            self.play(FadeOut(Group(*self.mobjects)), run_time=0.5)
            self.play(FadeIn(dt.cols), FadeIn(dt.inp), run_time=0.4)
            wait_until(self, tr, "list")
            self.play(LaggedStart(*[FadeIn(r) for r in dt.rows], lag_ratio=0.25), FadeIn(dt.vdots),
                      FadeIn(dt.hdots), run_time=1.2)
            self.play(LaggedStart(*[Create(b) for b in dt.diag], lag_ratio=0.25), run_time=1.0)
            self.play(FadeIn(dt.d_lab),
                      LaggedStart(*[TransformFromCopy(dt.vals[j][j], dt.d_vals[j]) for j in range(4)],
                                  lag_ratio=0.25), run_time=1.4)
            plus1 = tag("diagonal + 1", size=30, color=PRIMARY).next_to(dt.d_vals, RIGHT, 0.5)
            self.play(FadeIn(plus1), run_time=0.4)
            wait_until(self, tr, "differs")
            for j in range(4):
                self.play(FadeIn(dt.neq[j]), Indicate(dt.diag[j], color=BAD), Indicate(dt.d_vals[j], color=BAD),
                          run_time=rt(min(0.7, tr.get_remaining_duration() / 5)))
            rest(self, tr)

        msg = text("to compute everything computable,\nsome programs must be allowed to run forever",
                   size=38, color=FG, line_spacing=0.8).move_to(UP * 1.2)
        inset = halting_inset(1.1).next_to(msg, DOWN, 0.8)
        with self.voiceover(text=N("s06.b5")) as tr:
            self.play(FadeOut(Group(*self.mobjects)), run_time=0.5)
            self.play(FadeIn(msg, shift=UP * 0.15), run_time=0.8)
            self.wait(frac_time(tr, 0.3))
            self.play(FadeIn(inset), run_time=0.8)
            rest(self, tr)
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.8)


class Thumbnail(Scene):
    def construct(self):
        amn = math("A(m, n)", size=110, color=PRIMARY)
        tw = tower(6, size=64, color=FG)
        lab = math("A(4, 3) =", size=44, color=MUTED)
        row = VGroup(lab, tw).arrange(RIGHT, buff=0.25)
        left = VGroup(amn, row).arrange(DOWN, buff=0.7).move_to(LEFT * 3.6)
        t1 = text("The function", size=80, weight="BOLD")
        t2 = text("no for-loop", size=88, weight="BOLD", color=PRIMARY)
        t3 = text("can compute", size=80, weight="BOLD")
        words = VGroup(t1, t2, t3).arrange(DOWN, buff=0.3).move_to(RIGHT * 2.9)
        words.scale_to_fit_width(min(words.width, 7.0))
        self.add(left, words)
