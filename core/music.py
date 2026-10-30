"""
music.py — an original background bed synthesized per episode with numpy: slow
chord pads (plus a heartbeat for tense stories, plucks for kids) through a
convolution reverb. Nothing here is a third-party recording, so it can't draw a
Content ID claim. Ducked under the voice in video_builder.build_final_video.
"""

from __future__ import annotations

import random
from pathlib import Path

SAMPLE_RATE = 44100

# Semitones above A1 per chord.
PROGRESSIONS = {
    "warm": [[3, 15, 19, 22], [10, 17, 22, 26], [0, 12, 19, 24], [8, 15, 20, 24]],
    "calm": [[3, 10, 15, 22], [8, 15, 22, 27], [1, 8, 15, 20], [3, 10, 17, 22]],
    "tense": [[0, 7, 12, 15], [1, 8, 13, 16], [0, 7, 12, 15], [-2, 5, 10, 13]],
    "epic": [[0, 7, 12, 19], [-4, 3, 8, 15], [3, 10, 15, 22], [-2, 5, 10, 17]],
    "light": [[3, 10, 15, 19], [8, 15, 20, 24], [10, 17, 22, 26], [5, 12, 17, 20]],
    "playful": [[3, 15, 19, 22], [8, 20, 24, 27], [10, 22, 26, 29], [3, 15, 19, 22]],
}
CHORD_SECONDS = {"warm": 6.0, "calm": 8.0, "tense": 6.0, "epic": 5.0, "light": 4.0, "playful": 2.5}

CHANNEL_MOODS = {
    "hp01_betrayal_revenge": "tense",
    "hp02_court_drama": "tense",
    "hp03_karma_justice": "tense",
    "hp04_veteran_kindness": "warm",
    "hp06_literary_analysis": "calm",
    "hp07_senior_longevity": "light",
    "hp08_english_learning": "light",
    "hp09_kids_cartoon_stories": "playful",
    "ch03_hindu_mythology": "epic",
    "ch06_eastern_philosophy": "calm",
}


def channel_mood(config) -> str:
    return config.get("music_mood") or CHANNEL_MOODS.get(config["name"], "warm")


def _reverb(signal, seconds, rng):
    """Convolve with a decaying noise tail -- what makes a pad sound like a
    room instead of a test tone."""
    import numpy as np

    n = int(seconds * SAMPLE_RATE)
    tail = rng.standard_normal(n) * np.exp(-6.0 * np.linspace(0, 1, n))
    size = len(signal) + n
    wet = np.fft.irfft(np.fft.rfft(signal, size) * np.fft.rfft(tail, size), size)[:len(signal)]
    return signal + 0.5 * wet / (np.max(np.abs(wet)) + 1e-9) * np.max(np.abs(signal))


def write_music_bed(out_path: str | Path, duration: float, mood: str = "warm", seed: int | None = None) -> Path:
    import numpy as np
    import soundfile as sf

    rng = np.random.default_rng(seed if seed is not None else random.randint(0, 2**31 - 1))
    progression = PROGRESSIONS.get(mood, PROGRESSIONS["warm"])
    chord_seconds = CHORD_SECONDS.get(mood, 6.0)
    root = 55.0 * 2 ** (int(rng.integers(-2, 3)) / 12)  # a new key each episode
    start = int(rng.integers(0, len(progression)))
    total = int((duration + 1.0) * SAMPLE_RATE)
    step = int(chord_seconds * SAMPLE_RATE)
    overlap = int(min(1.5, chord_seconds / 2) * SAMPLE_RATE)
    left, right = np.zeros(total), np.zeros(total)

    for c in range(total // step + 1):
        chord = progression[(start + c) % len(progression)]
        begin = c * step
        n = min(step + overlap, total - begin)
        if n <= 0:
            break
        t = np.arange(n) / SAMPLE_RATE
        env = np.minimum(1.0, np.minimum(t / (overlap / SAMPLE_RATE), (n - 1 - np.arange(n)) / overlap))
        for voice, semitone in enumerate(chord):
            freq = root * 2 ** (semitone / 12)
            pan = 0.5 + 0.3 * np.sin(voice * 2.1)
            for detune, level in ((0.997, 0.5), (1.003, 0.5), (2.0, 0.12)):
                phase = rng.uniform(0, 2 * np.pi)
                tone = np.sin(2 * np.pi * freq * detune * t + phase) * level * env / (1 + voice * 0.35)
                left[begin:begin + n] += tone * (1 - pan)
                right[begin:begin + n] += tone * pan

    if mood == "tense":  # low heartbeat: two soft thumps every ~1.7s
        for beat_at in np.arange(0.5, duration, 1.7):
            for offset, level in ((0.0, 1.0), (0.28, 0.6)):
                i = int((beat_at + offset) * SAMPLE_RATE)
                n = min(int(0.3 * SAMPLE_RATE), total - i)
                if n > 0:
                    t = np.arange(n) / SAMPLE_RATE
                    thump = np.sin(2 * np.pi * 52 * t) * np.exp(-14 * t) * 1.6 * level
                    left[i:i + n] += thump
                    right[i:i + n] += thump
    elif mood == "playful":  # plucked arpeggio over the chords
        scale = [3, 7, 10, 15, 19, 22]
        for k, at in enumerate(np.arange(0.0, duration, chord_seconds / 8)):
            i = int(at * SAMPLE_RATE)
            n = min(int(0.5 * SAMPLE_RATE), total - i)
            if n > 0:
                t = np.arange(n) / SAMPLE_RATE
                freq = root * 8 * 2 ** (scale[k % len(scale)] / 12)
                pluck = np.sin(2 * np.pi * freq * t) * np.exp(-7 * t) * 0.7
                left[i:i + n] += pluck
                right[i:i + n] += pluck

    left, right = _reverb(left, 2.5, rng), _reverb(right, 2.5, rng)
    fade = np.ones(total)
    fade_in, fade_out = int(1.0 * SAMPLE_RATE), int(1.5 * SAMPLE_RATE)
    fade[:fade_in] = np.linspace(0, 1, fade_in)
    fade[-fade_out:] = np.linspace(1, 0, fade_out)
    stereo = np.stack([left * fade, right * fade], axis=1)
    stereo *= 0.7 / (np.max(np.abs(stereo)) + 1e-9)

    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    sf.write(str(out), stereo.astype(np.float32), SAMPLE_RATE)
    return out
