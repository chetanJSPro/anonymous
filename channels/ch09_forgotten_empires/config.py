"""
config.py for Forgotten Empires (Khmer, Mali, Sogdian) — edit topic_prompts / voice / query terms here.
Everything else is handled by core/pipeline.py.
"""

SYSTEM_PROMPT = "You are a documentary narrator specializing in lesser-known historical empires. Write a vivid, historically-grounded 150-180 word script about one moment or fact from a forgotten empire. End on a striking hook or 'why don't we learn about this in school' style close."

TOPIC_PROMPTS = ['the rise of the Khmer Empire and the building of Angkor Wat', 'Mansa Musa of the Mali Empire and his legendary wealth', 'the Sogdians who controlled the Silk Road for centuries', 'the sudden collapse of the Khmer Empire', 'the trans-Saharan gold and salt trade of the Mali Empire']

QUERY_TERMS = ['epic historical documentary painting, {topic}, cinematic golden light, highly detailed']

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
    "name": 'ch09_forgotten_empires',
    "system_prompt": SYSTEM_PROMPT,
    "topic_prompts": TOPIC_PROMPTS,
    "visual_source": 'ai',
    "visual_query_fn": visual_query_fn,
    "voice": 'en-US-GuyNeural',
    "vertical": True,
    "category_id": '27',
    "channel_token_file": "token_ch09_forgotten_empires.json",
    "title_fn": title_fn,
    "description_fn": description_fn,
    "tags": ['forgotten history', 'ancient empires', 'khmer empire', 'mali empire', 'history'],
}
