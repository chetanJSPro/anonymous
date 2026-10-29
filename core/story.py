"""
story.py — AI storyboard visuals: one generated scene image per beat of the
narration, shown IN ORDER for exactly as long as that beat is spoken, each
with its own camera move. Replaces random shuffled stock b-roll (the
"interchangeable template" look YouTube's 2026 inauthentic-content policy
targets) for channels that set config["visual_mode"] = "story".

Image sources (all free):
  1) Cloudflare Workers AI @cf/black-forest-labs/flux-1-schnell -- cheapest
  2) Cloudflare Workers AI @cf/leonardo/lucid-origin -- 9:16 but ~45x the
     neurons per image (square FLUX output is panned inside the frame)
  Env: CLOUDFLARE_ACCOUNT_ID, CLOUDFLARE_API_TOKEN (Workers AI token)

Returns None from build_story_background when no image source works, so the
caller falls back to the existing stock pipeline -- a channel never fails to
publish because of this module.
"""

import base64
import json
import os
import random
import re
import subprocess
import time
import urllib.error
import urllib.request

from core.llm import generate_script

CF_ACCOUNT_ID = os.environ.get("CLOUDFLARE_ACCOUNT_ID", "")
CF_API_TOKEN = os.environ.get("CLOUDFLARE_API_TOKEN", "")
CF_URL = "https://api.cloudflare.com/client/v4/accounts/{acct}/ai/run/{model}"
MODAL_ENABLED = bool(os.environ.get("MODAL_TOKEN_ID") and os.environ.get("MODAL_TOKEN_SECRET"))
_cf_exhausted = False
_modal_cls = None

# Appended to every prompt -- image models love to paint fake signage/patch
# lettering, which reads as obvious AI garbage on screen.
NO_TEXT = "no text, no letters, no words, no watermark, no captions, no signage"

STORYBOARD_SYSTEM = (
    "You are a film storyboard artist. You turn narration into a sequence of "
    "image-generation prompts for a short vertical video. Reply with ONLY valid JSON."
)


