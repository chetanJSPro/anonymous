"""
llm.py — FREE script generation.

Primary: Groq API (free tier, no credit card, very fast Llama/Mixtral models)
  Sign up: https://console.groq.com  -> API Keys -> create key
  Set env var: GROQ_API_KEY

Fallback (zero signup at all): Pollinations.ai text endpoint (free, no key,
lower reliability / rate limited, good as an emergency backup only).

Usage:
    from core.llm import generate_script
    text = generate_script(system_prompt, user_prompt)
"""

import os
import re
import json
import time
import random
import urllib.request
import urllib.error

GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
GROQ_MODEL = os.environ.get("GROQ_MODEL", "openai/gpt-oss-120b")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

POLLINATIONS_TEXT_URL = "https://text.pollinations.ai/openai"


def _post_json(url, payload, headers, timeout=60, retries=3):
    data = json.dumps(payload).encode("utf-8")
    headers = {**headers, "User-Agent": "Mozilla/5.0"}
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    last_err = None
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            last_err = e
            body = e.read().decode("utf-8", errors="ignore")
            if e.code == 429:
                # Jittered backoff -- with 4 channels running in parallel
                # (GitHub Actions matrix max-parallel: 4), all 4 tend to
                # hit Groq's per-minute free-tier limit at nearly the same
                # moment and, without jitter, retry in lockstep too,
                # re-colliding on the same rate limit every round.
                time.sleep(4 * (attempt + 1) + random.uniform(0, 2))
                continue
            raise RuntimeError(f"LLM HTTP {e.code}: {body}")
        except Exception as e:
            last_err = e
            time.sleep(2 * (attempt + 1))
    raise RuntimeError(f"LLM request failed after {retries} retries: {last_err}")


def _groq_chat(system_prompt, user_prompt, max_tokens=1200, temperature=0.9):
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": GROQ_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "max_tokens": max_tokens,
        "temperature": temperature,
    }
    # retries=6 (up from the 3 default) -- confirmed 2026-08-20: 4 parallel
    # channel jobs each now make several Groq calls per episode (script,
    # visual queries, hook title), and free-tier 429s under that load are
    # common enough that 3 retries wasn't enough headroom before falling
    # through to the Pollinations fallback, which is itself dead (402
    # Payment Required as of Aug 2026, see CLAUDE.md) -- so a Groq 429
    # that outlasts the retry budget currently has nowhere left to go.
    result = _post_json(GROQ_URL, payload, headers, retries=6)
    return result["choices"][0]["message"]["content"].strip()


def _pollinations_chat(system_prompt, user_prompt):
    headers = {"Content-Type": "application/json"}
    payload = {
        "model": "openai",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    }
    result = _post_json(POLLINATIONS_TEXT_URL, payload, headers)
    return result["choices"][0]["message"]["content"].strip()


def generate_script(system_prompt, user_prompt, max_tokens=1200, temperature=0.9):
    """Generate a script. Uses Groq if GROQ_API_KEY is set, else falls back
    to the keyless Pollinations endpoint (less reliable, use as backup)."""
    if GROQ_API_KEY:
        try:
            return _groq_chat(system_prompt, user_prompt, max_tokens, temperature)
        except Exception as e:
            print(f"[llm] Groq failed ({e}), falling back to Pollinations...")
    return _pollinations_chat(system_prompt, user_prompt)


def generate_topic(niche_hint, avoid_topics, max_tokens=300):
    """One fresh topic idea for a channel's niche, steered away from
    recently-used topics so a channel doesn't need hundreds of hand-written
    topic_prompts to stay unique run over run — see core/topics.py, which
    persists the avoid-list per channel.

    max_tokens is generous even though the answer itself is short: GROQ_MODEL
    (openai/gpt-oss-120b) is a reasoning model that spends part of the token
    budget on hidden reasoning tokens before the visible answer — too low a
    budget (e.g. 60) silently returns an empty string with nothing left over
    for the actual reply."""
    system = (
        "You generate ONE fresh, specific, engaging video topic idea for a YouTube channel. "
        "Reply with ONLY the topic phrase itself — no numbering, no quotes, no preamble, "
        "under 20 words."
    )
    avoid_block = "\n".join(f"- {t}" for t in avoid_topics[-25:]) or "(none yet)"
    user = (
        f"Channel niche/style:\n{niche_hint}\n\n"
        f"Topics already used recently — do NOT repeat these or anything too similar:\n{avoid_block}\n\n"
        "Give one new topic idea for this channel."
    )
    topic = generate_script(system, user, max_tokens=max_tokens, temperature=1.05)
    return topic.strip().strip('"').strip("'").split("\n")[0].strip()


