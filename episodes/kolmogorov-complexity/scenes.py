"""Most strings can't be compressed: Kolmogorov complexity."""

import random

import numpy as np
from manim import *
from manim_voiceover import VoiceoverScene

from mathvid import layout  # noqa: F401  must come before scene code runs
from mathvid.anim import rest, rt, wait_until
from mathvid.code import PANEL_BG, CodePanel, mono
from mathvid.layout import FH, FW
from mathvid.orders import cross, tick
from mathvid.script import Script
from mathvid.style import (BAD, BG, FG, GOOD, MUTED, PRIMARY, SECONDARY, TERTIARY, math, text,
                           title_card)
from mathvid.voice import get_speech_service

N = Script(__file__)

TITLE = "Kolmogorov complexity"
RAND_C = SECONDARY  # "random"


def frac_time(tr, f):
    return rt(tr.duration * f)


def rand_bits(n, seed):
    rng = random.Random(seed)
    return "".join(rng.choice("01") for _ in range(n))


ZO = "01" * 50
MESSY = rand_bits(100, 11)
X_SHORT = "1101000111"


# ---------------------------------------------------------------------------
# Shared builders (also used by shorts.py)
# ---------------------------------------------------------------------------


def bit_block(s, per_line=50, size=22, color=FG):
    rows = [s[i:i + per_line] for i in range(0, len(s), per_line)]
    return VGroup(*[mono(r, size, color) for r in rows]).arrange(DOWN, buff=0.12, aligned_edge=LEFT)


def tag(s, size=28, color=MUTED, **kw):
    return text(s, size=size, color=color, **kw)


def file_icon(w=1.0, h=1.3, color=FG, noise=False, seed=0, label=None, label_size=22):
    fold = min(w, h) * 0.26
    body = Polygon([-w / 2, h / 2, 0], [w / 2 - fold, h / 2, 0], [w / 2, h / 2 - fold, 0],
                   [w / 2, -h / 2, 0], [-w / 2, -h / 2, 0], color=color, stroke_width=3)
    body.set_fill(BG, 1)
    flap = VMobject(color=color, stroke_width=3).set_points_as_corners(
        [[w / 2 - fold, h / 2, 0], [w / 2 - fold, h / 2 - fold, 0], [w / 2, h / 2 - fold, 0]])
    g = VGroup(body, flap)
    if noise:
        rng = random.Random(seed)
        cols, rows = 5, 7
        cw, ch = (w - 0.3) / cols, (h - 0.4) / rows
        sq = VGroup()
        for r in range(rows):
            for c in range(cols):
                if rng.random() < 0.5:
                    s = Square(min(cw, ch) * 0.8, stroke_width=0).set_fill(color, 0.85)
                    s.move_to([-w / 2 + 0.15 + cw * (c + 0.5), h / 2 - 0.3 - ch * (r + 0.5), 0])
                    sq.add(s)
        g.add(sq)
    else:
        ls = VGroup()
        n = 4
        for i in range(n):
            x1 = w / 2 - 0.18 - (0.25 if i == n - 1 else 0)
            y = h / 2 - 0.4 - i * (h - 0.6) / n
            ls.add(Line([-w / 2 + 0.18, y, 0], [x1 - (fold * 0.6 if i == 0 else 0), y, 0], color=color,
                        stroke_width=3))
        g.add(ls)
    if label:
        g.add(tag(label, size=label_size).next_to(body, DOWN, 0.15))
    return g


def compressor(w=2.8, h=1.6, size=34):
    box = RoundedRectangle(corner_radius=0.2, width=w, height=h, color=PRIMARY, stroke_width=4)
    box.set_fill(PANEL_BG, 1)
    lab = text("compressor", size=size, color=PRIMARY)
    lab.scale_to_fit_width(min(lab.width, w - 0.4)).move_to(box)
    g = VGroup(box, lab)
    g.set_z_index(3)
    g.box, g.lab = box, lab
    return g


def run_through(scene, comp, f_in, f_out, total, gap=1.6):
    """f_in slides into the compressor from the left, f_out comes out on the right."""
    f_in.move_to(comp.get_left() + LEFT * (gap + f_in.width / 2))
    f_out.move_to(comp)
    t = max(1.2, total)
    scene.play(FadeIn(f_in, shift=RIGHT * 0.3), run_time=0.25 * t)
    scene.play(f_in.animate.move_to(comp), run_time=0.3 * t)
    scene.remove(f_in)
    scene.add(f_out)
    scene.play(f_out.animate.move_to(comp.get_right() + RIGHT * (gap + f_out.width / 2)), run_time=0.45 * t)


def mt(*parts, size=40, color=FG, buff=0.16):
    """Words and math on one line: strings starting with "$" are math, others are words."""
    mobs = []
    for p in parts:
        if isinstance(p, Mobject):
            mobs.append(p)
        elif p.startswith("$"):
            mobs.append(math(p[1:], size=size * 1.15, color=color))
        else:
            mobs.append(text(p, size=size, color=color))
    return VGroup(*mobs).arrange(RIGHT, buff=buff)


def kdef(size=40):
    return mt("$K(x) =", "length of the shortest program that prints", "$x", size=size)


def str_col(strings, size=30, color=FG, buff=0.16):
    return VGroup(*[empty_str(size) if s == "" else mono(s, size, color) for s in strings]).arrange(DOWN, buff=buff)


def empty_str(size=30, color=MUTED):
    return text("(empty)", size=size * 0.85, color=color)


def all_strings(n):
    return [format(i, f"0{n}b") for i in range(2 ** n)] if n else [""]


def shorter_strings(n):
    out = []
    for k in range(n):
        out += all_strings(k)
    return out


class OutputSlots(VGroup):
    """Outputs of length 0..n as slots in rows, with a chip (a file) sitting in each."""

    def __init__(self, n=3, cell_w=1.15, cell_h=0.62, size=26, row_buff=0.45, col_buff=0.14,
                 row_labels=True, label_size=26):
        super().__init__()
        self.rows, self.chips, self.slots = VGroup(), {}, {}
        for k in range(n + 1):
            row = VGroup()
            for s in all_strings(k):
                slot = RoundedRectangle(corner_radius=0.1, width=cell_w, height=cell_h, color=MUTED,
                                        stroke_width=2)
                row.add(slot)
                self.slots[s] = slot
            row.arrange(RIGHT, buff=col_buff)
            self.rows.add(row)
        self.rows.arrange(DOWN, buff=row_buff)
        self.add(self.rows)
        self.labels = VGroup()
        if row_labels:
            for k, row in enumerate(self.rows):
                lab = tag(f"{k} bit" + ("" if k == 1 else "s"), size=label_size)
                lab.next_to(self.rows, LEFT, 0.4).match_y(row)
                self.labels.add(lab)
            self.add(self.labels)
        for s, slot in self.slots.items():
            c = chip(s, cell_w - 0.12, cell_h - 0.12, size)
            c.move_to(slot)
            self.chips[s] = c
        self.chip_group = VGroup(*self.chips.values())
        self.add(self.chip_group)


def chip(s, w, h, size, color=FG):
    box = RoundedRectangle(corner_radius=0.08, width=w, height=h, stroke_width=0).set_fill("#2A2F3A", 1)
    lab = empty_str(size * 0.75) if s == "" else mono(s, size, color)
    lab.scale_to_fit_width(min(lab.width, w - 0.1)).move_to(box)
    g = VGroup(box, lab)
    g.box, g.lab = box, lab
    return g


def fraction_bar(w=10.0, h=0.7, sliver=0.1, size=28):
    whole = Rectangle(width=w, height=h, stroke_color=RAND_C, stroke_width=3).set_fill(RAND_C, 0.25)
    sl = Rectangle(width=sliver, height=h, stroke_width=0).set_fill(PRIMARY, 1)
    sl.align_to(whole, LEFT)
    g = VGroup(whole, sl)
    g.whole, g.sl = whole, sl
    return g


def magnifier(r=0.55, color=FG):
    ring = Circle(radius=r, color=color, stroke_width=6)
    handle = Line(ring.point_at_angle(-PI / 4), ring.point_at_angle(-PI / 4) + (DOWN + RIGHT) * r * 0.9,
                  color=color, stroke_width=10)
    return VGroup(ring, handle)


