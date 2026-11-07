"""Vertical shorts. Render with MV_ASPECT=portrait."""

import sys
from pathlib import Path

from manim import *
from manim_voiceover import VoiceoverScene

from mathvid import layout  # noqa: F401  must come before scene code runs
from mathvid.anim import rest, rt, strike, wait_until
from mathvid.layout import SAFE_BOTTOM, SAFE_TOP
from mathvid.script import Script
from mathvid.style import BAD, FG, GOOD, MUTED, PRIMARY, SECONDARY, math, text
from mathvid.voice import get_speech_service

sys.path.insert(0, str(Path(__file__).parent))
from scenes import (  # noqa: E402
    LIST11,
    MOVES,
    PIECES,
    SPOTS,
    Fr,
    Game,
    RatLine,
    curtain,
    diagonal_walk,
    list_row,
    list_slots,
    placed_rationals,
    reveal,
    spot_line,
    table,
)

N = Script(__file__)

MID = (SAFE_TOP + SAFE_BOTTOM) / 2  # center of the safe area


def game():
    return Game(top_y=MID + 1.5, bot_y=MID - 1.2, top_unit=0.95, bot_unit=2.3, top_half=3.9,
                list_y=(MID + 3.3, MID - 3.2), list_step=0.82, list_x0=-3.3, list_n=8,
                list_size=32, lab=30, qt=6, qb=8)


def add_move(scene, g, t, b, run_time, *extra):
    """Mark both dots and draw their thread."""
    m0, m1 = g.mark(0, t), g.mark(1, b)
    th = g.thread(t, b)
    scene.play(FadeIn(m0, scale=1.5), FadeIn(m1, scale=1.5), Create(th), *extra, run_time=run_time)
    g.marks.add(m0, m1)
    g.threads.add(th)
    g.pairs.append((t, b))


# ---------------------------------------------------------------------------
# short1 The rationals in disguise
# ---------------------------------------------------------------------------


