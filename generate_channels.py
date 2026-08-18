"""
generate_channels.py — one-time generator script that writes out
channels/<name>/config.py and channels/<name>/run.py for all 10 channels.

Run once: `python3 generate_channels.py`
(Already run for you — this file is kept so you can regenerate/tweak
all 10 at once if you edit CHANNELS below instead of hand-editing each folder.)
"""

import os

RUN_PY_TEMPLATE = '''"""
run.py for {name} — auto-generated. Run with:
    python3 -m channels.{name}.run                 # generate only (no upload)
    python3 -m channels.{name}.run --upload         # generate + upload to YouTube
    python3 -m channels.{name}.run --topic "..."    # force a specific topic
"""
import argparse
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from core.pipeline import run_episode
from channels.{name}.config import CONFIG

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--upload", action="store_true")
    parser.add_argument("--topic", default=None)
    parser.add_argument("--privacy", default="public", choices=["public", "unlisted", "private"])
    args = parser.parse_args()

    result = run_episode(CONFIG, topic=args.topic, upload=args.upload, privacy_status=args.privacy)
    print(result)
'''

CHANNELS = [
    dict(
        name="ch01_ai_asmr",
        display="AI ASMR (soap / slime / glass cutting)",
        system_prompt=(
            "You write a single short spoken caption line (max 12 words) that could "
            "overlay a satisfying ASMR video (soap cutting, slime, glass, kinetic sand). "
            "No narration needed beyond this one caption. Keep it minimal and sensory."
        ),
        topic_prompts=[
            "glossy soap bar being sliced into cubes",
            "colorful slime being stretched and folded",
            "glass orb cracking in slow motion",
            "kinetic sand being cut with a knife",
            "honeycomb soap crumbling apart",
        ],
        visual_source="pixabay_video",
        query_terms=["soap cutting asmr", "slime asmr", "sand cutting", "satisfying asmr"],
        voice="en-US-AriaNeural",
        vertical=True,
        category_id="24",
        tags=["asmr", "satisfying", "relaxing", "shorts"],
        title_prefix="Satisfying ASMR:",
    ),
    dict(
        name="ch02_nature_ambient",
        display="Nature Ambient Long-form (rain, fire, forest)",
        system_prompt=(
            "Write ONE short on-screen title (max 10 words) for a long-form ambient "
            "nature video (rain, campfire, forest, ocean). No spoken narration — just a title."
        ),
        topic_prompts=[
            "heavy rain on a cabin roof at night",
            "crackling campfire in a quiet forest",
            "ocean waves on a rocky shore at dusk",
            "wind through a pine forest at dawn",
            "thunderstorm over a misty lake",
        ],
        visual_source="pixabay_video",
        query_terms=["rain forest nature", "campfire night", "ocean waves", "forest ambient"],
        voice="en-US-AriaNeural",
        vertical=False,
        category_id="22",
        tags=["ambient", "nature sounds", "relaxing", "sleep", "study"],
        title_prefix="",
    ),
    dict(
        name="ch03_hindu_mythology",
        display="Hindu Mythology (Mahabharata, Ramayana)",
        system_prompt=(
            "You are a respectful, historically-grounded narrator of Hindu mythology "
            "(Mahabharata, Ramayana, and Puranic stories) for a general global YouTube "
            "audience. Write a vivid 150-180 word narration script for one self-contained "
            "story or scene. Be accurate to well-known tellings, avoid embellishing sacred "
            "material irreverently, and end on a compelling hook or reflection."
        ),
        topic_prompts=[
            "the moment Arjuna receives the Bhagavad Gita's wisdom from Krishna before the war",
            "Hanuman's leap across the ocean to Lanka",
            "the exile of Rama, Sita, and Lakshmana to the forest",
            "Draupadi's vastraharan and Krishna's protection",
            "the birth and strength of Bhima",
            "Ravana's ten heads and his devotion to Shiva",
        ],
        visual_source="ai",
        query_terms=["epic Indian mythological painting style, {topic}, dramatic lighting, detailed, cinematic"],
        voice="en-US-ChristopherNeural",
        vertical=True,
        category_id="27",
        tags=["hindu mythology", "mahabharata", "ramayana", "mythology"],
        title_prefix="",
    ),
    dict(
        name="ch04_geography_quiz",
        display="Geography Quiz Shorts ('Guess the Country')",
        system_prompt=(
            "You create a 'Guess the Country' quiz short. Write: 3 short numbered clues "
            "(each under 12 words) about one real country, ending with 'What country is this?', "
            "then on a new line write 'ANSWER: <country>'. Make clues progressively easier."
        ),
        topic_prompts=[
            "a country in South America known for a famous ancient citadel",
            "a Southeast Asian country made of over 17000 islands",
            "a European country famous for tulips and windmills",
            "an African country home to the world's longest river",
            "a Middle Eastern country famous for its ancient rose-red city",
        ],
        visual_source="ai",
        query_terms=["minimalist world map style illustration, geography quiz background, {topic}, flat design"],
        voice="en-US-JennyNeural",
        vertical=True,
        category_id="27",
        tags=["geography quiz", "guess the country", "quiz", "shorts"],
        title_prefix="Can You Guess This Country?",
    ),
    dict(
        name="ch05_norse_sagas",
        display="Norse / Viking Sagas",
        system_prompt=(
            "You are a dramatic narrator of Norse mythology and Viking sagas. Write a "
            "vivid 150-180 word narration script for one self-contained myth or saga moment "
            "(Odin, Thor, Loki, Ragnarok, real Viking history). End on a striking hook."
        ),
        topic_prompts=[
            "Odin sacrificing his eye at Mimir's well for wisdom",
            "Thor's battle with the Midgard Serpent",
            "Loki's binding after the death of Baldr",
            "the signs that foretell Ragnarok",
            "a Viking longship raid on the English coast",
        ],
        visual_source="ai",
        query_terms=["epic viking norse mythology painting, {topic}, dramatic stormy lighting, detailed, cinematic"],
        voice="en-GB-RyanNeural",
        vertical=True,
        category_id="27",
        tags=["norse mythology", "vikings", "mythology", "odin", "thor"],
        title_prefix="",
    ),
    dict(
        name="ch06_eastern_philosophy",
        display="Eastern Philosophy (Zen, Tao, Buddhism)",
        system_prompt=(
            "You are a calm, wise narrator explaining one Eastern philosophy concept "
            "(Zen, Taoism, Buddhism) in plain, modern language. Write a 130-160 word script: "
            "a short story or parable, then one clear practical takeaway. Calm, slow pacing."
        ),
        topic_prompts=[
            "the Zen parable of the full teacup",
            "the Taoist idea of wu wei (effortless action)",
            "the Buddhist concept of impermanence (anicca)",
            "the parable of the two monks and the river",
            "the Tao Te Ching's teaching on softness overcoming hardness",
        ],
        visual_source="ai",
        query_terms=["serene minimalist zen painting, {topic}, soft light, calm, ink wash style"],
        voice="en-US-ChristopherNeural",
        vertical=True,
        category_id="27",
        tags=["philosophy", "zen", "taoism", "buddhism", "mindfulness"],
        title_prefix="",
    ),
    dict(
        name="ch07_egyptian_mythology",
        display="Egyptian Mythology Breakdowns",
        system_prompt=(
            "You are a narrator breaking down Egyptian mythology for a curious general "
            "audience. Write a vivid 150-180 word script about one god, myth, or afterlife "
            "concept. Accurate to well-documented mythology, end on a compelling hook."
        ),
        topic_prompts=[
            "Anubis and the weighing of the heart ceremony",
            "the myth of Osiris, Isis, and Set",
            "Ra's nightly battle against the serpent Apep",
            "the story of the Eye of Horus",
            "how ancient Egyptians believed the afterlife (Duat) worked",
        ],
        visual_source="ai",
        query_terms=["epic ancient egyptian mythology art, {topic}, gold and sand tones, dramatic, detailed"],
        voice="en-GB-RyanNeural",
        vertical=True,
        category_id="27",
        tags=["egyptian mythology", "ancient egypt", "mythology", "gods"],
        title_prefix="",
    ),
    dict(
        name="ch08_ai_cooking_asmr",
        display="AI Cooking / Food ASMR",
        system_prompt=(
            "Write ONE short caption line (max 12 words) overlaying a satisfying cooking "
            "or food ASMR clip (sizzling, chopping, pouring, melting cheese). Sensory, minimal."
        ),
        topic_prompts=[
            "cheese slowly melting and stretching over noodles",
            "crispy chicken being sliced open steaming",
            "chocolate being poured over a cake",
            "vegetables being chopped rhythmically on a board",
            "syrup being drizzled over pancakes",
        ],
        visual_source="pixabay_video",
        query_terms=["food asmr cooking", "melting cheese", "chopping vegetables", "pouring sauce food"],
        voice="en-US-AriaNeural",
        vertical=True,
        category_id="26",
        tags=["food asmr", "cooking asmr", "satisfying", "shorts"],
        title_prefix="Satisfying Food ASMR:",
    ),
    dict(
        name="ch09_forgotten_empires",
        display="Forgotten Empires (Khmer, Mali, Sogdian)",
        system_prompt=(
            "You are a documentary narrator specializing in lesser-known historical "
            "empires. Write a vivid, historically-grounded 150-180 word script about one "
            "moment or fact from a forgotten empire. End on a striking hook or 'why don't "
            "we learn about this in school' style close."
        ),
        topic_prompts=[
            "the rise of the Khmer Empire and the building of Angkor Wat",
            "Mansa Musa of the Mali Empire and his legendary wealth",
            "the Sogdians who controlled the Silk Road for centuries",
            "the sudden collapse of the Khmer Empire",
            "the trans-Saharan gold and salt trade of the Mali Empire",
        ],
        visual_source="ai",
        query_terms=["epic historical documentary painting, {topic}, cinematic golden light, highly detailed"],
        voice="en-US-GuyNeural",
        vertical=True,
        category_id="27",
        tags=["forgotten history", "ancient empires", "khmer empire", "mali empire", "history"],
        title_prefix="",
    ),
    dict(
        name="ch10_space_documentary",
        display="Space Documentary Long-form",
        system_prompt=(
            "You are a calm, awe-inspiring space documentary narrator (Carl Sagan-esque). "
            "Write a 300-350 word long-form narration script exploring one space topic with "
            "scientific accuracy and wonder, structured with a hook, 2-3 explained facts, and "
            "a reflective closing line about our place in the universe."
        ),
        topic_prompts=[
            "what would happen if you fell into a black hole",
            "how large the observable universe really is",
            "the search for life on Europa, Jupiter's icy moon",
            "how neutron stars form and why they're so extreme",
            "what the James Webb Space Telescope has revealed about early galaxies",
        ],
        visual_source="ai",
        query_terms=["epic space nebula documentary visual, {topic}, cinematic, ultra detailed, cosmic"],
        voice="en-US-ChristopherNeural",
        vertical=False,
        category_id="27",
        tags=["space", "astronomy", "documentary", "universe", "science"],
        title_prefix="",
    ),
]

