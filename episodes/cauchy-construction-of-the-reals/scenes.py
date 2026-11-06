from manim import *
from manim_voiceover import VoiceoverScene

from mathvid import layout  # noqa: F401  must come before scene code runs
from mathvid.anim import rest, rt, strike, wait_until
from mathvid.layout import FW
from mathvid.numberline import ZoomLine
from mathvid.script import Script
from mathvid.style import BAD, BG, FG, GOOD, MUTED, PRIMARY, SECONDARY, math, text
from mathvid.voice import get_speech_service

N = Script(__file__)

SQ2 = 2**0.5
DEC_STR = ["1", "1.4", "1.41", "1.414", "1.4142", "1.41421", "1.414213", "1.4142135"]
DEC = [float(s) for s in DEC_STR]
ORB = [(1, 1), (3, 2), (7, 5), (17, 12), (41, 29), (99, 70)]
ABOVE_STR = ["2", "1.5", "1.42", "1.415", "1.4143"]

# Number line ranges for the zoom in s05. Z0 is also how s05 ends and s06 starts.
Z0 = (0.95, 1.55)
Z1 = (1.40, 1.43)
Z2 = (SQ2 - 0.0004, SQ2 + 0.0004)
Z3 = (1.39, 1.44)
Z4 = (1.411, 1.4175)
LINE_C = DOWN * 0.5


def frac(p, q):
    return str(p) if q == 1 else rf"\frac{{{p}}}{{{q}}}"


def refresh(*mobs):
    """Run updaters once, so a mobject redrawn while hidden fades in in its new state."""
    for m in mobs:
        m.update()


# ---------------------------------------------------------------------------
# Shared builders (also used by shorts.py)
# ---------------------------------------------------------------------------


def list_tex(terms):
    return r"\left(" + r",\ ".join(terms) + r",\ \dots\right)"


DEC_LIST = list_tex(DEC_STR[:5])
ORB_LIST = list_tex([frac(p, q) for p, q in ORB[:5]])


def set_of_lists(size=40, rows=(DEC_LIST, ORB_LIST)):
    """{ (1, 1.4, ...), (1, 3/2, ...), ... } as VGroup(left brace, rows, vdots, right brace)."""
    rs = VGroup(*[math(r, size=size) for r in rows]).arrange(DOWN, buff=0.45)
    vd = math(r"\vdots", size=size).next_to(rs, DOWN, buff=0.3)
    body = VGroup(rs, vd)
    lb, rb = Brace(body, LEFT, buff=0.25, color=MUTED), Brace(body, RIGHT, buff=0.25, color=MUTED)
    return VGroup(lb, rs, vd, rb)


def decimal_column(size=48, n=8):
    rows = VGroup(*[math(s, size=size) for s in DEC_STR[:n]])
    rows.arrange(DOWN, aligned_edge=LEFT, buff=0.24)
    vd = math(r"\vdots", size=size).next_to(rows, DOWN, buff=0.2).align_to(rows, LEFT).shift(RIGHT * 0.1)
    return VGroup(rows, vd)


def s04_column():
    return decimal_column().to_edge(LEFT, buff=1.0).shift(UP * 0.1)


def s04_row():
    """The same decimals laid out across the top: how s04 ends and s05 starts."""
    terms = VGroup(*[math(t + ",", size=40) for t in DEC_STR] + [math(r"\dots", size=40)])
    terms.arrange(RIGHT, buff=0.3, aligned_edge=DOWN).move_to(UP * 2.7)
    return terms


def unit_square(side=3.0):
    sq = Square(side, color=FG, stroke_width=4)
    diag = Line(sq.get_corner(DL), sq.get_corner(UR), color=PRIMARY, stroke_width=6)
    l1 = math("1", size=36, color=MUTED).next_to(sq, DOWN, buff=0.2)
    l2 = math("1", size=36, color=MUTED).next_to(sq, LEFT, buff=0.2)
    return VGroup(sq, l1, l2), diag


def term_row(terms, y, x0=-2.6, col=1.5, size=40, color=FG):
    """(t1, t2, ..., ...) with each term centered on a fixed column, so rows line up."""
    ts = VGroup(*[math(t, size=size, color=color).move_to([x0 + i * col, y, 0]) for i, t in enumerate(terms)])
    commas = VGroup(*[math(",", size=size, color=color).next_to(t, RIGHT, buff=0.06).align_to(t, DOWN)
                      .set_y(y - 0.18) for t in ts])
    lp = math(r"(", size=size + 6, color=color).next_to(ts[0], LEFT, buff=0.12).set_y(y)
    tail = math(r"\dots)", size=size, color=color)
    tail.next_to(commas[-1], RIGHT, buff=0.2).set_y(y)
    tail[0][-1].scale(1.15)
    return VGroup(lp, ts, commas, tail)


def row_label(tex, row, color=FG, size=40):
    return math(tex, size=size, color=color).next_to(row[0], LEFT, buff=0.3)


ROW_Y = (1.9, 0.6, -0.7)


def three_rows():
    r1 = term_row(DEC_STR[:5], ROW_Y[0])
    r2 = term_row([frac(p, q) for p, q in ORB[:5]], ROW_Y[1])
    r3 = term_row(ABOVE_STR, ROW_Y[2])
    return r1, r2, r3


def bundle(rows):
    """Gather rows into one brace group: VGroup(lb, rows, vdots, rb)."""
    rows = VGroup(*rows)
    vd = math(r"\vdots", size=40).next_to(rows, DOWN, buff=0.25)
    body = VGroup(rows, vd)
    lb, rb = Brace(body, LEFT, buff=0.2, color=MUTED), Brace(body, RIGHT, buff=0.2, color=MUTED)
    return VGroup(lb, rows, vd, rb)


def ruler(p1, p2, label_tex, y_off=0.55, color=SECONDARY):
    """A measuring bar between two points, with end stops and a label above."""
    a, b = p1 + UP * y_off, p2 + UP * y_off
    bar = Line(a, b, color=color, stroke_width=4)
    stops = VGroup(Line(a + DOWN * 0.15, a + UP * 0.15, color=color, stroke_width=4),
                   Line(b + DOWN * 0.15, b + UP * 0.15, color=color, stroke_width=4))
    lab = math(label_tex, size=38, color=color).next_to(bar, UP, buff=0.18)
    return VGroup(bar, stops, lab)


