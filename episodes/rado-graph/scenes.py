"""There's only one random graph. Long-form scenes."""

from math import cos, sin, sqrt

import numpy as np
from manim import *
from manim_voiceover import VoiceoverScene

from mathvid import layout  # noqa: F401  must come before scene code runs
from mathvid.anim import rest, rt, wait_until
from mathvid.layout import FH, FW
from mathvid.orders import cross, tick
from mathvid.script import Script
from mathvid.style import (BAD, BG, FG, GOOD, MUTED, PRIMARY, SECONDARY, TERTIARY, math, text,
                           title_card)
from mathvid.voice import get_speech_service

N = Script(__file__)

TITLE = "The random graph"
EDGE = MUTED
THREAD = PRIMARY
MATCHED = SECONDARY

ERDOS = "Erd\u0151s"
RENYI = "R\u00e9nyi"


# ---------------------------------------------------------------------------
# Graph helpers (also used by shorts.py)
# ---------------------------------------------------------------------------


def key(i, j):
    return (i, j) if i < j else (j, i)


def cloud_points(n, center=ORIGIN, rx=2.5, ry=2.5, seed=0, min_d=0.6):
    """n points spread over an ellipse, no two closer than min_d."""
    rng = np.random.default_rng(seed)
    c = np.array(center, dtype=float)
    pts = []
    for _ in range(60000):
        if len(pts) >= n:
            break
        a = rng.uniform(0, TAU)
        r = sqrt(rng.uniform(0.0, 1.0))
        p = c + np.array([rx * r * cos(a), ry * r * sin(a), 0])
        if all(np.linalg.norm(p - q) >= min_d for q in pts):
            pts.append(p)
    return pts


def rim_points(n, center, rx, ry, seed=0, phase=0.0):
    """Points on an ellipse around a cloud: the dots that are 'still coming'."""
    rng = np.random.default_rng(seed)
    c = np.array(center, dtype=float)
    out = []
    for k in range(n):
        a = phase + TAU * k / n + rng.uniform(-0.25, 0.25)
        f = rng.uniform(0.92, 1.05)
        out.append(c + np.array([rx * f * cos(a), ry * f * sin(a), 0]))
    return out


def ring_points(n, center=ORIGIN, radius=2.0, start=PI / 2):
    c = np.array(center, dtype=float)
    return [c + radius * np.array([cos(start - TAU * i / n), sin(start - TAU * i / n), 0]) for i in range(n)]


def coin_edges(n, seed, p=0.5, start=0):
    """Fair coin for every pair among dots start..n-1 (and pairs with earlier dots)."""
    rng = np.random.default_rng(seed)
    return {(i, j) for j in range(n) for i in range(j) if j >= start and rng.random() < p}


def bit_edges(n):
    """The binary recipe: k < m are joined when bit k of m is 1."""
    return {(k, m) for m in range(n) for k in range(m) if (m >> k) & 1}


PALEY_Q = {1, 3, 4, 9, 10, 12}  # the nonzero squares mod 13


def paley_edges(n=13, flip=False):
    return {(i, j) for i in range(n) for j in range(i + 1, n) if (((j - i) % n) in PALEY_Q) != flip}


class Net(VGroup):
    """Dots and lines. Lines are kept per pair so scenes can light up single edges."""

    def __init__(self, pts, edges=(), r=0.11, color=FG, ecolor=EDGE, ewidth=2.5, eopacity=0.8,
                 labels=False, label_size=22, label_center=None, label_buff=0.3, label_color=MUTED):
        super().__init__()
        self.pts = [np.array(p, dtype=float) for p in pts]
        self.edges = {key(*e) for e in edges}
        self.ecolor, self.ewidth, self.eopacity = ecolor, ewidth, eopacity
        self.ds = VGroup(*[Dot(p, radius=r, color=color) for p in self.pts])
        self.ls = {}
        self.lg = VGroup()
        for e in sorted(self.edges):
            ln = self.make_line(*e)
            self.ls[e] = ln
            self.lg.add(ln)
        self.add(self.lg, self.ds)
        self.lab = VGroup()
        self.label_buff = label_buff
        self.label_c = np.array(label_center if label_center is not None else np.mean(self.pts, axis=0), dtype=float)
        if labels:
            c = self.label_c
            for i, p in enumerate(self.pts):
                d = p - c
                d = d / (np.linalg.norm(d) + 1e-9)
                self.lab.add(text(str(i), size=label_size, color=label_color).move_to(p + d * label_buff))
            self.add(self.lab)

    def make_line(self, i, j, color=None, width=None, opacity=None, dashed=False):
        a, b = self.ds[i].get_center(), self.ds[j].get_center()
        cls = DashedLine if dashed else Line
        kw = dict(dash_length=0.12) if dashed else {}
        return cls(a, b, color=color or self.ecolor, stroke_width=width or self.ewidth,
                   stroke_opacity=self.eopacity if opacity is None else opacity, **kw)

    def adj(self, i, j):
        return key(i, j) in self.edges

    def line(self, i, j):
        return self.ls[key(i, j)]

    def hide_lines(self):
        for ln in self.ls.values():
            ln.set_stroke(opacity=0)
        return self

    def follow(self):
        """Lines and labels track their dots while the dots move."""
        for (i, j), ln in self.ls.items():
            ln.add_updater(lambda m, a=self.ds[i], b=self.ds[j]: m.put_start_and_end_on(a.get_center(), b.get_center()))
        def place(m, d):
            v = d.get_center() - self.label_c
            v = v / (np.linalg.norm(v) + 1e-9)
            m.move_to(d.get_center() + v * self.label_buff)

        for i, lb in enumerate(self.lab):
            lb.add_updater(lambda m, d=self.ds[i]: place(m, d))
        return self

    def unfollow(self):
        for m in list(self.ls.values()) + list(self.lab):
            m.clear_updaters()
        return self


def face_mob(face, r):
    return text(face, size=int(r * 100), color=PRIMARY, weight="BOLD")


def coin(face="H", r=0.32):
    disc = Circle(radius=r, color=PRIMARY, stroke_width=4).set_fill(BG, 1)
    g = VGroup(disc, face_mob(face, r).move_to(disc))
    g.face, g.r = face, r
    return g


def flip(scene, cn, face, run_time=0.4, extra=()):
    """Flip a coin onto the given face (a squash and stretch)."""
    h = rt(run_time / 2)
    scene.play(cn.animate.stretch(0.06, 1), run_time=h)
    cn[1].become(face_mob(face, cn.r).move_to(cn[0]).stretch(0.06, 1))
    scene.play(cn.animate.stretch(1 / 0.06, 1), *extra, run_time=h)
    cn.face = face


def fill_anim(net, pairs, cn=None, lines=True):
    """One coin flip per pair, revealing each heads pair's line as its flip lands."""
    pairs = [key(*p) for p in pairs]
    faces = ["H" if p in net.edges else "T" for p in pairs]
    mobs = [net.ls[p] for p in pairs if p in net.edges] if lines else []
    target = net.eopacity
    group = VGroup(*mobs) if cn is None else VGroup(cn, *mobs)
    state = {"k": -1}
    H = face_mob("H", cn.r) if cn is not None else None
    T = face_mob("T", cn.r) if cn is not None else None

    def upd(m, a):
        k = min(len(pairs) - 1, int(a * len(pairs)))
        while state["k"] < k:
            state["k"] += 1
            p = pairs[state["k"]]
            if p in net.edges and lines:
                net.ls[p].set_stroke(opacity=target)
            if cn is not None:
                cn[1].become((H if faces[state["k"]] == "H" else T).copy().move_to(cn[0]))

    return UpdateFromAlphaFunc(group, upd)


def ring_around(mob, color=PRIMARY, r=0.24, width=4):
    return Circle(radius=r, color=color, stroke_width=width).move_to(mob)


def bubble(lines, size=30, width=None, colors=None):
    """A rounded box of text lines: a wish, a rule, a card."""
    rows = VGroup(*[text(s, size=size, color=(colors[i] if colors else FG)) for i, s in enumerate(lines)])
    rows.arrange(DOWN, buff=0.14)
    box = SurroundingRectangle(rows, color=MUTED, buff=0.3, corner_radius=0.2, stroke_width=3)
    box.set_fill(BG, 0.92)
    return VGroup(box, rows)


def wish_bubble(size=30):
    t1 = text("wish: a new dot,", size=size)
    t2 = VGroup(text("joined to every", size=size), text("green", size=size, color=GOOD, weight="BOLD")).arrange(RIGHT, buff=0.14)
    t3 = VGroup(text("and to no", size=size), text("red", size=size, color=BAD, weight="BOLD")).arrange(RIGHT, buff=0.14)
    for t in (t2, t3):
        t[1].align_to(t[0], DOWN)
    rows = VGroup(t1, t2, t3).arrange(DOWN, buff=0.14, aligned_edge=LEFT)
    box = SurroundingRectangle(rows, color=MUTED, buff=0.3, corner_radius=0.2, stroke_width=3)
    box.set_fill(BG, 0.92)
    return VGroup(box, rows)


# ---------------------------------------------------------------------------
# The matching game (s04, short1)
# ---------------------------------------------------------------------------


