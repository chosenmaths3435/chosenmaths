from manim import *
from manim_voiceover import VoiceoverScene

from mathvid import layout  # noqa: F401  must come before scene code runs
from mathvid.anim import morph_parts, rest, rt, strikes, wait_until
from mathvid.script import Script
from mathvid.style import BAD, BG, FG, GOOD, MUTED, PRIMARY, SECONDARY, math, text
from mathvid.voice import get_speech_service

N = Script(__file__)

# ---------------------------------------------------------------------------
# Shared builders. Positions that carry across scene cuts are fixed here so the
# last frame of one scene matches the first frame of the next.
# ---------------------------------------------------------------------------

RULE3 = r"I\big(p\, I^{-1}(q)\big) = pq - I\big(q\, I^{-1}(p)\big)"
RULE3_PARTS = [r"I\big(", r"p\,", r"I^{-1}(q)", r"\big)", r"=", r"pq", r"-",
               r"I\big(", r"q\,", r"I^{-1}(p)", r"\big)"]
TABLE_ANCHOR = RIGHT * 4.4 + UP * 2.4  # top-left corner of the "known" table
WORK = LEFT * 1.6  # center of the working area left of the table
ROWS = [("1", "x"), ("x", r"\frac{x^2}{2}"), ("x^2", r"\frac{x^3}{3}"),
        ("x^3", r"\frac{x^4}{4}"), ("x^4", r"\frac{x^5}{5}"), ("x^5", r"\frac{x^6}{6}")]


def machine(label="I"):
    box = RoundedRectangle(
        corner_radius=0.2, width=2.2, height=1.4, color=FG, stroke_width=3,
        fill_color=BG, fill_opacity=1,
    )
    lab = math(label, size=60).move_to(box)
    return VGroup(box, lab)


def feed(scene, m, inp, out, run_time, backwards=False):
    """Send inp through machine m and bring out out. Backwards runs right to left."""
    side = RIGHT if backwards else LEFT
    inp.next_to(m, side, buff=0.8)
    out.next_to(m, -side, buff=0.8)
    target = out.copy()
    out.move_to(m).set_opacity(0)
    scene.play(FadeIn(inp, shift=-side * 0.3), run_time=rt(run_time * 0.25))
    scene.play(inp.animate.move_to(m).set_opacity(0), run_time=rt(run_time * 0.35))
    scene.play(Transform(out, target), run_time=rt(run_time * 0.4))
    scene.remove(inp)
    return out


def rule_rows(size=38):
    r1 = VGroup(
        text("1. Linear", size=30, color=MUTED),
        math(r"I(p+q) = I(p) + I(q)", size=size),
        math(r"I(c\,p) = c\,I(p)", size=size),
    ).arrange(DOWN, aligned_edge=LEFT, buff=0.15)
    r2 = VGroup(
        text("2. One free answer", size=30, color=MUTED),
        math(r"I(1) = x", size=size),
    ).arrange(DOWN, aligned_edge=LEFT, buff=0.15)
    return r1, r2


def rule3_block(size=38):
    f = math(RULE3, size=size)
    note = text("p, q: outputs of I", size=24, color=MUTED).next_to(f, DOWN, buff=0.12)
    return VGroup(f, note)


def rule3_panel():
    head = text("3. Integration by parts", size=30, color=MUTED)
    return VGroup(head, rule3_block(38)).arrange(DOWN, aligned_edge=LEFT, buff=0.15)


def rule3_top():
    return rule3_block(44).to_edge(UP, buff=0.4)


def table(rows, size=36):
    """rows: list of (input_tex, output_tex). Returns VGroup(header, row, row, ...)."""
    head = text("Known so far", size=26, color=MUTED)
    lines = [math(a, r"\mapsto", b, size=size) for a, b in rows]
    g = VGroup(head, *lines).arrange(DOWN, aligned_edge=LEFT, buff=0.22)
    g.move_to(TABLE_ANCHOR, aligned_edge=UL)
    return g


def grow_table(scene, tbl, n_rows, source=None, run_time=1.0, color=None):
    """Replace tbl (showing n_rows - 1 rows) by one showing n_rows rows.

    The new row flies in from source if given, else fades in. Old rows do not move.
    """
    new = table(ROWS[:n_rows])
    if color:
        new[-1].set_color(color)
    anim = TransformFromCopy(source, new[-1]) if source is not None else FadeIn(new[-1], shift=LEFT * 0.2)
    scene.play(anim, run_time=run_time)
    scene.remove(tbl, new[-1])
    scene.add(new)
    return new


def row_arrow(tbl, i):
    """Curved arrow on the left of the table from row i to row i + 1 (rows count from 1)."""
    a, b = tbl[i], tbl[i + 1]
    return CurvedArrow(a.get_left() + LEFT * 0.15, b.get_left() + LEFT * 0.15,
                       angle=TAU / 3, color=MUTED, stroke_width=3, tip_length=0.15)


def focus(mob, color=PRIMARY):
    return SurroundingRectangle(mob, color=color, buff=0.08, stroke_width=3)


# ---------------------------------------------------------------------------
# s01 Hook
# ---------------------------------------------------------------------------


