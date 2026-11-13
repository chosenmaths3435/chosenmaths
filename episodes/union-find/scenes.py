"""Equality in disguise: equivalence relations and union-find.

Long-form scenes. Builders here are shared with shorts.py.
"""

import numpy as np
from manim import *
from manim_voiceover import VoiceoverScene

from mathvid import layout  # noqa: F401  must come before scene code runs
from mathvid.anim import rest, rt, wait_until
from mathvid.layout import FH, FW
from mathvid.orders import cross, tick
from mathvid.script import Script
from mathvid.style import BAD, BG, FG, GOOD, MUTED, PRIMARY, SECONDARY, TERTIARY, math, text
from mathvid.voice import get_speech_service

N = Script(__file__)

TITLE = "Equality in disguise"
CLASS_COLORS = [PRIMARY, SECONDARY, TERTIARY]
FIND_C = GOOD      # steps billed to the find
NODE_C = TERTIARY  # steps billed to the node


def freeze(scene):
    """Stop every updater on screen, so a final fade sees fixed shapes."""
    for m in scene.mobjects:
        m.clear_updaters()
        for s in m.get_family():
            s.clear_updaters()


def clear(scene, run_time=0.5):
    freeze(scene)
    if scene.mobjects:
        scene.play(FadeOut(Group(*scene.mobjects)), run_time=run_time)


# ---------------------------------------------------------------------------
# Words, rules, small pictures
# ---------------------------------------------------------------------------


def word(w, size=84, color=FG):
    return text(w, size=size, color=color)


def sort_letters(mob, w, size=84):
    """Animations that slide the glyphs of `mob` (the Text of w) into sorted order."""
    s = "".join(sorted(w))
    tgt = text(s, size=size).move_to(mob)
    used, anims = set(), []
    for i, ch in enumerate(w):
        j = next(j for j, c in enumerate(s) if c == ch and j not in used)
        used.add(j)
        anims.append(mob[i].animate(path_arc=-PI / 2.5).move_to(tgt[j]))
    return anims


def rules(size=44, sym=r"\sim"):
    """The three rules of an equivalence relation, as three rows of MathTex."""
    r1 = math(rf"x {sym} x", size=size)
    r2 = math(rf"x {sym} y", r"\ \Rightarrow\ ", rf"y {sym} x", size=size)
    r3 = math(rf"x {sym} y", r"\ \text{and}\ ", rf"y {sym} z", r"\ \Rightarrow\ ", rf"x {sym} z",
              size=size)
    return VGroup(r1, r2, r3).arrange(DOWN, buff=0.45, aligned_edge=LEFT)


def f_rules(size=40):
    r1 = math(r"f(x) = f(x)", size=size)
    r2 = math(r"f(x) = f(y)", r"\ \Rightarrow\ ", r"f(y) = f(x)", size=size)
    r3 = math(r"f(x) = f(y) = f(z)", r"\ \Rightarrow\ ", r"f(x) = f(z)", size=size)
    return VGroup(r1, r2, r3).arrange(DOWN, buff=0.45, aligned_edge=LEFT)


def loop_icon(color=PRIMARY):
    d = Dot(radius=0.09, color=color)
    a = Arc(radius=0.2, start_angle=-PI / 2 + 0.5, angle=2 * PI - 1.0, color=color, stroke_width=3)
    a.move_arc_center_to(d.get_center() + UP * 0.22)
    a.add_tip(tip_length=0.11, tip_width=0.11)
    return VGroup(a, d)


def sym_icon(color=PRIMARY):
    a, b = Dot(LEFT * 0.4, radius=0.09, color=color), Dot(RIGHT * 0.4, radius=0.09, color=color)
    arr = DoubleArrow(a.get_center(), b.get_center(), buff=0.12, stroke_width=3, color=color,
                      tip_length=0.12, max_tip_length_to_length_ratio=0.5)
    return VGroup(arr, a, b)


def trans_icon(color=PRIMARY):
    p = [LEFT * 0.45 + DOWN * 0.2, UP * 0.3, RIGHT * 0.45 + DOWN * 0.2]
    ds = VGroup(*[Dot(q, radius=0.09, color=color) for q in p])
    kw = dict(buff=0.12, stroke_width=3, tip_length=0.12, max_tip_length_to_length_ratio=0.5)
    a1 = Arrow(p[0], p[1], color=color, **kw)
    a2 = Arrow(p[1], p[2], color=color, **kw)
    a3 = Arrow(p[0], p[2], color=GOOD, **kw)
    return VGroup(a1, a2, a3, ds)


def clock(radius=0.85, hl=7):
    c = Circle(radius=radius, color=MUTED, stroke_width=3)
    ticks = VGroup()
    for h in range(1, 13):
        ang = PI / 2 - h * TAU / 12
        u = np.array([np.cos(ang), np.sin(ang), 0])
        ticks.add(Line(u * radius * 0.86, u * radius, color=MUTED, stroke_width=2))
    ang = PI / 2 - hl * TAU / 12
    u = np.array([np.cos(ang), np.sin(ang), 0])
    hand = Line(ORIGIN, u * radius * 0.7, color=PRIMARY, stroke_width=5)
    spot = Dot(u * radius, radius=0.08, color=PRIMARY)
    return VGroup(c, ticks, hand, spot)


# ---------------------------------------------------------------------------
# The projection picture: X in classes, each class landing on one point of Y
# ---------------------------------------------------------------------------


class Projection(VGroup):
    def __init__(self, scale=1.0):
        super().__init__()
        self.X = Ellipse(width=5.4, height=4.6, color=MUTED, stroke_width=3).move_to([-3.3, -0.4, 0])
        self.Y = Ellipse(width=2.4, height=4.2, color=MUTED, stroke_width=3).move_to([3.6, -0.4, 0])
        self.xl = math("X", size=48, color=MUTED).next_to(self.X, UP, buff=0.15)
        self.yl = math("Y", size=48, color=MUTED).next_to(self.Y, UP, buff=0.15)
        specs = [
            ([-3.5, 0.95], 2.6, 1.0, [(-0.8, 0.1), (-0.2, -0.15), (0.35, 0.15), (0.85, -0.1)]),
            ([-3.0, -0.35], 2.4, 1.0, [(-0.7, 0.05), (0.0, 0.15), (0.7, -0.1)]),
            ([-3.5, -1.65], 2.6, 1.0, [(-0.75, -0.05), (0.0, 0.15), (0.75, -0.1)]),
        ]
        self.classes = VGroup()
        self.dots = []
        for (c, w, h, pts), col in zip(specs, CLASS_COLORS):
            e = Ellipse(width=w, height=h, color=col, stroke_width=3).set_fill(col, 0.12).move_to([*c, 0])
            ds = VGroup(*[Dot([c[0] + x, c[1] + y, 0], radius=0.09, color=col) for x, y in pts])
            self.classes.add(VGroup(e, ds))
            self.dots.append(ds)
        self.ypts = VGroup(*[Dot([3.6, y, 0], radius=0.12, color=col)
                             for y, col in zip([0.95, -0.35, -1.65], CLASS_COLORS)])
        self.extra = Dot([3.95, 0.3, 0], radius=0.1, color=MUTED)
        self.add(self.X, self.Y, self.xl, self.yl, self.classes, self.ypts, self.extra)
        self.scale(scale)

    def arrows(self):
        g = VGroup()
        for ds, yp in zip(self.dots, self.ypts):
            for d in ds:
                g.add(CurvedArrow(d.get_center(), yp.get_center(), angle=-0.2, color=MUTED,
                                  stroke_width=2, tip_length=0.14))
        return g


# ---------------------------------------------------------------------------
# Vector space icons
# ---------------------------------------------------------------------------


def axes3(s=1.0):
    o = ORIGIN
    kw = dict(color=MUTED, stroke_width=2.5)
    return VGroup(Line(o, RIGHT * 1.2 * s, **kw), Line(o, UP * 1.1 * s, **kw),
                  Line(o, (DL * 0.75) * s, **kw), Line(o, LEFT * 0.9 * s, **kw),
                  Line(o, DOWN * 0.7 * s, **kw))


def plane_icon(label=True, size=30):
    u, v = np.array([1.3, 0.25, 0]), np.array([-0.55, -0.6, 0])
    p = Polygon(-u - v, u - v, u + v, -u + v, color=SECONDARY, stroke_width=2).set_fill(SECONDARY, 0.3)
    g = VGroup(p, axes3(), Dot(radius=0.06, color=FG))
    if label:
        g.add(text("plane through 0", size=size, color=MUTED).next_to(g, DOWN, buff=0.2))
    return g


def line_icon(label=True, size=30):
    d = np.array([1.2, 0.7, 0])
    g = VGroup(axes3(), Line(-d, d, color=SECONDARY, stroke_width=5), Dot(radius=0.06, color=FG))
    if label:
        g.add(text("line through 0", size=size, color=MUTED).next_to(g, DOWN, buff=0.2))
    return g


def space_icon(label=True, size=30):
    c = Cube(side_length=1.1, fill_opacity=0.12, fill_color=SECONDARY, stroke_color=SECONDARY,
             stroke_width=1.5)
    c.rotate(0.5, axis=UP).rotate(0.35, axis=RIGHT)
    g = VGroup(c, axes3(), Dot(radius=0.06, color=FG))
    if label:
        g.add(text("all of 3D space", size=size, color=MUTED).next_to(g, DOWN, buff=0.2))
    return g


def poly_icon(label=True, size=30):
    g = VGroup(math(r"a + b\,x", size=60))
    if label:
        g.add(text("degree at most 1", size=size, color=MUTED).next_to(g[0], DOWN, buff=0.3))
    return g


# ---------------------------------------------------------------------------
# Disjoint set forests
# ---------------------------------------------------------------------------