def spinner(size=40, color=SECONDARY):
    s = math(r"\circlearrowright", size=size, color=color)
    return s


def berry_phrase(size=40, width=None):
    lines = VGroup(text("the smallest number that cannot be", size=size),
                   text("described in under sixty letters", size=size)).arrange(DOWN, buff=0.25)
    if width:
        lines.scale_to_fit_width(min(lines.width, width))
    return lines


def letter_count(scene, phrase, counter_pos, run_time, size=48):
    glyphs = [g for line in phrase for g in line if len(g.points) > 0]
    vt = ValueTracker(0)
    lab = text("letters:", size=size * 0.7, color=MUTED).move_to(counter_pos, aligned_edge=RIGHT)
    num = Integer(0, font_size=size, color=PRIMARY)
    anchor = lab.get_right() + RIGHT * 0.25

    def upd(m):
        m.set_value(int(round(vt.get_value())))
        m.move_to(anchor, aligned_edge=LEFT)

    num.add_updater(upd)
    upd(num)
    scene.add(num, lab)
    anims = [g.animate.set_color(PRIMARY) for g in glyphs]
    scene.play(vt.animate.set_value(len(glyphs)), LaggedStart(*anims, lag_ratio=0.6),
               run_time=run_time, rate_func=linear)
    num.clear_updaters()
    num.set_value(len(glyphs))
    return VGroup(lab, num)


P_K = [
    "def K(x): ...",
    "L = ...",
    "for x in all_strings():",
    "    if K(x) > L:",
    "        print(x)",
    "        stop()",
]


def k_program(L="...", size=30):
    lines = list(P_K)
    lines[1] = f"L = {L}"
    return CodePanel(lines, size=size, min_width=mono(P_K[2], size).width)


P_PROOF = [
    "axioms = [...]",
    "L = 1000000000",
    "for p in all_proofs(axioms):",
    "    if p proves K(x) > L:",
    "        print(x)",
    "        stop()",
]


def proof_program(size=30):
    return CodePanel(P_PROOF, size=size)


def split_braces(panel, fixed_lines, l_line, fixed_label, size=28, side=RIGHT):
    """A brace over the fixed lines and one over the L line, labelled."""
    fixed = VGroup(*[panel.line(i) for i in fixed_lines])
    lbit = panel.line(l_line)
    lb = SurroundingRectangle(lbit, color=PRIMARY, buff=0.08, stroke_width=3, corner_radius=0.05)
    lt = mt(r"$\approx \log_2 L", "bits", size=size, color=PRIMARY)
    br = Brace(panel.bg, side, color=MUTED)
    ft = tag(fixed_label, size=size, color=FG)
    return lb, lt, br, ft


def length_bars(prog_fixed=1.6, prog_l=0.35, l_len=9.0, size=26, fixed_label="fixed part",
                l_label="L"):
    """Program length (fixed + L digits) against a much longer bar for L."""
    f = Rectangle(width=prog_fixed, height=0.42, stroke_width=0).set_fill(MUTED, 1)
    p = Rectangle(width=prog_l, height=0.42, stroke_width=0).set_fill(PRIMARY, 1).next_to(f, RIGHT, 0)
    prog = VGroup(f, p)
    lbar = Rectangle(width=l_len, height=0.42, stroke_width=0).set_fill(BAD, 0.75)
    lbar.next_to(prog, DOWN, 0.75).align_to(prog, LEFT)
    plab = tag("this program", size=size, color=FG).next_to(prog, UP, 0.15).align_to(prog, LEFT)
    llab = tag(l_label, size=size, color=FG).next_to(lbar, UP, 0.15).align_to(lbar, LEFT)
    g = VGroup(prog, lbar, plab, llab)
    g.prog, g.lbar, g.plab, g.llab = prog, lbar, plab, llab
    return g


def contra_pair(size=30, out_bits="0110100110010111", out_lab="K > L", prog_lab="length < L"):
    prog = CodePanel(["(the program)"], size=size, highlight=False)
    out = mono(out_bits, size + 2, PRIMARY)
    arr = Arrow(LEFT, RIGHT, color=MUTED, stroke_width=4)
    row = VGroup(prog, arr, out).arrange(RIGHT, buff=0.35)
    pl = mt("length", "$< L", size=size, color=GOOD).next_to(prog, DOWN, 0.3)
    ol = math(r"K > L", size=size + 6, color=BAD).next_to(out, DOWN, 0.3)
    g = VGroup(row, pl, ol)
    g.row, g.prog, g.out, g.arr, g.pl, g.ol = row, prog, out, arr, pl, ol
    return g


def coin_strip(n=160, seed=5, size=26, chunk=40):
    bits = rand_bits(n, seed)
    parts = [mono(bits[i:i + chunk], size, FG) for i in range(0, n, chunk)]
    g = VGroup(*parts).arrange(RIGHT, buff=0)
    for a, b in zip(parts, parts[1:]):
        b.next_to(a, RIGHT, buff=mono("00", size).width - 2 * mono("0", size).width + 0.02)
        b.align_to(a, DOWN)
    return g


def chaitin_line(w=11.0, size=26):
    ax = Arrow(LEFT * w / 2, RIGHT * w / 2, color=MUTED, stroke_width=4, buff=0, tip_length=0.25)
    lab = tag("K", size=size + 4).next_to(ax, RIGHT, 0.15)
    lx = -w / 2 + w * 0.3
    mark = Line([lx, -0.25, 0], [lx, 0.25, 0], color=PRIMARY, stroke_width=6)
    ml = math("L", size=size + 12, color=PRIMARY).next_to(mark, DOWN, 0.15)
    g = VGroup(ax, lab, mark, ml)
    g.ax, g.mark, g.ml, g.lx = ax, mark, ml, lx
    return g


def unprovable_card(s, size=30, color=PRIMARY, note="true, but no proof"):
    body = text(s, size=size)
    box = SurroundingRectangle(body, buff=0.3, corner_radius=0.15, color=color, stroke_width=3)
    nt = tag(note, size=size * 0.8, color=color).next_to(box, DOWN, 0.15)
    return VGroup(box, body, nt)


# ---------------------------------------------------------------------------
# s01 Hook
# ---------------------------------------------------------------------------


class S01Hook(VoiceoverScene):
    def construct(self):
        self.set_speech_service(get_speech_service())
        comp = compressor().move_to(UP * 0.3)
        with self.voiceover(text=N("s01.b1")) as tr:
            self.play(FadeIn(comp), run_time=0.5)
            tf = file_icon(1.1, 1.4, label="notes.txt")
            tf_out = file_icon(0.75, 0.95, label="notes.zip", label_size=20)
            run_through(self, comp, tf, tf_out, min(2.2, tr.time_until_bookmark("bigger") - 0.6))
            wait_until(self, tr, "bigger")
            nf = file_icon(1.1, 1.4, noise=True, seed=3, label="noise.bin")
            nf_out = file_icon(1.2, 1.52, noise=True, seed=3, color=BAD, label="noise.zip", label_size=20)
            self.play(FadeOut(tf_out), run_time=0.3)
            run_through(self, comp, nf, nf_out, 2.0)
            plus = text("+1 byte", size=34, color=BAD).next_to(nf_out, UP, 0.25)
            self.play(FadeIn(plus, shift=UP * 0.2), run_time=0.4)
            rest(self, tr)

        nab = text("not a bug", size=52, weight="BOLD").move_to(DOWN * 2.0)
        sub = tag("not enough short files to go around", size=34).next_to(nab, DOWN, 0.35)
        with self.voiceover(text=N("s01.b2")) as tr:
            self.play(FadeIn(nab, scale=1.1), run_time=0.6)
            self.wait(frac_time(tr, 0.25))
            self.play(FadeIn(sub, shift=UP * 0.15), run_time=0.6)
            rest(self, tr)

        a = bit_block(ZO, size=26)
        b = bit_block(MESSY, size=26)
        pair = VGroup(a, b).arrange(DOWN, buff=0.9).move_to(UP * 0.2)
        ca = mt("chance", "$1/2^{100}", size=28, color=MUTED).next_to(a, DOWN, 0.15)
        cb = mt("chance", "$1/2^{100}", size=28, color=MUTED).next_to(b, DOWN, 0.15)
        with self.voiceover(text=N("s01.b3")) as tr:
            self.play(FadeOut(VGroup(nab, sub, comp, nf_out, plus)), run_time=0.4)
            self.play(FadeIn(a, shift=RIGHT * 0.3), run_time=0.6)
            self.play(FadeIn(b, shift=RIGHT * 0.3), run_time=0.6)
            wait_until(self, tr, "equal")
            self.play(FadeIn(ca), FadeIn(cb), run_time=0.6)
            self.wait(frac_time(tr, 0.12))
            self.play(Indicate(b, color=SECONDARY, scale_factor=1.03), run_time=1.0)
            rest(self, tr)

        short = text('"01, fifty times"', size=48, color=PRIMARY).move_to(a)
        q = text("?", size=72, color=SECONDARY).next_to(b, RIGHT, 0.3)
        with self.voiceover(text=N("s01.b4")) as tr:
            wait_until(self, tr, "short")
            self.play(FadeOut(ca), ReplacementTransform(a, short), run_time=1.0)
            self.wait(frac_time(tr, 0.15))
            self.play(FadeIn(q, scale=1.3), FadeOut(cb), run_time=0.6)
            self.wait(frac_time(tr, 0.2))
            rnd = tag("random", size=40, color=RAND_C).next_to(b, DOWN, 0.3)
            self.play(FadeIn(rnd, shift=UP * 0.15), run_time=0.6)
            rest(self, tr)
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.5)
        title_card(self, TITLE)


