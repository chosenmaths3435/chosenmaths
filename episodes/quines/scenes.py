"""Can a program print itself? Quines, a relational interpreter, and the recursion theorem.

Long-form scenes. Builders here are shared with shorts.py.
"""

import numpy as np
from manim import *
from manim_voiceover import VoiceoverScene

from mathvid import layout  # noqa: F401  must come before scene code runs
from mathvid.anim import clear, rest, strike, wait_frac, wait_until
from mathvid.code import CodePanel, char_width, mono, py_panel
from mathvid.layout import FH, FW
from mathvid.script import Script
from mathvid.style import BAD, BG, FG, GOOD, MUTED, PRIMARY, SECONDARY, TERTIARY, math, text, title_card
from mathvid.voice import get_speech_service

N = Script(__file__)

TITLE = "Can a program print itself?"
DATA_C = PRIMARY      # the data half (A, the quoted part)
INSTR_C = SECONDARY   # the instructions half (B)
TERM_BG = "#0B0D10"

# The quine from the user's notes, exactly (it prints itself byte for byte).
QUINE = [
    "def PB():",
    r"""    return 'def B(w):\n    return f"def PB():\\n    return {repr(w)}\\n{w}\\nprint(B(PB()))"'""",
    "def B(w):",
    r'''    return f"def PB():\n    return {repr(w)}\n{w}\nprint(B(PB()))"''',
    "print(B(PB()))",
]

INSTRUCTION = "Print two copies of the following, the second one in quotes:"
QUOTED = '"' + INSTRUCTION + '"'

LISP = ["((lambda (x) (list x (list 'quote x)))",
        " '(lambda (x) (list x (list 'quote x))))"]
QUERY = "(run 1 (q) (evalo q '() q))"


# ---------------------------------------------------------------------------
# Builders
# ---------------------------------------------------------------------------


def editor(lines, title="self.py", size=30, width_chars=34, python=True):
    if python:
        p = py_panel(lines, size=size, min_width=width_chars * char_width(size))
    else:
        p = CodePanel(lines, size=size, highlight=False, min_width=width_chars * char_width(size))
    t = mono(title, size * 0.8, MUTED).next_to(p.bg, UP, buff=0.12).align_to(p.bg, LEFT)
    g = VGroup(p, t)
    g.panel, g.title = p, t
    return g


def terminal(lines, size=30, width_chars=34):
    cols = [[MUTED] * len(l) if l.startswith("$") else None for l in lines]
    cols = [c if c is not None else [FG] * len(l) for c, l in zip(cols, lines)]
    return CodePanel(lines, size=size, colors=cols, bg=TERM_BG,
                     min_width=width_chars * char_width(size))


def code_bars(panel, rows, widths, color=MUTED, height=None):
    """Grey bars standing in for code, one per listed row of a panel."""
    h = height or panel.lines[0].anchor.height * 0.55
    left = panel.bg.get_left()[0] + 0.32
    g = VGroup()
    for r, w in zip(rows, widths):
        y = panel.lines[r].anchor.get_center()[1]
        g.add(RoundedRectangle(width=w, height=h, corner_radius=h / 2, stroke_width=0,
                               fill_color=color, fill_opacity=0.8).move_to([left + w / 2, y, 0]))
    return g


def nest(depth, size=54, ratio=0.66):
    """print("print("print(... nested `depth` deep. Returns (group, levels, gaps): levels[k]
    holds level k's 'print("' and '")', gaps[k] is a box around everything inside level k."""
    levels, gaps = [], []

    def build(k, s):
        L = mono('print("', s, FG)
        R = mono('")', s, FG)
        if k == depth - 1:
            inner = Rectangle(width=char_width(s) * 3, height=mono("M", s).height, stroke_width=0)
        else:
            inner = build(k + 1, s * ratio)
        g = VGroup(L, inner, R).arrange(RIGHT, buff=char_width(s) * 0.15)
        levels.insert(0, VGroup(L, R))
        return g

    grp = build(0, size)  # levels[k] is level k: the innermost call inserts first
    node = grp
    for k in range(depth):
        inner = node[1]
        gaps.append(SurroundingRectangle(inner, buff=0.06, corner_radius=0.06, color=PRIMARY,
                                         stroke_width=3, fill_color=PRIMARY, fill_opacity=0.18))
        node = inner
    return grp, levels, gaps


def sentence_block(size=32, buff=0.25):
    instr = text(INSTRUCTION, size=size, color=INSTR_C)
    data = text(QUOTED, size=size, color=DATA_C)
    g = VGroup(instr, data).arrange(DOWN, buff=buff, aligned_edge=LEFT)
    return g, instr, data


def part_box(label, color, w, h=0.95, size=40):
    r = Rectangle(width=w, height=h, stroke_color=color, stroke_width=4, fill_color=color,
                  fill_opacity=0.12)
    t = text(label, size=size, color=color, weight="BOLD").move_to(r)
    g = VGroup(r, t)
    g.rect, g.label = r, t
    return g


def self_boxes(wa=2.2, wb=3.0, h=0.95):
    a = part_box("A", DATA_C, wa, h)
    b = part_box("B", INSTR_C, wb, h)
    row = VGroup(a, b).arrange(RIGHT, buff=0)
    lab = text("SELF", size=34, color=FG, weight="BOLD").next_to(row, UP, buff=0.15)
    g = VGroup(lab, row)
    g.a, g.b, g.row, g.lab = a, b, row, lab
    return g


def chip(label, color, w, h=0.6, size=28):
    r = RoundedRectangle(width=w, height=h, corner_radius=0.1, stroke_color=color, stroke_width=3,
                         fill_color=color, fill_opacity=0.3)
    t = text(label, size=size, color=FG).move_to(r)
    return VGroup(r, t)


def steps_panel(header, color, lines, size=28, width=None):
    rows = VGroup()
    for ln in lines:
        rows.add(ln if isinstance(ln, Mobject) else text(ln, size=size))
    rows.arrange(DOWN, buff=0.2, aligned_edge=LEFT)
    hd = text(header, size=size, color=color, weight="BOLD")
    body = VGroup(hd, rows).arrange(DOWN, buff=0.22, aligned_edge=LEFT)
    w = max(width or 0, body.width + 0.6)
    bg = RoundedRectangle(width=w, height=body.height + 0.5, corner_radius=0.15, stroke_color=color,
                          stroke_width=3, fill_color=BG, fill_opacity=1)
    body.move_to(bg).align_to(bg, LEFT).shift(RIGHT * 0.3)
    g = VGroup(bg, body)
    g.rows, g.bg = rows, bg
    return g


