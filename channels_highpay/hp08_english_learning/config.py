"""
config.py for English Learning Podcast Shorts (est. RPM $11.88) — edit topic_prompts / voice / query terms here.
Everything else is handled by core/pipeline.py (same shared toolkit as channels/).
"""

SYSTEM_PROMPT = 'You write a short spoken-English learning lesson for intermediate ESL learners. Teach ONE common phrase, idiom, or grammar point: explain it in very simple English, give 2 example sentences, and note when to use it. Write 70-90 words, warm and encouraging teacher tone, simple vocabulary. Teach American English (US spelling, pronunciation, and everyday phrasing) with example sentences set in relatable American situations. Output ONLY the spoken narration itself — no stage directions, no chatty preamble — start directly with the lesson.'

TOPIC_PROMPTS = ["the phrase 'get the hang of it' and how to use it naturally", "the difference between 'make' and 'do' in everyday English", "the idiom 'hit the books' and when native speakers use it", 'how to politely disagree in English using softening phrases', "the phrasal verb 'look forward to' and common mistakes learners make"]

STOCK_QUERIES = ['person writing notebook', 'open dictionary book', 'student studying laptop',
                  'teacher whiteboard classroom']
AI_PROMPTS = [
    'clean minimalist educational illustration, {topic}, friendly, bright colors, flat design',
    'clean minimalist flat illustration, open notebook with vocabulary words, bright friendly colors',
    'clean minimalist flat illustration, speech bubble icon, bright cheerful colors, educational',
    'clean minimalist flat illustration, world map with language icons, bright colors, friendly',
    'clean minimalist flat illustration, confident person speaking, bright cheerful colors, educational',
]

def visual_query_fn(topic, script):
    """Story-specific visual scenes pulled from the actual script (so
    footage matches what's being narrated instead of generic stock terms),
    falling back to STOCK_QUERIES on any failure."""
    from core.llm import generate_visual_queries
    return generate_visual_queries("Spoken English learning lessons for ESL learners",
                                    topic, script, count=8, fallback=STOCK_QUERIES)

def title_fn(topic):
    prefix = 'Learn English:'
    t = topic[0].upper() + topic[1:]
    return (prefix + " " + t).strip()[:100] if prefix else t[:100]

def description_fn(topic):
    base = f"{topic}\n\nFollow for a new English lesson every day."
    return base + "\n#shorts #learnenglish #esl"

CONFIG = {
    "name": 'hp08_english_learning',
    "system_prompt": SYSTEM_PROMPT,
    "topic_prompts": TOPIC_PROMPTS,
    "visual_source": 'mixed',
    "visual_query_fn": visual_query_fn,
    "voice": 'en-US-JennyNeural',
    "vertical": True,
    "category_id": '27',
    "client_secret_file": "client_secret_b.json",
    "channel_token_file": "token_hp08_english_learning.json",
    "title_fn": title_fn,
    "description_fn": description_fn,
    "tags": ['learn english', 'esl', 'english lesson', 'vocabulary'],
    "niche": "English learning podcast shorts",
    "est_rpm": 11.88,
}
