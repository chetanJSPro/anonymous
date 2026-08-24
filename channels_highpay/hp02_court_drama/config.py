"""
config.py for Court Drama Stories (est. RPM $9.03) — edit topic_prompts / voice / query terms here.
Everything else is handled by core/pipeline.py (same shared toolkit as channels/).
"""

SYSTEM_PROMPT = "You write a viral first-person 'courtroom story' script — a small claims dispute, a wild legal case, or a judge calling out an obviously dishonest party. Write 90-110 words with a clear conflict, a tense back-and-forth, and a decisive, satisfying ruling. Set it in a US courtroom (small claims court, American legal terms, dollar amounts). Plausible and specific, never a real identifiable case or person — write it as a fictionalized dramatization. Open with the single most shocking or tense detail as your very first sentence -- a scroll-stopping hook, never a slow scene-setting opener. End on a short, punchy final line, not a wrapped-up summary, so the video loops naturally back into a rewatch. Output ONLY the spoken narration itself — no stage directions like (gavel bangs), no preamble like 'Here's your script', no generic greeting like 'Hey friends' or 'Welcome back' — start directly with the story's first line, using specific concrete details instead of vague generic phrasing."

TOPIC_PROMPTS = ["a small claims case over a neighbor's fence built two feet into the wrong yard", 'a landlord suing a tenant who then produced text messages proving retaliation', 'a dispute over a wedding photographer who never delivered the photos', 'a case where a dog walker was sued after a dog went missing, then video evidence changed everything', 'a contractor sued for a bad renovation who had secretly recorded every conversation']

STOCK_QUERIES = ['courtroom interior', 'judge gavel closeup', 'lawyer with documents',
                  'witness testifying', 'people shaking hands after agreement']
AI_PROMPTS = [
    'cinematic courtroom drama scene, {topic}, dramatic lighting, photorealistic, tense atmosphere',
    "photorealistic close-up of a judge's gavel, dramatic courtroom lighting, cinematic",
    'cinematic wide shot of an empty courtroom, dramatic light through windows, photorealistic',
    'photorealistic tense witness stand scene, cinematic lighting, film still',
    'cinematic photorealistic scene, relief and justice served, warm light, film still',
]

def visual_query_fn(topic, script):
    """Story-specific visual scenes pulled from the actual script (so
    footage matches what's being narrated instead of generic stock terms),
    falling back to STOCK_QUERIES on any failure."""
    from core.llm import generate_visual_queries
    return generate_visual_queries("Courtroom drama stories",
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
    base = f"{topic}\n\nFollow for a new courtroom story every day."
    return base + "\n#shorts #storytime #courtroomdrama"

CONFIG = {
    "name": 'hp02_court_drama',
    "system_prompt": SYSTEM_PROMPT,
    "topic_prompts": TOPIC_PROMPTS,
    "visual_source": 'mixed',
    "visual_query_fn": visual_query_fn,
    "stock_query_fn": stock_query_fn,
    "voice": 'en-US-ChristopherNeural',
    "vertical": True,
    "category_id": '24',
    "client_secret_file": "client_secret_a.json",
    "channel_token_file": "token_hp02_court_drama.json",
    "title_fn": title_fn,
    "description_fn": description_fn,
    "tags": ['court drama', 'courtroom story', 'legal drama', 'storytime'],
    "niche": "Court drama stories",
    "est_rpm": 9.03,
}