class Short1Disguise(VoiceoverScene):
    def construct(self):
        self.set_speech_service(get_speech_service())
        y = MID + 1.2
        L = RatLine(-1.3, 4.3, 1.3, y=y, qmax=7)
        nums = L.numbers(range(-1, 5), size=32)
        outside = VGroup(*[d for v, d in L.by.items() if not any(a < v < b for a, b in PIECES)])
        segs = VGroup(*[Line(L.p(a), L.p(b), color=MUTED, stroke_width=3) for a, b in PIECES])
        holes = VGroup(*[L.hollow(v) for v in range(4)])
        small = RatLine(-1.3, 4.3, 1.3, y=MID - 1.6, qmax=7)
        eq = math("=", size=90, color=PRIMARY).move_to([0, MID - 0.3, 0])
        with self.voiceover(text=N("short1.b1")) as tr:
            self.play(FadeIn(L), FadeIn(nums), run_time=0.6)
            wait_until(self, tr, "keep")
            self.play(FadeOut(outside), FadeOut(L.axis), FadeIn(segs), FadeIn(holes),
                      run_time=rt(min(1.2, tr.time_until_bookmark("same") - 0.2)))
            wait_until(self, tr, "same")
            self.play(FadeIn(eq, scale=1.5), FadeIn(small), run_time=0.5)
            rest(self, tr)

        g = game()
        g.instant(MOVES[:2])
        bad = g.thread(Fr(1), Fr(1, 3), color=BAD, width=5)
        with self.voiceover(text=N("short1.b2")) as tr:
            self.play(FadeOut(VGroup(L.dots, nums, segs, holes, eq, small)), FadeIn(g.base()), run_time=0.5)
            self.play(FadeIn(g.marks), Create(g.threads, lag_ratio=0.5),
                      run_time=rt(min(1.2, tr.time_until_bookmark("cross") - 0.1)))
            wait_until(self, tr, "cross")
            self.play(Create(bad), run_time=0.4)
            self.wait(0.4)
            self.play(FadeOut(bad), run_time=0.3)
            per = rt((tr.get_remaining_duration() - 0.3) / 2)
            for _, t, b in MOVES[2:4]:
                add_move(self, g, t, b, per)
            rest(self, tr)

        with self.voiceover(text=N("short1.b3")) as tr:
            g.strikes.submobjects.clear()
            for _, t, b in MOVES[:4]:
                g.strikes.add(g.cross(0, t), g.cross(1, b))
            self.play(FadeIn(g.list_group), FadeIn(g.strikes), run_time=0.5)
            wait_until(self, tr, "match")
            per = rt(tr.get_remaining_duration() / 2)
            for _, t, b in MOVES[4:6]:
                s = VGroup(g.cross(0, t), g.cross(1, b))
                add_move(self, g, t, b, per, Create(s))
                g.strikes.add(*s)
            rest(self, tr)

        lo, hi = Fr(7, 3), Fr(5, 2)
        reg = g.region(1, lo, hi)
        dots = VGroup(*[Dot(g.bot.p(lo + (hi - lo) * Fr(i, 8)), radius=0.06, color=GOOD) for i in range(1, 8)])
        new = Dot(g.top.p(Fr(3, 4)), radius=0.1, color=GOOD)
        th = g.thread(Fr(3, 4), (lo + hi) / 2, color=GOOD)
        far = Dot(g.top.p(Fr(3)), radius=0.1, color=GOOD)
        reg2 = g.region(1, Fr(8, 3), Fr(3))
        th2 = g.thread(Fr(3), Fr(11, 4), color=GOOD)
        with self.voiceover(text=N("short1.b4")) as tr:
            self.play(FadeOut(g.list_group), *[FadeOut(s) for s in g.strikes], run_time=0.3)
            self.remove(*g.strikes.submobjects)
            self.play(FadeIn(new, scale=2), FadeIn(reg), run_time=0.4)
            t = tr.time_until_bookmark("out")
            self.play(FadeIn(dots, lag_ratio=0.2), run_time=rt(min(1.0, t * 0.5)))
            self.play(Create(th), run_time=rt(min(0.5, t * 0.3)))
            wait_until(self, tr, "out")
            self.play(FadeOut(reg), FadeOut(dots), FadeIn(far, scale=2), FadeIn(reg2), run_time=0.4)
            self.play(Create(th2), run_time=rt(min(0.6, tr.get_remaining_duration())))
            rest(self, tr)

        curt = curtain(g, MOVES[6:])
        self.add(curt)
        with self.voiceover(text=N("short1.b5")) as tr:
            self.play(FadeOut(VGroup(g.marks, new, far, reg2, th, th2)),
                      g.threads.animate.set_stroke(width=1.3, opacity=0.6), run_time=0.4)
            wait_until(self, tr, "fast")
            self.play(UpdateFromAlphaFunc(curt, reveal(curt)),
                      run_time=rt(tr.get_remaining_duration() * 0.8), rate_func=lambda a: a**2)
            rest(self, tr)
        self.wait(0.5)


# ---------------------------------------------------------------------------
# short2 As many fractions as integers
# ---------------------------------------------------------------------------