def padic_defs(size=36):
    lines = VGroup(
        math(r"x = 2^k \cdot \tfrac{a}{b}\quad(a, b \text{ odd})", size=size),
        math(r"v_2(x) = k", size=size),
        math(r"|x|_2 = 2^{-v_2(x)},\quad |0|_2 = 0", size=size),
        math(r"d_2(x, y) = |x - y|_2", size=size),
    ).arrange(DOWN, aligned_edge=LEFT, buff=0.4)
    return lines


def q2_symbol(size=120):
    return math(r"\mathbb{Q}_2", size=size, color=PRIMARY)


def sum_tex(size=56):
    return math(r"1 + 2 + 4 + 8 + \cdots = -1", size=size)


def make_zoomline(rng=Z0, length=12.0, center=LINE_C, label_size=28):
    zl = ZoomLine(*rng, length=length, center=center, label_size=label_size)
    ring = zl.ring(SQ2)
    dec_dots = [zl.dot(x, color=SECONDARY, hole=SQ2) for x in DEC]
    orb_dots = [zl.dot(p / q, color=PRIMARY, hole=SQ2) for p, q in ORB]
    arcs = [zl.arc(ORB[i][0] / ORB[i][1], ORB[i + 1][0] / ORB[i + 1][1], up=(i % 2 == 0), color=PRIMARY,
                   angle=0.45 * PI)
            for i in range(len(ORB) - 1)]
    return zl, ring, dec_dots, orb_dots, arcs


def orbit_in(scene, zl, orb_dots, arcs, per, zooms=None, highlight=None):
    """Drop the orbit fractions in one by one, drawing the jump arcs, zooming after
    selected terms. zooms: {index: (lo, hi)}. highlight: list of mobjects to color."""
    zooms = zooms or {}
    for i, d in enumerate(orb_dots):
        anims = [d.show.animate.set_value(1)]
        if i > 0:
            anims.append(arcs[i - 1].show.animate.set_value(1))
        if highlight is not None:
            anims.append(highlight[i].animate.set_color(PRIMARY))
        scene.play(*anims, run_time=rt(per))
        if i in zooms:
            scene.play(*zl.zoom_to(*zooms[i]), run_time=rt(per * 1.4))


# ---------------------------------------------------------------------------
# s01 Hook
# ---------------------------------------------------------------------------


class S01Hook(VoiceoverScene):
    def construct(self):
        self.set_speech_service(get_speech_service())
        q = math(r"\sqrt{2}", "=", "?", size=110)
        q[2].set_color(PRIMARY)

        with self.voiceover(text=N("s01.b1")) as tr:
            self.play(Write(q), run_time=rt(min(1.5, tr.duration)))
            rest(self, tr)

        st = set_of_lists(size=46)
        lead = math(r"\sqrt{2}", "=", size=72)
        VGroup(lead, st).arrange(RIGHT, buff=0.4).move_to(ORIGIN)
        with self.voiceover(text=N("s01.b2")) as tr:
            wait_until(self, tr, "set")
            self.play(TransformMatchingTex(q, lead), FadeIn(st[0]), FadeIn(st[3]), FadeIn(st[2]),
                      run_time=1.0)
            self.play(Indicate(VGroup(st[0], st[3]), color=PRIMARY, scale_factor=1.05), run_time=0.8)
            wait_until(self, tr, "lists")
            self.play(LaggedStart(*[Write(r) for r in st[1]], lag_ratio=0.5),
                      run_time=rt(min(2.5, tr.get_remaining_duration())))
            rest(self, tr)

        title = VGroup(text("So... what actually is", size=60, weight="BOLD"),
                       math(r"\sqrt{2}\,?", size=80, color=PRIMARY)).arrange(RIGHT, buff=0.3)
        with self.voiceover(text=N("s01.b3")) as tr:
            wait_until(self, tr, "title")
            self.play(FadeOut(VGroup(lead, st), scale=0.6), run_time=0.6)
            self.play(FadeIn(title, shift=UP * 0.2), run_time=0.7)
            rest(self, tr)
        self.wait(0.8)
        self.play(FadeOut(title), run_time=0.5)


# ---------------------------------------------------------------------------
# s02 The cult of numbers
# ---------------------------------------------------------------------------


def boat():
    hull = Polygon([-1.1, 0, 0], [1.1, 0, 0], [0.75, -0.4, 0], [-0.75, -0.4, 0],
                   color=FG, fill_color=FG, fill_opacity=1, stroke_width=0)
    mast = Line([0, 0, 0], [0, 1.6, 0], color=FG, stroke_width=4)
    sail = Polygon([0.06, 1.5, 0], [0.06, 0.15, 0], [0.95, 0.15, 0],
                   color=FG, fill_color=FG, fill_opacity=0.85, stroke_width=0)
    waves = VGroup(*[FunctionGraph(lambda x, k=k: 0.12 * np.sin(2.4 * x + k), x_range=[-3, 3],
                                   color=SECONDARY, stroke_width=3).shift(DOWN * (0.45 + 0.3 * k))
                     for k in range(3)])
    return VGroup(waves, VGroup(hull, mast, sail))