# ---------------------------------------------------------------------------
# s02 Descriptions
# ---------------------------------------------------------------------------


class S02Descriptions(VoiceoverScene):
    def construct(self):
        self.set_speech_service(get_speech_service())
        prog = CodePanel(['print("01" * 50)'], size=36).move_to(LEFT * 3.4 + UP * 0.9)
        out = bit_block(ZO, per_line=25, size=24).move_to(RIGHT * 3.3 + UP * 0.9)
        arr = Arrow(prog.get_right(), out.get_left(), buff=0.25, color=MUTED, stroke_width=4)
        pbits = mono(rand_bits(26, 21), 26, PRIMARY).next_to(prog, DOWN, 0.7)
        br = Brace(pbits, DOWN, color=MUTED)
        bl = tag("length = number of bits", size=28).next_to(br, DOWN, 0.1)
        with self.voiceover(text=N("s02.b1")) as tr:
            self.play(FadeIn(prog, shift=RIGHT * 0.2), run_time=0.7)
            self.play(GrowArrow(arr), FadeIn(out, shift=RIGHT * 0.2), run_time=0.8)
            self.wait(frac_time(tr, 0.2))
            self.play(TransformFromCopy(prog.lines, pbits), run_time=1.0)
            self.play(GrowFromCenter(br), FadeIn(bl), run_time=0.7)
            rest(self, tr)

        kd = kdef(size=40).move_to(DOWN * 2.6)
        with self.voiceover(text=N("s02.b2")) as tr:
            wait_until(self, tr, "K")
            self.play(Write(kd), run_time=min(2.0, max(0.8, tr.get_remaining_duration() - 0.5)))
            rest(self, tr)

        kd_small = kdef(size=34).to_edge(UP, buff=0.6)
        k1 = VGroup(math(r"K(", size=44), mono("0101...01", 32), math(r")", size=44),
                    mt("$=", "small", size=40, color=GOOD)).arrange(RIGHT, buff=0.08).move_to(UP * 1.2)
        pi_s = mt("first million digits of", r"$\pi", size=34)
        pi_p = CodePanel(["digits_of_pi(1000000)"], size=30)
        pi_k = mt("$K =", "small", size=36, color=GOOD)
        pi_row = VGroup(pi_s, pi_p, pi_k).arrange(RIGHT, buff=0.5).move_to(DOWN * 0.9)
        pi_row.scale_to_fit_width(min(pi_row.width, FW - 1.2))
        with self.voiceover(text=N("s02.b3")) as tr:
            self.play(FadeOut(VGroup(prog, arr, out, pbits, br, bl)), ReplacementTransform(kd, kd_small),
                      run_time=0.8)
            self.play(FadeIn(k1, shift=UP * 0.2), run_time=0.6)
            wait_until(self, tr, "pi")
            self.play(FadeIn(pi_s), run_time=0.5)
            self.play(FadeIn(pi_p, shift=LEFT * 0.2), run_time=0.5)
            self.play(FadeIn(pi_k), run_time=0.4)
            rest(self, tr)

        pp = CodePanel(['print("1101000111...")'], size=34).move_to(UP * 0.9)
        bound = mt("$K(x) \\le", "length of", "$x", "$+\\, c", size=44).next_to(pp, DOWN, 0.8)
        bound[3].set_color(PRIMARY)
        with self.voiceover(text=N("s02.b4")) as tr:
            self.play(FadeOut(VGroup(k1, pi_row)), run_time=0.5)
            wait_until(self, tr, "print")
            self.play(FadeIn(pp, shift=UP * 0.2), run_time=0.7)
            self.wait(frac_time(tr, 0.15))
            self.play(Write(bound), run_time=1.2)
            rest(self, tr)

        la = VGroup(RoundedRectangle(corner_radius=0.15, width=3.4, height=1.3, color=SECONDARY, stroke_width=3),
                    text("language A", size=34, color=SECONDARY))
        lb = VGroup(RoundedRectangle(corner_radius=0.15, width=3.4, height=1.3, color=TERTIARY, stroke_width=3),
                    text("language B", size=34, color=TERTIARY))
        for g in (la, lb):
            g[1].move_to(g[0])
        langs = VGroup(la, lb).arrange(RIGHT, buff=3.2).move_to(UP * 0.6)
        top = CurvedArrow(la.get_top() + UP * 0.1, lb.get_top() + UP * 0.1, angle=-PI / 4, color=MUTED,
                          stroke_width=4)
        bot = CurvedArrow(lb.get_bottom() + DOWN * 0.1, la.get_bottom() + DOWN * 0.1, angle=-PI / 4,
                          color=MUTED, stroke_width=4)
        tl = tag("translator", size=28).next_to(top, UP, 0.1)
        bl2 = tag("translator", size=28).next_to(bot, DOWN, 0.1)
        fixed = text("K changes by at most a fixed amount", size=38, color=PRIMARY).to_edge(DOWN, buff=0.8)
        with self.voiceover(text=N("s02.b5")) as tr:
            self.play(FadeOut(VGroup(pp, bound)), run_time=0.5)
            self.play(FadeIn(la), FadeIn(lb), run_time=0.7)
            self.play(Create(top), FadeIn(tl), run_time=0.7)
            self.play(Create(bot), FadeIn(bl2), run_time=0.7)
            self.wait(frac_time(tr, 0.15))
            self.play(FadeIn(fixed, shift=UP * 0.2), run_time=0.7)
            rest(self, tr)

        comp = VGroup(text("compressible:", size=48, color=PRIMARY),
                      mt("$K(x) <", "length of", "$x", size=48)).arrange(RIGHT, buff=0.4).move_to(UP * 0.3)
        sub = tag("some program, shorter than x, prints x", size=34).next_to(comp, DOWN, 0.5)
        with self.voiceover(text=N("s02.b6")) as tr:
            self.play(FadeOut(VGroup(la, lb, top, bot, tl, bl2, fixed)), run_time=0.5)
            wait_until(self, tr, "comp")
            self.play(FadeIn(comp, shift=UP * 0.2), run_time=0.8)
            self.wait(frac_time(tr, 0.15))
            self.play(FadeIn(sub), run_time=0.6)
            rest(self, tr)
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.5)


# ---------------------------------------------------------------------------
# s03 Counting
# ---------------------------------------------------------------------------


