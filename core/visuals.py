"""
visuals.py — FREE visual sourcing: stock video/images from two libraries +
AI-generated images, usually combined for maximum variety per episode.

Three free sources:

1) Pixabay (stock video + photos) — FREE, needs a free API key.
   Sign up: https://pixabay.com/accounts/register/  -> https://pixabay.com/api/docs/
   Set env var: PIXABAY_API_KEY

2) Pexels (stock video + photos) — FREE, needs a free API key, usually a
   larger/higher-production-value library than Pixabay for "people" and
   "lifestyle" style footage.
   Sign up: https://www.pexels.com/api/  -> your API key is on that page.
   Set env var: PEXELS_API_KEY

3) Pollinations.ai (AI image generation) — FREE, ZERO signup, no key needed.
   Just build a URL and download the image. Good for custom/stylized scenes
   real stock footage can't match (mythology, dramatic reenactment framing,
   flat-design illustration for the English-learning channel, etc).

4) Agnes AI (agnes-ai.com, real text-to-video generation) — FREE tier,
   needs a free API key (enter at agnes-ai.com, signup required unlike
   Pollinations). ~16 requests/minute. Used as an ACCENT source only, a
   handful of clips per episode topped up with stock video — reviews flag
   inconsistent motion quality on complex scenes, so this is layered on top
   of the stock pipeline, never the sole source. If AGNES_API_KEY isn't set,
   or a generation fails/rate-limits, `fetch_hybrid_stock_agnes_videos`
   silently falls back to 100% stock video — never blocks a run.
   Set env var: AGNES_API_KEY

Usage:
    from core.visuals import fetch_pixabay_videos, fetch_pixabay_images
    from core.visuals import fetch_pexels_videos, fetch_pexels_images
    from core.visuals import generate_ai_image, fetch_mixed_visuals
    from core.visuals import fetch_agnes_videos, fetch_hybrid_stock_agnes_videos
"""

import os
import time
import random
import urllib.request
import urllib.parse
import json

PIXABAY_API_KEY = os.environ.get("PIXABAY_API_KEY", "")
PIXABAY_VIDEO_URL = "https://pixabay.com/api/videos/"
PIXABAY_IMAGE_URL = "https://pixabay.com/api/"

PEXELS_API_KEY = os.environ.get("PEXELS_API_KEY", "")
PEXELS_VIDEO_URL = "https://api.pexels.com/videos/search"
PEXELS_IMAGE_URL = "https://api.pexels.com/v1/search"

POLLINATIONS_IMAGE_URL = "https://image.pollinations.ai/prompt/"

AGNES_API_KEY = os.environ.get("AGNES_API_KEY", "")
AGNES_CREATE_URL = "https://apihub.agnes-ai.com/v1/videos"
AGNES_STATUS_URL = "https://apihub.agnes-ai.com/agnesapi"

# Neither Pixabay nor Pexels do real semantic matching -- a thin-result niche
# query (e.g. "ganges river ghat india") falls back to loosely related
# "popular" clips, which is how an unrelated lipstick/makeup clip ended up
# cut into a Kurukshetra mythology narration. This is a blocklist backstop:
# categories that should never appear under any of this project's niches
# (spiritual, ASMR-food/craft, story-narration b-roll), checked against
# Pixabay's tags field and Pexels' descriptive URL slug (its only text field).
OFF_THEME_BLOCKLIST = [
    "lipstick", "makeup", "make up", "make-up", "cosmetic", "cosmetics",
    "mascara", "nail polish", "nail art", "manicure", "eyeshadow",
    "skincare", "skin care", "perfume", "beauty product", "beauty routine",
    "hair salon", "haircut tutorial",
]


def _tags_or_slug_ok(hit_text: str) -> bool:
    t = (hit_text or "").lower()
    return not any(bad in t for bad in OFF_THEME_BLOCKLIST)


def _download(url, out_path, timeout=60, headers=None):
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0", **(headers or {})})
    with urllib.request.urlopen(req, timeout=timeout) as resp, open(out_path, "wb") as f:
        f.write(resp.read())
    return out_path


# ---------------------------------------------------------------- Pixabay --

