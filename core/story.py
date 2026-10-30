"""
story.py — AI storyboard visuals: one generated scene image per beat of the
narration, shown IN ORDER for exactly as long as that beat is spoken, each
with its own camera move. Replaces random shuffled stock b-roll (the
"interchangeable template" look YouTube's 2026 inauthentic-content policy
targets) for channels that set config["visual_mode"] = "story".

Image sources (all free):
  1) Cloudflare Workers AI @cf/black-forest-labs/flux-2-klein-4b -- native
     9:16, ~100 neurons/image, takes the episode's first scene as a reference
     image so the same character carries through every shot
  2) Cloudflare Workers AI @cf/black-forest-labs/flux-1-schnell -- square
     only (panned inside the frame), used if Klein errors
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
import uuid
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
KLEIN_MODEL = "@cf/black-forest-labs/flux-2-klein-4b"
SCHNELL_MODEL = "@cf/black-forest-labs/flux-1-schnell"
# ~3.5 output tiles at 26 neurons each -- keeps ~10 story channels/day inside
# the free 10k neurons. Upscaled 1.5x to 1080x1920 by the motion step.
KLEIN_SIZE = (720, 1280)
CROSSFADE_SECONDS = 0.25

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


def _cf_run_multipart(model, fields, files=None, timeout=120):
    """FLUX 2 models only accept multipart/form-data."""
    boundary = uuid.uuid4().hex
    body = b""
    for key, value in fields.items():
        body += f'--{boundary}\r\nContent-Disposition: form-data; name="{key}"\r\n\r\n{value}\r\n'.encode("utf-8")
    for key, data in (files or {}).items():
        body += (f'--{boundary}\r\nContent-Disposition: form-data; name="{key}"; filename="{key}.jpg"\r\n'
                 "Content-Type: image/jpeg\r\n\r\n").encode("utf-8") + data + b"\r\n"
    body += f"--{boundary}--\r\n".encode("utf-8")
    req = urllib.request.Request(
        CF_URL.format(acct=CF_ACCOUNT_ID, model=model), data=body, method="POST",
        headers={"Authorization": f"Bearer {CF_API_TOKEN}",
                 "Content-Type": f"multipart/form-data; boundary={boundary}"},
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        result = json.loads(resp.read().decode("utf-8"))
    img = (result.get("result") or {}).get("image")
    if not result.get("success") or not img:
        raise RuntimeError(f"Cloudflare {model}: {str(result.get('errors'))[:300]}")
    return base64.b64decode(img)


def generate_scene_image(prompt, out_path, width, height, seed=None, reference=None):
    """Klein (vertical, can follow a reference image) first, FLUX schnell as
    fallback, then Modal. Returns (path, is_square). Retries once per model on
    transient errors. `reference` is JPEG bytes of the episode's first scene."""
    full = f"{prompt}, {NO_TEXT}"
    klein_fields = {"prompt": full, "width": KLEIN_SIZE[0], "height": KLEIN_SIZE[1],
                    **({"seed": seed} if seed is not None else {})}
    klein_files = {"input_image_0": reference} if reference else None
    # flux-1-schnell's schema is only prompt+steps: sending a seed is a 400
    # (confirmed 2026-10-30 against the live API).
    attempts = [
        (KLEIN_MODEL, lambda: _cf_run_multipart(KLEIN_MODEL, klein_fields, klein_files), False),
        (SCHNELL_MODEL, lambda: _cf_run(SCHNELL_MODEL, {"prompt": full, "steps": 8}), True),
    ]
    global _cf_exhausted
    last = None
    cf_ok = CF_ACCOUNT_ID and CF_API_TOKEN and not _cf_exhausted
    for model, call, square in (attempts if cf_ok else []):
        for _ in range(2):
            try:
                data = call()
                with open(out_path, "wb") as f:
                    f.write(data)
                return out_path, square
            except urllib.error.HTTPError as e:
                last = e
                # 429 = the account's free 10k neurons/day are spent; that is
                # shared by all models and won't recover until 00:00 UTC.
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
        "striking, emotional image of the main character -- it is the scroll-stopping first "
        "frame and the reference for every later shot. Compose for a tall vertical frame with the "
        "subject's head below the top fifth of the frame and nothing important in the lower third "
        "(the hook and captions sit there). Every shot must differ from the last in pose, distance "
        "and angle, and at least a third of the shots should be details or environments without a "
        "face (hands, objects, the place itself). The character never looks into the camera. At "
        "most two people in focus; no crowds in close-up. Never put written text, signs, screens, labels, or "
        "open pages of writing in a shot -- image models garble lettering."
    )
    # gpt-oss on Groq spends part of max_tokens on hidden reasoning -- 1500
    # truncated the JSON mid-string on a 10-beat storyboard (2026-10-28).
    last = None
    for _ in range(2):
        raw = generate_script(STORYBOARD_SYSTEM, user, max_tokens=5000, temperature=0.7)
        m = re.search(r"\{.*\}", raw, re.S)
        try:
            data = json.loads(m.group(0) if m else raw)
        except ValueError as e:
            last = e
            continue
        shots = [str(s) for s in data.get("shots", [])][:len(beats)]
        if len(shots) == len(beats):
            break
        last = ValueError(f"storyboard returned {len(shots)} shots for {len(beats)} beats")
    else:
        raise last
    cast = str(data.get("cast", "")).strip()
    return [f"{art_style}. {cast} {s}".strip() for s in shots]


