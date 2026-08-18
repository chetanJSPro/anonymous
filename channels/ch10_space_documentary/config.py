"""
config.py for Space Documentary Long-form — edit topic_prompts / voice / query terms here.
Everything else is handled by core/pipeline.py.
"""

SYSTEM_PROMPT = 'You are a calm, awe-inspiring space documentary narrator (Carl Sagan-esque). Write a 300-350 word long-form narration script exploring one space topic with scientific accuracy and wonder, structured with a hook, 2-3 explained facts, and a reflective closing line about our place in the universe.'

TOPIC_PROMPTS = ['what would happen if you fell into a black hole', 'how large the observable universe really is', "the search for life on Europa, Jupiter's icy moon", "how neutron stars form and why they're so extreme", 'what the James Webb Space Telescope has revealed about early galaxies']

QUERY_TERMS = ['epic space nebula documentary visual, {topic}, cinematic, ultra detailed, cosmic']

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
    "name": 'ch10_space_documentary',
    "system_prompt": SYSTEM_PROMPT,
    "topic_prompts": TOPIC_PROMPTS,
    "visual_source": 'ai',
    "visual_query_fn": visual_query_fn,
    "voice": 'en-US-ChristopherNeural',
    "vertical": False,
    "category_id": '27',
    "channel_token_file": "token_ch10_space_documentary.json",
    "title_fn": title_fn,
    "description_fn": description_fn,
    "tags": ['space', 'astronomy', 'documentary', 'universe', 'science'],
}
