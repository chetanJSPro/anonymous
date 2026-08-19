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
    """Real stock video search terms only — no AI stills."""
    return [q.format(topic=topic) if "{topic}" in q else q for q in QUERY_TERMS]

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
}
