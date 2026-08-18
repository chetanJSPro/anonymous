"""
config.py for Nature Ambient Long-form (rain, fire, forest) — edit topic_prompts / voice / query terms here.
Everything else is handled by core/pipeline.py.
"""

SYSTEM_PROMPT = 'Write ONE short on-screen title (max 10 words) for a long-form ambient nature video (rain, campfire, forest, ocean). No spoken narration — just a title.'

TOPIC_PROMPTS = ['heavy rain on a cabin roof at night', 'crackling campfire in a quiet forest', 'ocean waves on a rocky shore at dusk', 'wind through a pine forest at dawn', 'thunderstorm over a misty lake']

QUERY_TERMS = ['rain forest nature', 'campfire night', 'ocean waves', 'forest ambient']

def visual_query_fn(topic, script):
    """Return a list of search terms (pixabay) or AI image prompts to source
    visuals for this episode. Edit QUERY_TERMS above to change the look."""
    return [q.format(topic=topic) if "{topic}" in q else q for q in QUERY_TERMS]

def title_fn(topic):
    prefix = ''
    t = topic[0].upper() + topic[1:]
    return (prefix + " " + t).strip()[:100] if prefix else t[:100]

def description_fn(topic):
    base = f"{topic}\n\nAuto-generated with a free AI content pipeline (script + voice + visuals)."
    return base + "\n#shorts" if False else base

CONFIG = {
    "name": 'ch02_nature_ambient',
    "system_prompt": SYSTEM_PROMPT,
    "topic_prompts": TOPIC_PROMPTS,
    "visual_source": 'pixabay_video',
    "visual_query_fn": visual_query_fn,
    "voice": 'en-US-AriaNeural',
    "vertical": False,
    "category_id": '22',
    "channel_token_file": "token_ch02_nature_ambient.json",
    "title_fn": title_fn,
    "description_fn": description_fn,
    "tags": ['ambient', 'nature sounds', 'relaxing', 'sleep', 'study'],
}
