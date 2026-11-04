"""Vertical shorts. Render with MV_ASPECT=portrait."""

import sys
from pathlib import Path

from manim import *
from manim_voiceover import VoiceoverScene

from mathvid import layout  # noqa: F401  must come before scene code runs
from mathvid.anim import morph_parts, rest, rt, wait_until
from mathvid.layout import SAFE_BOTTOM, SAFE_TOP
from mathvid.script import Script
from mathvid.style import FG, GOOD, MUTED, PRIMARY, SECONDARY, math, text
from mathvid.voice import get_speech_service

sys.path.insert(0, str(Path(__file__).parent))
from scenes import bars, plane, region_labels, regions  # noqa: E402

N = Script(__file__)

INT = r"\int_0^a"


# ---------------------------------------------------------------------------
# short1 Self-solving
# ---------------------------------------------------------------------------


class Short1SelfSolving(VoiceoverScene):
    def construct(self):
        self.set_speech_service(get_speech_service())

        title = text("An integral that\nsolves itself", size=52, weight="BOLD").move_to(UP * (SAFE_TOP - 0.9))
        q = math(INT + r" x\,dx =", r"\;?", size=60).move_to(UP * 2.2)
        note = text("allowed: derivatives,\nintegration by parts", size=30, color=MUTED).next_to(q, DOWN, buff=0.5)

        with self.voiceover(text=N("short1.b1")) as tr:
            self.play(FadeIn(title, shift=DOWN * 0.2), run_time=rt(min(1.0, tr.duration)))
            rest(self, tr)

        with self.voiceover(text=N("short1.b2")) as tr:
            self.play(FadeIn(note), run_time=0.8)
            self.play(Write(q), run_time=rt(min(1.2, tr.get_remaining_duration())))
            rest(self, tr)

        ibp = math(INT + r" p\,q'\,dx = \big[pq\big]_0^a - " + INT + r" q\,p'\,dx", size=36).move_to(
            UP * (SAFE_TOP - 0.6))
        e1 = math(INT + r" x\,dx", "=", "a^2", "-", INT + r" x\,dx", size=50).move_to(UP * 0.6)
        with self.voiceover(text=N("short1.b3")) as tr:
            self.play(FadeOut(title), FadeOut(note), q.animate.scale(0.75).move_to(UP * 3.6),
                      FadeIn(ibp), run_time=1.0)
            wait_until(self, tr, "eq")
            self.play(TransformFromCopy(ibp, e1), run_time=rt(min(1.5, tr.get_remaining_duration())))
            self.play(e1[0].animate.set_color(PRIMARY), e1[4].animate.set_color(PRIMARY), run_time=0.5)
            rest(self, tr)

        with self.voiceover(text=N("short1.b4")) as tr:
            e2 = math("2", INT + r" x\,dx", "=", "a^2", size=50).move_to(e1)
            e2[1].set_color(PRIMARY)
            e1 = morph_parts(self, e1, e2, [(0, 1), (4, 0), (1, 2), (2, 3)], run_time=1.2)
            e3 = math(INT + r" x\,dx", "=", r"\frac{a^2}{2}", size=50).move_to(e1)
            e3[2].set_color(GOOD)
            e1 = morph_parts(self, e1, e3, [(1, 0), (2, 1), ((0, 3), 2)], run_time=1.0)
            self.play(FadeOut(q), run_time=rt(min(0.5, tr.get_remaining_duration())))
            rest(self, tr)

        f1 = math(INT + r" x^2\,dx", "=", "a^3", "-", INT + r" x\cdot 2x\,dx", size=46).move_to(DOWN * 1.6)
        with self.voiceover(text=N("short1.b5")) as tr:
            per = tr.duration / 4
            self.play(Write(f1), run_time=rt(per))
            f2 = math(INT + r" x^2\,dx", "=", "a^3", "-", "2", INT + r" x^2\,dx", size=46).move_to(f1)
            f2[0].set_color(PRIMARY); f2[5].set_color(PRIMARY)
            f1 = morph_parts(self, f1, f2, [(0, 0), (1, 1), (2, 2), (3, 3), (4, (4, 5))], run_time=rt(per))
            f3 = math(INT + r" x^2\,dx", "=", r"\frac{a^3}{3}", size=46).move_to(f1)
            f3[2].set_color(GOOD)
            f1 = morph_parts(self, f1, f3, [(0, 0), (1, 1), ((2, 3, 4, 5), 2)], run_time=rt(per))
            rest(self, tr)

        col = VGroup(*[math(INT + r" x^{%d}\,dx = \frac{a^{%d}}{%d}" % (n, n + 1, n + 1) if n > 1 else
                            INT + r" x\,dx = \frac{a^2}{2}", size=42) for n in (1, 2, 3, 4)]
                     ).arrange(DOWN, buff=0.35).move_to(UP * 2.2)
        dots = math(r"\vdots", size=42).next_to(col, DOWN, buff=0.2)
        general = math(INT + r" x^n\,dx = \frac{a^{n+1}}{n+1}", size=54).next_to(dots, DOWN, buff=0.4)
        frame = SurroundingRectangle(general, color=GOOD, buff=0.2)
        with self.voiceover(text=N("short1.b6")) as tr:
            self.play(FadeOut(ibp), ReplacementTransform(e1, col[0]), ReplacementTransform(f1, col[1]), run_time=1.0)
            self.play(LaggedStart(FadeIn(col[2]), FadeIn(col[3]), FadeIn(dots), lag_ratio=0.4),
                      run_time=rt(tr.get_remaining_duration() * 0.4))
            self.play(Write(general), Create(frame), run_time=rt(min(1.5, tr.get_remaining_duration())))
            rest(self, tr)
        self.wait(1.0)


