"""
config.py for Sleep & Healing Soundscapes (est. RPM $10.92) — edit topic_prompts / voice / query terms here.
Everything else is handled by core/pipeline.py (same shared toolkit as channels/).
"""

SYSTEM_PROMPT = 'Write ONE short on-screen title (max 10 words) for a long-form sleep/healing ambient soundscape video (rain, soft drones, deep sleep tones, healing frequencies framing). No spoken narration — just a calming title.'

TOPIC_PROMPTS = ['deep sleep rain sounds for relaxation and healing', 'calming ocean waves for stress relief and sleep', 'gentle forest ambience for deep relaxation', 'soft thunderstorm sounds for undisturbed sleep', 'peaceful night ambience with distant wind for sleep']

STOCK_QUERIES = ['calm night sky stars', 'soft rain window', 'ocean waves calm', 'peaceful forest night',
                  'candle flame slow motion', 'clouds timelapse peaceful']
# AI fallback if no PEXELS_API_KEY/PIXABAY_API_KEY are set yet — without these
# the "mixed" fetch has nothing else to fall back on for a no-narration channel.
AI_PROMPTS = [
    'serene photorealistic night sky full of stars, calm, dreamy, cinematic',
    'photorealistic soft rain on a window at night, cozy, calm, cinematic',
    'photorealistic calm ocean waves at dusk, peaceful, cinematic, soft light',
    'photorealistic quiet forest at night, moonlight, peaceful, cinematic',
]

def visual_query_fn(topic, script):
    """Real stock video search terms only — no AI stills."""
    return STOCK_QUERIES

def title_fn(topic):
    prefix = ''
    t = topic[0].upper() + topic[1:]
    return (prefix + " " + t).strip()[:100] if prefix else t[:100]

def description_fn(topic):
    base = f"{topic}\n\nAuto-generated with a free AI content pipeline (script + voice + visuals)."
    return base + "\n#shorts" if False else base

CONFIG = {
    "name": 'hp05_sleep_soundscapes',
    "system_prompt": SYSTEM_PROMPT,
    "topic_prompts": TOPIC_PROMPTS,
    "visual_source": 'mixed',
    "visual_query_fn": visual_query_fn,
    "voice": 'en-US-AriaNeural',
    "vertical": False,
    "category_id": '22',
    "client_secret_file": "client_secret_b.json",
    "channel_token_file": "token_hp05_sleep_soundscapes.json",
    "title_fn": title_fn,
    "description_fn": description_fn,
    "tags": ['sleep sounds', 'relaxation', 'healing music', 'ambient'],
    "niche": "Sleep & healing soundscapes",
    "est_rpm": 10.92,
}
