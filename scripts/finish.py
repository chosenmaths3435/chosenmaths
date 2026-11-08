"""Build the final deliverables for an episode.

    uv run scripts/finish.py <slug> [--voice eleven|draft] [--quality h|l]
                                    [--only long|shorts] [--scenes S01Hook,...]

Writes to out/<slug>/:
    <slug>.mp4          long-form, scenes joined, loudness normalized
    <slug>.srt          long-form captions (for upload, not burned in)
    chapters.txt        YouTube chapter list from the script's scene names
    <short>.mp4         each short, vertical, with burned-in captions
    <short>.srt         the same captions as a file
    <short>-cover.jpg   each short's cover: a frame of the short with a caption, set by
                        `cover:` in metadata.yaml; <short>-cover-crops.png previews how
                        the profile grid (3:4) and feed (1:1) crop it

Rendering reuses manim's cache, so rerunning after a small change only re-renders the
scenes that changed. Narration audio is cached by text, so the voice is only generated
for new or edited lines.
"""

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
QUALITY = {"h": ("-qh", "1080p60", "1920p60"), "l": ("-ql", "480p15", "854p15")}
LOUDNESS = "loudnorm=I=-14:TP=-1.5:LRA=11"  # -14 LUFS: what YouTube, TikTok, IG normalize to
CAPTION_FONT = "Source Sans 3"


def run(cmd, env=None):
    print("+", " ".join(str(c) for c in cmd), flush=True)
    subprocess.run(cmd, check=True, env=env)


def duration(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                          str(path)], check=True, capture_output=True, text=True).stdout
    return float(out.strip())


def scene_classes(py, prefix):
    return re.findall(rf"^class ({prefix}\w*)\(", py.read_text(), re.M)


def scene_names(script_md):
    """Map scene ids (s01, short1) to their names in script.md."""
    return dict(re.findall(r"^##\s+(\w+)\s+(.+?)\s*$", script_md.read_text(), re.M))


# --- subtitles ---------------------------------------------------------------

def parse_srt(path):
    if not path.exists():
        return []
    blocks = re.split(r"\n\s*\n", path.read_text().strip())
    out = []
    for b in blocks:
        lines = b.strip().splitlines()
        if len(lines) < 3:
            continue
        m = re.match(r"(\S+) --> (\S+)", lines[1])
        out.append((ts_in(m.group(1)), ts_in(m.group(2)), " ".join(lines[2:])))
    return out


def ts_in(s):
    h, m, rest = s.split(":")
    sec, ms = rest.split(",")
    return int(h) * 3600 + int(m) * 60 + int(sec) + int(ms) / 1000


def ts_srt(t):
    ms = round(t * 1000)
    return f"{ms // 3600000:02}:{ms // 60000 % 60:02}:{ms // 1000 % 60:02},{ms % 1000:03}"


def ts_ass(t):
    cs = round(t * 100)
    return f"{cs // 360000}:{cs // 6000 % 60:02}:{cs // 100 % 60:02}.{cs % 100:02}"


def write_srt(entries, path):
    path.write_text("\n".join(f"{i}\n{ts_srt(a)} --> {ts_srt(b)}\n{t}\n" for i, (a, b, t) in
                              enumerate(entries, 1)))


def chunk_entries(entries, max_words=3):
    """Split caption lines into short chunks for vertical video, timed by character count."""
    out = []
    for a, b, text in entries:
        words = text.split()
        chunks, cur = [], []
        for w in words:
            cur.append(w)
            if len(cur) >= max_words or w[-1] in ".,?!;:":
                chunks.append(cur)
                cur = []
        if cur:
            chunks.append(cur)
        total = sum(len(" ".join(c)) for c in chunks) or 1
        t = a
        for c in chunks:
            s = " ".join(c)
            dt = (b - a) * len(s) / total
            out.append((t, t + dt, s))
            t += dt
    return out


def write_ass(entries, path, width=1080, height=1920, from_bottom=0.24, scale=1.0):
    size = round(height * 0.05 * scale)
    margin_v = round(height * from_bottom - size / 2)
    head = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {width}
