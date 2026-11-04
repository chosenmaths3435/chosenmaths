"""Speech services for manim-voiceover.

Pick one with the MV_VOICE environment variable:

    draft   (default) offline silence whose length is estimated from the word count.
            Free and fast; use it while iterating on animations.
    eleven  ElevenLabs with the cloned voice. Uses the /with-timestamps endpoint, so
            bookmarks land on the exact word. Needs ELEVENLABS_API_KEY and
            ELEVENLABS_VOICE_ID in the environment or in a .env file at the repo root.

Both services cache by input text, so re-rendering only pays for narration that changed.
"""

from __future__ import annotations

import base64
import os
import re
import wave
from pathlib import Path

import requests
from dotenv import find_dotenv, load_dotenv
from manim_voiceover.helper import remove_bookmarks
from manim_voiceover.services.base import SpeechService, initialize_speech_service
from manim_voiceover.tracker import AUDIO_OFFSET_RESOLUTION

load_dotenv(find_dotenv(usecwd=True))

ELEVEN_URL = "https://api.elevenlabs.io/v1/text-to-speech/{voice_id}/with-timestamps"
DEFAULT_MODEL = os.environ.get("ELEVENLABS_MODEL_ID", "eleven_multilingual_v2")
DEFAULT_SETTINGS = {"stability": 0.5, "similarity_boost": 0.8, "style": 0.0, "use_speaker_boost": True}


def _word_spans(text: str):
    """Yield (start, end) character spans of the words in text."""
    for m in re.finditer(r"\S+", text):
        yield m.start(), m.end()


def _boundaries_from_char_times(text: str, starts: list[float]) -> list[dict]:
    out = []
    for a, b in _word_spans(text):
        out.append(
            {
                "audio_offset": int(starts[a] * AUDIO_OFFSET_RESOLUTION),
                "text_offset": a,
                "word_length": b - a,
                "text": text[a:b],
                "boundary_type": "Word",
            }
        )
    return out


class DraftService(SpeechService):
    """Silent placeholder narration timed at a fixed speaking rate."""

    def __init__(self, words_per_minute: float = 160, **kwargs):
        initialize_speech_service(self, kwargs)
        self.wpm = words_per_minute

    def generate_from_text(self, text, cache_dir=None, path=None, **kwargs):
        cache_dir = Path(cache_dir or self.cache_dir)
        input_text = remove_bookmarks(text)
        input_data = {"input_text": input_text, "service": "draft", "wpm": self.wpm}
        cached = self.get_cached_result(input_data, cache_dir)
        if cached is not None:
            return cached

        spans = list(_word_spans(input_text))
        sec_per_word = 60.0 / self.wpm
        duration = max(1.0, len(spans) * sec_per_word + 0.3)
        audio_path = path or self.get_audio_basename(input_data) + ".wav"
        rate = 22050
        with wave.open(str(cache_dir / audio_path), "wb") as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(rate)
            w.writeframes(b"\x00\x00" * int(duration * rate))

        boundaries = [
            {
                "audio_offset": int(i * sec_per_word * AUDIO_OFFSET_RESOLUTION),
                "text_offset": a,
                "word_length": b - a,
                "text": input_text[a:b],
                "boundary_type": "Word",
            }
            for i, (a, b) in enumerate(spans)
        ]
        return {
            "input_text": text,
            "input_data": input_data,
            "original_audio": audio_path,
            "word_boundaries": boundaries,
        }


class ElevenLabsTimestampService(SpeechService):
    """ElevenLabs TTS with character-level timestamps (no Whisper needed)."""

    def __init__(self, voice_id=None, model_id=DEFAULT_MODEL, voice_settings=None, **kwargs):
        initialize_speech_service(self, kwargs)
        self.api_key = os.environ.get("ELEVENLABS_API_KEY")
        self.voice_id = voice_id or os.environ.get("ELEVENLABS_VOICE_ID")
        if not self.api_key or not self.voice_id:
            raise RuntimeError("Set ELEVENLABS_API_KEY and ELEVENLABS_VOICE_ID (env or .env).")
        self.model_id = model_id
        self.voice_settings = {**DEFAULT_SETTINGS, **(voice_settings or {})}

    def generate_from_text(self, text, cache_dir=None, path=None, **kwargs):
        cache_dir = Path(cache_dir or self.cache_dir)
        input_text = remove_bookmarks(text)
        input_data = {
            "input_text": input_text,
            "service": "elevenlabs-ts",
            "voice_id": self.voice_id,
            "model_id": self.model_id,
            "voice_settings": self.voice_settings,
        }
        cached = self.get_cached_result(input_data, cache_dir)
        if cached is not None:
            return cached

        resp = requests.post(
            ELEVEN_URL.format(voice_id=self.voice_id),
            headers={"xi-api-key": self.api_key, "Content-Type": "application/json"},
            params={"output_format": "mp3_44100_128"},
            json={"text": input_text, "model_id": self.model_id, "voice_settings": self.voice_settings},
            timeout=120,
        )
        if resp.status_code != 200:
            raise RuntimeError(f"ElevenLabs error {resp.status_code}: {resp.text[:500]}")
        body = resp.json()

        audio_path = path or self.get_audio_basename(input_data) + ".mp3"
        (cache_dir / audio_path).write_bytes(base64.b64decode(body["audio_base64"]))

        align = body.get("alignment") or {}
        chars = "".join(align.get("characters", []))
        starts = align.get("character_start_times_seconds", [])
        data = {"input_text": text, "input_data": input_data, "original_audio": audio_path}
        # Alignment is per character of the text we sent. If it does not line up
        # (it should), fall back to the tracker's linear interpolation.
        if chars == input_text and len(starts) == len(input_text):
            data["word_boundaries"] = _boundaries_from_char_times(input_text, starts)
        return data


def get_speech_service(**kwargs) -> SpeechService:
    mode = os.environ.get("MV_VOICE", "draft")
    if mode == "draft":
        return DraftService(**kwargs)
    if mode == "eleven":
        return ElevenLabsTimestampService(**kwargs)
    raise ValueError(f"Unknown MV_VOICE={mode!r}; use draft or eleven")
