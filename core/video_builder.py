"""
video_builder.py — ported from peace_reels_automation/src/video_builder.py so
all anonymous-master channels get the same rendering quality: real stock
video clips normalized/cropped/color-graded and concatenated with ffmpeg,
then ASS subtitles burned in via ffmpeg's `ass=` filter — instead of
core/assemble.py's old MoviePy Ken-Burns-on-stills + plain TextClip captions.

Requires ffmpeg + ffprobe on PATH.
"""

from __future__ import annotations

import json
import math
import random
import shlex
import subprocess
from pathlib import Path


def ensure_dir(path: str | Path) -> Path:
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p


def run(cmd: list[str]) -> subprocess.CompletedProcess:
    print("$", " ".join(shlex.quote(c) for c in cmd))
    proc = subprocess.run(cmd, text=True, capture_output=True)
    if proc.returncode != 0:
        print(proc.stdout)
        print(proc.stderr)
        raise RuntimeError(f"Command failed with exit code {proc.returncode}: {' '.join(cmd)}")
    return proc


def ffprobe_duration(path: str | Path) -> float:
    cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "json", str(path)]
    proc = run(cmd)
    data = json.loads(proc.stdout)
    return float(data["format"]["duration"])


def _ass_filter_path(path: str | Path) -> str:
    # FFmpeg filter escaping. Wrap in single quotes so the drive-letter colon
    # (e.g. C:) isn't parsed as a filter option separator on Windows.
    p = str(Path(path).resolve()).replace("\\", "/")
    p = p.replace(":", r"\:").replace("'", r"\'")
    return f"'{p}'"


def _has_audio_stream(path: str | Path) -> bool:
    cmd = ["ffprobe", "-v", "error", "-select_streams", "a", "-show_entries",
           "stream=index", "-of", "csv=p=0", str(path)]
    proc = subprocess.run(cmd, text=True, capture_output=True)
    return proc.returncode == 0 and proc.stdout.strip() != ""


def normalize_clip(
    src: str | Path,
    out: str | Path,
    *,
    duration: float,
    width: int,
    height: int,
    fps: int = 30,
    offset: float = 0.0,
    keep_audio: bool = False,
) -> Path:
    """keep_audio: preserve the source clip's own audio track (boosted)
    instead of stripping it with -an -- needed for channels whose trigger
    SOUND is the actual content (ASMR: soap cutting, glass, slime), not
    just narration over silent b-roll (see ch01_ai_asmr's 2026-08-24 fix).
    When the source has no audio (e.g. an Agnes AI-generated clip, which is
    always silent), a silent stereo track is synthesized instead so every
    normalized clip has a uniform audio stream -- required for the concat
    demuxer's `-c copy` in build_background to work across a mixed
    pool of real-audio and silent clips."""
    out = Path(out)
    out.parent.mkdir(parents=True, exist_ok=True)
    vf = (
        f"scale={width}:{height}:force_original_aspect_ratio=increase,"
        f"crop={width}:{height},setsar=1,fps={fps},"
        "eq=contrast=1.04:saturation=1.08,format=yuv420p"
    )
    if not keep_audio:
        cmd = [
            "ffmpeg", "-y", "-ss", f"{offset:.2f}", "-i", str(src),
            "-t", f"{duration:.2f}", "-vf", vf, "-an",
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "21",
            str(out),
        ]
    elif _has_audio_stream(src):
        cmd = [
            "ffmpeg", "-y", "-ss", f"{offset:.2f}", "-i", str(src),
            "-t", f"{duration:.2f}", "-vf", vf, "-af", "volume=1.6",
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "21",
            "-c:a", "aac", "-b:a", "128k", "-ar", "44100", "-ac", "2",
            str(out),
        ]
    else:
        cmd = [
            "ffmpeg", "-y", "-ss", f"{offset:.2f}", "-i", str(src),
            "-f", "lavfi", "-i", "anullsrc=channel_layout=stereo:sample_rate=44100",
            "-t", f"{duration:.2f}", "-vf", vf,
            "-map", "0:v:0", "-map", "1:a:0",
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "21",
            "-c:a", "aac", "-b:a", "128k", "-shortest",
            str(out),
        ]
    run(cmd)
    return out


