"""
config.py for Eastern Philosophy (Zen, Tao, Buddhism) — edit topic_prompts / voice / query terms here.
Everything else is handled by core/pipeline.py.
"""

SYSTEM_PROMPT = 'You are a calm, wise narrator explaining one Eastern philosophy concept (Zen, Taoism, Buddhism) in plain, modern language. Write a 70-90 word script: a short story or parable, then one clear practical takeaway. Calm, slow pacing. Narrate in American English for a US-based audience, using relatable everyday American scenarios in the story or parable.'

TOPIC_PROMPTS = ['the Zen parable of the full teacup', 'the Taoist idea of wu wei (effortless action)', 'the Buddhist concept of impermanence (anicca)', 'the parable of the two monks and the river', "the Tao Te Ching's teaching on softness overcoming hardness"]

STOCK_QUERIES = ['zen garden raked sand', 'monk walking temple', 'misty mountain forest',
                  'candle flame close up', 'slow river water flowing', 'bamboo forest wind']

def visual_query_fn(topic, script):
    """Real stock video search terms only — no AI stills."""
    return STOCK_QUERIES

def title_fn(topic):
    prefix = ''
    t = topic[0].upper() + topic[1:]
    return (prefix + " " + t).strip()[:100] if prefix else t[:100]

def description_fn(topic):
    base = f"{topic}\n\nFollow for a new philosophy story every day."
    return base + "\n#shorts #philosophy #zen"

CONFIG = {
    "name": 'ch06_eastern_philosophy',
    "system_prompt": SYSTEM_PROMPT,
    "topic_prompts": TOPIC_PROMPTS,
    "visual_source": 'mixed',
    "visual_query_fn": visual_query_fn,
    "voice": 'en-US-ChristopherNeural',
    "vertical": True,
    "category_id": '27',
    "client_secret_file": "client_secret_c.json",
    "channel_token_file": "token_ch06_eastern_philosophy.json",
    "title_fn": title_fn,
    "description_fn": description_fn,
    "tags": ['philosophy', 'zen', 'taoism', 'buddhism', 'mindfulness'],
}