def b_steps(size=28):
    s3 = VGroup(text("3.", size=size), text("Print", size=size), text("everything written.", size=size))
    s3.arrange(RIGHT, buff=0.12, aligned_edge=DOWN)
    p = steps_panel("B", INSTR_C, ["1. Let w be what's written so far.",
                                   "2. Write P(w) in front of w.", s3], size=size)
    p.print_word = s3[1]
    return p


def a_steps(size=28):
    return steps_panel("A", DATA_C, ["1. Write the text of B."], size=size)


def tool_group(size=34):
    w = text("w", size=size + 10)
    arr = Arrow(LEFT, RIGHT, buff=0, color=MUTED).scale(0.9)
    inner = mono('write "w"', size - 4, FG)
    box = SurroundingRectangle(inner, buff=0.25, corner_radius=0.1, color=FG, stroke_width=3)
    lab = math(r"P(w)", size=size).next_to(box, UP, buff=0.12)
    pw = VGroup(box, inner, lab)
    g = VGroup(w, arr, pw).arrange(RIGHT, buff=0.35)
    cap = text("add write and quotes", size=size - 8, color=MUTED).next_to(g, DOWN, buff=0.3)
    g.add(cap)
    return g


def strip(width=11.0, h=0.9):
    r = Rectangle(width=width, height=h, stroke_color=MUTED, stroke_width=3, fill_color=BG,
                  fill_opacity=1)
    lab = text("written so far", size=26, color=MUTED).next_to(r, UP, buff=0.1).align_to(r, LEFT)
    g = VGroup(r, lab)
    g.rect = r
    return g


def star(color=PRIMARY, r=0.32):
    return Star(5, outer_radius=r, inner_radius=r * 0.45, color=color, fill_color=color,
                fill_opacity=1, stroke_width=2)


def prog_bar(w, color=MUTED, h=0.42, label=None, size=26):
    r = RoundedRectangle(width=w, height=h, corner_radius=h / 2, stroke_width=0, fill_color=color,
                         fill_opacity=0.85)
    g = VGroup(r)
    if label:
        g.add(text(label, size=size, color=FG).next_to(r, LEFT, buff=0.25))
    g.bar = r
    return g


def c_steps(size=30, width=None):
    rows = [text("1. Get your own source code.", size=size),
            text("2. Run E until it lists a program D longer than C.", size=size),
            text("3. Do what D does.", size=size)]
    return steps_panel("C", PRIMARY, rows, size=size, width=width)


def cross(mob, color=BAD, width=7):
    return VGroup(Line(mob.get_corner(UL), mob.get_corner(DR), color=color, stroke_width=width),
                  Line(mob.get_corner(DL), mob.get_corner(UR), color=color, stroke_width=width))


def lisp_panel(size=30):
    return CodePanel(LISP, size=size, highlight=False)


def e_lister(n=9, seed=3, x0=0.0, top=2.0, gap=0.5, longest=None):
    """Bars of uneven length, as if printed one after another by E."""
    rng = np.random.default_rng(seed)
    ws = list(rng.uniform(0.6, 3.0, n))
    if longest is not None:
        ws[longest] = 5.6
    bars = VGroup(*[prog_bar(w, color=FG) for w in ws])
    for i, b in enumerate(bars):
        b.move_to([x0 + b.width / 2, top - i * gap, 0])
    return bars


# ---------------------------------------------------------------------------
# s01 Hook
# ---------------------------------------------------------------------------


class S01Hook(VoiceoverScene):
    def construct(self):
        self.set_speech_service(get_speech_service())
        ed = editor(["", "", ""], title="self.py", size=30, width_chars=36).move_to(UP * 1.6)
        term = terminal(["$ python self.py", "", "", ""], size=30, width_chars=36).move_to(DOWN * 2.0)
        cursor = Rectangle(width=0.06, height=0.38, stroke_width=0, fill_color=FG, fill_opacity=1)
        cursor.move_to(ed.panel.lines[0].anchor).shift(RIGHT * char_width(30))
        with self.voiceover(text=N("s01.b1")) as tr:
            self.play(FadeIn(ed), FadeIn(term), FadeIn(cursor), run_time=0.6)
            for _ in range(2):
                self.play(cursor.animate.set_opacity(0), run_time=0.3)
                self.play(cursor.animate.set_opacity(1), run_time=0.3)
            wait_until(self, tr, "character")
            widths = [3.2, 5.6, 2.4]
            bars = code_bars(ed.panel, [0, 1, 2], widths, color=SECONDARY)
            obars = code_bars(term, [1, 2, 3], widths, color=SECONDARY)
            eq = VGroup(CurvedArrow(ed.panel.bg.get_right() + LEFT * 0.1 + DOWN * 0.2,
                                    term.bg.get_right() + LEFT * 0.1 + UP * 0.2, angle=-PI / 2,
                                    color=PRIMARY))
            eq.add(text("=", size=60, color=PRIMARY).next_to(eq[0], RIGHT, buff=0.15))
            self.play(FadeOut(cursor), LaggedStart(*[GrowFromEdge(b, LEFT) for b in bars], lag_ratio=0.3),
                      run_time=0.9)
            self.play(LaggedStart(*[GrowFromEdge(b, LEFT) for b in obars], lag_ratio=0.3), Create(eq[0]),
                      FadeIn(eq[1]), run_time=0.9)
            rest(self, tr)

        src = "print(open(__file__).read())"
        ed2 = editor([src], title="self.py", size=30, width_chars=36).move_to(ed.panel.bg.get_center())
        ed2.shift(ed.panel.bg.get_top() - ed2.panel.bg.get_top())
        term2 = terminal(["$ python self.py", src], size=30, width_chars=36)
        term2.shift(term.bg.get_top() - term2.bg.get_top())
        with self.voiceover(text=N("s01.b2")) as tr:
            self.play(FadeOut(bars), FadeOut(obars), FadeOut(eq), FadeTransform(ed, ed2),
                      FadeTransform(term, term2), run_time=0.8)
            wait_frac(self, tr, 0.3)
            self.play(Write(term2.lines[1].body()), run_time=0.7)
            wait_until(self, tr, "cheating")
            st = strike(ed2.panel.line(0), width=6)
            ch = text("cheating", size=44, color=BAD).next_to(ed2.panel.bg, RIGHT, buff=0.3)
            if ch.get_right()[0] > FW / 2 - 0.3:
                ch.next_to(ed2.panel.bg, DOWN, buff=0.25).align_to(ed2.panel.bg, RIGHT)
            self.play(Create(st), FadeIn(ch, shift=LEFT * 0.2), run_time=0.6)
            rest(self, tr)

        r1 = VGroup(cross(Square(0.32), width=5), text("no reading files", size=40)).arrange(RIGHT, buff=0.3)
        r2 = VGroup(cross(Square(0.32), width=5), text("no input", size=40)).arrange(RIGHT, buff=0.3)
        rules = VGroup(r1, r2).arrange(DOWN, buff=0.35, aligned_edge=LEFT).move_to(DOWN * 1.9)
        with self.voiceover(text=N("s01.b3")) as tr:
            self.play(FadeOut(term2), FadeOut(ch), run_time=0.5)
            wait_until(self, tr, "files")
            self.play(FadeIn(r1, shift=UP * 0.2), run_time=0.5)
            wait_until(self, tr, "input")
            self.play(FadeIn(r2, shift=UP * 0.2), run_time=0.5)
            rest(self, tr)
        clear(self, run_time=0.5)
        title_card(self, TITLE)