def _cf_run(model, payload, timeout=120):
    req = urllib.request.Request(
        CF_URL.format(acct=CF_ACCOUNT_ID, model=model),
        data=json.dumps(payload).encode("utf-8"),
        headers={"Authorization": f"Bearer {CF_API_TOKEN}", "Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        body = json.loads(resp.read().decode("utf-8"))
    img = (body.get("result") or {}).get("image")
    if not body.get("success") or not img:
        raise RuntimeError(f"Cloudflare {model}: {str(body.get('errors'))[:300]}")
    return base64.b64decode(img)


def generate_scene_image(prompt, out_path, width, height, seed=None):
    """Lucid Origin first (exact aspect ratio), FLUX schnell as fallback
    (always 1024x1024 -- the motion step pans across it). Returns
    (path, is_square). Retries once per model on transient errors."""
    full = f"{prompt}, {NO_TEXT}"
    # Lucid Origin caps each side; keep the aspect ratio, scale down.
    scale = min(1.0, 1344 / max(width, height))
    w, h = int(width * scale) // 16 * 16, int(height * scale) // 16 * 16
    # FLUX schnell first: ~58 neurons/image (4 tiles x 4.8 + 4 steps x 9.6)
    # vs ~2,640 for Lucid Origin at this size, so the free 10k/day covers
    # ~170 scenes instead of ~3. Lucid Origin stays only as a last resort.
    attempts = [
        ("@cf/black-forest-labs/flux-1-schnell", {"prompt": full, "steps": 4,
                                                   **({"seed": seed} if seed is not None else {})}, True),
        ("@cf/leonardo/lucid-origin", {"prompt": full, "width": w, "height": h, "steps": 8,
                                        **({"seed": seed} if seed is not None else {})}, False),
    ]
    global _cf_exhausted
    last = None
    cf_ok = CF_ACCOUNT_ID and CF_API_TOKEN and not _cf_exhausted
    for model, payload, square in (attempts if cf_ok else []):
        for _ in range(2):
            try:
                data = _cf_run(model, payload)
                with open(out_path, "wb") as f:
                    f.write(data)
                return out_path, square
            except urllib.error.HTTPError as e:
                last = e
                # 429 = the account's free 10k neurons/day are spent; that is
                # shared by both models and won't recover until 00:00 UTC.
                if e.code == 429:
                    _cf_exhausted = True
                    print("[story] Cloudflare free daily allocation used up -- using Modal")
                    break
                time.sleep(3)
            except (urllib.error.URLError, RuntimeError, TimeoutError) as e:
                last = e
                time.sleep(3)
        if _cf_exhausted:
            break
    if MODAL_ENABLED:
        try:
            data = _modal_flux().generate.remote(full, 768, 1344, seed)
            with open(out_path, "wb") as f:
                f.write(data)
            return out_path, False
        except Exception as e:
            last = e
    raise RuntimeError(f"all image models failed: {last}")


def _modal_flux():
    """FLUX.1-schnell on Modal (modal_apps/flux_images.py, deployed as
    "story-images"). Paid from Modal credits, so it's the fallback after
    Cloudflare's free tier."""
    global _modal_cls
    if _modal_cls is None:
        import modal
        _modal_cls = modal.Cls.from_name("story-images", "Flux")()
    return _modal_cls


def plan_storyboard(niche, script, beats, art_style):
    """One prompt per beat, with a single fixed character/setting sheet
    prepended to every prompt so the same people/places recur across shots
    (what makes it read as a story rather than a slideshow of strangers)."""
    numbered = "\n".join(f"{i+1}. {b}" for i, b in enumerate(beats))
    user = (
        f"Niche: {niche}\nArt style for every shot: {art_style}\n\n"
        f"Narration, split into {len(beats)} beats:\n{numbered}\n\n"
        "Return JSON: {\"cast\": \"one sentence fixing the main character(s)' exact look "
        "(age, ethnicity, hair, clothing) and the main setting, reused verbatim in every shot\", "
        f"\"shots\": [exactly {len(beats)} strings]}}. Each shot is ONE sentence, under 35 words, "
        "a concrete visual description (do not repeat the cast sentence inside it) "
        "of what that beat shows: subject, action, emotion, camera angle (close-up / wide / "
        "over-the-shoulder / low angle), lighting. Vary the angles. Shot 1 must be the most "
        "striking, emotional image -- it is the scroll-stopping first frame. Never put any "
        "written text, signs, or labels in a shot."
    )
    # gpt-oss on Groq spends part of max_tokens on hidden reasoning -- 1500
    # truncated the JSON mid-string on a 10-beat storyboard (2026-10-28).
    raw = generate_script(STORYBOARD_SYSTEM, user, max_tokens=5000, temperature=0.7)
    m = re.search(r"\{.*\}", raw, re.S)
    data = json.loads(m.group(0) if m else raw)
    shots = [str(s) for s in data.get("shots", [])][:len(beats)]
    if len(shots) < len(beats):
        raise ValueError(f"storyboard returned {len(shots)} shots for {len(beats)} beats")
    cast = str(data.get("cast", "")).strip()
    return [f"{art_style}. {cast} {s}".strip() for s in shots]


def group_beats(segments, target_seconds=3.2):
    """Merge caption Segments (.start/.end/.text) into visual beats of
    roughly target_seconds each -- a new image every ~3s keeps Shorts
    moving without cutting mid-sentence. Returns [(start, end, text)]."""
    beats, cur = [], None
    for seg in segments:
        start, end, text = seg.start, seg.end, seg.text
        if cur is None:
            cur = [start, end, text]
        elif end - cur[0] <= target_seconds * 1.3 and cur[1] - cur[0] < target_seconds:
            cur[1], cur[2] = end, f"{cur[2]} {text}"
        else:
            beats.append(tuple(cur))
            cur = [start, end, text]
    if cur:
        beats.append(tuple(cur))
    return beats


def _motion_clip(image_path, out_path, seconds, width, height, fps, move, square):
    """Still image -> moving shot. Rendered at 2x then downscaled so zoompan's
    integer rounding doesn't jitter. Square sources are always panned
    sideways (they're wider than the vertical frame)."""
    frames = max(1, int(round(seconds * fps)))
    W, H = width * 2, height * 2
    if square:
        side = max(W, H)
        d = max(seconds, 0.1)
        x = f"(iw-{W})*t/{d:.3f}" if move in ("pan_r", "zoom_in") else f"(iw-{W})*(1-t/{d:.3f})"
        vf = f"scale={side}:{side},crop={W}:{H}:'{x}':'(ih-{H})/2',scale={width}:{height}"
    else:
        pre = f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H}"
        z = {"zoom_in": f"1+0.18*on/{frames}", "zoom_out": f"1.18-0.18*on/{frames}",
             "pan_l": "1.12", "pan_r": "1.12"}[move]
        x = {"zoom_in": "iw/2-(iw/zoom/2)", "zoom_out": "iw/2-(iw/zoom/2)",
             "pan_l": f"(iw-iw/zoom)*(1-on/{frames})", "pan_r": f"(iw-iw/zoom)*on/{frames}"}[move]
        vf = (f"{pre},zoompan=z='{z}':x='{x}':y='ih/2-(ih/zoom/2)':d={frames}:"
              f"s={width}x{height}:fps={fps}")
    vf += ",setsar=1,eq=contrast=1.04:saturation=1.06,format=yuv420p"
    cmd = ["ffmpeg", "-y", "-loop", "1", "-framerate", str(fps), "-i", str(image_path),
           "-f", "lavfi", "-i", "anullsrc=channel_layout=stereo:sample_rate=44100",
           "-t", f"{seconds:.3f}", "-vf", vf, "-map", "0:v:0", "-map", "1:a:0",
           "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
           "-c:a", "aac", "-b:a", "128k", "-shortest", str(out_path)]
    proc = subprocess.run(cmd, text=True, capture_output=True)
    if proc.returncode != 0:
        raise RuntimeError(f"ffmpeg motion clip failed: {proc.stderr[-400:]}")
    return out_path


# Per-channel look when a config doesn't set its own "art_style".
DEFAULT_ART_STYLES = {
    "ch03_hindu_mythology": "epic Indian mythological digital painting, divine glow, rich saffron and gold, cinematic",
    "ch06_eastern_philosophy": "serene Studio-Ghibli-inspired painted animation still, soft mist, calm muted palette",
    "hp09_kids_cartoon_stories": "bright friendly 3D cartoon animation still, Pixar-like, colorful, cute characters",
    "hp08_english_learning": "clean colorful flat illustration, modern editorial style, expressive characters",
    "hp06_literary_analysis": "moody painterly book-illustration style, dramatic chiaroscuro",
}


def build_story_background(config, script, segments, duration, out_dir,
                           width, height, fps=30):
    """Full story visual track for one episode, or None if image generation
    isn't available/working (caller then uses the stock pipeline)."""
    if not (CF_ACCOUNT_ID and CF_API_TOKEN) and not MODAL_ENABLED:
        print("[story] no Cloudflare or Modal credentials set -- skipping story mode")
        return None
    beats = group_beats(segments, float(config.get("beat_seconds", 3.2)))
    try:
        prompts = plan_storyboard(config.get("niche", config["name"]), script,
                                  [b[2] for b in beats],
                                  config.get("art_style") or DEFAULT_ART_STYLES.get(
                                      config["name"], "cinematic photorealistic film still, 35mm, dramatic lighting"))
    except Exception as e:
        print(f"[story] storyboard planning failed ({e}) -- skipping story mode")
        return None

    os.makedirs(out_dir, exist_ok=True)
    moves = ["zoom_in", "pan_r", "zoom_out", "pan_l"]
    rng = random.Random()
    seed = rng.randint(1, 2**31 - 1)
    clips, failed = [], 0
    for i, ((start, end, _), prompt) in enumerate(zip(beats, prompts)):
        # Last beat runs to the end of the audio (incl. the tail pad).
        seconds = (duration - start) if i == len(beats) - 1 else (end - start)
        img = os.path.join(out_dir, f"scene_{i:02d}.jpg")
        try:
            _, square = generate_scene_image(prompt, img, width, height, seed=seed + i)
        except Exception as e:
            print(f"[story] scene {i} image failed ({e})")
            failed += 1
            if not clips:
                continue
            # Reuse the previous image with a different move rather than
            # leaving a hole in the timeline.
            img, square = clips[-1][1], clips[-1][2]
        clip = os.path.join(out_dir, f"scene_{i:02d}.mp4")
        _motion_clip(img, clip, max(seconds, 0.5), width, height, fps, moves[i % 4], square)
        clips.append((clip, img, square))
    if not clips or failed > len(beats) // 2:
        print(f"[story] {failed}/{len(beats)} scenes failed -- falling back to stock")
        return None

    concat = os.path.join(out_dir, "story_concat.txt")
    with open(concat, "w", encoding="utf-8") as f:
        f.writelines(f"file '{os.path.abspath(c[0]).replace(os.sep, '/')}'\n" for c in clips)
    bg = os.path.join(out_dir, "story_background.mp4")
    proc = subprocess.run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", concat,
                           "-c", "copy", bg], text=True, capture_output=True)
    if proc.returncode != 0:
        print(f"[story] concat failed: {proc.stderr[-300:]}")
        return None
    print(f"[story] {len(clips)} story scenes built ({failed} reused)")
    return bg