class S02Cult(VoiceoverScene):
    def construct(self):
        self.set_speech_service(get_speech_service())

        star = RegularPolygram(5, density=2, radius=1.5, color=PRIMARY, stroke_width=5)
        ring = Circle(radius=1.5, color=PRIMARY, stroke_width=3)
        motto = text("All is number", size=44).next_to(VGroup(star, ring), DOWN, buff=0.5)
        emblem = VGroup(star, ring, motto).move_to(UP * 0.3)
        floats = VGroup(*[math(t, size=50, color=SECONDARY).move_to(p) for t, p in [
            ("1", LEFT * 4.5 + UP * 2.2), ("2", RIGHT * 4.2 + UP * 2.6), ("3", LEFT * 5.2 + DOWN * 1.4),
            (r"\tfrac12", RIGHT * 5.0 + DOWN * 0.6), (r"\tfrac23", LEFT * 3.4 + DOWN * 2.8),
            (r"\tfrac54", RIGHT * 3.6 + DOWN * 2.8)]])
        with self.voiceover(text=N("s02.b1")) as tr:
            self.play(Create(star), Create(ring), run_time=1.5)
            wait_until(self, tr, "creed")
            self.play(FadeIn(motto, shift=UP * 0.2), run_time=0.8)
            wait_until(self, tr, "ratios")
            self.play(LaggedStart(*[FadeIn(f, scale=0.6) for f in floats], lag_ratio=0.25),
                      run_time=rt(min(2.0, tr.get_remaining_duration())))
            rest(self, tr)

        nl = NumberLine(x_range=[0, 2, 1], length=11, color=MUTED, include_numbers=True,
                        font_size=40, stroke_width=3).shift(DOWN * 0.3)
        rounds = []
        for n in range(1, 7):
            g = VGroup()
            for k in range(1, 2 * 2**n, 2):
                x = k / 2**n
                h = 0.5 / n**0.7
                p = nl.n2p(x)
                g.add(Line(p + DOWN * h / 2, p + UP * h / 2, color=SECONDARY,
                           stroke_width=max(1.2, 4 - 0.5 * n)))
                if n <= 2:
                    g.add(math(rf"\frac{{{k}}}{{{2**n}}}", size=40 if n == 1 else 32, color=SECONDARY)
                          .next_to(p, UP, buff=0.25 + h / 2))
            rounds.append(g)
        with self.voiceover(text=N("s02.b2")) as tr:
            self.play(FadeOut(VGroup(emblem, floats)), run_time=0.6)
            self.play(Create(nl), run_time=1.0)
            self.play(FadeIn(rounds[0]), run_time=1.0)
            wait_until(self, tr, "fill")
            per = max(0.3, (tr.get_remaining_duration() - 1.0) / 5)
            for g in rounds[1:]:
                self.play(LaggedStart(*[FadeIn(m) for m in g], lag_ratio=0.02), run_time=per)
            rest(self, tr)

        usq, diag = unit_square(3.0)
        VGroup(usq, diag).move_to(LEFT * 2.6 + DOWN * 0.2)
        qm = math("?", size=48, color=PRIMARY).move_to(diag.get_center() + UL * 0.45)
        with self.voiceover(text=N("s02.b3")) as tr:
            wait_until(self, tr, "sq")
            self.play(FadeOut(VGroup(nl, *rounds)), run_time=0.5)
            self.play(Create(usq[0]), FadeIn(usq[1:]), run_time=0.8)
            wait_until(self, tr, "diag")
            self.play(Create(diag), FadeIn(qm), run_time=1.0)
            rest(self, tr)

        r2 = math(r"\sqrt{2}", size=44, color=PRIMARY).move_to(qm)
        pyth = math(r"1^2 + 1^2 = \left(\sqrt{2}\right)^2", size=52).move_to(RIGHT * 3.3 + UP * 0.8)
        which = math(r"\left(\frac{a}{b}\right)^2 = 2\;?", size=56, color=PRIMARY).next_to(pyth, DOWN, buff=0.8)
        with self.voiceover(text=N("s02.b4")) as tr:
            self.play(Transform(qm, r2), FadeIn(pyth), run_time=1.2)
            self.wait(rt(tr.get_remaining_duration() * 0.45 - 1.2))
            self.play(Write(which), run_time=1.0)
            rest(self, tr)

        bt = boat().scale(0.9).move_to(RIGHT * 0.4 + DOWN * 0.2)
        cap = text("Hippasus (legend)", size=30, color=MUTED).next_to(bt, DOWN, buff=0.4)
        with self.voiceover(text=N("s02.b5")) as tr:
            self.play(FadeOut(VGroup(pyth, which)), VGroup(usq, diag, qm).animate.scale(0.6).to_edge(LEFT, buff=0.8),
                      run_time=0.8)
            wait_until(self, tr, "boat")
            self.play(FadeIn(bt, shift=UP * 0.3), FadeIn(cap), run_time=1.0)
            self.play(bt[1].animate.shift(RIGHT * 0.5).rotate(0.06), run_time=1.5, rate_func=there_and_back)
            rest(self, tr)
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.6)


# ---------------------------------------------------------------------------
# s03 No fraction squares to two (the picture proof)
# ---------------------------------------------------------------------------