def eight_vs_seven(size=34, buff=0.13, gap=4.2):
    right = str_col(all_strings(3), size=size, buff=buff)
    left = str_col(shorter_strings(3), size=size, buff=buff)
    left.match_y(right)
    VGroup(left, right).arrange(RIGHT, buff=gap)
    left.align_to(right, UP).shift(DOWN * (right.height - left.height) / 2 * 0)
    rl = tag("strings of length 3", size=28).next_to(right, UP, 0.35)
    ll = tag("shorter programs", size=28).next_to(left, UP, 0.35)
    rl.match_y(ll)
    return left, right, ll, rl


def map_arrows(left, right, skip=5):
    arrs = VGroup()
    targets = [i for i in range(len(right)) if i != skip]
    for l, ti in zip(left, targets):
        arrs.add(Arrow(l.get_right(), right[ti].get_left(), buff=0.15, color=MUTED, stroke_width=3,
                       tip_length=0.15, max_tip_length_to_length_ratio=0.08))
    return arrs


class S03Counting(VoiceoverScene):
    def construct(self):
        self.set_speech_service(get_speech_service())
        left, right, ll, rl = eight_vs_seven()
        VGroup(left, right, ll, rl).move_to(DOWN * 0.1)
        q = text("how many strings are compressible?", size=40).move_to(UP * 0.3)
        with self.voiceover(text=N("s03.b1")) as tr:
            self.play(FadeIn(q), run_time=0.6)
            self.wait(frac_time(tr, 0.3))
            self.play(FadeOut(q), FadeIn(rl),
                      LaggedStart(*[FadeIn(s, shift=LEFT * 0.2) for s in right], lag_ratio=0.12), run_time=1.2)
            wait_until(self, tr, "eight")
            n8 = math("8", size=60, color=PRIMARY).next_to(right, RIGHT, 0.6)
            self.play(FadeIn(n8, scale=1.3), run_time=0.4)
            rest(self, tr)

        arrs = map_arrows(left, right, skip=5)
        with self.voiceover(text=N("s03.b2")) as tr:
            self.play(FadeIn(ll), FadeIn(left[0]), run_time=0.6)
            self.play(FadeIn(left[1:3]), run_time=0.6)
            self.play(FadeIn(left[3:7]), run_time=0.6)
            wait_until(self, tr, "seven")
            n7 = math("7", size=60, color=SECONDARY).next_to(left, LEFT, 0.6)
            self.play(FadeIn(n7), run_time=0.4)
            self.play(LaggedStart(*[GrowArrow(a) for a in arrs], lag_ratio=0.15), run_time=1.6)
            self.play(right[5].animate.set_color(RAND_C).scale(1.15), run_time=0.6)
            box = SurroundingRectangle(right[5], color=RAND_C, buff=0.1)
            self.play(Create(box), run_time=0.5)
            rest(self, tr)

        gen = VGroup(mt("$2^n", "strings of length", "$n", size=44),
                     mt("$1 + 2 + 4 + \\dots + 2^{n-1} =", "$2^n - 1", "shorter programs", size=40)
                     ).arrange(DOWN, buff=0.7).move_to(UP * 0.8)
        gen[0][0].set_color(PRIMARY)
        gen[1][1].set_color(SECONDARY)
        concl = text("at every length, at least one string can't be compressed", size=34, color=RAND_C)
        concl.next_to(gen, DOWN, 0.9)
        with self.voiceover(text=N("s03.b3")) as tr:
            self.play(FadeOut(VGroup(left, right, ll, rl, arrs, n8, n7, box)), run_time=0.5)
            self.play(FadeIn(gen[0], shift=UP * 0.2), run_time=0.7)
            self.play(FadeIn(gen[1], shift=UP * 0.2), run_time=0.9)
            wait_until(self, tr, "left")
            self.play(FadeIn(concl, shift=UP * 0.2), run_time=0.7)
            rest(self, tr)

        bar = fraction_bar(w=11.0, h=0.8, sliver=0.12).move_to(DOWN * 0.2)
        btitle = tag("all strings of length n", size=30).next_to(bar, UP, 0.3).align_to(bar, LEFT)
        sl_lab = text("shortened by 10 bits: fewer than 1 in 500", size=30, color=PRIMARY)
        sl_lab.next_to(bar, DOWN, 0.9).align_to(bar, LEFT)
        sl_arr = Arrow(sl_lab.get_top() + RIGHT * 0.2, bar.sl.get_bottom(), buff=0.08, color=PRIMARY,
                       stroke_width=3, tip_length=0.15)
        rnd = text("random", size=44, color=RAND_C, weight="BOLD").move_to(bar.whole).shift(RIGHT * 0.5)
        with self.voiceover(text=N("s03.b4")) as tr:
            self.play(FadeOut(VGroup(gen, concl)), run_time=0.5)
            self.play(FadeIn(btitle), GrowFromEdge(bar.whole, LEFT), run_time=0.9)
            wait_until(self, tr, "frac")
            self.play(FadeIn(bar.sl), GrowArrow(sl_arr), FadeIn(sl_lab), run_time=0.8)
            self.wait(frac_time(tr, 0.15))
            self.play(FadeIn(rnd, scale=1.1), run_time=0.7)
            rest(self, tr)

        sl = OutputSlots(n=3).move_to(DOWN * 0.5)
        lg_slot = RoundedRectangle(corner_radius=0.1, width=0.9, height=0.5, color=MUTED, stroke_width=2)
        lg_chip = chip("", 0.9, 0.5, 18)
        lg_chip.lab.set_opacity(0)
        legend = VGroup(VGroup(lg_slot, tag("an output", size=32)).arrange(RIGHT, buff=0.2),
                        VGroup(lg_chip, tag("a file, sitting at its output", size=32)).arrange(RIGHT, buff=0.2)
                        ).arrange(RIGHT, buff=0.9).to_edge(UP, buff=0.5)
        with self.voiceover(text=N("s03.b5")) as tr:
            self.play(FadeOut(VGroup(bar, btitle, sl_lab, sl_arr, rnd)), run_time=0.5)
            self.play(FadeIn(sl.rows), FadeIn(sl.labels), FadeIn(legend), run_time=0.7)
            wait_until(self, tr, "zip")
            self.play(LaggedStart(*[FadeIn(c, scale=0.8) for c in sl.chip_group], lag_ratio=0.06), run_time=1.2)
            wait_until(self, tr, "shortest")
            mover = sl.chips["101"]
            self.play(mover.box.animate.set_fill(PRIMARY, 1), mover.lab.animate.set_color(BG), run_time=0.4)
            self.play(mover.animate.move_to(sl.slots["01"].get_center() + UP * 0.12), run_time=0.8)
            upper = VGroup(*[sl.slots[s] for s in shorter_strings(3)])
            self.play(LaggedStart(*[Indicate(s, color=SECONDARY, scale_factor=1.08) for s in upper],
                                  lag_ratio=0.05), run_time=1.4)
            wait_until(self, tr, "grow")
            bumped = sl.chips["01"]
            self.play(bumped.animate.move_to(sl.slots["101"]), mover.animate.move_to(sl.slots["01"]), run_time=0.7)
            self.play(bumped.box.animate.set_fill(BAD, 1), run_time=0.3)
            grew = text("grew", size=30, color=BAD).next_to(sl.slots["101"], DOWN, 0.15)
            self.play(FadeIn(grew, shift=UP * 0.1), run_time=0.4)
            rest(self, tr)
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.5)


# ---------------------------------------------------------------------------
# s04 Where compressible strings come from
# ---------------------------------------------------------------------------


PALS8 = ["00000000", "00011000", "00100100", "00111100", "01000010", "01011010"]


def pal_list(size=32):
    rows = VGroup(*[mono(p, size) for p in PALS8], text("...", size=size, color=MUTED)).arrange(DOWN, buff=0.16)
    mirror = DashedLine(rows.get_top() + UP * 0.15, rows[-2].get_bottom() + DOWN * 0.1, color=PRIMARY,
                        stroke_width=3, dash_length=0.08)
    mirror.set_x(rows[0].get_center()[0])
    return rows, mirror


PAL_INDEX = [("#0", "000...000000...000"), ("#1", "000...001100...000"), ("#2", "000...010010...000"),
             ("...", None), ("#713,402,288,515,107", "101...110011...101"), ("...", None)]


