"""
pipeline.py — the ONE function every channel's run.py calls.

Ties together: llm.py (script) -> tts_kokoro.py (voice) -> captions.py
(subtitle timing/ASS) -> visuals.py (real stock video only) ->
video_builder.py (ffmpeg background + burned-in captions) -> upload.py
(optional).

This is the peace_reels_automation rendering engine (Kokoro TTS, ffmpeg
background build with color grading, ASS subtitle burn-in via ffmpeg's
`ass=` filter) ported in so every anonymous-master channel matches that
quality bar — real video B-roll (no AI still images) with properly-timed,
styled captions, instead of the old edge-tts + MoviePy-TextClip pipeline.
"""

import os
import re
import sys

# Windows' console defaults to cp1252/cp437, which can't encode arbitrary
# Unicode punctuation the LLM sometimes emits in topics/scripts (e.g. a
# narrow no-break space, U+202F) — an unhandled print() of that text used
# to crash the whole process with UnicodeEncodeError, killing an entire
# batch run partway through (every script here imports this module first,
# so reconfiguring stdout/stderr once here covers all of them).
for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(encoding="utf-8", errors="replace")

from core.llm import generate_script
from core.tts_kokoro import synthesize_kokoro
from core.captions import distribute_segments, write_ass, write_srt
from core.visuals import fetch_stock_videos
from core.video_builder import build_background, build_final_video, ffprobe_duration
from core.upload import upload_video
from core.topics import pick_topic

# Old edge-tts voice names (still used as config["voice"] values) mapped to
# Kokoro English voice IDs of a matching gender/tone, so channel configs
# didn't all need hand-editing to switch TTS engines.
KOKORO_VOICE_MAP = {
    "en-US-GuyNeural": "am_michael",
    "en-US-AriaNeural": "af_bella",
    "en-US-ChristopherNeural": "am_adam",
    "en-US-JennyNeural": "af_nicole",
    "en-GB-RyanNeural": "bm_george",
}


def _split_into_subtitle_lines(script: str) -> list[str]:
    """Break narration prose into caption-sized chunks. Splits on sentence
    boundaries first (matches how the voice actually paces the read), then
    breaks any single sentence that's still too long for one caption card."""
    sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", script.replace("\n", " ")) if s.strip()]
    lines = []
    for s in sentences:
        if len(s) <= 90:
            lines.append(s)
            continue
        words = s.split()
        cur = ""
        for w in words:
            if len(cur) + len(w) + 1 > 90 and cur:
                lines.append(cur)
                cur = w
            else:
                cur = w if not cur else cur + " " + w
        if cur:
            lines.append(cur)
    return lines or [script.strip()]


def run_episode(config, topic=None, upload=False, privacy_status="public"):
    """
    config keys:
      name              str  - channel folder name, used for output paths
      system_prompt     str  - persona/style instructions for the LLM
      topic_prompts      list[str] - pool of topics; one picked at random if `topic` not given
      visual_query_fn   fn(topic:str, script:str) -> list[str] real-world b-roll
                        search terms (e.g. "empty courtroom", "ganges river ghat india").
                        No AI-image mode anymore — real stock video only.
      voice             str  - edge-tts-style voice name, mapped to a Kokoro voice via
                        KOKORO_VOICE_MAP (falls back to a generic male voice if unmapped)
      vertical          bool - True for Shorts (1080x1920), False for long-form (1920x1080)
      category_id       str  - YouTube category id for upload
      channel_token_file str - per-channel OAuth token filename (see core/upload.py)
      title_fn          fn(topic:str) -> str
      description_fn    fn(topic:str) -> str
      tags              list[str]
    """
    topic = topic or pick_topic(config)
    out_dir = os.path.join("output", config["name"])
    os.makedirs(out_dir, exist_ok=True)
    work_dir = os.path.join(out_dir, "work")
    os.makedirs(work_dir, exist_ok=True)

    print(f"[pipeline] ({config['name']}) topic: {topic}")
    script = generate_script(config["system_prompt"], topic)
    print(f"[pipeline] script generated ({len(script.split())} words)")

    vertical = config.get("vertical", True)
    width, height = (1080, 1920) if vertical else (1920, 1080)

    # 1) Voiceover — Kokoro (local, free, the peace_reels_automation voice engine).
    voice_id = KOKORO_VOICE_MAP.get(config.get("voice"), "am_michael")
    narration_path = os.path.join(out_dir, "narration.wav")
    synthesize_kokoro(script, narration_path, lang_code="a", voice_id=voice_id,
                       speed=float(config.get("speed", 1.0)))
    duration = ffprobe_duration(narration_path) + 0.45
    print(f"[pipeline] voice generated ({duration:.1f}s)")

    # 2) Captions — timed to the actual narration length, burned in via ffmpeg later.
    subtitle_lines = _split_into_subtitle_lines(script)
    segments = distribute_segments(subtitle_lines, duration)
    ass_path = os.path.join(out_dir, "captions_burnin.ass")
    srt_path = os.path.join(out_dir, "captions_upload.srt")
    write_ass(segments, ass_path, width=width, height=height, duration=duration,
               location_label=config.get("location_label"))
    write_srt(segments, srt_path)

    # 3) Visuals — real stock video only (Pexels first, Pixabay fallback/top-up).
    queries = config["visual_query_fn"](topic, script)
    visuals_dir = os.path.join(out_dir, "visuals")
    os.makedirs(visuals_dir, exist_ok=True)
    visual_paths = fetch_stock_videos(queries, visuals_dir, count=8, vertical=vertical)
    print(f"[pipeline] {len(visual_paths)} stock video clips ready")

    # 4) Assemble — ffmpeg background (normalized/color-graded/concatenated) + ASS burn-in.
    background = build_background(visual_paths, work_dir, total_duration=duration,
                                   width=width, height=height, fps=30, clip_seconds=5)
    final_path = os.path.join(out_dir, "final.mp4")
    build_final_video(background, narration_path, ass_path, final_path, duration=duration)
    print(f"[pipeline] video assembled: {final_path}")

    if upload:
        video_id = upload_video(
            video_path=final_path,
            title=config["title_fn"](topic),
            description=config["description_fn"](topic),
            tags=config.get("tags", []),
            category_id=config.get("category_id", "27"),
            privacy_status=privacy_status,
            channel_token_file=config["channel_token_file"],
            client_secret_file=config.get("client_secret_file"),
        )
        return {"topic": topic, "video_path": final_path, "video_id": video_id}

    return {"topic": topic, "video_path": final_path, "video_id": None}