PlayResY: {height}
WrapStyle: 0

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Cap,{CAPTION_FONT},{size},&H00FFFFFF,&H00FFFFFF,&H00000000,&H64000000,-1,0,0,0,100,100,0,0,1,{round(size * 0.09)},0,2,80,80,{margin_v},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    lines = [f"Dialogue: 0,{ts_ass(a)},{ts_ass(b)},Cap,,0,0,0,,{t}" for a, b, t in entries]
    path.write_text(head + "\n".join(lines) + "\n")


# --- build steps -------------------------------------------------------------

def render(ep_dir, py, cls, media, qflag, voice, aspect):
    env = {**os.environ, "MV_VOICE": voice, "MV_ASPECT": aspect}
    run(["uv", "run", "manim", "-v", "WARNING", qflag, "--media_dir", str(media), str(py), cls], env=env)


def build_long(slug, ep_dir, media, out, q, voice, only_scenes):
    qflag, res, _ = QUALITY[q]
    py = ep_dir / "scenes.py"
    classes = scene_classes(py, "S")
    for cls in classes:
        if not only_scenes or cls in only_scenes:
            render(ep_dir, py, cls, media, qflag, voice, "landscape")
    vids = [media / "videos" / "scenes" / res / f"{c}.mp4" for c in classes]

    listing = out / "concat.txt"
    listing.write_text("".join(f"file '{v}'\n" for v in vids))
    joined = out / "joined.mp4"
    run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", listing, "-c", "copy", joined])
    final = out / f"{slug}.mp4"
    run(["ffmpeg", "-v", "error", "-y", "-i", joined, "-c:v", "copy", "-af", LOUDNESS, "-ar", "48000",
         "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", final])
    joined.unlink()
    listing.unlink()

    # Captions and chapters, offset by each scene's start time.
    names = scene_names(ep_dir / "script.md")
    srt, chapters, t = [], [], 0.0
    for cls, v in zip(classes, vids):
        sid = "s" + re.match(r"S(\d+)", cls).group(1)
        m, s = divmod(int(t), 60)
        chapters.append(f"{m}:{s:02} {names.get(sid, cls)}")
        srt += [(a + t, b + t, txt) for a, b, txt in parse_srt(v.with_suffix(".srt"))]
        t += duration(v)
    write_srt(srt, out / f"{slug}.srt")
    if "Thumbnail" in re.findall(r"^class (\w+)\(", py.read_text(), re.M):
        run(["uv", "run", "manim", "-v", "WARNING", "-s", "-qh", "--media_dir", str(media), str(py), "Thumbnail"])
        png = sorted((media / "images" / "scenes").glob("Thumbnail*.png"))[-1]
        run(["ffmpeg", "-v", "error", "-y", "-i", png, "-vf", "scale=1280:720", out / "thumbnail.png"])
    (out / "chapters.txt").write_text("\n".join(chapters) + "\n")
    print(f"long-form: {final} ({t / 60:.1f} min)")


# Covers sit in the caption band, nudged up so the bottom line stays inside the
# middle 1:1 square that Instagram shows when a reel is shared to the feed.
COVER_FROM_BOTTOM = 0.26


def build_cover(v, name, cover, out, w, h):
    """A frame of the clean short (no burned-in captions) plus a caption in the same style."""
    at = float(cover["at"])
    if at > duration(v):
        raise SystemExit(f"{name}: cover time {at}s is past the end of the short")
    # Lines break where the text has newlines; extra lines stack upward.
    text = r"\N".join(t.strip() for t in str(cover.get("text", "")).strip().splitlines())
    ass = out / f"{name}-cover.ass"
    write_ass([(0, 10, text)] if text else [], ass, w, h,
              float(cover.get("from_bottom", COVER_FROM_BOTTOM)), float(cover.get("scale", 1.0)))
    jpg = out / f"{name}-cover.jpg"
    run(["ffmpeg", "-v", "error", "-y", "-ss", str(at), "-i", v, "-frames:v", "1", "-vf", f"ass={ass}",
         "-q:v", "2", jpg])
    ass.unlink()
    # Preview of the crops the profile grid (3:4) and a feed share (1:1) show.
    crops = out / f"{name}-cover-crops.png"
    g = round(w * 4 / 3)
    run(["ffmpeg", "-v", "error", "-y", "-i", jpg, "-filter_complex",
         f"[0]split=3[a][b][c];[b]crop={w}:{g}:0:{(h - g) // 2},pad={w}:{h}:0:{(h - g) // 2}:gray[b2];"
         f"[c]crop={w}:{w}:0:{(h - w) // 2},pad={w}:{h}:0:{(h - w) // 2}:gray[c2];"
         f"[a][b2][c2]hstack=3,scale=-2:960", crops])
    print(f"cover: {jpg} (frame at {at}s)")


