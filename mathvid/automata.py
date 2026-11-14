"""State diagrams for finite state machines: labelled dots, arrows, self-loops, runs.

    m = Machine({0: UP * 2, 1: RIGHT * 2, 2: LEFT * 2}, r=0.4)
    m.add_edge(0, 1, "1, 4, 7", bend=0.4)      # curved arrow with a label
    m.add_edge(0, 0, "0, 3, 6, 9")             # self-loop, pointing away from the middle
    m.add_start(0)                             # small arrow from nowhere
    m.add_accept(0)                            # double circle
    self.play(FadeIn(m))
    m.light(self, 0)                           # current state glows
    m.hop(self, 0, 1, run_time=0.8)            # a glow runs along the arrow to state 1

Edges sit behind the dots, so arrows can start at a dot's center without showing through.
"""

import numpy as np
from manim import (
    DOWN,
    LEFT,
    PI,
    RIGHT,
    UP,
    Arc,
    BackgroundRectangle,
    ArcBetweenPoints,
    Circle,
    Dot,
    FadeIn,
    FadeOut,
    Line,
    MoveAlongPath,
    Transform,
    VGroup,
    VMobject,
    rotate_vector,
)

from mathvid.style import BG, FG, MUTED, PRIMARY, text


def _unit(v):
    n = np.linalg.norm(v)
    return v / n if n > 1e-9 else np.array([0.0, 1.0, 0.0])


def _text_of(lab):
    return lab[1] if isinstance(lab, VGroup) and len(lab) == 2 and isinstance(lab[0], BackgroundRectangle) else lab


def _push_out(mob, p, normal, buff):
    """Place mob just beyond point p along the unit vector normal."""
    ext = abs(normal[0]) * mob.width / 2 + abs(normal[1]) * mob.height / 2
    mob.move_to(p + normal * (buff + ext))
    return mob


class Edge(VGroup):
    """One arrow (and maybe its label). `path` is the curve a glow runs along."""

    def __init__(self, arrow, path, label, label_at, normal):
        super().__init__(arrow)
        self.arrow, self.path, self.label = arrow, path, label
        self.label_at, self.normal = label_at, normal
        if label is not None:
            self.add(label)


