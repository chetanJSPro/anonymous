"""
config.py for Betrayal & Revenge Stories (est. RPM $12.82) — edit topic_prompts / voice / query terms here.
Everything else is handled by core/pipeline.py (same shared toolkit as channels/).
"""

SYSTEM_PROMPT = "You write a viral first-person 'reddit confession' style story about betrayal and a satisfying karmic payoff (a cheating partner exposed, a backstabbing friend or coworker caught, a family member's scheme unraveling). Write 180-220 words: a clear setup, rising tension, and a satisfying twist or comeuppance ending. Sound like a real anonymous confession — plain, specific, emotionally honest — never like a lecture or moral. No real names, keep it clearly a story, not targeting any real identifiable person."

TOPIC_PROMPTS = ['a maid of honor who stole the wedding date and got exposed at the reception', 'a coworker who took credit for a project until the client called out the truth in a meeting', 'a roommate who secretly rented out the apartment on weekends until the landlord found out', "a sibling who forged a parent's signature on an inheritance document", 'a business partner who was skimming money until the accountant noticed']

STOCK_QUERIES = ['couple arguing at home', 'wedding reception celebration', 'tense office meeting',
                  'hands signing documents', 'person walking away sad']
AI_PROMPTS = [
    'cinematic moody photorealistic dramatic scene, {topic}, shallow depth of field, film still, emotional',
    'tense close-up photorealistic portrait, conflicted expression, cinematic lighting, film still',
    'cinematic wide shot, empty room aftermath of confrontation, dramatic shadows, photorealistic',
    'photorealistic cinematic scene, hands clenched in anger, dim lighting, film still',
    'cinematic photorealistic scene, quiet resolution moment, warm light breaking through, film still',
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
    "name": 'hp01_betrayal_revenge',
    "system_prompt": SYSTEM_PROMPT,
    "topic_prompts": TOPIC_PROMPTS,
    "visual_source": 'mixed',
    "visual_query_fn": visual_query_fn,
    "voice": 'en-US-GuyNeural',
    "vertical": True,
    "category_id": '24',
    "client_secret_file": "client_secret_a.json",
    "channel_token_file": "token_hp01_betrayal_revenge.json",
    "title_fn": title_fn,
    "description_fn": description_fn,
    "tags": ['reddit story', 'revenge story', 'betrayal', 'storytime'],
    "niche": "Betrayal & revenge stories",
    "est_rpm": 12.82,
}