def group_beats(segments, target_seconds=4.0):
    """Merge caption Segments (.start/.end/.text) into visual beats of
    roughly target_seconds each -- a new image every ~4s keeps Shorts
    moving without cutting mid-sentence or overspending the image quota. Returns [(start, end, text)]."""
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
    """Still image -> moving shot with an eased camera move. Rendered at 2x
    then downscaled so zoompan's integer rounding doesn't jitter. Square
    sources stay near centre (their sides are cropped off a vertical frame)."""
    frames = max(1, int(round(seconds * fps)))
    W, H = width * 2, height * 2
    # smoothstep: the move settles in and out instead of starting abruptly
    ease = f"(pow(on/{frames},2)*(3-2*on/{frames}))"
    if square:
        side = max(W, H)
        d = max(seconds, 0.1)
        drift = f"(t/{d:.3f})" if move in ("pan_r", "zoom_in") else f"(1-t/{d:.3f})"
        vf = f"scale={side}:{side},crop={W}:{H}:'(iw-{W})*(0.40+0.20*{drift})':'(ih-{H})/2',scale={width}:{height}"
    else:
        pre = f"scale={W}:{H}:force_original_aspect_ratio=increase:flags=lanczos,crop={W}:{H}"
        z = {"zoom_in": f"1+0.14*{ease}", "zoom_out": f"1.14-0.14*{ease}",
             "pan_l": "1.10", "pan_r": "1.10"}[move]
        x = {"zoom_in": "iw/2-(iw/zoom/2)", "zoom_out": "iw/2-(iw/zoom/2)",
             "pan_l": f"(iw-iw/zoom)*(1-{ease})", "pan_r": f"(iw-iw/zoom)*{ease}"}[move]
        vf = (f"{pre},zoompan=z='{z}':x='{x}':y='ih/2-(ih/zoom/2)':d={frames}:"
              f"s={width}x{height}:fps={fps}")
    # Light vignette + grain: pulls the eye to the subject and hides the
    # too-clean AI surface; grain also stops banding in skies after re-encode.
    vf += ",setsar=1,eq=contrast=1.04:saturation=1.05,vignette=PI/6,noise=alls=3:allf=t,format=yuv420p"
    cmd = ["ffmpeg", "-y", "-loop", "1", "-framerate", str(fps), "-i", str(image_path),
           "-t", f"{seconds:.3f}", "-vf", vf, "-an",
           "-c:v", "libx264", "-preset", "veryfast", "-crf", "16", str(out_path)]
    proc = subprocess.run(cmd, text=True, capture_output=True)
    if proc.returncode != 0:
        raise RuntimeError(f"ffmpeg motion clip failed: {proc.stderr[-400:]}")
    return out_path


def _join_with_crossfades(clips, scene_seconds, out_path, fps):
    """Dissolve between scenes. Every clip but the last is rendered
    CROSSFADE_SECONDS long, so each new image lands exactly on its beat and
    the total still equals the narration length."""
    inputs, chain, last, t = [], [], "0:v", 0.0
    for i, clip in enumerate(clips):
        inputs += ["-i", clip]
        if i:
            t += scene_seconds[i - 1]
            chain.append(f"[{last}][{i}:v]xfade=transition=fade:duration={CROSSFADE_SECONDS}:"
                         f"offset={t:.3f}[v{i}]")
            last = f"v{i}"
    cmd = ["ffmpeg", "-y", *inputs]
    if chain:
        cmd += ["-filter_complex", ";".join(chain), "-map", f"[{last}]"]
    cmd += ["-r", str(fps), "-c:v", "libx264", "-preset", "veryfast", "-crf", "16",
            "-pix_fmt", "yuv420p", "-an", str(out_path)]
    return subprocess.run(cmd, text=True, capture_output=True)