class S03Proof(VoiceoverScene):
    def construct(self):
        self.set_speech_service(get_speech_service())
        A = 4.4
        B = A / SQ2
        C = LEFT * 3.4 + DOWN * 0.3
        O = C - np.array([A / 2, A / 2, 0])

        def at(x, y):
            return O + np.array([x, y, 0])

        big = Square(A, color=FG, stroke_width=4).move_to(C)
        la = math("a", size=40).next_to(big, DOWN, buff=0.2)
        s1 = Square(B, color=SECONDARY, stroke_width=3, fill_color=SECONDARY, fill_opacity=0.35)
        s2 = s1.copy()
        VGroup(s1, s2).arrange(RIGHT, buff=0.3).move_to(RIGHT * 3.2 + DOWN * 0.3 + DOWN * (A - B) / 2)
        lb1 = math("b", size=40).next_to(s1, DOWN, buff=0.2)
        lb2 = math("b", size=40).next_to(s2, DOWN, buff=0.2)

        top = math(r"\sqrt{2} = \frac{a}{b}", size=56).move_to(UP * 3.2)
        top2 = math(r"a^2 = 2b^2", size=56).move_to(top)
        with self.voiceover(text=N("s03.b1")) as tr:
            self.play(Write(top), run_time=1.2)
            self.wait(rt(tr.time_until_bookmark("areas") - 2.4))
            self.play(TransformMatchingShapes(top, top2), run_time=1.0)
            wait_until(self, tr, "areas")
            self.play(Create(big), FadeIn(la), run_time=1.0)
            self.play(FadeIn(s1), FadeIn(s2), FadeIn(lb1), FadeIn(lb2), run_time=1.0)
            rest(self, tr)

        overlap = Square(2 * B - A, color=PRIMARY, stroke_width=3, fill_color=PRIMARY, fill_opacity=0.9).move_to(C)
        tl = Square(A - B, color=BAD, stroke_width=5).move_to(at((A - B) / 2, (A + B) / 2))
        br = Square(A - B, color=BAD, stroke_width=5).move_to(at((A + B) / 2, (A - B) / 2))
        with self.voiceover(text=N("s03.b2")) as tr:
            self.play(FadeOut(lb1), FadeOut(lb2), s1.animate.move_to(at(B / 2, B / 2)),
                      s2.animate.move_to(at(A - B / 2, A - B / 2)), run_time=1.6)
            wait_until(self, tr, "overlap")
            self.play(FadeIn(overlap), run_time=0.8)
            wait_until(self, tr, "corners")
            self.play(Create(tl), Create(br), run_time=0.8)
            self.play(Indicate(tl, color=BAD), Indicate(br, color=BAD), run_time=0.8)
            rest(self, tr)

        icon_o = Square(1.0, color=PRIMARY, fill_color=PRIMARY, fill_opacity=0.9, stroke_width=3)
        icon_c1 = Square(1.0 * (A - B) / (2 * B - A), color=BAD, stroke_width=4)
        icon_c2 = icon_c1.copy()
        eqn = VGroup(icon_o, math("=", size=56), icon_c1, math("+", size=56), icon_c2)
        eqn.arrange(RIGHT, buff=0.35).move_to(RIGHT * 3.4 + DOWN * 0.3)
        with self.voiceover(text=N("s03.b3")) as tr:
            self.play(Indicate(overlap, color=PRIMARY, scale_factor=1.15), run_time=1.0)
            self.play(Indicate(VGroup(tl, br), color=BAD, scale_factor=1.1), run_time=1.0)
            wait_until(self, tr, "eq")
            self.play(TransformFromCopy(overlap, icon_o), run_time=0.8)
            self.play(FadeIn(eqn[1]), TransformFromCopy(tl, icon_c1), FadeIn(eqn[3]),
                      TransformFromCopy(br, icon_c2), run_time=1.0)
            rest(self, tr)

        lo = math("2b-a", size=42, color=BG).move_to(overlap)
        lc1 = math("a-b", size=36, color=BAD).move_to(tl)
        lc2 = math("a-b", size=36, color=BAD).move_to(br)
        note = text("whole numbers, smaller than a and b", size=32, color=MUTED).move_to(RIGHT * 3.4 + DOWN * 1.8)
        with self.voiceover(text=N("s03.b4")) as tr:
            wait_until(self, tr, "sides")
            self.play(FadeIn(lo), run_time=0.7)
            self.play(FadeIn(lc1), FadeIn(lc2), run_time=0.7)
            self.wait(rt(tr.get_remaining_duration() * 0.4))
            self.play(FadeIn(note), run_time=0.7)
            rest(self, tr)

        picture = VGroup(big, la, s1, s2, overlap, tl, br, lo, lc1, lc2)
        new_big = VGroup(overlap.copy(), lo.copy())
        new_c1, new_c2 = VGroup(tl.copy(), lc1.copy()), VGroup(br.copy(), lc2.copy())
        for m in (new_c1, new_c2):
            m[0].set_fill(BAD, 0.35)
        target = VGroup(new_big.copy(), new_c1.copy(), new_c2.copy()).arrange(RIGHT, buff=0.4, aligned_edge=DOWN)
        target.move_to(RIGHT * 3.4 + DOWN * 0.3)
        contra = text("Contradiction.", size=44, color=BAD).move_to(RIGHT * 3.4 + DOWN * 2.4)
        with self.voiceover(text=N("s03.b5")) as tr:
            self.play(FadeOut(eqn), FadeOut(note), run_time=0.5)
            self.play(picture.animate.set_opacity(0.25), run_time=0.6)
            wait_until(self, tr, "smaller")
            self.play(Transform(new_big, target[0]), Transform(new_c1, target[1]), Transform(new_c2, target[2]),
                      run_time=1.4)
            self.wait(rt(tr.get_remaining_duration() - 1.4))
            self.play(Write(contra), run_time=0.8)
            rest(self, tr)

        usq, diag, lab, verdict = s03_verdict()
        with self.voiceover(text=N("s03.b6")) as tr:
            self.play(FadeOut(VGroup(picture, new_big, new_c1, new_c2, contra, top2)), run_time=0.7)
            self.play(Create(usq[0]), FadeIn(usq[1:]), Create(diag), FadeIn(lab), run_time=1.0)
            self.play(Write(verdict), run_time=1.2)
            rest(self, tr)


def s03_verdict():
    """The last frame of s03, which s04 starts from."""
    usq, diag = unit_square(2.6)
    VGroup(usq, diag).move_to(LEFT * 3.2)
    lab = math(r"\sqrt{2}", size=40, color=PRIMARY).move_to(diag.get_center() + UL * 0.4)
    verdict = VGroup(math(r"\sqrt{2}", size=64, color=PRIMARY), text("is not a fraction", size=52)).arrange(RIGHT, buff=0.3)
    verdict.move_to(RIGHT * 2.4)
    return VGroup(usq, diag, lab, verdict)


# ---------------------------------------------------------------------------
# s04 Nobody notices
# ---------------------------------------------------------------------------


def calculator():
    body = RoundedRectangle(corner_radius=0.25, width=3.0, height=4.4, color=MUTED, stroke_width=3)
    disp = Rectangle(width=2.5, height=0.8, color=MUTED, stroke_width=2).move_to(body.get_top() + DOWN * 0.7)
    val = text("1.414213562", size=30).move_to(disp).align_to(disp, RIGHT).shift(LEFT * 0.15)
    keys = VGroup(*[RoundedRectangle(corner_radius=0.06, width=0.48, height=0.42, color=MUTED, stroke_width=2)
                    for _ in range(16)]).arrange_in_grid(4, 4, buff=0.14)
    keys.next_to(disp, DOWN, buff=0.35)
    return VGroup(body, disp, keys, val)


