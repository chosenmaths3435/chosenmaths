from math import sqrt

import numpy as np
from manim import *
from manim_voiceover import VoiceoverScene

from mathvid import layout  # noqa: F401  must come before scene code runs
from mathvid.anim import rest, rt, wait_until
from mathvid.layout import FH, FW
from mathvid.script import Script
from mathvid.style import (BAD, BG, FG, GOOD, MUTED, PRIMARY, SECONDARY, TERTIARY, math, tex,
                           text, title_card)
from mathvid.voice import get_speech_service

N = Script(__file__)

TITLE = "Skolem's paradox"
ROUND_COLORS = [FG, PRIMARY, SECONDARY, TERTIARY, GOOD]

CANTOR_ROWS = ["1415926", "0500000", "7182818", "4142135", "3333333", "6180339"]
M_ROWS = ["2500000", "7071067", "3183098", "1235567", "5772156"]


def diagonal(rows):
    """Cantor's rule: each diagonal digit becomes 5, or 4 if it was already 5."""
    return "".join("4" if r[i] == "5" else "5" for i, r in enumerate(rows))


def frac_time(tr, f):
    return rt(tr.duration * f)


# ---------------------------------------------------------------------------
# Shared builders (also used by shorts.py)
# ---------------------------------------------------------------------------


class Blob(VGroup):
    """A universe drawn as a soft closed curve with dots inside."""

    def __init__(self, radius=3.0, center=ORIGIN, seed=0, n=40, squash=0.78, color=MUTED,
                 dot_color=FG, dot_r=0.06, stroke=4, gap=0.42, fill=0.0):
        super().__init__()
        rng = np.random.default_rng(seed)
        ph = rng.uniform(0, TAU, 3)
        c = np.array(center, dtype=float)
        rf = lambda th: radius * (1 + 0.07 * np.sin(3 * th + ph[0]) + 0.05 * np.cos(5 * th + ph[1])
                                  + 0.03 * np.sin(2 * th + ph[2]))
        self.pt = lambda th, rho: c + rho * rf(th) * np.array([np.cos(th), squash * np.sin(th), 0])
        self.border = ParametricFunction(lambda t: self.pt(t, 1.0), t_range=[0, TAU, TAU / 160],
                                         color=color, stroke_width=stroke)
        if fill:
            self.border.set_fill(color, opacity=fill)
        pts = []
        tries = 0
        while len(pts) < n and tries < 20000:
            tries += 1
            p = self.pt(rng.uniform(0, TAU), np.sqrt(rng.uniform(0.0, 0.74)))
            if all(np.linalg.norm(p - q) > gap for q in pts):
                pts.append(p)
        self.dots = VGroup(*[Dot(p, radius=dot_r, color=dot_color) for p in pts])
        self.add(self.border, self.dots)

    def nearest(self, point):
        """Index of the dot nearest a point."""
        point = np.array(point, dtype=float)
        return int(np.argmin([np.linalg.norm(d.get_center() - point) for d in self.dots]))


class RealLine(VGroup):
    """A plain number line. Do not move it after building it; place it with y and x0."""

    def __init__(self, lo=-3.5, hi=3.5, length=12.0, y=0.0, x0=0.0, ticks=True, size=26,
                 color=FG, stroke=4):
        super().__init__()
        self.lo, self.hi, self.length, self.y, self.x0 = lo, hi, length, y, x0
        self.line = Line(self.p(lo), self.p(hi), color=color, stroke_width=stroke)
        self.ticks, self.labels = VGroup(), VGroup()
        if ticks:
            for k in range(int(np.ceil(lo)), int(np.floor(hi)) + 1):
                self.ticks.add(Line(self.p(k) + UP * 0.1, self.p(k) + DOWN * 0.1, color=color,
                                    stroke_width=3))
                self.labels.add(math(str(k), size=size, color=MUTED).next_to(self.p(k), DOWN, 0.2))
        self.add(self.line, self.ticks, self.labels)

    def p(self, v):
        x = self.x0 + (v - (self.lo + self.hi) / 2) / (self.hi - self.lo) * self.length
        return np.array([x, self.y, 0.0])


def c_rounds():
    """The numbers added to C, round by round, starting from the seed 0 and 1."""
    rng = np.random.default_rng(3)
    first = [-1, sqrt(2), 1.5]
    pool = set()
    for q in range(1, 9):
        for p in range(-28, 29):
            v = p / q
            if -3.4 < v < 3.4:
                pool.add(round(v, 6))
    for k in (2, 3, 5, 6, 7, 10):
        for s in (1, -1):
            for v in (s * sqrt(k), s * sqrt(k) / 2, s * (sqrt(k) - 1), 1 + s * sqrt(k) / 3):
                if -3.4 < v < 3.4:
                    pool.add(round(v, 6))
    pool -= {0.0, 1.0, -1.0, round(sqrt(2), 6), 1.5}
    pool = sorted(pool)
    rng.shuffle(pool)
    sizes = [10, 18, 30, 46]
    out, i = [[0, 1], first], 0
    for s in sizes:
        out.append(pool[i:i + s])
        i += s
    return out


C_ROUNDS = c_rounds()
DOT_R = [0.08, 0.075, 0.062, 0.052, 0.044, 0.038]


def c_dust(rl, upto=len(C_ROUNDS), color_rounds=False, opacity=1.0):
    """Dots of C on a RealLine, one VGroup per round."""
    out = VGroup()
    for k, vals in enumerate(C_ROUNDS[:upto]):
        col = ROUND_COLORS[k % len(ROUND_COLORS)] if color_rounds else FG
        out.add(VGroup(*[Dot(rl.p(v), radius=DOT_R[k], color=col, fill_opacity=opacity)
                         for v in vals]))
    return out


def decimal_list(rows, size=40, top=2.5, x0=-2.6, dy=0.7, dx=0.3, numbered=True, vdots=True):
    """Numbered decimals, each digit its own mobject. rows_m[i][2 + k] is digit k."""
    g = VGroup()
    g.rows = []
    g.index = VGroup()
    for i, r in enumerate(rows):
        y = top - i * dy
        g.rows.append(decimal_row("0." + r, y, x0, dx, size))
        g.add(g.rows[-1])
        if numbered:
            g.index.add(text(str(i + 1), size=size - 6, color=MUTED).move_to([x0 - 1.0, y + 0.13, 0]))
    g.add(g.index)
    if vdots:
        g.vd = math(r"\vdots", size=size, color=MUTED).move_to([x0 + 4 * dx, top - len(rows) * dy + 0.15, 0])
        g.add(g.vd)
    g.geom = (x0, dx, size)
    g.strs = list(rows)
    return g


def decimal_row(s, y, x0, dx, size, color=FG):
    row = VGroup()
    for j, ch in enumerate(s):
        row.add(text(ch, size=size, color=color).move_to([x0 + j * dx, y, 0], aligned_edge=DOWN))
    row.add(text("...", size=size, color=MUTED).move_to([x0 + len(s) * dx + 0.3, y, 0], aligned_edge=DOWN))
    return row


def run_diagonal(scene, dl, d_y, t_light, t_change, label="d ="):
    """Light the diagonal of a decimal_list and build the new number below it. Returns d's row."""
    x0, dx, size = dl.geom
    rows = [r for r in dl.rows]
    n = len(rows)
    digs = [rows[i][2 + i] for i in range(n)]
    scene.play(LaggedStart(*[d.animate.set_color(PRIMARY) for d in digs], lag_ratio=0.3),
               run_time=t_light)
    new = diagonal(dl.strs)
    drow = decimal_row("0." + new, d_y, x0, dx, size, color=PRIMARY)
    lab = text(label, size=size, color=PRIMARY).next_to(drow[0], LEFT, 0.25)
    drow.add(lab)
    copies = [d.copy() for d in digs]
    scene.play(FadeIn(lab), FadeIn(drow[0]), FadeIn(drow[1]),
               *[ReplacementTransform(c, drow[2 + i]) for i, c in enumerate(copies)],
               FadeIn(drow[2 + n]), run_time=t_change)
    return drow


def tick(size=44):
    return math(r"\checkmark", size=size, color=GOOD)


def scroll(title, lines, size=26, width=5.2, title_size=34):
    body = VGroup(*[text(l, size=size) for l in lines]).arrange(DOWN, aligned_edge=LEFT, buff=0.22)
    head = text(title, size=title_size, weight="BOLD", color=PRIMARY)
    inner = VGroup(head, body).arrange(DOWN, buff=0.3)
    box = RoundedRectangle(corner_radius=0.2, width=max(width, inner.width + 0.6),
                           height=inner.height + 0.6, color=MUTED, stroke_width=3)
    box.move_to(inner)
    g = VGroup(box, head, body)
    g.box, g.head, g.body = box, head, body
    return g


def list_card(n=5, title="our list", size=36, name="r"):
    rows = VGroup(*[math(rf"{i}\quad {name}_{{{i}}}", size=size) for i in range(1, n + 1)])
    rows.add(math(r"\vdots", size=size, color=MUTED))
    rows.arrange(DOWN, buff=0.18)
    head = text(title, size=size - 2, color=SECONDARY, weight="BOLD")
    inner = VGroup(head, rows).arrange(DOWN, buff=0.25)
    box = RoundedRectangle(corner_radius=0.15, width=inner.width + 0.6, height=inner.height + 0.5,
                           color=SECONDARY, stroke_width=3).move_to(inner)
    g = VGroup(box, inner)
    g.box = box
    return g