def pal_index_list(size=28):
    """Palindromes of length 100 in order, with their positions; row 4 is the circled one."""
    labs = VGroup(*[text(a, size=size, color=MUTED if s is None else FG) for a, s in PAL_INDEX])
    labs.arrange(DOWN, buff=0.24, aligned_edge=RIGHT)
    rows = VGroup()
    for lab, (a, s) in zip(labs, PAL_INDEX):
        row = VGroup(lab)
        if s is not None:
            row.add(mono(s, size).next_to(labs, RIGHT, 0.5).match_y(lab))
        rows.add(row)
    return rows


class S04Patterns(VoiceoverScene):
    def construct(self):
        self.set_speech_service(get_speech_service())
        rows, mirror = pal_list(size=40)
        VGroup(rows, mirror).move_to(DOWN * 0.4)
        lab = tag("palindromes: same forwards and backwards", size=34).to_edge(UP, buff=0.6)
        q = text("which strings are compressible?", size=40).move_to(UP * 2.2)
        ex = VGroup(*[VGroup(mono(a, 32), tag(b, size=30)).arrange(RIGHT, buff=0.5)
                      for a, b in (("010101010101010...", "01 repeated"), ("000000000000000...", "all zeros"),
                                   ("110010010000111...", "pi, in binary"))]
                    ).arrange(DOWN, buff=0.35, aligned_edge=LEFT).next_to(q, DOWN, 0.7)
        rule = tag("each follows a rule that picks out only a few strings", size=32, color=PRIMARY)
        rule.next_to(ex, DOWN, 0.6)
        with self.voiceover(text=N("s04.b1")) as tr:
            self.play(FadeIn(q), run_time=0.5)
            self.play(LaggedStart(*[FadeIn(e, shift=RIGHT * 0.2) for e in ex], lag_ratio=0.3), run_time=1.2)
            self.play(FadeIn(rule), run_time=0.6)
            wait_until(self, tr, "pal")
            self.play(FadeOut(VGroup(q, ex, rule)), run_time=0.4)
            self.play(FadeIn(lab), LaggedStart(*[FadeIn(r, shift=DOWN * 0.1) for r in rows], lag_ratio=0.12),
                      run_time=1.2)
            self.play(Create(mirror), run_time=0.7)
            rest(self, tr)

        big = Square(5.0, color=MUTED, stroke_width=3).set_fill(MUTED, 0.12).move_to(LEFT * 2.5 + DOWN * 0.3)
        bl = mt("$2^{100}", "strings of length 100", size=34).next_to(big, UP, 0.25)
        small = Square(0.12, stroke_width=0).set_fill(PRIMARY, 1).move_to(big.get_corner(DL) + UR * 0.6)
        sl_ = mt("$2^{50}", "palindromes", size=34, color=PRIMARY).move_to(RIGHT * 3.6 + DOWN * 1.6)
        sa = Arrow(sl_.get_left(), small.get_right(), buff=0.12, color=PRIMARY, stroke_width=3, tip_length=0.15)
        with self.voiceover(text=N("s04.b2")) as tr:
            self.play(FadeOut(VGroup(rows, mirror, lab)), run_time=0.4)
            self.play(FadeIn(big), FadeIn(bl), run_time=0.7)
            wait_until(self, tr, "few")
            self.play(FadeIn(small, scale=3), FadeIn(sl_), run_time=0.5)
            self.play(GrowArrow(sa), run_time=0.4)
            rest(self, tr)

        ent = pal_index_list()
        ent.move_to(UP * 1.3)
        circ = SurroundingRectangle(ent[4], color=PRIMARY, buff=0.12, corner_radius=0.1)
        prog = CodePanel(["print_palindrome(100, 713402288515107)"], size=30).move_to(DOWN * 1.9)
        nb = prog.box_part(0, "713402288515107")
        nlab = text("at most 50 bits", size=28, color=PRIMARY).next_to(prog, DOWN, 0.3)
        nlab.align_to(nb, RIGHT)
        with self.voiceover(text=N("s04.b3")) as tr:
            self.play(FadeOut(VGroup(big, bl, small, sl_, sa)), run_time=0.4)
            self.play(LaggedStart(*[FadeIn(r) for r in ent], lag_ratio=0.15), run_time=1.0)
            wait_until(self, tr, "index")
            self.play(Create(circ), run_time=0.5)
            self.play(FadeIn(prog, shift=UP * 0.2), run_time=0.7)
            self.wait(frac_time(tr, 0.15))
            self.play(Create(nb), FadeIn(nlab), run_time=0.7)
            rest(self, tr)

        allr = RoundedRectangle(corner_radius=0.2, width=10.5, height=3.6, color=MUTED, stroke_width=3)
        allr.set_fill(MUTED, 0.1).move_to(UP * 0.6)
        al = tag("all strings of length n", size=28).next_to(allr, UP, 0.2).align_to(allr, LEFT)
        band = Rectangle(width=10.5, height=0.35, stroke_width=0).set_fill(PRIMARY, 0.7).move_to(allr).shift(DOWN * 0.6)
        bandl = mt("the rule: at most", "$2^{n/2}", "strings of each length", "$n", size=30,
                   color=PRIMARY).next_to(allr, DOWN, 0.3)
        long_s = Rectangle(width=8.0, height=0.4, stroke_width=0).set_fill(PRIMARY, 1).move_to(DOWN * 2.6)
        long_l = tag("a long string that follows the rule", size=26).next_to(long_s, UP, 0.12)
        half_l = tag("its description: about half as long", size=26, color=GOOD)
        with self.voiceover(text=N("s04.b4")) as tr:
            self.play(FadeOut(VGroup(ent, circ, prog, nb, nlab)), run_time=0.4)
            self.play(FadeIn(allr), FadeIn(al), run_time=0.6)
            self.wait(frac_time(tr, 0.2))
            self.play(FadeIn(band), FadeIn(bandl), run_time=0.8)
            wait_until(self, tr, "half")
            self.play(VGroup(allr, al, band).animate.shift(UP * 0.5), bandl.animate.shift(UP * 0.5),
                      FadeIn(long_s), FadeIn(long_l), run_time=0.6)
            self.play(long_s.animate.stretch_to_fit_width(4.0).align_to(long_s, LEFT).set_fill(GOOD, 1),
                      Transform(long_l, half_l.move_to(long_l).align_to(long_l, LEFT)), run_time=1.0)
            rest(self, tr)

        comp = compressor().move_to(UP * 0.3)
        with self.voiceover(text=N("s04.b5")) as tr:
            self.play(FadeOut(VGroup(allr, al, band, bandl, long_s, long_l)), FadeIn(comp), run_time=0.6)
            tf = file_icon(1.1, 1.4, label="essay.txt")
            tf_out = file_icon(0.7, 0.9, label="smaller", label_size=20)
            run_through(self, comp, tf, tf_out, min(2.2, max(1.2, tr.time_until_bookmark("noise") - 0.4)))
            wait_until(self, tr, "noise")
            nf = file_icon(1.1, 1.4, noise=True, seed=8, label="noise")
            nf_out = file_icon(1.2, 1.52, noise=True, seed=8, color=BAD, label="bigger", label_size=20)
            self.play(FadeOut(tf_out), run_time=0.3)
            run_through(self, comp, nf, nf_out, 1.8)
            rest(self, tr)
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.5)


# ---------------------------------------------------------------------------
# s05 Why not just search?
# ---------------------------------------------------------------------------


SEARCH = [
    ('print("0")', "0"),
    ('print("1")', "1"),
    ("while True: pass", None),
    ('print("01" * 5)', "0101010101"),
    ("n = 1; while n: n += 1", None),
    ('print("1101" * 2)', "11011101"),
    ('print("1101000111")', X_SHORT),
]


def search_table(size=28):
    rows = VGroup()
    for src, outp in SEARCH:
        rows.add(CodePanel([src], size=size, highlight=False, pad=0.16))
    rows.arrange(DOWN, buff=0.12, aligned_edge=LEFT)
    return rows


