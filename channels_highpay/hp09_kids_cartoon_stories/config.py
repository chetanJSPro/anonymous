"""
config.py for Kids Cartoon Stories (original funny-animal slapstick shorts for
children, licensed cartoon/animation stock only — Pixabay/Pexels, no ripped
studio IP). Edit topic_prompts / voice / query terms here. Everything else is
handled by core/pipeline.py.

made_for_kids=True below is not cosmetic: this channel is clearly directed at
children, so YouTube's COPPA rules require the self-declared "made for kids"
flag be True (disables personalized ads + most comments/notifications on the
video) -- see core/upload.py's selfDeclaredMadeForKids wiring. Getting that
wrong is a real policy/legal risk, not just a metadata detail.
"""

SYSTEM_PROMPT = (
    "You write a short, cheerful children's cartoon story (90-110 words) starring a clumsy, "
    "lovable animal character who gets into silly slapstick trouble (chasing something, a "
    "prank gone wrong, a wobbly tower of objects) and always ends up okay, with a gentle "
    "laugh and a small kind lesson (sharing, patience, saying sorry, trying again). Keep the "
    "tone playful, simple, and G-rated -- no violence beyond harmless cartoon pratfalls (no "
    "weapons, no real danger, nobody gets hurt), no scary content, no product or brand names, "
    "no mention of real people. Use simple words a young child narrating a picture book would "
    "understand. Output ONLY the spoken narration itself -- no stage directions like (laughs), "
    "no preamble like 'Here's your story', start directly with the first line."
)

TOPIC_PROMPTS = [
    'a clumsy puppy who chases his own tail into a pile of leaves',
    'a mischievous kitten who knocks over a tower of blocks and helps rebuild it',
    'a silly duckling who slips on a puddle during a race with his friends',
    'a greedy little raccoon who grabs too many berries and drops them all',
    'a sleepy bear cub who tries to sneak an extra snack and gets caught',
    'two squirrel friends who argue over one acorn and learn to share it',
    'a clumsy piglet who paints the whole barn instead of just the fence',
    'a curious bunny who gets stuck in a rabbit hole chasing a butterfly',
]

# Real, literal genre search terms for Pixabay/Pexels' licensed cartoon and
# animation stock libraries -- kept plain/literal (not moody "cinematic"
# phrasing) since that's what these libraries actually index well, same
# lesson as ch01_ai_asmr's STOCK_QUERIES.
STOCK_QUERIES = [
    'cartoon animation kids', 'funny cartoon animal', '2d cartoon animation',
    'colorful cartoon background', 'cute animated character', 'kids cartoon animation',
    'animated forest cartoon', 'cartoon animals playing',
]


# Flat, vibrant children's book / 2D cartoon illustration style -- applied
# to every Pollinations AI-image prompt (see ai_style_suffix in CONFIG
# below). Replaces the old approach of cutting together unrelated real
# stock "cartoon animation" clips: those never actually matched the story
# being narrated (a generic "kids cartoon animation" search can't return a
# clumsy puppy chasing its tail specifically) and, since they're real
# third-party footage from a shared library, carried the same content-risk
# class as the 2026-08-24 incident (a mismatched, inappropriate real clip
# landing under a loosely-related search term). A self-contained
# AI-generated image per story beat is both more visually on-topic and
# fully first-party, so nothing unvetted from an external library ever
# appears in a kids video again.
AI_STYLE_SUFFIX = ("flat 2D cartoon illustration, vibrant colors, cute simple character design, "
                    "children's picture book art style, clean bold outlines, no text, no watermark, "
                    "vertical portrait composition")


def visual_query_fn(topic, script):
    """Story-specific AI-image prompts derived from the actual script (so
    each generated image matches this episode's specific scene -- the
    clumsy puppy, the wobbly block tower, etc. -- instead of the same 8
    generic STOCK_QUERIES terms repeating every episode), falling back to
    STOCK_QUERIES only if generation fails. Mirrors hp01's
    visual_query_fn pattern."""
    from core.llm import generate_visual_queries
    return generate_visual_queries("Cheerful children's cartoon animal story, flat 2D illustration style",
                                    topic, script, count=8, fallback=STOCK_QUERIES)


def stock_query_fn(topic, script):
    """Real stock (Pexels/Pixabay) search terms -- see hp01's stock_query_fn
    docstring for the general reasoning. These are licensed cartoon/animation
    stock clips, never actual studio show footage."""
    return STOCK_QUERIES


def title_fn(topic):
    t = topic[0].upper() + topic[1:]
    return t[:100]


def description_fn(topic):
    base = f"{topic}\n\nA new silly animal story every day!"
    return base + "\n#shorts #kids #cartoon #kidsstories"


CONFIG = {
    "name": 'hp09_kids_cartoon_stories',
    "system_prompt": SYSTEM_PROMPT,
    "topic_prompts": TOPIC_PROMPTS,
    "visual_source": 'mixed',
    "visual_query_fn": visual_query_fn,
    "stock_query_fn": stock_query_fn,
    "voice": 'en-US-JennyNeural',
    "vertical": True,
    "category_id": '1',  # Film & Animation
    "client_secret_file": "client_secret_d.json",
    "channel_token_file": "token_hp09_kids_cartoon_stories.json",
    "title_fn": title_fn,
    "description_fn": description_fn,
    "tags": ['kids cartoon', 'funny animals', 'cartoon shorts', 'kids stories', 'animation'],
    "niche": "Kids cartoon animal stories",
    "est_rpm": 2.5,  # kids/COPPA-flagged content loses personalized-ad revenue, so RPM runs low
    # No Agnes AI (photorealistic, wrong look for a cartoon channel).
    "agnes_clip_count": 0,
    "made_for_kids": True,
    # Fully AI-generated flat-cartoon-style visuals (Pollinations stills ->
    # Ken-Burns clips) instead of real stock cartoon b-roll -- see
    # visual_query_fn's docstring above for why. ai_style_suffix keeps
    # fetch_hybrid_stock_agnes_videos' AI-image prompts in this channel's
    # cartoon style instead of its old hardcoded "photorealistic" default.
    # kids_safe (from made_for_kids above) still governs the rare stock
    # top-up if Pollinations itself is ever unreachable.
    "ai_only_visuals": True,
    "ai_style_suffix": AI_STYLE_SUFFIX,
}
