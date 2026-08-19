"""
config.py for Senior Health & Longevity Habits (est. RPM $6.17) — edit topic_prompts / voice / query terms here.
Everything else is handled by core/pipeline.py (same shared toolkit as channels/).
"""

SYSTEM_PROMPT = 'You write general wellness and longevity lifestyle content for an older adult audience — everyday habits linked to healthy aging (walking, sleep routines, social connection, balanced meals, staying mentally active). Write an 80-100 word script sharing ONE practical, non-medical lifestyle habit and why it helps healthy aging. Do not give medical advice, do not mention specific conditions, medications, or diagnoses — keep it general wellness and lifestyle only, and suggest viewers consult a doctor for personal advice. Write for a US audience — American English, US customary units (miles, pounds, Fahrenheit), and relatable American daily-life framing.'

TOPIC_PROMPTS = ['why a short daily walk after meals supports healthy aging', 'the longevity benefits of staying socially connected in later life', 'how a consistent sleep routine supports healthy aging', 'why staying mentally active with new hobbies matters for older adults', 'the value of stretching and light mobility work for older adults']

STOCK_QUERIES = ['senior couple walking outdoors', 'elderly person exercising', 'healthy meal preparation',
                  'senior friends socializing', 'peaceful morning nature walk']
AI_PROMPTS = [
    'warm photorealistic lifestyle scene, {topic}, natural light, dignified, real-life feeling',
    'photorealistic portrait of an active senior smiling, natural warm light, cinematic',
    'cinematic wide shot, peaceful morning walk outdoors, soft natural light, photorealistic',
    'photorealistic scene of a healthy home-cooked meal, warm natural light, cinematic',
    'cinematic photorealistic scene, quiet contentment at sunset, warm light, film still',
]

def visual_query_fn(topic, script):
    """Real stock video search terms only — no AI stills."""
    return STOCK_QUERIES

def title_fn(topic):
    prefix = ''
    t = topic[0].upper() + topic[1:]
    return (prefix + " " + t).strip()[:100] if prefix else t[:100]

def description_fn(topic):
    base = f"{topic}\n\nFollow for a new healthy-aging tip every day."
    return base + "\n#shorts #healthyaging #wellness"

CONFIG = {
    "name": 'hp07_senior_longevity',
    "system_prompt": SYSTEM_PROMPT,
    "topic_prompts": TOPIC_PROMPTS,
    "visual_source": 'mixed',
    "visual_query_fn": visual_query_fn,
    "voice": 'en-US-AriaNeural',
    "vertical": True,
    "category_id": '26',
    "client_secret_file": "client_secret_b.json",
    "channel_token_file": "token_hp07_senior_longevity.json",
    "title_fn": title_fn,
    "description_fn": description_fn,
    "tags": ['healthy aging', 'longevity', 'senior wellness', 'lifestyle tips'],
    "niche": "Senior health & longevity",
    "est_rpm": 6.17,
}