class S05Search(VoiceoverScene):
    def construct(self):
        self.set_speech_service(get_speech_service())
        xs = VGroup(math("x =", size=44), mono(X_SHORT, 34, PRIMARY)).arrange(RIGHT, buff=0.25).to_edge(UP, buff=0.4)
        rows = search_table(size=26).to_edge(LEFT, buff=0.7).shift(DOWN * 0.45)
        res_x = rows.get_right()[0] + 0.8
        ptr = Triangle(color=PRIMARY).set_fill(PRIMARY, 1).scale(0.15).rotate(-PI / 2)
        results = []
        with self.voiceover(text=N("s05.b1")) as tr:
            self.play(FadeIn(xs), run_time=0.5)
            wait_until(self, tr, "try")
            self.play(FadeIn(rows), run_time=0.6)
            ptr.next_to(rows[0], LEFT, 0.2)
            self.play(FadeIn(ptr), run_time=0.2)
            step = max(0.35, (tr.get_remaining_duration() - 0.8) / len(SEARCH) - 0.05)
            for i, (src, outp) in enumerate(SEARCH):
                self.play(ptr.animate.next_to(rows[i], LEFT, 0.2), run_time=min(0.3, step * 0.4))
                y = rows[i].get_center()[1]
                if outp is None:
                    r = spinner(54).move_to([res_x, y, 0])
                    r.add_updater(lambda m, dt: m.rotate(-dt * 2.5))
                elif outp == X_SHORT:
                    r = VGroup(mono(outp, 26, GOOD), tick(at=ORIGIN)).arrange(RIGHT, buff=0.3)
                    r.move_to([res_x, y, 0], aligned_edge=LEFT)
                else:
                    o = mono(outp, 26, MUTED)
                    r = VGroup(o, cross(ORIGIN, s=0.12)).arrange(RIGHT, buff=0.3).move_to([res_x, y, 0],
                                                                                          aligned_edge=LEFT)
                if outp is None:
                    r.move_to([res_x + 0.2, y, 0])
                results.append(r)
                self.play(FadeIn(r), run_time=min(0.4, step * 0.6))
            rest(self, tr)

        loop_row = rows[2]
        hl = SurroundingRectangle(VGroup(loop_row, results[2]), color=SECONDARY, buff=0.1)
        clock = text("running: 1 hour", size=32, color=MUTED).to_edge(RIGHT, buff=0.6).shift(UP * 1.6)
        b1 = text("about to print x?", size=30, color=FG)
        b2 = text("runs forever?", size=30, color=FG)
        bubbles = VGroup(*[VGroup(SurroundingRectangle(b, buff=0.2, corner_radius=0.2, color=MUTED), b)
                           for b in (b1, b2)]).arrange(DOWN, buff=0.35).next_to(clock, DOWN, 0.5)
        bubbles.align_to(clock, RIGHT)
        with self.voiceover(text=N("s05.b2")) as tr:
            wait_until(self, tr, "loop")
            self.play(Create(hl), FadeOut(ptr), run_time=0.5)
            self.play(FadeIn(clock), run_time=0.4)
            for s in ("1 day", "1 year"):
                self.wait(frac_time(tr, 0.08))
                self.play(Transform(clock, text(f"running: {s}", size=32, color=MUTED).move_to(clock)
                                    .align_to(clock, RIGHT)), run_time=0.4)
            self.play(FadeIn(bubbles[0], shift=LEFT * 0.2), run_time=0.5)
            self.play(FadeIn(bubbles[1], shift=LEFT * 0.2), run_time=0.5)
            rest(self, tr)

        hbox = VGroup(RoundedRectangle(corner_radius=0.15, width=2.2, height=1.1, color=GOOD, stroke_width=4),
                      text("halts?", size=36, color=GOOD))
        hbox[1].move_to(hbox[0])
        hbox.to_edge(RIGHT, buff=0.8).shift(UP * 0.3)
        hp = text("the halting problem: no program can decide this", size=30, color=MUTED).to_edge(DOWN, buff=0.35)
        with self.voiceover(text=N("s05.b3")) as tr:
            self.play(FadeOut(VGroup(clock, bubbles)), FadeIn(hp), run_time=0.6)
            wait_until(self, tr, "box")
            self.play(FadeIn(hbox, shift=LEFT * 0.3), run_time=0.6)
            skips = VGroup()
            for i in (2, 4):
                results[i].clear_updaters()
                s = text("never halts: skip", size=28, color=SECONDARY).move_to([res_x, results[i].get_center()[1], 0],
                                                                                aligned_edge=LEFT)
                skips.add(s)
                self.play(rows[i].line(0).animate.set_opacity(0.35), rows[i].bg.animate.set_stroke(opacity=0.35),
                          ReplacementTransform(results[i], s), run_time=0.6)
            self.play(FadeOut(hl), Indicate(VGroup(rows[6], results[6]), color=GOOD, scale_factor=1.04),
                      run_time=0.9)
            rest(self, tr)

        for r in results:
            r.clear_updaters()
        only = text("the only thing in the way: the halting problem", size=38, color=FG).move_to(UP * 0.4)
        para = text("an old paradox", size=40, color=PRIMARY).next_to(only, DOWN, 0.6)
        with self.voiceover(text=N("s05.b4")) as tr:
            self.play(FadeOut(Group(*self.mobjects)), run_time=0.6)
            self.play(FadeIn(only), run_time=0.6)
            self.wait(frac_time(tr, 0.35))
            self.play(FadeIn(para, shift=UP * 0.2), run_time=0.6)
            rest(self, tr)
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.5)


# ---------------------------------------------------------------------------
# s06 The Berry paradox
# ---------------------------------------------------------------------------