def build_background(
    video_paths: list[str | Path],
    workdir: str | Path,
    *,
    total_duration: float,
    width: int,
    height: int,
    fps: int = 30,
    clip_seconds: float = 5.0,
    seed: int | None = None,
    keep_audio: bool = False,
) -> Path:
    if not video_paths:
        raise ValueError("No source videos available — check PIXABAY_API_KEY/PEXELS_API_KEY.")
    work = ensure_dir(workdir)
    normalized: list[Path] = []
    needed = math.ceil(total_duration / clip_seconds) + 1
    rng = random.Random(seed)
    pool = list(video_paths)
    rng.shuffle(pool)
    sequence: list[Path] = []
    while len(sequence) < needed:
        rng.shuffle(pool)
        sequence.extend(Path(p) for p in pool)
    for i in range(needed):
        src = sequence[i]
        try:
            src_dur = ffprobe_duration(src)
        except Exception:
            src_dur = clip_seconds
        offset = 0.0
        if src_dur > clip_seconds + 1:
            offset = rng.uniform(0, max(0.0, src_dur - clip_seconds - 0.5))
        out = work / f"norm_{i:03d}.mp4"
        normalize_clip(src, out, duration=clip_seconds, width=width, height=height, fps=fps,
                        offset=offset, keep_audio=keep_audio)
        normalized.append(out)

    concat_list = work / "concat.txt"
    concat_list.write_text("".join(f"file '{p.resolve().as_posix()}'\n" for p in normalized), encoding="utf-8")
    bg = work / "background.mp4"
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(concat_list), "-c", "copy", str(bg)])
    return bg


def build_final_video(
    background: str | Path,
    narration: str | Path,
    ass_file: str | Path,
    out_path: str | Path,
    *,
    duration: float,
    music_path: str | Path | None = None,
    music_volume: float = 0.10,
    background_audio: bool = False,
    background_audio_volume: float = 1.0,
    narration_volume: float = 1.0,
) -> Path:
    """background_audio: mix the background clip's own audio track (real
    ASMR trigger sounds -- see build_background's keep_audio) in alongside
    narration, instead of assuming the background is silent. narration_volume
    lets a channel duck narration below the trigger sound (e.g. ch01_ai_asmr)
    so the real satisfying audio -- not the voiceover -- is what's primary,
    matching how actual ASMR channels are built."""
    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    vf = f"ass={_ass_filter_path(ass_file)}"
    bg_leg = f"[0:a]volume={background_audio_volume}[b];" if background_audio else ""
    narr_leg = f"[1:a]volume={narration_volume}[n];" if background_audio else "[1:a]volume=1.0[n];"
    if music_path and Path(music_path).exists():
        mix_inputs = "[b][n][m]" if background_audio else "[n][m]"
        n_inputs = 3 if background_audio else 2
        cmd = [
            "ffmpeg", "-y", "-i", str(background), "-i", str(narration),
            "-stream_loop", "-1", "-i", str(music_path),
            "-filter_complex",
            f"{bg_leg}{narr_leg}"
            f"[2:a]volume={music_volume},atrim=0:{duration:.2f},asetpts=N/SR/TB[m];"
            f"{mix_inputs}amix=inputs={n_inputs}:duration=first:dropout_transition=2[a]",
            "-vf", vf, "-map", "0:v:0", "-map", "[a]", "-t", f"{duration:.2f}",
            "-c:v", "libx264", "-preset", "medium", "-crf", "20",
            "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", "-shortest",
            str(out),
        ]
    elif background_audio:
        cmd = [
            "ffmpeg", "-y", "-i", str(background), "-i", str(narration),
            "-filter_complex",
            f"{bg_leg}{narr_leg}[b][n]amix=inputs=2:duration=first:dropout_transition=2[a]",
            "-vf", vf, "-map", "0:v:0", "-map", "[a]", "-t", f"{duration:.2f}",
            "-c:v", "libx264", "-preset", "medium", "-crf", "20",
            "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", "-shortest",
            str(out),
        ]
    else:
        cmd = [
            "ffmpeg", "-y", "-i", str(background), "-i", str(narration),
            "-vf", vf, "-map", "0:v:0", "-map", "1:a:0", "-t", f"{duration:.2f}",
            "-c:v", "libx264", "-preset", "medium", "-crf", "20",
            "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", "-shortest",
            str(out),
        ]
    run(cmd)
    return out