def suppose_tag():
    w = text("suppose", size=30, color=PRIMARY, slant=ITALIC)
    u = Line(w.get_corner(DL) + DOWN * 0.08, w.get_corner(DR) + DOWN * 0.08, color=PRIMARY,
             stroke_width=3)
    return VGroup(w, u)


def corner(mob):
    return mob.to_corner(UL, buff=0.4)


def bubble(s, size=30, color=FG, check=True):
    t = text(s, size=size, color=color)
    parts = VGroup(t, tick(size + 6)).arrange(RIGHT, buff=0.25) if check else VGroup(t)
    box = RoundedRectangle(corner_radius=0.25, width=parts.width + 0.6, height=parts.height + 0.5,
                           color=color, stroke_width=3).move_to(parts)
    tail = Polygon(box.get_bottom() + LEFT * 0.35, box.get_bottom() + LEFT * 0.05,
                   box.get_bottom() + LEFT * 0.45 + DOWN * 0.35, color=color, stroke_width=3)
    tail.set_fill(BG, 1)
    return VGroup(box, tail, parts)


def crack(mob, color=BAD):
    a, b = mob.get_left() + LEFT * 0.15, mob.get_right() + RIGHT * 0.15
    pts = [a + (b - a) * t + UP * (0.09 if i % 2 else -0.09) * (1 if 0 < i < 8 else 0)
           for i, t in enumerate(np.linspace(0, 1, 9))]
    return VMobject(color=color, stroke_width=4).set_points_as_corners(pts)


def eye(scale=1.0):
    outer = VMobject(color=FG, stroke_width=4)
    outer.set_points_smoothly([LEFT * 0.7, UP * 0.32, RIGHT * 0.7, DOWN * 0.32, LEFT * 0.7])
    iris = Circle(radius=0.2, color=FG, stroke_width=3).set_fill(SECONDARY, 1)
    pupil = Dot(radius=0.08, color=BG)
    return VGroup(outer, iris, pupil).scale(scale)


def slot_row(n, y, x0, step, size=22, above=True):
    """Positions and number labels for a numbered row of slots."""
    pos = [np.array([x0 + i * step, y, 0.0]) for i in range(n)]
    labs = VGroup(*[text(str(i + 1), size=size, color=MUTED).move_to(p + (UP if above else DOWN) * 0.38)
                    for i, p in enumerate(pos)])
    return pos, labs


def list_up(dots, pos, offscreen_x, keep=None):
    """Animations that fly dots into numbered slots; extra dots fly off to the right."""
    anims = []
    order = list(range(len(dots)))
    if keep is not None:
        order.remove(keep)
        order.insert(min(6, len(order)), keep)
    for k, i in enumerate(order):
        target = pos[k] if k < len(pos) else np.array([offscreen_x + (k - len(pos)) * 0.8, pos[0][1], 0])
        anims.append(dots[i].animate.move_to(target))
    return anims


def m_universe(radius=2.2, center=ORIGIN, n=22, seed=11, squash=0.78):
    """The countable universe M, with its set of reals marked."""
    m = Blob(radius=radius, center=center, seed=seed, n=n, color=SECONDARY, dot_r=0.06, gap=0.4, squash=squash)
    i = m.nearest(np.array(center) + np.array([0.5 * radius, 0.15 * radius * squash, 0]))
    m.r_dot = m.dots[i]
    m.r_dot.set_color(PRIMARY).scale(1.5)
    m.r_lab = math(r"\mathbb{R}", size=34, color=PRIMARY).next_to(m.r_dot, UR, 0.05)
    m.label = math("M", size=48, color=SECONDARY).next_to(m.border, UP, 0.15)
    m.add(m.r_lab)
    return m


def rand_dust(n, x_lo, x_hi, y, seed=5, r=0.035, color=MUTED):
    rng = np.random.default_rng(seed)
    return VGroup(*[Dot([x, y, 0], radius=r, color=color) for x in rng.uniform(x_lo, x_hi, n)])


# ---------------------------------------------------------------------------
# s01 Hook
# ---------------------------------------------------------------------------


class S01Hook(VoiceoverScene):
    def construct(self):
        self.set_speech_service(get_speech_service())
        line = Line(LEFT * 6, RIGHT * 6, color=FG, stroke_width=5).shift(DOWN * 0.3)
        lab = math(r"\mathbb{R}", size=60).next_to(line.get_right(), UP, 0.25)
        big = text("uncountable", size=64, color=PRIMARY, weight="BOLD").move_to(UP * 1.6)

        u = Blob(radius=3.1, center=DOWN * 0.45, seed=1, n=42, gap=0.5)
        ri = u.nearest(DOWN * 0.1 + RIGHT * 1.0)
        rdot = u.dots[ri]
        rdot.set_color(PRIMARY).scale(1.6)
        rlab = math(r"\mathbb{R}", size=36, color=PRIMARY).next_to(rdot, UP, 0.12)
        rtag = text("uncountable", size=22, color=PRIMARY).next_to(rdot, DOWN, 0.14)
        others = VGroup(*[d for i, d in enumerate(u.dots) if i != ri])
        ulabel = text("a universe of sets", size=30, color=MUTED).next_to(u.border, UP, 0.2)

        with self.voiceover(text=N("s01.b1")) as tr:
            self.play(Create(line), FadeIn(lab), run_time=1.2)
            self.play(FadeIn(big, shift=DOWN * 0.2), run_time=0.8)
            wait_until(self, tr, "unless")
            self.play(ReplacementTransform(line, rdot), Transform(lab, rlab), Transform(big, rtag),
                      Create(u.border), LaggedStart(*[FadeIn(d, scale=0.5) for d in others], lag_ratio=0.03),
                      run_time=max(1.8, tr.get_remaining_duration()))

        with self.voiceover(text=N("s01.b2")) as tr:
            self.play(FadeIn(ulabel), run_time=0.8)
            self.wait(frac_time(tr, 0.08))
            every = text("every theorem of set theory is true here", size=30).next_to(u.border, DOWN, 0.2)
            self.play(FadeIn(every, shift=UP * 0.15), run_time=0.8)
            self.wait(frac_time(tr, 0.12))
            self.play(Indicate(big, color=PRIMARY, scale_factor=1.4), Indicate(rdot, scale_factor=1.6),
                      run_time=1.2)
            wait_until(self, tr, "list")
            pos, nums = slot_row(16, 0.0, -6.3, 0.84)
            rgroup = VGroup(lab, big)
            anims = list_up(u.dots, pos, 7.6, keep=ri)
            self.play(FadeOut(u.border), FadeOut(ulabel), FadeOut(every), *anims, FadeIn(nums),
                      rgroup.animate.move_to(pos[6] + DOWN * 0.55).scale(0.9),
                      run_time=max(1.6, tr.get_remaining_duration()))
            lab.next_to(rdot, DOWN, 0.15)
        self.wait(0.4)
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.6)
        title_card(self, TITLE)


# ---------------------------------------------------------------------------
# s02 Bigger infinities
# ---------------------------------------------------------------------------