# Per-channel look when a config doesn't set its own "art_style".
DEFAULT_ART_STYLES = {
    "hp01_betrayal_revenge": "moody neo-noir film still, 35mm, low-key lighting, cold teal shadows, tense atmosphere",
    "hp02_court_drama": "prestige courtroom-drama film still, 35mm, dramatic window light, dark wood, shallow depth of field",
    "hp03_karma_justice": "gritty cinematic film still, 35mm, overcast natural light, muted colors, grounded realism",
    "hp07_senior_longevity": "bright natural-light lifestyle film still, 50mm, soft morning sun, fresh healthy colors, hopeful",
    "ch03_hindu_mythology": "epic Indian mythological digital painting, divine glow, rich saffron and gold, cinematic",
    "ch06_eastern_philosophy": "serene Studio-Ghibli-inspired painted animation still, soft mist, calm muted palette",
    "hp09_kids_cartoon_stories": "bright friendly 3D cartoon animation still, Pixar-like, colorful, cute characters",
    "hp08_english_learning": "clean colorful flat illustration, modern editorial style, expressive characters",
    "hp06_literary_analysis": "moody painterly book-illustration style, dramatic chiaroscuro",
}


def _reference_bytes(image_path, out_path):
    """Small copy of the first scene -- each input tile costs neurons, and
    this resolution is enough to hold a character's face and clothing."""
    proc = subprocess.run(["ffmpeg", "-y", "-i", str(image_path), "-vf", "scale=384:-2",
                           "-q:v", "3", str(out_path)], text=True, capture_output=True)
    if proc.returncode != 0:
        return None
    with open(out_path, "rb") as f:
        return f.read()


def build_story_background(config, script, segments, duration, out_dir,
                           width, height, fps=30):
    """Full story visual track for one episode, or None if image generation
    isn't available/working (caller then uses the stock pipeline)."""
    if not (CF_ACCOUNT_ID and CF_API_TOKEN) and not MODAL_ENABLED:
        print("[story] no Cloudflare or Modal credentials set -- skipping story mode")
        return None
    beats = group_beats(segments, float(config.get("beat_seconds", 4.0)))
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
    images, reference = [], None
    for i, prompt in enumerate(prompts):
        img = os.path.join(out_dir, f"scene_{i:02d}.jpg")
        if reference:
            # Identity only: left unqualified, Klein also copies the reference's
            # pose and framing and every shot comes out the same portrait.
            prompt = (f"Keep only the person's face, hair and clothing from the reference image; "
                      f"use a completely new pose, camera angle and framing. {prompt}")
        try:
            _, square = generate_scene_image(prompt, img, width, height, seed=seed + i, reference=reference)
            images.append((img, square))
            if reference is None and not square:
                reference = _reference_bytes(img, os.path.join(out_dir, "reference.jpg"))
        except Exception as e:
            print(f"[story] scene {i} image failed ({e})")
            images.append(None)
    failed = images.count(None)
    # A reused image is a visibly repeated shot, so this is deliberately
    # stricter than "most scenes worked" -- skip the episode instead.
    if failed > len(beats) // 4:
        print(f"[story] {failed}/{len(beats)} scenes failed -- no story background")
        return None
    # Fill any hole from a neighbouring scene (the next move still differs)
    # so every beat keeps its slot on the timeline, including beat 0.
    for i in list(range(1, len(images))) + list(range(len(images) - 2, -1, -1)):
        if images[i] is None:
            images[i] = images[i - 1] if i and images[i - 1] else images[min(i + 1, len(images) - 1)]

    # Each scene runs up to the next beat's start, and the last to the end of
    # the audio (incl. the tail pad), so pauses never desync pictures from voice.
    starts = [0.0] + [b[0] for b in beats[1:]]
    ends = starts[1:] + [duration]
    scene_seconds = [max(e - st, 0.5) for st, e in zip(starts, ends)]
    clips = []
    for i, ((img, square), seconds) in enumerate(zip(images, scene_seconds)):
        extra = CROSSFADE_SECONDS if i < len(images) - 1 else 0.0
        clip = os.path.join(out_dir, f"scene_{i:02d}.mp4")
        _motion_clip(img, clip, seconds + extra, width, height, fps, moves[i % 4], square)
        clips.append(clip)

    bg = os.path.join(out_dir, "story_background.mp4")
    proc = _join_with_crossfades(clips, scene_seconds, bg, fps)
    if proc.returncode != 0:
        print(f"[story] crossfade join failed: {proc.stderr[-300:]}")
        return None
    print(f"[story] {len(clips)} story scenes built ({failed} reused, "
          f"reference image: {'yes' if reference else 'no'})")
    return bg
