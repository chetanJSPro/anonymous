"""
config.py for Norse / Viking Sagas — edit topic_prompts / voice / query terms here.
Everything else is handled by core/pipeline.py.
"""

SYSTEM_PROMPT = 'You are a dramatic narrator of Norse mythology and Viking sagas. Write a vivid 150-180 word narration script for one self-contained myth or saga moment (Odin, Thor, Loki, Ragnarok, real Viking history). End on a striking hook.'

TOPIC_PROMPTS = ["Odin sacrificing his eye at Mimir's well for wisdom", "Thor's battle with the Midgard Serpent", "Loki's binding after the death of Baldr", 'the signs that foretell Ragnarok', 'a Viking longship raid on the English coast']

QUERY_TERMS = ['epic viking norse mythology painting, {topic}, dramatic stormy lighting, detailed, cinematic']

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
    return base + "\n#shorts" if True else base

CONFIG = {
    "name": 'ch05_norse_sagas',
    "system_prompt": SYSTEM_PROMPT,
    "topic_prompts": TOPIC_PROMPTS,
    "visual_source": 'ai',
    "visual_query_fn": visual_query_fn,
    "voice": 'en-GB-RyanNeural',
    "vertical": True,
    "category_id": '27',
    "channel_token_file": "token_ch05_norse_sagas.json",
    "title_fn": title_fn,
    "description_fn": description_fn,
    "tags": ['norse mythology', 'vikings', 'mythology', 'odin', 'thor'],
}