CONFIG_PY_TEMPLATE = '''"""
config.py for {display} — edit topic_prompts / voice / query terms here.
Everything else is handled by core/pipeline.py.
"""

SYSTEM_PROMPT = {system_prompt!r}

TOPIC_PROMPTS = {topic_prompts!r}

QUERY_TERMS = {query_terms!r}

def visual_query_fn(topic, script):
    """Return a list of search terms (pixabay) or AI image prompts to source
    visuals for this episode. Edit QUERY_TERMS above to change the look."""
    return [q.format(topic=topic) if "{{topic}}" in q else q for q in QUERY_TERMS]

def title_fn(topic):
    prefix = {title_prefix!r}
    t = topic[0].upper() + topic[1:]
    return (prefix + " " + t).strip()[:100] if prefix else t[:100]

def description_fn(topic):
    base = f"{{topic}}\\n\\nAuto-generated with a free AI content pipeline (script + voice + visuals)."
    return base + "\\n#shorts" if {vertical!r} else base

CONFIG = {{
    "name": {name!r},
    "system_prompt": SYSTEM_PROMPT,
    "topic_prompts": TOPIC_PROMPTS,
    "visual_source": {visual_source!r},
    "visual_query_fn": visual_query_fn,
    "voice": {voice!r},
    "vertical": {vertical!r},
    "category_id": {category_id!r},
    "channel_token_file": "token_{name}.json",
    "title_fn": title_fn,
    "description_fn": description_fn,
    "tags": {tags!r},
}}
'''

base = os.path.dirname(os.path.abspath(__file__))
channels_dir = os.path.join(base, "channels")

for ch in CHANNELS:
    ch_dir = os.path.join(channels_dir, ch["name"])
    os.makedirs(ch_dir, exist_ok=True)
    with open(os.path.join(ch_dir, "__init__.py"), "w") as f:
        f.write("")
    with open(os.path.join(ch_dir, "config.py"), "w") as f:
        f.write(CONFIG_PY_TEMPLATE.format(**ch))
    with open(os.path.join(ch_dir, "run.py"), "w") as f:
        f.write(RUN_PY_TEMPLATE.format(name=ch["name"]))
    print(f"generated channels/{ch['name']}/ ({ch['display']})")

print(f"\\nDone. {len(CHANNELS)} channels generated.")