class S01Hook(VoiceoverScene):
    def construct(self):
        self.set_speech_service(get_speech_service())

        power = math(r"\int x^n\,dx = \frac{x^{n+1}}{n+1} + C", size=56)
        others = VGroup(
            math(r"\int \sin x\,dx = -\cos x + C", size=36),
            math(r"\int e^x\,dx = e^x + C", size=36),
            math(r"\int \frac{dx}{x} = \ln|x| + C", size=36),
            math(r"\int \frac{dx}{1+x^2} = \arctan x + C", size=36),
        )
        for o, pos in zip(others, [UL, UR, DL, DR]):
            o.move_to(pos * [3.8, 2.4, 0])

        with self.voiceover(text=N("s01.b1")) as tr:
            self.play(Write(power), run_time=rt(tr.time_until_bookmark("cross")))
            self.play(LaggedStart(*[FadeIn(o) for o in others], lag_ratio=0.2), run_time=1.0)
            lines = strikes(power, *others)
            self.play(LaggedStart(*[Create(s) for s in lines], lag_ratio=0.15), run_time=1.0)
            self.play(FadeOut(VGroup(power, others, lines)), run_time=rt(tr.get_remaining_duration()))

        ibp = math(r"\int p\,q'\,dx = pq - \int q\,p'\,dx", size=64)
        with self.voiceover(text=N("s01.b2")) as tr:
            self.play(Write(ibp), run_time=rt(max(1.2, tr.time_until_bookmark("ibp") + 0.6)))
            rest(self, tr)

        q = math(r"\int x^5\,dx =", r"\;?", size=84)
        with self.voiceover(text=N("s01.b3")) as tr:
            self.play(ibp.animate.scale(0.6).to_edge(UP, buff=0.6), run_time=rt(tr.time_until_bookmark("q")))
            self.play(Write(q), run_time=rt(min(1.5, tr.get_remaining_duration())))
            rest(self, tr)

        with self.voiceover(text=N("s01.b4")) as tr:
            self.play(Indicate(q[1], color=PRIMARY, scale_factor=1.4), run_time=rt(tr.duration * 0.5))
            self.play(FadeOut(VGroup(ibp, q)), run_time=rt(tr.get_remaining_duration()))


# ---------------------------------------------------------------------------
# s02 The rules
# ---------------------------------------------------------------------------


class S02Rules(VoiceoverScene):
    def construct(self):
        self.set_speech_service(get_speech_service())

        m = machine()
        with self.voiceover(text=N("s02.b1")) as tr:
            self.play(FadeIn(m, scale=0.9), run_time=1.0)
            out = feed(self, m, math("3x^2 + 1"), math("?", color=PRIMARY), tr.duration - 1.5)
            rest(self, tr)

        title = text("Rules", size=36, weight="BOLD").move_to(RIGHT * 0.4 + UP * 3.3, aligned_edge=LEFT)
        with self.voiceover(text=N("s02.b2")) as tr:
            self.play(
                FadeOut(out),
                m.animate.move_to(LEFT * 3.8 + UP * 1.6),
                run_time=rt(tr.duration * 0.25),
            )
            guess = math(r"I = \int", size=48).next_to(m, DOWN, buff=0.5)
            self.play(FadeIn(guess), run_time=rt(tr.duration * 0.15))
            no = strikes(guess)
            self.play(Create(no), run_time=rt(tr.duration * 0.15))
            self.play(FadeOut(VGroup(guess, no)), FadeIn(title, shift=DOWN * 0.2),
                      run_time=rt(tr.get_remaining_duration()))

        r1, r2 = rule_rows()
        r3 = rule3_panel()
        panel = VGroup(r1, r2, r3).arrange(DOWN, aligned_edge=LEFT, buff=0.45)
        panel.next_to(title, DOWN, buff=0.4)
        panel.shift(RIGHT * (0.4 - panel.get_left()[0]))

        with self.voiceover(text=N("s02.b3")) as tr:
            wait_until(self, tr, "r1")
            self.play(FadeIn(r1, shift=LEFT * 0.2), run_time=rt(min(1.0, tr.get_remaining_duration())))
            rest(self, tr)

        with self.voiceover(text=N("s02.b4")) as tr:
            wait_until(self, tr, "r2")
            self.play(FadeIn(r2, shift=LEFT * 0.2), run_time=0.8)
            x_out = feed(self, m, math("1"), math("x", color=PRIMARY), max(1.0, tr.get_remaining_duration() - 0.2))
            rest(self, tr)

        usual = math(r"\int", r"p\,", r"q'", r"\,dx", r"=", r"pq", r"-", r"\int", r"q\,", r"p'", r"\,dx", size=48)
        usual.move_to(LEFT * 3.8 + DOWN * 1.4)
        with self.voiceover(text=N("s02.b5")) as tr:
            self.play(FadeOut(x_out), run_time=rt(tr.time_until_bookmark("ibp") * 0.5))
            wait_until(self, tr, "ibp")
            self.play(Write(usual), run_time=rt(tr.get_remaining_duration() * 0.5))
            self.play(usual[2].animate.set_color(PRIMARY), usual[9].animate.set_color(PRIMARY),
                      run_time=rt(tr.get_remaining_duration()))

        inv_label = math(r"I^{-1}", size=40, color=SECONDARY).next_to(m, DOWN, buff=0.25)
        with self.voiceover(text=N("s02.b6")) as tr:
            self.play(Wiggle(usual[2]), Wiggle(usual[9]), run_time=rt(min(1.5, tr.time_until_bookmark("inv"))))
            wait_until(self, tr, "inv")
            self.play(FadeIn(inv_label), m[0].animate.set_stroke(color=SECONDARY), run_time=0.6)
            one = feed(self, m, math("x"), math("1", color=SECONDARY), max(1.0, tr.get_remaining_duration() - 0.2),
                       backwards=True)
            rest(self, tr)

        new = math(*RULE3_PARTS, size=40).move_to(usual)
        with self.voiceover(text=N("s02.b7")) as tr:
            self.play(FadeOut(one), FadeOut(inv_label), m[0].animate.set_stroke(color=FG), run_time=0.5)
            self.play(TransformMatchingTex(usual, new), run_time=1.5)
            wait_until(self, tr, "rule")
            target = r3[1][0]
            self.play(FadeIn(r3[0]), ReplacementTransform(new, target), run_time=1.2)
            self.play(FadeIn(r3[1][1]), run_time=0.5)
            rest(self, tr)

        tbl = table([("1", "x")])
        tbl_start = tbl.copy().move_to(LEFT * 3.8 + DOWN * 1.6)
        with self.voiceover(text=N("s02.b8")) as tr:
            self.play(FadeIn(tbl_start, shift=UP * 0.2), run_time=1.0)
            self.play(Indicate(tbl_start[1], color=PRIMARY), run_time=1.0)
            # Settle into the layout s03 starts from: rule 3 on top, table on the right.
            hold = tr.get_remaining_duration() - 1.5
            if hold > 0.05:
                self.wait(hold)
            self.play(
                FadeOut(VGroup(m, title, r1, r2, r3[0])),
                ReplacementTransform(r3[1], rule3_top()),
                ReplacementTransform(tbl_start, tbl),
                run_time=1.5,
            )