class S04Digits(VoiceoverScene):
    def construct(self):
        self.set_speech_service(get_speech_service())
        col = s04_column()
        rows, vd = col
        prev = s03_verdict()
        self.add(prev)
        with self.voiceover(text=N("s04.b1")) as tr:
            wait_until(self, tr, "digits")
            self.play(FadeOut(prev), run_time=0.5)
            per = max(0.3, (tr.get_remaining_duration() - 0.3) / (len(rows) + 1))
            for r in rows:
                self.play(Write(r), run_time=per)
            self.play(FadeIn(vd), run_time=per)
            rest(self, tr)

        calc = calculator().move_to(RIGHT * 4.6)
        fracs = VGroup(*[math(rf"= {s.replace('.', '')}/{10 ** (len(s) - 2)}", size=40,
                              color=PRIMARY).next_to(r, RIGHT, buff=0.35)
                         for s, r in zip(DEC_STR[1:], rows[1:])])
        for f, r in zip(fracs, rows[1:]):
            f.set_x(rows.get_right()[0] + 0.4 + f.width / 2)
        with self.voiceover(text=N("s04.b2")) as tr:
            self.play(FadeIn(calc, shift=LEFT * 0.3), run_time=1.0)
            wait_until(self, tr, "frac")
            self.play(LaggedStart(*[FadeIn(f, shift=RIGHT * 0.2) for f in fracs], lag_ratio=0.25),
                      run_time=rt(min(2.5, tr.get_remaining_duration())))
            rest(self, tr)

        row = s04_row()
        with self.voiceover(text=N("s04.b3")) as tr:
            self.play(FadeOut(calc), FadeOut(fracs), run_time=0.8)
            self.play(*[ReplacementTransform(r, t) for r, t in zip(rows, row[:-1])],
                      ReplacementTransform(vd, row[-1]), run_time=1.2)
            rest(self, tr)


# ---------------------------------------------------------------------------
# s05 Something we can't see
# ---------------------------------------------------------------------------


def starfield(seed=3, n=160):
    rng = np.random.default_rng(seed)
    g = VGroup()
    for _ in range(n):
        d = Dot(radius=rng.uniform(0.008, 0.022), color=FG)
        d.set_opacity(rng.uniform(0.2, 0.8))
        d.move_to([rng.uniform(-FW / 2, FW / 2), rng.uniform(-4, 4), 0])
        g.add(d)
    return g


ORBITS = [(2.3, 0.86, 0.35, 0.0), (1.6, 0.6, 2.5, 1.7), (2.0, 0.75, 4.3, 3.6)]  # a, e, periapsis angle, phase


def kepler(a, e, w, M):
    E = M
    for _ in range(8):
        E = E - (E - e * np.sin(E) - M) / (1 - e * np.cos(E))
    x, y = a * (np.cos(E) - e), a * np.sqrt(1 - e * e) * np.sin(E)
    c, s = np.cos(w), np.sin(w)
    return np.array([c * x - s * y, s * x + c * y, 0])


