"""
assemble.py — FREE video assembly using MoviePy 2.x (no paid tools, runs locally).

Combines: narration audio + a list of images/video clips (Ken Burns pan-zoom
on images) + burned-in SRT captions -> final MP4, sized for either
YouTube Shorts (1080x1920) or long-form (1920x1080).

Requires ffmpeg on PATH (already present on most systems; install via your
OS package manager if `ffmpeg -version` fails) and a system font — this
module defaults to DejaVu Sans Bold, which ships on virtually all Linux
distros. On Windows/Mac, point CAPTION_FONT at any local .ttf/.otf file.

Usage:
    from core.assemble import build_video
    build_video(
        audio_path="out/voice.mp3",
        visual_paths=["out/img1.jpg", "out/img2.jpg"],
        srt_path="out/voice.srt",
        out_path="out/final.mp4",
        vertical=True,
    )
"""

import os
import glob
from moviepy import (
    AudioFileClip, ImageClip, VideoFileClip, CompositeVideoClip,
    concatenate_videoclips, TextClip,
)

# Default caption font — override with an absolute path to your own .ttf/.otf
# if DejaVu isn't installed (e.g. on Windows: "C:/Windows/Fonts/arialbd.ttf").
_CANDIDATE_FONTS = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
] + glob.glob("/usr/share/fonts/**/*ejaVuSans-Bold.ttf", recursive=True) \
  + glob.glob("/System/Library/Fonts/**/*.ttf", recursive=True) \
  + glob.glob("C:/Windows/Fonts/arialbd.ttf")

CAPTION_FONT = next((f for f in _CANDIDATE_FONTS if os.path.exists(f)), None)


def _ken_burns_clip(img_path, duration, size, zoom_ratio=0.08):
    """Slow pan/zoom on a still image — the classic 'AI documentary' look."""
    clip = ImageClip(img_path)
    w, h = size
    clip = clip.resized(height=h) if clip.h < clip.w else clip.resized(width=w)
    clip = clip.with_duration(duration)
    clip = clip.resized(lambda t: 1 + zoom_ratio * (t / duration))
    return clip.with_position(("center", "center"))


def _visual_clip(path, duration, size):
    if path.lower().endswith((".mp4", ".mov", ".webm")):
        clip = VideoFileClip(path)
        clip = clip.resized(height=size[1]) if clip.h < clip.w else clip.resized(width=size[0])
        if clip.duration < duration:
            loops = int(duration // clip.duration) + 1
            clip = concatenate_videoclips([clip] * loops)
        return clip.subclipped(0, duration).with_position(("center", "center"))
    else:
        return _ken_burns_clip(path, duration, size)


def _parse_srt(srt_path):
    """Minimal SRT parser -> list of (start_sec, end_sec, text)."""
    entries = []
    if not srt_path or not os.path.exists(srt_path):
        return entries
    with open(srt_path, encoding="utf-8") as f:
        blocks = f.read().strip().split("\n\n")
    for block in blocks:
        lines = block.strip().splitlines()
        if len(lines) < 3:
            continue
        timing = lines[1]
        text = " ".join(lines[2:])
        start_str, end_str = timing.split(" --> ")

        def to_sec(t):
            h, m, rest = t.split(":")
            s, ms = rest.split(",")
            return int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000

        entries.append((to_sec(start_str), to_sec(end_str), text))
    return entries


def build_video(audio_path, visual_paths, out_path, srt_path=None,
                 vertical=True, fps=30, caption_fontsize=64,
                 caption_color="white", font_path=None):
    """Assemble final MP4. `visual_paths` is a list of image/video files;
    they are looped/cycled to cover the full narration length."""
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    size = (1080, 1920) if vertical else (1920, 1080)

    audio = AudioFileClip(audio_path)
    total_duration = audio.duration

    if not visual_paths:
        raise ValueError("visual_paths is empty — provide at least one image/video")

    per_clip = max(total_duration / len(visual_paths), 2.0)
    segments = []
    t = 0.0
    i = 0
    while t < total_duration:
        path = visual_paths[i % len(visual_paths)]
        dur = min(per_clip, total_duration - t)
        segments.append(_visual_clip(path, dur, size))
        t += dur
        i += 1

    background = concatenate_videoclips(segments, method="compose").with_duration(total_duration)
    layers = [CompositeVideoClip([background.with_position("center")], size=size)]

    font = font_path or CAPTION_FONT
    if srt_path and font:
        for start, end, text in _parse_srt(srt_path):
            try:
                txt_clip = TextClip(
                    font=font, text=text, font_size=caption_fontsize, color=caption_color,
                    method="caption", size=(size[0] - 120, None),
                    stroke_color="black", stroke_width=3,
                ).with_start(start).with_end(end).with_position(("center", size[1] * 0.72))
                layers.append(txt_clip)
            except Exception as e:
                print(f"[assemble] caption render skipped for '{text[:30]}...': {e}")
    elif srt_path and not font:
        print("[assemble] no caption font found — skipping burned-in captions "
              "(set font_path= to a .ttf/.otf file to enable them). The .srt "
              "file is still saved next to the audio if you want to add captions "
              "later in a video editor.")

    final = CompositeVideoClip(layers, size=size).with_audio(audio).with_duration(total_duration)
    # MoviePy's default temp audio filename is fixed (not derived from out_path),
    # so concurrent build_video() calls (e.g. multiple channels generating at once
    # from the same working directory) collide on it and crash with a
    # WinError 32 / file-in-use error. Deriving it from out_path keeps each
    # run's temp file unique.
    temp_audiofile = os.path.join(
        os.path.dirname(out_path) or ".",
        f"TEMP_MPY_audio_{os.path.splitext(os.path.basename(out_path))[0]}.m4a")
    final.write_videofile(out_path, fps=fps, codec="libx264", audio_codec="aac",
                           threads=4, temp_audiofile=temp_audiofile)
    return out_path


if __name__ == "__main__":
    print("Import and call build_video(...) — see module docstring for usage.")
    print(f"Detected caption font: {CAPTION_FONT or '(none found — captions will be skipped)'}")