# ---------------------------------------------------------------------------
# s02 Why it's hard
# ---------------------------------------------------------------------------


class S02WhyHard(VoiceoverScene):
    def construct(self):
        self.set_speech_service(get_speech_service())
        ed = editor(['print("hello")'], title="attempt.py", size=36, width_chars=24).move_to(UP * 1.4)
        term = terminal(["$ python attempt.py", "hello"], size=36, width_chars=24).move_to(DOWN * 1.6)
        with self.voiceover(text=N("s02.b1")) as tr:
            self.play(FadeIn(ed), FadeIn(term[0]), FadeIn(term.lines[0]), run_time=0.7)
            wait_frac(self, tr, 0.55)
            self.play(Write(term.lines[1].body()), run_time=0.6)
            rest(self, tr)

        grp, levels, gaps = nest(6, size=58)
        grp.move_to(ORIGIN)
        with self.voiceover(text=N("s02.b2")) as tr:
            self.play(FadeOut(ed), FadeOut(term), run_time=0.5)
            self.play(FadeIn(levels[0]), FadeIn(gaps[0]), run_time=0.7)
            wait_until(self, tr, "again")
            self.play(FadeIn(levels[1]), ReplacementTransform(gaps[0], gaps[1]), run_time=0.8)
            rest(self, tr)

        with self.voiceover(text=N("s02.b3")) as tr:
            per = (tr.duration - 0.6) / 4
            for k in range(2, 6):
                self.play(FadeIn(levels[k]), ReplacementTransform(gaps[k - 1], gaps[k]),
                          run_time=min(0.8, per * 0.6))
                self.wait(max(0.05, per * 0.4))
            rest(self, tr)

        left = text("can't contain a copy", size=44)
        right = text("build one", size=44, color=PRIMARY)
        VGroup(left, right).arrange(RIGHT, buff=1.6)
        st = strike(left, width=6)
        with self.voiceover(text=N("s02.b4")) as tr:
            self.play(FadeOut(grp), FadeOut(gaps[5]), run_time=0.5)
            self.play(FadeIn(left), run_time=0.5)
            self.play(Create(st), run_time=0.5)
            wait_frac(self, tr, 0.6)
            self.play(FadeIn(right, shift=LEFT * 0.2), run_time=0.6)
            rest(self, tr)
        clear(self)


# ---------------------------------------------------------------------------
# s03 The trick in English
# ---------------------------------------------------------------------------


class S03English(VoiceoverScene):
    def construct(self):
        self.set_speech_service(get_speech_service())
        orig, instr, data = sentence_block(size=32)
        orig.move_to(UP * 2.1)
        with self.voiceover(text=N("s03.b1")) as tr:
            self.play(FadeIn(instr, shift=UP * 0.1), run_time=0.7)
            self.play(FadeIn(data, shift=UP * 0.1), run_time=0.7)
            rest(self, tr)

        out1 = text(INSTRUCTION, size=32, color=DATA_C)
        out2 = text(QUOTED, size=32, color=DATA_C)
        out = VGroup(out1, out2).arrange(DOWN, buff=0.25, aligned_edge=LEFT)
        out.align_to(orig, LEFT).move_to([orig.get_center()[0], -1.2, 0])
        out.align_to(orig, LEFT)
        olab = text("output", size=26, color=MUTED).next_to(out, UP, buff=0.15).align_to(out, LEFT)
        with self.voiceover(text=N("s03.b2")) as tr:
            self.play(FadeIn(olab), TransformFromCopy(data[1:-1], out1), run_time=1.0)
            wait_frac(self, tr, 0.45)
            self.play(TransformFromCopy(data, out2), run_time=1.0)
            wait_until(self, tr, "whole")
            eq = math("=", size=80, color=GOOD).rotate(PI / 2).move_to([0, 0.45, 0])
            b1 = SurroundingRectangle(orig, buff=0.15, color=GOOD, corner_radius=0.08)
            b2 = SurroundingRectangle(out, buff=0.15, color=GOOD, corner_radius=0.08)
            self.play(FadeIn(eq), Create(b1), Create(b2), run_time=0.7)
            rest(self, tr)

        li = text("instructions", size=26, color=INSTR_C).next_to(instr, UP, buff=0.15).align_to(instr, LEFT)
        ld = text("data", size=26, color=DATA_C).next_to(data, RIGHT, buff=0.3)
        with self.voiceover(text=N("s03.b3")) as tr:
            self.play(FadeOut(eq), FadeOut(b1), FadeOut(b2), run_time=0.4)
            self.play(FadeIn(li), run_time=0.4)
            wait_frac(self, tr, 0.2)
            self.play(FadeIn(ld), run_time=0.4)
            wait_until(self, tr, "twice")
            a1 = CurvedArrow(data.get_left() + LEFT * 0.1, out1.get_left() + LEFT * 0.1, angle=PI / 2,
                             color=DATA_C)
            a2 = CurvedArrow(data.get_left() + LEFT * 0.1 + DOWN * 0.1, out2.get_left() + LEFT * 0.1,
                             angle=PI / 2.2, color=DATA_C)
            self.play(Create(a1), run_time=0.5)
            self.play(Create(a2), run_time=0.5)
            rest(self, tr)

        note = text("data = copy of the instructions", size=40, color=FG).move_to(DOWN * 1.2)
        with self.voiceover(text=N("s03.b4")) as tr:
            self.play(FadeOut(VGroup(a1, a2, out, olab)), run_time=0.5)
            self.play(Indicate(data[1:-1], color=DATA_C, scale_factor=1.04),
                      Indicate(instr, color=INSTR_C, scale_factor=1.04), run_time=1.0)
            self.play(FadeIn(note, shift=UP * 0.2), run_time=0.6)
            rest(self, tr)
        clear(self)