class S05Unseen(VoiceoverScene):
    def construct(self):
        self.set_speech_service(get_speech_service())
        row = s04_row()
        rows, vd = row[:-1], row[-1]
        self.add(row)
        zl, ring, dec_dots, orb_dots, arcs = make_zoomline(Z0)
        zl.hole_r.set_value(0)
        tag = text("fractions only", size=30, color=MUTED).to_corner(UL, buff=0.5)

        with self.voiceover(text=N("s05.b1")) as tr:
            self.play(Create(zl.line), FadeIn(zl.ticks), FadeIn(tag), run_time=1.0)
            self.add(*dec_dots)
            per = max(0.25, (tr.get_remaining_duration() - 0.5) / (len(rows) + 1))
            anims = []
            for r, x, d in zip(rows, DEC, dec_dots):
                target = zl.p(x)
                anims.append(AnimationGroup(r.animate.move_to(target).scale(0.4).set_opacity(0),
                                            d.show.animate.set_value(1)))
            self.play(LaggedStart(*anims, lag_ratio=0.7), FadeOut(vd), run_time=per * (len(rows) + 1))
            self.remove(rows)
            rest(self, tr)

        no_frac = text("no fraction here", size=30, color=MUTED)
        no_frac.add_updater(lambda m: m.next_to(zl.p(SQ2), UP, buff=0.35))
        with self.voiceover(text=N("s05.b2")) as tr:
            wait_until(self, tr, "zoom")
            self.play(*zl.zoom_to(*Z1), run_time=1.1)
            self.wait(0.2)
            self.play(*zl.zoom_to(*Z2), run_time=1.1)
            wait_until(self, tr, "hole")
            refresh(ring)
            no_frac.update()
            self.play(Create(ring), FadeIn(no_frac), zl.hole_r.animate.set_value(0.16), run_time=0.8)
            rest(self, tr)

        top = VGroup(*[math(frac(p, q) + ("," if i < len(ORB) - 1 else r",\ \dots"), size=38, color=MUTED)
                       for i, (p, q) in enumerate(ORB)]).arrange(RIGHT, buff=0.3).move_to(UP * 2.6)
        with self.voiceover(text=N("s05.b3")) as tr:
            self.wait(0.5)
            self.play(FadeOut(no_frac), *zl.zoom_to(*Z0), FadeIn(top), run_time=1.0)
            wait_until(self, tr, "orbit")
            self.add(*orb_dots, *arcs)
            per = max(0.3, tr.get_remaining_duration() / (len(ORB) + 2 * 1.4))
            orbit_in(self, zl, orb_dots, arcs, per, zooms={2: Z3, 4: Z4}, highlight=top)
            rest(self, tr)

        line_stuff = VGroup(zl, ring, tag, top, *dec_dots, *orb_dots, *arcs)
        sky = starfield()
        focus = UP * 0.3
        paths = VGroup(*[ParametricFunction(lambda t, o=o: focus + kepler(o[0], o[1], o[2], t), t_range=[0, TAU],
                                            color=MUTED, stroke_width=2, stroke_opacity=0.45) for o in ORBITS])
        T = ValueTracker(0)
        stars = VGroup(*[always_redraw(lambda o=o: Dot(radius=0.07, color=FG).move_to(
            focus + kepler(o[0], o[1], o[2], o[3] + T.get_value() * 1.6 / o[0] ** 1.5)))
            for o in ORBITS])
        cap = text("stars orbiting Sagittarius A*", size=28, color=MUTED).to_edge(DOWN, buff=0.4)
        with self.voiceover(text=N("s05.b4")) as tr:
            self.play(FadeOut(line_stuff), FadeIn(sky), run_time=0.8)
            self.play(Create(paths), FadeIn(stars), FadeIn(cap), run_time=1.0)
            self.play(T.animate.set_value(tr.get_remaining_duration()), run_time=rt(tr.get_remaining_duration()),
                      rate_func=linear)

        zl.set_range(*Z3)
        refresh(zl.ticks, ring, *dec_dots, *orb_dots, *arcs)
        line_back = VGroup(zl, ring, tag, *dec_dots, *orb_dots, *arcs)
        ok = VGroup(text("close to each other", size=42), math(r"\checkmark", size=46, color=GOOD)).arrange(RIGHT, buff=0.25)
        blank = Line(LEFT * 0.8, RIGHT * 0.8, color=MUTED, stroke_width=3)
        unknown = VGroup(text("close to", size=42, color=MUTED), blank).arrange(RIGHT, buff=0.25)
        blank.align_to(unknown[0], DOWN)
        VGroup(ok, unknown).arrange(DOWN, aligned_edge=LEFT, buff=0.35).move_to(UP * 2.3)
        with self.voiceover(text=N("s05.b5")) as tr:
            self.play(FadeOut(VGroup(sky, paths, stars, cap)), run_time=0.6)
            self.play(FadeIn(line_back), run_time=0.6)
            wait_until(self, tr, "close")
            self.play(FadeIn(ok, shift=DOWN * 0.2), run_time=0.8)
            wait_until(self, tr, "blank")
            self.play(FadeIn(unknown, shift=DOWN * 0.2), run_time=0.8)
            rest(self, tr)

        qlab = math("q", size=44, color=PRIMARY)
        qarrow = Arrow(UP * 0.9, ORIGIN, buff=0, color=PRIMARY, stroke_width=4, max_tip_length_to_length_ratio=0.3)
        qgroup = VGroup(qlab, qarrow).arrange(DOWN, buff=0.1).next_to(zl.p(SQ2), UP, buff=0.2)
        sq_row = math(r"\text{squares: }\ 1,\ 1.96,\ 1.9881,\ 1.999396,\ \dots \to 2", size=44).move_to(UP * 2.9)
        q2 = math(r"q^2 = 2", size=52, color=PRIMARY).move_to(UP * 1.8)
        why = text("(no fraction squares to 2)", size=32, color=MUTED).next_to(q2, RIGHT, buff=0.4)
        with self.voiceover(text=N("s05.b6")) as tr:
            self.play(FadeOut(VGroup(ok, unknown)), FadeIn(qgroup, shift=DOWN * 0.2), run_time=0.8)
            wait_until(self, tr, "squares")
            self.play(Write(sq_row), run_time=1.5)
            self.wait(rt(tr.time_until_bookmark("strike") - 1.2))
            self.play(FadeIn(q2), run_time=0.8)
            wait_until(self, tr, "strike")
            cross = strike(q2)
            self.play(Create(cross), FadeIn(why), run_time=0.7)
            rest(self, tr)
        self.play(FadeOut(VGroup(qgroup, sq_row, q2, cross, why, tag, *orb_dots, *arcs)), *zl.zoom_to(*Z0),
                  run_time=1.0)


# ---------------------------------------------------------------------------
# s06 Let the evidence be the number
# ---------------------------------------------------------------------------


def def_row():
    r1 = term_row(DEC_STR[:5], ROW_Y[0])
    lab = row_label(r"\sqrt{2} :=", r1)
    return r1, lab


class S06Evidence(VoiceoverScene):
    def construct(self):
        self.set_speech_service(get_speech_service())
        zl, ring, dec_dots, _, _ = make_zoomline(Z0)
        for d in dec_dots:
            d.show.set_value(1)
        refresh(*dec_dots)
        self.add(zl, ring, *dec_dots)

        r1, lab = def_row()
        with self.voiceover(text=N("s06.b1")) as tr:
            self.play(LaggedStart(*[Flash(zl.p(x), color=SECONDARY, line_length=0.18, flash_radius=0.22)
                                    for x in DEC[:3]], lag_ratio=0.3), run_time=1.2)
            wait_until(self, tr, "list")
            flyers = []
            for i, t in enumerate(r1[1]):
                src = math(DEC_STR[i], size=24, color=SECONDARY)
                x = DEC[i]
                src.move_to(zl.p(x) if abs(zl.u(x) - zl.u(SQ2)) > 0.16 else zl.p(SQ2)).set_opacity(0)
                flyers.append((src, t))
            self.play(*[ReplacementTransform(s.set_opacity(1), t) for s, t in flyers],
                      FadeIn(r1[0]), FadeIn(r1[2]), FadeIn(r1[3]),
                      FadeOut(VGroup(*dec_dots)), run_time=1.6)
            self.play(FadeOut(VGroup(zl, ring)), run_time=0.6)
            rest(self, tr)

        with self.voiceover(text=N("s06.b2")) as tr:
            wait_until(self, tr, "def")
            self.play(Write(lab), run_time=0.8)
            rest(self, tr)


# ---------------------------------------------------------------------------
# s07 Too many names
# ---------------------------------------------------------------------------