def simulate(sigma, inv, n):
    """Back-and-forth with the true partner. Turns are (side, picked, partner); side 0 is mine."""
    mg, mh, turns, side = {}, {}, [], 0
    while len(mg) < n:
        if side == 0:
            free = [g for g in range(n) if g not in mg]
            if free:
                g = free[0]
                mg[g], mh[sigma[g]] = sigma[g], g
                turns.append((0, g, sigma[g]))
        else:
            free = [h for h in range(n) if h not in mh]
            if free:
                h = free[0]
                mg[inv[h]], mh[h] = h, inv[h]
                turns.append((1, h, inv[h]))
        side ^= 1
    return turns


def matching_setup(n=10, seed=12):
    """Two random graphs that are secretly the same graph, renamed by sigma."""
    rng = np.random.default_rng(1000 + seed)
    E = {(i, j) for i in range(n) for j in range(i + 1, n) if rng.random() < 0.5}
    sigma = [0] + [int(x) for x in rng.permutation(n - 1) + 1]
    inv = [0] * n
    for g, h in enumerate(sigma):
        inv[h] = g
    HE = {key(sigma[i], sigma[j]) for i, j in E}
    return E, HE, sigma, inv, simulate(sigma, inv, n)


class Game:
    """Two graphs side by side; threads join matched dots."""

    def __init__(self, centers=((-3.4, 0.4, 0), (3.4, 0.4, 0)), radius=1.9, n=10, r=0.12,
                 label_size=24, titles=("mine", "yours"), title_size=36, start=PI / 2):
        E, HE, self.sigma, self.inv, self.turns = matching_setup(n)
        self.n = n
        self.nets = [Net(ring_points(n, c, radius, start=start), es, r=r, ewidth=2.5, eopacity=0.6,
                         labels=True, label_size=label_size, label_center=c, label_buff=0.36)
                     for c, es in zip(centers, (E, HE))]
        self.titles = VGroup()
        if titles:
            for net, t, c in zip(self.nets, titles, centers):
                self.titles.add(text(t, size=title_size, color=MUTED).move_to(np.array(c) + UP * (radius + 0.85)))
        self.threads = VGroup()
        self.matched = [dict(), dict()]  # side -> {dot: partner}
        self.step_i = 0

    def base(self):
        return VGroup(*self.nets, self.titles)

    def dot(self, side, i):
        return self.nets[side].ds[i]

    def thread(self, side, a, b, width=3):
        p, q = self.dot(side, a).get_center(), self.dot(1 - side, b).get_center()
        return Line(p, q, color=THREAD, stroke_width=width, stroke_opacity=0.8)

    def dim_threads(self):
        return [t.animate.set_stroke(opacity=0.35, width=2) for t in self.threads]

    def record(self, side, a, b):
        self.matched[side][a] = b
        self.matched[1 - side][b] = a

    def colors_for(self, side, a):
        """Matched dots on `side`, colored by how dot a connects to them."""
        net = self.nets[side]
        return {m: (GOOD if net.adj(a, m) else BAD) for m in self.matched[side]}

    def full_step(self, scene, tr, turn, marks=None, budget=None):
        """One turn, narrated: pick, color, carry, grant, thread."""
        side, a, b = turn
        other = 1 - side
        A, B = self.nets[side], self.nets[other]
        cols = self.colors_for(side, a)
        pick_ring = ring_around(A.ds[a])
        hl_a, hl_b = VGroup(), VGroup()
        for m, c in cols.items():
            if c == GOOD:
                hl_a.add(A.make_line(a, m, color=GOOD, width=5, opacity=1))
            else:
                hl_a.add(A.make_line(a, m, color=BAD, width=3, opacity=0.9, dashed=True))
        recolor_a = [A.ds[m].animate.set_color(c).scale(1.35) for m, c in cols.items()]
        if marks and "pick" in marks:
            wait_until(scene, tr, marks["pick"])
        scene.play(Create(pick_ring), A.lab[a].animate.set_color(PRIMARY), run_time=0.5)
        if cols:
            scene.play(Create(hl_a), *recolor_a, run_time=0.7)
        if marks and "carry" in marks:
            wait_until(scene, tr, marks["carry"])
        # Carry each color across its thread.
        if cols:
            travellers = VGroup()
            moves = []
            for m, c in cols.items():
                d = Dot(A.ds[m].get_center(), radius=0.1, color=c)
                travellers.add(d)
                moves.append(d.animate.move_to(B.ds[self.matched[side][m]].get_center()))
            scene.add(travellers)
            scene.play(*moves, run_time=0.8)
            scene.remove(travellers)
            scene.play(*[B.ds[self.matched[side][m]].animate.set_color(c).scale(1.35) for m, c in cols.items()],
                       run_time=0.3)
        if marks and "grant" in marks:
            wait_until(scene, tr, marks["grant"])
        hl_b = VGroup()
        for m, c in cols.items():
            pm = self.matched[side][m]
            if c == GOOD:
                hl_b.add(B.make_line(b, pm, color=GOOD, width=5, opacity=1))
            else:
                hl_b.add(B.make_line(b, pm, color=BAD, width=3, opacity=0.9, dashed=True))
        win_ring = ring_around(B.ds[b], color=PRIMARY)
        scene.play(Create(win_ring), B.lab[b].animate.set_color(PRIMARY), Create(hl_b), run_time=0.6)
        th = self.thread(side, a, b)
        scene.play(Create(th), *self.dim_threads(), run_time=0.6)
        self.threads.add(th)
        self.record(side, a, b)
        # Settle: matched dots go back to the matched color.
        settle = []
        for m in cols:
            settle += [A.ds[m].animate.set_color(MATCHED).scale(1 / 1.35),
                       B.ds[self.matched[side][m]].animate.set_color(MATCHED).scale(1 / 1.35)]
        settle += [A.ds[a].animate.set_color(MATCHED), B.ds[b].animate.set_color(MATCHED),
                   A.lab[a].animate.set_color(MUTED), B.lab[b].animate.set_color(MUTED)]
        scene.play(FadeOut(VGroup(pick_ring, win_ring, hl_a, hl_b)), *settle, run_time=0.5)

    def quick_step(self, scene, turn, run_time=0.6):
        side, a, b = turn
        th = self.thread(side, a, b)
        A, B = self.nets[side], self.nets[1 - side]
        scene.play(Flash(A.ds[a], color=PRIMARY, line_length=0.15, flash_radius=0.25),
                   Create(th), A.ds[a].animate.set_color(MATCHED), B.ds[b].animate.set_color(MATCHED),
                   *self.dim_threads(), run_time=rt(run_time))
        self.threads.add(th)
        self.record(side, a, b)

    def instant(self, turns):
        for side, a, b in turns:
            self.threads.add(self.thread(side, a, b))
            self.record(side, a, b)
            self.nets[side].ds[a].set_color(MATCHED)
            self.nets[1 - side].ds[b].set_color(MATCHED)
        return self.threads


# ---------------------------------------------------------------------------
# s01 Hook
# ---------------------------------------------------------------------------

HOOK_C = [(-3.6, -0.55, 0), (3.6, -0.55, 0)]


def hook_net(side, n0=7, extra=7, seed=0):
    c = HOOK_C[side]
    core = cloud_points(n0, c, 2.0, 1.75, seed=3 + side * 7, min_d=1.0)
    rim = rim_points(extra, c, 2.7, 2.5, seed=5 + side, phase=0.3 + side)
    pts = core + rim
    n = len(pts)
    edges = coin_edges(n, seed=11 + side * 13)
    net = Net(pts, edges, r=0.12, ewidth=2.5, eopacity=0.75)
    for k in range(n0, n):
        net.ds[k].set_opacity(0.0)
    return net, n0


def pair_order(n_lo, n_hi, seed):
    pairs = [(i, j) for j in range(n_hi) for i in range(j) if j >= n_lo]
    rng = np.random.default_rng(seed)
    rng.shuffle(pairs)
    return [tuple(p) for p in pairs]


class S01Hook(VoiceoverScene):
    def construct(self):
        self.set_speech_service(get_speech_service())
        A, n0 = hook_net(0)
        B, _ = hook_net(1)
        A.hide_lines()
        B.hide_lines()
        cA = coin("H", r=0.38).move_to([-3.6, 3.3, 0])
        cB = coin("H", r=0.38).move_to([3.6, 3.3, 0])
        core_pairs = pair_order(0, n0, seed=2)
        hp = next(p for p in core_pairs if key(*p) in A.edges)
        tp = next(p for p in core_pairs if key(*p) not in A.edges)
        rest_a = [p for p in core_pairs if p not in (hp, tp)]

        with self.voiceover(text=N("s01.b1")) as tr:
            self.add(A.lg)
            self.play(FadeIn(VGroup(*A.ds[:n0]), lag_ratio=0.1), FadeIn(cA), run_time=0.8)
            wait_until(self, tr, "heads")
            flip(self, cA, "H", run_time=0.4)
            A.line(*hp).set_stroke(opacity=A.eopacity)
            self.play(Create(A.line(*hp)), run_time=0.4)
            wait_until(self, tr, "tails")
            flip(self, cA, "T", run_time=0.4)
            ghost = DashedLine(A.ds[tp[0]].get_center(), A.ds[tp[1]].get_center(), color=BAD,
                               stroke_width=3, dash_length=0.12)
            self.play(Create(ghost), run_time=0.3)
            self.play(FadeOut(ghost), run_time=0.3)
            self.play(fill_anim(A, rest_a[:8], cA), run_time=rt(tr.get_remaining_duration()))

        with self.voiceover(text=N("s01.b2")) as tr:
            t = tr.time_until_bookmark("you")
            self.play(fill_anim(A, rest_a[8:], cA), run_time=rt(t))
            self.add(B.lg)
            self.play(FadeIn(VGroup(*B.ds[:n0]), lag_ratio=0.1), FadeIn(cB), run_time=0.6)
            self.play(fill_anim(B, pair_order(0, n0, seed=9), cB), run_time=rt(tr.get_remaining_duration()))

        dots_a = text("...", size=60, color=MUTED).move_to([-6.75, -0.55, 0])
        dots_b = text("...", size=60, color=MUTED).move_to([6.75, -0.55, 0])
        eq = math("=", size=140, color=PRIMARY).move_to([0, -0.55, 0])
        grow_a = pair_order(n0, len(A.pts), seed=4)
        grow_b = pair_order(n0, len(B.pts), seed=5)
        with self.voiceover(text=N("s01.b3")) as tr:
            t = tr.time_until_bookmark("same")
            rims = [A.ds[k].animate.set_opacity(0.55) for k in range(n0, len(A.pts))]
            rims += [B.ds[k].animate.set_opacity(0.55) for k in range(n0, len(B.pts))]
            self.play(*rims, FadeIn(dots_a), FadeIn(dots_b), run_time=0.5)
            self.play(fill_anim(A, grow_a, cA), fill_anim(B, grow_b, cB), run_time=rt(t - 0.7))
            wait_until(self, tr, "same")
            self.play(FadeIn(eq, scale=1.5), run_time=0.5)
            rest(self, tr)
        self.play(FadeOut(VGroup(A, B, cA, cB, dots_a, dots_b, eq)), run_time=0.5)
        title_card(self, TITLE)


