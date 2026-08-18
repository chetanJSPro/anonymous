"""
config.py for Egyptian Mythology Breakdowns — edit topic_prompts / voice / query terms here.
Everything else is handled by core/pipeline.py.
"""

SYSTEM_PROMPT = 'You are a narrator breaking down Egyptian mythology for a curious general audience. Write a vivid 150-180 word script about one god, myth, or afterlife concept. Accurate to well-documented mythology, end on a compelling hook.'

TOPIC_PROMPTS = ['Anubis and the weighing of the heart ceremony', 'the myth of Osiris, Isis, and Set', "Ra's nightly battle against the serpent Apep", 'the story of the Eye of Horus', 'how ancient Egyptians believed the afterlife (Duat) worked']

QUERY_TERMS = ['epic ancient egyptian mythology art, {topic}, gold and sand tones, dramatic, detailed']

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
    "name": 'ch07_egyptian_mythology',
    "system_prompt": SYSTEM_PROMPT,
    "topic_prompts": TOPIC_PROMPTS,
    "visual_source": 'ai',
    "visual_query_fn": visual_query_fn,
    "voice": 'en-GB-RyanNeural',
    "vertical": True,
    "category_id": '27',
    "channel_token_file": "token_ch07_egyptian_mythology.json",
    "title_fn": title_fn,
    "description_fn": description_fn,
    "tags": ['egyptian mythology', 'ancient egypt', 'mythology', 'gods'],
}
