"""
config.py for Karma & Justice Stories (est. RPM $5.70) — edit topic_prompts / voice / query terms here.
Everything else is handled by core/pipeline.py (same shared toolkit as channels/).
"""

SYSTEM_PROMPT = "You write a viral first-person 'petty revenge' or 'instant karma' story (a rude customer, an entitled neighbor, a bully getting an unexpected comeuppance). Write 85-105 words: relatable setup, escalating rudeness or unfairness, then a clean, satisfying karmic resolution. Set it in the US (American neighborhoods, stores, dollar amounts, casual American phrasing). Keep it light enough to be shareable, not mean-spirited or targeting real people. Open with the single most shocking or satisfying detail as your very first sentence -- a scroll-stopping hook, never a slow scene-setting opener. End on a short, punchy final line, not a wrapped-up summary, so the video loops naturally back into a rewatch. Output ONLY the spoken narration itself — no stage directions like (laughs), no preamble like 'Here's your script', no generic greeting like 'Hey friends' or 'Welcome back' — start directly with the story's first line, using specific concrete details instead of vague generic phrasing."

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
    """Story-specific visual scenes pulled from the actual script (so
    footage matches what's being narrated instead of generic stock terms),
    falling back to STOCK_QUERIES on any failure."""
    from core.llm import generate_visual_queries
    return generate_visual_queries("Petty revenge / instant karma stories",
                                    topic, script, count=8, fallback=STOCK_QUERIES)

def stock_query_fn(topic, script):
    """Real stock (Pexels/Pixabay) search terms -- see hp01's stock_query_fn
    docstring: this was silently reusing the LLM's Agnes-prompt-style
    output above, STOCK_QUERIES is a plain literal-keyword list already
    written for this exact purpose but never actually wired in."""
    return STOCK_QUERIES

def title_fn(topic):
    prefix = ''
    t = topic[0].upper() + topic[1:]
    return (prefix + " " + t).strip()[:100] if prefix else t[:100]

def description_fn(topic):
    base = f"{topic}\n\nFollow for a new instant karma story every day."
    return base + "\n#shorts #storytime #instantkarma"

CONFIG = {
    "name": 'hp03_karma_justice',
    "system_prompt": SYSTEM_PROMPT,
    "topic_prompts": TOPIC_PROMPTS,
    "visual_source": 'mixed',
    "visual_query_fn": visual_query_fn,
    "stock_query_fn": stock_query_fn,
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