# ---------------------------------------------------------------------------
# s03 The first step
# ---------------------------------------------------------------------------

def eq(*parts, size=48):
    return math(*parts, size=size).move_to(WORK)


class S03FirstStep(VoiceoverScene):
    def construct(self):
        self.set_speech_service(get_speech_service())
        top = rule3_top()
        tbl = table(ROWS[:1])
        self.add(top, tbl)

        ask = math(r"I(x) = \;?", size=52).move_to(WORK + UP * 1.4)
        with self.voiceover(text=N("s03.b1")) as tr:
            self.play(Write(ask), run_time=rt(min(1.5, tr.duration)))
            rest(self, tr)

        # I(x I^-1(x)) = x x - I(x I^-1(x))
        l1 = eq(r"I\big(", r"x\,", r"I^{-1}(x)", r"\big)", "=", r"x\cdot x", "-",
                r"I\big(", r"x\,", r"I^{-1}(x)", r"\big)")
        for i in (1, 8):
            l1[i].set_color(PRIMARY)
        with self.voiceover(text=N("s03.b2")) as tr:
            self.play(TransformFromCopy(top[0], l1), run_time=rt(min(1.8, tr.duration)))
            rest(self, tr)

        box = focus(l1[2])
        with self.voiceover(text=N("s03.b3")) as tr:
            self.play(Create(box), run_time=0.6)
            self.play(Indicate(tbl[1], color=PRIMARY), run_time=rt(min(1.2, tr.time_until_bookmark("one"))))
            wait_until(self, tr, "one")
            l1b = eq(r"I\big(", r"x\,", r"1", r"\big)", "=", r"x\cdot x", "-",
                     r"I\big(", r"x\,", r"I^{-1}(x)", r"\big)")
            l1b[1].set_color(PRIMARY); l1b[8].set_color(PRIMARY)
            l1 = morph_parts(self, l1, l1b, [(i, i) for i in range(11)], run_time=0.8, extra=[FadeOut(box)])
            l2 = eq(r"I(x)", "=", r"x\cdot x", "-", r"I\big(", r"x\,", r"I^{-1}(x)", r"\big)")
            l2[5].set_color(PRIMARY)
            l1 = morph_parts(self, l1, l2, [((0, 1, 2, 3), 0)] + [(i, i - 3) for i in range(4, 11)],
                             run_time=rt(min(1.0, tr.get_remaining_duration())))
            rest(self, tr)

        with self.voiceover(text=N("s03.b4")) as tr:
            l2b = eq(r"I(x)", "=", r"x^2", "-", r"I\big(", r"x\,", r"I^{-1}(x)", r"\big)")
            l1 = morph_parts(self, l1, l2b, [(i, i) for i in range(8)], run_time=rt(min(1.0, tr.time_until_bookmark("rhs"))))
            wait_until(self, tr, "rhs")
            l3 = eq(r"I(x)", "=", r"x^2", "-", r"I(x)")
            l1 = morph_parts(self, l1, l3, [(0, 0), (1, 1), (2, 2), (3, 3), ((4, 5, 6, 7), 4)],
                             run_time=rt(min(1.0, tr.get_remaining_duration())))
            rest(self, tr)

        with self.voiceover(text=N("s03.b5")) as tr:
            self.play(l1[0].animate.set_color(PRIMARY), l1[4].animate.set_color(PRIMARY), run_time=0.6)
            self.play(Indicate(l1[0], color=PRIMARY), Indicate(l1[4], color=PRIMARY), run_time=1.2)
            rest(self, tr)

        with self.voiceover(text=N("s03.b6")) as tr:
            wait_until(self, tr, "move")
            l4 = eq("2", r"I(x)", "=", r"x^2")
            l4[1].set_color(PRIMARY)
            l1 = morph_parts(self, l1, l4, [(0, 1), (4, 0), (1, 2), (2, 3)], run_time=1.0)
            l5 = eq(r"I(x)", "=", r"\frac{x^2}{2}")
            l1 = morph_parts(self, l1, l5, [(1, 0), (2, 1), ((0, 3), 2)], run_time=1.0)
            tbl = grow_table(self, tbl, 2, source=l1, run_time=rt(min(1.2, tr.get_remaining_duration())))
            rest(self, tr)

        with self.voiceover(text=N("s03.b7")) as tr:
            self.play(Indicate(tbl[2], color=PRIMARY), run_time=1.2)
            hold = tr.get_remaining_duration() - 0.8
            if hold > 0.05:
                self.wait(hold)
            self.play(FadeOut(VGroup(ask, l1)), run_time=0.8)


