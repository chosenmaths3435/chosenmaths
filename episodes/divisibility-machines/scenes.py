"""A divisibility test for any number: remainder machines and finite state machines.

Long-form scenes. Builders here are shared with shorts.py.
"""

import random

import numpy as np
from manim import *
from manim_voiceover import VoiceoverScene

from mathvid import layout  # noqa: F401  must come before scene code runs
from mathvid.anim import rest, rt, strike, wait_until
from mathvid.automata import Machine, glow_dot, remainder_machine, ring, run_states
from mathvid.layout import FH, FW
from mathvid.orders import cross, tick
from mathvid.script import Script
from mathvid.style import BAD, BG, FG, GOOD, MUTED, PRIMARY, SECONDARY, TERTIARY, math, text
from mathvid.voice import get_speech_service

N = Script(__file__)

TITLE = "A divisibility test for any number"
ONE_C = SECONDARY   # arrows that move one step (mod 3)
TWO_C = TERTIARY    # arrows that move two steps (mod 3)


# ---------------------------------------------------------------------------
# Timing helpers
# ---------------------------------------------------------------------------


def elapsed(tr):
    return tr.duration - tr.get_remaining_duration()


def wait_frac(scene, tr, f):
    """Hold until fraction f of this beat's narration has passed."""
    t = f * tr.duration - elapsed(tr)
    if t > 0.05:
        scene.wait(t)


def freeze(scene):
    for m in scene.mobjects:
        for s in m.get_family():
            s.clear_updaters()


def clear(scene, run_time=0.5, keep=()):
    freeze(scene)
    gone = [m for m in scene.mobjects if m not in keep]
    if gone:
        scene.play(*[FadeOut(m) for m in gone], run_time=run_time)


# ---------------------------------------------------------------------------
# Builders
# ---------------------------------------------------------------------------


def mod3_machine(radius=2.7, r=0.5, size=32, center=ORIGIN, start=True, bend=0.9):
    """The digit-sum machine: one step for 1, 4, 7; two steps for 2, 5, 8; stay for 0, 3, 6, 9."""
    m = Machine(ring(3, radius, center), r=r)
    m.one, m.two, m.loops = VGroup(), VGroup(), VGroup()
    for q in range(3):
        m.one.add(m.add_edge(q, (q + 1) % 3, "1, 4, 7", bend=bend, color=ONE_C, size=size,
                             on_path=True, width=3.5))
        m.two.add(m.add_edge(q, (q + 2) % 3, "2, 5, 8", bend=bend, color=TWO_C, size=size,
                             on_path=True, width=3.5))
        m.loops.add(m.add_edge(q, q, "0, 3, 6, 9", size=size, width=3.5))
    if start:
        m.add_start(0, LEFT, length=0.8)
    return m


def mod7_machine(radius=2.6, r=0.38, center=ORIGIN, opacity=0.55):
    """All of the mod 7 machine, arrows unlabelled (the active one gets a note)."""
    return remainder_machine(7, radius=radius, r=r, center=center, labels=False,
                             opacity=opacity, width=2.2)


def digit_row(s, size=64, color=FG):
    return text(s, size=size, color=color)


def read_digit(row, i, color=PRIMARY):
    """Animations that light digit i of a digit row and dim the ones before it."""
    out = [row[i].animate.set_color(color)]
    if i > 0:
        out.append(row[i - 1].animate.set_color(MUTED))
    return out


def run_digits(scene, tr, m, digits, row, marks=None, notes=None, lines=None, start=0,
               n=None, total=None, line_pos=None):
    """Run machine m on a digit string, one hop per digit.

    With marks, hop i starts at bookmark marks[i]; otherwise the hops share `total`
    seconds. notes[i] is shown beside the arrow; lines[i] (a mobject) fades in at hop i."""
    states = run_states(n, digits, start=start) if n else None
    k = len(digits)
    for i in range(k):
        if marks:
            wait_until(scene, tr, marks[i])
            nxt = (tr.time_until_bookmark(marks[i + 1]) if i + 1 < k
                   else tr.get_remaining_duration())
            dt = min(1.0, max(0.35, nxt - 0.05))
        else:
            dt = total / k
        a, b = states[i], states[i + 1]
        scene.play(*read_digit(row, i), *( [FadeIn(lines[i], shift=UP * 0.1)] if lines else []),
                   run_time=0.2 * dt)
        m.hop(scene, a, b, run_time=0.8 * dt, note=notes[i] if notes else None)
    return states


def pulse(scene, m, k, color=GOOD, run_time=0.6):
    scene.play(m.circles[k].animate.set_fill(color, 0.5).set_stroke(color), run_time=run_time / 2)
    scene.play(Indicate(m.nodes[k], color=color, scale_factor=1.25), run_time=run_time / 2)


def rule_tex(rhs, size=40, lhs="r"):
    """r --d--> <rhs> as a split MathTex: [r, arrow, 'remainder of', rhs...]."""
    parts = [lhs, r"\xrightarrow{\;d\;}", r"\text{remainder of }"] + list(rhs)
    return math(*parts, size=size)