# ---------------------------------------------------------------------------
# s02 What "same" means
# ---------------------------------------------------------------------------


class S02Same(VoiceoverScene):
    def construct(self):
        self.set_speech_service(get_speech_service())
        cl, cr = np.array([-3.4, -0.3, 0]), np.array([3.4, -0.3, 0])
        R = 1.85
        pent = Net(ring_points(5, cl, R), [(k, (k + 1) % 5) for k in range(5)], r=0.13, ewidth=4,
                   eopacity=1, ecolor=FG, labels=True, label_size=30, label_center=cl, label_buff=0.42)
        star = Net(ring_points(5, cr, R), [(k, (k + 2) % 5) for k in range(5)], r=0.13, ewidth=4,
                   eopacity=1, ecolor=FG, labels=True, label_size=30, label_center=cr, label_buff=0.42)
        head = text("graph = dots + lines", size=40).move_to(UP * 3.2)
        with self.voiceover(text=N("s02.b1")) as tr:
            self.play(FadeIn(head), run_time=0.6)
            self.play(FadeIn(pent), FadeIn(star), run_time=1.0)
            rest(self, tr)

        targets = ring_points(5, cr, R)
        star.follow()
        same = text("the same graph, renamed", size=36, color=PRIMARY).move_to(DOWN * 3.3)
        with self.voiceover(text=N("s02.b2")) as tr:
            wait_until(self, tr, "slide")
            self.play(*[star.ds[i].animate.move_to(targets[(2 * i) % 5]) for i in range(5)],
                      run_time=1.6, path_arc=0.0)
            star.unfollow()
            # Flash each left line with its partner on the right.
            per = max(0.35, min(0.6, (tr.get_remaining_duration() - 1.2) / 5))
            for k in range(5):
                a, b = k, (k + 1) % 5
                ia, ib = (3 * a) % 5, (3 * b) % 5  # right dots now sitting at positions a, b
                self.play(pent.line(a, b).animate(rate_func=there_and_back).set_color(PRIMARY).set_stroke(width=8),
                          star.line(ia, ib).animate(rate_func=there_and_back).set_color(PRIMARY).set_stroke(width=8),
                          run_time=per)
            self.play(FadeIn(same), run_time=0.5)
            rest(self, tr)

        # Two coin-flip graphs on five dots.
        lp = cloud_points(5, [-3.4, -0.2, 0], 1.9, 1.7, seed=21, min_d=1.3)
        rp = cloud_points(5, [3.4, -0.2, 0], 1.9, 1.7, seed=22, min_d=1.3)
        L = Net(lp, [(0, 1), (1, 2), (0, 2), (2, 3), (3, 4)], r=0.13, ewidth=4, eopacity=1, ecolor=FG)
        Rn = Net(rp, [(0, 1), (1, 2), (2, 3), (3, 4), (0, 4)], r=0.13, ewidth=4, eopacity=1, ecolor=FG)
        tri = Polygon(lp[0], lp[1], lp[2], stroke_width=0, fill_color=PRIMARY, fill_opacity=0.35)
        tri_lines = VGroup(L.line(0, 1), L.line(1, 2), L.line(0, 2))
        tag = text("no triangle", size=32, color=MUTED).next_to(Rn, DOWN, 0.5)
        tag_l = text("triangle", size=32, color=PRIMARY).next_to(L, DOWN, 0.5)
        tag_l.align_to(tag, DOWN)
        with self.voiceover(text=N("s02.b3")) as tr:
            self.play(FadeOut(VGroup(pent, star, head, same)), run_time=0.5)
            self.play(FadeIn(L.ds), FadeIn(Rn.ds), run_time=0.4)
            t = tr.time_until_bookmark("tri")
            self.play(Create(L.lg, lag_ratio=0.3), Create(Rn.lg, lag_ratio=0.3), run_time=rt(min(1.6, t - 0.1)))
            wait_until(self, tr, "tri")
            self.play(FadeIn(tri), tri_lines.animate.set_color(PRIMARY), FadeIn(tag_l), run_time=0.6)
            self.play(FadeIn(tag), run_time=0.5)
            rest(self, tr)

        c1 = text("10 dots", size=38)
        c2 = text("45 pairs", size=38)
        c3 = VGroup(math(r"2^{45}", size=46, color=PRIMARY),
                    text("= about 35 trillion ways", size=38, color=PRIMARY)).arrange(RIGHT, buff=0.2)
        counter = VGroup(c1, c2, c3).arrange(RIGHT, buff=0.8).move_to(UP * 3.1)
        g1 = Net(cloud_points(10, [-3.5, -0.8, 0], 2.4, 2.1, seed=31, min_d=0.95), coin_edges(10, 32),
                 r=0.11, ewidth=2.5, eopacity=0.8)
        g2 = Net(cloud_points(10, [3.5, -0.8, 0], 2.4, 2.1, seed=33, min_d=0.95), coin_edges(10, 34),
                 r=0.11, ewidth=2.5, eopacity=0.8)
        neq = math(r"\neq", size=110, color=BAD).move_to([0, -0.8, 0])
        with self.voiceover(text=N("s02.b4")) as tr:
            self.play(FadeOut(VGroup(L, Rn, tri, tag, tag_l)), run_time=0.4)
            self.play(FadeIn(c1), run_time=0.4)
            self.play(FadeIn(c2), run_time=0.4)
            wait_until(self, tr, "count")
            self.play(FadeIn(c3, shift=UP * 0.1), run_time=0.6)
            t = tr.time_until_bookmark("rare")
            self.play(FadeIn(g1), FadeIn(g2), run_time=rt(min(1.0, t)))
            wait_until(self, tr, "rare")
            self.play(FadeIn(neq, scale=1.4), run_time=0.5)
            rest(self, tr)

        n = 16
        xs = [-6.3 + 0.95 * k for k in range(n)]
        row_y = -1.6
        rpts = [np.array([x, row_y, 0]) for x in xs]
        row = Net(rpts, coin_edges(n, 41), r=0.1)
        arcs = {}
        for (i, j) in row.edges:
            a = ArcBetweenPoints(rpts[i], rpts[j], angle=-PI / 2, color=EDGE, stroke_width=2.2,
                                 stroke_opacity=0)
            arcs[(i, j)] = a
        row.ls = arcs
        row.lg = VGroup(*arcs.values())
        row.eopacity = 0.65
        nums = VGroup(*[text(str(k), size=24, color=MUTED).next_to(rpts[k], DOWN, 0.22) for k in range(n)])
        rc = coin("H").move_to([-6.2, 3.2, 0])
        chance = VGroup(text("chance two of these match:", size=38),
                        math("1", size=60, color=PRIMARY)).arrange(RIGHT, buff=0.3).move_to([0.8, 3.2, 0])
        with self.voiceover(text=N("s02.b5")) as tr:
            self.play(FadeOut(VGroup(counter, g1, g2, neq)), run_time=0.4)
            self.add(row.lg)
            self.play(FadeIn(row.ds, lag_ratio=0.05), FadeIn(nums, lag_ratio=0.05), FadeIn(rc), run_time=0.7)
            t = tr.time_until_bookmark("one")
            self.play(fill_anim(row, pair_order(0, n, seed=6), rc), run_time=rt(t))
            self.play(FadeIn(chance, shift=UP * 0.1), run_time=0.6)
            rest(self, tr)
        self.play(FadeOut(VGroup(row.ds, row.lg, nums, rc, chance)), run_time=0.5)


# ---------------------------------------------------------------------------
# s03 Every wish is granted
# ---------------------------------------------------------------------------

BIG_C = np.array([-3.4, -0.3, 0])


