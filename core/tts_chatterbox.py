"""
tts_chatterbox.py — Chatterbox TTS (Resemble AI), MIT-licensed, genuinely
free for commercial use (unlike XTTS-v2, whose weights are non-commercial-
only under the Coqui Public Model License — do not use XTTS-v2 output on
these monetized channels). Rated ahead of ElevenLabs in blind listening
tests; used here as the primary voice engine, with core/tts_kokoro.py kept
as an automatic fallback if Chatterbox fails or times out (slower on CPU
than Kokoro, since GitHub Actions runners have no GPU).

Usage:
    from core.tts_chatterbox import synthesize_chatterbox
    out_path, duration = synthesize_chatterbox(text, "out/voice.wav")
"""

from __future__ import annotations

import random
import re
from pathlib import Path

_MODEL = None  # lazy-loaded, reused across calls in the same process


def _get_model():
    global _MODEL
    if _MODEL is None:
        from chatterbox.tts import ChatterboxTTS
        _MODEL = ChatterboxTTS.from_pretrained(device="cpu")
    return _MODEL


def _split_sentences(text: str) -> list[str]:
    sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", text.replace("\n", " ")) if s.strip()]
    return sentences or [text.strip()]


def synthesize_chatterbox(
    text: str,
    out_path: str | Path,
    *,
    audio_prompt_path: str | None = None,
    pause_seconds: float = 0.45,
) -> tuple[Path, float]:
    """Generate narration with Chatterbox, sentence-by-sentence (mirrors
    tts_kokoro.py's approach: avoids one giant generate() call, and lets us
    insert the same jittered pause/fade between sentences for natural
    pacing). Returns (out_path, duration_seconds). Raises on any failure —
    callers should catch and fall back to synthesize_kokoro."""
    import numpy as np
    import soundfile as sf

    model = _get_model()
    sentences = _split_sentences(text)

    chunks = []
    fade_len = int(0.02 * model.sr)
    for sentence in sentences:
        wav = model.generate(sentence, audio_prompt_path=audio_prompt_path)
        audio = np.asarray(wav.squeeze().cpu().numpy(), dtype=np.float32)
        n = min(fade_len, len(audio) // 2)
        if n > 0:
            ramp = np.linspace(0.0, 1.0, n, dtype=np.float32)
            audio[:n] *= ramp
            audio[-n:] *= ramp[::-1]
        if chunks:
            gap = random.uniform(pause_seconds * 0.6, pause_seconds * 1.5)
            chunks.append(np.zeros(int(gap * model.sr), dtype=np.float32))
        chunks.append(audio)

    if not chunks:
        raise RuntimeError("Chatterbox produced no audio chunks")

    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    audio_all = np.concatenate(chunks)
    sf.write(str(out), audio_all, model.sr)
    return out, len(audio_all) / model.sr


if __name__ == "__main__":
    p, d = synthesize_chatterbox("This is a free test of Chatterbox text to speech.", "out/test_chatterbox.wav")
    print(p, f"{d:.2f}s")