# ---------------------------------------------------------------------------
# s04 Climbing
# ---------------------------------------------------------------------------


class S04Climbing(VoiceoverScene):
    def construct(self):
        self.set_speech_service(get_speech_service())
        top = rule3_top()
        tbl = table(ROWS[:2])
        self.add(top, tbl)

        l1 = eq(r"I\big(", r"x^2\,", r"I^{-1}(x)", r"\big)", "=", r"x^2\cdot x", "-",
                r"I\big(", r"x\,", r"I^{-1}(x^2)", r"\big)")
        l1[1].set_color(PRIMARY); l1[8].set_color(SECONDARY)
        with self.voiceover(text=N("s04.b1")) as tr:
            self.play(TransformFromCopy(top[0], l1), run_time=rt(min(1.8, tr.duration)))
            rest(self, tr)

        with self.voiceover(text=N("s04.b2")) as tr:
            box = focus(l1[2])
            self.play(Create(box), Indicate(tbl[1], color=PRIMARY), run_time=1.0)
            l2 = eq(r"I(x^2)", "=", r"x^2\cdot x", "-", r"I\big(", r"x\,", r"I^{-1}(x^2)", r"\big)")
            l2[5].set_color(SECONDARY)
            l1 = morph_parts(self, l1, l2, [((0, 1, 2, 3), 0)] + [(i, i - 3) for i in range(4, 11)],
                             run_time=1.0, extra=[FadeOut(box)])
            rest(self, tr)

        doubled = math(r"2x", r"\mapsto", r"x^2", size=40).next_to(l1, DOWN, buff=1.0)
        with self.voiceover(text=N("s04.b3")) as tr:
            box = focus(l1[6])
            self.play(Create(box), run_time=0.6)
            self.play(Indicate(tbl[2], color=PRIMARY), run_time=1.0)
            self.play(TransformFromCopy(tbl[2], doubled), run_time=rt(min(1.2, tr.time_until_bookmark("inv2"))))
            wait_until(self, tr, "inv2")
            l3 = eq(r"I(x^2)", "=", r"x^3", "-", r"I\big(", r"x\,", r"2x", r"\big)")
            l3[5].set_color(SECONDARY)
            l1 = morph_parts(self, l1, l3, [(i, i) for i in range(8)], run_time=1.0, extra=[FadeOut(box)])
            rest(self, tr)

        with self.voiceover(text=N("s04.b4")) as tr:
            l4 = eq(r"I(x^2)", "=", r"x^3", "-", r"I(2x^2)")
            l1 = morph_parts(self, l1, l4, [(0, 0), (1, 1), (2, 2), (3, 3), ((4, 5, 6, 7), 4)],
                             run_time=rt(min(1.0, tr.time_until_bookmark("sub"))))
            wait_until(self, tr, "sub")
            l5 = eq(r"I(x^2)", "=", r"x^3", "-", "2", r"I(x^2)")
            l1 = morph_parts(self, l1, l5, [(0, 0), (1, 1), (2, 2), (3, 3), (4, (4, 5))], run_time=1.0)
            self.play(l1[0].animate.set_color(PRIMARY), l1[5].animate.set_color(PRIMARY), run_time=0.5)
            rest(self, tr)

        with self.voiceover(text=N("s04.b5")) as tr:
            l6 = eq("3", r"I(x^2)", "=", r"x^3")
            l6[1].set_color(PRIMARY)
            l1 = morph_parts(self, l1, l6, [(0, 1), ((4, 5), 0), (1, 2), (2, 3)], run_time=1.0)
            l7 = eq(r"I(x^2)", "=", r"\frac{x^3}{3}")
            l1 = morph_parts(self, l1, l7, [(1, 0), (2, 1), ((0, 3), 2)], run_time=1.0)
            tbl = grow_table(self, tbl, 3, source=l1, run_time=rt(min(1.2, tr.get_remaining_duration())))
            rest(self, tr)

        with self.voiceover(text=N("s04.b6")) as tr:
            self.play(FadeOut(VGroup(l1, doubled)), run_time=0.6)
            wait_until(self, tr, "table")
            arrows = VGroup(row_arrow(tbl, 1), row_arrow(tbl, 2))
            self.play(LaggedStart(*[Create(a) for a in arrows], lag_ratio=0.5), run_time=1.0)
            arrows.add(row_arrow(table(ROWS[:4]), 3))
            self.play(Create(arrows[-1]), run_time=0.5)
            tbl = grow_table(self, tbl, 4, run_time=rt(min(0.8, tr.get_remaining_duration())))
            rest(self, tr)

        a = math(r"x^{n-1} \mapsto \frac{x^n}{n}", r"\quad\Longrightarrow\quad", r"I^{-1}(x^n) = n\,x^{n-1}",
                 size=40).move_to(WORK + UP * 1.3)
        g1 = eq(r"I(x^n)", "=", r"x^{n+1}", "-", r"I\big(x\cdot n\,x^{n-1}\big)").shift(DOWN * 0.4)
        with self.voiceover(text=N("s04.b7")) as tr:
            wait_until(self, tr, "general")
            per = tr.get_remaining_duration() / 5
            self.play(Write(a), run_time=rt(per))
            self.play(TransformFromCopy(top[0], g1), run_time=rt(per))
            g2 = eq(r"I(x^n)", "=", r"x^{n+1}", "-", r"n\,", r"I(x^n)").shift(DOWN * 0.4)
            g = morph_parts(self, g1, g2, [(0, 0), (1, 1), (2, 2), (3, 3), (4, (4, 5))], run_time=rt(per))
            self.play(g[0].animate.set_color(PRIMARY), g[5].animate.set_color(PRIMARY), run_time=0.4)
            g3 = eq(r"(n+1)\,", r"I(x^n)", "=", r"x^{n+1}").shift(DOWN * 0.4)
            g3[1].set_color(PRIMARY)
            g = morph_parts(self, g, g3, [(0, 1), ((4, 5), 0), (1, 2), (2, 3)], run_time=rt(per * 0.6))
            g4 = eq(r"I(x^n)", "=", r"\frac{x^{n+1}}{n+1}").shift(DOWN * 0.4)
            g = morph_parts(self, g, g4, [(1, 0), (2, 1), ((0, 3), 2)], run_time=rt(per * 0.6))
            rest(self, tr)

        hook = math(r"\int x^5\,dx =", r"\;?", size=56).move_to(WORK + DOWN * 0.4)
        with self.voiceover(text=N("s04.b8")) as tr:
            boxed = SurroundingRectangle(g, color=GOOD, buff=0.15)
            self.play(Create(boxed), run_time=0.6)
            more = [row_arrow(table(ROWS[:5]), 4), row_arrow(table(ROWS[:6]), 5)]
            self.play(Create(more[0]), run_time=0.4)
            tbl = grow_table(self, tbl, 5, run_time=0.5)
            self.play(Create(more[1]), run_time=0.4)
            tbl = grow_table(self, tbl, 6, run_time=0.5, color=PRIMARY)
            self.play(FadeOut(VGroup(a, g, boxed)), FadeIn(hook), run_time=rt(min(1.0, tr.time_until_bookmark("answer"))))
            wait_until(self, tr, "answer")
            ans = math(r"\int x^5\,dx =", r"\;\frac{x^6}{6}", size=56).move_to(hook)
            ans[1].set_color(PRIMARY)
            self.play(TransformFromCopy(tbl[-1][2], ans[1]), FadeOut(hook[1]), run_time=1.0)
            rest(self, tr)

        with self.voiceover(text=N("s04.b9")) as tr:
            hold = tr.get_remaining_duration() - 1.0
            if hold > 0.05:
                self.wait(hold)
            self.play(FadeOut(Group(*self.mobjects)), run_time=1.0)


