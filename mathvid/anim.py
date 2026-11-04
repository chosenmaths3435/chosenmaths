"""Small helpers for voiceover-timed animation and common effects."""

from manim import FadeIn, FadeOut, Line, ReplacementTransform, VGroup

from mathvid.style import BAD

MIN_RT = 0.1


def rt(seconds: float) -> float:
    """Clamp a run_time so manim never gets zero or a negative number."""
    return max(MIN_RT, seconds)


def wait_until(scene, tracker, mark: str) -> None:
    """Hold the current frame until a bookmark is reached."""
    t = tracker.time_until_bookmark(mark)
    if t > 0.05:
        scene.wait(t)


def rest(scene, tracker) -> None:
    """Hold the current frame until the narration of this beat ends."""
    t = tracker.get_remaining_duration()
    if t > 0.05:
        scene.wait(t)


def strike(mob, color=BAD, width=5) -> Line:
    """A line struck through a mobject, left to right."""
    return Line(mob.get_left(), mob.get_right(), color=color, stroke_width=width)


def strikes(*mobs, **kw) -> VGroup:
    return VGroup(*[strike(m, **kw) for m in mobs])


def _idx(i):
    return list(i) if isinstance(i, (list, tuple)) else [i]


def morph_parts(scene, src, dst, pairs, run_time=1.0, extra=()):
    """Morph one multi-part MathTex into another, piece by piece.

    pairs: list of (src_index_or_indices, dst_index_or_indices). Each listed source
    piece flies to its destination piece; unlisted source pieces fade out and
    unlisted destination pieces fade in. Use it for algebra steps where
    TransformMatchingTex guesses wrong. Returns dst, which is left on screen as one
    mobject.
    """
    used_s, used_d, anims, temps = set(), set(), [], []
    for s_i, d_i in pairs:
        s_i, d_i = _idx(s_i), _idx(d_i)
        sg = VGroup(*[src[i] for i in s_i])
        dg = VGroup(*[dst[j].copy() for j in d_i])
        anims.append(ReplacementTransform(sg, dg))
        temps.append(dg)
        used_s.update(s_i)
        used_d.update(d_i)
    anims += [FadeOut(src[i]) for i in range(len(src)) if i not in used_s]
    anims += [FadeIn(dst[j]) for j in range(len(dst)) if j not in used_d]
    scene.play(*anims, *extra, run_time=run_time)
    scene.remove(src, *src.submobjects, *temps, *dst.submobjects)
    scene.add(dst)
    return dst