def cat_machine(scale=1.0, center=ORIGIN):
    xs = [-4.2, -1.4, 1.4, 4.2]
    pos = {k: np.array([x, 0, 0]) + center for k, x in zip(["s", "c", "ca", "cat"], xs)}
    m = Machine(pos, labels={"s": "", "c": "c", "ca": "ca", "cat": "cat"}, r=0.5, label_size=36)
    m.main = VGroup(
        m.add_edge("s", "c", "c", size=32, color=FG),
        m.add_edge("c", "ca", "a", size=32, color=FG),
        m.add_edge("ca", "cat", "t", size=32, color=FG),
        m.add_edge("cat", "cat", "any", size=26, color=FG, loop_dir=UP),
    )
    faint = dict(color=MUTED, opacity=0.5, size=24)
    m.faint = VGroup(
        m.add_edge("s", "s", "other", loop_dir=UP, **faint),
        m.add_edge("c", "s", "other", bend=-0.9, **faint),
        m.add_edge("ca", "s", "other", bend=-0.75, **faint),
        m.add_edge("c", "c", "c", loop_dir=UP, **faint),
        m.add_edge("ca", "c", "c", bend=0.9, **faint),
    )
    m.add_start("s", LEFT, length=0.7)
    m.add_accept("cat")
    m.scale(scale)
    return m


def parity_machine(scale=1.0, center=ORIGIN):
    pos = {"e": np.array([-1.5, 0, 0]) + center, "o": np.array([1.5, 0, 0]) + center}
    m = Machine(pos, labels={"e": "even", "o": "odd"}, r=0.6, label_size=30)
    m.add_edge("e", "o", "1", bend=0.6, size=32, color=FG)
    m.add_edge("o", "e", "1", bend=0.6, size=32, color=FG)
    m.add_edge("e", "e", "0", loop_dir=UP, size=32, color=MUTED)
    m.add_edge("o", "o", "0", loop_dir=UP, size=32, color=MUTED)
    m.add_start("e", LEFT, length=0.7)
    m.add_accept("e")
    m.scale(scale)
    return m


def paren_pair(size=72):
    good = text("(()())", size=size)
    bad = text("(()", size=size)
    VGroup(good, bad).arrange(DOWN, buff=0.7)
    return good, bad


class ParenBox(VGroup):
    """A machine seen from outside: a box with k dots in it."""

    def __init__(self, cols=3, rows=2, w=4.6, h=3.4, k_label="k states", size=34):
        super().__init__()
        self.box = RoundedRectangle(width=w, height=h, corner_radius=0.3, color=MUTED,
                                    stroke_width=3)
        self.dots = VGroup(*[Dot(radius=0.2, color=FG) for _ in range(cols * rows)])
        self.dots.arrange_in_grid(rows=rows, cols=cols, buff=(w / (cols + 0.2), h / (rows + 1.1)))
        self.dots.move_to(self.box)
        self.label = text(k_label, size=size, color=MUTED).next_to(self.box, UP, buff=0.2)
        self.add(self.box, self.dots, self.label)


def paren_strings(n=7, size=40):
    return VGroup(*[text("(" * (i + 1), size=size) for i in range(n)])


# landing dot of each string: strings 3 and 7 collide (i = 3, j = 7)
LAND = [0, 1, 2, 3, 4, 5, 2]
I_IDX, J_IDX = 2, 6


def feed_strings(scene, box, strs, which, run_time):
    """Glows from each string in `which` into its dot in the box."""
    for idx in which:
        g = glow_dot(PRIMARY).move_to(strs[idx].get_right() + RIGHT * 0.2)
        tgt = box.dots[LAND[idx]]
        path = Line(g.get_center(), tgt.get_center())
        scene.add(g)
        scene.play(strs[idx].animate.set_color(PRIMARY), MoveAlongPath(g, path),
                   run_time=run_time * 0.75)
        scene.play(FadeOut(g), tgt.animate.set_color(SECONDARY),
                   strs[idx].animate.set_color(FG), run_time=run_time * 0.25)


# ---------------------------------------------------------------------------
# Scenes
# ---------------------------------------------------------------------------

M7_C = np.array([-2.4, -0.2, 0])
RIGHT_X = 3.9