class Forest(VGroup):
    """A disjoint set forest: nodes with parent pointers, laid out as trees.

    parent: dict node -> parent (a root is its own parent). Change pointers with
    `reparent`, then play `moves()` to slide nodes into the new layout; the pointers are
    redrawn every frame, so they follow. Ranks are drawn next to roots (or every node with
    rank_mode="all") when `rank_on` is 1.
    """

    def __init__(self, parent, order=None, labels=True, r=0.28, dx=0.8, dy=1.05, top=2.4, cx=0.0,
                 size=26, rank=None, rank_on=0.0, rank_mode="roots", tree_gap=0.6, loops=True):
        super().__init__()
        self.parent = dict(parent)
        self.order = list(order) if order is not None else list(parent.keys())
        self.r, self.dx, self.dy, self.top, self.cx, self.tree_gap = r, dx, dy, top, cx, tree_gap
        self.rank = dict(rank) if rank else {k: 0 for k in self.order}
        self.rank_mode = rank_mode
        self.rank_on = ValueTracker(rank_on)
        self.ptr_on = ValueTracker(1.0)
        self.loops = loops
        self.ptr_color = {}
        self.nodes = {}
        for k in self.order:
            c = Circle(radius=r, color=FG, stroke_width=3).set_fill(BG, 1)
            g = VGroup(c)
            if labels:
                g.add(text(str(k), size=size).move_to(c))
            self.nodes[k] = g
        pos = self.layout()
        for k, g in self.nodes.items():
            g.move_to(pos[k])
        self._rank_cache = {}
        self.ptrs = always_redraw(self._draw_ptrs)
        self.ranks = always_redraw(self._draw_ranks)
        self.add(self.ptrs, *self.nodes.values(), self.ranks)

    # structure
    def roots(self):
        return [k for k in self.order if self.parent[k] == k]

    def children(self, k):
        return [c for c in self.order if c != k and self.parent[c] == k]

    def find_path(self, k):
        path = [k]
        while self.parent[path[-1]] != path[-1]:
            path.append(self.parent[path[-1]])
        return path

    def depth(self, k):
        return len(self.find_path(k)) - 1

    def reparent(self, k, p):
        self.parent[k] = p

    def layout(self):
        def width(k):
            ch = self.children(k)
            return max(1.0, sum(width(c) for c in ch))

        roots = self.roots()
        total = sum(width(rt_) for rt_ in roots) + self.tree_gap * (len(roots) - 1)
        pos = {}

        def place(k, x0, d):
            w = width(k)
            pos[k] = np.array([self.cx + (x0 + w / 2 - total / 2) * self.dx, self.top - d * self.dy, 0])
            x = x0
            for c in self.children(k):
                place(c, x, d + 1)
                x += width(c)

        x = 0.0
        for rt_ in roots:
            place(rt_, x, 0)
            x += width(rt_) + self.tree_gap
        return pos

    def moves(self, **kw):
        pos = self.layout()
        return [g.animate(**kw).move_to(pos[k]) for k, g in self.nodes.items()]

    def snap(self):
        pos = self.layout()
        for k, g in self.nodes.items():
            g.move_to(pos[k])

    # drawing
    def _draw_ptrs(self):
        g = VGroup()
        a = self.ptr_on.get_value()
        for k in self.order:
            node = self.nodes[k]
            col = self.ptr_color.get(k, MUTED)
            p = self.parent[k]
            if p == k:
                if not self.loops:
                    continue
                top = node.get_top()
                arc = Arc(radius=0.15, start_angle=-PI / 2 + 0.6, angle=2 * PI - 1.2, color=col,
                          stroke_width=3)
                arc.move_arc_center_to(top + UP * 0.12)
                arc.add_tip(tip_length=0.1, tip_width=0.1)
                g.add(arc)
            else:
                s, e = node.get_center(), self.nodes[p].get_center()
                if np.linalg.norm(e - s) < 2 * self.r + 0.05:
                    continue
                g.add(Arrow(s, e, buff=self.r, color=col, stroke_width=3.5, tip_length=0.17,
                            max_tip_length_to_length_ratio=0.4))
        if a < 0.999:
            g.fade(1 - a)
        return g

    def _rank_label(self, k):
        key = (k, self.rank[k])
        if key not in self._rank_cache:
            self._rank_cache[key] = math(str(self.rank[k]), size=30, color=PRIMARY)
        return self._rank_cache[key].copy()

    def _draw_ranks(self):
        g = VGroup()
        a = self.rank_on.get_value()
        if a <= 0.001:
            return g
        for k in self.order:
            if self.rank_mode == "roots" and self.parent[k] != k:
                continue
            lab = self._rank_label(k)
            lab.next_to(self.nodes[k], UR, buff=0.02)
            g.add(lab)
        if a < 0.999:
            g.fade(1 - a)
        return g

    def color_node(self, k, col):
        return self.nodes[k][0].animate.set_stroke(col)


def walk(scene, forest, start, step_time=0.35, color=PRIMARY, ring=None, counter=None):
    """Highlight the path from start to its root, node by node. Returns the path."""
    path = forest.find_path(start)
    if ring is None:
        ring = Circle(radius=forest.r + 0.1, color=color, stroke_width=6).move_to(forest.nodes[start])
        scene.play(Create(ring), forest.color_node(start, color), run_time=0.3)
    for i, k in enumerate(path[1:]):
        extra = [counter.animate.set_value(i + 1)] if counter is not None else []
        scene.play(ring.animate.move_to(forest.nodes[k]), forest.color_node(k, color), *extra,
                   run_time=step_time)
    return path, ring


def binomial(k, start=0):
    """Parent dict of the union-by-rank tree of rank k (2^k nodes). Returns (root, parent, n)."""
    if k == 0:
        return start, {start: start}, 1
    r1, p1, n1 = binomial(k - 1, start)
    r2, p2, n2 = binomial(k - 1, start + n1)
    p = {**p1, **p2}
    p[r2] = r1
    return r1, p, n1 + n2


def counter_text(label, tracker, pos, size=36, color=FG):
    lab = text(label, size=size, color=color)

    def draw():
        g = VGroup(lab.copy(), math(str(int(round(tracker.get_value()))), size=size + 6, color=PRIMARY)
                   ).arrange(RIGHT, buff=0.2)
        return g.move_to(pos)
    return always_redraw(draw)


# ---------------------------------------------------------------------------
# Ackermann and alpha
# ---------------------------------------------------------------------------


def ack_rules(size=30):
    return VGroup(math(r"A(0, n) = n + 1", size=size),
                  math(r"A(m + 1, 0) = A(m, 1)", size=size),
                  math(r"A(m + 1, n + 1) = A(m, A(m + 1, n))", size=size)
                  ).arrange(DOWN, buff=0.18, aligned_edge=LEFT)


def ack_diagonal(size=44):
    rows = VGroup(math(r"A(0, 0) = 1", size=size), math(r"A(1, 1) = 3", size=size),
                  math(r"A(2, 2) = 7", size=size), math(r"A(3, 3) = 61", size=size),
                  math(r"A(4, 4) = 2^{2^{2^{65536}}} - 3", size=size))
    rows.arrange(DOWN, buff=0.3, aligned_edge=LEFT)
    rows[4][0].set_color(PRIMARY)
    return rows


def alpha_def(size=42):
    return math(r"\alpha(n) = \text{the smallest } k \text{ with } A(k, k) \ge n", size=size)


class AlphaLine(VGroup):
    """A stretched number line of n, cut where alpha(n) steps up: 1, 2, 4, 8, 62, A(4, 4)."""

    def __init__(self, xs=(-6.3, -5.5, -4.7, -3.8, -2.6, 5.0), y=0.0, size=36, big=48):
        super().__init__()
        self.xs = xs
        cols = [MUTED, MUTED, MUTED, MUTED, PRIMARY]
        labs = ["1", "2", "4", "8", "62", "A(4, 4)"]
        self.segs, self.vals, self.ticks, self.nums = VGroup(), VGroup(), VGroup(), VGroup()
        for i in range(5):
            seg = Line([xs[i], y, 0], [xs[i + 1], y, 0], color=cols[i], stroke_width=8 if i == 4 else 5)
            self.segs.add(seg)
            v = math(str(i), size=big if i == 4 else size, color=PRIMARY if i == 4 else FG)
            v.next_to(seg, UP, buff=0.25)
            self.vals.add(v)
        for x, lab in zip(xs, labs):
            self.ticks.add(Line([x, y - 0.15, 0], [x, y + 0.15, 0], color=FG, stroke_width=3))
            self.nums.add(math(lab, size=size - 4, color=MUTED).move_to([x, y - 0.5, 0]))
        self.head = math(r"\alpha(n)", size=size + 4, color=MUTED).next_to(self.vals[0], LEFT, buff=0.3)
        self.add(self.segs, self.ticks, self.nums, self.vals)


# ---------------------------------------------------------------------------
# Rank groups (the log* argument)
# ---------------------------------------------------------------------------

GROUPS = [("0, 1", 1.1), ("2", 0.9), ("3, 4", 1.2), ("5 ... 16", 2.1), ("17 ... 65536", 3.6)]


def rank_groups(size=30, y=0.0, x0=-6.3):
    boxes = VGroup()
    x = x0
    for i, (lab, w) in enumerate(GROUPS):
        col = CLASS_COLORS[i % 3]
        r = Rectangle(width=w, height=0.8, color=col, stroke_width=3).set_fill(col, 0.15)
        r.move_to([x + w / 2, y, 0])
        t = text(lab, size=size).move_to(r)
        boxes.add(VGroup(r, t))
        x += w + 0.15
    dots = math(r"\cdots", size=40, color=MUTED).next_to(boxes, RIGHT, buff=0.25)
    return VGroup(boxes, dots)


# ---------------------------------------------------------------------------
# Scenes
# ---------------------------------------------------------------------------


