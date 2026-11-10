"""Vertical short. Render with MV_ASPECT=portrait. This episode has no long-form video."""

from manim import *
from manim_voiceover import VoiceoverScene

from mathvid import layout  # noqa: F401  must come before scene code runs
from mathvid.anim import rest, rt, wait_until
from mathvid.layout import SAFE_BOTTOM, SAFE_TOP
from mathvid.orders import cross, tick
from mathvid.script import Script
from mathvid.style import BAD, GOOD, MUTED, PRIMARY, SECONDARY, math, text
from mathvid.voice import get_speech_service

N = Script(__file__)

MID = (SAFE_TOP + SAFE_BOTTOM) / 2  # center of the safe area
IRR, RAT = PRIMARY, SECONDARY  # "irrational" and "rational", in words and on the fork

TOWER_Y = SAFE_TOP - 0.75  # the tower at the top of the fork
LX, RX = -1.75, 1.75  # the two columns of the fork
LABEL_Y = TOWER_Y - 1.55
WORK_Y = LABEL_Y - 1.1  # where the right branch does its algebra
A_Y, B_Y = WORK_Y - 1.1, WORK_Y - 1.85
CHECK_Y = B_Y - 0.75
NOTE_Y = SAFE_BOTTOM + 0.35


def words(main, sup, color=IRR, size=70):
    """A word raised to a word, in the text font: "irrational^irrational"."""
    w = text(main, size=size, color=color)
    s = text(sup, size=round(size * 0.6), color=color)
    s.next_to(w, RIGHT, buff=0.1).align_to(w, UP).shift(UP * 0.38)
    return VGroup(w, s)


def tower(size=110):
    return math(r"\sqrt{2}", r"^{\sqrt{2}}", size=size)


def pair(a_tex, x, size=60):
    """The two rows "a = ..." and "b = root 2" of one branch."""
    a = math(r"a = ", a_tex, size=size).move_to([x, A_Y, 0])
    b = math(r"b = ", r"\sqrt{2}", size=size).move_to([x, B_Y, 0])
    b.align_to(a, LEFT)
    return VGroup(a, b)


def check_at(x):
    return tick(at=np.array([x, CHECK_Y, 0]), s=2.3)


