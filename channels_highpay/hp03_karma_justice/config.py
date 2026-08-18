"""
config.py for Karma & Justice Stories (est. RPM $5.70) — edit topic_prompts / voice / query terms here.
Everything else is handled by core/pipeline.py (same shared toolkit as channels/).
"""

SYSTEM_PROMPT = "You write a viral first-person 'petty revenge' or 'instant karma' story (a rude customer, an entitled neighbor, a bully getting an unexpected comeuppance). Write 160-200 words: relatable setup, escalating rudeness or unfairness, then a clean, satisfying karmic resolution. Keep it light enough to be shareable, not mean-spirited or targeting real people."

TOPIC_PROMPTS = ['an entitled customer who demanded a refund and got caught lying on camera', 'a neighbor who kept stealing parking spots until the HOA got involved', 'a bully in a group chat who got exposed by a screenshot they forgot existed', "a coworker who mocked someone's side hustle until it became the company's biggest client", 'a person who cut in line at the airport and the gate agent had the perfect response']

STOCK_QUERIES = ['rude customer at counter', 'neighborhood street candid', 'group of friends laughing',
                  'person smiling knowingly', 'city sidewalk crowd']
AI_PROMPTS = [
    'cinematic everyday-life dramatic scene, {topic}, warm realistic lighting, photorealistic',
    'photorealistic candid street scene, everyday people, natural lighting, cinematic',
    'cinematic close-up of a satisfied knowing smile, warm lighting, photorealistic',
    'photorealistic scene of an awkward public moment, natural light, cinematic',
    'cinematic photorealistic scene, poetic justice unfolding, golden hour, film still',
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
    return base + "\n#shorts" if True else base

CONFIG = {
    "name": 'hp03_karma_justice',
    "system_prompt": SYSTEM_PROMPT,
    "topic_prompts": TOPIC_PROMPTS,
    "visual_source": 'mixed',
    "visual_query_fn": visual_query_fn,
    "voice": 'en-US-JennyNeural',
    "vertical": True,
    "category_id": '24',
    "client_secret_file": "client_secret_a.json",
    "channel_token_file": "token_hp03_karma_justice.json",
    "title_fn": title_fn,
    "description_fn": description_fn,
    "tags": ['karma', 'instant karma', 'petty revenge', 'storytime'],
    "niche": "Karma & justice stories",
    "est_rpm": 5.70,
}