class S01Hook(VoiceoverScene):
    def construct(self):
        self.set_speech_service(get_speech_service())
        a = word("listen").move_to([-3.4, 0.5, 0])
        b = word("silent").move_to([3.4, 0.5, 0])
        sim = math(r"\sim", size=96).move_to([0, 0.5, 0])
        lab = text("anagrams", size=34, color=MUTED).next_to(sim, DOWN, buff=0.5)
        eq = math("=", size=96, color=GOOD).move_to(sim)
        with self.voiceover(text=N("s01.b1")) as tr:
            self.play(FadeIn(a, shift=UP * 0.2), run_time=0.6)
            self.play(FadeIn(b, shift=UP * 0.2), run_time=0.6)
            self.play(FadeIn(sim), FadeIn(lab), run_time=0.6)
            wait_until(self, tr, "sort")
            self.play(*sort_letters(a, "listen"), *sort_letters(b, "silent"), run_time=1.6)
            self.play(Indicate(a, color=PRIMARY, scale_factor=1.05), Indicate(b, color=PRIMARY, scale_factor=1.05),
                      run_time=0.8)
            self.play(ReplacementTransform(sim, eq), FadeOut(lab), run_time=0.7)
            rest(self, tr)
        t = text(TITLE, size=64, weight="BOLD").move_to(UP * 0.3)
        with self.voiceover(text=N("s01.b2")) as tr:
            self.play(FadeOut(VGroup(a, b, eq)), run_time=0.5)
            self.play(FadeIn(t, shift=UP * 0.2), run_time=0.8)
            rest(self, tr)
        self.play(FadeOut(t), run_time=0.4)


class S02Rules(VoiceoverScene):
    def construct(self):
        self.set_speech_service(get_speech_service())
        head = text("equivalence relation", size=44, color=PRIMARY).move_to([0, 3.25, 0])
        rs = rules(size=58).move_to([0.8, 1.1, 0])
        q0 = text("a rule for \"the same\"", size=44, color=MUTED).move_to([0, 3.25, 0])
        icons = VGroup(loop_icon(), sym_icon(), trans_icon())
        for ic, r in zip(icons, rs):
            ic.next_to(r, LEFT, buff=0.7)
            ic.set_x(rs.get_left()[0] - 1.1)
        with self.voiceover(text=N("s02.b1")) as tr:
            self.play(FadeIn(q0), run_time=0.6)
            wait_until(self, tr, "refl")
            self.play(FadeIn(rs[0]), FadeIn(icons[0]), run_time=0.6)
            wait_until(self, tr, "sym")
            self.play(FadeIn(rs[1]), FadeIn(icons[1]), run_time=0.6)
            wait_until(self, tr, "trans")
            self.play(FadeIn(rs[2]), FadeIn(icons[2][:2]), FadeIn(icons[2][3]), run_time=0.6)
            self.play(GrowArrow(icons[2][2]), run_time=0.6)
            self.wait(rt(tr.get_remaining_duration() - 0.8))
            self.play(ReplacementTransform(q0, head), run_time=0.6)
            rest(self, tr)

        ex1 = VGroup(text("listen", size=38), math(r"\sim", size=44), text("silent", size=38)).arrange(RIGHT, buff=0.25)
        ck = clock(0.75)
        ckl = VGroup(text("7:00", size=34), math(r"\sim", size=40), text("19:00", size=34)).arrange(RIGHT, buff=0.2)
        ex2 = VGroup(ck, ckl).arrange(DOWN, buff=0.25)
        ex3 = math(r"\tfrac{1}{2}", r"\sim", r"\tfrac{2}{4}", size=60)
        exs = VGroup(ex1, ex2, ex3).arrange(RIGHT, buff=1.4).move_to([0, -2.3, 0])
        with self.voiceover(text=N("s02.b2")) as tr:
            self.play(FadeIn(ex1, shift=UP * 0.2), run_time=0.6)
            wait_until(self, tr, "clock")
            self.play(FadeIn(ex2, shift=UP * 0.2), run_time=0.6)
            wait_until(self, tr, "frac")
            self.play(FadeIn(ex3, shift=UP * 0.2), run_time=0.6)
            rest(self, tr)

        nl = NumberLine(x_range=[-0.5, 2.1, 0.5], length=11, color=MUTED, include_numbers=False,
                        stroke_width=3).move_to([0, -1.0, 0])
        pts = [0.0, 0.8, 1.6]
        dots = VGroup(*[Dot(nl.n2p(p), radius=0.12, color=PRIMARY) for p in pts])
        labs = VGroup(*[math(s, size=40).next_to(nl.n2p(p), DOWN, buff=0.35)
                        for s, p in zip(["0", "0.8", "1.6"], pts)])
        a1 = ArcBetweenPoints(nl.n2p(0) + UP * 0.2, nl.n2p(0.8) + UP * 0.2, angle=-PI / 2.2, color=GOOD, stroke_width=5)
        a2 = ArcBetweenPoints(nl.n2p(0.8) + UP * 0.2, nl.n2p(1.6) + UP * 0.2, angle=-PI / 2.2, color=GOOD, stroke_width=5)
        w1 = text("within 1", size=30, color=GOOD).next_to(a1, UP, buff=0.1)
        w2 = text("within 1", size=30, color=GOOD).next_to(a2, UP, buff=0.1)
        a3 = ArcBetweenPoints(nl.n2p(0) + UP * 0.2, nl.n2p(1.6) + UP * 0.2, angle=-PI / 1.5, color=BAD, stroke_width=5)
        x3 = cross(a3.point_from_proportion(0.5), s=0.25, width=8)
        close = VGroup(text("close:", size=40), text("within 1 of each other", size=40, color=MUTED)
                       ).arrange(RIGHT, buff=0.3).move_to([0, 3.0, 0])
        with self.voiceover(text=N("s02.b3")) as tr:
            freeze(self)
            self.play(FadeOut(Group(*self.mobjects)), run_time=0.5)
            self.play(Create(nl), FadeIn(dots), FadeIn(labs), run_time=0.8)
            wait_until(self, tr, "close")
            self.play(FadeIn(close), run_time=0.5)
            self.play(Create(a1), FadeIn(w1), run_time=0.7)
            self.play(Create(a2), FadeIn(w2), run_time=0.7)
            wait_until(self, tr, "fail")
            self.play(Create(a3), run_time=0.7)
            self.play(Create(x3), run_time=0.4)
            rest(self, tr)
        clear(self)


class S03Theorem(VoiceoverScene):
    def construct(self):
        self.set_speech_service(get_speech_service())
        pj = Projection()
        arrows = pj.arrows()
        fl = math("f", size=56, color=FG).move_to([0.4, 2.0, 0])
        with self.voiceover(text=N("s03.b1")) as tr:
            self.play(FadeIn(pj.X), FadeIn(pj.xl), FadeIn(pj.classes), run_time=1.0)
            self.play(FadeIn(pj.Y), FadeIn(pj.yl), FadeIn(pj.ypts), FadeIn(pj.extra), run_time=0.8)
            wait_until(self, tr, "f")
            self.play(LaggedStart(*[Create(a) for a in arrows], lag_ratio=0.08), FadeIn(fl), run_time=1.8)
            rest(self, tr)

        pic = VGroup(pj, arrows, fl)
        stmt = math(r"x \sim y", r"\iff", r"f(x) = f(y)", size=52).move_to([0, 3.2, 0])
        sub = VGroup(text("anagrams:", size=32, color=MUTED), math("f", size=40),
                     text("= sort the letters", size=32, color=MUTED)).arrange(RIGHT, buff=0.15)
        sub.move_to([0, -3.45, 0])
        with self.voiceover(text=N("s03.b2")) as tr:
            self.play(pic.animate.scale(0.82).shift(DOWN * 0.35), run_time=0.7)
            self.play(Write(stmt), run_time=1.0)
            self.play(FadeIn(sub), run_time=0.6)
            rest(self, tr)

        fr = f_rules(size=46).move_to([0.3, 0.3, 0])
        ticks = VGroup(*[tick(r).shift(LEFT * 0.2) for r in fr])
        head = text("equality follows all three rules", size=36, color=MUTED).move_to([0, 2.4, 0])
        with self.voiceover(text=N("s03.b3")) as tr:
            self.play(FadeOut(pic), FadeOut(sub), run_time=0.5)
            self.play(FadeIn(head), LaggedStart(*[FadeIn(r) for r in fr], lag_ratio=0.3), run_time=1.4)
            wait_until(self, tr, "inherit")
            self.play(LaggedStart(*[Create(t) for t in ticks], lag_ratio=0.3), run_time=1.0)
            rest(self, tr)

        pj2 = Projection().scale(0.82).shift(DOWN * 0.35)
        lab = VGroup(math(r"f(x)", size=40), text("= the class of x", size=34)).arrange(RIGHT, buff=0.15)
        lab.move_to([0.3, -3.45, 0])
        with self.voiceover(text=N("s03.b4")) as tr:
            self.play(FadeOut(VGroup(fr, ticks, head)), run_time=0.5)
            self.play(FadeIn(VGroup(pj2.X, pj2.xl, pj2.classes, pj2.Y, pj2.yl)), run_time=0.8)
            wait_until(self, tr, "class")
            self.play(FadeIn(lab), run_time=0.5)
            self.wait(rt(tr.get_remaining_duration() * 0.45))
            shrink = []
            for cl, yp in zip(pj2.classes, pj2.ypts):
                shrink.append(Transform(cl, yp.copy()))
            self.play(LaggedStart(*shrink, lag_ratio=0.25), run_time=1.6)
            rest(self, tr)
        clear(self)


