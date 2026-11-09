"""Code panels: monospace source with simple keyword coloring and handles on substrings.

    p = CodePanel(["theorem foo : P -> P :=", "  fun p => p"], size=28)
    p.part(1, "fun p")       # the glyphs of that substring, to highlight or move
    p.line(0)                # one whole line
    p.box_part(1, "p => p")  # a rectangle around a substring

Text keeps one submobject per character (spaces included), so a substring's glyphs
are a slice of the line. Leading spaces are dropped by Text, so indentation is a shift.
"""

import re

from manim import (
    DOWN,
    LEFT,
    RIGHT,
    UP,
    RoundedRectangle,
    SurroundingRectangle,
    Text,
    VGroup,
)

from mathvid.style import FG, MUTED, PRIMARY, SECONDARY, BAD

MONO = "DejaVu Sans Mono"
PANEL_BG = "#1C1F26"
TYPE_C = "#C9A0DC"

KEYWORDS = {
    "theorem", "def", "fun", "match", "with", "inductive", "where", "if", "then", "else",
    "let", "have", "by", "example", "open", "in", "class", "structure", "noncomputable",
    "#eval", "#check", "#print", "nomatch",
}
SORTS = {"Prop", "Type", "Sort", "Nat", "Bool", "String", "List", "Fin", "True", "False"}
TOKEN = re.compile(r"#?[A-Za-z_][A-Za-z0-9_'.]*|--.*$")


def mono(s, size=28, color=FG):
    return Text(s, font=MONO, font_size=size, color=color, disable_ligatures=True)


def char_width(size=28):
    return mono("x" * 20, size).width / 20


class CodeLine(VGroup):
    """One line of code. A hidden "M" is prepended so every line shares a baseline
    and leading spaces survive (Text drops them otherwise)."""

    def __init__(self, src, size=28, color=FG, highlight=True):
        super().__init__()
        self.src = src
        self.text = mono("M" + src, size, color)
        self.anchor = self.text[0]
        self.anchor.set_opacity(0)
        self.add(self.text)
        if highlight:
            for m in TOKEN.finditer(src):
                w = m.group(0)
                col = None
                if w.startswith("--"):
                    col = MUTED
                elif w in KEYWORDS:
                    col = SECONDARY
                elif w in SORTS:
                    col = TYPE_C
                if col:
                    self.text[1 + m.start():1 + m.end()].set_color(col)

    def span(self, sub, nth=0):
        """Glyphs of the nth occurrence of sub in this line."""
        i = -1
        for _ in range(nth + 1):
            i = self.src.find(sub, i + 1)
            if i < 0:
                raise ValueError(f"{sub!r} not in {self.src!r}")
        return self.text[1 + i:1 + i + len(sub)]

    def body(self):
        return self.text[1:]


class CodePanel(VGroup):
    """A dark rounded panel holding lines of code, left aligned."""

    def __init__(self, lines, size=28, line_buff=0.16, pad=0.32, color=FG, highlight=True,
                 bg=PANEL_BG, stroke=MUTED, min_width=0):
        super().__init__()
        self.size = size
        cw = char_width(size)
        h = mono("Mg", size).height
        self.lines = VGroup()
        for i, src in enumerate(lines):
            ln = CodeLine(src, size, color, highlight)
            ln.shift(-ln.anchor.get_corner(DOWN + LEFT) + DOWN * i * (h + line_buff) + LEFT * cw)
            self.lines.add(ln)
        vis = VGroup(*[ln.body() for ln in self.lines])
        left = -cw * 0  # code starts at x = 0
        w = max(max((ln.body().get_right()[0] for ln in self.lines if len(ln.src.strip())), default=0) - left,
                min_width)
        top = max(ln.anchor.get_top()[1] for ln in self.lines)
        bot = min(ln.anchor.get_bottom()[1] for ln in self.lines) - h * 0.3
        self.bg = RoundedRectangle(corner_radius=0.15, width=w + 2 * pad, height=top - bot + 2 * pad,
                                   stroke_color=stroke, stroke_width=2, fill_color=bg, fill_opacity=1)
        self.bg.move_to([left + w / 2, (top + bot) / 2, 0])
        self.add(self.bg, self.lines)
        self.center()

    def line(self, i):
        return self.lines[i].body()

    def part(self, i, sub, nth=0):
        return self.lines[i].span(sub, nth)

    def box_part(self, i, sub, color=PRIMARY, buff=0.06, nth=0):
        return SurroundingRectangle(self.part(i, sub, nth), color=color, buff=buff, stroke_width=3,
                                    corner_radius=0.05)


def output_line(s, size=28, color=PRIMARY):
    return mono(s, size, color)


def error_text(lines, size=24, color=BAD):
    """A red error message, already broken into lines."""
    g = VGroup(*[mono(l, size, color) for l in lines]).arrange(DOWN, buff=0.1, aligned_edge=LEFT)
    return g