def build_shorts(slug, ep_dir, media, out, q, voice, only_scenes, covers_only=False):
    qflag, _, res = QUALITY[q]
    py = ep_dir / "shorts.py"
    if not py.exists():
        return
    sys.path.insert(0, str(ROOT))
    os.environ["MV_ASPECT"] = "portrait"
    from mathvid.layout import CAPTION_FROM_BOTTOM
    import yaml

    meta_path = ep_dir / "metadata.yaml"
    meta = yaml.safe_load(meta_path.read_text()) if meta_path.exists() else {}
    w, h = (1080, 1920) if q == "h" else (480, 854)

    for cls in scene_classes(py, "Short"):
        if only_scenes and cls not in only_scenes:
            continue
        v = media / "videos" / "shorts" / res / f"{cls}.mp4"
        name = re.match(r"Short(\d+)", cls).group(0).lower()
        cover = ((meta.get("shorts") or {}).get(name) or {}).get("cover")
        if covers_only:
            if not v.exists():
                raise SystemExit(f"{v} not rendered yet; run without --only covers first")
            if cover:
                build_cover(v, name, cover, out, w, h)
            else:
                print(f"{name}: no cover in metadata.yaml")
            continue
        render(ep_dir, py, cls, media, qflag, voice, "portrait")
        entries = parse_srt(v.with_suffix(".srt"))
        write_srt(entries, out / f"{name}.srt")
        ass = out / f"{name}.ass"
        write_ass(chunk_entries(entries), ass, w, h, CAPTION_FROM_BOTTOM)
        final = out / f"{name}.mp4"
        run(["ffmpeg", "-v", "error", "-y", "-i", v, "-vf", f"ass={ass}", "-c:v", "libx264", "-crf", "18",
             "-preset", "slow", "-pix_fmt", "yuv420p", "-af", LOUDNESS, "-ar", "48000", "-c:a", "aac",
             "-b:a", "192k", "-movflags", "+faststart", final])
        ass.unlink()
        print(f"short: {final} ({duration(final):.0f}s)")
        if cover:
            build_cover(v, name, cover, out, w, h)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("slug")
    ap.add_argument("--voice", default="eleven", choices=["eleven", "draft"])
    ap.add_argument("--quality", default="h", choices=["h", "l"])
    ap.add_argument("--only", choices=["long", "shorts", "covers"],
                    help="covers: rebuild short covers from the existing renders only")
    ap.add_argument("--scenes", default="", help="comma-separated classes to re-render; others reuse cache")
    a = ap.parse_args()

    os.chdir(ROOT)
    ep_dir = ROOT / "episodes" / a.slug
    suffix = "" if a.voice == "eleven" and a.quality == "h" else f"-{a.voice}-{a.quality}"
    media = ROOT / "media" / f"{a.slug}-final{suffix}"
    out = ROOT / "out" / f"{a.slug}{suffix}"
    out.mkdir(parents=True, exist_ok=True)
    only = set(filter(None, a.scenes.split(",")))
    if a.only in (None, "long"):
        build_long(a.slug, ep_dir, media, out, a.quality, a.voice, only)
    if a.only in (None, "shorts", "covers"):
        build_shorts(a.slug, ep_dir, media, out, a.quality, a.voice, only, a.only == "covers")


if __name__ == "__main__":
    main()