class S01Hook(VoiceoverScene):
    def construct(self):
        self.set_speech_service(get_speech_service())
        lines = VGroup(
            text("3:  add the digits", size=56),
            text("5:  look at the last digit", size=56),
            text("7:  ?", size=56, color=PRIMARY),
        ).arrange(DOWN, buff=0.6, aligned_edge=LEFT).move_to(ORIGIN)
        with self.voiceover(text=N("s01.b1")) as tr:
            self.play(FadeIn(lines[0], shift=RIGHT * 0.2), run_time=0.6)
            wait_frac(self, tr, 0.42)
            self.play(FadeIn(lines[1], shift=RIGHT * 0.2), run_time=0.6)
            wait_until(self, tr, "seven")
            self.play(FadeIn(lines[2], shift=RIGHT * 0.2), run_time=0.5)
            rest(self, tr)

        m = mod7_machine(center=M7_C)
        num = digit_row("1729", size=96).move_to([RIGHT_X, 1.2, 0])
        q = text("divisible by 7?", size=40, color=MUTED).next_to(num, DOWN, buff=0.35)
        with self.voiceover(text=N("s01.b2")) as tr:
            self.play(FadeOut(lines), run_time=0.4)
            self.play(FadeIn(m.node_layer), Create(m.edge_layer, lag_ratio=0.02),
                      FadeIn(num), FadeIn(q), run_time=1.6)
            m.light(self, 0, run_time=0.3)
            wait_until(self, tr, "feed")
            total = max(2.0, tr.get_remaining_duration() - 1.4)
            run_digits(self, tr, m, "1729", num, n=7, total=total)
            pulse(self, m, 0)
            yes = text("7 divides 1729", size=40, color=GOOD).move_to(q)
            self.play(ReplacementTransform(q, yes), run_time=0.4)
            rest(self, tr)

        with self.voiceover(text=N("s01.b3")) as tr:
            clear(self, run_time=0.5)
            t = text(TITLE, size=60, weight="BOLD")
            self.play(FadeIn(t, shift=UP * 0.2), run_time=0.8)
            rest(self, tr)
            self.play(FadeOut(t), run_time=0.4)


M3_C = np.array([0, -0.6, 0])


class S02MachineFor3(VoiceoverScene):
    def construct(self):
        self.set_speech_service(get_speech_service())
        m = mod3_machine(center=M3_C)
        with self.voiceover(text=N("s02.b1")) as tr:
            self.play(FadeIn(m.node_layer), run_time=0.8)
            wait_until(self, tr, "one")
            self.play(Create(VGroup(*[e.arrow for e in m.one])),
                      FadeIn(VGroup(*[e.label for e in m.one])), run_time=1.0)
            wait_until(self, tr, "two")
            self.play(Create(VGroup(*[e.arrow for e in m.two])),
                      FadeIn(VGroup(*[e.label for e in m.two])), run_time=1.0)
            wait_until(self, tr, "loop")
            self.play(Create(VGroup(*[e.arrow for e in m.loops])),
                      FadeIn(VGroup(*[e.label for e in m.loops])), run_time=1.0)
            rest(self, tr)

        num = digit_row("4812", size=110).move_to([RIGHT_X + 1.1, 0.9, 0])
        with self.voiceover(text=N("s02.b2")) as tr:
            self.play(FadeIn(m.start), run_time=0.5)
            m.light(self, 0)
            wait_frac(self, tr, 0.35)
            self.play(FadeIn(num), run_time=0.5)
            run_digits(self, tr, m, "4812", num, marks=["d1", "d2", "d3", "d4"], n=3)
            rest(self, tr)

        eq = math(r"4812 = 3 \times 1604", size=52, color=GOOD).next_to(num, DOWN, buff=0.5)
        with self.voiceover(text=N("s02.b3")) as tr:
            pulse(self, m, 0)
            wait_frac(self, tr, 0.5)
            self.play(FadeIn(eq, shift=UP * 0.1), num.animate.set_color(FG), run_time=0.6)
            rest(self, tr)

        rows = VGroup(*[
            VGroup(text(p, size=56), text("leaves", size=42, color=MUTED),
                   text(str(int(p) % 3), size=56, color=PRIMARY)).arrange(RIGHT, buff=0.35)
            for p in ["4", "48", "481", "4812"]
        ]).arrange(DOWN, buff=0.5, aligned_edge=RIGHT).move_to([3.4, -0.6, 0])
        head4 = VGroup(text("each dot:", size=40, color=MUTED),
                       text("the remainder so far", size=44, color=PRIMARY)).arrange(DOWN, buff=0.15)
        head4.move_to([3.4, 2.7, 0])
        with self.voiceover(text=N("s02.b4")) as tr:
            m.light(self, None, run_time=0.2)
            self.play(FadeOut(num), FadeOut(eq), m.animate.scale(0.7).move_to([-3.5, -0.3, 0]),
                      run_time=0.8)
            wait_frac(self, tr, 0.12)
            self.play(FadeIn(head4, shift=DOWN * 0.1), run_time=0.6)
            for i, mk in enumerate(["r1", "r2", "r3"]):
                wait_until(self, tr, mk)
                self.play(FadeIn(rows[i], shift=LEFT * 0.2), *m.light_anims(int(rows[i][2].text)),
                          run_time=0.5)
            wait_frac(self, tr, 0.97)
            self.play(FadeIn(rows[3], shift=LEFT * 0.2), *m.light_anims(0), run_time=0.4)
            rest(self, tr)

        l1 = math(r"x", r"\;\longrightarrow\;", r"10x + d", size=60)
        cap1 = text("read one more digit d", size=36, color=MUTED)
        l2 = math(r"10x", "=", r"9x", "+", "x", size=60)
        l3 = rule_tex([r"r + d"], size=48)
        col = VGroup(VGroup(cap1, l1).arrange(DOWN, buff=0.25), l2, l3).arrange(DOWN, buff=0.8)
        col.move_to([3.2, 0, 0])
        brace = Brace(l2[2], DOWN, buff=0.1, color=MUTED)
        blab = text("multiple of 3", size=32, color=MUTED).next_to(brace, DOWN, buff=0.1)
        with self.voiceover(text=N("s02.b5")) as tr:
            self.play(FadeOut(rows), FadeOut(head4), *m.light_anims(None), run_time=0.5)
            self.play(FadeIn(cap1), FadeIn(l1[0]), run_time=0.5)
            wait_until(self, tr, "tenx")
            self.play(FadeIn(l1[1:]), run_time=0.6)
            wait_until(self, tr, "nine")
            self.play(FadeIn(l2), run_time=0.6)
            self.play(GrowFromCenter(brace), FadeIn(blab), run_time=0.6)
            wait_until(self, tr, "plus")
            self.play(FadeIn(l3, shift=UP * 0.1), run_time=0.6)
            rest(self, tr)

        ds = VGroup(text("walking the arrows", size=44, color=MUTED), text("=", size=56, color=MUTED),
                    text("digit sum", size=60, color=PRIMARY)).arrange(DOWN, buff=0.25)
        with self.voiceover(text=N("s02.b6")) as tr:
            self.play(FadeOut(VGroup(col, brace, blab)), m.animate.scale(1 / 0.7).move_to([-2.0, M3_C[1] + 0.25, 0]),
                      run_time=0.9)
            ds.move_to([4.6, 0, 0])
            self.play(FadeIn(ds, shift=UP * 0.1), run_time=0.6)
            rest(self, tr)
        clear(self)


