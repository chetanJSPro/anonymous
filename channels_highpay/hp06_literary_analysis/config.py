"""
config.py for Literary Analysis & Book Reviews (est. RPM $9.15) — edit topic_prompts / voice / query terms here.
Everything else is handled by core/pipeline.py (same shared toolkit as channels/).
"""

SYSTEM_PROMPT = "You are a thoughtful literary narrator breaking down one book, author, or literary theme for a curious general audience (classic novels, famous authors' lives, the meaning behind a well-known book). Write a 160-190 word script: a hook, the core insight, and a closing thought that makes people want to read the book."

TOPIC_PROMPTS = ["the real meaning behind George Orwell's 1984", "why The Great Gatsby's ending still divides readers", "the dark true story that inspired Mary Shelley's Frankenstein", 'what Pride and Prejudice actually says about class and marriage', "why Kafka's The Metamorphosis is still so unsettling today"]

STOCK_QUERIES = ['open book closeup', 'cozy library interior', 'stack of books', 'person reading by window',
                  'turning pages of a book']
AI_PROMPTS = [
    'moody library aesthetic photorealistic scene, {topic}, warm lighting, books, cinematic',
    'photorealistic close-up of an open book, warm library light, cinematic, dust motes',
    'cinematic wide shot, cozy reading nook, warm lamplight, photorealistic',
    'photorealistic scene of stacked antique books, moody warm lighting, cinematic',
    'cinematic photorealistic scene, hand turning a page, warm light, film still',
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
    "name": 'hp06_literary_analysis',
    "system_prompt": SYSTEM_PROMPT,
    "topic_prompts": TOPIC_PROMPTS,
    "visual_source": 'mixed',
    "visual_query_fn": visual_query_fn,
    "voice": 'en-US-ChristopherNeural',
    "vertical": True,
    "category_id": '27',
    "client_secret_file": "client_secret_b.json",
    "channel_token_file": "token_hp06_literary_analysis.json",
    "title_fn": title_fn,
    "description_fn": description_fn,
    "tags": ['book review', 'literary analysis', 'books', 'classic literature'],
    "niche": "Literary analysis & book reviews",
    "est_rpm": 9.15,
}