class S02Bigger(VoiceoverScene):
    def construct(self):
        self.set_speech_service(get_speech_service())
        ys = [2.4 - 0.8 * i for i in range(6)]
        nums = VGroup(*[text(str(i + 1), size=34, color=MUTED).move_to([-5.2, y, 0]) for i, y in enumerate(ys)])
        slots = VGroup(*[Line([-4.7, y - 0.3, 0], [-3.3, y - 0.3, 0], color=MUTED, stroke_width=2) for y in ys])
        more = math(r"\vdots", size=36, color=MUTED).move_to([-4.0, ys[-1] - 0.8, 0])
        items = VGroup(Dot(radius=0.16, color=PRIMARY), Square(0.38, color=SECONDARY).set_fill(SECONDARY, 1),
                       Triangle(color=TERTIARY).set_fill(TERTIARY, 1).scale(0.26),
                       Star(outer_radius=0.28, color=GOOD).set_fill(GOOD, 1),
                       math(r"\pi", size=56, color=PRIMARY), math(r"\tfrac{1}{2}", size=50, color=SECONDARY))
        tag = text("countable: fits on one list", size=42).move_to(RIGHT * 1.6 + DOWN * 2.9)

        with self.voiceover(text=N("s02.b1")) as tr:
            self.play(FadeIn(nums), Create(slots), FadeIn(more), run_time=1.0)
            self.play(FadeIn(tag), run_time=0.6)
            t = max(0.3, (tr.duration - 2.6) / 6 - 0.05)
            for it, y in zip(items, ys):
                it.move_to([6.5, y, 0])
                self.play(it.animate.move_to([-4.0, y, 0]), run_time=t)
            rest(self, tr)
        self.play(FadeOut(VGroup(nums, slots, more, items, tag)), run_time=0.6)

        dl = decimal_list(CANTOR_ROWS, top=2.5, x0=-1.6, size=46, dy=0.78, dx=0.37)
        hdr = VGroup(text("a list of real numbers between", size=34, color=MUTED), math("0", size=40, color=MUTED),
                     text("and", size=34, color=MUTED), math("1", size=40, color=MUTED)).arrange(RIGHT, buff=0.18)
        hdr.move_to(UP * 3.4)
        with self.voiceover(text=N("s02.b2")) as tr:
            self.wait(frac_time(tr, 0.12))
            self.play(FadeIn(hdr), run_time=0.8)
            self.wait(frac_time(tr, 0.25))
            self.play(LaggedStart(*[FadeIn(r, shift=LEFT * 0.3) for r in dl.rows], lag_ratio=0.25),
                      FadeIn(dl.index), FadeIn(dl.vd), run_time=frac_time(tr, 0.45))
            rest(self, tr)

        with self.voiceover(text=N("s02.b3")) as tr:
            t1 = max(1.0, tr.time_until_bookmark("change") - 0.2)
            drow = run_diagonal(self, dl, -2.75, t1, 1.6)
            rest(self, tr)

        n = len(CANTOR_ROWS)
        nope = text("not on the list", size=38, color=BAD).next_to(drow, RIGHT, 0.6)
        xs = VGroup()
        with self.voiceover(text=N("s02.b4")) as tr:
            t = max(0.3, (tr.time_until_bookmark("miss") - 0.2) / n)
            for i in range(n):
                a, b = dl.rows[i][2 + i], drow[2 + i]
                x = math(r"\neq", size=40, color=BAD).next_to(dl.rows[i], RIGHT, 0.3)
                xs.add(x)
                self.play(a.animate.set_color(BAD), b.animate.set_color(BAD), FadeIn(x), run_time=t * 0.6)
                self.play(b.animate.set_color(PRIMARY), run_time=t * 0.4)
            wait_until(self, tr, "miss")
            self.play(FadeIn(nope, shift=LEFT * 0.2), run_time=0.7)
            rest(self, tr)
        self.play(FadeOut(VGroup(dl, drow, nope, xs, hdr)), run_time=0.6)

        w1 = text("uncountable", size=56, color=PRIMARY, weight="BOLD")
        eq = text("=", size=56)
        w2 = text("no list exists", size=56)
        line = VGroup(w1, eq, w2).arrange(RIGHT, buff=0.4)
        with self.voiceover(text=N("s02.b5")) as tr:
            self.play(FadeIn(w1), run_time=0.8)
            wait_until(self, tr, "nolist")
            self.play(FadeIn(eq), FadeIn(w2, shift=LEFT * 0.2), run_time=0.8)
            self.play(w2.animate.set_color(GOOD), Circumscribe(w2, color=GOOD), run_time=1.0)
            rest(self, tr)
        self.play(FadeOut(line), run_time=0.6)


# ---------------------------------------------------------------------------
# s03 A universe of sets
# ---------------------------------------------------------------------------


def zfc_scroll(size=26):
    return scroll("ZFC", ["two sets with the same members are equal", "there is an infinite set",
                          "every set has a set of all its subsets", "..."], size=size)


class S03Universe(VoiceoverScene):
    def construct(self):
        self.set_speech_service(get_speech_service())
        icons = VGroup(
            math("2", size=72),
            VGroup(Axes(x_range=[-1, 1], y_range=[0, 1], x_length=1.4, y_length=1.0,
                        tips=False, axis_config={"color": MUTED, "stroke_width": 2}),
                   ).add(FunctionGraph(lambda x: 0.45 * x * x + 0.1, x_range=[-1, 1], color=PRIMARY)
                         .scale(0.7)),
            Line(LEFT * 0.8, RIGHT * 0.8, color=SECONDARY, stroke_width=6),
            Triangle(color=TERTIARY, stroke_width=5).scale(0.6),
        ).arrange(RIGHT, buff=1.6).shift(UP * 0.4)
        icons[1][1].move_to(icons[1][0])
        braces = [r"\{\{\},\{\{\}\}\}", r"\{\{\{\}\},\{\}\}", r"\{\{\},\{\{\},\{\{\}\}\}\}",
                  r"\{\{\{\{\}\}\}\}"]
        bs = VGroup(*[math(b, size=44, color=c) for b, c in zip(braces, [FG, PRIMARY, SECONDARY, TERTIARY])])
        for b, ic in zip(bs, icons):
            b.move_to(ic)
        bs[2].scale(0.85)

        with self.voiceover(text=N("s03.b1")) as tr:
            self.play(LaggedStart(*[FadeIn(i, shift=UP * 0.2) for i in icons], lag_ratio=0.25), run_time=1.6)
            self.wait(frac_time(tr, 0.25))
            self.play(LaggedStart(*[FadeTransform(i, b) for i, b in zip(icons, bs)], lag_ratio=0.3),
                      run_time=frac_time(tr, 0.35))
            rest(self, tr)
        self.play(FadeOut(bs), run_time=0.5)

        z = zfc_scroll(size=32)
        extra = ["there is a set with no members", "any two sets have a pair set",
                 "every set has a union set"]
        with self.voiceover(text=N("s03.b2")) as tr:
            self.play(FadeIn(z), run_time=0.8)
            wait_until(self, tr, "zfc")
            self.play(Indicate(z.head, color=PRIMARY, scale_factor=1.4), run_time=0.8)
            t = max(0.3, (tr.get_remaining_duration() - 0.3) / len(extra))
            for e in extra:
                old = z.body[0]
                new = text(e, size=32).move_to(z.body[-2].get_left(), aligned_edge=LEFT)
                rest_rows = VGroup(*z.body[1:-1])
                step = z.body[1].get_center()[1] - z.body[2].get_center()[1]
                self.play(FadeOut(old, shift=UP * 0.4), rest_rows.animate.shift(UP * step),
                          FadeIn(new, shift=UP * 0.3), run_time=t)
                z.body.remove(old)
                z.body.submobjects.insert(len(z.body) - 1, new)
            rest(self, tr)

        u = Blob(radius=2.9, center=LEFT * 3.3 + UP * 0.1, seed=4, n=26, gap=0.55)
        rng = np.random.default_rng(2)
        arrows = VGroup()
        pairs = [(0, 1), (2, 3), (4, 1), (5, 6), (7, 3), (8, 9), (10, 6)]
        for a, b in pairs:
            pa, pb = u.dots[a].get_center(), u.dots[b].get_center()
            if np.linalg.norm(pa - pb) < 3.0:
                arrows.add(Arrow(pa, pb, buff=0.1, stroke_width=3, color=MUTED, tip_length=0.15,
                                 max_tip_length_to_length_ratio=0.25))
        a0 = arrows[0] if len(arrows) else None
        mem = VGroup(Arrow(LEFT * 0.5, RIGHT * 0.5, buff=0, stroke_width=3, color=MUTED, tip_length=0.15),
                     text("means \"is a member of\"", size=30, color=MUTED)).arrange(RIGHT, buff=0.25)
        mem.next_to(u.border, DOWN, 0.25)
        ticks = VGroup()
        with self.voiceover(text=N("s03.b3")) as tr:
            self.play(z.animate.scale(0.78).move_to(RIGHT * 3.6 + UP * 0.3), run_time=0.8)
            self.play(Create(u.border), LaggedStart(*[FadeIn(d) for d in u.dots], lag_ratio=0.03), run_time=1.2)
            self.play(LaggedStart(*[GrowArrow(a) for a in arrows], lag_ratio=0.15), FadeIn(mem), run_time=1.2)
            wait_until(self, tr, "obeys")
            for row in z.body[:-1]:
                ticks.add(tick(28).next_to(row, LEFT, 0.15))
            self.play(LaggedStart(*[FadeIn(t, scale=1.5) for t in ticks], lag_ratio=0.2), run_time=1.0)
            rest(self, tr)
        self.play(FadeOut(VGroup(z, ticks, arrows, mem)), FadeOut(u), run_time=0.6)

        syms = [(r"\in", "is a member of"), ("=", "equals"), (r"\land", "and"), (r"\lnot", "not"),
                (r"\forall", "for every"), (r"\exists", "there exists")]
        cols = VGroup(*[VGroup(math(s, size=60, color=PRIMARY), text(w, size=24, color=MUTED)).arrange(DOWN, buff=0.25)
                        for s, w in syms]).arrange(RIGHT, buff=0.7).shift(UP * 1.5)
        stmt = math(r"\exists x\, \forall y\, \lnot (y \in x)", size=60).shift(DOWN * 1.0)
        read = text("there is a set with no members", size=32, color=MUTED).next_to(stmt, DOWN, 0.4)
        with self.voiceover(text=N("s03.b4")) as tr:
            self.play(LaggedStart(*[FadeIn(c, shift=UP * 0.2) for c in cols], lag_ratio=0.25),
                      run_time=frac_time(tr, 0.55))
            self.play(Write(stmt), run_time=1.2)
            self.play(FadeIn(read), run_time=0.6)
            rest(self, tr)
        self.play(FadeOut(VGroup(cols, stmt, read)), run_time=0.6)

        u = Blob(radius=3.0, center=DOWN * 0.2, seed=6, n=30, gap=0.5)
        rng = np.random.default_rng(9)
        outside = VGroup()
        for _ in range(26):
            th = rng.uniform(0, TAU)
            p = u.pt(th, rng.uniform(1.18, 1.6))
            if abs(p[0]) < FW / 2 - 0.3 and abs(p[1]) < FH / 2 - 0.3:
                outside.add(Dot(p, radius=0.06, color=MUTED, fill_opacity=0.25))
        spot = Circle(radius=1.0, stroke_width=0).set_fill(PRIMARY, 0.18)
        spot.move_to(u.pt(2.6, 0.45))
        for d in u.dots:
            d.add_updater(lambda m, s=spot: m.set_color(PRIMARY if np.linalg.norm(m.get_center() - s.get_center()) < 1.0 else FG))
        path = ParametricFunction(lambda t: u.pt(2.6 + t, 0.45), t_range=[0, TAU * 0.9], color=BG)
        ulab = text("this universe", size=28, color=MUTED).next_to(u.border, UP, 0.12)
        with self.voiceover(text=N("s03.b5")) as tr:
            self.play(Create(u.border), FadeIn(u.dots), FadeIn(outside), FadeIn(ulab), run_time=1.0)
            wait_until(self, tr, "every")
            self.add(spot)
            self.play(FadeIn(spot), run_time=0.3)
            self.play(MoveAlongPath(spot, path), run_time=max(1.5, tr.get_remaining_duration() - 1.4))
            edge = u.pt(0.2, 0.86)
            self.play(spot.animate.move_to(edge), run_time=0.7)
            self.play(spot.animate.shift(LEFT * 0.12), u.border.animate.set_color(PRIMARY), run_time=0.4)
            rest(self, tr)
        for d in u.dots:
            d.clear_updaters()

        s1 = text('"the reals are uncountable"', size=40).move_to(UP * 0.2)
        s2 = text("no set in this universe is a list of the reals", size=40, color=PRIMARY).move_to(UP * 0.2)
        with self.voiceover(text=N("s03.b6")) as tr:
            self.play(FadeOut(VGroup(spot, outside, ulab)), FadeOut(u), run_time=0.6)
            self.play(FadeIn(s1), run_time=0.7)
            wait_until(self, tr, "nolist")
            self.play(FadeTransform(s1, s2), run_time=1.0)
            rest(self, tr)
        self.play(FadeOut(s2), run_time=0.6)


