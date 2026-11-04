# math-videos

Source for math and CS explainer videos: Manim animations, narration scripts, and the
small library they share. Code is MIT licensed.

## Layout

```
mathvid/            shared library
  layout.py         aspect ratio (MV_ASPECT=landscape|portrait) and safe areas
  style.py          palette, fonts, text/math helpers, title card
  voice.py          speech services (MV_VOICE=draft|eleven)
  script.py         loads narration from an episode's script.md
episodes/<slug>/
  episode.yaml      title, status, platform links
  script.md         narration, split into scenes (## s01) and beats ([b1])
  scenes.py         long-form scenes, one class per script scene
  shorts.py         vertical scenes for 60s clips
scripts/
  contact_sheet.sh  tile frames of a render into one image for review
```

## Setup

Needs [uv](https://docs.astral.sh/uv/), ffmpeg, a LaTeX install, and the Source Sans 3
font.

```sh
uv sync
cp .env.example .env    # only needed for the real voice
```

## Rendering

```sh
# Fast preview with silent placeholder narration
uv run manim -ql --media_dir media/<slug> episodes/<slug>/scenes.py S01Hook

# Vertical
MV_ASPECT=portrait uv run manim -ql --media_dir media/<slug> episodes/<slug>/shorts.py Short1

# Final quality with the real voice
MV_VOICE=eleven uv run manim -qh --media_dir media/<slug> episodes/<slug>/scenes.py S01Hook
```

Each episode renders into its own `media/<slug>/`. Narration audio is cached in
`media/<slug>/voiceovers/`, so re-rendering only generates speech for lines that changed.

## Narration

The narration is AI-generated speech from a clone of the author's own voice (ElevenLabs).
The scripts are written and checked by the author.