# ---------------------------------------------------------------------------
# s04 The construction
# ---------------------------------------------------------------------------


class S04Construction(VoiceoverScene):
    def construct(self):
        self.set_speech_service(get_speech_service())
        sb = self_boxes().move_to([-2.6, 2.75, 0])
        with self.voiceover(text=N("s04.b1")) as tr:
            self.play(FadeIn(sb.lab), Create(sb.a.rect), Create(sb.b.rect), run_time=0.8)
            wait_frac(self, tr, 0.7)
            self.play(FadeIn(sb.a.label), FadeIn(sb.b.label), run_time=0.6)
            rest(self, tr)

        tool = tool_group(34).move_to([0, 0.2, 0])
        with self.voiceover(text=N("s04.b2")) as tr:
            self.play(FadeIn(tool[0]), run_time=0.4)
            wait_frac(self, tr, 0.15)
            self.play(GrowArrow(tool[1]), FadeIn(tool[2]), run_time=0.8)
            wait_frac(self, tr, 0.6)
            self.play(FadeIn(tool[3]), run_time=0.5)
            rest(self, tr)
            self.play(FadeOut(tool), run_time=0.5)

        st = strip().move_to([0, -3.1, 0])
        bs = b_steps(26).move_to([2.9, 0.4, 0])
        with self.voiceover(text=N("s04.b3")) as tr:
            self.play(FadeIn(st), run_time=0.5)
            self.play(TransformFromCopy(sb.b.rect, bs.bg), FadeIn(bs[1][0]), run_time=0.7)
            for i, f in enumerate([0.15, 0.45, 0.75]):
                wait_frac(self, tr, f)
                self.play(FadeIn(bs.rows[i], shift=RIGHT * 0.2), run_time=0.5)
            rest(self, tr)

        asx = a_steps(26)
        apb = math(r"A = P(B)", size=40, color=DATA_C)
        asx_g = VGroup(asx, apb).arrange(DOWN, buff=0.3).move_to([-4.0, 0.4, 0])
        with self.voiceover(text=N("s04.b4")) as tr:
            self.play(TransformFromCopy(sb.a.rect, asx.bg), FadeIn(asx[1]), run_time=0.7)
            wait_frac(self, tr, 0.5)
            self.play(Write(apb), run_time=0.7)
            rest(self, tr)

        cb = chip("text of B", INSTR_C, 3.0).move_to(st.rect.get_center() + RIGHT * 1.0)
        ca = chip("text of A", DATA_C, 2.2).next_to(cb, LEFT, buff=0.1)
        wlab = math(r"w = B", size=36, color=INSTR_C).next_to(st.rect, UP, buff=0.12).set_x(cb.get_x())
        with self.voiceover(text=N("s04.b5")) as tr:
            self.play(sb.a.rect.animate.set_fill(DATA_C, 0.45), Indicate(asx.bg, color=DATA_C), run_time=0.6)
            self.play(TransformFromCopy(sb.b.rect, cb), run_time=0.8)
            wait_until(self, tr, "sees")
            self.play(sb.a.rect.animate.set_fill(DATA_C, 0.12), sb.b.rect.animate.set_fill(INSTR_C, 0.45),
                      FadeIn(wlab), run_time=0.6)
            wait_until(self, tr, "front")
            self.play(FadeIn(ca, shift=RIGHT * 0.6), FadeOut(wlab), run_time=0.7)
            wait_until(self, tr, "prints")
            outrow = VGroup(ca.copy(), cb.copy())
            tgt = VGroup(chip("A", DATA_C, 2.2, h=0.7), chip("B", INSTR_C, 3.0, h=0.7)).arrange(RIGHT, buff=0)
            tgt.next_to(sb.row, DOWN, buff=0.75)
            eq = math("=", size=60, color=GOOD).rotate(PI / 2).move_to((sb.row.get_bottom() + tgt.get_top()) / 2)
            self.play(FadeOut(bs), FadeOut(asx_g), run_time=0.4)
            self.play(Transform(outrow, tgt), run_time=0.8)
            self.play(FadeIn(eq), sb.b.rect.animate.set_fill(INSTR_C, 0.12), run_time=0.4)
            rest(self, tr)

        with self.voiceover(text=N("s04.b6")) as tr:
            self.play(FadeOut(VGroup(outrow, eq, st, ca, cb)), FadeOut(sb.lab), run_time=0.5)
            self.play(sb.row.animate.scale(1.25).move_to([0, -0.2, 0]), run_time=0.7)
            a_to_b = CurvedArrow(sb.a.get_top() + UP * 0.05, sb.b.get_top() + UP * 0.05, angle=-PI / 2.5,
                                 color=DATA_C)
            lab = text("copy of", size=30, color=DATA_C).next_to(a_to_b, UP, buff=0.1)
            wait_frac(self, tr, 0.3)
            self.play(Create(a_to_b), FadeIn(lab), run_time=0.7)
            wait_until(self, tr, "never")
            back = DashedVMobject(CurvedArrow(sb.b.get_bottom() + DOWN * 0.05, sb.a.get_bottom() + DOWN * 0.05,
                                              angle=-PI / 2.5, color=MUTED), num_dashes=14)
            self.play(Create(back), run_time=0.6)
            x = cross(Square(0.7).move_to(back.get_center()), width=6)
            self.play(Create(x), run_time=0.4)
            rest(self, tr)

        s_instr = text(INSTRUCTION, size=26, color=INSTR_C)
        s_data = text(QUOTED, size=26, color=DATA_C)
        sent = VGroup(s_instr, s_data).arrange(DOWN, buff=0.2).move_to([0, 2.9, 0])
        with self.voiceover(text=N("s04.b7")) as tr:
            self.play(FadeOut(VGroup(a_to_b, lab, back, x)), run_time=0.4)
            self.play(sb.row.animate.move_to([0, -1.2, 0]), FadeIn(sent), run_time=0.8)
            sb.lab.next_to(sb.row, UP, buff=0.15)
            self.play(FadeIn(sb.lab), run_time=0.3)
            la = Line(s_data.get_bottom() + DOWN * 0.05 + LEFT * 2.2, sb.a.get_top(), color=DATA_C, stroke_width=3)
            xr = max(s_instr.get_right()[0], s_data.get_right()[0]) + 0.35
            lb = VMobject(color=INSTR_C, stroke_width=3).set_points_as_corners([
                s_instr.get_right() + RIGHT * 0.08, [xr, s_instr.get_y(), 0],
                [xr, sb.b.get_y(), 0], sb.b.get_right()])
            hb = SurroundingRectangle(s_instr, buff=0.08, color=INSTR_C, stroke_width=2)
            wait_frac(self, tr, 0.3)
            self.play(Create(la), Indicate(s_data, color=DATA_C, scale_factor=1.03), run_time=0.7)
            wait_frac(self, tr, 0.6)
            self.play(Create(hb), Create(lb), run_time=0.7)
            rest(self, tr)
        clear(self)