def big_graph(center=BIG_C, n=15, rx=2.7, ry=2.8, seed=51, rim=7, r=0.11):
    core = cloud_points(n, center, rx, ry, seed=seed, min_d=0.9)
    pts = core + rim_points(rim, center, rx + 0.55, ry + 0.45, seed=seed + 1)
    tot = len(pts)
    edges = coin_edges(tot, seed=seed + 2)
    net = Net(pts, edges, r=r, ewidth=2, eopacity=0.45)
    for k in range(n, tot):
        net.ds[k].set_opacity(0.4)
    for (i, j), ln in net.ls.items():
        if i >= n or j >= n:
            ln.set_stroke(opacity=0.18)
    net.core = n
    return net


def pick_wish_dots(net, k=3):
    """Three core dots spread apart, for the green, green, red demo."""
    n = net.core
    c = np.mean(net.pts[:n], axis=0)
    order = sorted(range(n), key=lambda i: np.linalg.norm(net.pts[i] - c))
    near = order[: n // 2]
    picks = [near[0]]
    for i in near[1:]:
        if all(np.linalg.norm(net.pts[i] - net.pts[j]) > 1.4 for j in picks):
            picks.append(i)
        if len(picks) == k:
            break
    return picks


class S03Wishes(VoiceoverScene):
    def construct(self):
        self.set_speech_service(get_speech_service())
        G = big_graph()
        g1, g2, r1 = pick_wish_dots(G)
        wb = wish_bubble(size=32).move_to([3.7, 2.3, 0])
        with self.voiceover(text=N("s03.b1")) as tr:
            self.play(FadeIn(G), run_time=1.0)
            wait_until(self, tr, "green")
            self.play(G.ds[g1].animate.set_color(GOOD).scale(1.6), G.ds[g2].animate.set_color(GOOD).scale(1.6),
                      run_time=0.5)
            wait_until(self, tr, "red")
            self.play(G.ds[r1].animate.set_color(BAD).scale(1.6), run_time=0.5)
            self.play(FadeIn(wb, shift=LEFT * 0.2), run_time=0.7)
            rest(self, tr)

        # Test panel: copies of the three colored dots, and one candidate.
        P = [np.array([1.6, 0.9, 0]), np.array([1.6, -0.6, 0]), np.array([1.6, -2.1, 0])]
        cols = [GOOD, GOOD, BAD]
        need = ["H", "H", "T"]
        panel = VGroup(*[Dot(p, radius=0.17, color=c) for p, c in zip(P, cols)])
        cand_p = np.array([5.4, -0.6, 0])
        cand = Dot(cand_p, radius=0.17, color=FG)
        cand_src = next(i for i in range(G.core) if i not in (g1, g2, r1)
                        and G.pts[i][0] > BIG_C[0] + 0.6)
        paths = VGroup(*[DashedLine(cand_p, p, color=MUTED, stroke_width=2.5, dash_length=0.12) for p in P])
        coins = [coin(f, r=0.26).move_to(interpolate(cand_p, p, 0.5) + UP * 0.42) for p, f in zip(P, ("T", "T", "H"))]
        chance = VGroup(text("chance", size=34), math(r"\tfrac12 \cdot \tfrac12 \cdot \tfrac12 = \tfrac18", size=44,
                                                      color=PRIMARY)).arrange(RIGHT, buff=0.3).move_to([3.5, -3.3, 0])

        def show_result(faces):
            ok = list(faces) == need
            res = VGroup()
            for p, f in zip(P, faces):
                if f == "H":
                    res.add(Line(cand_p, p, color=FG, stroke_width=4))
            return res, ok

        with self.voiceover(text=N("s03.b2")) as tr:
            self.play(TransformFromCopy(VGroup(G.ds[g1], G.ds[g2], G.ds[r1]), panel),
                      TransformFromCopy(G.ds[cand_src], cand), Indicate(G.ds[cand_src]), run_time=0.9)
            self.play(Create(paths), FadeIn(VGroup(*coins)), run_time=0.6)
            t = tr.time_until_bookmark("eighth")
            for cn, f in zip(coins, need):
                flip(self, cn, f, run_time=rt(min(0.5, (t - 0.2) / 3)))
            res, _ = show_result(need)
            wait_until(self, tr, "eighth")
            self.play(Create(res), FadeIn(chance), run_time=0.6)
            rest(self, tr)

        tally_lab = text("chance all fail:", size=32).move_to([3.4, 3.2, 0])
        tally_vals = [r"\tfrac78", r"\left(\tfrac78\right)^{2}", r"\left(\tfrac78\right)^{10}", r"0"]
        tallies = [math(v, size=48, color=PRIMARY).next_to(tally_lab, RIGHT, 0.3) for v in tally_vals]
        fails = [("T", "H", "H"), ("H", "T", "T"), ("T", "T", "T"), ("H", "H", "H"), ("T", "H", "T"),
                 ("H", "T", "H"), ("T", "T", "H"), ("H", "H", "H"), ("T", "H", "T")]
        with self.voiceover(text=N("s03.b3")) as tr:
            self.play(FadeOut(wb), FadeOut(res), FadeOut(chance), run_time=0.4)
            self.play(FadeIn(tally_lab), run_time=0.3)
            cur = None
            mark = None
            t = tr.time_until_bookmark("shrink")
            per = rt((t - 0.8) / 2)
            for k in range(2):
                self.play(Flash(cand, color=FG, flash_radius=0.3), run_time=0.25)
                for cn, f in zip(coins, fails[k]):
                    cn[1].become(face_mob(f, cn.r).move_to(cn[0]))
                res, _ = show_result(fails[k])
                new = tallies[k]
                mk = cross(cand_p + DOWN * 0.6, s=0.16)
                anims = [FadeIn(res), Create(mk)]
                anims.append(FadeIn(new) if cur is None else ReplacementTransform(cur, new))
                self.play(*anims, run_time=rt(min(0.6, per - 0.25)))
                cur = new
                self.wait(max(0, per - 0.85))
                self.play(FadeOut(res), FadeOut(mk), run_time=0.2)
            wait_until(self, tr, "shrink")
            t = tr.time_until_bookmark("zero")
            k_fast = 7
            per = (t - 0.6) / k_fast
            for k in range(k_fast):
                for cn, f in zip(coins, fails[2 + k]):
                    cn[1].become(face_mob(f, cn.r).move_to(cn[0]))
                res, _ = show_result(fails[2 + k])
                self.add(res)
                if k == 0:
                    self.play(ReplacementTransform(cur, tallies[2]), run_time=rt(min(0.4, per)))
                    cur = tallies[2]
                    self.wait(max(0, per - 0.4))
                else:
                    self.wait(rt(per))
                self.remove(res)
            wait_until(self, tr, "zero")
            for cn, f in zip(coins, need):
                cn[1].become(face_mob(f, cn.r).move_to(cn[0]))
            res, _ = show_result(need)
            tk = tick(at=cand_p + DOWN * 0.6 + RIGHT * 0.05, s=1.3)
            self.play(ReplacementTransform(cur, tallies[3]), FadeIn(res), Create(tk), run_time=0.6)
            cur = tallies[3]
            rest(self, tr)

        # A list of wishes, each failing with chance 0.
        rng = np.random.default_rng(7)
        rows = VGroup()
        for k in range(12):
            m = int(rng.integers(1, 5))
            ds = VGroup(*[Dot(radius=0.13, color=(GOOD if rng.random() < 0.5 else BAD)) for _ in range(m)])
            ds.arrange(RIGHT, buff=0.18)
            lab = text("fails: 0", size=28, color=MUTED)
            row = VGroup(ds, lab).arrange(RIGHT, buff=0.45)
            ds.align_to(row, LEFT)
            rows.add(row)
        rows.arrange(DOWN, buff=0.32, aligned_edge=LEFT).move_to([1.3, 0, 0]).align_to(UP * 2.4, UP)
        for row in rows:
            row[1].set_x(2.15, LEFT)
            row[1].align_to(rows[0][1], LEFT)
        clip_top, clip_bot = 2.6, -2.0
        brace = BraceBetweenPoints([3.75, clip_top, 0], [3.75, clip_bot, 0], direction=RIGHT, color=PRIMARY)
        blab = VGroup(text("a list of zeros", size=30, color=PRIMARY),
                      text("adds up to 0", size=30, color=PRIMARY)).arrange(DOWN, buff=0.1).next_to(brace, RIGHT, 0.2)
        union = math(r"P(\text{some wish fails}) \le 0 + 0 + 0 + \cdots = 0", size=40).move_to([2.6, -3.0, 0])
        ok_all = text("every wish granted", size=34, color=GOOD).next_to(union, DOWN, 0.3)

        def visible(m):
            def upd(mob):
                for row in mob:
                    y = row.get_y()
                    o = 1.0 if clip_bot <= y <= clip_top else 0.0
                    row.set_opacity(o)
            return upd

        with self.voiceover(text=N("s03.b4")) as tr:
            self.play(FadeOut(VGroup(panel, cand, paths, *coins, res, tk, cur, tally_lab)),
                      G.ds[g1].animate.set_color(FG).scale(1 / 1.6), G.ds[g2].animate.set_color(FG).scale(1 / 1.6),
                      G.ds[r1].animate.set_color(FG).scale(1 / 1.6), run_time=0.5)
            rows.add_updater(visible(rows))
            self.add(rows)
            t = tr.time_until_bookmark("list")
            self.play(rows.animate.shift(UP * 1.2), run_time=rt(t), rate_func=linear)
            self.play(GrowFromCenter(brace), FadeIn(blab), rows.animate.shift(UP * 0.6), run_time=0.8,
                      rate_func=linear)
            t = tr.get_remaining_duration()
            self.play(FadeIn(union), rows.animate.shift(UP * 1.0), run_time=rt(min(1.0, t * 0.3)), rate_func=linear)
            self.play(rows.animate.shift(UP * 1.0), run_time=rt(t * 0.3), rate_func=linear)
            self.play(FadeIn(ok_all), rows.animate.shift(UP * 0.6), run_time=rt(min(0.8, t * 0.2)), rate_func=linear)
            rest(self, tr)
            rows.clear_updaters()

        tails = VGroup(*[coin("T", r=0.42) for _ in range(7)]).arrange(RIGHT, buff=0.3)
        more = text("...", size=60, color=MUTED)
        row_t = VGroup(tails, more).arrange(RIGHT, buff=0.3).move_to(UP * 0.5)
        cap = text("possible, but chance 0", size=40, color=PRIMARY).next_to(row_t, DOWN, 0.7)
        with self.voiceover(text=N("s03.b5")) as tr:
            self.play(FadeOut(VGroup(G, rows, brace, blab, union, ok_all)), run_time=0.5)
            t = tr.get_remaining_duration()
            self.play(LaggedStart(*[FadeIn(c, shift=DOWN * 0.3) for c in tails], lag_ratio=0.35),
                      run_time=rt(min(2.5, t * 0.4)))
            self.play(FadeIn(more), FadeIn(cap), run_time=0.6)
            rest(self, tr)
        self.play(FadeOut(VGroup(row_t, cap)), run_time=0.4)


# ---------------------------------------------------------------------------
# s04 Matching your graph to mine
# ---------------------------------------------------------------------------

CARD = ["pick your first dot without a thread", "color the matched dots",
        "the other side grants the wish"]


def card_row(size=26):
    parts = []
    for k, s in enumerate(CARD):
        parts.append(VGroup(text(f"{k + 1}.", size=size, color=PRIMARY), text(s, size=size)).arrange(RIGHT, buff=0.12))
    row = VGroup(*parts).arrange(DOWN, buff=0.1, aligned_edge=LEFT)
    box = SurroundingRectangle(row, color=MUTED, buff=0.22, corner_radius=0.15, stroke_width=2.5)
    return VGroup(box, row)


class S04Matching(VoiceoverScene):
    def construct(self):
        self.set_speech_service(get_speech_service())
        g = Game()
        rule = text("threads keep the lines: joined to joined, apart to apart", size=30, color=MUTED)
        rule.move_to(DOWN * 3.45)
        A0, B0 = g.nets
        da, db_ = next((a, b) for a, b in sorted(A0.edges) if a > 0 and b > 0)
        dc = next(c for c in range(1, g.n) if c not in (da, db_) and not A0.adj(da, c))
        with self.voiceover(text=N("s04.b1")) as tr:
            self.play(FadeIn(g.base()), run_time=1.0)
            demo = VGroup(g.thread(0, da, g.sigma[da]), g.thread(0, db_, g.sigma[db_]))
            t = tr.get_remaining_duration()
            self.play(Create(demo[0]), run_time=0.6)
            self.play(FadeIn(rule), run_time=0.6)
            self.wait(max(0, t * 0.15))
            self.play(Create(demo[1]), run_time=0.6)
            joined = VGroup(A0.make_line(da, db_, color=GOOD, width=6, opacity=1),
                            B0.make_line(g.sigma[da], g.sigma[db_], color=GOOD, width=6, opacity=1))
            self.play(Create(joined), run_time=0.7)
            self.wait(max(0, t * 0.12))
            demo.add(g.thread(0, dc, g.sigma[dc]))
            apart = VGroup(A0.make_line(da, dc, color=BAD, width=3, opacity=1, dashed=True),
                           B0.make_line(g.sigma[da], g.sigma[dc], color=BAD, width=3, opacity=1, dashed=True))
            self.play(Create(demo[2]), run_time=0.6)
            self.play(Create(apart), run_time=0.7)
            rest(self, tr)
            self.play(FadeOut(demo), FadeOut(joined), FadeOut(apart), run_time=0.3)

        T = g.turns
        with self.voiceover(text=N("s04.b2")) as tr:
            side, a, b = T[0]
            self.play(Create(ring_around(g.dot(0, a))), g.nets[0].lab[a].animate.set_color(PRIMARY), run_time=0.5)
            wait_until(self, tr, "t1")
            th = g.thread(0, a, b)
            ring_b = ring_around(g.dot(1, b))
            self.play(Create(ring_b), Create(th), run_time=0.7)
            g.threads.add(th)
            g.record(0, a, b)
            self.play(*[mob.animate.set_color(MATCHED) for mob in (g.dot(0, a), g.dot(1, b))],
                      g.nets[0].lab[a].animate.set_color(MUTED),
                      FadeOut(VGroup(*[m for m in self.mobjects if isinstance(m, Circle)])), run_time=0.4)
            rest(self, tr)

        with self.voiceover(text=N("s04.b3")) as tr:
            g.full_step(self, tr, T[1], marks={"pick": "pick", "carry": "carry", "grant": "t2"})
            rest(self, tr)

        with self.voiceover(text=N("s04.b4")) as tr:
            g.full_step(self, tr, T[2], marks={"grant": "t3"})
            rest(self, tr)

        card = card_row().move_to(DOWN * 2.95)
        tk = tick(at=card.get_right() + RIGHT * 0.45, s=1.2)
        with self.voiceover(text=N("s04.b5")) as tr:
            self.play(FadeOut(rule), run_time=0.3)
            self.play(LaggedStart(FadeIn(card[0]), *[FadeIn(p) for p in card[1]], lag_ratio=0.5), run_time=2.0)
            # Show one more turn quickly while the card is read.
            g.full_step(self, tr, T[3])
            wait_until(self, tr, "stuck")
            self.play(Create(tk), run_time=0.4)
            rest(self, tr)

        idx = 4
        with self.voiceover(text=N("s04.b6")) as tr:
            self.play(FadeOut(card), FadeOut(tk), run_time=0.3)
            t = tr.time_until_bookmark("skip")
            k1 = 3
            for k in range(k1):
                g.quick_step(self, T[idx + k], run_time=min(0.7, (t - 0.3) / k1))
            idx += k1
            wait_until(self, tr, "skip")
            # A dot on your side that is still waiting.
            waiting = max(h for h in range(g.n) if h not in g.matched[1])
            wring = ring_around(g.dot(1, waiting), color=BAD, r=0.27)
            wq = text("still waiting", size=30, color=BAD).move_to([3.4, -2.6, 0])
            wq.add(Arrow(wq.get_top(), g.dot(1, waiting).get_center(), color=BAD, buff=0.3, stroke_width=3,
                         max_tip_length_to_length_ratio=0.12))
            self.play(Create(wring), FadeIn(wq), run_time=0.5)
            rem = [t_ for t_ in T[idx:]]
            # Play turns until the waiting dot gets its thread.
            upto = next(k for k, t_ in enumerate(rem) if (t_[0] == 1 and t_[1] == waiting) or (t_[0] == 0 and t_[2] == waiting))
            budget = tr.get_remaining_duration() - 0.6
            for k in range(upto + 1):
                g.quick_step(self, rem[k], run_time=min(0.7, budget / (upto + 1)))
            idx += upto + 1
            self.play(wring.animate.set_color(GOOD), FadeOut(wq), run_time=0.4)
            rest(self, tr)
            self.play(FadeOut(wring), run_time=0.2)

        eq = math("=", size=110, color=PRIMARY).move_to(UP * 3.2)
        with self.voiceover(text=N("s04.b7")) as tr:
            t = tr.time_until_bookmark("all")
            rem = T[idx:]
            for k, t_ in enumerate(rem):
                g.quick_step(self, t_, run_time=min(0.5, max(0.15, (t - 0.2) / max(1, len(rem)))))
            wait_until(self, tr, "all")
            A, B = g.nets
            flashes = []
            for (i, j), ln in A.ls.items():
                flashes.append(ln.animate(rate_func=there_and_back).set_color(PRIMARY).set_stroke(width=6, opacity=1))
                lb = B.line(g.sigma[i], g.sigma[j])
                flashes.append(lb.animate(rate_func=there_and_back).set_color(PRIMARY).set_stroke(width=6, opacity=1))
            self.play(*flashes, run_time=1.4)
            self.play(FadeOut(g.titles), FadeIn(eq, scale=1.4), run_time=0.6)
            rest(self, tr)

        # Inset: the thread game on the rationals.
        top_y, bot_y = 0.9, -0.9
        lt = Line([-3.6, top_y, 0], [3.6, top_y, 0], color=FG, stroke_width=3)
        lb_ = Line([-3.6, bot_y, 0], [3.6, bot_y, 0], color=FG, stroke_width=3)
        xs_t = [-2.8, -1.6, -0.3, 0.6, 1.9, 2.9]
        xs_b = [-3.0, -1.1, -0.6, 1.0, 1.5, 3.1]
        dt = VGroup(*[Dot([x, top_y, 0], radius=0.1, color=SECONDARY) for x in xs_t])
        db = VGroup(*[Dot([x, bot_y, 0], radius=0.1, color=PRIMARY) for x in xs_b])
        ths = VGroup(*[Line(a.get_center(), b.get_center(), color=FG, stroke_width=2.5) for a, b in zip(dt, db)])
        inset = VGroup(lt, lb_, dt, db, ths)
        frame = SurroundingRectangle(inset, color=MUTED, buff=0.4, corner_radius=0.15)
        lab = text("same game", size=34, color=PRIMARY).next_to(frame, UP, 0.25)
        between = text("always another dot between any two, and beyond either end", size=28, color=MUTED)
        between.next_to(frame, DOWN, 0.35)
        here = text("here: the wishes", size=34, color=GOOD).next_to(between, DOWN, 0.25)
        with self.voiceover(text=N("s04.b8")) as tr:
            self.play(FadeOut(VGroup(g.base(), g.threads, eq)), run_time=0.5)
            self.play(FadeIn(frame), FadeIn(lab), FadeIn(VGroup(lt, lb_, dt, db)), run_time=0.6)
            t = tr.get_remaining_duration()
            self.play(Create(ths, lag_ratio=0.3), run_time=rt(min(1.5, t * 0.3)))
            self.play(FadeIn(between), run_time=0.6)
            self.wait(max(0, t * 0.35 - 1.2))
            self.play(FadeIn(here), run_time=0.5)
            rest(self, tr)
        self.play(FadeOut(VGroup(inset, frame, lab, between, here)), run_time=0.4)


# ---------------------------------------------------------------------------
# s05 The random graph
# ---------------------------------------------------------------------------

PALEY_C = np.array([-3.3, -0.45, 0])
HOUSE = [(0, 1), (1, 2), (2, 3), (3, 0), (4, 0), (4, 1)]
HOUSE_IN = (0, 1, 2, 3, 10)  # an induced house in the Paley graph, found by search


def paley_pts(center=PALEY_C, rx=2.9, ry=2.75, seed=61):
    return cloud_points(13, center, rx, ry, seed=seed, min_d=1.05 * min(rx / 2.9, ry / 2.75))


def rado_title(size=46):
    return VGroup(text("the random graph", size=size, weight="BOLD"),
                  text("(the Rado graph)", size=int(size * 0.7), color=MUTED)).arrange(DOWN, buff=0.12)


class S05Rado(VoiceoverScene):
    def construct(self):
        self.set_speech_service(get_speech_service())
        pts = paley_pts()
        P = Net(pts, paley_edges(), r=0.13, ewidth=2.5, eopacity=0.7)
        ttl = rado_title().move_to([3.6, 2.6, 0])
        with self.voiceover(text=N("s05.b1")) as tr:
            self.play(FadeIn(P.ds, lag_ratio=0.05), run_time=0.8)
            self.play(Create(P.lg, lag_ratio=0.02), run_time=1.4)
            t = tr.get_remaining_duration()
            self.wait(max(0, t * 0.4))
            self.play(FadeIn(ttl, shift=DOWN * 0.1), run_time=0.7)
            rest(self, tr)

        used = VGroup(
            VGroup(text("coins", size=34), cross(ORIGIN, s=0.16)).arrange(RIGHT, buff=0.35),
            VGroup(text("wishes", size=34), tick(at=ORIGIN, s=1.1)).arrange(RIGHT, buff=0.35),
        ).arrange(DOWN, buff=0.3, aligned_edge=LEFT)
        used_lab = text("the matching used:", size=32, color=MUTED)
        used_g = VGroup(used_lab, used).arrange(DOWN, buff=0.3, aligned_edge=LEFT).move_to([3.6, 0.4, 0])
        eqn = VGroup(text("dots in a list", size=34),
                     text("+ every wish granted", size=34),
                     text("= the random graph", size=34, color=PRIMARY)).arrange(DOWN, buff=0.15, aligned_edge=LEFT)
        box = SurroundingRectangle(eqn, color=PRIMARY, buff=0.3, corner_radius=0.15)
        eqg = VGroup(box, eqn).move_to([3.6, -2.2, 0])
        with self.voiceover(text=N("s05.b2")) as tr:
            self.play(FadeIn(used_lab), FadeIn(used[0][0]), run_time=0.5)
            self.play(Create(used[0][1]), run_time=0.4)
            self.play(FadeIn(used[1][0]), Create(used[1][1]), run_time=0.6)
            wait_until(self, tr, "any")
            self.play(Create(box), FadeIn(eqn, lag_ratio=0.3), run_time=1.0)
            rest(self, tr)

        C = Net(pts, paley_edges(flip=True), r=0.13, ewidth=2.5, eopacity=0.7)
        lab_flip = text("flip every connection", size=36).move_to([3.6, 1.0, 0])
        lab_same = text("the same graph back", size=36, color=PRIMARY).move_to([3.6, -0.6, 0])
        # A wish whose colors swap under the flip.
        w = [5, 7, 11]
        with self.voiceover(text=N("s05.b3")) as tr:
            self.play(FadeOut(VGroup(used_g, eqg, ttl)), run_time=0.4)
            wait_until(self, tr, "flip")
            self.add(C.lg)
            C.lg.set_stroke(opacity=0)
            self.play(P.lg.animate.set_stroke(opacity=0), C.lg.animate.set_stroke(opacity=0.7), FadeIn(lab_flip),
                      run_time=1.2)
            self.remove(P.lg)
            C.ds = P.ds
            C.follow()
            t = tr.get_remaining_duration()
            wc = [GOOD, GOOD, BAD]
            self.play(*[P.ds[i].animate.set_color(c).scale(1.5) for i, c in zip(w, wc)], run_time=0.5)
            self.play(*[P.ds[i].animate.set_color(c) for i, c in zip(w, [BAD, BAD, GOOD])], run_time=0.6)
            self.play(*[P.ds[i].animate.set_color(FG).scale(1 / 1.5) for i in w], run_time=0.4)
            self.play(*[P.ds[i].animate.move_to(pts[(2 * i) % 13]) for i in range(13)],
                      run_time=rt(min(2.0, t - 2.0)))
            self.play(FadeIn(lab_same), run_time=0.5)
            rest(self, tr)
        C.unfollow()
        # The picture now matches the original exactly; swap back to the original objects.
        P2 = Net(pts, paley_edges(), r=0.13, ewidth=2.5, eopacity=0.7)
        self.remove(C.lg, P.ds)
        self.add(P2)

        house_pts = [np.array(p) for p in ([0, 0, 0], [0.9, 0, 0], [0.9, -0.9, 0], [0, -0.9, 0], [0.45, 0.65, 0])]
        hc = np.array([4.9, 2.2, 0])
        house_pts = [p + hc - np.array([0.45, -0.1, 0]) for p in house_pts]
        house = Net(house_pts, HOUSE, r=0.1, ewidth=4, eopacity=1, ecolor=PRIMARY, color=PRIMARY)
        want = text("want this one?", size=30, color=MUTED).next_to(house, LEFT, 0.5)
        every = text("every finite graph is inside", size=34, color=PRIMARY).move_to([3.6, -1.6, 0])
        every2 = text("(and every listable infinite one)", size=28, color=MUTED).next_to(every, DOWN, 0.2)
        with self.voiceover(text=N("s05.b4")) as tr:
            self.play(FadeOut(VGroup(lab_flip, lab_same)), FadeIn(house), FadeIn(want), run_time=0.6)
            wait_until(self, tr, "build")
            budget = tr.get_remaining_duration() - 1.4
            per = budget / 5
            placed = []
            for k, v in enumerate(HOUSE_IN):
                marks = VGroup()
                for kk in placed:
                    u = HOUSE_IN[kk]
                    col = GOOD if (key(kk, k) in {key(*e) for e in HOUSE}) else BAD
                    marks.add(ring_around(P2.ds[u], color=col, r=0.25))
                new_lines = VGroup(*[P2.line(HOUSE_IN[kk], v).copy().set_color(PRIMARY).set_stroke(width=5, opacity=1)
                                     for kk in placed if key(kk, k) in {key(*e) for e in HOUSE}])
                self.play(FadeIn(marks), house.ds[k].animate.scale(1.6), run_time=rt(per * 0.35))
                self.play(P2.ds[v].animate.set_color(PRIMARY).scale(1.4), Create(new_lines),
                          house.ds[k].animate.scale(1 / 1.6), run_time=rt(per * 0.4))
                self.play(FadeOut(marks), run_time=rt(per * 0.25))
                placed.append(k)
            self.play(FadeIn(every), FadeIn(every2), run_time=0.6)
            rest(self, tr)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.5)