class S06Berry(VoiceoverScene):
    def construct(self):
        self.set_speech_service(get_speech_service())
        ph = berry_phrase(size=48).move_to(UP * 0.8)
        fin = tag("phrases under sixty letters: only finitely many", size=32).move_to(DOWN * 1.4)
        with self.voiceover(text=N("s06.b1")) as tr:
            self.play(FadeIn(ph[0]), run_time=0.8)
            self.play(FadeIn(ph[1]), run_time=0.8)
            self.wait(frac_time(tr, 0.15))
            self.play(FadeIn(fin, shift=UP * 0.15), run_time=0.6)
            rest(self, tr)

        with self.voiceover(text=N("s06.b2")) as tr:
            self.play(FadeOut(fin), run_time=0.4)
            wait_until(self, tr, "count")
            cnt = letter_count(self, ph, DOWN * 1.3 + LEFT * 0.3, run_time=max(1.2, tr.get_remaining_duration() - 0.9),
                               size=64)
            lt = math("< 60", size=56, color=BAD).next_to(cnt, RIGHT, 0.4)
            self.play(FadeIn(lt), run_time=0.4)
            rest(self, tr)

        fuzzy = ph[1][:9]  # "described"
        with self.voiceover(text=N("s06.b3")) as tr:
            self.play(FadeOut(VGroup(cnt, lt)), ph.animate.set_color(FG), run_time=0.5)
            self.play(fuzzy.animate.set_color(SECONDARY), run_time=0.4)
            self.play(Wiggle(fuzzy, scale_value=1.15), run_time=1.0)
            fz = tag('"described" is fuzzy', size=32, color=SECONDARY).next_to(ph, DOWN, 0.6)
            self.play(FadeIn(fz), run_time=0.5)
            self.wait(frac_time(tr, 0.15))
            prog = tag("programs: nothing fuzzy", size=32, color=PRIMARY).next_to(fz, DOWN, 0.3)
            self.play(FadeIn(prog), run_time=0.5)
            rest(self, tr)

        panel = k_program(size=34).move_to(LEFT * 2.2)
        with self.voiceover(text=N("s06.b4")) as tr:
            self.play(FadeOut(VGroup(ph, fz, prog)), run_time=0.5)
            self.play(FadeIn(panel, shift=UP * 0.2), run_time=0.8)
            wait_until(self, tr, "first")
            hl = panel.box_part(3, "if K(x) > L:")
            self.play(Create(hl), run_time=0.6)
            stops = tag("almost every string has K > L, so this stops", size=28).next_to(panel, DOWN, 0.4)
            self.play(FadeIn(stops), run_time=0.5)
            rest(self, tr)

        fixed = VGroup(panel.line(0), *[panel.line(i) for i in range(2, 6)])
        fbr = Brace(panel.bg, RIGHT, color=MUTED)
        ftx = tag("fixed part", size=30, color=FG).next_to(fbr, RIGHT, 0.2).shift(UP * 0.4)
        lbox = SurroundingRectangle(panel.line(1), color=PRIMARY, buff=0.08, corner_radius=0.05)
        ltx = mt("$L:\\ \\approx \\log_2 L", "bits", size=32, color=PRIMARY).next_to(fbr, RIGHT, 0.2).shift(DOWN * 0.4)
        with self.voiceover(text=N("s06.b5")) as tr:
            self.play(FadeOut(VGroup(hl, stops)), run_time=0.4)
            self.play(GrowFromCenter(fbr), FadeIn(ftx), fixed.animate.set_opacity(0.8), run_time=0.7)
            wait_until(self, tr, "L")
            self.play(Create(lbox), FadeIn(ltx), run_time=0.7)
            rest(self, tr)

        panel2 = k_program("1000000000", size=34).move_to(panel)
        bars = length_bars(prog_fixed=2.0, prog_l=0.3, l_len=13.0, l_label="L = a billion bits")
        bars.to_edge(LEFT, buff=0.6).shift(DOWN * 2.6)
        thirty = tag("30 bits", size=26, color=PRIMARY).next_to(bars.prog, RIGHT, 0.2)
        with self.voiceover(text=N("s06.b6")) as tr:
            self.play(ReplacementTransform(panel, panel2), FadeOut(lbox), run_time=0.8)
            lbox2 = SurroundingRectangle(panel2.line(1), color=PRIMARY, buff=0.08, corner_radius=0.05)
            self.play(Create(lbox2), Transform(ltx, tag("about 30 bits", size=32, color=PRIMARY).move_to(ltx)
                                               .align_to(ltx, LEFT)), run_time=0.6)
            grp = VGroup(panel2, lbox2, fbr, ftx, ltx)
            self.play(grp.animate.scale(0.8).to_edge(UP, buff=0.3), run_time=0.7)
            self.play(FadeIn(bars.prog), FadeIn(bars.plab), FadeIn(thirty), run_time=0.6)
            wait_until(self, tr, "short")
            self.play(GrowFromEdge(bars.lbar, LEFT), FadeIn(bars.llab), run_time=1.0)
            rest(self, tr)

        cp = contra_pair(size=30).move_to(DOWN * 0.3)
        with self.voiceover(text=N("s06.b7")) as tr:
            self.play(FadeOut(VGroup(grp, bars, thirty)), run_time=0.5)
            self.play(FadeIn(cp.row), run_time=0.7)
            self.play(FadeIn(cp.ol), run_time=0.5)
            wait_until(self, tr, "contra")
            self.play(FadeIn(cp.pl), run_time=0.5)
            x = cross(cp.arr.get_center() + UP * 1.2, s=0.4, width=10)
            self.play(Create(x), run_time=0.5)
            nk = text("no program computes K", size=44, color=BAD, weight="BOLD").next_to(cp, DOWN, 0.9)
            self.play(FadeIn(nk, shift=UP * 0.2), run_time=0.6)
            rest(self, tr)
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.5)


# ---------------------------------------------------------------------------
# s07 You can't prove it either
# ---------------------------------------------------------------------------


def scroll_strip(scene, strip, duration, dist=6.0):
    scene.play(strip.animate.shift(LEFT * dist), run_time=duration, rate_func=linear)


