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


def visual_query_fn(topic, script):
    """This channel never uses Agnes AI (agnes_clip_count=0 below) --
    Agnes generates photorealistic video, which doesn't match a cartoon
    look. Reusing the literal STOCK_QUERIES here too instead of an LLM call
    keeps this a plain no-op passthrough."""
    return STOCK_QUERIES


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
    # No Agnes AI (photorealistic, wrong look for a cartoon channel) -- pure
    # licensed stock cartoon/animation clips from Pixabay/Pexels instead.
    "agnes_clip_count": 0,
    "made_for_kids": True,
}