class S07Names(VoiceoverScene):
    def construct(self):
        self.set_speech_service(get_speech_service())
        r1, lab1 = def_row()
        _, r2, r3 = three_rows()
        self.add(r1, lab1)
        lab2 = VGroup(text("?", size=40, color=BAD), row_label(r"\sqrt{2} :=", r2, color=BAD))
        lab3 = VGroup(text("?", size=40, color=BAD), row_label(r"\sqrt{2} :=", r3, color=BAD))
        for lab in (lab2, lab3):
            lab[0].next_to(lab[1], LEFT, buff=0.2)
        with self.voiceover(text=N("s07.b1")) as tr:
            wait_until(self, tr, "two")
            self.play(FadeIn(r2, shift=DOWN * 0.2), FadeIn(lab2), run_time=0.9)
            wait_until(self, tr, "three")
            self.play(FadeIn(r3, shift=DOWN * 0.2), FadeIn(lab3), run_time=0.9)
            self.play(Indicate(VGroup(lab1, lab2, lab3), color=BAD, scale_factor=1.06), run_time=1.0)
            rest(self, tr)

        gaps = VGroup(*[math(g, size=38, color=PRIMARY).move_to([-2.6 + i * 1.5, -2.1, 0])
                        for i, g in enumerate(["1", "0.1", "0.01", "0.001", "0.0001"])])
        to0 = math(r"\to 0", size=38, color=PRIMARY).next_to(gaps, RIGHT, buff=0.5)
        glab = text("gap", size=34, color=MUTED).next_to(gaps, LEFT, buff=0).set_x(lab1.get_center()[0])
        sep = Line(LEFT * 3.5, RIGHT * 5.0, color=MUTED, stroke_width=2).move_to(DOWN * 1.45 + RIGHT * 0.75)
        with self.voiceover(text=N("s07.b2")) as tr:
            self.play(VGroup(r2, lab2).animate.set_opacity(0.3), r3.animate.set_color(SECONDARY),
                      r1.animate.set_color(SECONDARY), run_time=0.8)
            wait_until(self, tr, "gap")
            self.play(Create(sep), FadeIn(glab), run_time=0.5)
            per = max(0.3, (tr.get_remaining_duration() - 0.8) / 6)
            for g in gaps:
                self.play(FadeIn(g, shift=DOWN * 0.15), run_time=per)
            self.play(Write(to0), run_time=0.8)
            rest(self, tr)

        b = bundle([r1, r2, r3])
        big_lab = math(r"\sqrt{2} =", size=48, color=PRIMARY).next_to(b, LEFT, buff=0.3)
        with self.voiceover(text=N("s07.b3")) as tr:
            self.play(FadeOut(VGroup(gaps, to0, glab, sep)), run_time=0.6)
            self.play(VGroup(r2, lab2).animate.set_opacity(1), r1.animate.set_color(FG), r3.animate.set_color(FG),
                      run_time=0.6)
            wait_until(self, tr, "group")
            self.play(FadeOut(VGroup(lab1, lab2, lab3)), run_time=0.5)
            self.play(GrowFromCenter(b[0]), GrowFromCenter(b[3]), FadeIn(b[2]), Write(big_lab), run_time=1.2)
            rest(self, tr)

        ones = term_row(["1", "1", "1", "1"], 1.2, x0=-2.0, col=1.6)
        nines = term_row(["0.9", "0.99", "0.999", "0.9999"], -0.5, x0=-2.0, col=1.6)
        ngaps = VGroup(*[math(g, size=30, color=MUTED).move_to([-2.0 + i * 1.6, 0.35, 0])
                         for i, g in enumerate(["0.1", "0.01", "0.001", "0.0001"])])
        res = math(r"0.999\ldots = 1", size=60, color=PRIMARY).move_to(DOWN * 2.2)
        with self.voiceover(text=N("s07.b4")) as tr:
            self.play(FadeOut(VGroup(b, big_lab)), run_time=0.6)
            self.play(FadeIn(ones), FadeIn(nines), run_time=0.8)
            self.play(LaggedStart(*[FadeIn(g) for g in ngaps], lag_ratio=0.3), run_time=0.8)
            wait_until(self, tr, "nines")
            self.play(Write(res), run_time=0.8)
            hold = tr.get_remaining_duration() - 0.6
            if hold > 0.05:
                self.wait(hold)
            self.play(FadeOut(VGroup(ones, nines, ngaps, res)), run_time=0.6)


# ---------------------------------------------------------------------------
# s08 What a real number is
# ---------------------------------------------------------------------------