# ---------------------------------------------------------------------------
# s04 Shrinking the real line
# ---------------------------------------------------------------------------


def ops_tag():
    return math(r"+\qquad\times\qquad<", size=60, color=PRIMARY)


def stmt_box(tex_s, size=48):
    m = math(tex_s, size=size)
    box = SurroundingRectangle(m, buff=0.25, corner_radius=0.15, color=MUTED, stroke_width=3)
    return VGroup(box, m)


STREAM = [r"\exists y\,(y+1=0)", r"\exists y\,(y\cdot y=1+1)", r"\exists y\,(1<y<1+1)",
          r"\exists y\,(y\cdot (1+1)=1)", r"\exists y\,(y+y+y=1)", r"\exists y\,(y\cdot y\cdot y=1+1)",
          r"\exists y\,(\sqrt{2}<y<1+1)", r"\exists y\,(y+\sqrt{2}=0)", r"\exists y\,(y\cdot y=\tfrac{3}{2})"]


class S04Shrink(VoiceoverScene):
    def construct(self):
        self.set_speech_service(get_speech_service())
        rl = RealLine(-3.5, 3.5, 12, y=-0.6, size=32)
        ops = ops_tag().move_to(UP * 2.4)
        logic = math(r"=\qquad\land\qquad\lnot\qquad\forall\qquad\exists", size=52, color=MUTED).next_to(ops, DOWN, 0.4)
        rnd = text("round 1", size=32, color=MUTED).to_corner(UL, buff=0.5)
        with self.voiceover(text=N("s04.b1")) as tr:
            self.play(Create(rl.line), FadeIn(rl.ticks), FadeIn(rl.labels), run_time=1.2)
            self.wait(frac_time(tr, 0.1))
            self.play(FadeIn(ops, shift=DOWN * 0.2), run_time=0.8)
            self.wait(frac_time(tr, 0.2))
            self.play(FadeIn(logic, shift=DOWN * 0.2), run_time=0.8)
            self.wait(frac_time(tr, 0.1))
            self.play(FadeOut(logic), ops.animate.scale(0.75).to_corner(UR, buff=0.5), run_time=0.8)
            rest(self, tr)

        dust = c_dust(rl, color_rounds=True)
        seed = dust[0]
        with self.voiceover(text=N("s04.b2")) as tr:
            self.play(rl.line.animate.set_stroke(opacity=0.35), rl.ticks.animate.set_stroke(opacity=0.35),
                      rl.labels.animate.set_opacity(0.5), run_time=1.0)
            wait_until(self, tr, "seed")
            self.play(LaggedStart(*[FadeIn(d, scale=2) for d in seed], lag_ratio=0.4), run_time=0.8)
            rest(self, tr)

        box = stmt_box(r"\exists y\,\big(\;\cdots\;\big)").move_to(UP * 2.0)
        slot = Square(0.45, color=PRIMARY, stroke_width=3).next_to(box, RIGHT, 0.5)
        ylab = math("y=", size=40, color=PRIMARY).next_to(slot, LEFT, 0.1)
        slot_g = VGroup(ylab, slot).next_to(box, RIGHT, 0.4)
        pop = Dot(slot.get_center(), radius=0.1, color=PRIMARY)
        with self.voiceover(text=N("s04.b3")) as tr:
            self.play(FadeIn(rnd), FadeIn(box), run_time=0.8)
            self.play(FadeIn(slot_g), run_time=0.6)
            wait_until(self, tr, "add")
            self.play(FadeIn(pop, scale=3), run_time=0.6)
            rest(self, tr)

        r1 = dust[1]
        labs = [r"-1", r"\sqrt{2}", r"1.5"]
        stmts = STREAM[:3]
        marks = ["neg", "root", "pick"]
        lab_mobs = VGroup()
        with self.voiceover(text=N("s04.b4")) as tr:
            cur = box
            for k in range(3):
                nb = stmt_box(stmts[k]).move_to(UP * 2.0)
                self.play(FadeOut(VGroup(slot_g, pop)) if k == 0 else Wait(0.01),
                          ReplacementTransform(cur, nb), run_time=0.6)
                cur = nb
                if k == 2:
                    rng = np.random.default_rng(1)
                    cands = VGroup(*[Dot(rl.p(v), radius=0.07, color=MUTED) for v in rng.uniform(1.05, 1.95, 5)])
                    t = max(0.2, (tr.time_until_bookmark("pick") - 0.1) / 5)
                    for c in cands:
                        self.play(FadeIn(c, scale=2), run_time=t * 0.5)
                        self.play(FadeOut(c), run_time=t * 0.5)
                wait_until(self, tr, marks[k])
                d = r1[k]
                start = cur.get_bottom() + DOWN * 0.2
                tgt = d.get_center()
                d.move_to(start)
                lm = math(labs[k], size=30, color=PRIMARY).next_to(tgt, UP, 0.2)
                self.play(d.animate.move_to(tgt), FadeIn(lm), run_time=0.7)
                lab_mobs.add(lm)
            rest(self, tr)

        with self.voiceover(text=N("s04.b5")) as tr:
            self.play(FadeOut(cur), FadeOut(lab_mobs), Indicate(rnd, color=PRIMARY), run_time=0.8)
            wait_until(self, tr, "rounds")
            n_r = len(dust) - 2
            t = max(0.5, (tr.get_remaining_duration() - 0.2) / n_r)
            for k in range(2, len(dust)):
                nr = text(f"round {k}", size=30, color=MUTED).move_to(rnd)
                self.play(LaggedStart(*[FadeIn(d, scale=2.5) for d in dust[k]], lag_ratio=0.03),
                          Transform(rnd, nr), run_time=t)
            rest(self, tr)

        lines = VGroup(*[math(rf"{i + 1}.\quad " + s, size=40) for i, s in enumerate(STREAM)])
        lines.arrange(DOWN, aligned_edge=LEFT, buff=0.22)
        col_top = 3.4
        clabel = math("C", size=60, color=PRIMARY).next_to(rl.line.get_left(), UP, 0.35)
        all_dots = VGroup(*[d for g in dust for d in g])
        with self.voiceover(text=N("s04.b6")) as tr:
            vis = 4
            shown = VGroup()
            t = max(0.3, (tr.time_until_bookmark("count") - 0.3) / len(STREAM))
            for i, ln in enumerate(lines):
                ln.move_to([-2.2, col_top - 0.62 * min(i, vis - 1), 0], aligned_edge=LEFT)
                anims = [FadeIn(ln, shift=UP * 0.2)]
                if i >= vis:
                    anims += [FadeOut(shown[0], shift=UP * 0.3), shown[1:].animate.shift(UP * 0.62)]
                    shown.remove(shown[0])
                shown.add(ln)
                self.play(*anims, run_time=t)
            wait_until(self, tr, "count")
            pos, nums = slot_row(15, 2.3, -6.2, 0.85)
            copies = VGroup(*[d.copy().set_color(FG) for d in all_dots[:15]])
            self.play(FadeOut(shown), FadeOut(rnd), run_time=0.5)
            self.play(*[c.animate.move_to(p) for c, p in zip(copies, pos)], FadeIn(nums),
                      all_dots.animate.set_color(FG), run_time=1.2)
            dots3 = math(r"\cdots", size=40, color=MUTED).next_to(pos[-1], RIGHT, 0.3)
            self.play(FadeIn(dots3), Write(clabel), run_time=0.8)
            rest(self, tr)
        self.play(FadeOut(VGroup(copies, nums, dots3, ops)), run_time=0.6)


# ---------------------------------------------------------------------------
# s05 Why nothing changes
# ---------------------------------------------------------------------------