# ---------------------------------------------------------------------------
# s05 The picture
# ---------------------------------------------------------------------------

PANEL_X = 3.9  # center of the right-hand text panel in s05


def plane(width=5.0):
    ax = Axes(x_range=[0, 1.2, 1], y_range=[0, 1.2, 1], x_length=width, y_length=width, tips=False,
              axis_config={"color": MUTED, "include_ticks": False})
    return ax


def regions(ax, k):
    pts = [ax.c2p(t, t ** k) for t in np.linspace(0, 1, 80)]
    under = Polygon(ax.c2p(0, 0), *pts, ax.c2p(1, 0), stroke_width=0, fill_color=PRIMARY, fill_opacity=0.45)
    left = Polygon(ax.c2p(0, 0), *pts, ax.c2p(0, 1), stroke_width=0, fill_color=SECONDARY, fill_opacity=0.45)
    curve = ax.plot(lambda t: t ** k, x_range=[0, 1], color=FG, stroke_width=4)
    return under, left, curve


def region_labels(ax, k):
    a = math("A", size=40).move_to(ax.c2p(0.78, 0.18 if k > 1 else 0.3))
    b = math("A" if k == 1 else f"{k}A", size=40).move_to(ax.c2p(0.3 if k > 1 else 0.25, 0.68 if k > 1 else 0.7))
    return VGroup(a, b)


def bars(n, height=1.8, total=2.4):
    w = total / n
    return VGroup(*[
        Rectangle(width=w, height=height, stroke_color=FG, stroke_width=2,
                  fill_color=PRIMARY if i == 0 else SECONDARY, fill_opacity=0.5)
        for i in range(n)
    ]).arrange(RIGHT, buff=0)


def share_block(k):
    """Bars for k + 1 shares, with 'under = 1/(k+1) of the rectangle' under them."""
    b = bars(k + 1)
    lab = math(r"\text{under} = \tfrac{1}{%d}" % (k + 1), r"\text{ of the rectangle}", size=34)
    lab[0].set_color(PRIMARY)
    return VGroup(b, lab).arrange(DOWN, buff=0.3).move_to(RIGHT * PANEL_X + DOWN * 1.6)