# ---------------------------------------------------------------------------
# s06 A recipe with no coins
# ---------------------------------------------------------------------------


def binary_row(bits, size=64, color=FG, buff=0.35, positions=True, pos_size=26):
    """Digits left to right with their positions (counting from the right, from 0) below."""
    digs = VGroup(*[math(b, size=size, color=color) for b in bits]).arrange(RIGHT, buff=buff)
    n = len(bits)
    pos = VGroup(*[text(str(n - 1 - k), size=pos_size, color=MUTED).next_to(digs[k], DOWN, 0.25) for k in range(n)])
    g = VGroup(digs, pos) if positions else VGroup(digs)
    g.digs, g.pos = digs, pos
    return g


def rule_text(size=32):
    return VGroup(text("a smaller number k joins a bigger number m", size=size),
                  text("when m, in binary, has a 1 in position k", size=size)).arrange(DOWN, buff=0.1)


def bit_circle(n=16, center=ORIGIN, radius=2.8, label_size=24):
    return Net(ring_points(n, center, radius), bit_edges(n), r=0.11, ewidth=2.2, eopacity=0.6, labels=True,
               label_size=label_size, label_center=center, label_buff=0.36)


class S06Recipe(VoiceoverScene):
    def construct(self):
        self.set_speech_service(get_speech_service())
        rule = rule_text().move_to(UP * 3.2)
        b13 = binary_row("1101").move_to([0.9, 1.3, 0])
        lhs = math("13", "=", size=64).next_to(b13.digs, LEFT, 0.4)
        xs = [-6.4 + 0.92 * k for k in range(14)]
        row_y = -2.4
        rpts = [np.array([x, row_y, 0]) for x in xs]
        row = VGroup(*[Dot(p, radius=0.11, color=FG) for p in rpts])
        nums = VGroup(*[text(str(k), size=24, color=MUTED).next_to(rpts[k], DOWN, 0.22) for k in range(14)])
        arcs = VGroup(*[ArcBetweenPoints(rpts[13], rpts[k], angle=PI / 2.2, color=PRIMARY, stroke_width=4)
                        for k in (0, 2, 3)])
        with self.voiceover(text=N("s06.b1")) as tr:
            t = tr.time_until_bookmark("bin")
            self.play(FadeIn(row, lag_ratio=0.05), FadeIn(nums, lag_ratio=0.05), run_time=rt(min(1.5, t * 0.3)))
            self.wait(max(0, t * 0.15))
            self.play(FadeIn(rule), run_time=0.8)
            wait_until(self, tr, "bin")
            self.play(FadeIn(lhs), FadeIn(b13.digs, lag_ratio=0.2), row[13].animate.set_color(PRIMARY).scale(1.4),
                      run_time=0.8)
            self.play(FadeIn(b13.pos, lag_ratio=0.2), run_time=0.7)
            wait_until(self, tr, "ones")
            hi = [0, 1, 3]  # digit indices (left to right) holding ones: positions 3, 2, 0
            self.play(*[b13.digs[k].animate.set_color(PRIMARY) for k in hi],
                      *[b13.pos[k].animate.set_color(PRIMARY) for k in hi], run_time=0.6)
            t = tr.get_remaining_duration()
            self.play(Create(arcs, lag_ratio=0.3), *[row[k].animate.set_color(PRIMARY) for k in (0, 2, 3)],
                      run_time=rt(min(1.4, t * 0.5)))
            rest(self, tr)

        BC = bit_circle(16, center=[0, -0.35, 0], radius=2.75)
        wish = VGroup(text("wish: joined to", size=32), text("0", size=32, color=GOOD, weight="BOLD"),
                      text(", not to", size=32), text("1, 2, 3", size=32, color=BAD, weight="BOLD")).arrange(RIGHT, buff=0.12)
        wish.move_to(UP * 3.5)
        with self.voiceover(text=N("s06.b2")) as tr:
            self.play(FadeOut(VGroup(rule, b13, lhs, row, nums, arcs)), run_time=0.4)
            wait_until(self, tr, "graph")
            self.play(FadeIn(BC.ds), FadeIn(BC.lab), Create(BC.lg, lag_ratio=0.02), run_time=1.5)
            t = tr.get_remaining_duration()
            self.wait(max(0, t - 1.6))
            self.play(FadeIn(wish), BC.ds[0].animate.set_color(GOOD).scale(1.4),
                      *[BC.ds[k].animate.set_color(BAD).scale(1.4) for k in (1, 2, 3)], run_time=0.8)
            rest(self, tr)

        # Build the answer digit by digit.
        rxs = [-5.4, -4.0, -2.6, -1.2, 0.2]
        ry = -2.6
        rdots = VGroup(*[Dot([x, ry, 0], radius=0.15, color=c) for x, c in zip(rxs, [GOOD, BAD, BAD, BAD, MUTED])])
        rnums = VGroup(*[text(str(k), size=30, color=MUTED).next_to(rdots[k], DOWN, 0.25) for k in range(5)])
        slot_w = 0.75
        slot_x = [-2.6 + k * 1.0 for k in range(5)]  # positions 4, 3, 2, 1, 0 left to right
        sy = 1.6
        slots = VGroup(*[Line([x - slot_w / 2, sy - 0.45, 0], [x + slot_w / 2, sy - 0.45, 0], color=MUTED,
                              stroke_width=4) for x in slot_x])
        spos = VGroup(*[text(str(4 - k), size=26, color=MUTED).move_to([slot_x[k], sy - 0.85, 0]) for k in range(5)])
        digits = ["1", "0", "0", "0", "1"]
        dcol = [PRIMARY, BAD, BAD, BAD, GOOD]
        dmobs = VGroup(*[math(d, size=64, color=c).move_to([slot_x[k], sy, 0]) for k, (d, c) in enumerate(zip(digits, dcol))])
        eq1 = math("=", "1", size=60).next_to(dmobs[4], RIGHT, 0.6)
        eq17 = math("=", "17", size=60, color=PRIMARY).next_to(dmobs[4], RIGHT, 0.6)
        own_arrow = Arrow(eq1.get_bottom() + DOWN * 0.1, rdots[1].get_top() + UP * 0.15, color=BAD, buff=0.1,
                          stroke_width=4)
        own_x = cross(rdots[1].get_center() + UP * 0.6 + RIGHT * 0.45, s=0.16)
        d17 = Dot([4.4, -0.4, 0], radius=0.16, color=PRIMARY)
        l17 = text("17", size=32, color=PRIMARY).next_to(d17, RIGHT, 0.2)
        e0 = Line(d17.get_center(), rdots[0].get_center(), color=GOOD, stroke_width=5)
        e4 = Line(d17.get_center(), rdots[4].get_center(), color=MUTED, stroke_width=3)
        ok = text("wish granted", size=36, color=GOOD).move_to([4.4, -2.6, 0])
        with self.voiceover(text=N("s06.b3")) as tr:
            self.play(FadeOut(BC), run_time=0.4)
            self.play(wish.animate.scale(0.9).move_to(UP * 3.4), FadeIn(rdots[:4]), FadeIn(rnums[:4]),
                      FadeIn(slots[1:]), FadeIn(spos[1:]), run_time=0.6)
            wait_until(self, tr, "fill")
            self.play(LaggedStart(*[FadeIn(dmobs[k], shift=DOWN * 0.2) for k in (4, 1, 2, 3)], lag_ratio=0.4),
                      run_time=1.2)
            wait_until(self, tr, "own")
            self.play(FadeIn(eq1), run_time=0.4)
            self.play(GrowArrow(own_arrow), Create(own_x), run_time=0.6)
            wait_until(self, tr, "lead")
            self.play(FadeOut(own_arrow), FadeOut(own_x), FadeIn(slots[0]), FadeIn(spos[0]), run_time=0.4)
            self.play(FadeIn(dmobs[0], shift=DOWN * 0.2), ReplacementTransform(eq1, eq17), run_time=0.7)
            wait_until(self, tr, "check")
            self.play(FadeIn(rdots[4]), FadeIn(rnums[4]), FadeIn(d17), FadeIn(l17), run_time=0.5)
            self.play(Create(e0), Create(e4), run_time=0.7)
            self.play(FadeIn(ok), run_time=0.5)
            rest(self, tr)

        msg = text("every wish, granted on demand", size=48, color=PRIMARY).move_to(UP * 1.0)
        cr1 = text(f"{ERDOS} and {RENYI}, 1963: coin flips give one graph", size=32, color=MUTED)
        cr2 = text("Rado, 1964: this recipe", size=32, color=MUTED)
        crs = VGroup(cr1, cr2).arrange(DOWN, buff=0.2).next_to(msg, DOWN, 0.8)
        with self.voiceover(text=N("s06.b4")) as tr:
            self.play(FadeOut(VGroup(wish, rdots, rnums, slots, spos, dmobs, eq17, d17, l17, e0, e4, ok)),
                      run_time=0.5)
            self.play(FadeIn(msg), run_time=0.7)
            t = tr.get_remaining_duration()
            self.wait(max(0, t * 0.25))
            self.play(FadeIn(cr1), run_time=0.6)
            self.wait(max(0, t * 0.2))
            self.play(FadeIn(cr2), run_time=0.6)
            rest(self, tr)
        self.play(FadeOut(VGroup(msg, crs)), run_time=0.4)


