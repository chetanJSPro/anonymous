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

import glob
import os
import random
import re
import sys
import time

# Windows' console defaults to cp1252/cp437, which can't encode arbitrary
# Unicode punctuation the LLM sometimes emits in topics/scripts (e.g. a
# narrow no-break space, U+202F) — an unhandled print() of that text used
# to crash the whole process with UnicodeEncodeError, killing an entire
# batch run partway through (every script here imports this module first,
# so reconfiguring stdout/stderr once here covers all of them).
for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(encoding="utf-8", errors="replace")

from core.llm import generate_visual_queries, generate_script, generate_hook_title, sanitize_narration_script
from core.tts_kokoro import synthesize_kokoro
from core.tts_chatterbox import synthesize_chatterbox
from core.captions import distribute_segments, segments_from_words, write_ass, write_srt
from core.music import channel_mood, write_music_bed
from core.visuals import fetch_hybrid_stock_agnes_videos
from core.story import build_story_background
from core.video_builder import build_background, build_final_video, ffprobe_duration
from core.upload import upload_video
from core.topics import pick_topic

# Old edge-tts voice names (still used as config["voice"] values) mapped to
# Kokoro English voice IDs of a matching gender/tone, so channel configs
# didn't all need hand-editing to switch TTS engines.
SFX_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "sfx")


# A boing on a veteran's story or a court verdict undoes the mood, so the
# stinger is chosen from the ones that suit the channel's music mood.
SFX_BY_MOOD = {
    "tense": ("hook_whoosh_impact", "hook_whoosh_fast"),
    "warm": ("hook_sparkle_whoosh", "hook_ding_reveal"),
    "calm": ("hook_sparkle_whoosh",),
    "epic": ("hook_whoosh_impact",),
    "light": ("hook_pop", "hook_tech_affirm", "hook_ding_reveal"),
    "playful": ("hook_boing", "hook_pop", "hook_sparkle_whoosh"),
}