M5_C = np.array([-2.6, 0.0, 0])


class S03AnyNumber(VoiceoverScene):
    def construct(self):
        self.set_speech_service(get_speech_service())
        labels = ["0", "1", "2", "", "n-1"]
        xs = [-4.5, -2.7, -0.9, 1.2, 3.3]
        row = VGroup()
        for x, lab in zip(xs, labels):
            if lab == "":
                row.add(text("...", size=44, color=MUTED).move_to([x, 1.6, 0]))
            else:
                c = Circle(radius=0.48, color=FG, stroke_width=4).move_to([x, 1.6, 0])
                row.add(VGroup(c, text(lab, size=34).move_to(c)))
        ra = Machine({"r": [-1.6, -0.6, 0], "s": [2.4, -0.6, 0]}, labels={"r": "r", "s": ""}, r=0.48)
        e = ra.add_edge("r", "s", "d", bend=-0.5, size=36, color=PRIMARY, width=4)
        rule = rule_tex([r"10r", r"+ d"], size=54).move_to([0, -3.0, 0])
        qmark = math(r"?", size=40, color=MUTED).move_to(ra.pos["s"])
        with self.voiceover(text=N("s03.b1")) as tr:
            self.play(LaggedStart(*[FadeIn(x) for x in row], lag_ratio=0.15), run_time=1.4)
            wait_until(self, tr, "rule")
            self.play(FadeIn(ra.node_layer), FadeIn(qmark), Create(e.arrow), FadeIn(e.label), run_time=0.8)
            self.play(FadeIn(rule, shift=UP * 0.1), run_time=0.6)
            rest(self, tr)

        m = Machine(ring(5, 2.1, M5_C), r=0.42)
        into3 = VGroup(*[m.add_edge(q, 3, "3, 8" if q == 3 else None, bend=0.0 if q in (2, 4) else 0.35,
                                    color=ONE_C, size=32, width=3.5) for q in range(5)])
        into0 = VGroup(*[m.add_edge(q, 0, "0, 5" if q == 0 else None, bend=0.0 if q in (1, 4) else 0.35,
                                    color=TWO_C, size=32, width=3.5) for q in range(5)])
        rule5 = rule.copy()
        with self.voiceover(text=N("s03.b2")) as tr:
            self.play(FadeOut(row), FadeOut(ra.node_layer), FadeOut(qmark), FadeOut(e), run_time=0.5)
            self.play(FadeIn(m.node_layer), rule.animate.scale(0.92).move_to([3.6, -0.4, 0]), run_time=0.8)
            wait_until(self, tr, "drops")
            s = strike(rule[3], width=6)
            self.play(Create(s), rule[3].animate.set_opacity(0.4), run_time=0.6)
            wait_until(self, tr, "three")
            self.play(Create(VGroup(*[x.arrow for x in into3])), FadeIn(into3[3].label), run_time=1.0)
            wait_until(self, tr, "zero")
            self.play(Create(VGroup(*[x.arrow for x in into0])), FadeIn(into0[0].label), run_time=1.0)
            rest(self, tr)

        last = text("last digit 0 or 5", size=52, color=TWO_C).move_to([RIGHT_X, 1.4, 0])
        with self.voiceover(text=N("s03.b3")) as tr:
            wait_frac(self, tr, 0.3)
            self.play(FadeIn(last, shift=LEFT * 0.2), run_time=0.6)
            rest(self, tr)

        m7 = mod7_machine(center=M7_C)
        ten = math(r"10", r"\to", r"\text{remainder } 3", size=54).move_to([RIGHT_X, 1.6, 0])
        rule7 = rule_tex([r"3r", r"+ d"], size=50).move_to([RIGHT_X, 0.3, 0])
        with self.voiceover(text=N("s03.b4")) as tr:
            clear(self)
            self.play(FadeIn(ten), FadeIn(m7.node_layer), run_time=0.6)
            wait_frac(self, tr, 0.3)
            self.play(FadeIn(rule7, shift=UP * 0.1), run_time=0.6)
            wait_until(self, tr, "whole")
            self.play(Create(m7.edge_layer, lag_ratio=0.03), run_time=2.0)
            rest(self, tr)

        num = digit_row("1729", size=90).move_to([RIGHT_X, 2.9, 0])
        steps = VGroup(
            math(r"3 \cdot 0 + 1 = 1", size=50),
            math(r"3 \cdot 1 + 7 = 10 \to 3", size=50),
            math(r"3 \cdot 3 + 2 = 11 \to 4", size=50),
            math(r"3 \cdot 4 + 9 = 21 \to 0", size=50),
        ).arrange(DOWN, buff=0.35, aligned_edge=LEFT).move_to([RIGHT_X, -1.3, 0])
        with self.voiceover(text=N("s03.b5")) as tr:
            self.play(*m7.fade_edges(0.3), FadeOut(ten),
                      rule7.animate.move_to([RIGHT_X, 1.75, 0]), FadeIn(num), run_time=0.8)
            m7.light(self, 0)
            run_digits(self, tr, m7, "1729", num, marks=["d1", "d2", "d3", "d4"], n=7,
                       notes=list("1729"), lines=steps)
            pulse(self, m7, 0)
            rest(self, tr)

        m11 = remainder_machine(11, radius=2.75, r=0.32, center=M7_C, labels=False, opacity=0.22,
                                width=1.8, bend=0.3)
        minus = math(r"10", r"\to", r"\text{remainder } 10", r"= -1", size=50).move_to([RIGHT_X, 3.0, 0])
        rule11 = rule_tex([r"d - r"], size=50).move_to([RIGHT_X, 1.9, 0])
        num11 = digit_row("1331", size=80).move_to([RIGHT_X, 0.7, 0])
        alt = VGroup(
            math(r"1", size=48),
            math(r"3 - 1 = 2", size=48),
            math(r"3 - 3 + 1 = 1", size=48),
            math(r"1 - 3 + 3 - 1 = 0", size=48),
        ).arrange(DOWN, buff=0.28, aligned_edge=RIGHT).move_to([RIGHT_X, -1.75, 0])
        with self.voiceover(text=N("s03.b6")) as tr:
            clear(self)
            self.play(FadeIn(m11), run_time=1.0)
            wait_until(self, tr, "minus")
            self.play(FadeIn(minus), run_time=0.6)
            self.play(FadeIn(rule11, shift=UP * 0.1), run_time=0.6)
            wait_until(self, tr, "run")
            self.play(FadeIn(num11), run_time=0.4)
            m11.light(self, 0, run_time=0.2)
            states = [0]
            for ch in "1331":
                states.append((int(ch) - states[-1]) % 11)
            per = max(0.6, min(1.4, (tr.get_remaining_duration() - 3.0) / 4))
            for i in range(4):
                self.play(*read_digit(num11, i), FadeIn(alt[i], shift=UP * 0.1), run_time=0.2 * per)
                m11.hop(self, states[i], states[i + 1], run_time=0.8 * per, note="1331"[i])
            pulse(self, m11, 0)
            rest(self, tr)
        clear(self)