def head_tex(k):
    """The integration by parts step for x^k, as shown at the top of s05."""
    if k == 1:
        return r"I(x) = x^2 - I(x)"
    if k == "k":
        return r"I(x^k) = x^{k+1} - k\,I(x^k)"
    return r"I(x^{%d}) = x^{%d} - %d\,I(x^{%d})" % (k, k + 1, k, k)


class S05Picture(VoiceoverScene):
    def construct(self):
        self.set_speech_service(get_speech_service())
        head = math(r"I(x^2) = x^3 - 2\,I(x^2)", size=40).to_edge(UP, buff=0.35)
        ax = plane().move_to(LEFT * 2.8 + DOWN * 0.55)
        o = ax.c2p(0, 0)
        rect = DashedVMobject(Polygon(o, ax.c2p(1, 0), ax.c2p(1, 1), ax.c2p(0, 1), color=FG, stroke_width=2),
                              num_dashes=40)
        under, left, curve = regions(ax, 2)
        bw = Brace(Line(o, ax.c2p(1, 0)), DOWN, color=MUTED)
        bw_lab = math(r"q = t,\ \text{so } a", size=32).next_to(bw, DOWN, buff=0.1)
        bh = Brace(Line(o, ax.c2p(0, 1)), LEFT, color=MUTED)
        bh_lab = math(r"p = t^2,", r"\text{so } a^2", size=32).arrange(DOWN, buff=0.1).next_to(bh, LEFT, buff=0.1)
        area = math(r"\text{rectangle} = a^3", size=36).move_to(RIGHT * PANEL_X + UP * 2.2)

        with self.voiceover(text=N("s05.b1")) as tr:
            self.play(FadeIn(head), Create(ax), run_time=1.2)
            self.play(Create(curve), run_time=rt(min(1.5, tr.time_until_bookmark("rect"))))
            wait_until(self, tr, "rect")
            self.play(Create(rect), GrowFromCenter(bw), GrowFromCenter(bh), run_time=1.0)
            self.play(FadeIn(bw_lab), FadeIn(bh_lab), run_time=0.6)
            self.play(Write(area), run_time=rt(min(1.0, tr.get_remaining_duration())))
            rest(self, tr)

        with self.voiceover(text=N("s05.b2")) as tr:
            wait_until(self, tr, "under")
            self.play(FadeIn(under), run_time=0.8)
            wait_until(self, tr, "left")
            self.play(FadeIn(left), run_time=rt(min(0.8, tr.get_remaining_duration())))
            rest(self, tr)

        p1 = math(r"\text{under} + \text{left} = a^3", size=36).next_to(area, DOWN, buff=0.4)
        p1[0][:5].set_color(PRIMARY)
        with self.voiceover(text=N("s05.b3")) as tr:
            self.play(under.animate.shift(DR * 0.15), left.animate.shift(UL * 0.15), run_time=0.8)
            self.play(under.animate.shift(UL * 0.15), left.animate.shift(DR * 0.15), run_time=0.8)
            self.play(Write(p1), run_time=1.0)
            self.play(Indicate(head[0][6:8], color=PRIMARY), run_time=rt(min(1.2, tr.get_remaining_duration())))
            rest(self, tr)

        dt = 0.05
        tt = ValueTracker(0.35)

        def make_strip():
            t = tt.get_value()
            return Polygon(ax.c2p(0, t ** 2), ax.c2p(t, t ** 2), ax.c2p(t + dt, (t + dt) ** 2),
                           ax.c2p(0, (t + dt) ** 2), stroke_color=FG, stroke_width=2, fill_color=FG,
                           fill_opacity=0.8)

        strip = always_redraw(make_strip)
        strip_lab = math(r"\text{width } t,\ \text{thickness } 2t\,dt", size=30).next_to(p1, DOWN, buff=0.35)
        p2 = math(r"\text{left} = \int_0^a t\cdot 2t\,dt = 2A", size=36).next_to(p1, DOWN, buff=0.35)
        labels = region_labels(ax, 2)
        shares = share_block(2)
        with self.voiceover(text=N("s05.b4")) as tr:
            per = tr.duration / 5
            self.play(FadeIn(strip), FadeIn(strip_lab), run_time=rt(per))
            self.play(tt.animate.set_value(0.85), run_time=rt(per * 0.5))
            self.play(tt.animate.set_value(0.6), run_time=rt(per * 0.5))
            self.play(FadeOut(strip), ReplacementTransform(strip_lab, p2), run_time=rt(per * 0.6))
            self.play(FadeIn(labels), Indicate(head[0][-6], color=PRIMARY), run_time=rt(per * 0.6))
            self.play(FadeIn(shares, shift=UP * 0.2), run_time=rt(min(1.0, tr.get_remaining_duration())))
            rest(self, tr)

        def set_power(k, run_time):
            nu, nl, nc = regions(ax, k)
            new_lab = region_labels(ax, k)
            new_sh = share_block(k)
            new_bh = math(r"p = t^{%d}," % k if k > 1 else r"p = t,", r"\text{so } a^{%d}" % k if k > 1 else r"\text{so } a",
                          size=32).arrange(DOWN, buff=0.1).next_to(bh, LEFT, buff=0.1)
            new_head = math(head_tex(k), size=40).move_to(head)
            new_area = math(r"\text{rectangle} = a^{%d}" % (k + 1), size=36).move_to(area)
            self.play(Transform(under, nu), Transform(left, nl), Transform(curve, nc),
                      Transform(labels, new_lab), Transform(shares, new_sh), Transform(bh_lab, new_bh),
                      Transform(head, new_head), Transform(area, new_area),
                      run_time=run_time)

        with self.voiceover(text=N("s05.b5")) as tr:
            self.play(FadeOut(VGroup(p1, p2)), run_time=0.6)
            wait_until(self, tr, "k1")
            set_power(1, rt(min(1.5, tr.get_remaining_duration())))
            rest(self, tr)

        with self.voiceover(text=N("s05.b6")) as tr:
            wait_until(self, tr, "k3")
            set_power(3, rt(tr.get_remaining_duration() * 0.5))
            set_power(4, rt(tr.get_remaining_duration()))

        gen = VGroup(
            math(r"y = t^k", size=36),
            math(r"\text{left} = k \cdot \text{under}", size=36),
        ).arrange(DOWN, buff=0.3).move_to(RIGHT * PANEL_X + UP * 1.1)
        rule = math(r"\int_0^a t^k\,dt = \frac{a^{k+1}}{", r"k+1", r"}", size=44).move_to(RIGHT * PANEL_X + DOWN * 1.6)
        rule[1].set_color(PRIMARY)
        with self.voiceover(text=N("s05.b7")) as tr:
            self.play(FadeIn(gen),
                      Transform(head, math(head_tex("k"), size=40).move_to(head)),
                      Transform(area, math(r"\text{rectangle} = a^{k+1}", size=36).move_to(area)),
                      run_time=1.0)
            self.play(Indicate(shares[1][0], color=PRIMARY), run_time=1.0)
            self.play(FadeOut(shares[0]), ReplacementTransform(shares[1], rule), run_time=rt(min(1.5, tr.get_remaining_duration() - 1.0)))
            self.play(Indicate(rule[1], color=PRIMARY), run_time=1.0)
            hold = tr.get_remaining_duration() - 1.0
            if hold > 0.05:
                self.wait(hold)
            self.play(FadeOut(Group(*self.mobjects)), run_time=1.0)