# ---------------------------------------------------------------------------
# s05 A real language
# ---------------------------------------------------------------------------


def quine_panel(size=16):
    return py_panel(QUINE, size=size)


def hl(mobs, color, buff=0.06):
    return SurroundingRectangle(mobs, buff=buff, color=color, stroke_width=3, corner_radius=0.05)


class S05Python(VoiceoverScene):
    def construct(self):
        self.set_speech_service(get_speech_service())
        qp = quine_panel(17).move_to([0, 2.15, 0])
        title = mono("quine.py", 17 * 0.9, MUTED).next_to(qp.bg, UP, buff=0.1).align_to(qp.bg, LEFT)
        with self.voiceover(text=N("s05.b1")) as tr:
            self.play(FadeIn(qp.bg), FadeIn(title), run_time=0.4)
            self.play(LaggedStart(*[FadeIn(qp.line(i), shift=RIGHT * 0.1) for i in range(5)], lag_ratio=0.25),
                      run_time=1.6)
            rest(self, tr)

        box_a = hl(VGroup(qp.line(0), qp.line(1)), DATA_C)
        tag_a = text("<- A", size=34, color=DATA_C, weight="BOLD").next_to(qp.line(0), RIGHT, buff=0.5)
        with self.voiceover(text=N("s05.b2")) as tr:
            self.play(Create(box_a), FadeIn(tag_a), run_time=0.7)
            wait_frac(self, tr, 0.5)
            self.play(Indicate(qp.line(1), color=DATA_C, scale_factor=1.0), run_time=1.0)
            rest(self, tr)

        box_b = hl(VGroup(qp.line(2), qp.line(3)), INSTR_C)
        tag_b = text("<- B", size=34, color=INSTR_C, weight="BOLD").next_to(qp.line(2), RIGHT, buff=0.5)
        tmpl = qp.box_part(3, r"def PB():\n    return {repr(w)}", color=PRIMARY)
        tmpl_lab = math(r"P(w)", size=40, color=PRIMARY).move_to([tmpl.get_center()[0], 0.3, 0])
        tmpl_ln = Line(tmpl.get_bottom(), tmpl_lab.get_top(), color=PRIMARY, stroke_width=2)
        rbox = qp.box_part(3, "repr", color=GOOD, buff=0.03)
        rlab = text("adds quotes", size=30, color=GOOD).move_to([rbox.get_center()[0] + 2.6, 0.3, 0])
        rln = Line(rbox.get_bottom(), rlab.get_top() + LEFT * 0.6, color=GOOD, stroke_width=2)
        with self.voiceover(text=N("s05.b3")) as tr:
            self.play(FadeOut(box_a), FadeOut(tag_a), Create(box_b), FadeIn(tag_b), run_time=0.7)
            wait_until(self, tr, "repr")
            self.play(Create(tmpl), FadeIn(tmpl_lab), Create(tmpl_ln), run_time=0.7)
            wait_frac(self, tr, 0.72)
            self.play(Create(rbox), FadeIn(rlab), Create(rln), run_time=0.6)
            rest(self, tr)

        wbox = qp.box_part(3, "{w}", color=INSTR_C, buff=0.03)
        pbox = qp.box_part(3, "print(B(PB()))", color=PRIMARY, buff=0.03)
        with self.voiceover(text=N("s05.b4")) as tr:
            self.play(FadeOut(VGroup(tmpl, tmpl_lab, tmpl_ln, rbox, rlab, rln)), run_time=0.4)
            self.play(Create(wbox), run_time=0.5)
            wait_frac(self, tr, 0.55)
            self.play(Create(pbox), run_time=0.5)
            rest(self, tr)

        lbox = hl(qp.line(4), PRIMARY)
        term = terminal(["$ python quine.py"] + QUINE, size=17, width_chars=93)
        term.move_to([0, -1.75, 0])
        with self.voiceover(text=N("s05.b5")) as tr:
            self.play(FadeOut(VGroup(wbox, pbox, box_b, tag_b)), Create(lbox), run_time=0.6)
            wait_frac(self, tr, 0.3)
            self.play(FadeIn(term.bg), FadeIn(term.lines[0]), run_time=0.5)
            self.play(LaggedStart(*[FadeIn(term.lines[i]) for i in range(1, 6)], lag_ratio=0.2), run_time=1.0)
            wait_until(self, tr, "character")
            ok = text("diff: identical", size=34, color=GOOD)
            eq = math("=", size=60, color=GOOD).rotate(PI / 2)
            mid = VGroup(eq, ok).arrange(RIGHT, buff=0.3).move_to([0, (qp.bg.get_bottom()[1] + term.bg.get_top()[1]) / 2, 0])
            self.play(FadeOut(lbox), FadeIn(mid), Indicate(term, color=GOOD, scale_factor=1.0), run_time=0.8)
            rest(self, tr)

        word = text("quine", size=120, color=PRIMARY, weight="BOLD")
        plate = BackgroundRectangle(word, color=BG, fill_opacity=0.85, buff=0.3)
        with self.voiceover(text=N("s05.b6")) as tr:
            self.play(FadeIn(plate), FadeIn(word, scale=1.2), run_time=0.8)
            rest(self, tr)
        clear(self)


# ---------------------------------------------------------------------------
# s06 Running an interpreter backwards
# ---------------------------------------------------------------------------