class S04FiniteStateMachines(VoiceoverScene):
    def construct(self):
        self.set_speech_service(get_speech_service())
        m = mod7_machine(center=M7_C)
        tags = VGroup(
            text("states", size=44, color=SECONDARY),
            VGroup(text("input", size=44, color=PRIMARY), text("1 7 2 9", size=44)).arrange(RIGHT, buff=0.4),
            text("transitions", size=44, color=TERTIARY),
            text("accept: end on 0", size=44, color=GOOD),
        ).arrange(DOWN, buff=0.6, aligned_edge=LEFT).move_to([RIGHT_X, 0, 0])
        with self.voiceover(text=N("s04.b1")) as tr:
            self.play(FadeIn(m), run_time=0.8)
            wait_until(self, tr, "states")
            self.play(FadeIn(tags[0]), *[Indicate(c, color=SECONDARY) for c in m.circles.values()],
                      run_time=0.8)
            wait_until(self, tr, "input")
            self.play(FadeIn(tags[1]), run_time=0.6)
            wait_until(self, tr, "arrow")
            m.show_edge(1, 3, color=TERTIARY, width=6)
            self.play(FadeIn(tags[2]), Indicate(m.edges[(1, 3)].arrow, color=TERTIARY, scale_factor=1.05),
                      run_time=0.8)
            wait_until(self, tr, "accept")
            m.restore_edge(1, 3)
            acc = Circle(radius=m.r * 0.8, color=GOOD, stroke_width=3).move_to(m.p(0))
            self.play(FadeIn(tags[3]), Create(acc), m.circles[0].animate.set_stroke(GOOD), run_time=0.8)
            m.nodes[0].add(acc)
            rest(self, tr)

        rng = random.Random(7)
        digits = "".join(str(rng.randrange(10)) for _ in range(400))
        states = run_states(7, digits)
        k = ValueTracker(0)
        strip_x = RIGHT_X
        window = 12

        def strip():
            i = int(k.get_value())
            s = digits[i:i + window]
            t = text(s, size=48, color=FG)
            t.move_to([strip_x, 1.6, 0])
            t[0].set_color(PRIMARY)
            return t

        def mark():
            i = int(k.get_value())
            q = states[i]
            return Circle(radius=m.r, color=PRIMARY, stroke_width=5).set_fill(PRIMARY, 0.35).move_to(m.p(q))

        count = ValueTracker(0)

        def counter():
            v = int(count.get_value())
            return text(f"digits read: {v:,}", size=40, color=MUTED).move_to([strip_x, -1.2, 0])

        with self.voiceover(text=N("s04.b2")) as tr:
            self.wait(0.6)
            self.play(FadeOut(tags), run_time=0.5)
            s_m, mk_m, c_m = always_redraw(strip), always_redraw(mark), always_redraw(counter)
            self.play(FadeIn(s_m), FadeIn(c_m), run_time=0.4)
            self.add(mk_m)
            d = max(2.0, tr.get_remaining_duration() - 0.6)
            self.play(k.animate.set_value(380), count.animate.set_value(1_000_000),
                      rate_func=lambda t: t ** 2.2, run_time=d)
            rest(self, tr)
            freeze(self)
            self.remove(s_m, mk_m, c_m)
            self.add(s_m.copy(), mk_m.copy(), c_m.copy())

        cat = cat_machine()
        cat.move_to([0.7, 1.1, 0])
        par = parity_machine().move_to([0.7, -2.2, 0])
        with self.voiceover(text=N("s04.b3")) as tr:
            others = [x for x in self.mobjects if x is not m]
            self.play(*[FadeOut(x) for x in others], m.animate.scale(0.38).to_corner(UL, buff=0.3),
                      run_time=0.8)
            wait_until(self, tr, "cat")
            self.play(FadeIn(cat.node_layer), FadeIn(cat.extra), Create(cat.main), run_time=1.0)
            self.play(FadeIn(cat.faint), run_time=0.6)
            wait_until(self, tr, "even")
            self.play(FadeIn(par), run_time=0.8)
            rest(self, tr)

        head = text("language", size=56, color=PRIMARY).move_to([0, 3.1, 0])
        sub = text("the inputs a machine says yes to", size=32, color=MUTED).next_to(head, DOWN, buff=0.15)
        icon7 = mod7_machine(opacity=0.6).scale_to_fit_height(1.4)
        icon_cat = cat_machine().scale_to_fit_width(2.2)
        icon_par = parity_machine().scale_to_fit_width(1.8)
        rows = VGroup(
            VGroup(icon7, VGroup(math(r"\{0,\ 7,\ 14,\ 21,\ \dots\}", size=54),
                                 text("multiples of 7", size=32, color=MUTED)).arrange(DOWN, buff=0.1, aligned_edge=LEFT)),
            VGroup(icon_cat, text("strings containing \"cat\"", size=42)),
            VGroup(icon_par, text("bit strings with an even number of 1s", size=42)),
        )
        for k_, r_ in enumerate(rows):
            r_[0].move_to([-3.2, -0.5 - 1.75 * k_ + 1.75, 0])
            r_[1].next_to(r_[0], RIGHT, buff=0.5)
            if r_[1].width > 8.0:
                r_[1].scale_to_fit_width(8.0)
            r_[1].set_x(-1.8 + r_[1].width / 2)
        brace = Brace(rows, LEFT, buff=0.35, color=GOOD)
        reg = text("regular", size=44, color=GOOD).next_to(brace, LEFT, buff=0.2)
        with self.voiceover(text=N("s04.b4")) as tr:
            clear(self)
            self.play(FadeIn(head), FadeIn(sub), run_time=0.6)
            wait_frac(self, tr, 0.38)
            self.play(FadeIn(rows[0], shift=UP * 0.1), run_time=0.6)
            wait_frac(self, tr, 0.58)
            self.play(FadeIn(rows[1], shift=UP * 0.1), run_time=0.6)
            wait_frac(self, tr, 0.72)
            self.play(FadeIn(rows[2], shift=UP * 0.1), run_time=0.6)
            wait_until(self, tr, "regular")
            self.play(GrowFromCenter(brace), FadeIn(reg), run_time=0.7)
            rest(self, tr)
        clear(self)


