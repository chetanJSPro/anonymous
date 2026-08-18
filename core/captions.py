"""
captions.py — ported from peace_reels_automation/src/captions.py so all
anonymous-master channels get the same subtitle quality: proper per-line
timing (weighted by line length, not just an even split), wrapped/escaped
ASS text with fade-in/out and outline/shadow styling burned in via ffmpeg
(see core/video_builder.py), instead of core/assemble.py's old plain
MoviePy TextClip captions.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass
class Segment:
    start: float
    end: float
    text: str


def distribute_segments(lines: list[str], duration: float, *, lead_in: float = 0.25, lead_out: float = 0.3) -> list[Segment]:
    lines = [l.strip() for l in lines if l.strip()]
    if not lines:
        return []
    usable = max(1.0, duration - lead_in - lead_out)
    weights = [max(1, len(l)) for l in lines]
    total = sum(weights)
    t = lead_in
    segs: list[Segment] = []
    for i, line in enumerate(lines):
        # Minimum on-screen time keeps short lines readable.
        share = usable * weights[i] / total
        length = max(1.6, share)
        if i == len(lines) - 1:
            end = max(t + 1.6, duration - lead_out)
        else:
            end = min(duration - lead_out, t + length)
        segs.append(Segment(t, end, line))
        t = end
    return segs


def ass_time(seconds: float) -> str:
    seconds = max(0, seconds)
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    cs = int(round((seconds - int(seconds)) * 100))
    return f"{h}:{m:02d}:{s:02d}.{cs:02d}"


def srt_time(seconds: float) -> str:
    seconds = max(0, seconds)
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int(round((seconds - int(seconds)) * 1000))
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def escape_ass(text: str) -> str:
    return text.replace("{", "(").replace("}", ")").replace("\n", r"\N")


def wrap_for_ass(text: str, max_chars: int = 28) -> str:
    words = text.split()
    lines = []
    cur = ""
    for w in words:
        if len(cur) + len(w) + 1 > max_chars and cur:
            lines.append(cur)
            cur = w
        else:
            cur = w if not cur else cur + " " + w
    if cur:
        lines.append(cur)
    return r"\N".join(lines)


def write_srt(segments: list[Segment], out_path: str | Path) -> Path:
    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    parts = []
    for i, seg in enumerate(segments, 1):
        parts.append(f"{i}\n{srt_time(seg.start)} --> {srt_time(seg.end)}\n{seg.text}\n")
    out.write_text("\n".join(parts), encoding="utf-8")
    return out


def write_ass(
    segments: list[Segment],
    out_path: str | Path,
    *,
    width: int = 1080,
    height: int = 1920,
    duration: float = 30.0,
    caption_font: str = "Arial",
    caption_font_size: int = 76,
    caption_margin_bottom: int = 240,
    location_label: str | None = None,
    location_font: str = "Arial",
    location_font_size: int = 54,
    location_margin_top: int = 95,
) -> Path:
    """Burned-in caption track. `location_label` is optional here (unlike the
    India-pin-specific original) — most anonymous-master niches have no
    location concept, so it's only drawn when a channel config sets one."""
    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    header = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {width}
PlayResY: {height}
ScaledBorderAndShadow: yes
WrapStyle: 0

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Caption,{caption_font},{caption_font_size},&H00FFFFFF,&H000000FF,&H00101010,&H99000000,-1,0,0,0,100,100,0,0,1,4,2,2,70,70,{caption_margin_bottom},1
Style: Location,{location_font},{location_font_size},&H00FFFFFF,&H000000FF,&H00101010,&H85000000,-1,0,0,0,100,100,0,0,3,10,0,8,80,80,{location_margin_top},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    events = [header]
    if location_label:
        loc_text = escape_ass("📍 " + location_label)
        events.append(f"Dialogue: 2,{ass_time(0)},{ass_time(duration)},Location,,0,0,0,,{{\\fad(400,400)}}{loc_text}\n")
    for seg in segments:
        txt = escape_ass(wrap_for_ass(seg.text))
        events.append(f"Dialogue: 3,{ass_time(seg.start)},{ass_time(seg.end)},Caption,,0,0,0,,{{\\fad(120,120)}}{txt}\n")
    out.write_text("".join(events), encoding="utf-8")
    return out
