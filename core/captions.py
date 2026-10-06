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


@dataclass
class _Chunk:
    start: float
    end: float
    text: str
    highlight: bool


def _punch_chunks(segments: list[Segment], max_words: int = 3) -> list[_Chunk]:
    """Split each sentence segment into <=max_words-word chunks, timed by
    character length inside the segment's window (close enough to Kokoro's
    even pacing that captions track the voice without word timestamps)."""
    out: list[_Chunk] = []
    n = 0
    for seg in segments:
        words = seg.text.split()
        groups = [" ".join(words[i:i + max_words]) for i in range(0, len(words), max_words)] or [seg.text]
        total = sum(len(g) + 2 for g in groups)
        t = seg.start
        for g in groups:
            end = t + (seg.end - seg.start) * (len(g) + 2) / total
            out.append(_Chunk(t, end, g, n % 2 == 1))
            n += 1
            t = end
    return out


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
    caption_margin_bottom: int = 340,
    location_label: str | None = None,
    location_font: str = "Arial",
    location_font_size: int = 54,
    location_margin_top: int = 95,
    hook_text: str | None = None,
    hook_seconds: float = 2.6,
    punchy: bool = True,
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
Style: Punch,{caption_font},{int(caption_font_size * 1.35)},&H00FFFFFF,&H0000E5FF,&H00000000,&H00000000,-1,0,0,0,100,100,0,0,1,7,3,5,60,60,0,1
Style: Hook,{caption_font},{int(caption_font_size * 1.05)},&H0000E5FF,&H000000FF,&H00000000,&HCC000000,-1,0,0,0,100,100,0,0,3,18,0,8,60,60,{location_margin_top + 140},1
Style: Location,{location_font},{location_font_size},&H00FFFFFF,&H000000FF,&H00101010,&H85000000,-1,0,0,0,100,100,0,0,3,10,0,8,80,80,{location_margin_top},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    events = [header]
    if location_label:
        loc_text = escape_ass("📍 " + location_label)
        events.append(f"Dialogue: 2,{ass_time(0)},{ass_time(duration)},Location,,0,0,0,,{{\\fad(400,400)}}{loc_text}\n")
    if hook_text:
        hook = escape_ass(wrap_for_ass(hook_text.upper(), max_chars=22))
        events.append(f"Dialogue: 4,{ass_time(0)},{ass_time(min(hook_seconds, duration))},Hook,,0,0,0,,"
                      f"{{\\fad(0,200)\\fscx80\\fscy80\\t(0,150,\\fscx100\\fscy100)}}{hook}\n")
    if punchy:
        # Viral-Shorts caption style: 1-3 huge words centered on screen,
        # pop-in scale, every other chunk in yellow for rhythm.
        for ch in _punch_chunks(segments):
            txt = escape_ass(wrap_for_ass(ch.text.upper(), max_chars=14))
            colour = "\\c&H0000E5FF&" if ch.highlight else ""
            events.append(f"Dialogue: 3,{ass_time(ch.start)},{ass_time(ch.end)},Punch,,0,0,0,,"
                          f"{{{colour}\\fscx70\\fscy70\\t(0,90,\\fscx105\\fscy105)\\t(90,160,\\fscx100\\fscy100)}}{txt}\n")
        segments = []
    for seg in segments:
        txt = escape_ass(wrap_for_ass(seg.text))
        events.append(f"Dialogue: 3,{ass_time(seg.start)},{ass_time(seg.end)},Caption,,0,0,0,,{{\\fad(120,120)}}{txt}\n")
    out.write_text("".join(events), encoding="utf-8")
    return out
