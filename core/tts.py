"""
tts.py — FREE text-to-speech using edge-tts (Microsoft Edge's online voices).

100% free, no API key, no signup. Also produces word-level timestamps so
we can auto-generate burned-in captions with zero extra tools (no Whisper
needed since we already have the exact text).

Usage:
    from core.tts import synthesize
    audio_path, srt_path, duration = synthesize(text, "out/voice.mp3", voice="en-US-GuyNeural")

Popular free voices (run `edge-tts --list-voices` to see all):
    en-US-GuyNeural        - deep male, narration
    en-US-AriaNeural       - warm female
    en-US-ChristopherNeural- calm male, documentary style
    en-GB-RyanNeural       - British male
    en-US-JennyNeural      - friendly female, good for quizzes/shorts
"""

import asyncio
import os
import edge_tts


def _format_srt_timestamp(seconds):
    ms = int(round(seconds * 1000))
    h, ms = divmod(ms, 3600000)
    m, ms = divmod(ms, 60000)
    s, ms = divmod(ms, 1000)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"


async def _synthesize_async(text, out_mp3, voice, rate, pitch):
    communicate = edge_tts.Communicate(text, voice, rate=rate, pitch=pitch)
    submaker = edge_tts.SubMaker()
    words = []
    with open(out_mp3, "wb") as f:
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                f.write(chunk["data"])
            elif chunk["type"] == "WordBoundary":
                words.append(chunk)
    return words


def synthesize(text, out_mp3, voice="en-US-GuyNeural", rate="+0%", pitch="+0Hz",
                srt_path=None, words_per_caption=6):
    """Generate narration audio + an SRT caption file grouped into short
    chunks (words_per_caption words each) for punchy on-screen captions."""
    os.makedirs(os.path.dirname(out_mp3) or ".", exist_ok=True)
    words = asyncio.run(_synthesize_async(text, out_mp3, voice, rate, pitch))

    duration = 0.0
    if words:
        last = words[-1]
        duration = (last["offset"] + last["duration"]) / 10_000_000  # 100ns units -> s

    if srt_path is None:
        srt_path = os.path.splitext(out_mp3)[0] + ".srt"

    if words:
        lines = []
        idx = 1
        for i in range(0, len(words), words_per_caption):
            group = words[i:i + words_per_caption]
            start = group[0]["offset"] / 10_000_000
            end = (group[-1]["offset"] + group[-1]["duration"]) / 10_000_000
            text_chunk = " ".join(w["text"] for w in group)
            lines.append(f"{idx}\n{_format_srt_timestamp(start)} --> {_format_srt_timestamp(end)}\n{text_chunk}\n")
            idx += 1
        with open(srt_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

    return out_mp3, srt_path, duration


if __name__ == "__main__":
    p, s, d = synthesize("This is a free test of edge text to speech.", "out/test.mp3")
    print(p, s, f"{d:.2f}s")