# ---------------------------------------------------------------------------
# s07 Ending: the zero-one law
# ---------------------------------------------------------------------------


def mini_cloud(n, center, rx, ry, seed, n_lines=None, r=0.05):
    pts = cloud_points(n, center, rx, ry, seed=seed, min_d=min(rx, ry) * 2.4 / sqrt(n))
    rng = np.random.default_rng(seed + 1)
    m = len(pts)
    k = n_lines if n_lines is not None else m
    pairs = set()
    while len(pairs) < k:
        i, j = rng.integers(0, m, 2)
        if i != j and np.linalg.norm(pts[i] - pts[j]) < (rx + ry) * 0.8:
            pairs.add(key(int(i), int(j)))
    return Net(pts, pairs, r=r, ewidth=1.2, eopacity=0.45)


class Bar(VGroup):
    def __init__(self, length=3.2, height=0.32, color=PRIMARY, value=0.0):
        super().__init__()
        self.length = length
        self.track = Rectangle(width=length, height=height, color=MUTED, stroke_width=2.5)
        self.fill = Rectangle(width=length, height=height, stroke_width=0, fill_color=color, fill_opacity=0.85)
        self.add(self.track, self.fill)
        self.v = ValueTracker(value)
        self.fill.add_updater(self._upd)
        self._upd(self.fill)

    def _upd(self, m):
        v = max(1e-3, self.v.get_value())
        m.stretch_to_fit_width(self.length * v)
        m.align_to(self.track, LEFT).set_y(self.track.get_y())