def fetch_pixabay_videos(query, out_dir, count=5, min_duration=5):
    """Download up to `count` free stock video clips matching `query`."""
    if not PIXABAY_API_KEY:
        raise RuntimeError("Set PIXABAY_API_KEY env var (free signup at pixabay.com)")
    params = {
        "key": PIXABAY_API_KEY,
        "q": query,
        "video_type": "film",
        "per_page": max(count * 5, 20),
        "safesearch": "true",
    }
    url = PIXABAY_VIDEO_URL + "?" + urllib.parse.urlencode(params)
    with urllib.request.urlopen(url, timeout=30) as resp:
        data = json.loads(resp.read().decode("utf-8"))

    paths = []
    for hit in data.get("hits", []):
        if len(paths) >= count:
            break
        if not _tags_or_slug_ok(hit.get("tags", "")):
            print(f"[visuals] skipped off-theme Pixabay clip (tags: {hit.get('tags', '')!r})")
            continue
        video_url = hit["videos"]["medium"]["url"] if "medium" in hit["videos"] else hit["videos"]["small"]["url"]
        out_path = os.path.join(out_dir, f"pixabay_{query.replace(' ', '_')}_{len(paths)}.mp4")
        paths.append(_download(video_url, out_path))
        time.sleep(0.5)
    return paths


def fetch_pixabay_images(query, out_dir, count=5):
    """Download up to `count` free stock images matching `query`."""
    if not PIXABAY_API_KEY:
        raise RuntimeError("Set PIXABAY_API_KEY env var (free signup at pixabay.com)")
    params = {
        "key": PIXABAY_API_KEY,
        "q": query,
        "image_type": "photo",
        "per_page": max(count, 3),
        "safesearch": "true",
    }
    url = PIXABAY_IMAGE_URL + "?" + urllib.parse.urlencode(params)
    with urllib.request.urlopen(url, timeout=30) as resp:
        data = json.loads(resp.read().decode("utf-8"))

    paths = []
    for i, hit in enumerate(data.get("hits", [])[:count]):
        img_url = hit["largeImageURL"]
        out_path = os.path.join(out_dir, f"pixabay_{query.replace(' ', '_')}_{i}.jpg")
        paths.append(_download(img_url, out_path))
        time.sleep(0.5)
    return paths


# ----------------------------------------------------------------- Pexels --

