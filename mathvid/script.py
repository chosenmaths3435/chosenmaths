"""Load narration from an episode's script.md so the text lives in one place.

Format:

    ## s01 Hook                 <- scene id, then a free-form name
    > visual: grid of dots      <- notes for the animator (ignored by the loader)
    [b1] First line of narration, with <bookmark mark="grid"/> bookmarks inline.
    It can wrap onto more lines; a blank line ends the beat.
    [b2] Next beat.

In scenes.py:

    from mathvid.script import Script
    N = Script(__file__)
    with self.voiceover(text=N("s01.b1")) as tr: ...
"""

import re
from pathlib import Path

SCENE_RE = re.compile(r"^##\s+(\w+)\b")
BEAT_RE = re.compile(r"^\[(\w+)\]\s*(.*)$")


def parse(md: str) -> dict[str, str]:
    beats: dict[str, str] = {}
    scene = None
    key = None
    for line in md.splitlines():
        stripped = line.strip()
        m = SCENE_RE.match(stripped)
        if m:
            scene, key = m.group(1), None
            continue
        m = BEAT_RE.match(stripped)
        if m and scene:
            key = f"{scene}.{m.group(1)}"
            if key in beats:
                raise ValueError(f"duplicate beat {key}")
            beats[key] = m.group(2)
            continue
        if not stripped or stripped.startswith((">", "<!--", "#")):
            key = None
            continue
        if key:
            beats[key] += " " + stripped
    return {k: " ".join(v.split()) for k, v in beats.items()}


class Script:
    def __init__(self, scenes_file: str, name: str = "script.md"):
        self.path = Path(scenes_file).resolve().parent / name
        self.beats = parse(self.path.read_text())

    def __call__(self, key: str) -> str:
        if key not in self.beats:
            raise KeyError(f"{key} not in {self.path.name}; have {sorted(self.beats)}")
        return self.beats[key]

    def scene(self, scene_id: str) -> list[str]:
        """All beat keys of one scene, in order."""
        return [k for k in self.beats if k.startswith(scene_id + ".")]