class S04BetterF(VoiceoverScene):
    def construct(self):
        self.set_speech_service(get_speech_service())
        top = VGroup(math(r"f(x)", size=40), text("= the class of x", size=36),
                     text("(always works)", size=32, color=MUTED)).arrange(RIGHT, buff=0.2).move_to([0, 3.0, 0])

        def row(left, right, note):
            g = VGroup(left, math(r"\longmapsto", size=50, color=MUTED), right).arrange(RIGHT, buff=0.4)
            if note is not None:
                g.add(note.next_to(g, RIGHT, buff=0.5))
            return g

        r1 = row(text("listen", size=44), text("eilnst", size=44, color=PRIMARY), None)
        r2 = row(math("19", size=52), math("7", size=52, color=PRIMARY),
                 text("remainder after dividing by 12", size=30, color=MUTED))
        r3 = row(math(r"\tfrac{2}{4}", size=60), math("0.5", size=52, color=PRIMARY), None)
        rows_ = VGroup(r1, r2, r3).arrange(DOWN, buff=0.6, aligned_edge=LEFT).move_to([0, -0.3, 0])
        cls_words = VGroup(*[text(w, size=40) for w in ("listen", "silent", "enlist", "tinsel", "inlets")]
                           ).arrange(RIGHT, buff=0.45)
        blob = SurroundingRectangle(cls_words, buff=0.35, corner_radius=0.4, color=PRIMARY, stroke_width=3)
        blob.set_fill(PRIMARY, 0.08)
        cl_lab = text("the class of \"listen\"", size=32, color=MUTED).next_to(blob, UP, buff=0.25)
        cls = VGroup(cls_words, blob, cl_lab).move_to([0, 0.2, 0])
        with self.voiceover(text=N("s04.b1")) as tr:
            self.play(FadeIn(top), run_time=0.6)
            self.play(FadeIn(cl_lab), Create(blob), LaggedStart(*[FadeIn(w) for w in cls_words], lag_ratio=0.2),
                      run_time=1.4)
            self.wait(rt(tr.time_until_bookmark("sort") - 0.6))
            self.play(FadeOut(cls), run_time=0.5)
            wait_until(self, tr, "sort")
            self.play(FadeIn(r1, shift=RIGHT * 0.2), run_time=0.6)
            wait_until(self, tr, "rem")
            self.play(FadeIn(r2, shift=RIGHT * 0.2), run_time=0.6)
            wait_until(self, tr, "num")
            self.play(FadeIn(r3, shift=RIGHT * 0.2), run_time=0.6)
            rest(self, tr)

        pl = plane_icon().move_to([-3.6, 1.3, 0])
        po = poly_icon().move_to([3.6, 1.3, 0])
        iso = VGroup(math(r"\cong", size=64), text("isomorphic", size=30, color=MUTED)).arrange(DOWN, buff=0.15)
        iso.move_to([0, 1.5, 0])
        two_a = math("2", size=64, color=PRIMARY).move_to([-3.6, -1.6, 0])
        two_b = math("2", size=64, color=PRIMARY).move_to([3.6, -1.6, 0])
        ar_a = Arrow(pl.get_bottom(), two_a.get_top(), color=MUTED, buff=0.15)
        ar_b = Arrow(po.get_bottom() + DOWN * 0.1, two_b.get_top(), color=MUTED, buff=0.15)
        with self.voiceover(text=N("s04.b2")) as tr:
            freeze(self)
            self.play(FadeOut(VGroup(top, rows_)), run_time=0.5)
            self.play(FadeIn(pl), FadeIn(po), run_time=0.8)
            wait_until(self, tr, "iso")
            lm = DoubleArrow(pl.get_right() + RIGHT * 0.2, po.get_left() + LEFT * 0.2, color=PRIMARY, buff=0,
                             stroke_width=4, tip_length=0.2).shift(DOWN * 0.1)
            lml = text("a linear map you can undo", size=32, color=PRIMARY).move_to([lm.get_x(), 2.75, 0])
            corr = math(r"(a, b) \ \leftrightarrow\ a + b\,x", size=36, color=MUTED).next_to(lm, DOWN, buff=0.3)
            self.play(GrowFromCenter(lm), FadeIn(lml), run_time=0.7)
            self.play(FadeIn(corr), run_time=0.6)
            self.wait(rt(tr.time_until_bookmark("dim") * 0.55))
            self.play(FadeOut(VGroup(lm, lml, corr)), FadeIn(iso), run_time=0.6)
            wait_until(self, tr, "dim")
            self.play(GrowArrow(ar_a), GrowArrow(ar_b), FadeIn(two_a), FadeIn(two_b), run_time=0.8)
            # more spaces drop in
            left = VGroup(pl, ar_a, two_a)
            right = VGroup(po, ar_b, two_b)
            ln = line_icon().scale(0.85)
            sp = space_icon().scale(0.85)
            one = math("1", size=64, color=PRIMARY)
            three = math("3", size=64, color=PRIMARY)
            self.play(left.animate.scale(0.85).move_to([-2.2, 0.0, 0]),
                      right.animate.scale(0.85).move_to([2.2, 0.0, 0]),
                      FadeOut(iso[1]), iso[0].animate.move_to([0, 0.9, 0]), run_time=0.8)
            ln.move_to([-5.7, 0.0, 0]).align_to(pl, UP)
            sp.move_to([5.7, 0.0, 0]).align_to(pl, UP)
            one.move_to([ln.get_x(), two_a.get_y(), 0])
            three.move_to([sp.get_x(), two_a.get_y(), 0])
            ar1 = Arrow(ln.get_bottom(), one.get_top(), color=MUTED, buff=0.15)
            ar3 = Arrow(sp.get_bottom(), three.get_top(), color=MUTED, buff=0.15)
            self.play(FadeIn(ln), FadeIn(sp), GrowArrow(ar1), GrowArrow(ar3), FadeIn(one), FadeIn(three),
                      run_time=0.9)
            fd = VGroup(math("f", size=48), text("= dimension", size=40)).arrange(RIGHT, buff=0.2)
            fd.move_to([0, 3.2, 0])
            self.play(FadeIn(fd), run_time=0.6)
            wait_until(self, tr, "one")
            self.play(*[Indicate(m, color=PRIMARY) for m in (one, two_a, two_b, three)], run_time=1.0)
            rest(self, tr)
        clear(self)


# items for the computing scenes
POS10 = {i: np.array([0.4 + 1.35 * (i % 5), 1.0 if i < 5 else -1.0, 0]) for i in range(10)}


def item_dots(size=30, r=0.32):
    g = {}
    for i in range(10):
        c = Circle(radius=r, color=FG, stroke_width=3).set_fill(BG, 1)
        g[i] = VGroup(c, text(str(i), size=size).move_to(c)).move_to(POS10[i])
    return g


class S05Computing(VoiceoverScene):
    def construct(self):
        self.set_speech_service(get_speech_service())
        dots = item_dots()
        dg = VGroup(*dots.values())
        facts = [(1, 4), (4, 7), (2, 9)]
        fact_t = VGroup(*[math(rf"{a} \sim {b}", size=44) for a, b in facts]).arrange(DOWN, buff=0.35)
        fact_t.move_to([-4.6, 0.6, 0])
        fhead = text("facts", size=32, color=MUTED).next_to(fact_t, UP, buff=0.4)
        edges = VGroup(*[Line(dots[a].get_center(), dots[b].get_center(), color=SECONDARY, stroke_width=5)
                         for a, b in facts])
        q = math(r"1 \sim 7\ ?", size=48, color=PRIMARY).move_to([-4.6, -2.3, 0])
        with self.voiceover(text=N("s05.b1")) as tr:
            self.play(FadeIn(dg), run_time=0.8)
            wait_until(self, tr, "facts")
            self.play(FadeIn(fhead), run_time=0.3)
            for t, e in zip(fact_t, edges):
                self.add_foreground_mobjects(dg)
                self.play(FadeIn(t, shift=RIGHT * 0.2), Create(e), run_time=0.6)
            wait_until(self, tr, "ask")
            self.play(FadeIn(q), run_time=0.5)
            self.play(edges[0].animate.set_color(PRIMARY), edges[1].animate.set_color(PRIMARY),
                      *[dots[k][0].animate.set_stroke(PRIMARY) for k in (1, 4, 7)], run_time=0.8)
            rest(self, tr)

        rep = {1: 4, 4: 4, 7: 4, 2: 9, 9: 9}
        labs = VGroup(*[text(str(rep.get(i, i)), size=28, color=MUTED).next_to(dots[i], UP, buff=0.15)
                        for i in range(10)])
        crowns = VGroup(*[Circle(radius=0.42, color=GOOD, stroke_width=4).move_to(dots[i])
                          for i in range(10) if rep.get(i, i) == i])
        q2 = math(r"f(1) = f(7)\ ?", size=44, color=PRIMARY).move_to(q)
        q3 = math(r"4 = 4", size=48, color=GOOD).move_to(q)
        with self.voiceover(text=N("s05.b2")) as tr:
            self.play(edges[0].animate.set_color(SECONDARY), edges[1].animate.set_color(SECONDARY),
                      *[dots[k][0].animate.set_stroke(FG) for k in (1, 4, 7)], run_time=0.4)
            wait_until(self, tr, "rep")
            self.play(Create(crowns), run_time=0.7)
            self.play(FadeIn(labs), run_time=0.7)
            wait_until(self, tr, "eq")
            self.play(TransformMatchingShapes(q, q2), run_time=0.7)
            self.play(Indicate(labs[1], color=PRIMARY), Indicate(labs[7], color=PRIMARY), run_time=0.8)
            self.play(TransformMatchingShapes(q2, q3), run_time=0.6)
            rest(self, tr)

        f4 = math(r"7 \sim 2", size=44, color=PRIMARY).next_to(fact_t, DOWN, buff=0.35)
        e4 = Line(dots[7].get_center(), dots[2].get_center(), color=PRIMARY, stroke_width=5)
        new2 = text("4", size=28, color=PRIMARY).move_to(labs[2])
        new9 = text("4", size=28, color=PRIMARY).move_to(labs[9])
        crown9 = [c for c in crowns if np.allclose(c.get_center(), dots[9].get_center())][0]
        with self.voiceover(text=N("s05.b3")) as tr:
            self.play(FadeOut(q3), FadeIn(f4, shift=RIGHT * 0.2), Create(e4), run_time=0.8)
            self.play(Transform(labs[2], new2), Transform(labs[9], new9), FadeOut(crown9), run_time=0.8)
            rest(self, tr)
        clear(self)


