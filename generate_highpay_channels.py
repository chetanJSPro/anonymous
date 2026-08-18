"""
generate_highpay_channels.py — generates channels_highpay/<name>/config.py + run.py
for the higher-RPM, faster-growing, lower-competition niches (Aug 2026 research,
see channel_docs_highpay/00_Niche_Research_Summary.docx for sources).

These are ADDITIONAL to the original 10 in channels/ — nothing there was touched.
Run: python3 generate_highpay_channels.py
"""

import os

RUN_PY_TEMPLATE = '''"""
run.py for {name} — auto-generated. Run with:
    python3 -m channels_highpay.{name}.run
    python3 -m channels_highpay.{name}.run --upload
    python3 -m channels_highpay.{name}.run --topic "..."
"""
import argparse
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from core.pipeline import run_episode
from channels_highpay.{name}.config import CONFIG

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
        name="hp01_betrayal_revenge",
        display="Betrayal & Revenge Stories",
        rpm="$12.82",
        system_prompt=(
            "You write a viral first-person 'reddit confession' style story about "
            "betrayal and a satisfying karmic payoff (a cheating partner exposed, a "
            "backstabbing friend or coworker caught, a family member's scheme unraveling). "
            "Write 180-220 words: a clear setup, rising tension, and a satisfying twist "
            "or comeuppance ending. Sound like a real anonymous confession — plain, "
            "specific, emotionally honest — never like a lecture or moral. No real names, "
            "keep it clearly a story, not targeting any real identifiable person."
        ),
        topic_prompts=[
            "a maid of honor who stole the wedding date and got exposed at the reception",
            "a coworker who took credit for a project until the client called out the truth in a meeting",
            "a roommate who secretly rented out the apartment on weekends until the landlord found out",
            "a sibling who forged a parent's signature on an inheritance document",
            "a business partner who was skimming money until the accountant noticed",
        ],
        visual_source="ai",
        query_terms=["cinematic moody photorealistic dramatic scene, {topic}, shallow depth of field, film still, emotional"],
        voice="en-US-GuyNeural", vertical=True, category_id="24",
        tags=["reddit story", "revenge story", "betrayal", "storytime"],
        title_prefix="",
    ),
    dict(
        name="hp02_court_drama",
        display="Court Drama Stories",
        rpm="$9.03",
        system_prompt=(
            "You write a viral first-person 'courtroom story' script — a small claims "
            "dispute, a wild legal case, or a judge calling out an obviously dishonest "
            "party. Write 180-220 words with a clear conflict, a tense back-and-forth, "
            "and a decisive, satisfying ruling. Plausible and specific, never a real "
            "identifiable case or person — write it as a fictionalized dramatization."
        ),
        topic_prompts=[
            "a small claims case over a neighbor's fence built two feet into the wrong yard",
            "a landlord suing a tenant who then produced text messages proving retaliation",
            "a dispute over a wedding photographer who never delivered the photos",
            "a case where a dog walker was sued after a dog went missing, then video evidence changed everything",
            "a contractor sued for a bad renovation who had secretly recorded every conversation",
        ],
        visual_source="ai",
        query_terms=["cinematic courtroom drama scene, {topic}, dramatic lighting, photorealistic, tense atmosphere"],
        voice="en-US-ChristopherNeural", vertical=True, category_id="24",
        tags=["court drama", "courtroom story", "legal drama", "storytime"],
        title_prefix="",
    ),
    dict(
        name="hp03_karma_justice",
        display="Karma & Justice Stories",
        rpm="$5.70",
        system_prompt=(
            "You write a viral first-person 'petty revenge' or 'instant karma' story "
            "(a rude customer, an entitled neighbor, a bully getting an unexpected "
            "comeuppance). Write 160-200 words: relatable setup, escalating rudeness or "
            "unfairness, then a clean, satisfying karmic resolution. Keep it light enough "
            "to be shareable, not mean-spirited or targeting real people."
        ),
        topic_prompts=[
            "an entitled customer who demanded a refund and got caught lying on camera",
            "a neighbor who kept stealing parking spots until the HOA got involved",
            "a bully in a group chat who got exposed by a screenshot they forgot existed",
            "a coworker who mocked someone's side hustle until it became the company's biggest client",
            "a person who cut in line at the airport and the gate agent had the perfect response",
        ],
        visual_source="ai",
        query_terms=["cinematic everyday-life dramatic scene, {topic}, warm realistic lighting, photorealistic"],
        voice="en-US-JennyNeural", vertical=True, category_id="24",
        tags=["karma", "instant karma", "petty revenge", "storytime"],
        title_prefix="",
    ),
    dict(
        name="hp04_veteran_kindness",
        display="Veteran Kindness Stories",
        rpm="$7.13",
        system_prompt=(
            "You write a heartfelt, uplifting true-feeling story about a veteran being "
            "shown unexpected kindness, respect, or recognition by a stranger (a free "
            "meal, an upgraded flight, a small business honoring them). Write 160-200 "
            "words, warm and sincere tone, ending on an emotional, feel-good note. "
            "Respectful and dignified — never pitying."
        ),
        topic_prompts=[
            "a diner owner who quietly comps every veteran's meal on their anniversary",
            "a stranger at an airport who gave up a first class seat to a veteran flying home",
            "a young cashier who noticed a veteran's hat and paid for their groceries",
            "a small town that surprises a returning veteran with a welcome home parade",
            "a mechanic who fixed a veteran's truck for free after hearing their story",
        ],
        visual_source="ai",
        query_terms=["warm cinematic heartfelt photorealistic scene, {topic}, golden hour lighting, emotional, respectful"],
        voice="en-US-ChristopherNeural", vertical=True, category_id="22",
        tags=["veteran story", "kindness", "feel good story", "storytime"],
        title_prefix="",
    ),
    dict(
        name="hp05_sleep_soundscapes",
        display="Sleep & Healing Soundscapes",
        rpm="$10.92",
        system_prompt=(
            "Write ONE short on-screen title (max 10 words) for a long-form sleep/healing "
            "ambient soundscape video (rain, soft drones, deep sleep tones, healing "
            "frequencies framing). No spoken narration — just a calming title."
        ),
        topic_prompts=[
            "deep sleep rain sounds for relaxation and healing",
            "calming ocean waves for stress relief and sleep",
            "gentle forest ambience for deep relaxation",
            "soft thunderstorm sounds for undisturbed sleep",
            "peaceful night ambience with distant wind for sleep",
        ],
        visual_source="pixabay_video",
        query_terms=["calm night sky", "soft rain relaxing", "ocean waves calm", "peaceful forest night"],
        voice="en-US-AriaNeural", vertical=False, category_id="22",
        tags=["sleep sounds", "relaxation", "healing music", "ambient"],
        title_prefix="",
    ),
    dict(
        name="hp06_literary_analysis",
        display="Literary Analysis & Book Reviews",
        rpm="$9.15",
        system_prompt=(
            "You are a thoughtful literary narrator breaking down one book, author, or "
            "literary theme for a curious general audience (classic novels, famous "
            "authors' lives, the meaning behind a well-known book). Write a 160-190 word "
            "script: a hook, the core insight, and a closing thought that makes people "
            "want to read the book."
        ),
        topic_prompts=[
            "the real meaning behind George Orwell's 1984",
            "why The Great Gatsby's ending still divides readers",
            "the dark true story that inspired Mary Shelley's Frankenstein",
            "what Pride and Prejudice actually says about class and marriage",
            "why Kafka's The Metamorphosis is still so unsettling today",
        ],
        visual_source="ai",
        query_terms=["moody library aesthetic photorealistic scene, {topic}, warm lighting, books, cinematic"],
        voice="en-US-ChristopherNeural", vertical=True, category_id="27",
        tags=["book review", "literary analysis", "books", "classic literature"],
        title_prefix="",
    ),
    dict(
        name="hp07_senior_longevity",
        display="Senior Health & Longevity Habits",
        rpm="$6.17",
        system_prompt=(
            "You write general wellness and longevity lifestyle content for an older "
            "adult audience — everyday habits linked to healthy aging (walking, sleep "
            "routines, social connection, balanced meals, staying mentally active). Write "
            "a 150-180 word script sharing ONE practical, non-medical lifestyle habit and "
            "why it helps healthy aging. Do not give medical advice, do not mention "
            "specific conditions, medications, or diagnoses — keep it general wellness "
            "and lifestyle only, and suggest viewers consult a doctor for personal advice."
        ),
        topic_prompts=[
            "why a short daily walk after meals supports healthy aging",
            "the longevity benefits of staying socially connected in later life",
            "how a consistent sleep routine supports healthy aging",
            "why staying mentally active with new hobbies matters for older adults",
            "the value of stretching and light mobility work for older adults",
        ],
        visual_source="ai",
        query_terms=["warm photorealistic lifestyle scene, {topic}, natural light, dignified, real-life feeling"],
        voice="en-US-AriaNeural", vertical=True, category_id="26",
        tags=["healthy aging", "longevity", "senior wellness", "lifestyle tips"],
        title_prefix="",
    ),
    dict(
        name="hp08_english_learning",
        display="English Learning Podcast Shorts",
        rpm="$11.88",
        system_prompt=(
            "You write a short spoken-English learning lesson for intermediate ESL "
            "learners. Teach ONE common phrase, idiom, or grammar point: explain it in "
            "very simple English, give 2 example sentences, and note when to use it. "
            "Write 120-150 words, warm and encouraging teacher tone, simple vocabulary."
        ),
        topic_prompts=[
            "the phrase 'get the hang of it' and how to use it naturally",
            "the difference between 'make' and 'do' in everyday English",
            "the idiom 'hit the books' and when native speakers use it",
            "how to politely disagree in English using softening phrases",
            "the phrasal verb 'look forward to' and common mistakes learners make",
        ],
        visual_source="ai",
        query_terms=["clean minimalist educational illustration, {topic}, friendly, bright colors, flat design"],
        voice="en-US-JennyNeural", vertical=True, category_id="27",
        tags=["learn english", "esl", "english lesson", "vocabulary"],
        title_prefix="Learn English:",
    ),
]

CONFIG_PY_TEMPLATE = '''"""
config.py for {display} (est. RPM {rpm}) — edit topic_prompts / voice / query terms here.
Everything else is handled by core/pipeline.py (same shared toolkit as channels/).
"""

SYSTEM_PROMPT = {system_prompt!r}

TOPIC_PROMPTS = {topic_prompts!r}

QUERY_TERMS = {query_terms!r}

def visual_query_fn(topic, script):
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
channels_dir = os.path.join(base, "channels_highpay")

for ch in CHANNELS:
    ch_dir = os.path.join(channels_dir, ch["name"])
    os.makedirs(ch_dir, exist_ok=True)
    with open(os.path.join(ch_dir, "__init__.py"), "w") as f:
        f.write("")
    with open(os.path.join(ch_dir, "config.py"), "w") as f:
        f.write(CONFIG_PY_TEMPLATE.format(**ch))
    with open(os.path.join(ch_dir, "run.py"), "w") as f:
        f.write(RUN_PY_TEMPLATE.format(name=ch["name"]))
    print(f"generated channels_highpay/{ch['name']}/ ({ch['display']}, RPM {ch['rpm']})")

print(f"\\nDone. {len(CHANNELS)} high-pay channels generated.")
