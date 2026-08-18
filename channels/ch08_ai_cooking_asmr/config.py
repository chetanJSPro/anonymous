"""
config.py for AI Cooking / Food ASMR — edit topic_prompts / voice / query terms here.
Everything else is handled by core/pipeline.py.
"""

SYSTEM_PROMPT = 'Write ONE short caption line (max 12 words) overlaying a satisfying cooking or food ASMR clip (sizzling, chopping, pouring, melting cheese). Sensory, minimal.'

TOPIC_PROMPTS = ['cheese slowly melting and stretching over noodles', 'crispy chicken being sliced open steaming', 'chocolate being poured over a cake', 'vegetables being chopped rhythmically on a board', 'syrup being drizzled over pancakes']

QUERY_TERMS = ['food asmr cooking', 'melting cheese', 'chopping vegetables', 'pouring sauce food']

def visual_query_fn(topic, script):
    """Return a list of search terms (pixabay) or AI image prompts to source
    visuals for this episode. Edit QUERY_TERMS above to change the look."""
    return [q.format(topic=topic) if "{topic}" in q else q for q in QUERY_TERMS]

def title_fn(topic):
    prefix = 'Satisfying Food ASMR:'
    t = topic[0].upper() + topic[1:]
    return (prefix + " " + t).strip()[:100] if prefix else t[:100]

def description_fn(topic):
    base = f"{topic}\n\nAuto-generated with a free AI content pipeline (script + voice + visuals)."
    return base + "\n#shorts" if True else base

CONFIG = {
    "name": 'ch08_ai_cooking_asmr',
    "system_prompt": SYSTEM_PROMPT,
    "topic_prompts": TOPIC_PROMPTS,
    "visual_source": 'pixabay_video',
    "visual_query_fn": visual_query_fn,
    "voice": 'en-US-AriaNeural',
    "vertical": True,
    "category_id": '26',
    "channel_token_file": "token_ch08_ai_cooking_asmr.json",
    "title_fn": title_fn,
    "description_fn": description_fn,
    "tags": ['food asmr', 'cooking asmr', 'satisfying', 'shorts'],
}