def interp_group(size=34, box_label="interpreter"):
    box = RoundedRectangle(width=3.6, height=1.5, corner_radius=0.15, color=FG, stroke_width=3)
    lab = text(box_label, size=size + 4).move_to(box)
    left = mono("(list 'a 'b)", size, FG)
    right = mono("(a b)", size, FG)
    left.next_to(box, LEFT, buff=1.4)
    right.next_to(box, RIGHT, buff=1.4)
    a1 = Arrow(left.get_right(), box.get_left(), buff=0.15, color=MUTED)
    a2 = Arrow(box.get_right(), right.get_left(), buff=0.15, color=MUTED)
    g = VGroup(box, lab, left, right, a1, a2)
    g.box, g.lab, g.left, g.right, g.a1, g.a2 = box, lab, left, right, a1, a2
    return g


class S06Backwards(VoiceoverScene):
    def construct(self):
        self.set_speech_service(get_speech_service())
        ig = interp_group().move_to(ORIGIN)
        with self.voiceover(text=N("s06.b1")) as tr:
            self.play(Create(ig.box), FadeIn(ig.lab), run_time=0.7)
            wait_frac(self, tr, 0.55)
            self.play(FadeIn(ig.left, shift=RIGHT * 0.3), GrowArrow(ig.a1), run_time=0.6)
            self.play(GrowArrow(ig.a2), FadeIn(ig.right, shift=RIGHT * 0.3), run_time=0.6)
            rest(self, tr)

        lab2 = text("evalo", size=40).move_to(ig.box)
        le = text("expression", size=36).move_to(ig.left)
        rv = text("value", size=36).move_to(ig.right)
        d1 = DoubleArrow(le.get_right(), ig.box.get_left(), buff=0.15, color=PRIMARY, tip_length=0.25)
        d2 = DoubleArrow(ig.box.get_right(), rv.get_left(), buff=0.15, color=PRIMARY, tip_length=0.25)
        q1 = text("?", size=60, color=PRIMARY).next_to(le, UP, buff=0.2)
        q2 = text("?", size=60, color=PRIMARY).next_to(rv, UP, buff=0.2)
        with self.voiceover(text=N("s06.b2")) as tr:
            self.play(Transform(ig.lab, lab2), run_time=0.6)
            wait_frac(self, tr, 0.3)
            self.play(Transform(ig.left, le), Transform(ig.right, rv), ReplacementTransform(ig.a1, d1),
                      ReplacementTransform(ig.a2, d2), run_time=0.9)
            wait_until(self, tr, "either")
            self.play(FadeIn(q1, scale=1.4), run_time=0.4)
            self.play(FadeIn(q2, scale=1.4), run_time=0.4)
            rest(self, tr)

        qp = CodePanel([QUERY], size=40, highlight=False).move_to([0, 2.6, 0])
        with self.voiceover(text=N("s06.b3")) as tr:
            self.play(FadeOut(VGroup(ig.box, ig.lab, ig.left, ig.right, d1, d2, q1, q2)), run_time=0.5)
            self.play(FadeIn(qp), run_time=0.6)
            wait_until(self, tr, "itself")
            qa, qb = qp.part(0, "q", 1), qp.part(0, "q", 2)
            self.play(qa.animate.set_color(PRIMARY), qb.animate.set_color(PRIMARY), run_time=0.4)
            self.play(Indicate(qa, color=PRIMARY, scale_factor=1.5), Indicate(qb, color=PRIMARY, scale_factor=1.5),
                      run_time=0.8)
            rest(self, tr)

        ans = lisp_panel(34).move_to([0, 0.5, 0])
        note = text("variable renamed: _.0 is shown as x", size=24, color=MUTED).next_to(ans, DOWN, buff=0.2)
        note.align_to(ans, RIGHT)
        with self.voiceover(text=N("s06.b4")) as tr:
            self.play(FadeIn(ans.bg), run_time=0.3)
            self.play(Write(ans.line(0)), Write(ans.line(1)), run_time=1.2)
            self.play(FadeIn(note), run_time=0.4)
            rest(self, tr)

        bx2 = hl(ans.line(1), DATA_C)
        bx1 = hl(ans.line(0), INSTR_C)
        l2 = text("data", size=30, color=DATA_C).next_to(bx2, RIGHT, buff=0.25)
        l1 = text("instructions", size=30, color=INSTR_C).next_to(bx1, RIGHT, buff=0.25)
        l1.next_to(ans.bg, UP, buff=0.12).align_to(ans.bg, RIGHT)
        val = CodePanel(LISP, size=34, highlight=False, stroke=GOOD).move_to([0, -2.4, 0])
        vlab = text("value", size=30, color=GOOD).next_to(val, LEFT, buff=0.25)
        if vlab.get_left()[0] < -FW / 2 + 0.2:
            vlab.next_to(val, UP, buff=0.1).align_to(val, LEFT)
        with self.voiceover(text=N("s06.b5")) as tr:
            self.play(FadeOut(note), Create(bx2), FadeIn(l2), run_time=0.6)
            wait_frac(self, tr, 0.25)
            self.play(Create(bx1), FadeIn(l1), run_time=0.6)
            wait_until(self, tr, "quotes")
            for k in range(2):
                fly = ans.line(1).copy()
                extra = [FadeIn(val.bg), FadeIn(vlab)] if k == 0 else []
                self.play(*extra, fly.animate.move_to(val.lines[k].body()).set_opacity(0),
                          FadeIn(val.lines[k]), run_time=0.9)
                self.remove(fly)
            ok = text("= the expression", size=30, color=GOOD).next_to(val, DOWN, buff=0.15).align_to(val, RIGHT)
            self.play(FadeIn(ok), run_time=0.4)
            rest(self, tr)
        clear(self)


# ---------------------------------------------------------------------------
# s07 The recursion theorem
# ---------------------------------------------------------------------------


