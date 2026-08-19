"""
config.py for Hindu Mythology (Mahabharata, Ramayana) — edit topic_prompts / voice / query terms here.
Everything else is handled by core/pipeline.py.
"""

SYSTEM_PROMPT = 'You are a respectful, historically-grounded narrator of Hindu mythology (Mahabharata, Ramayana, and Puranic stories) for a general global YouTube audience. Write a vivid 80-100 word narration script for one self-contained story or scene. Be accurate to well-known tellings, avoid embellishing sacred material irreverently, and end on a compelling hook or reflection. Narrate in American English for a US-based audience unfamiliar with the mythology, briefly clarifying any terms they may not know.'

TOPIC_PROMPTS = ["the moment Arjuna receives the Bhagavad Gita's wisdom from Krishna before the war", "Hanuman's leap across the ocean to Lanka", 'the exile of Rama, Sita, and Lakshmana to the forest', "Draupadi's vastraharan and Krishna's protection", 'the birth and strength of Bhima', "Ravana's ten heads and his devotion to Shiva"]

STOCK_QUERIES = ['ganges river ghat india', 'temple diya lamps', 'himalaya mountains sunrise',
                  'incense smoke close up', 'indian temple bells', 'sunrise over mountains india']

def visual_query_fn(topic, script):
    """Real stock video search terms only — no AI stills."""
    return STOCK_QUERIES

def title_fn(topic):
    prefix = ''
    t = topic[0].upper() + topic[1:]
    return (prefix + " " + t).strip()[:100] if prefix else t[:100]

def description_fn(topic):
    base = f"{topic}\n\nFollow for a new mythology story every day."
    return base + "\n#shorts #mythology #hinduism"

CONFIG = {
    "name": 'ch03_hindu_mythology',
    "system_prompt": SYSTEM_PROMPT,
    "topic_prompts": TOPIC_PROMPTS,
    "visual_source": 'mixed',
    "visual_query_fn": visual_query_fn,
    "voice": 'en-US-ChristopherNeural',
    "vertical": True,
    "category_id": '27',
    "client_secret_file": "client_secret_c.json",
    "channel_token_file": "token_ch03_hindu_mythology.json",
    "title_fn": title_fn,
    "description_fn": description_fn,
    "tags": ['hindu mythology', 'mahabharata', 'ramayana', 'mythology'],
}