class S07Chaitin(VoiceoverScene):
    def construct(self):
        self.set_speech_service(get_speech_service())
        strip = coin_strip(220, seed=5, size=30)
        strip.move_to(UP * 0.5, aligned_edge=LEFT).set_x(-FW / 2 + strip.width / 2 - 0.5)
        fade_l = Rectangle(width=1.2, height=1.0, stroke_width=0).set_fill(BG, 1).move_to([-FW / 2 + 0.6, 0.5, 0])
        lab = tag("a million coin flips", size=32).move_to(UP * 1.6)
        rnd = text("almost surely random", size=36, color=RAND_C).move_to(DOWN * 0.6)
        q = text("can we prove it?", size=44, color=PRIMARY).move_to(DOWN * 2.0)
        with self.voiceover(text=N("s07.b1")) as tr:
            self.add(strip, fade_l)
            strip.add_updater(lambda m, dt: m.shift(LEFT * dt * 1.5))
            self.play(FadeIn(lab), run_time=0.5)
            self.wait(frac_time(tr, 0.3))
            self.play(FadeIn(rnd, shift=UP * 0.15), run_time=0.8)
            self.wait(frac_time(tr, 0.25))
            self.play(FadeIn(q, shift=UP * 0.15), run_time=0.8)
            rest(self, tr)
            strip.clear_updaters()

        panel = proof_program(size=32).move_to(LEFT * 2.2 + UP * 0.2)
        with self.voiceover(text=N("s07.b2")) as tr:
            self.play(FadeOut(VGroup(strip, lab, rnd, q)), run_time=0.5)
            self.remove(fade_l)
            self.play(FadeIn(panel, shift=UP * 0.2), run_time=0.8)
            wait_until(self, tr, "proofs")
            hp = panel.box_part(2, "all_proofs(axioms)")
            self.play(Create(hp), run_time=0.5)
            self.wait(frac_time(tr, 0.15))
            self.play(FadeOut(hp), run_time=0.3)
            hl = panel.box_part(3, "if p proves K(x) > L:")
            self.play(Create(hl), run_time=0.6)
            rest(self, tr)

        fbr = Brace(panel.bg, RIGHT, color=MUTED)
        ftx = VGroup(tag("axioms + proof checker", size=28, color=FG), tag("(fixed)", size=26)).arrange(DOWN, buff=0.1)
        ftx.next_to(fbr, RIGHT, 0.2).shift(UP * 0.5)
        lbox = SurroundingRectangle(panel.line(1), color=PRIMARY, buff=0.08, corner_radius=0.05)
        ltx = mt("$L:\\ \\approx \\log_2 L", "bits", size=30, color=PRIMARY).next_to(fbr, RIGHT, 0.2).shift(DOWN * 0.5)
        with self.voiceover(text=N("s07.b3")) as tr:
            self.play(FadeOut(hl), GrowFromCenter(fbr), FadeIn(ftx), run_time=0.7)
            self.play(Create(lbox), FadeIn(ltx), run_time=0.6)
            grp = VGroup(panel, fbr, ftx, lbox, ltx)
            self.wait(frac_time(tr, 0.1))
            self.play(grp.animate.scale(0.8).to_edge(UP, buff=0.3), run_time=0.6)
            bars = length_bars(prog_fixed=2.3, prog_l=0.3, l_len=13.0, l_label="L")
            bars.to_edge(LEFT, buff=0.6).shift(DOWN * 2.4)
            self.play(FadeIn(bars.prog), FadeIn(bars.plab), run_time=0.5)
            self.play(GrowFromEdge(bars.lbar, LEFT), FadeIn(bars.llab), run_time=0.8)
            proven = text("prints a string proven to need more than L", size=30, color=BAD).next_to(bars, DOWN, 0.35)
            proven.align_to(bars, LEFT)
            self.play(FadeIn(proven), run_time=0.5)
            rest(self, tr)

        stream = VGroup(*[text(f"proof #{i}", size=28, color=MUTED) for i in range(1, 13)]).arrange(DOWN, buff=0.2)
        win = Rectangle(width=2.5, height=3.6, stroke_color=MUTED, stroke_width=2).to_edge(RIGHT, buff=0.5)
        win.shift(DOWN * 0.3)
        none = mt("no proof of", "$K(x) > L,", "for any", "$x", size=34, color=FG).to_edge(DOWN, buff=0.5)
        none.set_z_index(6)
        with self.voiceover(text=N("s07.b4")) as tr:
            x = cross(proven.get_right() + RIGHT * 0.5, s=0.25)
            self.play(Create(x), run_time=0.4)
            self.wait(frac_time(tr, 0.2))
            self.play(FadeOut(VGroup(bars, proven, x)), grp.animate.to_edge(LEFT, buff=0.4).set_y(0.3), run_time=0.6)
            sp = spinner(56).next_to(win, UP, 0.2)
            sp.add_updater(lambda m, dt: m.rotate(-dt * 2.5))
            stream.move_to(win.get_top() + DOWN * 0.2, aligned_edge=UP)
            mask_t = Rectangle(width=2.8, height=6.0, stroke_width=0).set_fill(BG, 1).next_to(win, UP, 0)
            mask_b = Rectangle(width=2.8, height=8.0, stroke_width=0).set_fill(BG, 1).next_to(win, DOWN, 0)
            mask_t.set_z_index(4)
            mask_b.set_z_index(4)
            win.set_z_index(5)
            sp.set_z_index(5)
            self.add(stream, mask_t, mask_b, win, sp)
            wait_until(self, tr, "never")
            self.play(stream.animate.shift(UP * 3.0), FadeIn(none), run_time=rt(tr.get_remaining_duration()),
                      rate_func=linear)
            sp.clear_updaters()
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.5)

        who = text("Gregory Chaitin, 1970s", size=40, color=PRIMARY).to_edge(UP, buff=0.6)
        cl = chaitin_line(w=12.0).move_to(UP * 0.4)
        lnote = tag("about the size of the axioms + checker", size=26, color=PRIMARY).next_to(cl.ml, DOWN, 0.2)
        crowd = VGroup()
        rng = random.Random(4)
        for i in range(9):
            s = mono(rand_bits(8, 30 + i), 22, RAND_C)
            crowd.add(s)
        crowd.arrange_in_grid(rows=3, cols=3, buff=(0.5, 0.25))
        crowd.move_to([cl.lx + 4.2, -1.9, 0])
        ct = tag("K > L: true, no proof", size=28, color=RAND_C).next_to(crowd, UP, 0.25)
        with self.voiceover(text=N("s07.b5")) as tr:
            self.play(FadeIn(who), run_time=0.6)
            self.play(GrowArrow(cl.ax), FadeIn(cl[1]), run_time=0.7)
            self.play(Create(cl.mark), FadeIn(cl.ml), FadeIn(lnote), run_time=0.7)
            self.wait(frac_time(tr, 0.2))
            self.play(LaggedStart(*[FadeIn(s, shift=UP * 0.1) for s in crowd], lag_ratio=0.12), FadeIn(ct),
                      run_time=1.4)
            rest(self, tr)

        ab = Rectangle(width=1.4, height=0.5, stroke_width=0).set_fill(MUTED, 1)
        mb = Rectangle(width=12.0, height=0.5, stroke_width=0).set_fill(RAND_C, 0.7)
        bars = VGroup(ab, mb).arrange(DOWN, buff=1.0, aligned_edge=LEFT).to_edge(LEFT, buff=0.6).shift(DOWN * 0.2)
        al = tag("usual axioms of math + checker", size=30, color=FG).next_to(ab, RIGHT, 0.3)
        ml = tag("1,000,000 bits: our coin flips", size=30, color=FG).next_to(mb, UP, 0.15).align_to(mb, LEFT)
        no = text("no proof will ever say it's random", size=38, color=PRIMARY).to_edge(DOWN, buff=0.8)
        with self.voiceover(text=N("s07.b6")) as tr:
            self.play(FadeOut(VGroup(who, cl, lnote, crowd, ct)), FadeIn(ab), FadeIn(al), run_time=0.6)
            wait_until(self, tr, "fit")
            self.play(GrowFromEdge(mb, LEFT), FadeIn(ml), run_time=0.9)
            self.wait(frac_time(tr, 0.15))
            self.play(FadeIn(no, shift=UP * 0.2), run_time=0.6)
            rest(self, tr)

        g = unprovable_card("G has no proof in this system.", size=32, color=SECONDARY)
        gl = tag("from the incompleteness video", size=24).next_to(g, UP, 0.2)
        r = unprovable_card("this string is random", size=32, color=PRIMARY)
        pair = VGroup(VGroup(gl, g), r).arrange(RIGHT, buff=1.0).move_to(UP * 0.3)
        many = VGroup(*[unprovable_card(f"{rand_bits(10, 50 + i)} is random", size=22, color=PRIMARY, note="")
                        for i in range(4)]).arrange(RIGHT, buff=0.3).to_edge(DOWN, buff=0.7)
        many.scale_to_fit_width(min(many.width, FW - 1))
        with self.voiceover(text=N("s07.b7")) as tr:
            self.play(FadeOut(VGroup(ab, mb, al, ml, no)), run_time=0.5)
            self.play(FadeIn(gl), FadeIn(g), run_time=0.7)
            self.wait(frac_time(tr, 0.2))
            wait_until(self, tr, "random")
            self.play(FadeIn(r, shift=LEFT * 0.2), run_time=0.6)
            self.play(LaggedStart(*[FadeIn(m) for m in many], lag_ratio=0.2), run_time=1.2)
            rest(self, tr)
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.5)


# ---------------------------------------------------------------------------
# s08 Ending
# ---------------------------------------------------------------------------


def bit_wall(rows=9, cols=4, n=16, size=24, seed=100):
    g = VGroup(*[mono(rand_bits(n, seed + i), size, RAND_C) for i in range(rows * cols)])
    g.arrange_in_grid(rows=rows, cols=cols, buff=(0.7, 0.32))
    for i, s in enumerate(g):
        s.set_opacity(0.55 + 0.3 * ((i * 7) % 5) / 4)
    return g


class S08Ending(VoiceoverScene):
    def construct(self):
        self.set_speech_service(get_speech_service())
        wall = bit_wall(n=14).move_to(ORIGIN)
        wall.scale_to_fit_height(min(wall.height, FH - 0.8))
        wall.scale_to_fit_width(min(wall.width, FW - 0.8))
        mag = magnifier().move_to(wall[0])
        stops = [5, 14, 22, 31]
        with self.voiceover(text=N("s08.b1")) as tr:
            self.play(LaggedStart(*[FadeIn(s) for s in wall], lag_ratio=0.02), run_time=1.5)
            wait_until(self, tr, "name")
            mag.move_to(wall[stops[0]].get_center() + DOWN * 0.1)
            self.play(FadeIn(mag), run_time=0.3)
            per = max(0.4, (tr.get_remaining_duration() - 0.3) / len(stops))
            for i in stops:
                self.play(mag.animate.move_to(wall[i].get_center() + DOWN * 0.1), run_time=per * 0.55)
                qm = text("?", size=56, color=PRIMARY, weight="BOLD").next_to(wall[i], RIGHT, 0.08)
                self.play(FadeIn(qm, scale=1.4), run_time=per * 0.35)
            rest(self, tr)

        one = mono(rand_bits(16, 7), 40, RAND_C)
        qm = text("?", size=64, color=PRIMARY).next_to(one, RIGHT, 0.3)
        with self.voiceover(text=N("s08.b2")) as tr:
            self.play(FadeOut(Group(*[m for m in self.mobjects])), run_time=1.0)
            self.play(FadeIn(one), FadeIn(qm), run_time=0.8)
            rest(self, tr)
        self.wait(0.4)
        self.play(FadeOut(Group(*self.mobjects)), run_time=1.5)
        self.wait(0.5)


# ---------------------------------------------------------------------------
# Thumbnail
# ---------------------------------------------------------------------------


class Thumbnail(Scene):
    def construct(self):
        wall = bit_wall(rows=11, cols=4, n=16, size=26, seed=300).move_to(ORIGIN)
        wall.set_opacity(0.18)
        t1 = text("Almost every string", size=78, weight="BOLD")
        t2 = text("is random.", size=78, weight="BOLD")
        t3 = text("Name one.", size=96, weight="BOLD", color=PRIMARY)
        words = VGroup(t1, t2, t3).arrange(DOWN, buff=0.35)
        words[2].shift(DOWN * 0.25)
        words.scale_to_fit_width(min(words.width, FW - 1.6)).move_to(ORIGIN)
        self.add(wall, words)
