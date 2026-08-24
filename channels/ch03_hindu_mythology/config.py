"""
config.py for Hindu Mythology (Mahabharata, Ramayana) — edit topic_prompts / voice / query terms here.
Everything else is handled by core/pipeline.py.
"""

SYSTEM_PROMPT = 'You are a respectful, historically-grounded narrator of Hindu mythology (Mahabharata, Ramayana, and Puranic stories) for a general global YouTube audience. Write a vivid 80-100 word narration script for one self-contained story or scene. Be accurate to well-known tellings, avoid embellishing sacred material irreverently. Open with the single most striking or dramatic moment of the scene as your very first sentence -- a scroll-stopping hook, never a slow scene-setting opener. End on a short, compelling reflection line, not a wrapped-up summary, so the video loops naturally back into a rewatch. Narrate in American English for a US-based audience unfamiliar with the mythology, briefly clarifying any terms they may not know. Output ONLY the spoken narration itself — no stage directions, no chatty preamble — start directly with the story.'

TOPIC_PROMPTS = ["the moment Arjuna receives the Bhagavad Gita's wisdom from Krishna before the war", "Hanuman's leap across the ocean to Lanka", 'the exile of Rama, Sita, and Lakshmana to the forest', "Draupadi's vastraharan and Krishna's protection", 'the birth and strength of Bhima', "Ravana's ten heads and his devotion to Shiva"]

STOCK_QUERIES = ['ganges river ghat india', 'temple diya lamps', 'himalaya mountains sunrise',
                  'incense smoke close up', 'indian temple bells', 'sunrise over mountains india']

def visual_query_fn(topic, script):
    """Story-specific scenes (named characters like Krishna/Arjuna/Hanuman
    allowed) fed to Agnes AI generation, which can actually attempt a
    custom scene from a text prompt -- unlike stock search below, which has
    zero real footage of named mythological figures/places."""
    from core.llm import generate_visual_queries
    return generate_visual_queries("Hindu mythology stories (Mahabharata, Ramayana)",
                                    topic, script, count=8, fallback=STOCK_QUERIES)

def stock_query_fn(topic, script):
    """Separate, generic/matchable query list used ONLY for the Pexels/
    Pixabay stock top-up. Real stock libraries have no footage of Krishna,
    Arjuna, Rama, Hanuman, etc. -- searching with those (as visual_query_fn's
    story-specific terms do) silently falls back to unrelated "popular"
    results (confirmed 2026-08-20: candle/bamboo clips under a Mahabharata
    narration). avoid_named_entities=True steers the LLM toward generic
    Indian/mythological-adjacent imagery (temple architecture, fire
    rituals, warrior silhouettes, rivers, mountains) that actually exists
    in these libraries and still reads as on-theme."""
    from core.llm import generate_visual_queries
    return generate_visual_queries("Hindu mythology stories (Mahabharata, Ramayana) -- "
                                    "generic scenery/mood b-roll only, no named characters",
                                    topic, script, count=8, fallback=STOCK_QUERIES,
                                    avoid_named_entities=True)

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
    "stock_query_fn": stock_query_fn,
    # Bumped from the 6-of-8 default: stock (Pexels/Pixabay) genuinely has
    # no Mahabharata/Ramayana footage, so Agnes gets first shot at every
    # clip and stock_query_fn's generic-but-on-theme queries fill in
    # whatever Agnes doesn't land.
    #
    # ai_only_visuals was True (2026-08-21 request: "only AI not stock"),
    # routing whatever Agnes missed to Pollinations-generated AI stills
    # instead of stock. Reverted 2026-08-22: confirmed via two consecutive
    # full runs that Agnes AI now fails ~100% of clips (its free-tier rate
    # limit is shared across ALL Agnes users globally, not just this
    # project -- no amount of our own request pacing fixes that), AND
    # Pollinations' free/no-signup tier quietly dropped to a much lower-
    # quality model (confirmed via its /models endpoint: only "sana" is
    # served now, model=flux/turbo requests are silently ignored and
    # served from sana anyway -- byte-identical output either way). With
    # both AI paths effectively dead, ai_only_visuals meant 100% of clips
    # were low-quality Pollinations stills. Real stock (now the sharpest
    # tier per core/visuals.py's fetch_pexels_videos/fetch_pixabay_videos)
    # is the better available option until Agnes/Pollinations recover.
    "agnes_clip_count": 8,
    "voice": 'en-US-ChristopherNeural',
    "vertical": True,
    "category_id": '27',
    "client_secret_file": "client_secret_c.json",
    "channel_token_file": "token_ch03_hindu_mythology.json",
    "title_fn": title_fn,
    "description_fn": description_fn,
    "tags": ['hindu mythology', 'mahabharata', 'ramayana', 'mythology'],
}