def c_scene_base():
    """The end state of s04: a faint line, C's dust, and the label C."""
    rl = RealLine(-3.5, 3.5, 12, y=-0.6, size=32)
    rl.line.set_stroke(opacity=0.35)
    rl.ticks.set_stroke(opacity=0.35)
    rl.labels.set_opacity(0.5)
    dust = c_dust(rl)
    clabel = math("C", size=60, color=PRIMARY).next_to(rl.line.get_left(), UP, 0.35)
    return rl, dust, clabel


def two_ticks(size=36):
    a = VGroup(text("true in", size=size), math(r"\mathbb{R}", size=size + 6), tick(size + 4)).arrange(RIGHT, buff=0.2)
    b = VGroup(text("true in", size=size), math("C", size=size + 6, color=PRIMARY), tick(size + 4)).arrange(RIGHT, buff=0.2)
    return VGroup(a, b).arrange(RIGHT, buff=0.9)


class S05Same(VoiceoverScene):
    def construct(self):
        self.set_speech_service(get_speech_service())
        rl, dust, clabel = c_scene_base()
        self.add(rl, dust, clabel)

        st = text("every positive number has a square root", size=38).move_to(UP * 2.7)
        tt = two_ticks().move_to(UP * 1.6)
        with self.voiceover(text=N("s05.b1")) as tr:
            self.play(FadeIn(st), run_time=0.8)
            self.wait(frac_time(tr, 0.3))
            self.play(FadeIn(tt[0]), run_time=0.6)
            self.play(FadeIn(tt[1]), run_time=0.6)
            rest(self, tr)
        self.play(FadeOut(VGroup(st, tt)), run_time=0.5)

        fact = math(r"1+1>1", size=52).move_to(UP * 2.7)
        tt = two_ticks().move_to(UP * 1.6)
        a, b = rl.p(0.5), rl.p(1.0)
        da = Dot(a, radius=0.1, color=SECONDARY)
        db = Dot(b, radius=0.1, color=SECONDARY)
        la = math("a", size=34, color=SECONDARY).next_to(da, DOWN, 0.45)
        lb = math("b", size=34, color=SECONDARY).next_to(db, DOWN, 0.45)
        dab = Dot(rl.p(1.5), radius=0.1, color=PRIMARY)
        lab = math("a+b", size=34, color=PRIMARY).next_to(dab, UP, 0.3)
        arc = CurvedArrow(a + UP * 0.15, rl.p(1.5) + UP * 0.15, angle=-PI / 2, color=PRIMARY, stroke_width=3,
                          tip_length=0.15)
        with self.voiceover(text=N("s05.b2")) as tr:
            self.play(FadeIn(fact), run_time=0.8)
            self.wait(frac_time(tr, 0.2))
            self.play(FadeIn(da), FadeIn(db), FadeIn(la), FadeIn(lb), run_time=0.7)
            self.play(Create(arc), FadeIn(dab, scale=2), FadeIn(lab), run_time=1.0)
            wait_until(self, tr, "simple")
            self.play(FadeIn(tt), run_time=0.8)
            rest(self, tr)
        self.play(FadeOut(VGroup(da, db, la, lb, dab, lab, arc)), run_time=0.4)

        comb = math(r"(1+1>1)", r"\;\land\;", r"\lnot", r"(1>1+1)", size=52).move_to(UP * 2.7)
        fa = math(r"\forall x", size=60).move_to(UP * 2.7)
        fb = math(r"\lnot\,\exists x\,\lnot", size=60).move_to(UP * 2.7)
        with self.voiceover(text=N("s05.b3")) as tr:
            self.play(TransformMatchingTex(fact, comb), run_time=1.0)
            self.play(Indicate(tt, color=GOOD, scale_factor=1.05), run_time=0.8)
            self.wait(frac_time(tr, 0.15))
            self.play(FadeOut(comb), FadeOut(tt), FadeIn(fa), run_time=0.7)
            self.play(TransformMatchingShapes(fa, fb), run_time=1.0)
            rest(self, tr)

        ex = stmt_box(r"\exists y\,\big(\;\cdots\;\big)").move_to(UP * 2.4)
        bad = Dot(rl.p(2.37), radius=0.11, color=BAD)
        badl = text("outside C", size=28, color=BAD).next_to(bad, UP, 0.35)
        good = Dot(rl.p(1.25), radius=0.11, color=PRIMARY)
        goodl = text("inside C", size=28, color=PRIMARY).next_to(good, UP, 0.35)
        short_a = math(r"\exists y\,", r"\big(\;\cdots y \cdots\;\big)", size=48).move_to(UP * 2.4)
        short_b = math(r"\big(\;\cdots b \cdots\;\big)", size=48).move_to(UP * 2.4)
        shorter = text("shorter", size=28, color=MUTED).next_to(short_b, RIGHT, 0.5)
        with self.voiceover(text=N("s05.b4")) as tr:
            self.play(FadeOut(fb), FadeIn(ex), run_time=0.7)
            wait_until(self, tr, "out")
            self.play(FadeIn(bad, scale=2), FadeIn(badl), run_time=0.6)
            self.play(Flash(bad, color=BAD), run_time=0.6)
            wait_until(self, tr, "inside")
            self.play(FadeOut(VGroup(bad, badl)), FadeIn(good, scale=2), FadeIn(goodl), run_time=0.7)
            self.wait(frac_time(tr, 0.05))
            self.play(FadeOut(ex), FadeIn(short_a), run_time=0.6)
            self.play(TransformMatchingTex(short_a, short_b), FadeIn(shorter), run_time=1.0)
            rest(self, tr)
        self.play(FadeOut(VGroup(good, goodl, short_b, shorter)), run_time=0.4)

        ls = text("L\u00f6wenheim-Skolem theorem", size=52, color=PRIMARY, weight="BOLD").move_to(UP * 3.1)
        big = Blob(radius=2.6, center=LEFT * 2.6 + DOWN * 0.5, seed=8, n=0, color=MUTED)
        small = Blob(radius=1.0, center=LEFT * 2.4 + DOWN * 0.6, seed=12, n=9, color=SECONDARY, gap=0.3)
        same = text("same statements true", size=36).move_to(RIGHT * 3.3 + DOWN * 0.2)
        arr = Arrow(same.get_left() + LEFT * 0.1, small.border.get_right() + RIGHT * 0.05, color=MUTED,
                    stroke_width=3)
        biglab = text("any structure", size=32, color=MUTED).next_to(big.border, UP, 0.1)
        smlab = text("countable part", size=30, color=SECONDARY).next_to(small.border, DOWN, 0.15)
        with self.voiceover(text=N("s05.b5")) as tr:
            self.play(FadeOut(VGroup(rl, dust, clabel)), FadeIn(ls), run_time=0.8)
            self.play(Create(big.border), FadeIn(biglab), run_time=0.9)
            self.play(Create(small.border), FadeIn(small.dots), FadeIn(smlab), run_time=0.9)
            wait_until(self, tr, "same")
            self.play(FadeIn(same), GrowArrow(arr), run_time=0.8)
            rest(self, tr)
        self.play(FadeOut(VGroup(ls, big, small, same, arr, biglab, smlab)), run_time=0.6)

        zl = RealLine(0, 1, 12, y=-0.4, ticks=True, size=30)
        vals = sorted({p / q for q in range(1, 23) for p in range(0, q + 1)})
        hole_v = 0.4142
        dz = VGroup(*[Dot(zl.p(v), radius=0.035 if v not in (0, 1) else 0.06, color=FG)
                      for v in vals if abs(v - hole_v) > 0.006])
        ring = Circle(radius=0.2, color=BAD, stroke_width=4).move_to(zl.p(hole_v))
        q = text("?", size=40, color=BAD).next_to(ring, UP, 0.15)
        zlab = math("C", size=50, color=PRIMARY).next_to(zl.line.get_left(), UP, 0.4)
        with self.voiceover(text=N("s05.b6")) as tr:
            self.play(FadeIn(zl), FadeIn(zlab), LaggedStart(*[FadeIn(d) for d in dz], lag_ratio=0.004),
                      run_time=1.6)
            wait_until(self, tr, "hole")
            self.play(Create(ring), FadeIn(q), run_time=0.7)
            self.wait(frac_time(tr, 0.15))
            self.play(FadeOut(q), run_time=frac_time(tr, 0.2))
            rest(self, tr)
        self.play(FadeOut(VGroup(zl, zlab, dz, ring)), run_time=0.6)


# ---------------------------------------------------------------------------
# s06 The paradox
# ---------------------------------------------------------------------------