class S06Table(VoiceoverScene):
    def construct(self):
        self.set_speech_service(get_speech_service())
        rep = {1: 4, 4: 4, 7: 4, 2: 9, 9: 9}
        boxes = VGroup()
        vals = {}
        for i in range(10):
            b = Square(side_length=1.0, color=MUTED, stroke_width=3).move_to([-5.4 + 1.2 * i, 0.3, 0])
            idx = text(str(i), size=28, color=MUTED).next_to(b, DOWN, buff=0.2)
            v = math(str(rep.get(i, i)), size=48).move_to(b)
            vals[i] = v
            boxes.add(VGroup(b, idx, v))
        head = VGroup(text("item", size=30, color=MUTED), text("representative", size=30, color=MUTED))
        head[0].next_to(boxes, DOWN, buff=0.75).align_to(boxes, LEFT)
        head[1].next_to(boxes, UP, buff=0.3).align_to(boxes, LEFT)
        cnt = ValueTracker(0)
        ctr = counter_text("rewrites:", cnt, [3.6, -2.7, 0])
        with self.voiceover(text=N("s06.b1")) as tr:
            self.play(LaggedStart(*[FadeIn(b) for b in boxes], lag_ratio=0.06), FadeIn(head), run_time=1.2)
            wait_until(self, tr, "lookup")
            self.play(boxes[7][0].animate.set_stroke(PRIMARY, width=6), Indicate(vals[7], color=PRIMARY), run_time=0.8)
            self.play(boxes[7][0].animate.set_stroke(MUTED, width=3), run_time=0.3)
            wait_until(self, tr, "merge")
            m = text("merge {1, 4, 7} with {2, 9}", size=34, color=PRIMARY).move_to([-2.3, -2.7, 0])
            self.play(FadeIn(m), FadeIn(ctr), run_time=0.5)
            for n, i in enumerate((1, 4, 7)):
                nv = math("9", size=48, color=PRIMARY).move_to(vals[i])
                self.play(Transform(vals[i], nv), boxes[i][0].animate.set_stroke(PRIMARY), cnt.animate.set_value(n + 1),
                          run_time=0.45)
            big = text("with n items: up to n rewrites per merge", size=34, color=BAD).move_to([0, 2.7, 0])
            self.play(FadeIn(big), run_time=0.6)
            rest(self, tr)
        clear(self)


class S07Forest(VoiceoverScene):
    def construct(self):
        self.set_speech_service(get_speech_service())
        parent = {i: i for i in range(10)}
        parent.update({1: 4, 7: 1, 2: 9})
        order = [0, 3, 4, 1, 7, 5, 6, 8, 9, 2]
        fo = Forest(parent, order=order, top=1.9, dx=1.2, dy=1.35, cx=0.0, r=0.38, size=34)
        fo.ptr_on.set_value(0.0)
        with self.voiceover(text=N("s07.b1")) as tr:
            self.add(fo)
            self.play(FadeIn(VGroup(*fo.nodes.values())), run_time=0.7)
            wait_until(self, tr, "ptr")
            self.play(fo.ptr_on.animate.set_value(1.0), run_time=1.0)
            self.play(*[Circumscribe(fo.nodes[k], shape=Circle, color=GOOD, buff=0.08) for k in fo.roots()], run_time=1.0)
            name = text("disjoint set forest", size=40, color=PRIMARY).move_to([0, -3.2, 0])
            self.wait(rt(tr.get_remaining_duration() - 1.4))
            self.play(FadeIn(name), run_time=0.6)
            rest(self, tr)

        with self.voiceover(text=N("s07.b2")) as tr:
            self.play(FadeOut(name), run_time=0.3)
            lab = VGroup(text("find(7)", size=36, color=PRIMARY)).move_to([0, -3.2, 0])
            self.play(FadeIn(lab), run_time=0.3)
            wait_until(self, tr, "find")
            path, ring = walk(self, fo, 7, step_time=0.5)
            self.wait(0.3)
            lab2 = text("merge the groups of 7 and 2", size=36, color=PRIMARY).move_to(lab)
            self.play(FadeOut(ring), *[fo.color_node(k, FG) for k in path], Transform(lab, lab2), run_time=0.5)
            ring2 = Circle(radius=fo.r + 0.1, color=SECONDARY, stroke_width=6).move_to(fo.nodes[2])
            self.play(Create(ring2), run_time=0.3)
            self.play(ring2.animate.move_to(fo.nodes[9]), run_time=0.4)
            ring4 = Circle(radius=fo.r + 0.1, color=PRIMARY, stroke_width=6).move_to(fo.nodes[4])
            self.play(Create(ring4), run_time=0.3)
            wait_until(self, tr, "union")
            fo.ptr_color[9] = PRIMARY
            fo.reparent(9, 4)
            self.play(*fo.moves(), ring2.animate.move_to(fo.layout()[9]), ring4.animate.move_to(fo.layout()[4]),
                      run_time=1.0)
            self.play(FadeOut(ring2), FadeOut(ring4), run_time=0.4)
            rest(self, tr)

        n = 9
        cp = {i: i for i in range(n)}
        chain = Forest(cp, order=list(range(n)), labels=False, r=0.22, dx=1.1, dy=0.76, top=3.3, cx=0.0,
                       tree_gap=0.3)
        cnt = ValueTracker(0)
        ctr = counter_text("steps:", cnt, [4.6, -2.8, 0])
        with self.voiceover(text=N("s07.b3")) as tr:
            freeze(self)
            self.play(FadeOut(Group(*self.mobjects)), run_time=0.4)
            self.add(chain)
            self.play(FadeIn(VGroup(*chain.nodes.values())), run_time=0.4)
            wait_until(self, tr, "chain")
            for i in range(n - 1):
                chain.reparent(i, i + 1)
                self.play(*chain.moves(), run_time=0.3)
            self.play(FadeIn(ctr), run_time=0.3)
            walk(self, chain, 0, step_time=0.3, counter=cnt)
            rest(self, tr)
        clear(self)


class S08Rank(VoiceoverScene):
    def construct(self):
        self.set_speech_service(get_speech_service())
        _, p2, n2 = binomial(2, 0)
        _, p1, n1 = binomial(1, n2)
        parent = {**p2, **p1}
        rank = {k: 0 for k in parent}
        rank[0], rank[n2] = 2, 1
        fo = Forest(parent, labels=False, r=0.3, dx=1.1, dy=1.2, top=1.8, rank=rank, rank_on=1.0,
                    tree_gap=1.5)
        rl = text("rank = height", size=32, color=MUTED).move_to([0, 3.0, 0])
        with self.voiceover(text=N("s08.b1")) as tr:
            self.add(fo)
            self.play(FadeIn(fo), run_time=0.6)
            self.play(FadeIn(rl), run_time=0.5)
            wait_until(self, tr, "short")
            fo.ptr_color[n2] = PRIMARY
            fo.reparent(n2, 0)
            self.play(*fo.moves(), run_time=1.0)
            same = text("height stays 2", size=32, color=GOOD).move_to([0, -2.6, 0])
            self.play(FadeIn(same), run_time=0.4)
            wait_until(self, tr, "tie")
            freeze(self)
            self.play(FadeOut(fo), FadeOut(same), run_time=0.4)
            _, a, na = binomial(2, 0)
            _, b, nb = binomial(2, na)
            pr = {**a, **b}
            rk = {k: 0 for k in pr}
            rk[0], rk[na] = 2, 2
            f2 = Forest(pr, labels=False, r=0.3, dx=1.0, dy=1.2, top=1.8, rank=rk, rank_on=1.0, tree_gap=1.5)
            self.add(f2)
            self.play(FadeIn(f2), run_time=0.4)
            f2.ptr_color[na] = PRIMARY
            f2.reparent(na, 0)
            self.play(*f2.moves(), run_time=1.0)
            f2.rank[0] = 3
            up = text("equal ranks: rank goes up by one", size=32, color=PRIMARY).move_to([0, -2.6, 0])
            self.play(FadeIn(up), f2.nodes[0][0].animate.set_stroke(PRIMARY, width=6), run_time=0.8)
            rest(self, tr)

        trees = []
        xs = [-5.9, -3.9, -1.3, 3.5]
        for k, x in zip(range(4), xs):
            _, pk, nk = binomial(k, 0)
            rk = {i: 0 for i in pk}
            rk[0] = k
            t = Forest(pk, labels=False, r=0.22, dx=0.75, dy=0.9, top=2.2, cx=x, rank=rk, rank_on=1.0, loops=False)
            trees.append(t)
        cnts = VGroup(*[text(f"at least {2 ** k}", size=30).move_to([x, -2.0, 0]) for k, x in zip(range(4), xs)])
        nodes_l = text("nodes", size=30, color=MUTED).next_to(cnts, DOWN, buff=0.25)
        with self.voiceover(text=N("s08.b2")) as tr:
            freeze(self)
            self.play(FadeOut(Group(*self.mobjects)), run_time=0.4)
            for t in trees:
                self.add(t)
            self.play(*[FadeIn(t) for t in trees], run_time=0.8)
            wait_until(self, tr, "nodes")
            self.play(LaggedStart(*[FadeIn(c) for c in cnts], lag_ratio=0.25), FadeIn(nodes_l), run_time=1.2)
            wait_until(self, tr, "double")
            t3 = trees[3]
            half = [k for k in t3.order if 4 <= k < 8]
            self.play(*[t3.nodes[k][0].animate.set_stroke(SECONDARY) for k in half],
                      *[t3.nodes[k][0].animate.set_stroke(PRIMARY) for k in t3.order if k < 4], run_time=0.8)
            plus = math(r"4 + 4 = 8", size=44, color=PRIMARY).next_to(nodes_l, DOWN, buff=0.3).set_x(3.5)
            self.play(FadeIn(plus), run_time=0.5)
            rest(self, tr)

        l1 = VGroup(math(r"n", size=52), text("items", size=40), math(r"\Rightarrow", size=52),
                    text("height at most", size=40), math(r"\log_2 n", size=52)).arrange(RIGHT, buff=0.3)
        l2 = VGroup(math(r"n = 1{,}000{,}000", size=52), math(r"\Rightarrow", size=52),
                    text("at most 20 steps", size=40, color=PRIMARY)).arrange(RIGHT, buff=0.3)
        VGroup(l1, l2).arrange(DOWN, buff=0.8).move_to(ORIGIN)
        with self.voiceover(text=N("s08.b3")) as tr:
            freeze(self)
            self.play(FadeOut(Group(*self.mobjects)), run_time=0.4)
            wait_until(self, tr, "log")
            self.play(FadeIn(l1, shift=UP * 0.2), run_time=0.8)
            wait_until(self, tr, "million")
            self.play(FadeIn(l2, shift=UP * 0.2), run_time=0.8)
            rest(self, tr)
        clear(self)