class S05WhatTheyCant(VoiceoverScene):
    def construct(self):
        self.set_speech_service(get_speech_service())
        icons = VGroup(
            mod7_machine(opacity=0.6).scale_to_fit_height(3.0),
            cat_machine().scale_to_fit_width(4.4),
            parity_machine().scale_to_fit_width(3.2),
        )
        caps = VGroup(*[text(s, size=40, color=PRIMARY) for s in
                        ["the remainder", "the last few letters", "even or odd so far"]])
        cols = VGroup(*[VGroup(i, c).arrange(DOWN, buff=0.5) for i, c in zip(icons, caps)])
        cols.arrange(RIGHT, buff=0.6).move_to([0, 0.2, 0])
        for c in cols:
            c[1].move_to([c[0].get_x(), -2.3, 0])
            c[0].move_to([c[0].get_x(), 0.7, 0])
        head = text("all it remembers:", size=40, color=MUTED).move_to([0, -1.4, 0])
        with self.voiceover(text=N("s05.b1")) as tr:
            self.play(FadeIn(icons), run_time=0.8)
            wait_frac(self, tr, 0.5)
            self.play(FadeIn(head), run_time=0.4)
            for i, f in enumerate([0.62, 0.75, 0.87]):
                wait_frac(self, tr, f)
                self.play(FadeIn(caps[i], shift=UP * 0.1), run_time=0.4)
            rest(self, tr)

        good, bad = paren_pair(size=80)
        tk = tick(good, s=1.6)
        cr = cross(bad.get_left() + LEFT * 0.55, s=0.22)
        with self.voiceover(text=N("s05.b2")) as tr:
            clear(self)
            self.play(FadeIn(good), FadeIn(bad), run_time=0.6)
            self.play(Create(tk), Create(cr), run_time=0.6)
            rest(self, tr)

        box = ParenBox().move_to([2.9, -0.3, 0])
        strs = paren_strings(7, size=40).arrange(DOWN, buff=0.28, aligned_edge=LEFT).move_to([-4.2, -0.4, 0])
        slab = text("k + 1 inputs", size=34, color=MUTED).next_to(strs, UP, buff=0.35)
        with self.voiceover(text=N("s05.b3")) as tr:
            clear(self)
            self.play(FadeIn(box), run_time=0.7)
            self.play(LaggedStart(*[FadeIn(s, shift=RIGHT * 0.1) for s in strs], lag_ratio=0.25),
                      FadeIn(slab), run_time=1.6)
            per = max(0.4, (tr.time_until_bookmark("same") - 0.3) / 6)
            feed_strings(self, box, strs, range(6), per)
            wait_until(self, tr, "same")
            feed_strings(self, box, strs, [6], 0.9)
            hit = box.dots[LAND[6]]
            il = text("i", size=40, color=PRIMARY).next_to(strs[I_IDX], RIGHT, buff=0.3)
            jl = text("j", size=40, color=PRIMARY).next_to(strs[J_IDX], RIGHT, buff=0.3)
            self.play(hit.animate.set_color(PRIMARY).scale(1.4),
                      strs[I_IDX].animate.set_color(PRIMARY), strs[J_IDX].animate.set_color(PRIMARY),
                      run_time=0.6)
            wait_frac(self, tr, 0.8)
            self.play(FadeIn(il), FadeIn(jl), run_time=0.5)
            rest(self, tr)

        si = text("(((" + ")))", size=48)
        sj = text("(((((((" + ")))", size=48)
        si[3:].set_color(SECONDARY)
        sj[7:].set_color(SECONDARY)
        si.move_to([-3.6, 1.0, 0])
        sj.move_to([-3.6, -1.6, 0])
        si.align_to(sj, LEFT)
        end_dot = box.dots[5]
        with self.voiceover(text=N("s05.b4")) as tr:
            rest_strs = [s for k_, s in enumerate(strs) if k_ not in (I_IDX, J_IDX)]
            self.play(*[FadeOut(s) for s in rest_strs], FadeOut(slab), FadeOut(il), FadeOut(jl),
                      ReplacementTransform(strs[I_IDX], si[:3]), ReplacementTransform(strs[J_IDX], sj[:7]),
                      *[d.animate.set_color(FG) for d in box.dots if d is not hit], run_time=0.8)
            self.play(FadeIn(si[3:], shift=LEFT * 0.2), FadeIn(sj[7:], shift=LEFT * 0.2), run_time=0.6)
            path = ArcBetweenPoints(hit.get_center(), end_dot.get_center(), angle=-0.8)
            trail = path.copy().set_stroke(SECONDARY, 4)
            g1, g2 = glow_dot(SECONDARY), glow_dot(SECONDARY)
            g1.move_to(hit)
            g2.move_to(hit)
            self.play(Create(trail), MoveAlongPath(g1, path), MoveAlongPath(g2, path.copy()), run_time=1.4)
            self.play(FadeOut(g1), FadeOut(g2), end_dot.animate.set_color(SECONDARY).scale(1.4), run_time=0.4)
            wait_until(self, tr, "bal")
            t1 = tick(si, s=1.3)
            l1 = text("balanced", size=34, color=GOOD).next_to(si, DOWN, buff=0.2).align_to(si, LEFT)
            self.play(Create(t1), FadeIn(l1), run_time=0.5)
            wait_until(self, tr, "open")
            c2 = cross(sj.get_left() + LEFT * 0.5, s=0.2)
            l2 = text("not balanced", size=34, color=BAD).next_to(sj, DOWN, buff=0.2).align_to(sj, LEFT)
            self.play(Create(c2), FadeIn(l2), run_time=0.5)
            wait_frac(self, tr, 0.85)
            self.play(end_dot.animate.set_color(BAD), Flash(end_dot, color=BAD), run_time=0.7)
            rest(self, tr)

        msg = VGroup(text("no finite state machine", size=44),
                     text("checks balanced parentheses", size=44)).arrange(DOWN, buff=0.2)
        frame = SurroundingRectangle(msg, color=PRIMARY, buff=0.4, corner_radius=0.2)
        card = VGroup(msg, frame).move_to([-2.9, 0.3, 0])
        m7 = mod7_machine(opacity=0.6).scale(0.7).move_to([4.3, 0.5, 0])
        fixed = text("7 is fixed in advance", size=38, color=GOOD).next_to(m7, DOWN, buff=0.35)
        with self.voiceover(text=N("s05.b5")) as tr:
            clear(self)
            self.play(FadeIn(msg), Create(frame), run_time=0.8)
            wait_frac(self, tr, 0.55)
            self.play(FadeIn(m7), run_time=0.8)
            wait_until(self, tr, "fixed")
            self.play(FadeIn(fixed, shift=UP * 0.1), run_time=0.6)
            rest(self, tr)
        clear(self)