class S06Paradox(VoiceoverScene):
    def construct(self):
        self.set_speech_service(get_speech_service())
        big = Blob(radius=3.4, center=LEFT * 2.2 + DOWN * 0.35, seed=21, n=70, dot_r=0.04,
                   dot_color=MUTED, gap=0.35)
        blab = text("big universe", size=30, color=MUTED).next_to(big.border, UP, 0.1)
        sup = suppose_tag().scale(1.5).move_to(RIGHT * 4.3 + UP * 1.5)
        sup_c = corner(suppose_tag())
        with self.voiceover(text=N("s06.b1")) as tr:
            self.play(Create(big.border), LaggedStart(*[FadeIn(d) for d in big.dots], lag_ratio=0.01),
                      FadeIn(blab), run_time=1.4)
            wait_until(self, tr, "suppose")
            self.play(FadeIn(sup, scale=1.2), run_time=0.7)
            self.wait(max(0.1, tr.get_remaining_duration() - 1.0))
            self.play(Transform(sup, sup_c), run_time=0.9)
            rest(self, tr)

        m = m_universe(radius=1.5, center=big.border.get_center() + RIGHT * 0.2, n=16, seed=13)
        stmts = [("a set with no members", r"\varnothing"), ("the set of natural numbers", r"\mathbb{N}"),
                 ("the set of real numbers", r"\mathbb{R}")]
        m_dots = list(m.dots)
        named = [m_dots[0], m_dots[1], m.r_dot]
        if m_dots[0] is m.r_dot or m_dots[1] is m.r_dot:
            named = [d for d in m_dots if d is not m.r_dot][:2] + [m.r_dot]
        rest_dots = [d for d in m_dots if all(d is not x for x in named)]
        tags = VGroup()
        with self.voiceover(text=N("s06.b2")) as tr:
            t = max(0.6, (tr.duration * 0.6) / 3)
            for (s, sym), d in zip(stmts, named):
                st = text(s, size=34).move_to(RIGHT * 4.0 + UP * 0.2)
                tgt = d.get_center()
                d.move_to(st.get_bottom() + DOWN * 0.3)
                tg = math(sym, size=30, color=d.get_color()).next_to(tgt, UL, 0.04)
                self.play(FadeIn(st), FadeIn(d), run_time=t * 0.35)
                self.play(d.animate.move_to(tgt), FadeIn(tg), FadeOut(st), run_time=t * 0.65)
                tags.add(tg)
            self.play(LaggedStart(*[FadeIn(d, scale=2) for d in rest_dots], lag_ratio=0.06),
                      run_time=frac_time(tr, 0.2))
            self.play(Create(m.border), FadeIn(m.label), run_time=1.0)
            rest(self, tr)
        self.remove(*named)
        m.remove(m.r_lab)
        self.add(m.dots)
        r_tag = tags[2]

        mgroup = VGroup(m.border, m.dots, tags, m.label)
        claim = text("the reals are uncountable", size=36).move_to(RIGHT * 3.4 + UP * 0.6)
        tm = VGroup(text("true in", size=32), math("M", size=38, color=SECONDARY), tick(36)).arrange(RIGHT, buff=0.2)
        tm.next_to(claim, DOWN, 0.4)
        with self.voiceover(text=N("s06.b3")) as tr:
            self.play(FadeOut(big), FadeOut(blab), mgroup.animate.scale(1.45).move_to(LEFT * 3.0 + DOWN * 0.2),
                      run_time=1.2)
            self.play(FadeIn(claim), run_time=0.8)
            wait_until(self, tr, "cantor")
            self.play(FadeIn(tm), run_time=0.7)
            rest(self, tr)

        pos, nums = slot_row(len(m.dots), -3.0, -6.3, 0.8)
        pos = pos[:16]
        copies = VGroup(*[d.copy() for d in m.dots])
        rcirc = Circle(radius=1.5, color=PRIMARY, stroke_width=3).move_to(RIGHT * 3.4 + DOWN * 0.3)
        rl2 = math(r"\mathbb{R}", size=40, color=PRIMARY).next_to(rcirc, UP, 0.1)
        rng = np.random.default_rng(4)
        inner = VGroup()
        while len(inner) < 9:
            p = rcirc.get_center() + np.array([rng.uniform(-1.1, 1.1), rng.uniform(-1.1, 1.1), 0])
            if np.linalg.norm(p - rcirc.get_center()) < 1.15 and all(np.linalg.norm(p - d.get_center()) > 0.45 for d in inner):
                inner.add(Dot(p, radius=0.06, color=FG))
        inner_n = VGroup(*[text(str(i + 1), size=20, color=MUTED).next_to(d, UR, 0.02) for i, d in enumerate(inner)])
        with self.voiceover(text=N("s06.b4")) as tr:
            self.play(FadeOut(VGroup(claim, tm)), run_time=0.5)
            self.play(*[c.animate.move_to(p) for c, p in zip(copies, pos)], FadeIn(nums[:len(pos)]),
                      run_time=1.4)
            self.play(TransformFromCopy(m.r_dot, rcirc), FadeIn(rl2), run_time=0.9)
            wait_until(self, tr, "few")
            self.play(LaggedStart(*[FadeIn(d, scale=2) for d in inner], lag_ratio=0.1),
                      LaggedStart(*[FadeIn(x) for x in inner_n], lag_ratio=0.1), run_time=1.2)
            rest(self, tr)

        left = VGroup(text("inside M", size=36, color=SECONDARY),
                      text("no list of the reals", size=42)).arrange(DOWN, buff=0.3).move_to(LEFT * 3.4 + UP * 0.4)
        card = list_card(5, title="out with us: M's reals").move_to(RIGHT * 3.4 + UP * 0.3)
        card.scale_to_fit_height(min(card.height, 5.2))
        divider = DashedLine(UP * 3, DOWN * 2.2, color=MUTED)
        who = text("Thoralf Skolem, 1922", size=36, color=MUTED).move_to(DOWN * 3.2)
        with self.voiceover(text=N("s06.b5")) as tr:
            self.play(FadeOut(VGroup(copies, nums, rcirc, rl2, inner, inner_n, mgroup)), run_time=0.6)
            self.play(FadeIn(left), Create(divider), run_time=0.8)
            self.play(FadeIn(card), run_time=0.8)
            self.wait(frac_time(tr, 0.2))
            self.play(FadeIn(who), run_time=0.8)
            rest(self, tr)
        self.play(FadeOut(VGroup(left, card, divider, who)), run_time=0.6)


# ---------------------------------------------------------------------------
# s07 The list isn't in M
# ---------------------------------------------------------------------------


