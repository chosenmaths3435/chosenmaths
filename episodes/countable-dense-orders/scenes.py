from fractions import Fraction as Fr
from itertools import count
from math import gcd

from manim import *
from manim_voiceover import VoiceoverScene

from mathvid import layout  # noqa: F401  must come before scene code runs
from mathvid.anim import rest, rt, strike, wait_until
from mathvid.layout import FW
from mathvid.script import Script
from mathvid.style import BAD, BG, FG, GOOD, MUTED, PRIMARY, SECONDARY, TERTIARY, math, text
from mathvid.voice import get_speech_service

N = Script(__file__)

TITLE = ("What makes the rational numbers", "so special?")
PIECES = [(0, 1), (2, 3)]
FACTS = ["a line, with no ends", "dense", "countable"]


# ---------------------------------------------------------------------------
# The math behind the pictures
# ---------------------------------------------------------------------------


def head(i):
    """Table headers: 1, -1, 2, -2, ..."""
    return (i // 2 + 1) * (1 if i % 2 == 0 else -1)


def top_list(n):
    """The rationals in diagonal order, with zero first."""
    seen, out = {Fr(0)}, [Fr(0)]
    for d in count():
        for r in range(d + 1):
            v = Fr(head(r), head(d - r))
            if v not in seen:
                seen.add(v)
                out.append(v)
                if len(out) == n:
                    return out


def bot_list(n):
    """The rationals strictly inside the two pieces, switching piece each time."""
    out = []
    for q in count(2):
        for p in range(1, q):
            if gcd(p, q) == 1:
                out += [Fr(p, q), Fr(p, q) + 2]
                if len(out) >= n:
                    return out[:n]


def simulate(turns, tn=1500, bn=1500):
    """Play the thread game. Each move is (side, top dot, bottom dot), side 0 for top."""
    T, B = top_list(tn), bot_list(bn)
    moves, pairs = [], []
    used = [set(), set()]
    lists = [T, B]
    ptr = [0, 0]
    for k in range(turns):
        side = k % 2
        me, other = lists[side], lists[1 - side]
        while me[ptr[side]] in used[side]:
            ptr[side] += 1
        x = me[ptr[side]]
        below = [p[1 - side] for p in pairs if p[side] < x]
        above = [p[1 - side] for p in pairs if p[side] > x]
        lo, hi = max(below, default=None), min(above, default=None)
        y = next((v for v in other if v not in used[1 - side]
                  and (lo is None or v > lo) and (hi is None or v < hi)), None)
        if y is None:  # Only in the blur of the fast run, where any dot in the gap will do.
            y = (lo + hi) / 2
            if side == 0 and 1 <= y <= 2:
                y = (lo + 1) / 2 if lo < 1 else (2 + hi) / 2
        used[side].add(x)
        used[1 - side].add(y)
        pair = (x, y) if side == 0 else (y, x)
        pairs.append(pair)
        moves.append((side, *pair))
    return moves


def careless(ring, n):
    """Top-only play with free partner choice, so that the bottom dot `ring` is never used."""
    alpha = 0.3819
    pairs = []
    for t in top_list(n):
        left = t < alpha
        lows = [b for a, b in pairs if a < t and (a < alpha) == left]
        highs = [b for a, b in pairs if a > t and (a < alpha) == left]
        lo = max(lows, default=Fr(0) if left else ring)
        hi = min(highs, default=ring if left else Fr(3))
        b = (lo + hi) / 2
        if 1 <= b <= 2:
            b = (2 + hi) / 2 if not highs else (lo + 1) / 2
        pairs.append((t, b))
    return pairs


def rats(lo, hi, qmax):
    """Rationals strictly between lo and hi with denominator at most qmax."""
    out = set()
    for q in range(1, qmax + 1):
        for p in range(int(lo * q) - 1, int(hi * q) + 2):
            v = Fr(p, q)
            if lo < v < hi:
                out.add(v)
    return sorted(out)


def fr_tex(f):
    f = Fr(f)
    if f.denominator == 1:
        return str(f.numerator)
    sign = "-" if f < 0 else ""
    return rf"{sign}\frac{{{abs(f.numerator)}}}{{{f.denominator}}}"


# ---------------------------------------------------------------------------
# Shared builders (also used by shorts.py)
# ---------------------------------------------------------------------------


class RatLine(VGroup):
    """A line of rational dots. Dots with bigger denominators are drawn smaller."""

    def __init__(self, lo, hi, unit, y=0.0, x0=0.0, qmax=8, pieces=None, r=0.085,
                 color=FG, axis_color=MUTED, extra=()):
        super().__init__()
        self.mid, self.unit, self.y, self.x0 = (lo + hi) / 2, unit, y, x0
        spans = pieces or [(lo, hi)]
        self.axis = VGroup(*[Line(self.p(a), self.p(b), color=axis_color, stroke_width=3)
                             for a, b in spans])
        vals = set(extra)
        for a, b in spans:
            vals |= set(rats(a, b, qmax))
        self.by = {v: Dot(self.p(v), radius=r * v.denominator ** -0.35, color=color)
                   for v in sorted(vals)}
        self.dots = VGroup(*self.by.values())
        self.add(self.axis, self.dots)

    def p(self, v):
        return np.array([self.x0 + (float(v) - self.mid) * self.unit, self.y, 0.0])

    def hollow(self, v):
        return Circle(radius=0.08, color=FG, stroke_width=2.5, fill_color=BG,
                      fill_opacity=1).move_to(self.p(v))

    def numbers(self, vals, size=30, color=MUTED, buff=0.26):
        return VGroup(*[math(str(v), size=size, color=color).next_to(self.p(v), DOWN, buff=buff)
                        for v in vals])


def tips(x_left, x_right, y, color=MUTED, size=0.13):
    tri = Triangle(color=color, fill_opacity=1, stroke_width=0).scale(size)
    return VGroup(tri.copy().rotate(PI / 2).move_to([x_left, y, 0]),
                  tri.copy().rotate(-PI / 2).move_to([x_right, y, 0]))


def two_piece(unit, y, x0=0.0, qmax=9, labels=True, **kw):
    """The rationals strictly between 0 and 1 and strictly between 2 and 3."""
    line = RatLine(0, 3, unit, y=y, x0=x0, qmax=qmax, pieces=PIECES, **kw)
    line.holes = VGroup(*[line.hollow(v) for v in range(4)])
    line.add(line.holes)
    if labels:
        line.nums = line.numbers(range(4))
        line.add(line.nums)
    return line


def Checkmark(mob, color=GOOD):
    """A small tick to the left of a line of text."""
    p = mob.get_left() + LEFT * 0.55
    return VMobject(color=color, stroke_width=6).set_points_as_corners(
        [p + np.array([-0.16, 0.0, 0]), p + np.array([-0.04, -0.14, 0]), p + np.array([0.2, 0.18, 0])])


def fact_tag(i, size=34, color=PRIMARY):
    return text(f"{i + 1}. {FACTS[i]}", size=size, color=color)


def fact_stack(n=3, size=34, color=PRIMARY):
    g = VGroup(*[fact_tag(i, size, color) for i in range(n)])
    g.arrange(DOWN, aligned_edge=LEFT, buff=0.16)
    return g.to_corner(UL, buff=0.45)


def table(cols=6, rows=6, cell_w=1.3, cell_h=0.76, x=0.3, y=1.85, size=34):
    """The fraction table: (top headers, side headers, cells, rules, dots)."""
    xc = lambda c: x + (c - cols / 2 + 0.5) * cell_w  # noqa: E731
    yr = lambda r: y - (r + 1) * cell_h  # noqa: E731
    top = VGroup(*[math(str(head(c)), size=size + 2, color=SECONDARY).move_to([xc(c), y, 0])
                   for c in range(cols)])
    side = VGroup(*[math(str(head(r)), size=size + 2, color=PRIMARY).move_to([xc(-1), yr(r), 0])
                    for r in range(rows)])
    cells = {(r, c): math(f"{{{head(r)}}}/{{{head(c)}}}", size=size).move_to([xc(c), yr(r), 0])
             for r in range(rows) for c in range(cols)}
    w, h = cols * cell_w, rows * cell_h
    rules = VGroup(
        Line([xc(-1) - 0.45, y - cell_h / 2, 0], [xc(cols - 1) + 0.6, y - cell_h / 2, 0],
             color=MUTED, stroke_width=2),
        Line([xc(0) - cell_w / 2, y + 0.3, 0], [xc(0) - cell_w / 2, yr(rows - 1) - 0.3, 0],
             color=MUTED, stroke_width=2),
    )
    more = VGroup(math(r"\cdots", size=size).move_to([xc(cols - 1) + 0.75, y, 0]),
                  math(r"\vdots", size=size).move_to([xc(-1), yr(rows) + 0.2, 0]))
    return top, side, cells, rules, more


def diagonal_walk(dmax):
    """(row, col, is_new) along the diagonals, top right to bottom left of each."""
    seen = {Fr(0)}
    for d in range(dmax + 1):
        for r in range(d + 1):
            v = Fr(head(r), head(d - r))
            yield r, d - r, v not in seen
            seen.add(v)


def list_row(vals, y, x0=-5.3, step=1.02, size=34, color=FG, tail=True):
    entries = VGroup(*[math(fr_tex(v), size=size, color=color).move_to([x0 + i * step, y, 0])
                       for i, v in enumerate(vals)])
    dots = math(r"\dots", size=size, color=color).move_to([x0 + len(vals) * step, y, 0])
    return entries, dots


def list_slots(n, y, x0=-5.3, step=1.02, w=0.7):
    return VGroup(*[Line([x0 + i * step - w / 2, y, 0], [x0 + i * step + w / 2, y, 0],
                         color=MUTED, stroke_width=2) for i in range(n)])


SPOTS = [0, 1, -1, 2, -2, 3, -3, 4, -4, 5, -5]
LIST11 = top_list(11)
HALF, TWO = 3, 4  # where 1/2 and 2 sit in LIST11


def spot_line(y=-0.8, unit=1.2, half=6.7, top=5, size=30):
    """The axis with integer spots marked: VGroup(axis, ticks, labels)."""
    pt = lambda v: np.array([float(v) * unit, y, 0])  # noqa: E731
    axis = Line(LEFT * half + UP * y, RIGHT * half + UP * y, color=MUTED, stroke_width=3)
    ticks = VGroup(*[Line(pt(s) + DOWN * 0.12, pt(s) + UP * 0.12, color=MUTED, stroke_width=3)
                     for s in range(-top, top + 1)])
    labels = VGroup(*[math(str(s), size=size, color=MUTED).next_to(pt(s), DOWN, buff=0.26)
                      for s in range(-top, top + 1)])
    return VGroup(axis, ticks, labels), pt


def placed_rationals(pt, on_spot=True, n=11):
    """The list as dot and fraction label pairs, sitting at their integer spots or true values."""
    out = VGroup()
    for v, s in zip(LIST11[:n], SPOTS):
        at = pt(s if on_spot else v)
        d = Dot(at, radius=0.1, color=PRIMARY)
        lab = math(fr_tex(v), size=30, color=FG).next_to(at, UP, buff=0.22)
        out.add(VGroup(d, lab))
    return out


class Game:
    """The thread game: rationals on top, the two-piece line below, threads between."""

    def __init__(self, top_y=1.2, bot_y=-1.2, top_unit=1.5, bot_unit=3.7, top_half=4.6,
                 list_y=(3.2, -3.35), list_step=1.02, list_x0=-5.3, list_n=11, list_size=32,
                 lab=30, qt=6, qb=9, width=3):
        self.top = RatLine(-top_half, top_half, top_unit, y=top_y, qmax=qt, r=0.05, color=MUTED)
        self.bot = two_piece(bot_unit, bot_y, qmax=qb, r=0.05, color=MUTED)
        self.lines = (self.top, self.bot)
        self.colors = (SECONDARY, PRIMARY)
        self.lab, self.width = lab, width
        self.list_n = list_n
        self.vals = (top_list(list_n), bot_list(list_n))
        self.lists = [list_row(self.vals[i], list_y[i], x0=list_x0, step=list_step,
                               size=list_size, color=self.colors[i]) for i in range(2)]
        self.list_group = VGroup(*[VGroup(e, d) for e, d in self.lists])
        self.threads, self.marks, self.strikes = VGroup(), VGroup(), VGroup()
        self.pairs = []

    def base(self):
        return VGroup(self.top, self.bot)

    def thread(self, t, b, color=FG, width=None, opacity=1.0):
        return Line(self.top.p(t), self.bot.p(b), color=color, stroke_width=width or self.width,
                    stroke_opacity=opacity)

    def mark(self, side, v):
        """A bright dot with its fraction label, on one of the lines."""
        at = self.lines[side].p(v)
        d = Dot(at, radius=0.1, color=self.colors[side])
        lab = math(fr_tex(v), size=self.lab, color=self.colors[side])
        lab.next_to(at, UP if side == 0 else DOWN, buff=0.2 if side == 0 else 0.3)
        if side == 0 and v == Fr(1, 3):  # sits right next to 1/2
            lab.shift(UP * 0.62)
        return VGroup(d, lab)

    def entry(self, side, v):
        return self.lists[side][0][self.vals[side].index(v)]

    def region(self, side, lo, hi, color=GOOD):
        """A soft bar over the part of a line where a partner is allowed."""
        ln = self.lines[side]
        xmax = FW / 2 - 0.4
        a = -xmax if lo is None else ln.p(lo)[0]
        b = xmax if hi is None else ln.p(hi)[0]
        return Rectangle(width=b - a, height=0.5, stroke_width=0, fill_color=color,
                         fill_opacity=0.28).move_to([(a + b) / 2, ln.y, 0])

    def bounds(self, side, x):
        below = [p[side] for p in self.pairs if p[1 - side] < x]
        above = [p[side] for p in self.pairs if p[1 - side] > x]
        return max(below, default=None), min(above, default=None)

    def instant(self, moves):
        """Everything the given moves leave on screen, without animating."""
        out = VGroup()
        for side, t, b in moves:
            m0, m1 = self.mark(0, t), self.mark(1, b)
            th = self.thread(t, b)
            s0, s1 = self.cross(0, t), self.cross(1, b)
            self.marks.add(m0, m1)
            self.threads.add(th)
            self.strikes.add(s0, s1)
            self.pairs.append((t, b))
            out.add(th, m0, m1, s0, s1)
        return out

    def cross(self, side, v):
        e = self.entry(side, v)
        return strike(e, color=MUTED, width=3).scale(1.1)

    def play_move(self, scene, tr, move, mark):
        """One narrated turn: pick, shade the allowed stretch, scan, thread."""
        side, t, b = move
        x, y = (t, b) if side == 0 else (b, t)
        other = 1 - side
        lo, hi = self.bounds(other, x)
        T = tr.time_until_bookmark(mark)
        pick, partner = self.mark(side, x), self.mark(other, y)
        box = SurroundingRectangle(self.entry(side, x), color=self.colors[side], buff=0.07)
        reg = self.region(other, lo, hi)
        scene.play(Create(box), FadeIn(pick, scale=1.6), run_time=rt(min(0.8, T * 0.3)))
        scene.play(FadeIn(reg), run_time=rt(min(0.7, T * 0.25)))
        left = tr.time_until_bookmark(mark)
        if left > 0.6:
            scene.wait(left - 0.6)
        box2 = SurroundingRectangle(self.entry(other, y), color=self.colors[other], buff=0.07)
        scene.play(FadeIn(box2), run_time=0.25)
        th = self.thread(t, b)
        s0, s1 = self.cross(side, x), self.cross(other, y)
        scene.play(FadeIn(partner, scale=1.6), Create(th), FadeOut(reg), FadeOut(box), FadeOut(box2),
                   Create(s0), Create(s1), run_time=0.7)
        self.marks.add(pick, partner)
        self.threads.add(th)
        self.strikes.add(s0, s1)
        self.pairs.append((t, b))


def curtain(game, moves, width=1.3, opacity=0.6):
    """Threads for many moves, hidden, in order. Pair with reveal()."""
    return VGroup(*[game.thread(t, b, width=width, opacity=0.0) for _, t, b in moves])


def reveal(curt, opacity=0.6):
    """Show threads one after another, in play order, as alpha goes from 0 to 1."""
    n = len(curt)

    def go(m, a):
        k = int(n * a)
        for i, th in enumerate(m):
            th.set_stroke(opacity=opacity if i < k else 0.0)

    return go


def title_two_lines():
    a, b = text(TITLE[0], size=52, weight="BOLD"), text(TITLE[1], size=52, weight="BOLD", color=PRIMARY)
    return VGroup(a, b).arrange(DOWN, buff=0.25)


# ---------------------------------------------------------------------------
# s01 Hook
# ---------------------------------------------------------------------------


class S01Hook(VoiceoverScene):
    def construct(self):
        self.set_speech_service(get_speech_service())
        L = RatLine(-1.5, 4.5, 2.0, y=-0.2, qmax=10)
        nums = L.numbers(range(-1, 5))
        arrows = tips(-6.45, 6.45, -0.2)
        lab = text("the rational numbers", size=38).move_to(UP * 2.0)
        with self.voiceover(text=N("s01.b1")) as tr:
            self.play(Create(L.axis), FadeIn(arrows), FadeIn(nums), run_time=0.7)
            self.play(FadeIn(L.dots, lag_ratio=0.01), FadeIn(lab), run_time=rt(min(2.5, tr.duration - 1.0)))
            rest(self, tr)

        outside = VGroup(*[d for v, d in L.by.items() if not any(a < v < b for a, b in PIECES)])
        segs = VGroup(*[Line(L.p(a), L.p(b), color=MUTED, stroke_width=3) for a, b in PIECES])
        holes = VGroup(*[L.hollow(v) for v in range(4)])
        with self.voiceover(text=N("s01.b2")) as tr:
            wait_until(self, tr, "keep")
            self.play(FadeOut(outside), FadeOut(L.axis), FadeOut(arrows), FadeIn(segs), FadeIn(holes),
                      FadeOut(lab), run_time=rt(min(1.5, tr.get_remaining_duration())))
            rest(self, tr)

        root = Dot(L.p(2**0.5), radius=0.13, color=PRIMARY)
        rlab = math(r"\sqrt{2}", size=46, color=PRIMARY).next_to(L.p(2**0.5), UP, buff=0.45)
        with self.voiceover(text=N("s01.b3")) as tr:
            self.play(FadeIn(outside), FadeIn(L.axis), FadeIn(arrows), FadeOut(segs), FadeOut(holes),
                      run_time=rt(min(0.8, tr.time_until_bookmark("add"))))
            wait_until(self, tr, "add")
            self.play(FadeIn(root, shift=DOWN * 0.8), FadeIn(rlab, shift=DOWN * 0.8), run_time=0.7)
            rest(self, tr)

        ys = (2.3, 0.0, -2.3)
        A = RatLine(-1.5, 4.5, 2.0, y=ys[0], qmax=8)
        B = two_piece(2.0, ys[1], qmax=8, labels=False)
        B.shift(RIGHT * (L.p(0)[0] - B.p(0)[0]))
        C = RatLine(-1.5, 4.5, 2.0, y=ys[2], qmax=8)
        root2 = Dot(C.p(2**0.5), radius=0.11, color=PRIMARY)
        rlab2 = math(r"\sqrt{2}", size=36, color=PRIMARY).next_to(C.p(2**0.5), DOWN, buff=0.22)
        eqs = VGroup(*[math("=", size=70, color=PRIMARY).move_to(UP * y)
                       for y in (1.15, -1.15)])
        current = VGroup(L, nums, arrows, root, rlab)
        with self.voiceover(text=N("s01.b4")) as tr:
            self.play(FadeOut(current), FadeIn(A), FadeIn(B), FadeIn(C), FadeIn(root2), FadeIn(rlab2),
                      run_time=1.0)
            wait_until(self, tr, "same")
            self.play(FadeIn(eqs, scale=1.6, lag_ratio=0.3), run_time=0.8)
            rest(self, tr)
        self.play(FadeOut(VGroup(A, B, C, root2, rlab2, eqs)), run_time=0.4)
        ttl = title_two_lines()
        self.play(FadeIn(ttl, shift=UP * 0.2), run_time=0.6)
        self.wait(1.2)
        self.play(FadeOut(ttl), run_time=0.4)


# ---------------------------------------------------------------------------
# s02 A crowded line
# ---------------------------------------------------------------------------


class S02Crowded(VoiceoverScene):
    def construct(self):
        self.set_speech_service(get_speech_service())
        y = -0.3
        L = RatLine(-7, 7, 2.0, y=y, qmax=7)
        nums = L.numbers(range(-6, 7))
        moving = VGroup(L, nums)
        arrows = tips(-6.85, 6.85, y, size=0.15)
        tag1 = fact_tag(0).to_corner(UL, buff=0.45)
        with self.voiceover(text=N("s02.b1")) as tr:
            self.play(FadeIn(moving), FadeIn(arrows), run_time=0.7)
            self.play(FadeIn(tag1), run_time=rt(min(0.6, tr.time_until_bookmark("first"))))
            wait_until(self, tr, "first")
            t = tr.get_remaining_duration()
            self.play(moving.animate.shift(LEFT * 3.5), run_time=rt(t * 0.3), rate_func=smooth)
            self.play(moving.animate.shift(RIGHT * 7), run_time=rt(t * 0.4), rate_func=smooth)
            self.play(moving.animate.shift(LEFT * 3.5), run_time=rt(t * 0.3), rate_func=smooth)

        ax = Line(LEFT * 6.3 + UP * y, RIGHT * 6.3 + UP * y, color=MUTED, stroke_width=3)
        a0, b0 = -5.0, 5.0
        pt = lambda x: np.array([x, y, 0])  # noqa: E731
        da, db = Dot(pt(a0), radius=0.14, color=PRIMARY), Dot(pt(b0), radius=0.14, color=PRIMARY)
        la = math("a", size=44, color=PRIMARY).next_to(da, UP, buff=0.25)
        lb = math("b", size=44, color=PRIMARY).next_to(db, UP, buff=0.25)
        mid = Dot(pt(0), radius=0.11, color=SECONDARY)
        mlab = math(r"\frac{a+b}{2}", size=38, color=SECONDARY).next_to(mid, UP, buff=0.25)
        rounds = []
        for k in range(2, 8):
            n = 2**k
            r = max(0.022, 0.1 * 0.72 ** (k - 1))
            rounds.append(VGroup(*[Dot(pt(a0 + (b0 - a0) * i / n), radius=r, color=FG)
                                   for i in range(1, n, 2)]))
        with self.voiceover(text=N("s02.b2")) as tr:
            self.play(FadeOut(moving), FadeOut(arrows), FadeIn(ax), run_time=0.6)
            self.play(FadeIn(da, scale=2), FadeIn(la), FadeIn(db, scale=2), FadeIn(lb),
                      run_time=rt(min(0.8, tr.time_until_bookmark("avg") - 0.1)))
            wait_until(self, tr, "avg")
            self.play(FadeIn(mid, scale=2), FadeIn(mlab), run_time=0.6)
            wait_until(self, tr, "fill")
            t = tr.time_until_bookmark("dense")
            self.play(FadeOut(mlab), run_time=0.3)
            t = max(0.6, t - 0.3)
            weights = [1.2, 1.0, 0.8, 0.7, 0.6, 0.5]
            for g, w in zip(rounds, weights):
                self.play(FadeIn(g, lag_ratio=0.08), run_time=rt(t * w / sum(weights)))
            wait_until(self, tr, "dense")
            tag2 = fact_tag(1)
            tag2.next_to(tag1, DOWN, buff=0.16, aligned_edge=LEFT)
            word = text("dense", size=60, color=PRIMARY, weight="BOLD").move_to(UP * 1.7)
            self.play(FadeIn(word, shift=UP * 0.2), FadeIn(tag2), run_time=0.5)
            rest(self, tr)
        self.play(FadeOut(VGroup(ax, da, db, la, lb, mid, word, *rounds)), run_time=0.4)


# ---------------------------------------------------------------------------
# s03 Countable anyway
# ---------------------------------------------------------------------------

LIST_Y = 3.2


class S03Countable(VoiceoverScene):
    def construct(self):
        self.set_speech_service(get_speech_service())
        tags = VGroup(fact_stack(2))
        self.add(tags)
        y = -0.3
        L = RatLine(-4.6, 4.6, 1.5, y=y, qmax=9, r=0.07, color=FG)
        ints = VGroup(*[Dot(L.p(i), radius=0.12, color=PRIMARY) for i in range(-4, 5)])
        for i in range(-4, 5):
            L.by[Fr(i)].set_opacity(0)
        nums = L.numbers(range(-4, 5), size=34)
        with self.voiceover(text=N("s03.b1")) as tr:
            self.play(Create(L.axis), FadeIn(ints, lag_ratio=0.1), FadeIn(nums), run_time=1.2)
            wait = tr.get_remaining_duration()
            self.play(FadeIn(L.dots, lag_ratio=0.005), run_time=rt(min(2.0, wait)))
            rest(self, tr)

        slots = list_slots(11, -2.6)
        ldots = math(r"\dots", size=34).move_to([-5.3 + 11 * 1.02, -2.4, 0])
        tag3 = fact_tag(2).next_to(tags, DOWN, buff=0.16, aligned_edge=LEFT)
        with self.voiceover(text=N("s03.b2")) as tr:
            wait_until(self, tr, "same")
            self.play(L.dots.animate.set_color(SECONDARY), run_time=0.5)
            self.play(L.dots.animate.set_color(FG), FadeIn(tag3), run_time=0.5)
            t = tr.get_remaining_duration()
            self.wait(max(0, t * 0.45))
            self.play(Create(slots, lag_ratio=0.1), FadeIn(ldots), run_time=rt(min(1.5, t * 0.5)))
            rest(self, tr)

        top, side, cells, rules, more = table()
        entries, ldots2 = list_row(LIST11, LIST_Y)
        slots2 = list_slots(11, LIST_Y - 0.42)
        with self.voiceover(text=N("s03.b3")) as tr:
            self.play(FadeOut(VGroup(tags, tag3, L, ints, nums)), Transform(slots, slots2),
                      ldots.animate.move_to(ldots2), run_time=0.7)
            t = tr.time_until_bookmark("cell")
            self.play(Create(rules), FadeIn(top, lag_ratio=0.15), run_time=rt(t * 0.5))
            self.play(FadeIn(side, lag_ratio=0.15), FadeIn(more), run_time=rt(t * 0.4))
            wait_until(self, tr, "cell")
            ordered = [cells[(r, c)] for d in range(11) for r in range(6) for c in range(6) if r + c == d]
            self.play(FadeIn(VGroup(*ordered), lag_ratio=0.03), run_time=rt(min(2.2, tr.get_remaining_duration())))
            rest(self, tr)

        box23 = SurroundingRectangle(cells[(2, 4)], color=PRIMARY, buff=0.06)
        box1 = SurroundingRectangle(cells[(0, 0)], color=BAD, buff=0.06)
        box2 = SurroundingRectangle(cells[(1, 1)], color=BAD, buff=0.06)
        with self.voiceover(text=N("s03.b4")) as tr:
            self.play(Create(box23), run_time=0.5)
            wait_until(self, tr, "twice")
            self.play(FadeOut(box23), Create(box1), Create(box2), run_time=0.5)
            rest(self, tr)

        walk = list(diagonal_walk(5))
        lines = VGroup(*[Line(cells[(0, d)].get_center(), cells[(d, 0)].get_center(),
                              color=SECONDARY, stroke_width=2, stroke_opacity=0.45)
                         for d in range(1, 6)])
        zero = entries[0]
        with self.voiceover(text=N("s03.b5")) as tr:
            self.play(FadeOut(box1), FadeOut(box2), FadeIn(zero, shift=UP * 0.2), run_time=0.5)
            wait_until(self, tr, "walk")
            self.play(Create(lines, lag_ratio=0.3), run_time=rt(min(1.2, tr.time_until_bookmark("one"))))
            wait_until(self, tr, "one")
            box = SurroundingRectangle(cells[(0, 0)], color=SECONDARY, buff=0.06)
            self.add(box)
            per = tr.get_remaining_duration() / len(walk)
            i = 1
            for r, c, new in walk:
                cell = cells[(r, c)]
                anims = [box.animate.move_to(cell)]
                if new:
                    anims.append(TransformFromCopy(cell, entries[i]))
                    i += 1
                else:
                    anims.append(Create(strike(cell, width=3).scale(1.15)))
                    anims.append(cell.animate.set_opacity(0.3))
                self.play(*anims, run_time=rt(per))
            self.play(FadeOut(box), FadeIn(ldots2), run_time=0.2)
            rest(self, tr)

        ln, pt = spot_line()
        placed = placed_rationals(pt, on_spot=False)
        for g in placed:
            g[1].set_opacity(0)
        haze = RatLine(-5.6, 5.6, 1.2, y=-0.8, qmax=7, r=0.06, color=MUTED)
        for v in LIST11:
            if v in haze.by:
                haze.by[v].set_opacity(0)
        keep = VGroup(entries, ldots2, slots, ldots)
        others = [m for m in self.mobjects if m not in (entries, ldots2, slots, ldots)
                  and m not in entries.submobjects]
        with self.voiceover(text=N("s03.b6")) as tr:
            self.play(*[FadeOut(m) for m in others], run_time=0.6)
            self.remove(*others)
            self.add(entries, ldots2, slots)
            self.play(FadeIn(ln), FadeIn(haze.dots), FadeIn(VGroup(*[g[0] for g in placed])), run_time=0.7)
            wait_until(self, tr, "fly")
            t = tr.get_remaining_duration()
            weights = [1.0, 1.0, 1.0, 0.9, 0.9, 0.5, 0.5, 0.35, 0.35, 0.3, 0.3]
            flow = 0.9
            for k, (g, s) in enumerate(zip(placed, SPOTS)):
                shift = pt(s) - g[0].get_center()
                g[1].set_opacity(1).next_to(g[0], UP, buff=0.22)
                dur = rt((t - flow) * weights[k] / sum(weights))
                self.play(entries[k].animate.set_color(PRIMARY),
                          g.animate(path_arc=-PI / 2 if float(s) >= float(LIST11[k]) else PI / 2).shift(shift),
                          run_time=dur)
            self.play(*[d.animate.shift(RIGHT * (9 if d.get_x() >= 0 else -9)).set_opacity(0)
                        for d in haze.dots], run_time=flow, rate_func=rush_into)
            self.remove(haze.dots)


# ---------------------------------------------------------------------------
# s04 What got scrambled
# ---------------------------------------------------------------------------


class S04Scrambled(VoiceoverScene):
    def construct(self):
        self.set_speech_service(get_speech_service())
        entries, ldots = list_row(LIST11, LIST_Y)
        entries.set_color(PRIMARY)
        slots = list_slots(11, LIST_Y - 0.42)
        ln, pt = spot_line()
        placed = placed_rationals(pt)
        self.add(entries, ldots, slots, ln, placed)

        half, two = placed[HALF], placed[TWO]
        r1 = SurroundingRectangle(half, color=SECONDARY, buff=0.1)
        r2 = SurroundingRectangle(two, color=SECONDARY, buff=0.1)
        arrow = CurvedArrow(r2.get_top() + UP * 0.1, r1.get_top() + UP * 0.1, angle=-PI / 3,
                            color=SECONDARY, stroke_width=4)
        with self.voiceover(text=N("s04.b1")) as tr:
            self.play(FadeOut(VGroup(entries, ldots, slots)), run_time=0.4)
            wait_until(self, tr, "half")
            self.play(Create(r1), Create(r2), run_time=0.5)
            self.play(Create(arrow), run_time=rt(min(1.0, tr.get_remaining_duration())))
            rest(self, tr)

        y = 0.2
        # Left: integers 3 and 4. Right: two rationals, with dots between.
        lx, rx = -3.4, 3.4
        la = Line([lx - 2.4, y, 0], [lx + 2.4, y, 0], color=MUTED, stroke_width=3)
        d3 = Dot([lx - 1.5, y, 0], radius=0.14, color=PRIMARY)
        d4 = Dot([lx + 1.5, y, 0], radius=0.14, color=PRIMARY)
        l3 = math("3", size=46).next_to(d3, DOWN, buff=0.25)
        l4 = math("4", size=46).next_to(d4, DOWN, buff=0.25)
        br = Brace(VGroup(d3, d4), UP, buff=0.3, color=MUTED)
        empty = text("nothing between", size=32, color=MUTED).next_to(br, UP, buff=0.15)
        ra = Line([rx - 2.4, y, 0], [rx + 2.4, y, 0], color=MUTED, stroke_width=3)
        p, q = Dot([rx - 1.5, y, 0], radius=0.14, color=SECONDARY), Dot([rx + 1.5, y, 0], radius=0.14, color=SECONDARY)
        lp = math(r"\tfrac{1}{3}", size=46).next_to(p, DOWN, buff=0.25)
        lq = math(r"\tfrac{1}{2}", size=46).next_to(q, DOWN, buff=0.25)
        between = VGroup(*[Dot([rx - 1.5 + 3 * i / 32, y, 0], radius=0.09 if i % 8 == 0 else 0.05, color=FG)
                           for i in range(1, 32)])
        br2 = Brace(VGroup(p, q), UP, buff=0.3, color=MUTED)
        full = text("always more", size=32, color=MUTED).next_to(br2, UP, buff=0.15)
        same = text("Same count, different shape.", size=44, color=PRIMARY).move_to(DOWN * 2.3)
        left = VGroup(la, d3, d4, l3, l4)
        right = VGroup(ra, p, q, lp, lq)
        with self.voiceover(text=N("s04.b2")) as tr:
            wait_until(self, tr, "gap")
            self.play(FadeOut(VGroup(ln, placed, r1, r2, arrow)), run_time=0.4)
            self.play(FadeIn(left), FadeIn(right), run_time=0.4)
            self.play(FadeIn(br), FadeIn(empty), run_time=0.5)
            self.play(FadeIn(between, lag_ratio=0.03), FadeIn(br2), FadeIn(full), run_time=rt(min(1.2, tr.get_remaining_duration() * 0.5)))
            t = tr.get_remaining_duration()
            self.wait(max(0, t - 0.8))
            self.play(FadeIn(same, shift=UP * 0.2), run_time=0.5)
            rest(self, tr)

        facts = VGroup(*[text(f, size=38) for f in FACTS]).arrange(DOWN, aligned_edge=LEFT, buff=0.3)
        checks = VGroup(*[Checkmark(f) for f in facts])
        sheet = VGroup(facts, checks).move_to(UP * 1.5)
        bare = RatLine(-2.6, 2.6, 2.2, y=-1.8, qmax=7, color=TERTIARY)
        mark = text("?", size=70, color=TERTIARY, weight="BOLD").next_to(bare, UP, buff=0.3)
        with self.voiceover(text=N("s04.b3")) as tr:
            self.play(FadeOut(VGroup(left, right, between, br, br2, empty, full, same)), run_time=0.5)
            self.play(FadeIn(facts, lag_ratio=0.3), FadeIn(checks, lag_ratio=0.3), run_time=1.0)
            self.play(FadeIn(bare), FadeIn(mark), run_time=rt(min(0.8, tr.get_remaining_duration())))
            rest(self, tr)
        self.play(FadeOut(VGroup(sheet, bare, mark)), run_time=0.4)


# ---------------------------------------------------------------------------
# s05 Disguises
# ---------------------------------------------------------------------------


def uneven_threads(top_y=1.3, bot_y=-1.3):
    """Two short lines with a few uneven dots, one thread per pair."""
    xs_top = [-5.4, -3.7, -2.9, -0.8, 0.6, 2.9, 5.2]
    xs_bot = [-5.0, -4.2, -1.9, -0.9, 1.8, 3.1, 4.6]
    ax_t = Line([-6.3, top_y, 0], [6.3, top_y, 0], color=MUTED, stroke_width=3)
    ax_b = Line([-6.3, bot_y, 0], [6.3, bot_y, 0], color=MUTED, stroke_width=3)
    dt = VGroup(*[Dot([x, top_y, 0], radius=0.11, color=SECONDARY) for x in xs_top])
    db = VGroup(*[Dot([x, bot_y, 0], radius=0.11, color=PRIMARY) for x in xs_bot])
    ths = VGroup(*[Line(a.get_center(), b.get_center(), color=FG, stroke_width=3)
                   for a, b in zip(dt, db)])
    return ax_t, ax_b, dt, db, ths


class S05Disguises(VoiceoverScene):
    def construct(self):
        self.set_speech_service(get_speech_service())
        L = RatLine(-3.5, 3.5, 1.9, y=-0.4, qmax=8)
        nums = L.numbers(range(-3, 4), size=34)
        ops = VGroup(math("+", size=70), math(r"\times", size=70)).arrange(RIGHT, buff=0.9).move_to(UP * 1.7)
        cross = VGroup(*[strike(o, width=7).scale(1.8).rotate(PI / 4) for o in ops])
        sides = VGroup(text("left", size=40, color=PRIMARY).next_to(L.p(-3.5), UP + RIGHT, buff=0.35),
                       text("right", size=40, color=PRIMARY).next_to(L.p(3.5), UP + LEFT, buff=0.35))
        with self.voiceover(text=N("s05.b1")) as tr:
            self.play(FadeIn(L), FadeIn(nums), FadeIn(ops), run_time=0.7)
            t = tr.get_remaining_duration()
            self.play(Create(cross), run_time=rt(min(0.7, t * 0.3)))
            self.wait(max(0, t * 0.15))
            self.play(FadeOut(nums), FadeIn(sides), run_time=rt(min(0.8, t * 0.25)))
            rest(self, tr)

        ax_t, ax_b, dt, db, ths = uneven_threads()
        i, j = 3, 4
        bad_i = Line(dt[i].get_center(), db[j].get_center(), color=BAD, stroke_width=4)
        bad_j = Line(dt[j].get_center(), db[i].get_center(), color=BAD, stroke_width=4)
        good_i, good_j = ths[i].copy(), ths[j].copy()
        with self.voiceover(text=N("s05.b2")) as tr:
            self.play(FadeOut(VGroup(L, ops, cross, sides)), run_time=0.4)
            self.play(FadeIn(ax_t), FadeIn(ax_b), FadeIn(dt), FadeIn(db), run_time=0.5)
            t = tr.time_until_bookmark("cross")
            self.play(Create(ths, lag_ratio=0.3), run_time=rt(min(2.2, t)))
            wait_until(self, tr, "cross")
            self.play(Transform(ths[i], bad_i), Transform(ths[j], bad_j), run_time=0.6)
            self.wait(0.5)
            self.play(Transform(ths[i], good_i), Transform(ths[j], good_j), run_time=0.6)
            rest(self, tr)

        two = two_piece(3.7, -0.6, qmax=10)
        facts = VGroup(*[text(f, size=34) for f in FACTS]).arrange(DOWN, aligned_edge=LEFT, buff=0.14)
        facts.to_corner(UL, buff=0.5).shift(RIGHT * 0.6)
        checks = [Checkmark(f) for f in facts]
        a_v, b_v = Fr(5, 6), Fr(13, 6)
        da, db2 = Dot(two.p(a_v), radius=0.13, color=SECONDARY), Dot(two.p(b_v), radius=0.13, color=SECONDARY)
        news = VGroup(*[Dot(two.p(v), radius=0.11, color=GOOD) for v in (Fr(11, 12), Fr(23, 24))])
        with self.voiceover(text=N("s05.b3")) as tr:
            self.play(FadeOut(VGroup(ax_t, ax_b, dt, db, ths)), run_time=0.4)
            self.play(FadeIn(two), FadeIn(facts), run_time=0.6)
            wait_until(self, tr, "ends")
            self.play(Indicate(two.holes[0], color=PRIMARY, scale_factor=2),
                      Indicate(two.holes[3], color=PRIMARY, scale_factor=2), Create(checks[0]), run_time=0.8)
            t = tr.time_until_bookmark("between")
            self.play(Indicate(two.holes[1], color=PRIMARY, scale_factor=2),
                      Indicate(two.holes[2], color=PRIMARY, scale_factor=2), run_time=rt(min(0.8, t)))
            self.play(FadeIn(da, scale=2), FadeIn(db2, scale=2), run_time=rt(min(0.6, t)))
            wait_until(self, tr, "between")
            self.play(FadeIn(news, scale=2, lag_ratio=0.5), Create(checks[1]), run_time=rt(min(1.0, tr.time_until_bookmark("list"))))
            wait_until(self, tr, "list")
            self.play(Create(checks[2]), run_time=0.5)
            rest(self, tr)

        A = RatLine(-3.5, 3.5, 1.9, y=1.3, qmax=8)
        B = two_piece(3.7, -1.3, qmax=9, labels=False)
        eq = math("=", size=90, color=PRIMARY).move_to(ORIGIN)
        iso = text("order isomorphic", size=30, color=MUTED).to_edge(DOWN, buff=0.6)
        with self.voiceover(text=N("s05.b4")) as tr:
            self.play(FadeOut(VGroup(two, facts, *checks, da, db2, news)), FadeIn(A), FadeIn(B), run_time=0.8)
            wait_until(self, tr, "claim")
            self.play(FadeIn(eq, scale=1.6), FadeIn(iso), run_time=0.6)
            rest(self, tr)
        self.play(FadeOut(VGroup(A, B, eq, iso)), run_time=0.4)


# ---------------------------------------------------------------------------
# s06 The thread game
# ---------------------------------------------------------------------------

MOVES = simulate(200)
RING = Fr(2, 3)


class S06Game(VoiceoverScene):
    def construct(self):
        self.set_speech_service(get_speech_service())
        g = Game()
        with self.voiceover(text=N("s06.b1")) as tr:
            self.play(FadeIn(g.base()), run_time=0.8)
            wait_until(self, tr, "lists")
            self.play(FadeIn(g.list_group[0], lag_ratio=0.05), FadeIn(g.list_group[1], lag_ratio=0.05),
                      run_time=rt(min(1.2, tr.time_until_bookmark("switch"))))
            wait_until(self, tr, "switch")
            per = min(0.55, tr.time_until_bookmark("pick") / 6)
            for v in g.vals[1][:6]:
                pop = Dot(g.bot.p(v), radius=0.13, color=PRIMARY)
                box = SurroundingRectangle(g.entry(1, v), color=PRIMARY, buff=0.07)
                self.add(pop, box)
                self.wait(per)
                self.remove(pop, box)
            wait_until(self, tr, "pick")
            first = VGroup(SurroundingRectangle(g.entry(0, g.vals[0][0]), color=SECONDARY, buff=0.07),
                           SurroundingRectangle(g.entry(1, g.vals[1][0]), color=PRIMARY, buff=0.07))
            self.play(Create(first), run_time=0.5)
            rest(self, tr)
            self.play(FadeOut(first), run_time=0.2)

        for i in range(4):
            with self.voiceover(text=N(f"s06.b{i + 2}")) as tr:
                g.play_move(self, tr, MOVES[i], f"t{i + 1}")
                rest(self, tr)

        ps = sorted(g.pairs)
        xmax = FW / 2
        tp = [np.array([-xmax, g.top.y, 0])] + [g.top.p(a) for a, _ in ps] + [np.array([xmax, g.top.y, 0])]
        bp = [np.array([-xmax, g.bot.y, 0])] + [g.bot.p(b) for _, b in ps] + [np.array([xmax, g.bot.y, 0])]
        cols = [SECONDARY, PRIMARY, TERTIARY, GOOD, SECONDARY]
        bands = VGroup(*[Polygon(tp[i], tp[i + 1], bp[i + 1], bp[i], stroke_width=0,
                                 fill_color=cols[i], fill_opacity=0.2) for i in range(5)])
        with self.voiceover(text=N("s06.b6")) as tr:
            wait_until(self, tr, "gaps")
            self.play(FadeIn(bands, lag_ratio=0.2), run_time=rt(min(1.2, tr.get_remaining_duration())))
            rest(self, tr)
            self.play(FadeOut(bands), run_time=0.3)


# ---------------------------------------------------------------------------
# s07 Why you never get stuck
# ---------------------------------------------------------------------------


class S07Stuck(VoiceoverScene):
    def construct(self):
        self.set_speech_service(get_speech_service())
        g = Game()
        drawn = g.instant(MOVES[:4])
        self.add(g.base(), g.list_group, drawn)

        new_t = Fr(3, 4)
        dot = Dot(g.top.p(new_t), radius=0.11, color=GOOD)
        lo, hi = Fr(7, 3), Fr(5, 2)
        y0 = -3.0
        x0, x1 = -1.2, 5.6
        ax = Line([x0 - 0.5, y0, 0], [x1 + 0.5, y0, 0], color=MUTED, stroke_width=3)
        d0, d1 = Dot([x0, y0, 0], radius=0.12, color=PRIMARY), Dot([x1, y0, 0], radius=0.12, color=PRIMARY)
        l0 = math(fr_tex(lo), size=30, color=PRIMARY).next_to(d0, UP, buff=0.18)
        l1 = math(fr_tex(hi), size=30, color=PRIMARY).next_to(d1, UP, buff=0.18)
        guide = VGroup(DashedLine(g.bot.p(lo), d0.get_center(), color=MUTED, stroke_width=2),
                       DashedLine(g.bot.p(hi), d1.get_center(), color=MUTED, stroke_width=2))
        mark = text("?", size=50, color=BAD, weight="BOLD").move_to([(x0 + x1) / 2, y0 + 0.5, 0])
        inset = VGroup(ax, d0, d1, l0, l1, guide)
        reg = g.region(1, lo, hi, color=BAD)
        with self.voiceover(text=N("s07.b1")) as tr:
            self.play(FadeOut(g.list_group), FadeOut(g.strikes), run_time=0.5)
            self.play(FadeIn(dot, scale=2), FadeIn(reg), run_time=0.5)
            self.play(FadeIn(inset), FadeIn(mark), run_time=rt(min(0.8, tr.get_remaining_duration())))
            rest(self, tr)

        fill = [VGroup(*[Dot([x0 + (x1 - x0) * i / n, y0, 0], radius=r, color=FG) for i in range(1, n, 2)])
                for n, r in ((2, 0.1), (4, 0.08), (8, 0.065), (16, 0.05), (32, 0.04))]
        tag = text("dense", size=38, color=GOOD, weight="BOLD").to_corner(UR, buff=0.5)
        th = g.thread(new_t, (lo + hi) / 2, color=GOOD)
        with self.voiceover(text=N("s07.b2")) as tr:
            wait_until(self, tr, "two")
            self.play(Indicate(d0, scale_factor=1.8), Indicate(d1, scale_factor=1.8), run_time=0.7)
            t = tr.get_remaining_duration()
            self.play(FadeOut(mark), FadeIn(tag), run_time=0.3)
            for f in fill:
                self.play(FadeIn(f, lag_ratio=0.1), run_time=rt((t - 1.0) / 5))
            self.play(Create(th), run_time=0.6)
            rest(self, tr)

        far = Fr(2)
        dot2 = g.mark(0, far).set_color(GOOD)
        reg2 = g.region(1, Fr(5, 2), Fr(3), color=GOOD)
        partner = g.mark(1, Fr(8, 3)).set_color(GOOD)
        th2 = g.thread(far, Fr(8, 3), color=GOOD)
        tag2 = text("no ends", size=38, color=GOOD, weight="BOLD").to_corner(UR, buff=0.5)
        with self.voiceover(text=N("s07.b3")) as tr:
            self.play(FadeOut(VGroup(inset, *fill, tag, th, dot, reg)), run_time=0.4)
            self.play(FadeIn(dot2, scale=1.6), run_time=0.5)
            wait_until(self, tr, "out")
            self.play(FadeIn(reg2), FadeIn(tag2), run_time=0.5)
            self.play(FadeIn(partner, scale=1.6), Create(th2), run_time=rt(min(0.8, tr.get_remaining_duration())))
            rest(self, tr)
        self.play(FadeOut(VGroup(reg2, tag2, dot2, partner, th2, g.threads, g.marks, g.base())), run_time=0.5)


# ---------------------------------------------------------------------------
# s08 Back and forth
# ---------------------------------------------------------------------------


class S08Back(VoiceoverScene):
    def construct(self):
        self.set_speech_service(get_speech_service())
        g = Game()
        ring_at = g.bot.p(RING)
        ring = Circle(radius=0.17, color=GOOD, stroke_width=4).move_to(ring_at)
        rdot = Dot(ring_at, radius=0.1, color=PRIMARY)
        pairs = careless(RING, 13)
        tmarks = VGroup(*[Dot(g.top.p(t), radius=0.09, color=SECONDARY) for t, _ in pairs])
        bmarks = VGroup(*[Dot(g.bot.p(b), radius=0.08, color=PRIMARY) for _, b in pairs])
        ths = VGroup(*[g.thread(t, b) for t, b in pairs])
        with self.voiceover(text=N("s08.b1")) as tr:
            self.play(FadeIn(g.base()), run_time=0.6)
            t = tr.time_until_bookmark("skip")
            self.play(FadeIn(rdot), Create(ring), run_time=0.5)
            n1 = 6
            for i in range(n1):
                self.play(FadeIn(tmarks[i]), FadeIn(bmarks[i]), Create(ths[i]), run_time=rt((t - 0.6) / n1))
            wait_until(self, tr, "skip")
            r = tr.get_remaining_duration()
            for i in range(n1, len(pairs)):
                self.play(FadeIn(tmarks[i]), FadeIn(bmarks[i]), Create(ths[i]), run_time=rt(r / (len(pairs) - n1)))
            rest(self, tr)

        with self.voiceover(text=N("s08.b2")) as tr:
            self.play(FadeOut(VGroup(ths, tmarks, bmarks)), FadeIn(g.list_group), run_time=0.5)
            wait_until(self, tr, "turns")
            per = max(0.3, (tr.get_remaining_duration() - 0.8) / 6)
            for k in range(6):
                side, a, b = MOVES[k]
                x = a if side == 0 else b
                s = g.cross(side, x)
                other = g.cross(1 - side, b if side == 0 else a)
                m0, m1 = g.mark(0, a), g.mark(1, b)
                th = g.thread(a, b, color=GOOD if b == RING else FG, width=5 if b == RING else None)
                self.play(FadeIn(m0, scale=1.5), FadeIn(m1, scale=1.5), Create(th), Create(s), Create(other),
                          run_time=rt(per))
                g.marks.add(m0, m1)
                g.threads.add(th)
                g.strikes.add(s, other)
            self.play(Flash(ring_at, color=GOOD), run_time=0.6)
            rest(self, tr)

        curt = curtain(g, MOVES[6:])
        self.add(curt)
        with self.voiceover(text=N("s08.b3")) as tr:
            wait_until(self, tr, "fast")
            self.play(FadeOut(g.list_group), FadeOut(g.strikes), FadeOut(g.marks), FadeOut(rdot), FadeOut(ring),
                      g.threads.animate.set_stroke(width=1.3, opacity=0.6, color=FG), run_time=0.5)
            self.play(UpdateFromAlphaFunc(curt, reveal(curt)), run_time=rt(tr.get_remaining_duration()),
                      rate_func=lambda a: a**2)
            rest(self, tr)

        eq = math("=", size=90, color=PRIMARY).move_to(UP * 0)
        plate = BackgroundRectangle(eq, color=BG, fill_opacity=0.85, buff=0.15)
        with self.voiceover(text=N("s08.b4")) as tr:
            self.play(FadeIn(plate), FadeIn(eq, scale=1.5), run_time=0.6)
            wait_until(self, tr, "any")
            self.play(Indicate(eq, color=PRIMARY), run_time=rt(min(0.8, tr.get_remaining_duration())))
            rest(self, tr)
        self.play(FadeOut(VGroup(curt, g.threads, g.base(), plate, eq)), run_time=0.5)


# ---------------------------------------------------------------------------
# s09 Ending
# ---------------------------------------------------------------------------


class S09Ending(VoiceoverScene):
    def construct(self):
        self.set_speech_service(get_speech_service())
        rows = [("dense", "the gaps are never empty"),
                ("no ends", "there's always room at the edges"),
                ("countable", "every dot gets its turn")]
        names = VGroup(*[text(a, size=46, color=PRIMARY, weight="BOLD") for a, _ in rows])
        jobs = VGroup(*[text(b, size=40) for _, b in rows])
        for i, (n, j) in enumerate(zip(names, jobs)):
            n.move_to(UP * (1.6 - i * 1.5) + LEFT * 2.0, aligned_edge=RIGHT)
            j.next_to(n, RIGHT, buff=0.6, aligned_edge=DOWN)
        grid = VGroup(names, jobs).move_to(ORIGIN)
        with self.voiceover(text=N("s09.b1")) as tr:
            self.play(FadeIn(names, lag_ratio=0.2), run_time=rt(min(0.9, tr.time_until_bookmark("d"))))
            for mark, i in (("d", 0), ("e", 1), ("c", 2)):
                wait_until(self, tr, mark)
                self.play(FadeIn(jobs[i], shift=RIGHT * 0.2), run_time=0.6)
            rest(self, tr)

        L = RatLine(-3.4, 3.4, 2.0, y=-1.2, qmax=8)
        with self.voiceover(text=N("s09.b2")) as tr:
            self.play(grid.animate.scale(0.72).move_to(UP * 1.5), run_time=0.7)
            self.play(FadeIn(L.axis), FadeIn(L.dots, lag_ratio=0.01), run_time=rt(min(1.5, tr.get_remaining_duration())))
            rest(self, tr)

        real = Line(LEFT * 6.3 + UP * 0.0, RIGHT * 6.3 + UP * 0.0, color=FG, stroke_width=7)
        rlab = text("the real numbers", size=40).move_to(UP * 1.9)
        hole = Circle(radius=0.15, color=PRIMARY, stroke_width=5, fill_color=BG, fill_opacity=1)
        nolist = text("can't be listed", size=40, color=BAD).move_to(DOWN * 1.3)
        with self.voiceover(text=N("s09.b3")) as tr:
            self.play(FadeOut(grid), FadeOut(L), FadeIn(real), FadeIn(rlab), run_time=0.8)
            self.play(FadeIn(nolist), run_time=rt(min(0.6, tr.time_until_bookmark("hole"))))
            wait_until(self, tr, "hole")
            self.play(GrowFromCenter(hole), run_time=0.5)
            rest(self, tr)

        R = RatLine(-3.4, 3.4, 2.0, y=0.0, qmax=9)
        rlab2 = text("the rational numbers", size=40).move_to(UP * 1.9)
        gone = R.by[Fr(0)]
        with self.voiceover(text=N("s09.b4")) as tr:
            self.play(FadeOut(VGroup(real, hole, rlab, nolist)), FadeIn(R), FadeIn(rlab2), run_time=0.7)
            wait_until(self, tr, "out")
            self.play(gone.animate.set_color(PRIMARY).scale(2.2), run_time=0.3)
            self.play(FadeOut(gone, scale=0.2), run_time=0.4)
            rest(self, tr)
        self.wait(0.8)
        self.play(FadeOut(VGroup(R.axis, *[d for d in R.dots if d is not gone], rlab2)), run_time=0.6)


class Thumbnail(Scene):
    def construct(self):
        g = Game(top_y=1.0, bot_y=-1.6, top_unit=1.25, bot_unit=3.9)
        curt = curtain(g, MOVES[:160], width=2.2)
        for th in curt:
            th.set_stroke(opacity=0.75)
        for ax in (g.top.axis, g.bot.axis):
            ax.set_stroke(color=FG, width=6)
        tag = text("These are the same.", size=88, weight="BOLD", color=PRIMARY).move_to(UP * 2.75)
        self.add(curt, g.top, g.bot, tag)
