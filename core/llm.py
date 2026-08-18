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
import json
import time
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
                time.sleep(3 * (attempt + 1))
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
    result = _post_json(GROQ_URL, payload, headers)
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


if __name__ == "__main__":
    demo = generate_script(
        "You are a concise YouTube Shorts scriptwriter.",
        "Write a 100-word script about a random forgotten empire.",
    )
    print(demo)