class S07NotInM(VoiceoverScene):
    def construct(self):
        self.set_speech_service(get_speech_service())
        sup = corner(suppose_tag())
        self.add(sup)
        m = Blob(radius=2.8, center=LEFT * 2.6 + DOWN * 0.3, seed=13, n=0, color=SECONDARY)
        mlab = math("M", size=48, color=SECONDARY).next_to(m.border, UP, 0.1)
        inside = VGroup(text("no set in M is a list", size=36), text("of M's reals", size=36)).arrange(DOWN, buff=0.15)
        inside.move_to(m.border.get_center())
        with self.voiceover(text=N("s07.b1")) as tr:
            self.play(Create(m.border), FadeIn(mlab), run_time=1.0)
            wait_until(self, tr, "inm")
            self.play(FadeIn(inside), run_time=0.8)
            rest(self, tr)

        card = list_card(4, title="our list").move_to(RIGHT * 4.6 + DOWN * 0.2)
        us = text("out here with us", size=26, color=MUTED).next_to(card, UP, 0.25)
        with self.voiceover(text=N("s07.b2")) as tr:
            self.play(FadeIn(card), FadeIn(us), run_time=0.8)
            wait_until(self, tr, "notin")
            home = card.get_center()
            hit = m.border.get_right()[0] + card.width / 2 + 0.05
            self.play(card.animate.move_to([hit, home[1], 0]), run_time=0.6, rate_func=rush_into)
            self.play(card.animate.move_to(home), m.border.animate.set_color(BAD), run_time=0.6, rate_func=rush_from)
            self.play(m.border.animate.set_color(SECONDARY), run_time=0.4)
            rest(self, tr)

        b_in = bubble("no list exists", size=34).move_to(m.border.get_center() + UP * 0.2)
        b_out = bubble("here's a list", size=34, color=SECONDARY).next_to(card, UP, 0.3)
        if b_out.get_right()[0] > FW / 2 - 0.3:
            b_out.shift(LEFT * (b_out.get_right()[0] - FW / 2 + 0.3))
        word = text("uncountable", size=40, color=PRIMARY, weight="BOLD").move_to(DOWN * 3.15)
        w1 = text("no list in M", size=34, color=SECONDARY).move_to(DOWN * 3.15 + LEFT * 3.0)
        w2 = text("no list at all", size=34, color=PRIMARY).move_to(DOWN * 3.15 + RIGHT * 3.0)
        with self.voiceover(text=N("s07.b3")) as tr:
            self.play(FadeOut(inside), FadeOut(us), FadeIn(b_in), run_time=0.8)
            self.wait(frac_time(tr, 0.15))
            self.play(FadeIn(b_out), run_time=0.8)
            self.play(FadeIn(word), run_time=0.6)
            wait_until(self, tr, "two")
            self.play(ReplacementTransform(word.copy(), w1), ReplacementTransform(word, w2), run_time=1.0)
            rest(self, tr)
        self.play(FadeOut(VGroup(m.border, mlab, b_in, b_out, card, w1, w2)), run_time=0.6)

        dl = decimal_list(M_ROWS, top=2.6, x0=-1.2, size=38)
        dlab = text("M's reals, our list", size=34, color=SECONDARY).next_to(dl, LEFT, 0.9).shift(UP * 0.5)
        rl = RealLine(0, 1, 11, y=-2.9, ticks=True, size=26)
        mdust = VGroup(*[Dot(rl.p(v), radius=0.03, color=MUTED)
                         for v in sorted({p / q for q in range(1, 15) for p in range(1, q)})])
        with self.voiceover(text=N("s07.b4")) as tr:
            self.play(FadeIn(dl), FadeIn(dlab), run_time=0.9)
            t1 = max(0.8, tr.time_until_bookmark("new") - 0.2)
            drow = run_diagonal(self, dl, -1.4, t1, 1.2)
            dval = float("0." + diagonal(M_ROWS))
            dd = Dot(rl.p(dval), radius=0.1, color=PRIMARY)
            ddl = VGroup(math("d", size=32, color=PRIMARY), text("not in M", size=26, color=PRIMARY)).arrange(RIGHT, buff=0.2)
            ddl.next_to(dd, DOWN, 0.5)
            self.play(FadeIn(rl), FadeIn(mdust), run_time=0.8)
            self.play(TransformFromCopy(drow[2], dd), FadeIn(ddl), run_time=1.0)
            rest(self, tr)

        full = RealLine(-3.5, 3.5, 12, y=-0.4)
        fdust = VGroup(*[Dot(full.p(v), radius=0.04, color=SECONDARY)
                         for v in sorted({p / q for q in range(1, 7) for p in range(-24, 25)}) if -3.5 < v < 3.5])
        flab = text("M's reals", size=30, color=SECONDARY).next_to(full.line.get_left(), UP, 0.4)
        with self.voiceover(text=N("s07.b5")) as tr:
            self.play(FadeOut(VGroup(dl, dlab, drow, rl, mdust, dd, ddl)), run_time=0.6)
            self.play(FadeIn(full), FadeIn(fdust), FadeIn(flab), run_time=0.9)
            self.play(fdust.animate.set_opacity(0.12).scale(0.4), full.line.animate.set_stroke(width=6),
                      run_time=max(1.0, tr.get_remaining_duration() - 0.2))
            rest(self, tr)
        self.play(FadeOut(VGroup(full, fdust, flab)), run_time=0.5)

        subs = [r"\varnothing", r"\{0\}", r"\{1,2\}", r"\{0,2,4,\ldots\}", r"\{2,3,5,7,\ldots\}",
                r"\{1,4,9,\ldots\}"]
        box_t = text('M\'s "all subsets of the natural numbers"', size=36)
        sg = VGroup(*[math(s, size=42) for s in subs]).arrange_in_grid(rows=2, buff=(0.7, 0.45))
        inner = VGroup(box_t, sg).arrange(DOWN, buff=0.4)
        bx = RoundedRectangle(corner_radius=0.25, width=inner.width + 0.8, height=inner.height + 0.7,
                              color=SECONDARY, stroke_width=3).move_to(inner)
        grp = VGroup(bx, inner).move_to(UP * 0.2)
        rng = np.random.default_rng(17)
        faint = VGroup()
        samples = [r"\{3\}", r"\{0,5\}", r"\{1,3,5,\ldots\}", r"\{7,8\}", r"\{0,1\}", r"\{4,6,\ldots\}",
                   r"\{2\}", r"\{5,10,\ldots\}", r"\{9\}", r"\{1,2,3\}", r"\{6\}", r"\{0,3,6,\ldots\}"]
        while len(faint) < 16:
            p = np.array([rng.uniform(-6.6, 6.6), rng.uniform(-3.6, 3.4), 0])
            if abs(p[0]) < bx.width / 2 + 0.6 and abs(p[1] - 0.2) < bx.height / 2 + 0.4:
                continue
            if abs(p[0]) > 5.2 and p[1] > 2.8:
                continue
            cand = math(samples[len(faint) % len(samples)], size=32, color=MUTED).set_opacity(0.4).move_to(p)
            if any(np.linalg.norm(cand.get_center() - f.get_center()) < 1.3 for f in faint):
                continue
            faint.add(cand)
        with self.voiceover(text=N("s07.b6")) as tr:
            self.play(FadeIn(bx), FadeIn(box_t), run_time=0.8)
            self.wait(frac_time(tr, 0.35))
            self.play(LaggedStart(*[FadeIn(s) for s in sg], lag_ratio=0.15), run_time=1.2)
            self.play(LaggedStart(*[FadeIn(f) for f in faint], lag_ratio=0.04), run_time=1.4)
            rest(self, tr)
        self.play(FadeOut(VGroup(grp, faint)), run_time=0.6)


# ---------------------------------------------------------------------------
# s08 What can't we see from inside?
# ---------------------------------------------------------------------------


class S08Inside(VoiceoverScene):
    def construct(self):
        self.set_speech_service(get_speech_service())
        sup = corner(suppose_tag())
        self.add(sup)
        c17 = Circle(radius=1.4, color=SECONDARY, stroke_width=3).move_to(LEFT * 3.2 + UP * 0.2)
        d17 = VGroup(*[Dot(c17.get_center() + 1.0 * np.array([np.cos(a), np.sin(a), 0]), radius=0.07)
                       for a in np.linspace(0, TAU, 17, endpoint=False)])
        l17 = VGroup(text("exactly 17 members", size=36), tick(40)).arrange(RIGHT, buff=0.2).next_to(c17, DOWN, 0.4)
        c0 = Circle(radius=1.4, color=SECONDARY, stroke_width=3).move_to(RIGHT * 3.2 + UP * 0.2)
        l0 = VGroup(text("empty", size=36), tick(40)).arrange(RIGHT, buff=0.2).next_to(c0, DOWN, 0.4)
        with self.voiceover(text=N("s08.b1")) as tr:
            self.play(Create(c17), run_time=0.6)
            wait_until(self, tr, "seventeen")
            self.play(LaggedStart(*[FadeIn(d, scale=2) for d in d17], lag_ratio=0.05), run_time=1.0)
            self.play(FadeIn(l17), run_time=0.5)
            wait_until(self, tr, "empty")
            self.play(Create(c0), FadeIn(l0), run_time=0.8)
            rest(self, tr)

        good = VGroup(text("exactly 17 members", size=40), tick(44)).arrange(RIGHT, buff=0.2).move_to(LEFT * 3.3 + UP * 2.2)
        unc = text("uncountable", size=40, color=PRIMARY, weight="BOLD").move_to(RIGHT * 3.3 + UP * 2.2)
        cr = crack(unc)
        rules = ["ZFC", "ZFC + more rules", "any rules in this language"]
        cards = VGroup()
        for i, r in enumerate(rules):
            hd = text(r, size=30, color=PRIMARY, weight="BOLD")
            bl = Blob(radius=0.75, center=ORIGIN, seed=30 + i, n=7, color=SECONDARY, dot_r=0.05, gap=0.25)
            cnt = text("countable universe", size=26, color=SECONDARY)
            inner = VGroup(hd, bl, cnt).arrange(DOWN, buff=0.2)
            bx = RoundedRectangle(corner_radius=0.2, width=max(3.4, inner.width + 0.4), height=inner.height + 0.5,
                                  color=MUTED, stroke_width=3)
            bx.move_to(inner)
            cards.add(VGroup(bx, inner))
        cards.arrange(RIGHT, buff=0.4).move_to(DOWN * 1.2)
        cards.scale_to_fit_width(min(cards.width, FW - 0.8))
        with self.voiceover(text=N("s08.b2")) as tr:
            self.play(FadeOut(VGroup(c17, d17, l17, c0, l0)), FadeIn(good), FadeIn(unc), run_time=0.9)
            wait_until(self, tr, "breaks")
            self.play(Create(cr), unc.animate.set_color(BAD), run_time=0.8)
            self.wait(frac_time(tr, 0.3))
            self.play(LaggedStart(*[FadeIn(c, shift=UP * 0.2) for c in cards], lag_ratio=0.4),
                      run_time=max(1.2, tr.get_remaining_duration() - 0.3))
            rest(self, tr)
        self.play(FadeOut(VGroup(good, unc, cr, cards)), run_time=0.6)

        quote = text('"relativity of set-theoretic notions"', size=46, slant=ITALIC).move_to(UP * 0.4)
        who = text("Thoralf Skolem, 1922", size=30, color=MUTED).next_to(quote, DOWN, 0.5)
        with self.voiceover(text=N("s08.b3")) as tr:
            self.play(FadeIn(who), run_time=0.6)
            wait_until(self, tr, "relative")
            self.play(FadeIn(quote), run_time=0.9)
            rest(self, tr)
        self.play(FadeOut(VGroup(quote, who)), run_time=0.6)

        base = Line(LEFT * 6.5, RIGHT * 6.5, color=MUTED, stroke_width=3).shift(DOWN * 0.2)
        nat = VGroup(*[Dot([-6.0 + i * 0.9, -0.2, 0], radius=0.08) for i in range(9)])
        natl = VGroup(*[math(str(i), size=30, color=MUTED).next_to(d, DOWN, 0.25) for i, d in enumerate(nat)])
        dots3 = math(r"\cdots", size=40, color=MUTED).move_to([2.6, -0.2, 0])
        extra = VGroup(*[Dot([3.7 + i * 0.7, -0.2, 0], radius=0.08, color=TERTIARY) for i in range(4)])
        extral = VGroup(*[text("?", size=30, color=TERTIARY).next_to(d, DOWN, 0.25) for d in extra])
        br = Brace(extra, UP, color=TERTIARY)
        brl = VGroup(text("bigger than every ordinary", size=30, color=TERTIARY),
                     text("natural number", size=30, color=TERTIARY)).arrange(DOWN, buff=0.1).next_to(br, UP, 0.15)
        brl.shift(LEFT * max(0, brl.get_right()[0] - (FW / 2 - 0.3)))
        with self.voiceover(text=N("s08.b4")) as tr:
            self.play(Create(base), LaggedStart(*[FadeIn(d) for d in nat], lag_ratio=0.1), FadeIn(natl),
                      FadeIn(dots3), run_time=1.4)
            wait_until(self, tr, "extra")
            self.play(LaggedStart(*[FadeIn(d, scale=2) for d in extra], lag_ratio=0.2), FadeIn(extral), run_time=1.0)
            self.play(GrowFromCenter(br), FadeIn(brl), run_time=0.8)
            rest(self, tr)
        self.play(FadeOut(VGroup(base, nat, natl, dots3, extra, extral, br, brl)), run_time=0.6)

        unis = VGroup(*[Blob(radius=1.15, center=ORIGIN, seed=40 + i, n=8, color=SECONDARY, dot_r=0.05, gap=0.3)
                        for i in range(4)]).arrange(RIGHT, buff=0.5).shift(UP * 0.6)
        with self.voiceover(text=N("s08.b5")) as tr:
            self.play(LaggedStart(*[Create(u.border) for u in unis], lag_ratio=0.2),
                      LaggedStart(*[FadeIn(u.dots) for u in unis], lag_ratio=0.2), run_time=1.4)
            target = unis[1]
            others = VGroup(unis[0], unis[2], unis[3])
            outer = Blob(radius=4.0, center=DOWN * 0.1, seed=50, n=0, color=MUTED)
            olab = text("another universe", size=30, color=MUTED).next_to(outer.border, UP, 0.05)
            self.wait(frac_time(tr, 0.2))
            self.play(FadeOut(others), target.animate.move_to(UP * 0.8).scale(1.1), run_time=0.8)
            self.play(Create(outer.border), FadeIn(olab), run_time=0.9)
            wait_until(self, tr, "listed")
            pos, nums = slot_row(8, -1.5, -2.8, 0.8, size=24, above=False)
            self.play(*[d.animate.move_to(p) for d, p in zip(target.dots, pos)], FadeIn(nums), run_time=1.0)
            rest(self, tr)
        self.play(FadeOut(VGroup(target, outer, olab, nums)), run_time=0.6)

        ours = Blob(radius=2.2, center=DOWN * 0.3 + LEFT * 0.8, seed=60, n=18, color=SECONDARY, gap=0.4)
        olab = text("our universe", size=28, color=SECONDARY).next_to(ours.border, UP, 0.1)
        ghost = DashedVMobject(Blob(radius=3.5, center=DOWN * 0.3 + LEFT * 0.4, seed=61, n=0, color=MUTED).border,
                               num_dashes=60).set_stroke(opacity=0.5)
        e = eye(0.9).move_to(RIGHT * 5.0 + UP * 1.0)
        qm = text("?", size=72, color=PRIMARY).move_to(e)
        with self.voiceover(text=N("s08.b6")) as tr:
            self.play(Create(ours.border), FadeIn(ours.dots), FadeIn(olab), run_time=1.0)
            self.play(Create(ghost), FadeIn(e), run_time=1.0)
            wait_until(self, tr, "tell")
            self.play(FadeOut(e), FadeIn(qm), run_time=0.8)
            rest(self, tr)
        self.play(FadeOut(VGroup(ours, olab, ghost, qm)), run_time=0.6)