class S07Recursion(VoiceoverScene):
    def construct(self):
        self.set_speech_service(get_speech_service())
        sb = self_boxes().move_to([-3.2, 2.6, 0])
        bs = b_steps(28).move_to([2.6, 0.0, 0])
        with self.voiceover(text=N("s07.b1")) as tr:
            self.play(FadeIn(sb), FadeIn(bs), run_time=0.7)
            wait_frac(self, tr, 0.35)
            hl3 = hl(bs.rows[2], PRIMARY)
            self.play(Create(hl3), run_time=0.5)
            wait_until(self, tr, "anything")
            self.play(Create(strike(bs.print_word, width=6)), run_time=0.5)
            rest(self, tr)

        tb = part_box("T", TERTIARY, 2.6, h=1.2)
        s1 = VGroup(Rectangle(width=1.8, height=0.5, color=MUTED, stroke_width=2),
                    text("source code", size=24, color=MUTED))
        s1[1].move_to(s1[0])
        s2 = VGroup(Rectangle(width=1.8, height=0.5, color=MUTED, stroke_width=2), math("y", size=36, color=MUTED))
        s2[1].move_to(s2[0])
        slots = VGroup(s1, s2).arrange(DOWN, buff=0.15)
        tgrp = VGroup(slots, tb).arrange(RIGHT, buff=0.15).move_to([0, 0.3, 0])
        with self.voiceover(text=N("s07.b2")) as tr:
            self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.5)
            self.play(Create(tb.rect), FadeIn(tb.label), run_time=0.6)
            wait_frac(self, tr, 0.45)
            self.play(FadeIn(s1, shift=RIGHT * 0.2), run_time=0.5)
            wait_frac(self, tr, 0.8)
            self.play(FadeIn(s2, shift=RIGHT * 0.2), run_time=0.5)
            rest(self, tr)

        a = part_box("A", DATA_C, 2.0)
        b = part_box("B", INSTR_C, 2.6)
        row = VGroup(a, b).arrange(RIGHT, buff=0)
        tb_new = part_box("T", TERTIARY, 2.6, h=1.2)
        rgrp = VGroup(row, VGroup(slots.copy(), tb_new).arrange(RIGHT, buff=0.15)).arrange(RIGHT, buff=0)
        rgrp.move_to([0, 2.0, 0])
        rlab = text("R", size=44, weight="BOLD").next_to(rgrp, UP, buff=0.2)
        st = strip(width=10.5).move_to([0, -2.6, 0])
        cB = chip("B", INSTR_C, 2.6)
        cT = chip("T", TERTIARY, 2.6)
        cA = chip("A", DATA_C, 2.0)
        VGroup(cB, cT).arrange(RIGHT, buff=0).move_to(st.rect.get_center() + RIGHT * 1.0)
        cA.next_to(cB, LEFT, buff=0)
        yin = math("y", size=44, color=FG).next_to(rgrp, LEFT, buff=0.5)
        with self.voiceover(text=N("s07.b3")) as tr:
            self.play(tgrp.animate.move_to(rgrp[1]), run_time=0.7)
            self.play(FadeIn(row, shift=RIGHT * 0.3), FadeIn(rlab), run_time=0.6)
            wait_frac(self, tr, 0.2)
            self.play(FadeIn(yin, shift=RIGHT * 0.2), FadeIn(st), run_time=0.5)
            wait_frac(self, tr, 0.33)
            self.play(a.rect.animate.set_fill(DATA_C, 0.45), FadeIn(cB, shift=DOWN * 0.3),
                      FadeIn(cT, shift=DOWN * 0.3), run_time=0.7)
            wait_frac(self, tr, 0.5)
            self.play(a.rect.animate.set_fill(DATA_C, 0.12), b.rect.animate.set_fill(INSTR_C, 0.45),
                      FadeIn(cA, shift=RIGHT * 0.5), run_time=0.7)
            wait_until(self, tr, "hands")
            slot1, slot2 = slots[0], slots[1]
            pack = VGroup(cA, cB, cT)
            self.play(pack.animate.scale_to_fit_width(slot1.width * 0.95).move_to(slot1),
                      yin.animate.move_to(slot2[1]), FadeOut(slot2[1]), FadeOut(slot1[1]),
                      b.rect.animate.set_fill(INSTR_C, 0.12), tb.rect.animate.set_fill(TERTIARY, 0.4),
                      run_time=1.0)
            rest(self, tr)

        head = text("Recursion theorem", size=48, color=PRIMARY, weight="BOLD").move_to([0, 2.4, 0])
        f1 = math(r"\text{for every } T \text{ there is } R \text{ with } R(y) = T(\langle R\rangle, y)", size=46)
        f2 = math(r"\langle R\rangle = \text{the source code of } R", size=36, color=MUTED)
        f3 = text("any program can use its own source code", size=40)
        fs = VGroup(f1, f2, f3).arrange(DOWN, buff=0.45).next_to(head, DOWN, buff=0.6)
        with self.voiceover(text=N("s07.b4")) as tr:
            self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.5)
            self.play(FadeIn(head), Write(f1), run_time=1.2)
            self.play(FadeIn(f2), run_time=0.5)
            wait_frac(self, tr, 0.5)
            self.play(FadeIn(f3, shift=UP * 0.2), run_time=0.6)
            rest(self, tr)
        clear(self)


# ---------------------------------------------------------------------------
# s08 You can't list the shortest programs
# ---------------------------------------------------------------------------