def tall_tree():
    """A tree of height 5: the path 0 <- 1 <- 2 <- 3 <- 4 <- 5, with side leaves 6..9."""
    parent = {0: 0, 1: 0, 2: 1, 3: 2, 4: 3, 5: 4, 6: 0, 7: 1, 8: 2, 9: 3}
    order = [0, 6, 1, 7, 2, 8, 3, 9, 4, 5]
    return parent, order


class S09Compress(VoiceoverScene):
    def construct(self):
        self.set_speech_service(get_speech_service())
        parent, order = tall_tree()
        rank = {k: 0 for k in parent}
        rank[0] = 5
        fo = Forest(parent, order=order, labels=False, r=0.24, dx=0.85, dy=1.0, top=2.9, rank=rank, rank_on=0.0)
        with self.voiceover(text=N("s09.b1")) as tr:
            self.add(fo)
            self.play(FadeIn(fo), run_time=0.6)
            path, ring = walk(self, fo, 5, step_time=0.4)
            wait_until(self, tr, "knows")
            tags = VGroup(*[text("root", size=24, color=PRIMARY).next_to(fo.nodes[k], RIGHT, buff=0.1)
                            for k in path[:-1]])
            self.play(LaggedStart(*[FadeIn(t) for t in tags], lag_ratio=0.15), run_time=0.8)
            self.wait(rt(tr.get_remaining_duration() - 0.7))
            self.play(FadeOut(tags), run_time=0.6)
            rest(self, tr)

        lab = text("path compression", size=40, color=PRIMARY).move_to([4.2, 2.9, 0])
        with self.voiceover(text=N("s09.b2")) as tr:
            wait_until(self, tr, "flat")
            for k in path[:-1]:
                if fo.parent[k] != 0:
                    fo.ptr_color[k] = PRIMARY
                fo.reparent(k, 0)
            self.play(*fo.moves(), ring.animate.move_to(fo.layout()[0]), run_time=1.2)
            self.play(FadeIn(lab), run_time=0.5)
            self.play(FadeOut(ring), *[fo.color_node(k, FG) for k in path], run_time=0.4)
            path2, ring2 = walk(self, fo, 5, step_time=0.5, color=SECONDARY)
            one = text("one step", size=32, color=SECONDARY).next_to(fo.nodes[5], DOWN, buff=0.2)
            self.play(FadeIn(one), run_time=0.4)
            rest(self, tr)

        # slider
        y = -3.0
        bar = Line([-4.6, y, 0], [4.6, y, 0], color=MUTED, stroke_width=4)
        star = Forest({0: 0, 1: 0, 2: 0, 3: 0}, labels=False, r=0.12, dx=0.35, dy=0.5, top=0, loops=False)
        star.move_to([-5.9, y + 0.15, 0])
        ch = Forest({0: 0, 1: 0, 2: 1, 3: 2}, labels=False, r=0.12, dx=0.35, dy=0.33, top=0, loops=False)
        ch.move_to([5.9, y + 0.15, 0])
        tl = text("fast finds, slow merges", size=30, color=MUTED).next_to(bar.get_start(), UP, buff=0.35).shift(RIGHT * 1.2)
        tr_ = text("fast merges, slow finds", size=30, color=MUTED).next_to(bar.get_end(), UP, buff=0.35).shift(LEFT * 1.2)
        marker = Triangle(color=PRIMARY, fill_opacity=1).scale(0.16).rotate(PI).move_to([1.2, y + 0.25, 0])
        with self.voiceover(text=N("s09.b3")) as tr:
            freeze(self)
            self.play(FadeOut(VGroup(lab, one, ring2)), *[fo.color_node(k, FG) for k in path2], run_time=0.4)
            fo2 = Forest(dict(fo.parent), order=order, labels=False, r=0.22, dx=0.8, dy=0.95, top=2.7)
            self.remove(fo)
            self.add(fo2)
            self.play(FadeIn(bar), run_time=0.4)
            wait_until(self, tr, "table")
            self.add(star)
            self.play(FadeIn(star), FadeIn(tl), run_time=0.6)
            wait_until(self, tr, "chainend")
            self.add(ch)
            self.play(FadeIn(ch), FadeIn(tr_), FadeIn(marker), run_time=0.6)
            p3, r3 = walk(self, fo2, 9, step_time=0.35)
            for k in p3[:-1]:
                fo2.reparent(k, 0)
            self.play(*fo2.moves(), r3.animate.move_to(fo2.layout()[0]), marker.animate.shift(LEFT * 1.6),
                      run_time=1.0)
            self.play(FadeOut(r3), *[fo2.color_node(k, FG) for k in p3], run_time=0.3)
            p4, r4 = walk(self, fo2, 8, step_time=0.35)
            for k in p4[:-1]:
                fo2.reparent(k, 0)
            self.play(*fo2.moves(), r4.animate.move_to(fo2.layout()[0]), marker.animate.shift(LEFT * 1.4),
                      run_time=1.0)
            self.play(FadeOut(r4), *[fo2.color_node(k, FG) for k in p4], run_time=0.3)
            rest(self, tr)

        with self.voiceover(text=N("s09.b4")) as tr:
            freeze(self)
            self.play(FadeOut(VGroup(bar, star, ch, tl, tr_, marker)), run_time=0.4)
            fo3 = Forest(dict(fo2.parent), order=order, labels=False, r=0.24, dx=0.85, dy=1.0, top=2.0,
                         rank={**{k: 0 for k in order}, 0: 5}, rank_on=1.0)
            self.remove(fo2)
            self.add(fo3)
            wait_until(self, tr, "rank")
            rk = VGroup(text("rank", size=34, color=PRIMARY), math("5", size=40, color=PRIMARY)).arrange(RIGHT, buff=0.15)
            hb = VGroup(text("height", size=34, color=SECONDARY), math("2", size=40, color=SECONDARY)).arrange(RIGHT, buff=0.15)
            VGroup(rk, hb).arrange(DOWN, buff=0.3, aligned_edge=LEFT).move_to([4.6, 1.2, 0])
            br = BraceBetweenPoints(fo3.nodes[0].get_top() + RIGHT * 0.1, fo3.nodes[5].get_bottom(), direction=RIGHT)
            self.play(FadeIn(rk), run_time=0.8)
            self.play(FadeIn(hb), run_time=0.6)
            ge = math(r"\text{rank} \ \ge\ \text{height}", size=44).move_to([0, -2.9, 0])
            self.play(FadeIn(ge), run_time=0.6)
            rest(self, tr)
        clear(self)


class S10Alpha(VoiceoverScene):
    def construct(self):
        self.set_speech_service(get_speech_service())
        s1 = text("m operations on n items:", size=40)
        s2 = VGroup(text("time at most proportional to", size=40), math(r"m \cdot \alpha(n)", size=52, color=PRIMARY)
                    ).arrange(RIGHT, buff=0.3)
        s3 = VGroup(math(r"\alpha", size=52, color=PRIMARY), text("= the inverse Ackermann function", size=40)
                    ).arrange(RIGHT, buff=0.2)
        s0 = text("union by rank + path compression", size=36, color=MUTED)
        stmt = VGroup(s0, s1, s2, s3).arrange(DOWN, buff=0.5).move_to(UP * 0.1)
        with self.voiceover(text=N("s10.b1")) as tr:
            self.play(FadeIn(s0), run_time=0.6)
            self.play(FadeIn(s1), run_time=0.6)
            wait_until(self, tr, "bound")
            self.play(FadeIn(s2, shift=UP * 0.2), run_time=0.8)
            self.wait(rt(tr.get_remaining_duration() - 1.4))
            self.play(FadeIn(s3, shift=UP * 0.2), run_time=0.7)
            rest(self, tr)

        ar = ack_rules(size=38).move_to([-3.7, 1.4, 0])
        arh = text("Ackermann's function", size=32, color=MUTED).next_to(ar, UP, buff=0.3).align_to(ar, LEFT)
        diag = ack_diagonal(size=46).move_to([2.9, -0.3, 0])
        with self.voiceover(text=N("s10.b2")) as tr:
            self.play(FadeOut(stmt), run_time=0.5)
            self.play(FadeIn(arh), FadeIn(ar), run_time=0.8)
            self.play(FadeIn(diag[0]), run_time=0.4)
            self.play(FadeIn(diag[1]), run_time=0.4)
            self.play(FadeIn(diag[2]), run_time=0.4)
            wait_until(self, tr, "a33")
            self.play(FadeIn(diag[3]), run_time=0.5)
            wait_until(self, tr, "a44")
            self.play(FadeIn(diag[4], scale=1.2), run_time=0.8)
            rest(self, tr)

        df = alpha_def(size=44).move_to([0, 2.9, 0])
        al = AlphaLine(y=0.0)
        atoms_x = al.xs[4] + 0.55
        atoms = VGroup(Line([atoms_x, -0.15, 0], [atoms_x, 0.15, 0], color=SECONDARY, stroke_width=3),
                       VGroup(math(r"10^{80}", size=34, color=SECONDARY),
                              text("atoms in the universe", size=30, color=SECONDARY)).arrange(DOWN, buff=0.1))
        atoms[1].move_to([atoms_x + 1.6, -1.7, 0])
        lead = Line(atoms[1].get_top(), [atoms_x, -0.2, 0], color=SECONDARY, stroke_width=2)
        with self.voiceover(text=N("s10.b3")) as tr:
            freeze(self)
            self.play(FadeOut(VGroup(ar, arh, diag)), run_time=0.5)
            self.play(Write(df), run_time=1.2)
            wait_until(self, tr, "reach")
            self.play(Create(al.segs[:4]), FadeIn(al.ticks[:5]), FadeIn(al.nums[:5]), run_time=1.0)
            self.play(LaggedStart(*[FadeIn(v) for v in al.vals[:4]], lag_ratio=0.3), run_time=1.0)
            self.play(Create(al.segs[4]), FadeIn(al.ticks[5]), FadeIn(al.nums[5]), run_time=1.6)
            self.play(FadeIn(al.vals[4], scale=1.4), run_time=0.6)
            self.play(FadeIn(atoms), Create(lead), run_time=0.7)
            wait_until(self, tr, "four")
            self.play(Indicate(al.vals[4], color=PRIMARY, scale_factor=1.5), run_time=1.0)
            rest(self, tr)

        more = Line([al.xs[5], 0.0, 0], [FW / 2 + 0.5, 0.0, 0], color=BAD, stroke_width=6)
        five = math("5", size=40, color=BAD).next_to(more, UP, buff=0.25)
        dots_ = math(r"6,\ 7,\ \ldots", size=38, color=BAD).move_to([6.0, 0.9, 0])
        inf = math(r"\alpha(n) \to \infty", size=48, color=BAD).move_to([0, -2.9, 0])
        slow = text("absurdly slowly", size=34, color=MUTED).next_to(inf, RIGHT, buff=0.5)
        with self.voiceover(text=N("s10.b4")) as tr:
            self.play(Create(more), FadeIn(five), run_time=0.8)
            self.play(FadeIn(dots_), run_time=0.4)
            self.play(Write(inf), run_time=0.8)
            wait_until(self, tr, "slow")
            self.play(FadeIn(slow), run_time=0.5)
            rest(self, tr)
        clear(self)