class Short1IrrationalPower(VoiceoverScene):
    def construct(self):
        self.set_speech_service(get_speech_service())

        # b1: the question
        q1 = words("irrational", "irrational")
        q2 = VGroup(text("=", size=84), text("rational", size=84, color=RAT), text("?", size=84))
        q2.arrange(RIGHT, buff=0.25)
        q = VGroup(q1, q2).arrange(DOWN, buff=0.5).move_to([0, MID + 1.6, 0])
        yes = text("Yes.", size=96, color=GOOD, weight="BOLD").next_to(q, DOWN, buff=1.0)
        which = text("...but which?", size=56, color=MUTED).next_to(yes, DOWN, buff=0.6)
        with self.voiceover(text=N("short1.b1")) as tr:
            self.play(FadeIn(q1, shift=DOWN * 0.2), run_time=0.6)
            self.play(FadeIn(q2, shift=DOWN * 0.2), run_time=0.5)
            wait_until(self, tr, "yes")
            self.play(FadeIn(yes, scale=1.4), run_time=0.4)
            wait_until(self, tr, "give")
            self.play(FadeIn(which), run_time=0.5)
            rest(self, tr)

        # b2: root 2, then root 2 to the root 2
        defn = VGroup(text("irrational =", size=44, color=IRR),
                      text("not a fraction of whole numbers", size=36)).arrange(DOWN, buff=0.2)
        defn.move_to([0, SAFE_TOP - 0.75, 0])
        r2 = math(r"\sqrt{2}", size=150).move_to([0, MID + 0.4, 0])
        tw = tower(150).move_to([0, MID + 0.6, 0])
        qm = text("?", size=110, color=PRIMARY, weight="BOLD").next_to(tw, DOWN, buff=0.7)
        with self.voiceover(text=N("short1.b2")) as tr:
            self.play(FadeOut(VGroup(q, yes, which)), FadeIn(defn), run_time=0.6)
            wait_until(self, tr, "root2")
            self.play(FadeIn(r2, scale=1.2), run_time=0.5)
            wait_until(self, tr, "tower")
            self.play(r2.animate.move_to(tw[0]), FadeIn(tw[1], shift=DOWN * 0.3), run_time=0.8)
            self.remove(r2)
            self.add(tw)
            self.play(FadeIn(qm, scale=1.3), run_time=0.4)
            rest(self, tr)

        # b3: the fork, and the rational branch
        top = tower(110).move_to([0, TOWER_Y, 0])
        start = top.get_bottom() + DOWN * 0.2
        legs = VGroup(*[Line(start, [x, LABEL_Y + 0.45, 0], color=MUTED, stroke_width=4) for x in (LX, RX)])
        lab_l = text("rational", size=56, color=RAT).move_to([LX, LABEL_Y, 0])
        lab_r = text("irrational", size=56, color=IRR).move_to([RX, LABEL_Y, 0])
        left = pair(r"\sqrt{2}", LX)
        ok_l = check_at(LX)
        with self.voiceover(text=N("short1.b3")) as tr:
            self.play(FadeOut(defn), FadeOut(qm), ReplacementTransform(tw, top), run_time=0.7)
            wait_until(self, tr, "fork")
            self.play(Create(legs), FadeIn(lab_l), FadeIn(lab_r), run_time=0.7)
            wait_until(self, tr, "yes1")
            self.play(FadeIn(left, shift=DOWN * 0.15), run_time=0.5)
            self.play(Create(ok_l), run_time=0.4)
            rest(self, tr)

        # b4: the irrational branch collapses to 2
        s1 = tower(80).move_to([RX, WORK_Y, 0])
        s2 = math(r"(", r"\sqrt{2}", r"^{\sqrt{2}}", r")", r"^{\sqrt{2}}", size=80).move_to([RX, WORK_Y, 0])
        s3 = math(r"\sqrt{2}", r"^{\sqrt{2}\cdot\sqrt{2}}", size=80).move_to([RX, WORK_Y, 0])
        s4 = math(r"\sqrt{2}", r"^{2}", size=80).move_to([RX, WORK_Y, 0])
        s5 = math(r"2", size=120, color=GOOD).move_to([RX, WORK_Y, 0])
        base_tag = text("new base", size=36, color=IRR).next_to(s1, DOWN, buff=0.2)
        right = pair(r"\sqrt{2}^{\sqrt{2}}", RX)
        ok_r = check_at(RX)
        with self.voiceover(text=N("short1.b4")) as tr:
            self.play(lab_r.animate.scale(1.12), legs[1].animate.set_color(IRR), run_time=0.4)
            self.play(TransformFromCopy(top, s1), run_time=0.7)
            self.play(FadeIn(base_tag), run_time=0.3)
            wait_until(self, tr, "again")
            self.play(FadeOut(base_tag), TransformMatchingShapes(s1, s2), run_time=0.7)
            wait_until(self, tr, "mult")
            self.play(TransformMatchingShapes(s2, s3), run_time=0.8)
            wait_until(self, tr, "sq")
            self.play(TransformMatchingShapes(s3, s4), run_time=0.6)
            self.play(s4[0].animate.set_color(IRR), run_time=0.3)
            wait_until(self, tr, "two")
            self.play(ReplacementTransform(s4, s5), run_time=0.6)
            t = tr.get_remaining_duration()
            self.play(FadeIn(right, shift=DOWN * 0.15), run_time=rt(min(0.5, t * 0.5)))
            self.play(Create(ok_r), run_time=rt(min(0.4, t * 0.4)))
            rest(self, tr)

        # b5: either way
        ask = text("which one?", size=64, color=PRIMARY, weight="BOLD").move_to([0, NOTE_Y + 1.2, 0])
        with self.voiceover(text=N("short1.b5")) as tr:
            wait_until(self, tr, "both")
            self.play(Indicate(ok_l, color=GOOD, scale_factor=1.3), Indicate(ok_r, color=GOOD, scale_factor=1.3),
                      run_time=0.8)
            wait_until(self, tr, "which")
            self.play(FadeIn(ask, scale=1.2), run_time=0.5)
            rest(self, tr)

        # b6: it's the second case
        dim = VGroup(lab_l, left, legs[0])
        x_l = cross(np.array([LX, CHECK_Y, 0]), s=0.35, width=8)
        ans = VGroup(math(r"\sqrt{2}^{\sqrt{2}}", size=60, color=IRR), text("is irrational", size=52))
        ans.arrange(RIGHT, buff=0.25).move_to([0, NOTE_Y + 1.2, 0])
        year = VGroup(text("Kuzmin, 1930", size=34, color=MUTED),
                      text("in general: Gelfond-Schneider, 1934", size=34, color=MUTED)).arrange(DOWN, buff=0.12)
        year.next_to(ans, DOWN, buff=0.3)
        with self.voiceover(text=N("short1.b6")) as tr:
            wait_until(self, tr, "answer")
            self.play(dim.animate.set_opacity(0.3), FadeOut(ok_l), Create(x_l), FadeOut(ask), FadeIn(ans), run_time=0.7)
            wait_until(self, tr, "year")
            self.play(FadeIn(year), run_time=0.6)
            rest(self, tr)
        self.wait(0.8)
