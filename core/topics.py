"""
topics.py — keeps each channel's topic supply from repeating so it can run
daily for a year without hand-written topic lists. Each run asks the LLM
for one fresh topic idea steered away from the channel's own recent
history (persisted in data/used_topics/<channel>.json); falls back to the
channel's small hardcoded topic_prompts pool (preferring never-used entries)
only if the LLM call fails.
"""

import json
import os
import random

from core.llm import generate_topic

STATE_DIR = os.path.join("data", "used_topics")


def _path(channel_name):
    return os.path.join(STATE_DIR, f"{channel_name}.json")


def load_used(channel_name):
    p = _path(channel_name)
    if os.path.exists(p):
        with open(p, encoding="utf-8") as f:
            return json.load(f)
    return []


def record_used(channel_name, topic, cap=1500):
    os.makedirs(STATE_DIR, exist_ok=True)
    used = load_used(channel_name)
    used.append(topic)
    used = used[-cap:]
    with open(_path(channel_name), "w", encoding="utf-8") as f:
        json.dump(used, f, ensure_ascii=False, indent=2)


def pick_topic(config):
    used = load_used(config["name"])
    niche_hint = config.get("niche") or config["system_prompt"][:300]
    try:
        topic = generate_topic(niche_hint, used)
        used_lower = {u.lower() for u in used}
        if topic and topic.lower() not in used_lower:
            record_used(config["name"], topic)
            return topic
        print(f"[topics] LLM repeated a used topic for {config['name']!r}, falling back to pool")
    except Exception as e:
        print(f"[topics] LLM topic generation failed for {config['name']!r} ({e}), falling back to pool")

    pool = config["topic_prompts"]
    used_lower = {u.lower() for u in used}
    unused = [t for t in pool if t.lower() not in used_lower]
    topic = random.choice(unused or pool)
    record_used(config["name"], topic)
    return topic