def chain_with_ranks(ranks, x=0.0, bottom=-2.9, dy=1.0, r=0.3, size=30):
    """A vertical path of nodes, bottom to top, with each node's rank written inside."""
    nodes = VGroup()
    for i, k in enumerate(ranks):
        c = Circle(radius=r, color=FG, stroke_width=3).set_fill(BG, 1).move_to([x, bottom + i * dy, 0])
        nodes.add(VGroup(c, math(str(k), size=size).move_to(c)))
    arrows = VGroup(*[Arrow(nodes[i].get_center(), nodes[i + 1].get_center(), buff=r, color=MUTED, stroke_width=3.5,
                            tip_length=0.17) for i in range(len(ranks) - 1)])
    return nodes, arrows


def group_of(k):
    for i, (lo, hi) in enumerate([(0, 1), (2, 2), (3, 4), (5, 16), (17, 65536)]):
        if lo <= k <= hi:
            return i
    return 5


GROUP_NAMES = ["0, 1", "2", "3, 4", "5 ... 16", "17 ... 65536"]


class S11WhyFast(VoiceoverScene):
    def construct(self):
        self.set_speech_service(get_speech_service())
        cred = text("Hopcroft and Ullman, 1973:", size=32, color=MUTED)
        credm = math(r"m \log^* n", size=40, color=MUTED)
        cr = VGroup(cred, credm).arrange(RIGHT, buff=0.25).move_to([0, 3.3, 0])
        nodes, arrows = chain_with_ranks([0, 1, 3, 4], x=-2.0, bottom=-2.2, dy=1.3)
        lab = math(r"0 < 1 < 3 < 4", size=48, color=PRIMARY).move_to([2.8, -0.3, 0])
        rk = text("ranks going up a path", size=32, color=MUTED).next_to(lab, UP, buff=0.3)
        two = text("two facts about ranks", size=40, color=PRIMARY).move_to([0, 1.2, 0])
        with self.voiceover(text=N("s11.b1")) as tr:
            self.play(FadeIn(cr), run_time=0.6)
            self.wait(rt(tr.time_until_bookmark("up") - 2.2))
            self.play(FadeIn(two), run_time=0.5)
            self.wait(0.6)
            self.play(FadeOut(two), run_time=0.4)
            self.play(FadeIn(nodes), FadeIn(arrows), run_time=0.8)
            self.play(FadeIn(rk), Write(lab), run_time=0.9)
            rest(self, tr)

        tris = VGroup()
        for x in (-4.0, 0.0, 4.0):
            top = Circle(radius=0.3, color=PRIMARY, stroke_width=3).set_fill(BG, 1).move_to([x, 1.3, 0])
            tl = math("r", size=34, color=PRIMARY).move_to(top)
            tri = Polygon([x, 1.0, 0], [x - 1.4, -1.4, 0], [x + 1.4, -1.4, 0], color=SECONDARY, stroke_width=3)
            tri.set_fill(SECONDARY, 0.15)
            inside = math(r"\ge 2^r", size=36).move_to([x, -0.6, 0])
            tris.add(VGroup(tri, top, tl, inside))
        claim = VGroup(text("at most", size=38), math(r"n / 2^r", size=48, color=PRIMARY),
                       text("nodes ever have rank r", size=38)).arrange(RIGHT, buff=0.25).move_to([0, -2.6, 0])
        with self.voiceover(text=N("s11.b2")) as tr:
            self.play(FadeOut(VGroup(nodes, arrows, lab, rk)), run_time=0.5)
            self.play(LaggedStart(*[FadeIn(t) for t in tris], lag_ratio=0.25), run_time=1.2)
            wait_until(self, tr, "rare")
            self.play(FadeIn(claim, shift=UP * 0.2), run_time=0.8)
            rest(self, tr)

        rg = rank_groups(size=30, y=0.6)
        rgh = text("ranks, in groups", size=32, color=MUTED).next_to(rg, UP, buff=0.4).align_to(rg, LEFT)
        ls = VGroup(text("number of groups: about", size=36), math(r"\log^* n", size=48, color=PRIMARY)
                    ).arrange(RIGHT, buff=0.25).move_to([0, -1.3, 0])
        lsd = text("how many times you take log2 to get down to 1", size=30, color=MUTED).next_to(ls, DOWN, buff=0.3)
        with self.voiceover(text=N("s11.b3")) as tr:
            self.play(FadeOut(VGroup(tris, claim)), run_time=0.5)
            self.play(FadeIn(rgh), run_time=0.3)
            self.play(LaggedStart(*[FadeIn(b, shift=RIGHT * 0.2) for b in rg[0]], lag_ratio=0.5), run_time=3.0)
            self.play(FadeIn(rg[1]), run_time=0.3)
            wait_until(self, tr, "logstar")
            self.play(FadeIn(ls), run_time=0.6)
            self.play(FadeIn(lsd), run_time=0.5)
            rest(self, tr)

        ranks = [1, 3, 4, 7, 9, 18, 20]
        nodes, arrows = chain_with_ranks(ranks, x=-1.6, bottom=-3.1, dy=1.02, r=0.3, size=28)
        glabs = VGroup(*[text("group " + GROUP_NAMES[group_of(k)], size=28, color=MUTED).next_to(nodes[i], LEFT, buff=0.4)
                         for i, k in enumerate(ranks)])
        kinds = []
        for i in range(len(ranks) - 1):
            cross_ = group_of(ranks[i]) != group_of(ranks[i + 1]) or i + 1 == len(ranks) - 1
            kinds.append(cross_)
        leg = VGroup(VGroup(Line(ORIGIN, RIGHT * 0.6, color=FIND_C, stroke_width=8), text("billed to the find", size=32)
                            ).arrange(RIGHT, buff=0.25),
                     VGroup(Line(ORIGIN, RIGHT * 0.6, color=NODE_C, stroke_width=8), text("billed to the node", size=32)
                            ).arrange(RIGHT, buff=0.25)).arrange(DOWN, buff=0.4, aligned_edge=LEFT).move_to([3.9, 0.6, 0])
        rl = text("root", size=26, color=MUTED).next_to(nodes[-1], RIGHT, buff=0.3)
        with self.voiceover(text=N("s11.b4")) as tr:
            freeze(self)
            self.play(FadeOut(VGroup(rg, rgh, ls, lsd, cr)), run_time=0.4)
            self.play(FadeIn(nodes), FadeIn(arrows), FadeIn(glabs), FadeIn(rl), run_time=0.8)
            wait_until(self, tr, "cross")
            self.play(FadeIn(leg[0]), *[arrows[i].animate.set_color(FIND_C) for i, c in enumerate(kinds) if c],
                      run_time=0.8)
            wait_until(self, tr, "node")
            self.play(FadeIn(leg[1]), *[arrows[i].animate.set_color(NODE_C) for i, c in enumerate(kinds) if not c],
                      run_time=0.8)
            rest(self, tr)

        # one node in the group 5..16, its parent's rank climbing
        frozen = VGroup(text("a node's rank is frozen once it stops being a root", size=32, color=MUTED),
                        text("its parent's rank only goes up", size=32, color=MUTED)).arrange(DOWN, buff=0.15)
        frozen.move_to([0, 3.2, 0])
        ax = NumberLine(x_range=[4, 19, 1], length=5.6, rotation=PI / 2, color=MUTED, include_numbers=False,
                        stroke_width=3).move_to([2.6, -0.45, 0])
        band = Rectangle(width=1.2, height=ax.n2p(16.5)[1] - ax.n2p(4.5)[1], color=PRIMARY, stroke_width=2)
        band.set_fill(PRIMARY, 0.12).move_to([2.6, (ax.n2p(16.5)[1] + ax.n2p(4.5)[1]) / 2, 0])
        bandl = text("group 5 ... 16", size=32, color=PRIMARY).next_to(band, RIGHT, buff=0.3)
        nums = VGroup(*[math(str(v), size=30, color=MUTED).next_to(ax.n2p(v), LEFT, buff=0.2) for v in (5, 8, 11, 14, 17)])
        x = Circle(radius=0.32, color=FG, stroke_width=3).set_fill(BG, 1).move_to([-2.4, ax.n2p(7)[1], 0])
        xl = math("7", size=30).move_to(x)
        xn = VGroup(x, xl)
        par = Dot(ax.n2p(8), radius=0.14, color=SECONDARY)
        ptr = always_redraw(lambda: Arrow(xn.get_center(), par.get_center(), buff=0.35, color=NODE_C, stroke_width=4,
                                          tip_length=0.2))
        pl = text("parent's rank", size=30, color=SECONDARY).next_to(ax, DOWN, buff=0.25)
        bills = ValueTracker(0)
        bc = counter_text("bills:", bills, [-2.6, 0.9, 0], size=36)
        with self.voiceover(text=N("s11.b5")) as tr:
            freeze(self)
            self.play(FadeOut(VGroup(nodes, arrows, glabs, leg, rl)), run_time=0.4)
            self.play(FadeIn(frozen), run_time=0.6)
            self.play(Create(ax), FadeIn(band), FadeIn(bandl), FadeIn(nums), FadeIn(xn), FadeIn(par), FadeIn(pl),
                      run_time=0.8)
            self.add(ptr)
            self.play(FadeIn(bc), run_time=0.3)
            wait_until(self, tr, "newparent")
            for i, v in enumerate((11, 14)):
                self.play(par.animate.move_to(ax.n2p(v)), bills.animate.set_value(i + 1), run_time=0.7)
            wait_until(self, tr, "leaves")
            self.play(par.animate.move_to(ax.n2p(17)).set_color(FIND_C), bills.animate.set_value(3), run_time=0.8)
            never = text("never billed again", size=32, color=FIND_C).next_to(bc, DOWN, buff=0.35)
            self.play(FadeIn(never), run_time=0.5)
            rest(self, tr)

        l1 = math(r"\frac{n}{32} + \frac{n}{64} + \cdots + \frac{n}{2^{16}} \ <\ \frac{n}{16}", size=48)
        l1n = text("nodes in the group", size=30, color=MUTED)
        l2 = math(r"\frac{n}{16} \times 16 \ =\ n", size=52, color=PRIMARY)
        l2n = text("bills for the whole group, at most", size=30, color=MUTED)
        blk = VGroup(VGroup(l1, l1n).arrange(DOWN, buff=0.25), VGroup(l2, l2n).arrange(DOWN, buff=0.25)
                     ).arrange(DOWN, buff=0.7).move_to(ORIGIN)
        with self.voiceover(text=N("s11.b6")) as tr:
            freeze(self)
            self.play(FadeOut(Group(*self.mobjects)), run_time=0.4)
            self.play(FadeIn(l1[0]), run_time=1.0)
            wait_until(self, tr, "few")
            self.play(FadeIn(l1n), Indicate(l1[0], color=PRIMARY, scale_factor=1.05), run_time=0.8)
            wait_until(self, tr, "n")
            self.play(FadeIn(l2), FadeIn(l2n), run_time=0.8)
            rest(self, tr)

        t1 = VGroup(text("finds:", size=36, color=FIND_C), math(r"m\,(\log^* n + 1)", size=46)).arrange(RIGHT, buff=0.3)
        t2 = VGroup(text("groups:", size=36, color=NODE_C), math(r"n \log^* n", size=46)).arrange(RIGHT, buff=0.3)
        t3 = VGroup(math(r"n \le m", size=40, color=MUTED), math(r"\Rightarrow", size=44),
                    text("time proportional to", size=36), math(r"m \log^* n", size=50, color=PRIMARY)
                    ).arrange(RIGHT, buff=0.3)
        tot = VGroup(t1, t2, t3).arrange(DOWN, buff=0.6).move_to(ORIGIN)
        with self.voiceover(text=N("s11.b7")) as tr:
            self.play(FadeOut(VGroup(l1, l1n, l2, l2n)), run_time=0.4)
            self.play(FadeIn(t1), run_time=0.6)
            self.play(FadeIn(t2), run_time=0.6)
            wait_until(self, tr, "total")
            self.play(FadeIn(t3, shift=UP * 0.2), run_time=0.8)
            rest(self, tr)
        clear(self)