class S08Shortest(VoiceoverScene):
    def construct(self):
        self.set_speech_service(get_speech_service())
        long_p = prog_bar(6.0, MUTED)
        short_p = prog_bar(2.2, FG)
        pair = VGroup(long_p, short_p).arrange(DOWN, buff=0.7, aligned_edge=LEFT).move_to([-0.6, 0.4, 0])
        same = text("same behavior", size=30, color=MUTED).next_to(pair, LEFT, buff=0.4)
        brace = Brace(pair, LEFT, color=MUTED)
        same.next_to(brace, LEFT, buff=0.2)
        stc = star().next_to(short_p, RIGHT, buff=0.35)
        stl = text("shortest", size=32, color=PRIMARY).next_to(stc, RIGHT, buff=0.2)
        with self.voiceover(text=N("s08.b1")) as tr:
            self.play(GrowFromEdge(long_p, LEFT), GrowFromEdge(short_p, LEFT), run_time=0.8)
            self.play(GrowFromCenter(brace), FadeIn(same), run_time=0.5)
            wait_frac(self, tr, 0.55)
            self.play(FadeIn(stc, scale=1.5), FadeIn(stl), run_time=0.6)
            rest(self, tr)

        claim = text("No program can list all the shortest programs.", size=42).move_to([0, 3.2, 0])
        with self.voiceover(text=N("s08.b2")) as tr:
            self.play(FadeOut(VGroup(long_p, short_p, same, brace, stc, stl)), run_time=0.4)
            self.play(FadeIn(claim, shift=DOWN * 0.2), run_time=0.7)
            rest(self, tr)

        ebox = part_box("E", FG, 1.6, h=1.6, size=48).move_to([-5.0, 0.0, 0])
        bars = e_lister(n=10, x0=-3.4, top=2.2, gap=0.48, longest=7)
        mark_x = -3.4 + 4.4
        mline = DashedLine([mark_x, 2.4, 0], [mark_x, -2.5, 0], color=PRIMARY, dash_length=0.12)
        mlab = text("any length", size=28, color=PRIMARY).next_to(mline, DOWN, buff=0.1)
        with self.voiceover(text=N("s08.b3")) as tr:
            self.play(FadeIn(ebox), run_time=0.5)
            n_first = 7
            per = max(0.2, (tr.time_until_bookmark("longer") - 0.8) / n_first)
            for i in range(n_first):
                self.play(GrowFromEdge(bars[i], LEFT), run_time=min(0.5, per * 0.7))
                if per * 0.3 > 0.05:
                    self.wait(per * 0.3)
            wait_until(self, tr, "longer")
            self.play(Create(mline), FadeIn(mlab), run_time=0.5)
            self.play(GrowFromEdge(bars[7], LEFT), run_time=0.6)
            self.play(bars[7].bar.animate.set_fill(PRIMARY), run_time=0.3)
            self.play(LaggedStart(*[GrowFromEdge(b, LEFT) for b in bars[8:]], lag_ratio=0.5), run_time=0.6)
            rest(self, tr)

        cs = c_steps(30, width=9.6).move_to([1.3, -0.3, 0])
        tag = text("recursion theorem", size=26, color=TERTIARY)
        with self.voiceover(text=N("s08.b4")) as tr:
            self.play(FadeOut(VGroup(bars, mline, mlab)), ebox.animate.scale(0.7).move_to([-5.6, 2.0, 0]),
                      run_time=0.6)
            self.play(FadeIn(cs.bg), FadeIn(cs[1][0]), run_time=0.5)
            for i, mk in enumerate(["one", "two", "three"]):
                wait_until(self, tr, mk)
                self.play(FadeIn(cs.rows[i], shift=RIGHT * 0.2), run_time=0.5)
                if i == 0:
                    arr = Arrow(RIGHT, LEFT, buff=0, color=TERTIARY, stroke_width=3, tip_length=0.18).scale(0.35)
                    arr.next_to(cs.rows[0], RIGHT, buff=0.3)
                    tag.next_to(arr, RIGHT, buff=0.15)
                    self.play(FadeIn(tag), GrowArrow(arr), run_time=0.5)
            rest(self, tr)

        cbar = prog_bar(2.4, PRIMARY, label="C")
        dbar = prog_bar(5.2, FG, label="D")
        cd = VGroup(cbar, dbar).arrange(DOWN, buff=0.5, aligned_edge=LEFT)
        cd.move_to([0.6, -2.6, 0])
        for g in (cbar, dbar):
            g[1].next_to(g.bar, LEFT, buff=0.25)
        same2 = text("same behavior", size=28, color=MUTED).next_to(cd, RIGHT, buff=0.4)
        dstar = star().next_to(dbar.bar, RIGHT, buff=0.25)
        same2.next_to(dstar, RIGHT, buff=0.4)
        with self.voiceover(text=N("s08.b5")) as tr:
            self.play(cs.animate.scale(0.8).move_to([1.0, 1.0, 0]), FadeOut(tag), FadeOut(arr), run_time=0.6)
            self.play(GrowFromEdge(cbar.bar, LEFT), FadeIn(cbar[1]), GrowFromEdge(dbar.bar, LEFT), FadeIn(dbar[1]),
                      FadeIn(dstar), run_time=0.8)
            self.play(FadeIn(same2), run_time=0.4)
            wait_until(self, tr, "isnt")
            crack = VMobject(color=BG, stroke_width=5).set_points_as_corners(
                [dstar.get_top(), dstar.get_center() + LEFT * 0.08, dstar.get_center() + RIGHT * 0.06,
                 dstar.get_bottom()])
            self.play(dstar.animate.set_fill(BAD).set_stroke(BAD), Create(crack), run_time=0.6)
            wait_until(self, tr, "exist")
            self.play(Create(cross(ebox, width=7)), run_time=0.5)
            rest(self, tr)

        with self.voiceover(text=N("s08.b6")) as tr:
            self.play(FadeOut(VGroup(cbar, dbar, same2, dstar, crack)), cs.animate.scale(1.25).move_to([0.5, -0.4, 0]),
                      run_time=0.7)
            glow = SurroundingRectangle(cs.rows[0], color=PRIMARY, buff=0.1, corner_radius=0.06)
            self.play(Create(glow), cs.rows[0].animate.set_color(PRIMARY), run_time=0.6)
            rest(self, tr)
        clear(self)


# ---------------------------------------------------------------------------
# s09 Ending
# ---------------------------------------------------------------------------


class S09Ending(VoiceoverScene):
    def construct(self):
        self.set_speech_service(get_speech_service())
        sb = self_boxes().move_to([0, 0.6, 0])
        g = math(r"G", r"\;\leftrightarrow\;", r"\neg\,\exists p\;\, \mathrm{Proof}(p,\ ", r"\ulcorner G \urcorner",
                 r")", size=64)
        g[0].set_color(PRIMARY)
        g[3].set_color(PRIMARY)
        g.move_to([0, 0.6, 0])
        cap = text("a sentence that says: I have no proof", size=40, color=MUTED).move_to([0, -1.2, 0])
        with self.voiceover(text=N("s09.b1")) as tr:
            self.play(FadeIn(sb), run_time=0.6)
            wait_frac(self, tr, 0.15)
            self.play(FadeTransform(sb, g), run_time=1.2)
            self.play(FadeIn(cap, shift=UP * 0.2), run_time=0.6)
            wait_frac(self, tr, 0.7)
            self.play(Indicate(g[3], color=PRIMARY, scale_factor=1.2), run_time=1.0)
            rest(self, tr)
        self.wait(0.8)
        clear(self, run_time=0.8)


# ---------------------------------------------------------------------------
# Thumbnail
# ---------------------------------------------------------------------------


class Thumbnail(Scene):
    def construct(self):
        head = text("This program prints itself", size=78, weight="BOLD").move_to([0, 2.7, 0])
        qp = quine_panel(16)
        qp.scale_to_fit_width(FW - 0.8).move_to([0, -0.4, 0])
        tag = text("character for character", size=40, color=PRIMARY).next_to(qp, DOWN, buff=0.35)
        self.add(head, qp, tag)
