"""
config.py for Literary Analysis & Book Reviews (est. RPM $9.15) — edit topic_prompts / voice / query terms here.
Everything else is handled by core/pipeline.py (same shared toolkit as channels/).
"""

SYSTEM_PROMPT = "You are a thoughtful literary narrator breaking down one book, author, or literary theme for a curious general audience (classic novels, famous authors' lives, the meaning behind a well-known book). Write an 80-100 word script: a hook, the core insight, and a closing thought that makes people want to read the book. Write for a US audience — American English spelling/phrasing, and relatable American cultural framing where useful. Open with the single most surprising or provocative claim about the book/author as your very first sentence -- a scroll-stopping hook, never a slow scene-setting opener. End on a short, punchy final line, not a wrapped-up summary, so the video loops naturally back into a rewatch. Output ONLY the spoken narration itself — no stage directions, no preamble like 'Here's your script', no generic greeting like 'Hey friends' or 'Welcome back' — start directly with the hook line."

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
    """Story-specific visual scenes pulled from the actual script (so
    footage matches what's being narrated instead of generic stock terms),
    falling back to STOCK_QUERIES on any failure."""
    from core.llm import generate_visual_queries
    return generate_visual_queries("Literary analysis & book reviews",
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
    base = f"{topic}\n\nFollow for a new book breakdown every day."
    return base + "\n#shorts #booktok #books"

CONFIG = {
    "name": 'hp06_literary_analysis',
    "system_prompt": SYSTEM_PROMPT,
    "topic_prompts": TOPIC_PROMPTS,
    "visual_source": 'mixed',
    "visual_query_fn": visual_query_fn,
    "stock_query_fn": stock_query_fn,
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


# Niche switched 2026-10-30 (the agreed plan); these override the values above.
CONFIG.update({'niche': 'AI and technology explained simply', 'system_prompt': 'You explain one surprising thing about AI or everyday technology so a curious beginner gets it instantly, using one vivid analogy. 85-105 words, energetic tone. Only state facts you are confident are true and well documented; never invent names, numbers or quotes. Open with the single most striking detail as your very first sentence, never slow scene-setting. Use specific concrete details. End on a short punchy final line, not a summary. Output ONLY the spoken narration: no stage directions, no preamble, no greeting.', 'topic_prompts': ['why AI chatbots confidently make things up', 'how your phone recognizes your face in the dark', 'how noise cancelling headphones erase sound', 'how a chip fits billions of switches', 'how AI image generators start from pure noise'], 'tags': ['ai explained', 'technology', 'how it works', 'shorts'], 'category_id': '27', 'music_mood': 'light', 'art_style': 'sleek futuristic cinematic still, clean neon and glass, shallow depth of field'})
CONFIG["title_fn"] = lambda topic: (topic[0].upper() + topic[1:])[:100]
CONFIG["description_fn"] = lambda topic: f"{topic}\n\n" + 'Follow for a new tech explainer every day.\n#shorts #ai #technology'
CONFIG["use_winners"] = False
