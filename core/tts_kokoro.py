"""
tts_kokoro.py — ported from peace_reels_automation/src/tts.py. Local, free,
open-weight neural TTS (Kokoro), replacing core/tts.py's edge-tts voices —
this is "the voice from peace reel" the anonymous-master channels were
asked to share. Runs locally (no API key, no per-request cost), needs
espeak-ng installed on the OS (already required by peace_reels_automation).

English voices commonly available in Kokoro (lang_code="a" = American
English, "b" = British English):
    af_heart, af_bella, af_nicole   - American female
    am_adam, am_michael             - American male
    bf_emma, bf_isabella            - British female
    bm_george, bm_lewis             - British male
"""

from __future__ import annotations

import random
from pathlib import Path


def synthesize_kokoro(
    text: str,
    out_path: str | Path,
    *,
    lang_code: str = "a",
    voice_id: str = "am_michael",
    speed: float = 1.0,
    pause_seconds: float = 0.45,
) -> Path:
    """Generate local TTS with Kokoro. `pause_seconds` is the *average*
    silence inserted between lines, jittered per-gap with a short fade
    in/out at each splice to avoid a metronomic/robotic cadence and
    audible clicks — pacing/delivery only, doesn't clone anyone's voice."""
    try:
        import numpy as np
        import soundfile as sf
        from kokoro import KPipeline
    except Exception as e:
        raise RuntimeError(
            "Kokoro TTS is not installed/working. pip install -r requirements.txt "
            "and make sure espeak-ng is installed on the OS."
        ) from e

    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    pipeline = KPipeline(lang_code=lang_code)
    sample_rate = 24000
    fade_len = int(0.02 * sample_rate)

    def _faded(audio) -> "np.ndarray":
        audio = np.asarray(audio, dtype=np.float32).copy()
        n = min(fade_len, len(audio) // 2)
        if n > 0:
            ramp = np.linspace(0.0, 1.0, n, dtype=np.float32)
            audio[:n] *= ramp
            audio[-n:] *= ramp[::-1]
        return audio

    chunks = []
    generator = pipeline(text, voice=voice_id, speed=speed, split_pattern=r"\n+")
    for _graphemes, _phonemes, audio in generator:
        if chunks:
            gap = random.uniform(pause_seconds * 0.6, pause_seconds * 1.5)
            chunks.append(np.zeros(int(gap * sample_rate), dtype=np.float32))
        chunks.append(_faded(audio))
    if not chunks:
        raise RuntimeError("Kokoro returned no audio chunks")
    audio_all = np.concatenate(chunks)
    sf.write(str(out), audio_all, sample_rate)
    return out