def fetch_pexels_videos(query, out_dir, count=5, orientation=None):
    """Download up to `count` free stock video clips matching `query`.
    orientation: "portrait" for Shorts, "landscape" for long-form (optional
    filter — Pexels supports it server-side, unlike Pixabay)."""
    if not PEXELS_API_KEY:
        raise RuntimeError("Set PEXELS_API_KEY env var (free signup at pexels.com/api)")
    params = {"query": query, "per_page": max(count * 5, 20)}
    if orientation:
        params["orientation"] = orientation
    url = PEXELS_VIDEO_URL + "?" + urllib.parse.urlencode(params)
    with urllib.request.urlopen(
            urllib.request.Request(url, headers={"Authorization": PEXELS_API_KEY, "User-Agent": "Mozilla/5.0"}),
            timeout=30) as resp:
        data = json.loads(resp.read().decode("utf-8"))

    paths = []
    for video in data.get("videos", []):
        if len(paths) >= count:
            break
        # Pexels gives no tags — its descriptive page URL slug (e.g.
        # ".../video/woman-applying-lipstick-1234567/") is the only text to
        # filter on.
        if not _tags_or_slug_ok(video.get("url", "")):
            print(f"[visuals] skipped off-theme Pexels clip ({video.get('url', '')!r})")
            continue
        files = sorted(video.get("video_files", []),
                        key=lambda f: f.get("width", 0) or 0)
        # prefer a mid-resolution file (smaller/faster download, still crisp on Shorts)
        candidates = [f for f in files if 720 <= (f.get("width") or 0) <= 1920] or files
        if not candidates:
            continue
        video_url = candidates[len(candidates) // 2]["link"]
        out_path = os.path.join(out_dir, f"pexels_{query.replace(' ', '_')}_{len(paths)}.mp4")
        paths.append(_download(video_url, out_path))
        time.sleep(0.5)
    return paths


def fetch_pexels_images(query, out_dir, count=5):
    """Download up to `count` free stock images matching `query`."""
    if not PEXELS_API_KEY:
        raise RuntimeError("Set PEXELS_API_KEY env var (free signup at pexels.com/api)")
    params = {"query": query, "per_page": max(count, 3)}
    url = PEXELS_IMAGE_URL + "?" + urllib.parse.urlencode(params)
    with urllib.request.urlopen(
            urllib.request.Request(url, headers={"Authorization": PEXELS_API_KEY, "User-Agent": "Mozilla/5.0"}),
            timeout=30) as resp:
        data = json.loads(resp.read().decode("utf-8"))

    paths = []
    for i, photo in enumerate(data.get("photos", [])[:count]):
        img_url = photo["src"]["large2x"]
        out_path = os.path.join(out_dir, f"pexels_{query.replace(' ', '_')}_{i}.jpg")
        paths.append(_download(img_url, out_path))
        time.sleep(0.5)
    return paths


# --------------------------------------------------------- Pollinations AI --

def generate_ai_image(prompt, out_path, width=1080, height=1920, seed=None):
    """Generate a free AI image via Pollinations.ai — no key, no signup.
    Good for vertical (1080x1920) short backgrounds or 16:9 (1920x1080) long-form."""
    if seed is None:
        seed = random.randint(1, 999999)
    encoded = urllib.parse.quote(prompt)
    url = f"{POLLINATIONS_IMAGE_URL}{encoded}?width={width}&height={height}&seed={seed}&nologo=true"
    return _download(url, out_path)


def generate_ai_image_batch(prompts, out_dir, width=1080, height=1920):
    paths = []
    for i, p in enumerate(prompts):
        out_path = os.path.join(out_dir, f"ai_img_{i}.jpg")
        paths.append(generate_ai_image(p, out_path, width, height, seed=i))
        time.sleep(1)  # be polite to the free endpoint
    return paths


# --------------------------------------------------------------- Agnes AI --

def _agnes_num_frames(seconds, frame_rate=24):
    """Agnes requires num_frames = 8n+1, max 441. Pick the closest valid
    value to the requested duration at the given frame rate."""
    target = round(seconds * frame_rate)
    n = max(1, round((target - 1) / 8))
    frames = min(441, 8 * n + 1)
    return frames


def generate_agnes_video(prompt, out_path, seconds=5, frame_rate=24,
                          width=1080, height=1920, poll_timeout=180, poll_interval=5):
    """Generate one AI video clip via Agnes AI's free text-to-video API.
    Raises on any failure (missing key, HTTP error, timeout, job failed) —
    callers should catch and fall back to stock video, this is not meant to
    be a hard dependency for any channel."""
    if not AGNES_API_KEY:
        raise RuntimeError("Set AGNES_API_KEY env var (free signup at agnes-ai.com)")
    import requests  # already a project dependency

    headers = {"Authorization": f"Bearer {AGNES_API_KEY}", "Content-Type": "application/json"}
    body = {
        "model": "agnes-video-v2.0",
        "prompt": prompt,
        "num_frames": _agnes_num_frames(seconds, frame_rate),
        "frame_rate": frame_rate,
        "width": width,
        "height": height,
    }
    resp = requests.post(AGNES_CREATE_URL, headers=headers, json=body, timeout=30)
    resp.raise_for_status()
    video_id = resp.json().get("video_id") or resp.json().get("id")
    if not video_id:
        raise RuntimeError(f"Agnes AI create-job response had no video_id: {resp.text[:300]}")

    waited = 0
    while waited < poll_timeout:
        time.sleep(poll_interval)
        waited += poll_interval
        status_resp = requests.get(AGNES_STATUS_URL, headers=headers,
                                    params={"video_id": video_id}, timeout=30)
        status_resp.raise_for_status()
        data = status_resp.json()
        status = data.get("status")
        if status == "completed":
            video_url = (data.get("metadata") or {}).get("url")
            if not video_url:
                raise RuntimeError(f"Agnes AI job completed but no output url: {data}")
            return _download(video_url, out_path)
        if status == "failed":
            raise RuntimeError(f"Agnes AI job {video_id} failed: {data}")
        # queued / in_progress -> keep polling
    raise RuntimeError(f"Agnes AI job {video_id} timed out after {poll_timeout}s")


def fetch_agnes_videos(prompts, out_dir, count=3, vertical=True, seconds=5):
    """Best-effort: generate up to `count` AI video clips via Agnes AI.
    Returns whatever succeeded (possibly an empty list) — never raises, so
    callers can always safely top up with stock video."""
    size = (1080, 1920) if vertical else (1920, 1080)
    paths = []
    for i, prompt in enumerate(prompts[:count]):
        try:
            out_path = os.path.join(out_dir, f"agnes_{i}.mp4")
            paths.append(generate_agnes_video(prompt, out_path, seconds=seconds,
                                                width=size[0], height=size[1]))
            print(f"[visuals] Agnes AI clip {i+1}/{min(count, len(prompts))} ready")
        except Exception as e:
            print(f"[visuals] Agnes AI failed for {prompt!r} ({e}) — skipping")
        time.sleep(4)  # stay well under the free tier's ~16 req/min shared limit
    return paths


# ------------------------------------------------------------------ Mixed --

def fetch_mixed_visuals(stock_queries, ai_prompts, out_dir, vertical=True,
                         stock_count_per_query=2):
    """The recommended default: real stock VIDEO clips (Pexels first, falls
    back to Pixabay per query if Pexels has no key/results) for genuine
    motion, plus a couple of AI-generated images for shots stock footage
    can't cover. Returns a shuffled list of local file paths (mp4s + jpgs)
    ready for core.assemble.build_video, which handles both.

    stock_queries: list[str] of plain b-roll search terms (e.g. "empty
      courtroom", "hands typing") — keep these generic/real-world, AI
      prompts stay separate since stock search doesn't understand "cinematic
      photorealistic" style language.
    ai_prompts: list[str] of Pollinations-style prompts for the 1-2 shots
      that need a custom/stylized look.
    """
    orientation = "portrait" if vertical else "landscape"
    size = (1080, 1920) if vertical else (1920, 1080)
    paths = []

    for q in stock_queries:
        clips = []
        if PEXELS_API_KEY:
            try:
                clips = fetch_pexels_videos(q, out_dir, count=stock_count_per_query, orientation=orientation)
            except Exception as e:
                print(f"[visuals] Pexels failed for {q!r} ({e}), trying Pixabay...")
        if not clips and PIXABAY_API_KEY:
            try:
                clips = fetch_pixabay_videos(q, out_dir, count=stock_count_per_query)
            except Exception as e:
                print(f"[visuals] Pixabay also failed for {q!r} ({e})")
        paths += clips

    for i, p in enumerate(ai_prompts):
        try:
            paths.append(generate_ai_image(p, os.path.join(out_dir, f"ai_img_{i}.jpg"),
                                             width=size[0], height=size[1], seed=i))
            time.sleep(1)
        except Exception as e:
            print(f"[visuals] AI image failed for {p!r}: {e}")

    if not paths:
        raise RuntimeError(
            "fetch_mixed_visuals produced 0 usable clips/images — check "
            "PEXELS_API_KEY / PIXABAY_API_KEY are set, or that ai_prompts is non-empty.")

    random.shuffle(paths)
    return paths


# -------------------------------------------------------------- Video-only --

def fetch_stock_videos(queries, out_dir, count=8, vertical=True):
    """The active default for all 11 channels: real stock VIDEO clips only —
    no AI stills. Tries Pexels first per query (usually higher production
    value), tops up with Pixabay if Pexels has no key/results or count isn't
    met yet. Matches core/video_builder.build_background's input (a flat
    list of local video file paths)."""
    orientation = "portrait" if vertical else "landscape"
    paths = []
    shuffled = list(queries)
    random.shuffle(shuffled)
    for q in shuffled:
        if len(paths) >= count:
            break
        remaining = count - len(paths)
        clips = []
        if PEXELS_API_KEY:
            try:
                clips = fetch_pexels_videos(q, out_dir, count=min(2, remaining), orientation=orientation)
            except Exception as e:
                print(f"[visuals] Pexels failed for {q!r} ({e}), trying Pixabay...")
        if not clips and PIXABAY_API_KEY:
            try:
                clips = fetch_pixabay_videos(q, out_dir, count=min(2, remaining))
            except Exception as e:
                print(f"[visuals] Pixabay also failed for {q!r} ({e})")
        paths += clips

    if not paths:
        raise RuntimeError(
            "fetch_stock_videos produced 0 clips — check PEXELS_API_KEY / "
            "PIXABAY_API_KEY are set in .env.")

    random.shuffle(paths)
    return paths


def fetch_hybrid_stock_agnes_videos(queries, out_dir, count=8, vertical=True,
                                     agnes_count=6, agnes_seconds=5):
    """The active default for all 11 channels: mostly real AI-generated video
    clips (Agnes AI) for a consistent human/cinematic look, topped up with
    real stock video (Pexels/Pixabay) for whatever Agnes doesn't cover.
    Falls back to 100% stock if AGNES_API_KEY isn't set or every Agnes
    attempt fails/rate-limits — a channel never fails to produce a video
    just because Agnes is down. Same return shape as fetch_stock_videos: a
    shuffled list of local mp4 paths ready for core.video_builder.build_background."""
    agnes_paths = []
    if AGNES_API_KEY and agnes_count > 0:
        prompts = [f"{q}, cinematic, photorealistic, dramatic lighting" for q in queries]
        agnes_paths = fetch_agnes_videos(prompts, out_dir, count=agnes_count,
                                          vertical=vertical, seconds=agnes_seconds)

    stock_needed = max(0, count - len(agnes_paths))
    stock_paths = []
    if stock_needed > 0:
        stock_paths = fetch_stock_videos(queries, out_dir, count=stock_needed, vertical=vertical)

    paths = agnes_paths + stock_paths
    if not paths:
        raise RuntimeError(
            "fetch_hybrid_stock_agnes_videos produced 0 usable clips — check "
            "AGNES_API_KEY / PEXELS_API_KEY / PIXABAY_API_KEY.")
    random.shuffle(paths)
    return paths


if __name__ == "__main__":
    generate_ai_image("ancient khmer empire temple at sunrise, cinematic, epic",
                       "out/test_ai_img.jpg")
    print("saved out/test_ai_img.jpg")