class S08Real(VoiceoverScene):
    def construct(self):
        self.set_speech_service(get_speech_service())
        b = bundle(three_rows())
        big_lab = math(r"\sqrt{2} =", size=48, color=PRIMARY).next_to(b, LEFT, buff=0.3)
        whole = VGroup(big_lab, b).scale(0.8).move_to(UP * 0.8)
        defn = VGroup(text("√2 = the set of all sequences of rationals", size=36),
                      text("that close in on the same spot", size=36)).arrange(DOWN, buff=0.2)
        defn.move_to(DOWN * 2.8)
        with self.voiceover(text=N("s08.b1")) as tr:
            self.play(FadeIn(whole), run_time=0.8)
            wait_until(self, tr, "formal")
            self.play(Indicate(b[0], color=PRIMARY), Indicate(b[3], color=PRIMARY), run_time=0.8)
            self.play(FadeIn(defn, shift=UP * 0.2), run_time=1.0)
            rest(self, tr)

        nl = NumberLine(x_range=[0, 4, 1], length=11, color=MUTED, include_numbers=True, font_size=34,
                        stroke_width=3).shift(DOWN * 1.6)
        pts = {}
        for key, val, tex in [("half", 0.5, r"\tfrac12"), ("r2", SQ2, r"\sqrt{2}"), ("e", np.e, "e"), ("pi", PI, r"\pi")]:
            d = Dot(nl.n2p(val), radius=0.09, color=PRIMARY)
            lab = math(tex, size=36, color=PRIMARY).next_to(d, UP, buff=0.3)
            glyph = math(r"\{\dots\}", size=26, color=MUTED).next_to(lab, UP, buff=0.2)
            pts[key] = VGroup(d, lab, glyph)
        add_l = math(r"(a_1, a_2, a_3, \dots) + (b_1, b_2, b_3, \dots) = (a_1 + b_1,\ a_2 + b_2,\ a_3 + b_3,\ \dots)",
                     size=34)
        mul_l = math(r"(a_1, a_2, a_3, \dots) \times (b_1, b_2, b_3, \dots) = (a_1 b_1,\ a_2 b_2,\ a_3 b_3,\ \dots)",
                     size=34)
        ops = VGroup(add_l, mul_l).arrange(DOWN, buff=0.35).move_to(UP * 2.5)
        with self.voiceover(text=N("s08.b2")) as tr:
            self.play(FadeOut(defn), run_time=0.5)
            self.play(Create(nl), ReplacementTransform(whole, pts["r2"]), run_time=1.2)
            self.play(FadeIn(pts["pi"], shift=DOWN * 0.2), run_time=0.7)
            wait_until(self, tr, "half")
            self.play(FadeIn(pts["half"], shift=DOWN * 0.2), FadeIn(pts["e"], shift=DOWN * 0.2), run_time=0.8)
            wait_until(self, tr, "add")
            self.play(FadeIn(add_l), run_time=0.8)
            self.play(FadeIn(mul_l), run_time=0.8)
            rest(self, tr)

        names = VGroup(text("Charles Méray (1869)", size=38), text("Georg Cantor (1872)", size=38))
        names.arrange(RIGHT, buff=1.0).move_to(UP * 2.6)
        with self.voiceover(text=N("s08.b3")) as tr:
            self.play(FadeOut(ops), run_time=0.6)
            wait_until(self, tr, "names")
            self.play(LaggedStart(*[FadeIn(n, shift=DOWN * 0.2) for n in names], lag_ratio=0.4), run_time=1.2)
            rest(self, tr)

        target = pts["r2"][0]
        seq = [SQ2 + (-1) ** k * 0.9 * 0.55**k for k in range(8)]
        crowd = VGroup(*[Dot(nl.n2p(x), radius=max(0.03, 0.07 - 0.005 * k), color=SECONDARY)
                         for k, x in enumerate(seq)])
        filled = text("no holes left", size=40, color=GOOD).move_to(UP * 2.6)
        with self.voiceover(text=N("s08.b4")) as tr:
            self.play(FadeOut(names), run_time=0.6)
            per = max(0.2, (tr.time_until_bookmark("filled") - 0.2) / len(crowd))
            for d in crowd:
                self.play(FadeIn(d, shift=DOWN * 0.3), run_time=per)
            wait_until(self, tr, "filled")
            self.play(Flash(target, color=PRIMARY, line_length=0.3, flash_radius=0.35),
                      target.animate.scale(1.5), run_time=0.8)
            self.play(FadeIn(filled), run_time=0.6)
            rest(self, tr)
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.6)


# ---------------------------------------------------------------------------
# s09 Change the ruler
# ---------------------------------------------------------------------------


class S09Ruler(VoiceoverScene):
    def construct(self):
        self.set_speech_service(get_speech_service())
        nl = NumberLine(x_range=[-1, 3, 1], length=11, color=MUTED, include_numbers=True, font_size=34,
                        stroke_width=3).shift(DOWN * 0.8)
        px, py = nl.n2p(0.25), nl.n2p(1.75)
        dx, dy = Dot(px, color=FG), Dot(py, color=FG)
        lx = math("x", size=40).next_to(dx, DOWN, buff=0.55)
        ly = math("y", size=40).next_to(dy, DOWN, buff=0.55)
        rl = ruler(px, py, r"|x - y|")
        with self.voiceover(text=N("s09.b1")) as tr:
            self.play(Create(nl), run_time=1.0)
            self.play(FadeIn(VGroup(dx, dy, lx, ly)), run_time=0.6)
            wait_until(self, tr, "ruler")
            self.play(GrowFromCenter(rl[0]), FadeIn(rl[1]), Write(rl[2]), run_time=1.0)
            rest(self, tr)

        defs = padic_defs(36).move_to(LEFT * 3.3 + UP * 0.2)
        q2 = q2_symbol(120).move_to(RIGHT * 3.6 + UP * 1.2)
        with self.voiceover(text=N("s09.b2")) as tr:
            wait_until(self, tr, "swap")
            self.play(FadeOut(VGroup(nl, dx, dy, lx, ly, rl)), run_time=0.6)
            self.play(FadeIn(defs, lag_ratio=0.3), run_time=rt(min(3.0, tr.get_remaining_duration() - 0.8)))
            self.play(Write(q2), run_time=0.8)
            rest(self, tr)

        s = sum_tex(48).next_to(q2, DOWN, buff=0.7)
        with self.voiceover(text=N("s09.b3")) as tr:
            wait_until(self, tr, "sum")
            self.play(Write(s), run_time=rt(min(2.5, tr.get_remaining_duration())))
            rest(self, tr)

        b = bundle(three_rows()).scale(0.55)
        rlab = math(r"\mathbb{R}", size=72, color=SECONDARY).next_to(b, DOWN, buff=0.4)
        left = VGroup(b, rlab).move_to(LEFT * 3.4 + UP * 0.2)
        right = VGroup(q2, s)
        with self.voiceover(text=N("s09.b4")) as tr:
            self.play(FadeOut(defs), right.animate.move_to(RIGHT * 3.2 + UP * 0.2), run_time=0.8)
            self.play(FadeIn(left), run_time=0.8)
            hold = tr.get_remaining_duration() - 1.0
            if hold > 0.05:
                self.wait(hold)
            self.play(FadeOut(Group(*self.mobjects)), run_time=1.0)
        self.wait(0.5)


# ---------------------------------------------------------------------------
# Thumbnail (rendered as a still by scripts/finish.py)
# ---------------------------------------------------------------------------


class Thumbnail(Scene):
    def construct(self):
        lead = math(r"\sqrt{2}", "=", size=150)
        lead[0].set_color(PRIMARY)
        st = set_of_lists(size=58, rows=(list_tex(DEC_STR[:4]), list_tex([frac(p, q) for p, q in ORB[:4]])))
        top = VGroup(lead, st).arrange(RIGHT, buff=0.4)
        top.scale_to_fit_width(min(top.width, FW - 1.0)).move_to(UP * 0.7)
        tag = text("an infinite set of lists", size=76, weight="BOLD", color=SECONDARY)
        tag.next_to(top, DOWN, buff=0.6)
        self.add(top, tag)