class Short2AsMany(VoiceoverScene):
    def construct(self):
        self.set_speech_service(get_speech_service())
        y = MID - 0.3
        L = RatLine(-2.7, 2.7, 1.4, y=y, qmax=8, r=0.07, color=FG)
        ints = VGroup(*[Dot(L.p(i), radius=0.13, color=PRIMARY) for i in range(-2, 3)])
        for i in range(-2, 3):
            L.by[Fr(i)].set_opacity(0)
        nums = L.numbers(range(-2, 3), size=38)
        head = VGroup(text("fractions", size=54, weight="BOLD", color=FG),
                      text("=", size=54, weight="BOLD", color=PRIMARY),
                      text("integers", size=54, weight="BOLD", color=PRIMARY)).arrange(RIGHT, buff=0.3)
        head.move_to([0, MID + 2.4, 0])
        sub = text("exactly as many", size=38, color=MUTED).next_to(head, UP, buff=0.3)
        with self.voiceover(text=N("short2.b1")) as tr:
            self.play(FadeIn(head), FadeIn(sub), Create(L.axis), FadeIn(ints), FadeIn(nums), run_time=0.7)
            wait_until(self, tr, "haze")
            self.play(FadeIn(L.dots, lag_ratio=0.01), run_time=rt(min(1.5, tr.get_remaining_duration())))
            rest(self, tr)

        ly = MID + 3.55
        n = 9
        x0, step = -3.2, 0.74
        entries, ldots = list_row(LIST11[:n], ly, x0=x0, step=step, size=32)
        slots = list_slots(n, ly - 0.42, x0=x0, step=step, w=0.56)
        top, side, cells, rules, more = table(cols=5, rows=5, cell_w=1.12, cell_h=0.88, x=0.35, y=MID + 2.25, size=32)
        with self.voiceover(text=N("short2.b2")) as tr:
            self.play(FadeOut(VGroup(head, sub, L, ints, nums)), run_time=0.4)
            t = tr.time_until_bookmark("cell")
            self.play(Create(rules), FadeIn(top, lag_ratio=0.15), run_time=rt(t * 0.5))
            self.play(FadeIn(side, lag_ratio=0.15), FadeIn(more), run_time=rt(t * 0.4))
            wait_until(self, tr, "cell")
            order = [cells[(r, c)] for d in range(9) for r in range(5) for c in range(5) if r + c == d]
            self.play(FadeIn(VGroup(*order), lag_ratio=0.03), run_time=rt(min(2.0, tr.get_remaining_duration())))
            rest(self, tr)

        walk = list(diagonal_walk(4))
        lines = VGroup(*[Line(cells[(0, d)].get_center(), cells[(d, 0)].get_center(), color=SECONDARY,
                              stroke_width=2, stroke_opacity=0.45) for d in range(1, 5)])
        with self.voiceover(text=N("short2.b3")) as tr:
            self.play(Create(slots, lag_ratio=0.1), FadeIn(ldots), FadeIn(entries[0]), run_time=0.5)
            wait_until(self, tr, "walk")
            self.play(Create(lines, lag_ratio=0.3), run_time=0.5)
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
            self.remove(box)

        ln, pt = spot_line(y=MID - 0.5, unit=0.82, half=3.8, top=4, size=32)
        placed = placed_rationals(pt, on_spot=False, n=n)
        for g in placed:
            g[1].set_opacity(0)
        others = [m for m in self.mobjects if m not in (entries, slots, ldots) and m not in entries.submobjects]
        with self.voiceover(text=N("short2.b4")) as tr:
            self.play(*[FadeOut(m) for m in others], run_time=0.4)
            self.remove(*others)
            self.add(entries, slots, ldots)
            self.play(FadeIn(ln), FadeIn(VGroup(*[g[0] for g in placed])), run_time=0.4)
            t = tr.get_remaining_duration()
            weights = [1, 1, 1, 0.9, 0.9, 0.7, 0.7, 0.6, 0.6]
            for k, (g, s) in enumerate(zip(placed, SPOTS)):
                shift = pt(s) - g[0].get_center()
                g[1].set_opacity(1).next_to(g[0], UP, buff=0.22)
                self.play(entries[k].animate.set_color(PRIMARY),
                          g.animate(path_arc=-PI / 2 if s >= float(LIST11[k]) else PI / 2).shift(shift),
                          run_time=rt(t * weights[k] / sum(weights)))

        verdict = text("same number of dots", size=50, weight="BOLD", color=PRIMARY).move_to([0, MID - 2.3, 0])
        with self.voiceover(text=N("short2.b5")) as tr:
            wait_until(self, tr, "same")
            self.play(FadeIn(verdict, shift=UP * 0.2), run_time=rt(min(0.6, tr.get_remaining_duration())))
            rest(self, tr)
        self.wait(0.5)