# ---------------------------------------------------------------------------
# s06 Why the other rules
# ---------------------------------------------------------------------------


def check():
    return math(r"\checkmark", size=48, color=GOOD)


class S06OtherRules(VoiceoverScene):
    def construct(self):
        self.set_speech_service(get_speech_service())
        r1, r2 = rule_rows(40)
        r3 = rule3_panel()
        panel = VGroup(r1, r2, r3).arrange(DOWN, aligned_edge=LEFT, buff=0.45).move_to(ORIGIN)

        with self.voiceover(text=N("s06.b1")) as tr:
            self.play(LaggedStart(*[FadeIn(r, shift=UP * 0.2) for r in panel], lag_ratio=0.3),
                      run_time=rt(min(2.0, tr.duration)))
            rest(self, tr)

        inv = math(r"(2I)^{-1} = \tfrac12\, I^{-1}", size=48).move_to(UP * 1.6)
        dbl = math("2", r"I\big(p\,", r"\tfrac12", r"I^{-1}(q)\big)", "=", "pq", "-",
                   "2", r"I\big(q\,", r"\tfrac12", r"I^{-1}(p)\big)", size=48).move_to(DOWN * 0.2)
        for i in (0, 7):
            dbl[i].set_color(PRIMARY)
        for i in (2, 9):
            dbl[i].set_color(SECONDARY)
        with self.voiceover(text=N("s06.b2")) as tr:
            self.play(FadeOut(panel), run_time=0.6)
            self.play(Write(inv), run_time=rt(min(1.5, tr.time_until_bookmark("double"))))
            wait_until(self, tr, "double")
            self.play(Write(dbl), run_time=1.2)
            cuts = VGroup(*[Line(dbl[i].get_corner(DL), dbl[i].get_corner(UR), color=BAD, stroke_width=4)
                            for i in (0, 2, 7, 9)])
            self.play(LaggedStart(*[Create(c) for c in cuts], lag_ratio=0.25), run_time=1.2)
            ok = check().next_to(dbl, RIGHT, buff=0.4)
            self.play(FadeIn(ok, scale=1.5), run_time=rt(min(0.6, tr.get_remaining_duration())))
            rest(self, tr)

        def boxed(lbl):
            m = machine(lbl).scale(0.8)
            return VGroup(m, check().scale(0.8).next_to(m, DOWN, buff=0.2))

        row = VGroup(boxed("2I"), boxed("10I"), boxed("100I")).arrange(RIGHT, buff=1.0).move_to(UP * 0.6)
        r2_big = math(r"I(1) = x", size=64).move_to(DOWN * 2.0)
        with self.voiceover(text=N("s06.b3")) as tr:
            self.play(FadeOut(VGroup(inv, dbl, cuts, ok)), run_time=0.6)
            self.play(LaggedStart(*[FadeIn(b, shift=UP * 0.2) for b in row], lag_ratio=0.4),
                      run_time=rt(tr.duration * 0.45))
            self.play(Write(r2_big), run_time=1.0)
            self.play(Create(focus(r2_big, GOOD)), run_time=rt(min(0.8, tr.get_remaining_duration())))
            rest(self, tr)

        rule2 = math(r"I(1) = x", size=48).move_to(LEFT * 4.5 + UP * 1.6)
        alt = math(r"I(1) = x + 5", size=48, color=MUTED).next_to(rule2, DOWN, buff=0.6)
        alt_x = strikes(alt)
        outs = VGroup(*[math(o, r"+\,0", size=40) for o in ("x", r"\frac{x^2}{2}", r"\frac{x^3}{3}")]
                      ).arrange(DOWN, aligned_edge=LEFT, buff=0.35).move_to(UP * 0.4)
        for o in outs:
            o[1].set_color(GOOD)
        mini = plane(2.6).move_to(RIGHT * 4.3 + DOWN * 0.2)
        mu, ml, mc = regions(mini, 2)
        dot = Dot(mini.c2p(0, 0), color=GOOD, radius=0.12)
        with self.voiceover(text=N("s06.b4")) as tr:
            self.play(FadeOut(Group(*self.mobjects)), run_time=0.5)
            self.play(FadeIn(rule2), run_time=0.5)
            wait_until(self, tr, "noc")
            self.play(FadeIn(alt), run_time=0.5)
            self.play(Create(alt_x), run_time=0.5)
            self.play(LaggedStart(*[FadeIn(o) for o in outs], lag_ratio=0.3), run_time=1.2)
            self.play(Create(mini), FadeIn(mu), FadeIn(ml), Create(mc), run_time=1.0)
            self.play(FadeIn(dot, scale=2), Flash(dot, color=GOOD), run_time=rt(min(1.0, tr.get_remaining_duration())))
            rest(self, tr)

        double = math(r"x \mapsto \tfrac{x^2}{2}", r"\quad\Longrightarrow\quad", r"2x \mapsto x^2", size=44).move_to(UP * 1.6)
        poly = math(r"I(4x^3 - x + 7)", r"= 4\,I(x^3) - I(x) + 7\,I(1)", size=44).move_to(DOWN * 0.2)
        poly2 = math(r"= x^4 - \tfrac{x^2}{2} + 7x", size=44)
        with self.voiceover(text=N("s06.b5")) as tr:
            self.play(FadeOut(Group(*self.mobjects)), run_time=0.5)
            self.play(Write(double), run_time=1.2)
            self.play(Indicate(double[2][0], color=PRIMARY), run_time=1.0)
            self.play(Write(poly), run_time=rt(tr.get_remaining_duration() * 0.4))
            poly2.next_to(poly[1], DOWN, buff=0.4, aligned_edge=LEFT)
            self.play(Write(poly2), run_time=rt(tr.get_remaining_duration() * 0.5))
            hold = tr.get_remaining_duration() - 0.8
            if hold > 0.05:
                self.wait(hold)
            self.play(FadeOut(Group(*self.mobjects)), run_time=0.8)