_PREAMBLE_RE = re.compile(
    r"^\s*(?:sure[,!.\s]+|okay[,!.\s]+|alright[,!.\s]+|certainly[,!.\s]+|"
    r"here'?s?\s+(?:is\s+)?(?:the|your|a)\s+script\b[^\n]*\n?|"
    r"title\s*:[^\n]*\n?|script\s*:\s*)",
    re.IGNORECASE,
)
_STAGE_DIRECTION_RE = re.compile(r"\((?:[^()]{0,80})\)|\[(?:[^\[\]]{0,80})\]|\*(?:[^*\n]{1,80})\*")
_GREETING_OPENER_RE = re.compile(
    r"^\s*(?:hey|hi|hello|yo|what'?s up|welcome back|welcome)\b[^.!?\n]{0,40}?[.!?,]\s*",
    re.IGNORECASE,
)


def sanitize_narration_script(text: str) -> str:
    """Strip common LLM script-generation junk before it ever reaches TTS.
    Confirmed real failure modes: stage directions like "(laughs)" or
    "*chuckles*" get read aloud verbatim by Kokoro as literal words, chatty
    preambles like "Sure, here's your script:" leak into the narration, and
    generic vlogger-style greeting openers ("Hey friends, you have been...")
    slip in despite system prompts asking for a first-person confession/
    story style — all instantly read as AI-generated filler, not a
    genuine story. This is a best-effort regex safety net on top of the
    system prompt instruction, not a replacement for it."""
    t = text.strip()
    for _ in range(3):  # "Sure, " and "here's your script:" can both lead --
        new_t = _PREAMBLE_RE.sub("", t).strip()  # strip repeatedly till stable
        if new_t == t:
            break
        t = new_t
    t = _STAGE_DIRECTION_RE.sub("", t)
    for _ in range(2):  # chained greetings, e.g. "Hey guys, welcome back!"
        new_t = _GREETING_OPENER_RE.sub("", t, count=1).strip()
        if new_t == t:
            break
        t = new_t
    t = re.sub(r"[ \t]{2,}", " ", t)
    t = re.sub(r"\n{3,}", "\n\n", t)
    t = re.sub(r"\s+([.,!?])", r"\1", t)
    t = t.strip()
    if t:
        t = t[0].upper() + t[1:]
    return t


def generate_visual_queries(niche_hint, topic, script, count=8, fallback=None):
    """Derive concrete, story-specific visual search/prompt terms from the
    actual generated script, instead of a static per-channel query list --
    a static list produces visuals unrelated to the specific story being
    told (generic "office meeting" b-roll under a script that never
    mentions an office), which reads as stock footage bolted on rather
    than visuals that match what's being narrated. These queries feed both
    the stock video search (Pexels/Pixabay) and the Agnes AI prompts, so
    improving them improves whichever source ends up used.
    Best-effort: falls back to `fallback` (the channel's static query list)
    on any failure or a too-short response."""
    system = (
        f"You extract concrete visual scene descriptions for video footage to "
        f"accompany a short narrated video. Channel style: {niche_hint}. Reply "
        f"with exactly {count} short visual scene descriptions, one per line, "
        f"no numbering, no quotes, no extra commentary -- each a concrete, "
        f"filmable real-world scene (a place, an action, an object, a mood) "
        f"tied to specific moments or details in the story below, not generic "
        f"stock-photo phrases."
    )
    user = f"Topic: {topic}\n\nStory:\n{script}\n\nGive {count} visual scene descriptions."
    try:
        raw = generate_script(system, user, max_tokens=400, temperature=0.8)
        lines = [l.strip(" -•\t\"'") for l in raw.strip().split("\n") if l.strip()]
        lines = [l for l in lines if 3 <= len(l) <= 100]
        if len(lines) >= 3:
            return lines[:count]
    except Exception as e:
        print(f"[llm] visual query generation failed ({e}), using fallback queries")
    return fallback or []


def generate_hook_title(niche_hint, topic, script, fallback, max_tokens=200):
    """A punchy, curiosity-driven Shorts title generated from the actual
    finished script (not just the raw topic sentence title_fn's plain
    capitalize-and-truncate used to produce) — YouTube Shorts titles are a
    major driver of impressions-to-click, and a flat description-style
    title ("A maid of honor who stole the wedding date...") reads as a
    summary, not a hook. Best-effort: falls back to `fallback` (the old
    title_fn output) on any failure, so a bad LLM response never blocks
    publishing."""
    system = (
        "You write short, high-CTR YouTube Shorts titles for the given story. "
        "Under 90 characters. Create real curiosity or tension — a question, a "
        "twist tease, or a bold claim — without spoiling the ending. No emoji "
        "spam (0-1 max), no clickbait that isn't true to the story, no quotes "
        "around the title. Reply with ONLY the title text, nothing else."
    )
    user = f"Channel style: {niche_hint}\n\nStory:\n{script}\n\nWrite the title."
    try:
        title = generate_script(system, user, max_tokens=max_tokens, temperature=0.95)
        title = title.strip().strip('"').strip("'").split("\n")[0].strip()
        if 4 <= len(title) <= 100:
            return title[:100]
    except Exception as e:
        print(f"[llm] hook title generation failed ({e}), using fallback title")
    return fallback


if __name__ == "__main__":
    demo = generate_script(
        "You are a concise YouTube Shorts scriptwriter.",
        "Write a 100-word script about a random forgotten empire.",
    )
    print(demo)