# ---------------------------------------------------------------------------
# s09 Ending
# ---------------------------------------------------------------------------


class S09Ending(VoiceoverScene):
    def construct(self):
        self.set_speech_service(get_speech_service())
        sup = corner(suppose_tag())
        self.add(sup)
        a = text("some universe obeys ZFC", size=40).move_to(UP * 0.5)
        iff = math(r"\Updownarrow", size=50, color=MUTED).next_to(a, DOWN, 0.3)
        b = text("ZFC never leads to a contradiction", size=40).next_to(iff, DOWN, 0.3)
        who = text("G\u00f6del's completeness theorem", size=34, color=MUTED).next_to(b, DOWN, 0.6)
        with self.voiceover(text=N("s09.b1")) as tr:
            wait_until(self, tr, "suppose")
            self.play(sup.animate.scale(1.6).move_to(UP * 2.3), run_time=1.0)
            self.play(FadeIn(a), run_time=0.7)
            self.wait(frac_time(tr, 0.15))
            self.play(FadeIn(iff), FadeIn(b), run_time=0.8)
            self.play(FadeIn(who), run_time=0.6)
            rest(self, tr)
        self.play(FadeOut(VGroup(sup, a, iff, b, who)), run_time=0.6)

        head = text("G\u00f6del's second incompleteness theorem, 1931", size=40, color=PRIMARY,
                    weight="BOLD").move_to(UP * 3.1)
        body = VGroup(text("if ZFC never contradicts itself,", size=40),
                      text("it can't prove that", size=40)).arrange(DOWN, buff=0.2).move_to(UP * 0.6)
        names = ["ZFC", "stronger rules", "even stronger rules"]
        stack = VGroup(*[scroll(n, [], title_size=34, width=4.4) for n in names])
        for s in stack:
            s.box.stretch_to_fit_height(0.85).move_to(s.head)
        stack.arrange(UP, buff=0.75).move_to(DOWN * 0.7 + LEFT * 0.8)
        arrows = VGroup(*[Arrow(stack[i + 1].get_bottom(), stack[i].get_top(), buff=0.05, color=MUTED, stroke_width=3)
                          for i in range(len(stack) - 1)])
        alabs = VGroup(*[text("proves it is safe", size=26, color=MUTED).next_to(a, RIGHT, 0.15) for a in arrows])
        top_q = text("?", size=56, color=PRIMARY).next_to(stack[-1], UP, 0.15)
        with self.voiceover(text=N("s09.b2")) as tr:
            self.play(FadeIn(head), run_time=0.8)
            self.play(FadeIn(body), run_time=0.8)
            self.wait(frac_time(tr, 0.15))
            self.play(FadeOut(body), FadeIn(stack[0]), run_time=0.6)
            self.play(FadeIn(stack[1]), GrowArrow(arrows[0]), FadeIn(alabs[0]), run_time=0.8)
            wait_until(self, tr, "stack")
            self.play(FadeIn(stack[2]), GrowArrow(arrows[1]), FadeIn(alabs[1]), run_time=0.8)
            self.play(FadeIn(top_q, shift=DOWN * 0.2), run_time=0.6)
            rest(self, tr)
        self.play(FadeOut(VGroup(head, stack, arrows, alabs, top_q)), run_time=0.6)

        bigu = Blob(radius=2.6, center=LEFT * 3.4 + DOWN * 0.2, seed=21, n=30, dot_r=0.035, dot_color=MUTED, gap=0.3)
        m = Blob(radius=1.0, center=LEFT * 3.2 + DOWN * 0.3, seed=13, n=6, color=SECONDARY, gap=0.3, dot_r=0.05)
        for d in list(bigu.dots):
            if np.linalg.norm(d.get_center() - m.border.get_center()) < 1.15:
                bigu.dots.remove(d)
        ours = Blob(radius=1.5, center=RIGHT * 3.4 + DOWN * 0.3, seed=60, n=10, color=SECONDARY, gap=0.3, dot_r=0.05)
        ghost = DashedVMobject(Blob(radius=2.6, center=RIGHT * 3.5 + DOWN * 0.2, seed=61, n=0, color=MUTED).border,
                               num_dashes=50).set_stroke(opacity=0.5)
        l1 = math("M", size=40, color=SECONDARY).next_to(m.border, UP, 0.05)
        l2 = text("our universe", size=26, color=SECONDARY).next_to(ours.border, UP, 0.1)
        with self.voiceover(text=N("s09.b3")) as tr:
            self.play(FadeIn(bigu), FadeIn(m), FadeIn(l1), run_time=1.0)
            self.wait(frac_time(tr, 0.2))
            self.play(FadeIn(ours), FadeIn(l2), Create(ghost), run_time=1.0)
            wait_until(self, tr, "outside")
            self.play(m.border.animate.set_stroke(PRIMARY, width=7), ours.border.animate.set_stroke(PRIMARY, width=7),
                      run_time=0.8)
            rest(self, tr)
        self.play(FadeOut(Group(*self.mobjects)), run_time=1.5)
        self.wait(0.5)


# ---------------------------------------------------------------------------
# Thumbnail
# ---------------------------------------------------------------------------


class Thumbnail(Scene):
    def construct(self):
        m = m_universe(radius=2.9, center=LEFT * 3.2 + DOWN * 0.6, n=26, seed=13)
        m.r_dot.scale(1.4)
        m.r_lab.scale(1.5).next_to(m.r_dot, UR, 0.05)
        t1 = text("Uncountable", size=92, weight="BOLD", color=PRIMARY)
        t2 = text("inside.", size=92, weight="BOLD", color=PRIMARY)
        t3 = text("Countable", size=92, weight="BOLD", color=SECONDARY)
        t4 = text("outside.", size=92, weight="BOLD", color=SECONDARY)
        words = VGroup(VGroup(t1, t2).arrange(DOWN, buff=0.15, aligned_edge=LEFT),
                       VGroup(t3, t4).arrange(DOWN, buff=0.15, aligned_edge=LEFT)).arrange(DOWN, buff=0.6, aligned_edge=LEFT)
        words.scale_to_fit_width(6.4).move_to(RIGHT * 3.55)
        mlab = math("M", size=110, color=SECONDARY).next_to(m.border, UP, 0.0).shift(LEFT * 1.6)
        self.add(m, words, mlab)