# ---------------------------------------------------------------------------
# short2 Rectangle
# ---------------------------------------------------------------------------


class Short2Rectangle(VoiceoverScene):
    def construct(self):
        self.set_speech_service(get_speech_service())

        ibp = math(r"\int p\,q'\,dx = pq - \int q\,p'\,dx", size=40).move_to(UP * (SAFE_TOP - 0.5))
        ax = plane(4.0).move_to(RIGHT * 0.5 + UP * 2.65)
        o = ax.c2p(0, 0)
        rect = DashedVMobject(Polygon(o, ax.c2p(1, 0), ax.c2p(1, 1), ax.c2p(0, 1), color=FG, stroke_width=2),
                              num_dashes=40)
        under, left, curve = regions(ax, 2)
        bw = Brace(Line(o, ax.c2p(1, 0)), DOWN, color=MUTED)
        bw_lab = math("a", size=36).next_to(bw, DOWN, buff=0.1)
        bh = Brace(Line(o, ax.c2p(0, 1)), LEFT, color=MUTED)
        bh_lab = math("a^2", size=36).next_to(bh, LEFT, buff=0.1)
        area = math(r"\text{rectangle} = a^3", size=40).move_to(DOWN * 0.55)

        with self.voiceover(text=N("short2.b1")) as tr:
            self.play(FadeIn(ibp), run_time=0.8)
            self.play(Create(ax), Create(curve), run_time=1.2)
            self.play(Create(rect), GrowFromCenter(bw), GrowFromCenter(bh), FadeIn(bw_lab), FadeIn(bh_lab),
                      run_time=1.0)
            self.play(Write(area), run_time=rt(min(1.0, tr.get_remaining_duration())))
            rest(self, tr)

        p1 = math(r"\text{under} + \text{left} = a^3", size=40).next_to(area, DOWN, buff=0.4)
        p1[0][:5].set_color(PRIMARY)
        with self.voiceover(text=N("short2.b2")) as tr:
            wait_until(self, tr, "split")
            self.play(FadeIn(under), run_time=0.7)
            self.play(FadeIn(left), run_time=0.7)
            self.play(Write(p1), run_time=rt(min(1.2, tr.get_remaining_duration())))
            rest(self, tr)

        dt = 0.05
        tt = ValueTracker(0.35)

        def make_strip():
            t = tt.get_value()
            return Polygon(ax.c2p(0, t ** 2), ax.c2p(t, t ** 2), ax.c2p(t + dt, (t + dt) ** 2),
                           ax.c2p(0, (t + dt) ** 2), stroke_color=FG, stroke_width=2, fill_color=FG,
                           fill_opacity=0.8)

        strip = always_redraw(make_strip)
        p2 = math(r"\text{left} = \int_0^a t\cdot 2t\,dt = 2A", size=40).next_to(p1, DOWN, buff=0.35)
        labels = region_labels(ax, 2)
        with self.voiceover(text=N("short2.b3")) as tr:
            per = tr.duration / 4
            self.play(FadeIn(strip), run_time=rt(per * 0.5))
            self.play(tt.animate.set_value(0.85), run_time=rt(per))
            self.play(tt.animate.set_value(0.6), run_time=rt(per * 0.5))
            self.play(FadeOut(strip), Write(p2), FadeIn(labels), run_time=rt(min(1.5, tr.get_remaining_duration())))
            rest(self, tr)

        def shares(k):
            b = bars(k + 1, height=1.3, total=3.0)
            lab = math(r"\text{under} = \tfrac{1}{%d}" % (k + 1), r"\text{ of the rectangle}", size=36)
            lab[0].set_color(PRIMARY)
            return VGroup(b, lab).arrange(DOWN, buff=0.25).move_to(DOWN * 2.05)

        sh = shares(2)
        with self.voiceover(text=N("short2.b4")) as tr:
            self.play(FadeOut(VGroup(p1, p2)), run_time=0.5)
            self.play(FadeIn(sh, shift=UP * 0.2), run_time=1.0)
            res = math(r"\text{under} = \tfrac{1}{3}\,a^3", size=44).move_to(area)
            self.play(Transform(area, res), run_time=rt(min(1.0, tr.get_remaining_duration())))
            rest(self, tr)

        def set_power(k, run_time):
            nu, nl, nc = regions(ax, k)
            new_bh = math("a^{%d}" % k, size=36).next_to(bh, LEFT, buff=0.1)
            new_area = math(r"\text{rectangle} = a^{%d}" % (k + 1), size=40).move_to(area)
            self.play(Transform(under, nu), Transform(left, nl), Transform(curve, nc),
                      Transform(labels, region_labels(ax, k)), Transform(sh, shares(k)),
                      Transform(bh_lab, new_bh), Transform(area, new_area), run_time=run_time)

        with self.voiceover(text=N("short2.b5")) as tr:
            set_power(3, rt(tr.duration * 0.45))
            set_power(4, rt(tr.get_remaining_duration()))

        rule = math(r"\int_0^a t^k\,dt = \frac{a^{k+1}}{", r"k+1", "}", size=52).move_to(sh)
        rule[1].set_color(PRIMARY)
        with self.voiceover(text=N("short2.b6")) as tr:
            self.play(FadeOut(sh[0]), ReplacementTransform(sh[1], rule), run_time=1.2)
            self.play(Indicate(rule[1], color=PRIMARY), run_time=rt(min(1.0, tr.get_remaining_duration())))
            rest(self, tr)
        self.wait(1.0)
