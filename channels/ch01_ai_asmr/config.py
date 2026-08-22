"""
config.py for AI ASMR (soap / slime / glass cutting) — edit topic_prompts / voice / query terms here.
Everything else is handled by core/pipeline.py.
"""

SYSTEM_PROMPT = (
    "You write a calm, sensory spoken narration (70-100 words) for a satisfying ASMR video "
    "(soap cutting, slime, glass, kinetic sand). Describe the sounds, textures, and slow "
    "satisfying motion in vivid, unhurried detail — like a whispered ASMR voiceover, not a "
    "list of facts. End with a short line inviting the viewer to relax and watch. "
    "Output ONLY the spoken narration itself — no stage directions, no preamble like "
    "'Here's your script' — start directly with the description."
)

TOPIC_PROMPTS = ['glossy soap bar being sliced into cubes', 'colorful slime being stretched and folded', 'glass orb cracking in slow motion', 'kinetic sand being cut with a knife', 'honeycomb soap crumbling apart']

QUERY_TERMS = ['soap cutting asmr', 'slime asmr', 'sand cutting', 'satisfying asmr', 'kinetic sand asmr']

def visual_query_fn(topic, script):
    """Story-specific AI-video prompts derived from the actual script (so
    Agnes generates a genuinely new scene each episode instead of the same
    5 static QUERY_TERMS hitting the same top Pixabay/Pexels results every
    time), falling back to QUERY_TERMS only if generation fails."""
    from core.llm import generate_visual_queries
    fallback = [q.format(topic=topic) if "{topic}" in q else q for q in QUERY_TERMS]
    return generate_visual_queries("Sensory ASMR video (soap/slime/glass/kinetic sand cutting)",
                                    topic, script, count=8, fallback=fallback)

def title_fn(topic):
    prefix = 'Satisfying ASMR:'
    t = topic[0].upper() + topic[1:]
    return (prefix + " " + t).strip()[:100] if prefix else t[:100]

def description_fn(topic):
    base = f"{topic}\n\nFollow for a new satisfying ASMR clip every day."
    return base + "\n#shorts #asmr #satisfying"

CONFIG = {
    "name": 'ch01_ai_asmr',
    "system_prompt": SYSTEM_PROMPT,
    "topic_prompts": TOPIC_PROMPTS,
    "visual_source": 'pixabay_video',
    "visual_query_fn": visual_query_fn,
    "voice": 'en-US-AriaNeural',
    "vertical": True,
    "category_id": '24',
    "client_secret_file": "client_secret_c.json",
    "channel_token_file": "token_ch01_ai_asmr.json",
    "title_fn": title_fn,
    "description_fn": description_fn,
    "tags": ['asmr', 'satisfying', 'relaxing', 'shorts'],
    # All 8 clips attempt Agnes AI generation first, real stock (Pexels/
    # Pixabay) tops up whatever Agnes doesn't land.
    #
    # ai_only_visuals was True (2026-08-21 request: no stock at all,
    # Pollinations-generated AI stills instead), reverted 2026-08-22:
    # confirmed via two consecutive full runs that Agnes AI now fails
    # ~100% of clips (its free-tier rate limit is shared across ALL Agnes
    # users globally, not just this project -- no amount of our own
    # request pacing fixes that), AND Pollinations' free/no-signup tier
    # quietly dropped to a much lower-quality model (confirmed via its
    # /models endpoint: only "sana" is served now, model=flux/turbo
    # requests are silently ignored and served from sana anyway --
    # byte-identical output either way). With both AI paths effectively
    # dead, ai_only_visuals meant 100% of clips were low-quality
    # Pollinations stills. Real stock (now the sharpest tier per
    # core/visuals.py's fetch_pexels_videos/fetch_pixabay_videos) is the
    # better available option until Agnes/Pollinations recover.
    "agnes_clip_count": 8,
}
