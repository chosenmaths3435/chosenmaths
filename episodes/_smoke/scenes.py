from manim import Circle, Create, Write, Transform, DOWN
from manim_voiceover import VoiceoverScene

from mathvid import layout  # noqa: F401  (sets aspect ratio)
from mathvid.style import PRIMARY, SECONDARY, math, text
from mathvid.voice import get_speech_service
from mathvid.script import Script

N = Script(__file__)


class Smoke(VoiceoverScene):
    def construct(self):
        self.set_speech_service(get_speech_service())
        eq = math(r"\sum_{k=1}^{n} k = \frac{n(n+1)}{2}")
        with self.voiceover(
            text=N("s01.b1")
        ) as tr:
            self.play(Write(eq), run_time=tr.time_until_bookmark("c"))
            c = Circle(color=PRIMARY).next_to(eq, DOWN)
            self.play(Create(c), run_time=tr.get_remaining_duration())
        with self.voiceover(text=N("s01.b2")) as tr:
            self.play(Transform(c, text("channel font", color=SECONDARY).next_to(eq, DOWN)), run_time=tr.duration)