class S12TrueAnswer(VoiceoverScene):
    def construct(self):
        self.set_speech_service(get_speech_service())
        rg = rank_groups(size=30, y=0.6)
        ends = text("ends: towers of twos", size=34, color=MUTED).next_to(rg, DOWN, buff=0.5)
        ends2 = text("ends: the Ackermann function", size=34, color=PRIMARY).move_to(ends)
        tj = VGroup(text("Tarjan, 1975:", size=40), math(r"m \cdot \alpha(n)", size=50, color=PRIMARY)
                    ).arrange(RIGHT, buff=0.3).move_to([0, 3.0, 0])
        with self.voiceover(text=N("s12.b1")) as tr:
            self.play(FadeIn(rg), FadeIn(ends), run_time=0.8)
            self.play(FadeIn(tj), run_time=0.6)
            wait_until(self, tr, "levels")
            self.play(Transform(ends, ends2), *[b[0].animate.set_stroke(PRIMARY).set_fill(PRIMARY, 0.15) for b in rg[0]],
                      run_time=1.0)
            rest(self, tr)

        a1 = text("Tarjan: some sequences really take this long", size=36)
        a2 = text("Fredman and Saks, 1989:", size=36)
        a3 = text("no union-find structure beats it by more than a constant factor", size=34)
        a4 = VGroup(math(r"\alpha(n)", size=52, color=PRIMARY), text("is the true answer", size=40)).arrange(RIGHT, buff=0.3)
        a5 = text("(even on a computer that only pays for reading and writing memory)", size=28, color=MUTED)
        blk = VGroup(a1, VGroup(a2, a3, a5).arrange(DOWN, buff=0.2), a4).arrange(DOWN, buff=0.6).move_to(DOWN * 0.2)
        model = a5
        blk[1].remove(a5)
        tk = tick(a4, s=1.6)
        with self.voiceover(text=N("s12.b2")) as tr:
            freeze(self)
            self.play(FadeOut(VGroup(rg, ends)), tj.animate.scale(0.8).move_to([0, 3.3, 0]), run_time=0.6)
            nw = text("not a weak spot in the proof", size=38, color=MUTED).move_to(a1)
            self.play(FadeIn(nw), run_time=0.6)
            wait_until(self, tr, "slow")
            self.play(ReplacementTransform(nw, a1), run_time=0.6)
            wait_until(self, tr, "any")
            self.play(FadeIn(blk[1], shift=UP * 0.2), run_time=0.6)
            self.wait(1.2)
            self.play(FadeIn(model), run_time=0.6)
            self.wait(rt(tr.get_remaining_duration() - 1.4))
            self.play(FadeIn(a4), Create(tk), run_time=0.8)
            rest(self, tr)
        clear(self)


def pentagon_graph(center, radius=1.4, star=False, color=FG):
    pts = [center + radius * np.array([np.cos(PI / 2 + k * TAU / 5), np.sin(PI / 2 + k * TAU / 5), 0])
           for k in range(5)]
    step = 2 if star else 1
    edges = VGroup(*[Line(pts[k], pts[(k + step) % 5], color=MUTED, stroke_width=4) for k in range(5)])
    dots = VGroup(*[Dot(p, radius=0.13, color=color) for p in pts])
    return VGroup(edges, dots)


class S13Ending(VoiceoverScene):
    def construct(self):
        self.set_speech_service(get_speech_service())
        parent = {0: 0, 1: 0, 2: 0, 3: 1, 4: 4, 5: 4, 6: 6}
        fo = Forest(parent, labels=False, r=0.2, dx=0.7, dy=0.85, top=1.4, cx=-3.6)
        fl = VGroup(math("f", size=44), text("= representative", size=34)).arrange(RIGHT, buff=0.15).move_to([-3.6, -1.6, 0])
        pl = plane_icon(label=False).scale(0.9).move_to([2.6, 1.0, 0])
        po = poly_icon(label=False).scale(0.8).move_to([5.0, 1.0, 0])
        two = math("2", size=56, color=PRIMARY).move_to([3.8, -0.6, 0])
        a1 = Arrow(pl.get_bottom(), two.get_top(), color=MUTED, buff=0.1)
        a2 = Arrow(po.get_bottom(), two.get_top(), color=MUTED, buff=0.1)
        dl = VGroup(math("f", size=44), text("= dimension", size=34)).arrange(RIGHT, buff=0.15).move_to([3.8, -1.6, 0])
        heads = VGroup(text("union-find: make it fast", size=32, color=MUTED).move_to([-3.6, 3.0, 0]),
                       text("math: find a good one", size=32, color=MUTED).move_to([3.8, 3.0, 0]))
        with self.voiceover(text=N("s13.b1")) as tr:
            self.add(fo)
            self.play(FadeIn(fo), FadeIn(fl), FadeIn(heads[0]), run_time=0.8)
            self.wait(rt(tr.get_remaining_duration() * 0.45))
            self.play(FadeIn(pl), FadeIn(po), GrowArrow(a1), GrowArrow(a2), FadeIn(two), FadeIn(dl), FadeIn(heads[1]),
                      run_time=1.0)
            rest(self, tr)

        g1 = pentagon_graph(np.array([-3.0, -0.1, 0]))
        g2 = pentagon_graph(np.array([3.0, -0.1, 0]), star=True, color=SECONDARY)
        q = text("same graph?", size=40).move_to([0, 2.5, 0])
        fq = math(r"f = \ ?", size=56, color=PRIMARY).move_to([0, -0.1, 0])
        with self.voiceover(text=N("s13.b2")) as tr:
            freeze(self)
            self.play(FadeOut(Group(*self.mobjects)), run_time=0.5)
            self.play(Create(g1), Create(g2), run_time=1.2)
            self.play(FadeIn(q), run_time=0.5)
            wait_until(self, tr, "open")
            self.play(FadeIn(fq, scale=1.2), run_time=0.7)
            rest(self, tr)
        self.wait(0.6)
        clear(self, run_time=0.8)


class Thumbnail(Scene):
    def construct(self):
        a = text("listen", size=96).move_to([-3.6, 1.6, 0])
        b = text("silent", size=96).move_to([-3.6, -0.2, 0])
        arr = Arrow([-1.2, 0.7, 0], [0.6, 0.7, 0], color=MUTED, stroke_width=8)
        c = text("eilnst", size=96, color=PRIMARY).move_to([3.2, 0.7, 0])
        t = text("Every \"same\" is an equals in disguise", size=52, weight="BOLD").move_to([0, -2.6, 0])
        self.add(a, b, arr, c, t)
