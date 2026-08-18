"""
config.py for Geography Quiz Shorts ('Guess the Country') — edit topic_prompts / voice / query terms here.
Everything else is handled by core/pipeline.py.
"""

SYSTEM_PROMPT = "You create a 'Guess the Country' quiz short. Write: 3 short numbered clues (each under 12 words) about one real country, ending with 'What country is this?', then on a new line write 'ANSWER: <country>'. Make clues progressively easier."

TOPIC_PROMPTS = ['a country in South America known for a famous ancient citadel', 'a Southeast Asian country made of over 17000 islands', 'a European country famous for tulips and windmills', "an African country home to the world's longest river", 'a Middle Eastern country famous for its ancient rose-red city']

QUERY_TERMS = ['minimalist world map style illustration, geography quiz background, {topic}, flat design']

def visual_query_fn(topic, script):
    """Return a list of search terms (pixabay) or AI image prompts to source
    visuals for this episode. Edit QUERY_TERMS above to change the look."""
    return [q.format(topic=topic) if "{topic}" in q else q for q in QUERY_TERMS]

def title_fn(topic):
    prefix = 'Can You Guess This Country?'
    t = topic[0].upper() + topic[1:]
    return (prefix + " " + t).strip()[:100] if prefix else t[:100]

def description_fn(topic):
    base = f"{topic}\n\nAuto-generated with a free AI content pipeline (script + voice + visuals)."
    return base + "\n#shorts" if True else base

CONFIG = {
    "name": 'ch04_geography_quiz',
    "system_prompt": SYSTEM_PROMPT,
    "topic_prompts": TOPIC_PROMPTS,
    "visual_source": 'ai',
    "visual_query_fn": visual_query_fn,
    "voice": 'en-US-JennyNeural',
    "vertical": True,
    "category_id": '27',
    "channel_token_file": "token_ch04_geography_quiz.json",
    "title_fn": title_fn,
    "description_fn": description_fn,
    "tags": ['geography quiz', 'guess the country', 'quiz', 'shorts'],
}