# ---------------------------------------------------------------------------
# s07 Ending
# ---------------------------------------------------------------------------


class S07Ending(VoiceoverScene):
    def construct(self):
        self.set_speech_service(get_speech_service())
        ingredients = VGroup(
            text("linear", size=36), math("+", size=40), text("integration by parts", size=36),
            math("+", size=40), math(r"I(1) = x", size=40),
        ).arrange(RIGHT, buff=0.3).move_to(UP * 1.6)
        arrow = math(r"\Downarrow", size=48).next_to(ingredients, DOWN, buff=0.35)
        power = math(r"I(x^n) = \frac{x^{n+1}}{n+1}", size=56).next_to(arrow, DOWN, buff=0.35)

        with self.voiceover(text=N("s07.b1")) as tr:
            self.play(LaggedStart(*[FadeIn(m) for m in ingredients], lag_ratio=0.2), run_time=1.5)
            self.play(FadeIn(arrow), Write(power), run_time=rt(min(1.5, tr.get_remaining_duration())))
            rest(self, tr)

        prod = math(r"(pq)' = p'q + pq'", size=52).move_to(UP * 1.6)
        blank = lambda: Line(LEFT * 0.8, RIGHT * 0.8, color=PRIMARY, stroke_width=5)
        b1, b2 = blank(), blank()
        challenge = VGroup(
            text("linear", size=40), math("+", size=44), b1, math("+", size=44), b2,
            math(r"\Longrightarrow", size=44), text("derivative", size=40),
        ).arrange(RIGHT, buff=0.3).move_to(DOWN * 0.6)
        for b in (b1, b2):
            b.align_to(challenge[0], DOWN)
        with self.voiceover(text=N("s07.b2")) as tr:
            self.play(FadeOut(VGroup(ingredients, arrow, power)), run_time=0.6)
            self.play(Write(prod), run_time=rt(min(1.5, tr.time_until_bookmark("challenge") - 0.6)))
            wait_until(self, tr, "challenge")
            self.play(FadeIn(challenge, shift=UP * 0.2), run_time=1.0)
            self.play(Indicate(b1, scale_factor=1.3), Indicate(b2, scale_factor=1.3), run_time=1.0)
            rest(self, tr)

        with self.voiceover(text=N("s07.b3")) as tr:
            self.play(Indicate(b1, scale_factor=1.3), Indicate(b2, scale_factor=1.3), run_time=1.0)
            hold = tr.get_remaining_duration() - 1.2
            if hold > 0.05:
                self.wait(hold)
            self.play(FadeOut(Group(*self.mobjects)), run_time=1.2)