class S06Ending(VoiceoverScene):
    def construct(self):
        self.set_speech_service(get_speech_service())
        m = mod3_machine(center=np.array([0, 0, 0]))
        m.scale(0.72).move_to([-3.4, 0.1, 0])
        nfa = Machine({"p": [1.2, 0.1, 0], "q": [3.3, 0.1, 0], "u": [5.6, 1.9, 0], "v": [5.6, -1.7, 0]},
                      labels={"p": "", "q": "", "u": "", "v": ""}, r=0.42)
        nfa.add_edge("p", "q", "b", size=34, color=FG)
        eu = nfa.add_edge("q", "u", "a", size=34, color=FG)
        ev = nfa.add_edge("q", "v", "a", size=34, color=FG, label_side=-1)
        nfa.add_start("p", LEFT, length=0.6)
        nfa.add_accept("u")
        with self.voiceover(text=N("s06.b1")) as tr:
            self.play(FadeIn(m), run_time=0.8)
            m.light(self, 0, run_time=0.2)
            for a, b in [(0, 1), (1, 2), (2, 0)]:
                m.hop(self, a, b, run_time=0.8)
            self.play(FadeIn(nfa), run_time=0.8)
            nfa.light(self, "p", run_time=0.2)
            nfa.hop(self, "p", "q", run_time=0.9)
            wait_until(self, tr, "many")
            g1, g2 = glow_dot(), glow_dot()
            g1.move_to(eu.path.get_start())
            g2.move_to(ev.path.get_start())
            self.add(g1, g2)
            self.play(MoveAlongPath(g1, eu.path), MoveAlongPath(g2, ev.path), run_time=1.0)
            self.play(FadeOut(g1), FadeOut(g2), nfa.circles["q"].animate.set_fill(BG, 1).set_stroke(FG),
                      nfa.circles["u"].animate.set_fill(PRIMARY, 0.35).set_stroke(PRIMARY),
                      nfa.circles["v"].animate.set_fill(PRIMARY, 0.35).set_stroke(PRIMARY), run_time=0.4)
            same = text("no new languages", size=40, color=MUTED).move_to([3.4, -3.0, 0])
            small = text("but can be exponentially smaller", size=40, color=PRIMARY).move_to([0, -3.0, 0])
            wait_frac(self, tr, 0.68)
            self.play(FadeIn(same, shift=UP * 0.1), run_time=0.5)
            wait_frac(self, tr, 0.84)
            self.play(same.animate.move_to([-3.4, -3.0, 0]), run_time=0.4)
            small.next_to(same, RIGHT, buff=0.5)
            self.play(FadeIn(small, shift=UP * 0.1), run_time=0.5)
            rest(self, tr)
        clear(self, run_time=0.8)


class Thumbnail(Scene):
    def construct(self):
        m = mod7_machine(radius=2.7, center=np.array([3.4, -0.1, 0]), opacity=0.35)
        for a, b in [(0, 1), (1, 3), (3, 4), (4, 0)]:
            m.show_edge(a, b, color=PRIMARY, width=7)
        m.circles[0].set_fill(GOOD, 0.4).set_stroke(GOOD)
        num = text("1729", size=150, weight="BOLD").move_to([-3.4, 1.0, 0])
        q = text("divisible by 7?", size=64, color=PRIMARY).next_to(num, DOWN, buff=0.3)
        self.add(m, num, q)