class S07Ending(VoiceoverScene):
    def construct(self):
        self.set_speech_service(get_speech_service())
        f1 = math(r"\forall x\, \forall y\, \exists z\;\, (z \sim x \,\wedge\, z \sim y)", size=52).move_to(UP * 3.1)
        keyl = VGroup(math(r"\sim", size=44, color=MUTED), text("= connected", size=30, color=MUTED)).arrange(RIGHT, buff=0.2)
        keyl.next_to(f1, DOWN, 0.25)
        s1 = text("any two dots have a common neighbor", size=34).move_to([-2.6, 1.2, 0])
        s2 = text("some dot is connected to every other dot", size=34).move_to([-2.6, -0.1, 0])
        s2.align_to(s1, LEFT)
        bar1 = Bar(value=0.0).move_to([3.4, 1.2, 0])
        bar2 = Bar(value=0.0, color=BAD).move_to([3.4, -0.1, 0])
        chance_lab = text("chance it's true", size=26, color=MUTED).next_to(bar1, UP, 0.2)
        with self.voiceover(text=N("s07.b1")) as tr:
            self.play(FadeIn(f1), run_time=0.8)
            self.play(FadeIn(keyl), run_time=0.5)
            wait_until(self, tr, "common")
            self.play(FadeIn(s1, shift=UP * 0.1), run_time=0.6)
            rest(self, tr)

        cl_specs = [("100 dots", 16, 0.75, 101), ("1,000 dots", 36, 0.9, 102), ("1,000,000 dots", 80, 1.05, 103)]
        clouds = VGroup()
        for k, (lab, n, rad, sd) in enumerate(cl_specs):
            c = np.array([-4.2 + 4.2 * k, -2.3, 0])
            cl = mini_cloud(n, c, rad * 1.5, rad * 0.95, sd, n_lines=int(n * 1.3))
            lb = text(lab, size=26, color=MUTED).next_to(cl, DOWN, 0.15)
            clouds.add(VGroup(cl, lb))
        vals1 = [0.55, 0.88, 0.995]
        with self.voiceover(text=N("s07.b2")) as tr:
            self.play(FadeIn(bar1), FadeIn(chance_lab), run_time=0.5)
            t = tr.time_until_bookmark("up")
            per = max(0.4, (tr.duration - 0.5) / 3.6)
            for k in range(3):
                self.play(FadeIn(clouds[k]), bar1.v.animate.set_value(vals1[k]), run_time=rt(per * 0.6))
                self.wait(max(0, per * 0.4))
            rest(self, tr)

        vals2 = [0.32, 0.08, 0.004]
        with self.voiceover(text=N("s07.b3")) as tr:
            self.play(FadeIn(s2, shift=UP * 0.1), FadeIn(bar2), run_time=0.6)
            wait_until(self, tr, "hub")
            per = max(0.4, tr.get_remaining_duration() / 3.4)
            for k in range(3):
                self.play(Indicate(clouds[k][0], color=BAD, scale_factor=1.05), bar2.v.animate.set_value(vals2[k]),
                          run_time=rt(per * 0.7))
                self.wait(max(0, per * 0.3))
            rest(self, tr)

        RG = Net(paley_pts(center=[0, 0, 0], rx=1.3, ry=1.2, seed=71), paley_edges(), r=0.07, ewidth=1.4, eopacity=0.6)
        RG.move_to([5.4, -2.3, 0])
        rg_lab = text("the random graph", size=28, color=PRIMARY).next_to(RG, LEFT, 0.3)
        one = math("1", size=44, color=PRIMARY).next_to(bar1, RIGHT, 0.25)
        zero = math("0", size=44, color=BAD).next_to(bar2, RIGHT, 0.25)
        tk1 = tick(at=s1.get_left() + LEFT * 0.4, s=1.1)
        cx2 = cross(s2.get_left() + LEFT * 0.4, s=0.15)
        law = text("the zero-one law", size=44, color=PRIMARY, weight="BOLD").move_to([-3.2, -2.4, 0])
        with self.voiceover(text=N("s07.b4")) as tr:
            self.play(FadeOut(clouds), bar1.v.animate.set_value(1.0), bar2.v.animate.set_value(0.0), run_time=0.7)
            self.play(FadeIn(one), FadeIn(zero), run_time=0.4)
            wait_until(self, tr, "ask")
            self.play(FadeIn(RG), FadeIn(rg_lab), run_time=0.7)
            t = tr.get_remaining_duration()
            self.play(Create(tk1), run_time=0.5)
            self.wait(max(0, t * 0.3 - 0.5))
            self.play(Create(cx2), run_time=0.5)
            self.wait(max(0, t * 0.4 - 0.5))
            self.play(FadeIn(law, shift=UP * 0.1), run_time=0.6)
            rest(self, tr)

        top = text("any two dots have a common neighbor", size=36).move_to(UP * 3.2)
        arg1 = text("true in the random graph", size=32).move_to(UP * 2.1)
        arg2 = text("so it follows from the wishes", size=32, color=PRIMARY).next_to(arg1, DOWN, 0.25)
        other = text("(otherwise: a wish-granting graph where it fails, but that graph is the random graph)",
                     size=24, color=MUTED).next_to(arg2, DOWN, 0.25)
        rules = VGroup(*[text(f"every wish with up to {k} colored dots is granted", size=30) for k in (3, 4, 5)])
        rules.arrange(DOWN, buff=0.18, aligned_edge=LEFT).move_to([-0.6, -1.15, 0])
        br = Brace(rules, direction=RIGHT, color=PRIMARY)
        br_lab = VGroup(text("finitely many", size=28, color=PRIMARY), text("wish rules", size=28, color=PRIMARY),
                        text("(compactness)", size=24, color=MUTED)).arrange(DOWN, buff=0.08).next_to(br, RIGHT, 0.2)
        big = text("in a big random graph: almost always true", size=30, color=GOOD).move_to(DOWN * 3.3)
        with self.voiceover(text=N("s07.b5")) as tr:
            self.play(FadeOut(VGroup(f1, keyl, s2, bar1, bar2, chance_lab, RG, rg_lab, one, zero, tk1, cx2, law)),
                      ReplacementTransform(s1, top), run_time=0.7)
            t = tr.time_until_bookmark("few")
            self.play(FadeIn(arg1), run_time=0.5)
            self.play(FadeIn(arg2), run_time=0.5)
            self.wait(max(0, t * 0.15))
            self.play(FadeIn(other), run_time=0.6)
            wait_until(self, tr, "few")
            self.play(FadeIn(rules, lag_ratio=0.3), run_time=0.9)
            self.play(GrowFromCenter(br), FadeIn(br_lab), run_time=0.6)
            t = tr.get_remaining_duration()
            self.wait(max(0, t * 0.4))
            self.play(FadeIn(big), run_time=0.6)
            rest(self, tr)

        fin = mini_cloud(40, [-4.1, -0.6, 0], 1.9, 1.8, 201, n_lines=70, r=0.07)
        inf = big_graph(center=np.array([4.1, -0.6, 0]), n=14, rx=1.65, ry=1.75, seed=81, rim=8, r=0.09)
        fin_lab = text("big random network", size=30, color=MUTED).next_to(fin, DOWN, 0.4)
        inf_lab = text("the random graph", size=30, color=PRIMARY).next_to(inf, DOWN, 0.25)
        inf_lab.align_to(fin_lab, DOWN)
        eq = math(r"\approx", size=90, color=MUTED).move_to([0, -0.6, 0])
        cap = text("on any one statement", size=30, color=MUTED).next_to(eq, DOWN, 0.35)
        with self.voiceover(text=N("s07.b6")) as tr:
            self.play(FadeOut(VGroup(arg1, arg2, other, rules, br, br_lab, big)), top.animate.move_to(UP * 3.2),
                      run_time=0.5)
            self.play(FadeIn(fin), FadeIn(fin_lab), FadeIn(inf), FadeIn(inf_lab), run_time=1.0)
            t = tr.get_remaining_duration()
            self.wait(max(0, t * 0.35))
            self.play(FadeIn(eq), FadeIn(cap), run_time=0.8)
            rest(self, tr)
        self.wait(0.6)
        self.play(FadeOut(VGroup(top, fin, inf, fin_lab, inf_lab, eq, cap)), run_time=0.8)


# ---------------------------------------------------------------------------
# Thumbnail
# ---------------------------------------------------------------------------


class Thumbnail(Scene):
    def construct(self):
        A = Net(ring_points(10, [-3.5, -1.35, 0], 1.85), matching_setup()[0], r=0.14, ewidth=3.5, eopacity=0.85)
        E, HE, sigma, inv, _ = matching_setup()
        B = Net(cloud_points(10, [3.5, -1.35, 0], 2.2, 1.85, seed=91, min_d=1.0), HE, r=0.14, ewidth=3.5,
                eopacity=0.85)
        eq = math("=", size=180, color=PRIMARY).move_to([0, -1.35, 0])
        t1 = text("Every infinite random graph", size=70, weight="BOLD")
        t2 = text("is the same graph", size=70, weight="BOLD", color=PRIMARY)
        t3 = text("(with probability 1)", size=40, color=MUTED)
        VGroup(t1, t2, t3).arrange(DOWN, buff=0.15).move_to(UP * 2.55)
        self.add(A, B, eq, t1, t2, t3)