def _pick_intro_sfx(mood=None):
    """A short (<=3.5s) hook/stinger sound effect (see assets/sfx/README.md
    for sourcing/licensing) played at t=0 only, layered under the narration
    -- an audio "scroll-stopping hook" to go with the visual/script one
    already in every channel's system_prompt. None if assets/sfx has
    nothing in it (e.g. a fresh checkout before the folder is populated) --
    a missing intro sfx must never block an episode."""
    files = glob.glob(os.path.join(SFX_DIR, "*.mp3")) + glob.glob(os.path.join(SFX_DIR, "*.wav"))
    suited = [f for f in files if os.path.splitext(os.path.basename(f))[0] in SFX_BY_MOOD.get(mood, ())]
    files = suited or files
    return random.choice(files) if files else None


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
    # Retry loop: the LLM occasionally refuses a topic outright ("I'm sorry,
    # but I can't help with that.") -- a content-filter false positive
    # confirmed 2026-08-19 on an entirely benign topic ("Former Navy SEAL
    # builds community garden for at-risk youth..."). A refusal produces a
    # near-empty script that min_duration_seconds correctly rejects below,
    # but without a retry that just fails the whole episode. Retrying the
    # same prompt at temperature>0 usually gets a real story on attempt 2.
    # Also retries on a hard failure (e.g. Groq 429 rate-limited AND the
    # Pollinations fallback failing too, confirmed 2026-08-20 under 4
    # parallel channel jobs) instead of only on a too-short/refused
    # response -- an uncaught exception here used to abort the whole
    # episode on attempt 1 even though attempt 2 often succeeds once a
    # transient rate limit clears.
    script = ""
    last_error = None
    for attempt in range(3):
        try:
            script = sanitize_narration_script(generate_script(config["system_prompt"], topic))
        except Exception as e:
            last_error = e
            print(f"[pipeline] script attempt {attempt+1} raised ({e}) -- retrying")
            time.sleep(5)
            continue
        if len(script.split()) >= 50:  # every channel targets 60+ words; less means cut off
            break
        print(f"[pipeline] script attempt {attempt+1} too short/refused "
              f"({len(script.split())} words: {script[:80]!r}) -- retrying")
    if not script:
        raise RuntimeError(f"{config['name']}: script generation failed all 3 attempts "
                            f"(last error: {last_error})")
    print(f"[pipeline] script generated ({len(script.split())} words)")

    vertical = config.get("vertical", True)
    width, height = (1080, 1920) if vertical else (1920, 1080)

    # 1) Voiceover — Kokoro (local, free, fast even on CPU) as primary.
    # Chatterbox (core/tts_chatterbox.py) is higher-quality/more human-like
    # but costs ~25 CPU-minutes per video on GitHub Actions' GPU-less
    # runners (confirmed 2026-08-19: 72s of audio took 1500+s to render) —
    # opt into it per-channel via config["voice_engine"] = "chatterbox" once
    # you've weighed that runtime/cost against Kokoro's quality.
    narration_path = os.path.join(out_dir, "narration.wav")
    words = []  # (word, start, end) from Kokoro; stays empty on Chatterbox
    if config.get("voice_engine") == "chatterbox":
        try:
            _, duration = synthesize_chatterbox(script, narration_path,
                                                 audio_prompt_path=config.get("voice_reference"))
            duration += 0.45
            print(f"[pipeline] voice generated via Chatterbox ({duration:.1f}s)")
        except Exception as e:
            print(f"[pipeline] Chatterbox failed ({e}) — falling back to Kokoro")
            voice_id = KOKORO_VOICE_MAP.get(config.get("voice"), "am_michael")
            synthesize_kokoro(script, narration_path, lang_code="a", voice_id=voice_id,
                               speed=float(config.get("speed", 1.0)), word_timings=words)
            duration = ffprobe_duration(narration_path) + 0.45
            print(f"[pipeline] voice generated via Kokoro fallback ({duration:.1f}s)")
    else:
        voice_id = KOKORO_VOICE_MAP.get(config.get("voice"), "am_michael")
        synthesize_kokoro(script, narration_path, lang_code="a", voice_id=voice_id,
                           speed=float(config.get("speed", 1.0)), word_timings=words)
        duration = ffprobe_duration(narration_path) + 0.45
        print(f"[pipeline] voice generated via Kokoro ({duration:.1f}s, {len(words)} timed words)")

    # Safety net: a channel whose script produces a near-empty narration
    # (e.g. a "no spoken narration, just a title" system_prompt like
    # hp05_sleep_soundscapes's -- Kokoro then just reads the short title
    # aloud, giving a several-second "video") must never silently publish.
    # Confirmed 2026-08-19: this exact case produced and PUBLISHED a real
    # 4-second video before this check existed. Channels genuinely meant to
    # run without narration need real ambient-audio + duration handling
    # built first (not implemented yet) -- until then, fail loudly instead.
    min_duration = float(config.get("min_duration_seconds", 15))
    if duration < min_duration:
        raise RuntimeError(
            f"{config['name']}: narration only {duration:.1f}s (< {min_duration}s minimum) "
            f"-- refusing to assemble/upload a near-empty video. If this channel is meant "
            f"to run without spoken narration, it needs real duration/audio handling built "
            f"in core/pipeline.py first, not just a short title script.")

    # 2) Captions — timed from the voice's own word timestamps when available
    # (estimated from line length otherwise), burned in via ffmpeg later.
    subtitle_lines = _split_into_subtitle_lines(script)
    segments = segments_from_words(subtitle_lines, words) if words else distribute_segments(subtitle_lines, duration)
    ass_path = os.path.join(out_dir, "captions_burnin.ass")
    srt_path = os.path.join(out_dir, "captions_upload.srt")
    # Hook title is generated up front (was upload-only) so it can also be
    # burned in as an on-screen hook card for the first ~2.5s -- the frame
    # that decides "viewed vs swiped away" on Shorts.
    fallback_title = config["title_fn"](topic)
    title = generate_hook_title(config.get("niche", config["name"]), topic, script, fallback_title)
    write_ass(segments, ass_path, width=width, height=height, duration=duration,
               location_label=config.get("location_label"),
               hook_text=title if (vertical and config.get("hook_card", True)) else None,
               punchy=bool(vertical and config.get("punchy_captions", True)),
               words=words,
               **(dict(caption_font="Arial", caption_font_size=76, caption_margin_bottom=340,
                       location_font="Arial", legacy=True) if config.get("legacy_style") else {}))
    write_srt(segments, srt_path)

    # 3) Visuals — mostly Agnes AI-generated clips (if AGNES_API_KEY is set)
    # for a consistent human/cinematic look, topped up with real stock video
    # (Pexels first, Pixabay fallback) for whatever Agnes doesn't cover.
    # Silently falls back to 100% stock if Agnes is unavailable/fails/rate-
    # limited on a given run — a channel never fails to produce a video.
    queries = config["visual_query_fn"](topic, script)
    # Optional second query list used ONLY for the stock (Pexels/Pixabay)
    # top-up -- needed by channels whose best Agnes/story prompts are full
    # of proper nouns (mythology figures, named places) that real stock
    # libraries have zero footage of and would otherwise search with,
    # silently returning unrelated "popular" results. See
    # core/llm.py::generate_visual_queries(avoid_named_entities=True).
    stock_queries = config["stock_query_fn"](topic, script) if config.get("stock_query_fn") else None
    # Story-matched stock search: literal, script-derived keywords first so
    # footage follows what's being narrated; the channel's static list stays
    # as a tail fallback. Opt out with config["story_stock_queries"] = False
    # (e.g. ASMR, where fixed trigger-sound queries ARE the content).
    if config.get("story_stock_queries", True):
        story_q = generate_visual_queries(config.get("niche", config["name"]), topic, script,
                                          count=8, fallback=[], avoid_named_entities=True)
        stock_queries = list(dict.fromkeys((story_q or []) + (stock_queries or queries or [])))
    visuals_dir = os.path.join(out_dir, "visuals")
    os.makedirs(visuals_dir, exist_ok=True)
    keep_bg_audio = bool(config.get("keep_background_audio", False))

    # Story mode: an AI-generated scene per narration beat, in order (see
    # core/story.py). None means it couldn't run -> stock pipeline below.
    background = None
    # Stock footage is the default: the AI-image story format cut median views
    # ~5x across channels (Oct 28 - Nov 4). "story" opts a channel in; "ab"
    # alternates story/stock by day so both formats can be compared on one channel.
    mode = config.get("visual_mode", "stock")
    if mode == "ab":
        import datetime
        mode = "story" if datetime.date.today().toordinal() % 2 else "stock"
        print(f"[pipeline] A/B test: today's visual_mode = {mode}")
    if mode == "story":
        background = build_story_background(config, script, segments, duration,
                                            os.path.join(work_dir, "story"), width, height, fps=30)
        # Skip the episode rather than publish narration over unrelated
        # stock b-roll (e.g. a diner story over sushi footage) -- that
        # mismatch is what kept these channels at ~200 views. Opt out with
        # config["story_stock_fallback"] = True.
        if background is None and not config.get("story_stock_fallback", False):
            raise RuntimeError(f"{config['name']}: story scenes unavailable -- "
                               "skipping instead of publishing stock b-roll")
    if background is not None:
        visual_paths = []
    else:
        visual_paths = _fetch_stock_visuals(config, topic, script, queries, stock_queries,
                                            visuals_dir, vertical)
        print(f"[pipeline] {len(visual_paths)} video clips ready")
        background = build_background(visual_paths, work_dir, total_duration=duration,
                                       width=width, height=height, fps=30,
                                       clip_seconds=float(config.get("clip_seconds", 1.8 if vertical else 5)),
                                       keep_audio=keep_bg_audio)

    # 4) Assemble — background + ASS burn-in.
    final_path = os.path.join(out_dir, "final.mp4")
    # hook_sfx: opt-out per channel (config["hook_sfx"] = False) -- on by
    # default everywhere since it's a cheap, harmless engagement lever, but
    # a channel whose own audio IS the content (keep_background_audio, e.g.
    # ch01_ai_asmr's trigger sounds) shouldn't have an unrelated stinger
    # competing with it.
    mood = channel_mood(config)
    intro_sfx = _pick_intro_sfx(mood) if config.get("hook_sfx", not keep_bg_audio) else None
    # Original bed synthesized per episode, so no Content ID claims. Off where
    # the source audio is the content (ASMR), or with config["music"] = False.
    music_path = None
    if config.get("music", False):  # off by default: pre-Oct-28 format had no music bed
        music_path = write_music_bed(os.path.join(work_dir, "music.wav"), duration, mood)
    build_final_video(background, narration_path, ass_path, final_path, duration=duration,
                       background_audio=keep_bg_audio,
                       background_audio_volume=float(config.get("background_audio_volume", 1.0)),
                       narration_volume=float(config.get("narration_volume", 1.0)),
                       intro_sfx_path=intro_sfx, music_path=music_path,
                       **({"intro_sfx_volume": 1.4} if config.get("legacy_style") else {}))
    print(f"[pipeline] video assembled: {final_path}")
    return _maybe_upload(config, topic, title, final_path, upload, privacy_status)


def _fetch_stock_visuals(config, topic, script, queries, stock_queries, visuals_dir, vertical):
    return fetch_hybrid_stock_agnes_videos(
        queries, visuals_dir, count=8, vertical=vertical,
        agnes_count=int(config.get("agnes_clip_count", 6)),
        stock_queries=stock_queries, channel_name=config["name"],
        ai_only=bool(config.get("ai_only_visuals", False)),
        kids_safe=bool(config.get("made_for_kids", False)),
        ai_style_suffix=config.get("ai_style_suffix"))


def _maybe_upload(config, topic, title, final_path, upload, privacy_status):
    if upload:
        print(f"[pipeline] title: {title}")
        video_id = upload_video(
            video_path=final_path,
            title=title,
            description=config["description_fn"](topic),
            tags=config.get("tags", []),
            category_id=config.get("category_id", "27"),
            privacy_status=privacy_status,
            channel_token_file=config["channel_token_file"],
            client_secret_file=config.get("client_secret_file"),
            made_for_kids=config.get("made_for_kids", False),
        )
        return {"topic": topic, "video_path": final_path, "video_id": video_id}

    return {"topic": topic, "video_path": final_path, "video_id": None}
