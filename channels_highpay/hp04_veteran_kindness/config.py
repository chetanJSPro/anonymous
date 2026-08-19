"""
config.py for Veteran Kindness Stories (est. RPM $7.13) — edit topic_prompts / voice / query terms here.
Everything else is handled by core/pipeline.py (same shared toolkit as channels/).
"""

SYSTEM_PROMPT = 'You write a heartfelt, uplifting true-feeling story about a veteran being shown unexpected kindness, respect, or recognition by a stranger (a free meal, an upgraded flight, a small business honoring them). Write 85-105 words, warm and sincere tone, ending on an emotional, feel-good note. Set it in the US (American towns, diners, airports, dollar amounts). Respectful and dignified — never pitying.'

TOPIC_PROMPTS = ["a diner owner who quietly comps every veteran's meal on their anniversary", 'a stranger at an airport who gave up a first class seat to a veteran flying home', "a young cashier who noticed a veteran's hat and paid for their groceries", 'a small town that surprises a returning veteran with a welcome home parade', "a mechanic who fixed a veteran's truck for free after hearing their story"]

STOCK_QUERIES = ['veteran portrait respectful', 'diner restaurant interior', 'airport terminal travelers',
                  'small town main street', 'handshake gratitude']
AI_PROMPTS = [
    'warm cinematic heartfelt photorealistic scene, {topic}, golden hour lighting, emotional, respectful',
    'photorealistic portrait of a veteran, dignified expression, warm cinematic light',
    'cinematic wide shot, small town main street, golden hour, photorealistic, respectful',
    'photorealistic close-up of a handshake, warm emotional lighting, cinematic',
    'cinematic photorealistic scene, community gathering in gratitude, warm light, film still',
]

def visual_query_fn(topic, script):
    """Real stock video search terms only — no AI stills."""
    return STOCK_QUERIES

def title_fn(topic):
    prefix = ''
    t = topic[0].upper() + topic[1:]
    return (prefix + " " + t).strip()[:100] if prefix else t[:100]

def description_fn(topic):
    base = f"{topic}\n\nFollow for a new feel-good story every day."
    return base + "\n#shorts #veteran #feelgood"

CONFIG = {
    "name": 'hp04_veteran_kindness',
    "system_prompt": SYSTEM_PROMPT,
    "topic_prompts": TOPIC_PROMPTS,
    "visual_source": 'mixed',
    "visual_query_fn": visual_query_fn,
    "voice": 'en-US-ChristopherNeural',
    "vertical": True,
    "category_id": '22',
    "client_secret_file": "client_secret_a.json",
    "channel_token_file": "token_hp04_veteran_kindness.json",
    "title_fn": title_fn,
    "description_fn": description_fn,
    "tags": ['veteran story', 'kindness', 'feel good story', 'storytime'],
    "niche": "Veteran kindness stories",
    "est_rpm": 7.13,
}