class Machine(VGroup):
    def __init__(self, pos, labels=None, r=0.4, label_size=None, color=FG, stroke=4):
        super().__init__()
        self.pos = {k: np.array(p, dtype=float) for k, p in pos.items()}
        self.r = r
        self.middle = np.mean(list(self.pos.values()), axis=0)
        self.edges = {}
        self.edge_layer = VGroup()
        self.node_layer = VGroup()
        self.extra = VGroup()
        self.paths = VGroup()  # invisible copies of each arrow's curve, moved with the machine
        self.add(self.paths, self.edge_layer, self.node_layer, self.extra)
        self.nodes, self.circles = {}, {}
        label_size = label_size or int(r * 95)
        labels = labels or {}
        for k, p in self.pos.items():
            c = Circle(radius=r, color=color, stroke_width=stroke).set_fill(BG, 1).move_to(p)
            lab = text(labels.get(k, str(k)), size=label_size).move_to(p)
            node = VGroup(c, lab)
            self.nodes[k], self.circles[k] = node, c
            self.node_layer.add(node)
        self.lit = None

    def p(self, k):
        """Current center of state k (follows the machine when it moves)."""
        return self.circles[k].get_center()

    # -- building --------------------------------------------------------------

    def add_edge(self, a, b, label=None, bend=0.0, size=28, color=MUTED, width=3,
                 opacity=1.0, loop_dir=None, label_side=1, buff=0.12, tip=0.2, label_color=None,
                 spread=0.55, on_path=False):
        r = self.r
        A, B = self.pos[a], self.pos[b]
        if a == b:
            d = _unit(loop_dir if loop_dir is not None else A - self.middle)
            p1 = A + r * rotate_vector(d, spread)
            p2 = A + r * rotate_vector(d, -spread)
            path = ArcBetweenPoints(p1, p2, angle=-1.55 * PI)
            proj = [np.dot(path.point_from_proportion(t) - A, d) for t in np.linspace(0, 1, 41)]
            label_at = A + d * max(proj)
            normal = d
            buff = max(buff, 0.2)
        elif abs(bend) < 1e-6:
            u = _unit(B - A)
            path = Line(A + u * r, B - u * r)
            label_at = (A + B) / 2
            normal = rotate_vector(u, PI / 2) * label_side
        else:
            full = ArcBetweenPoints(A, B, angle=bend)
            C = full.get_arc_center()
            R = np.linalg.norm(A - C)
            delta = 2 * np.arcsin(min(1.0, r / (2 * R)))
            s = np.sign(bend)
            P = C + rotate_vector(A - C, s * delta)
            Q = C + rotate_vector(B - C, -s * delta)
            path = ArcBetweenPoints(P, Q, angle=bend - 2 * s * delta)
            label_at = path.point_from_proportion(0.5)
            normal = _unit(label_at - (P + Q) / 2)
        path.set_stroke(color, width, opacity)
        arrow = path.copy()
        arrow.add_tip(tip_length=tip, tip_width=tip * 0.9)
        arrow.set_stroke(color, width, opacity)
        arrow.get_tip().set_fill(color, opacity).set_stroke(color, 0, opacity)
        lab = None
        if label is not None:
            lab = text(label, size=size, color=label_color or color)
            lab.set_opacity(opacity)
            if on_path:
                lab.move_to(label_at)
                lab = VGroup(BackgroundRectangle(lab, color=BG, fill_opacity=1, buff=0.06), lab)
            else:
                _push_out(lab, label_at, normal, buff)
        path.set_stroke(opacity=0)
        self.paths.add(path)
        e = Edge(arrow, path, lab, label_at, normal)
        e.style0 = (color, width, opacity)
        self.edges[(a, b)] = e
        self.edge_layer.add(e)
        return e

    def add_start(self, k, direction=LEFT, length=0.7, label=None, size=26):
        d = _unit(np.array(direction, dtype=float))
        end = self.pos[k] + d * self.r
        start = end + d * length
        arr = Line(start, end, color=FG, stroke_width=4)
        arr.add_tip(tip_length=0.2, tip_width=0.18)
        g = VGroup(arr)
        if label:
            g.add(_push_out(text(label, size=size, color=MUTED), start, d, 0.1))
        self.start = g
        self.extra.add(g)
        return g

    def add_accept(self, k, color=FG):
        ring = Circle(radius=self.r * 0.8, color=color, stroke_width=3).move_to(self.pos[k])
        self.nodes[k].add(ring)
        return ring

    # -- running ---------------------------------------------------------------

    def light_anims(self, k, color=PRIMARY):
        out = []
        if self.lit is not None and self.lit != k:
            out.append(self.circles[self.lit].animate.set_fill(BG, 1).set_stroke(FG))
        if k is not None:
            out.append(self.circles[k].animate.set_fill(color, 0.35).set_stroke(color))
        self.lit = k
        return out

    def light(self, scene, k, run_time=0.3, color=PRIMARY):
        anims = self.light_anims(k, color)
        if anims:
            scene.play(*anims, run_time=run_time)

    def show_edge(self, a, b, color=PRIMARY, width=6):
        e = self.edges[(a, b)]
        e.arrow.set_stroke(color, width, 1)
        e.arrow.get_tip().set_fill(color, 1)
        if e.label is not None:
            _text_of(e.label).set_color(color).set_opacity(1)

    def restore_edge(self, a, b):
        e = self.edges[(a, b)]
        color, width, opacity = e.style0
        e.arrow.set_stroke(color, width, opacity)
        e.arrow.get_tip().set_fill(color, opacity)
        if e.label is not None:
            _text_of(e.label).set_color(color).set_opacity(opacity)

    def fade_edges(self, opacity):
        """Animations that set every arrow (and label) to an opacity, without filling loops."""
        out = []
        for e in self.edges.values():
            tgt = e.arrow.copy()
            tgt.set_stroke(opacity=opacity)
            tgt.get_tip().set_fill(opacity=opacity)
            out.append(Transform(e.arrow, tgt))
            if e.label is not None:
                out.append(_text_of(e.label).animate.set_opacity(opacity))
            color, width, _ = e.style0
            e.style0 = (color, width, opacity)
        return out

    def hop(self, scene, a, b, run_time=1.0, color=PRIMARY, note=None, note_size=34, keep=False):
        """Light the arrow a -> b, run a glow along it, then light b.

        note: a short string shown beside the arrow while it is lit (for arrows drawn
        without labels). keep=True leaves the arrow lit."""
        e = self.edges[(a, b)]
        lit_arrow = e.arrow.copy().set_stroke(color, 6, 1)
        lit_arrow.get_tip().set_fill(color, 1)
        glow = glow_dot(color).move_to(e.path.get_start())
        extra = []
        if note is not None:
            n = text(note, size=note_size, color=color)
            at = e.path.point_from_proportion(0.5)
            _push_out(n, at, e.normal, 0.12)
            n.set_z_index(5)
            extra.append(n)
        lit_arrow.set_z_index(2)
        glow.set_z_index(6)
        scene.play(FadeIn(lit_arrow), *[FadeIn(x) for x in extra], run_time=0.2 * run_time)
        scene.add(glow)
        scene.play(MoveAlongPath(glow, e.path), run_time=0.55 * run_time)
        out = [FadeOut(glow)] + self.light_anims(b, color)
        if not keep:
            out += [FadeOut(lit_arrow)] + [FadeOut(x) for x in extra]
        scene.play(*out, run_time=0.25 * run_time)
        if keep:
            return VGroup(lit_arrow, *extra)
        return None


