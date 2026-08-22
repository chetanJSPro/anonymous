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


def generate_visual_queries(niche_hint, topic, script, count=8, fallback=None,
                             avoid_named_entities=False):
    """Derive concrete, story-specific visual search/prompt terms from the
    actual generated script, instead of a static per-channel query list --
    a static list produces visuals unrelated to the specific story being
    told (generic "office meeting" b-roll under a script that never
    mentions an office), which reads as stock footage bolted on rather
    than visuals that match what's being narrated. These queries feed both
    the stock video search (Pexels/Pixabay) and the Agnes AI prompts, so
    improving them improves whichever source ends up used.

    `avoid_named_entities`: for channels whose stories are full of proper
    nouns real stock libraries have zero footage of (mythology figures like
    Krishna/Arjuna/Rama, historical figures, named places) -- set True to
    get generic-but-on-theme scene descriptions (temple architecture,
    ritual objects, weather, silhouettes/gestures) that Pexels/Pixabay can
    actually match, instead of queries that always miss and fall back to
    unrelated "popular" results. Meant for the STOCK-search query list, not
    the Agnes AI prompt list -- Agnes can attempt named-character scenes
    directly, stock search can't.

    Best-effort: falls back to `fallback` (the channel's static query list)
    on any failure or a too-short response."""
    entity_note = (
        " Do NOT name individual characters, deities, or specific fictional/"
        "historical places (e.g. not \"Krishna\", not \"Arjuna\", not "
        "\"Ayodhya\") -- stock footage libraries have zero real footage of "
        "named mythological/historical figures or places and return unrelated "
        "results for those queries. DO still use the work/genre/culture-level "
        "terms real footage libraries actually have tagged (e.g. "
        "\"mahabharata\", \"hindu epic drama\", \"indian mythology "
        "reenactment\", \"sanskrit priest chanting\", \"indian temple "
        "ritual\") -- these aren't personal names and often match real, "
        "specific, on-theme footage far better than a fully generic "
        "description like \"temple architecture\" or \"warrior silhouette\" "
        "does. Prefer the more specific, real-searchable term whenever one "
        "exists."
        if avoid_named_entities else ""
    )
    system = (
        f"You write short stock-footage SEARCH QUERIES (like something typed "
        f"into Pexels or Pixabay's search box) for video footage to accompany "
        f"a short narrated video. Channel style: {niche_hint}. Reply with "
        f"exactly {count} search queries, one per line, no numbering, no "
        f"quotes, no extra commentary. Each query must be 3-6 WORDS, under "
        f"60 characters -- a short keyword phrase (a place + an object/action, "
        f"e.g. \"stone temple courtyard\" or \"warrior silhouette sunset\"), "
        f"NEVER a full sentence, and never longer than that limit. Still tie "
        f"each phrase to specific moments or details in the story below, not "
        f"generic unrelated stock-photo phrases.{entity_note}"
    )
    user = f"Topic: {topic}\n\nStory:\n{script}\n\nGive {count} visual scene descriptions."
    # Retry twice before giving up to `fallback` -- confirmed 2026-08-20:
    # GROQ_MODEL (a reasoning model) intermittently returns a genuinely
    # EMPTY visible response here (same refusal/reasoning-budget flakiness
    # documented on generate_script's retry loop in core/pipeline.py, not
    # something a bigger max_tokens alone fixes), which used to fall
    # straight to the single static `fallback` list on the very first
    # hiccup -- defeating per-episode/per-channel query variety (and, for
    # avoid_named_entities callers, the whole point of the fix) far more
    # often than the underlying failure rate justified.
    for attempt in range(3):
        try:
            # max_tokens bumped 400 -> 700: with the longer
            # avoid_named_entities system prompt added above, this model
            # spends part of its token budget on hidden reasoning before
            # the visible answer, and 400 was too tight to leave anything
            # for the actual list on longer prompts/stories.
            raw = generate_script(system, user, max_tokens=700, temperature=0.8)
            lines = [l.strip(" -•\t\"'") for l in raw.strip().split("\n") if l.strip()]
            # Kept at <=90 (not the sentence-length 160 tried earlier)
            # deliberately: Pixabay's search API hard-rejects any `q` over
            # ~100 chars with HTTP 400 (confirmed 2026-08-20 -- every query
            # from an earlier "full sentence" version of this prompt failed
            # Pixabay outright, silently producing 0 stock clips for the
            # whole episode). The system prompt above now asks for short
            # 3-6 word phrases directly, so this is just a safety cap.
            lines = [l for l in lines if 3 <= len(l) <= 90]
            if len(lines) >= 3:
                return lines[:count]
            print(f"[llm] visual query generation attempt {attempt+1} returned too few "
                  f"usable lines ({len(lines)}) -- retrying. Raw: {raw[:200]!r}")
        except Exception as e:
            print(f"[llm] visual query generation attempt {attempt+1} failed ({e}) -- retrying")
    print("[llm] visual query generation failed all 3 attempts, using fallback queries")
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