def glow_dot(color=PRIMARY):
    halo = VGroup(*[Dot(radius=0.11 + 0.05 * i, color=color).set_opacity(0.35 / (i + 1))
                    for i in range(3)])
    return VGroup(halo, Dot(radius=0.1, color=color))


def ring(n, radius, center=None, start=PI / 2, clockwise=True):
    """Positions of states 0..n-1 on a circle, state 0 at the top by default."""
    c = np.zeros(3) if center is None else np.array(center, dtype=float)
    s = -1 if clockwise else 1
    return {i: c + radius * np.array([np.cos(start + s * 2 * PI * i / n),
                                      np.sin(start + s * 2 * PI * i / n), 0.0])
            for i in range(n)}


def remainder_machine(n, base=10, radius=2.6, r=0.36, center=None, labels=True, size=22,
                      color=MUTED, width=2.5, opacity=1.0, bend=0.35, digit_sep=", "):
    """The machine for remainders mod n: state r goes to (base r + d) mod n on digit d.

    Digits with the same target share one arrow. Every ordered pair that some digit
    connects gets an arrow; pairs used both ways bend apart."""
    m = Machine(ring(n, radius, center), r=r)
    targets = {}
    for q in range(n):
        for d in range(base):
            targets.setdefault((q, (base * q + d) % n), []).append(d)
    for (a, b), ds in targets.items():
        lab = digit_sep.join(str(d) for d in ds) if labels else None
        if a == b:
            m.add_edge(a, b, lab, size=size, color=color, width=width, opacity=opacity,
                       tip=0.16, spread=0.5)
        else:
            both = (b, a) in targets
            m.add_edge(a, b, lab, bend=bend if both else 0.0, size=size, color=color,
                       width=width, opacity=opacity, tip=0.16)
    m.targets = targets
    return m


def run_states(n, digits, base=10, start=0):
    """States visited by the remainder machine on a digit string, start included."""
    out = [start]
    for ch in digits:
        out.append((base * out[-1] + int(ch)) % n)
    return out
