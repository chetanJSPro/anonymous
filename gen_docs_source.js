const fs = require("fs");
const path = require("path");
const {
  Document, Packer, Paragraph, TextRun, HeadingLevel, Table, TableRow, TableCell,
  WidthType, ShadingType, BorderStyle, AlignmentType, LevelFormat, convertInchesToTwip,
} = require("docx");

const PAGE = { width: 12240, height: 15840 }; // US Letter
const ACCENT = "2E5AAC";
const LIGHT = "EAF0FB";

function h1(text) {
  return new Paragraph({ text, heading: HeadingLevel.HEADING_1, spacing: { before: 300, after: 150 } });
}
function h2(text) {
  return new Paragraph({ text, heading: HeadingLevel.HEADING_2, spacing: { before: 240, after: 120 } });
}
function p(text, opts = {}) {
  return new Paragraph({ children: [new TextRun({ text, ...opts })], spacing: { after: 120 } });
}
function bullet(text, opts = {}) {
  return new Paragraph({
    children: [new TextRun({ text, ...opts })],
    numbering: { reference: "bullets", level: 0 },
    spacing: { after: 60 },
  });
}
function numbered(text, opts = {}) {
  return new Paragraph({
    children: [new TextRun({ text, ...opts })],
    numbering: { reference: "numbers", level: 0 },
    spacing: { after: 60 },
  });
}
function code(lines) {
  return new Paragraph({
    children: (Array.isArray(lines) ? lines : [lines]).flatMap((l, i, arr) => {
      const run = new TextRun({ text: l, font: "Consolas", size: 20 });
      return i < arr.length - 1 ? [run, new TextRun({ break: 1 })] : [run];
    }),
    shading: { type: ShadingType.CLEAR, fill: "1E1E1E" },
    spacing: { before: 100, after: 200 },
    border: {
      top: { style: BorderStyle.SINGLE, size: 2, color: "444444" },
      bottom: { style: BorderStyle.SINGLE, size: 2, color: "444444" },
      left: { style: BorderStyle.SINGLE, size: 2, color: "444444" },
      right: { style: BorderStyle.SINGLE, size: 2, color: "444444" },
    },
  });
}
function codeText(lines) {
  // white-on-dark code block via runs colored white
  return new Paragraph({
    children: (Array.isArray(lines) ? lines : [lines]).flatMap((l, i, arr) => {
      const run = new TextRun({ text: l, font: "Consolas", size: 20, color: "D4D4D4" });
      return i < arr.length - 1 ? [run, new TextRun({ break: 1 })] : [run];
    }),
    shading: { type: ShadingType.CLEAR, fill: "1E1E1E" },
    spacing: { before: 100, after: 200 },
    indent: { left: 200, right: 200 },
  });
}

function infoTable(rows) {
  const colWidths = [3000, 6800];
  return new Table({
    width: { size: colWidths[0] + colWidths[1], type: WidthType.DXA },
    columnWidths: colWidths,
    rows: rows.map(([k, v]) =>
      new TableRow({
        children: [
          new TableCell({
            width: { size: colWidths[0], type: WidthType.DXA },
            shading: { type: ShadingType.CLEAR, fill: LIGHT },
            children: [new Paragraph({ children: [new TextRun({ text: k, bold: true })] })],
          }),
          new TableCell({
            width: { size: colWidths[1], type: WidthType.DXA },
            children: [new Paragraph({ children: [new TextRun({ text: v })] })],
          }),
        ],
      })
    ),
  });
}

const numbering = {
  config: [
    {
      reference: "bullets",
      levels: [{ level: 0, format: LevelFormat.BULLET, text: "•", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 400, hanging: 260 } } } }],
    },
    {
      reference: "numbers",
      levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 400, hanging: 260 } } } }],
    },
  ],
};

function titlePage(ch) {
  return [
    new Paragraph({
      children: [new TextRun({ text: ch.emoji + "  " + ch.display, bold: true, size: 44, color: ACCENT })],
      spacing: { before: 200, after: 100 },
    }),
    new Paragraph({
      children: [new TextRun({ text: ch.tagline, italics: true, size: 24, color: "555555" })],
      spacing: { after: 300 },
    }),
    infoTable([
      ["Channel #", `${ch.num} of 10 — from your master list, item #${ch.sourceRef}`],
      ["Niche / category", ch.category],
      ["Format", ch.vertical ? "YouTube Shorts (1080×1920, vertical)" : "Long-form (1920×1080, horizontal)"],
      ["Est. monthly cost", ch.costTier + "  (all tools used below are free tier)"],
      ["Risk level", ch.risk],
      ["Automation level", ch.automation],
      ["Code folder", `channels/${ch.folder}/`],
    ]),
    new Paragraph({ text: "", spacing: { after: 200 } }),
  ];
}

function commonSetup() {
  return [
    h1("Part 1 — One-Time Setup (do this once, covers all 10 channels)"),
    p("This channel runs on a shared, 100% free Python toolkit (in the core/ folder of the zip you received). You only need to do this setup once — all 10 channels reuse it."),
    h2("1. Install Python + dependencies"),
    p("Requires Python 3.9+ and ffmpeg installed on your system (ffmpeg is free — on Windows use choco/scoop, on Mac “brew install ffmpeg”, on Linux it's usually preinstalled or one apt command)."),
    codeText([
      "cd faceless_automation",
      "python3 -m pip install -r requirements.txt",
    ]),
    h2("2. Get your free script-writing API key (Groq)"),
    numbered("Go to https://console.groq.com and sign up (free, no credit card)."),
    numbered("Click “API Keys” → “Create API Key”, copy it."),
    numbered("Set it as an environment variable before running any channel:"),
    codeText(["export GROQ_API_KEY=\"your-key-here\"     # Mac/Linux", "setx GROQ_API_KEY \"your-key-here\"       # Windows (restart terminal after)"]),
    p("If you skip this, the pipeline automatically falls back to a free keyless endpoint (Pollinations.ai) — works, but is slower and less reliable, so Groq is worth the 2-minute signup.", { italics: true, color: "555555" }),
    h2("3. Get your free visuals API key (Pixabay) — only needed for ASMR/cooking/nature channels"),
    numbered("Go to https://pixabay.com/accounts/register/ and sign up (free)."),
    numbered("Go to https://pixabay.com/api/docs/ — your API key is shown at the top once logged in."),
    numbered("Set it as an environment variable:"),
    codeText(["export PIXABAY_API_KEY=\"your-key-here\""]),
    p("Channels using AI-generated art (mythology, history, space, quiz) use Pollinations.ai instead — zero signup, zero key needed, nothing to configure.", { italics: true, color: "555555" }),
    h2("4. One-time YouTube upload authorization (per channel/account)"),
    p("Do this once per new YouTube channel you create — it lets the script upload directly instead of you doing it by hand."),
    numbered("Go to https://console.cloud.google.com → create a new project (free)."),
    numbered("APIs & Services → Library → enable “YouTube Data API v3”."),
    numbered("APIs & Services → OAuth consent screen → choose External → add the new channel's Google account as a test user."),
    numbered("APIs & Services → Credentials → Create Credentials → OAuth client ID → Application type: Desktop app."),
    numbered("Download the JSON → save it as client_secret.json inside the faceless_automation folder."),
    numbered("The first time you run a channel with --upload, a browser window opens asking you to log in as that channel's account and approve access. After that it's silent (a token file is saved)."),
    p("Free quota: 10,000 units/day per Google Cloud project — an upload costs ~1,600 units, so about 6 uploads/day per channel before hitting the free ceiling (way more than you'll need for a daily-post schedule).", { italics: true, color: "555555" }),
  ];
}

function channelSpecific(ch) {
  const runCmd = `python3 -m channels.${ch.folder}.run`;
  return [
    h1("Part 2 — This Channel's Setup"),
    h2("What this channel is"),
    p(ch.description),
    h2("Content style / prompt"),
    p("The AI is instructed with this system prompt (edit it anytime in channels/" + ch.folder + "/config.py to change tone/style):", { italics: true, color: "555555" }),
    codeText(wrapLines(ch.systemPrompt, 90)),
    h2("Example topics in the rotation"),
    ...ch.topics.map((t) => bullet(t)),
    p("Add as many more lines as you want to TOPIC_PROMPTS in config.py — the script picks one at random each run, or you can force a specific one with --topic.", { italics: true, color: "555555" }),
    h2("Voice & visuals"),
    infoTable([
      ["TTS voice", ch.voice + "  (free, via edge-tts — change anytime in config.py)"],
      ["Visual source", ch.visualSourceLabel],
      ["Video shape", ch.vertical ? "Vertical 1080×1920 (Shorts)" : "Horizontal 1920×1080 (long-form)"],
    ]),
    h1("Part 3 — Generating an Episode"),
    h2("Generate one video (no upload — review it first)"),
    codeText([runCmd]),
    p("This writes the finished MP4 to output/" + ch.folder + "/final.mp4 along with the narration audio and .srt captions. Watch it before you post — spot-check for factual slips or a bad caption render, especially for the mythology/history channels."),
    h2("Generate AND auto-upload straight to YouTube"),
    codeText([runCmd + " --upload"]),
    h2("Force a specific topic instead of a random one"),
    codeText([runCmd + ' --topic "your topic sentence here"']),
    h2("Post as unlisted first (recommended for your first 2–3 uploads)"),
    codeText([runCmd + " --upload --privacy unlisted"]),
    h1("Part 4 — Posting Schedule"),
    infoTable([
      ["Suggested cadence", ch.cadence],
      ["Best posting time (IST)", ch.postTime],
      ["Batch tip", "Run the generate command 5–7 times in a row (no --upload) to build a buffer of videos, review them all, then upload on schedule with --upload."],
    ]),
    h1("Part 5 — Monetization & Risk Notes"),
    ...ch.notes.map((n) => bullet(n)),
    new Paragraph({ text: "", pageBreakBefore: true }),
  ];
}

function wrapLines(text, width) {
  const words = text.split(" ");
  const lines = [];
  let cur = "";
  for (const w of words) {
    if ((cur + " " + w).trim().length > width) {
      lines.push(cur.trim());
      cur = w;
    } else {
      cur = (cur + " " + w).trim();
    }
  }
  if (cur) lines.push(cur);
  return lines;
}

const CHANNELS = [
  {
    num: 1, folder: "ch01_ai_asmr", sourceRef: 30, emoji: "\u{1F9FC}",
    display: "AI ASMR (Soap / Slime / Glass Cutting)",
    tagline: "Zero-script, pure sensory shorts — the fastest channel to automate on this list.",
    category: "ASMR", costTier: "$ (cheapest)", risk: "🟢 Low", automation: "⚡ Near-zero touch",
    vertical: true,
    description: "Short, satisfying visual loops (soap cutting, slime, glass, kinetic sand) with a single overlay caption and ambient/no narration. No factual content, no editorial risk — just sourcing good stock clips and stitching them with a caption.",
    systemPrompt: "You write a single short spoken caption line (max 12 words) that could overlay a satisfying ASMR video (soap cutting, slime, glass, kinetic sand). No narration needed beyond this one caption. Keep it minimal and sensory.",
    topics: ["Glossy soap bar being sliced into cubes", "Colorful slime being stretched and folded", "Glass orb cracking in slow motion", "Kinetic sand being cut with a knife", "Honeycomb soap crumbling apart"],
    voice: "en-US-AriaNeural", visualSourceLabel: "Pixabay free stock video (search terms: “soap cutting asmr”, “slime asmr”, “sand cutting”)",
    cadence: "1–2 shorts/day — this channel is cheap enough to post aggressively.",
    postTime: "8–9 PM (peak scroll time)",
    notes: [
      "Low copyright/demonetization risk — no claims, no music rights issues if you use royalty-free audio.",
      "YouTube Partner Program needs 1,000 subs + 10M Shorts views (90 days) or 4,000 watch hours — ASMR shorts are good for view-count velocity.",
      "Reused stock footage across many faceless ASMR channels can trigger “reused content” flags if you don't vary clips — rotate your Pixabay search terms often.",
    ],
  },
  {
    num: 2, folder: "ch02_nature_ambient", sourceRef: 32, emoji: "\u{1F327}️",
    display: "Nature Ambient Long-form",
    tagline: "Rain, fire, and forest loops for sleep/study audiences — long watch-time, low effort.",
    category: "ASMR / Ambient", costTier: "$$", risk: "🟢 Low", automation: "⚡ Near-zero touch",
    vertical: false,
    description: "Long-form (30–60+ min) ambient nature videos — rain on a roof, campfire, ocean waves — used for background noise, sleep, and study. No narration, just a title card and looping footage.",
    systemPrompt: "Write ONE short on-screen title (max 10 words) for a long-form ambient nature video (rain, campfire, forest, ocean). No spoken narration — just a title.",
    topics: ["Heavy rain on a cabin roof at night", "Crackling campfire in a quiet forest", "Ocean waves on a rocky shore at dusk", "Wind through a pine forest at dawn", "Thunderstorm over a misty lake"],
    voice: "n/a (no narration)", visualSourceLabel: "Pixabay free stock video, looped to fill 30–60+ minutes",
    cadence: "2–3 long-form videos/week — quality over quantity; each one gets replayed for years.",
    postTime: "9–10 PM (people search these before sleep)",
    notes: [
      "Extremely high watch-time potential per video — strong for ad revenue once monetized (4,000 watch hours threshold is easy to hit with 8-hour loop versions).",
      "Consider making 1-hour and 8-hour versions of your best performers — same source clips, just looped longer with core/assemble.py.",
      "No factual or copyright risk from the content itself; just make sure background music (if you add any) is royalty-free.",
    ],
  },
  {
    num: 3, folder: "ch03_hindu_mythology", sourceRef: 9, emoji: "\u{1F549}️",
    display: "Hindu Mythology (Mahabharata, Ramayana)",
    tagline: "Built-in massive audience, evergreen stories — needs a light accuracy check per episode.",
    category: "Mythology", costTier: "$$", risk: "🟢 Low (with review)", automation: "🛠 Needs light review",
    vertical: true,
    description: "Narrated retellings of scenes from the Mahabharata, Ramayana, and Puranas with AI-generated epic-style illustrations. Huge existing audience and evergreen demand, but content should be spot-checked for accuracy/sensitivity before posting since it touches sacred material.",
    systemPrompt: "You are a respectful, historically-grounded narrator of Hindu mythology (Mahabharata, Ramayana, and Puranic stories) for a general global YouTube audience. Write a vivid 150-180 word narration script for one self-contained story or scene. Be accurate to well-known tellings, avoid embellishing sacred material irreverently, and end on a compelling hook or reflection.",
    topics: ["Arjuna receiving the Bhagavad Gita's wisdom from Krishna before the war", "Hanuman's leap across the ocean to Lanka", "The exile of Rama, Sita, and Lakshmana to the forest", "Draupadi's vastraharan and Krishna's protection", "The birth and strength of Bhima", "Ravana's ten heads and his devotion to Shiva"],
    voice: "en-US-ChristopherNeural", visualSourceLabel: "AI-generated images (Pollinations.ai, free, no key) — prompt style: “epic Indian mythological painting, dramatic lighting”",
    cadence: "3–4 shorts/week — leave time to actually watch each one before posting.",
    postTime: "7–8 AM or 8–9 PM IST (matches core audience timezone)",
    notes: [
      "⚠️ Always watch the finished video before posting — AI can misstate names, events, or relationships in well-known epics; getting this wrong with a religious/cultural audience causes real backlash.",
      "Avoid the LLM inventing new plot details not in traditional tellings — keep TOPIC_PROMPTS specific to well-documented scenes.",
      "Strong monetization potential given audience size, but treat this as the one channel on your list that isn't truly ‘free-running’ — budget 5 minutes of review per episode.",
    ],
  },
  {
    num: 4, folder: "ch04_geography_quiz", sourceRef: 41, emoji: "\u{1F30D}",
    display: "Geography Quiz Shorts (“Guess the Country”)",
    tagline: "Fully templated format — the LLM can churn out infinite fresh quizzes.",
    category: "Quiz", costTier: "$$", risk: "🟢 Low", automation: "⚡ Near-zero touch",
    vertical: true,
    description: "3 progressively-easier clues about a real country, ending with a reveal. Fully templated, virtually zero editorial judgment required per episode — one of the safest channels to run unattended.",
    systemPrompt: "You create a 'Guess the Country' quiz short. Write: 3 short numbered clues (each under 12 words) about one real country, ending with 'What country is this?', then on a new line write 'ANSWER: <country>'. Make clues progressively easier.",
    topics: ["A country in South America known for a famous ancient citadel", "A Southeast Asian country made of over 17,000 islands", "A European country famous for tulips and windmills", "An African country home to the world's longest river", "A Middle Eastern country famous for its ancient rose-red city"],
    voice: "en-US-JennyNeural", visualSourceLabel: "AI-generated minimalist map-style background art (Pollinations.ai, free)",
    cadence: "1/day — quiz format supports high frequency without feeling repetitive.",
    postTime: "12–1 PM or 6–7 PM IST",
    notes: [
      "Lowest editorial-risk channel on the list besides ASMR — factual clues are easy to verify and low-stakes if occasionally imprecise.",
      "Great channel to A/B test hooks/thumbnails since output volume is high and cheap.",
      "Consider adding a 2–3 second pause + “comment your guess” before the reveal to boost engagement/comments.",
    ],
  },
  {
    num: 5, folder: "ch05_norse_sagas", sourceRef: 8, emoji: "⚔️",
    display: "Norse / Viking Sagas",
    tagline: "Strong short-form virality in the history/mythology niche.",
    category: "Mythology", costTier: "$$$", risk: "🟢 Low", automation: "🛠 Light review recommended",
    vertical: true,
    description: "Dramatic narrations of Norse myths (Odin, Thor, Loki, Ragnarok) and real Viking history moments, paired with epic AI-generated art.",
    systemPrompt: "You are a dramatic narrator of Norse mythology and Viking sagas. Write a vivid 150-180 word narration script for one self-contained myth or saga moment (Odin, Thor, Loki, Ragnarok, real Viking history). End on a striking hook.",
    topics: ["Odin sacrificing his eye at Mimir's well for wisdom", "Thor's battle with the Midgard Serpent", "Loki's binding after the death of Baldr", "The signs that foretell Ragnarok", "A Viking longship raid on the English coast"],
    voice: "en-GB-RyanNeural", visualSourceLabel: "AI-generated images (Pollinations.ai, free) — prompt style: “epic viking norse mythology painting, stormy lighting”",
    cadence: "3–4 shorts/week",
    postTime: "7–8 PM IST",
    notes: [
      "Lower cultural-sensitivity risk than living-religion mythology channels, but still worth a quick factual skim before posting.",
      "Strong crossover audience with gaming/history fans — cross-promote with your Forgotten Empires and Egyptian Mythology channels.",
      "British voice (en-GB-RyanNeural) tests well for this genre — swap if you prefer a different tone.",
    ],
  },
  {
    num: 6, folder: "ch06_eastern_philosophy", sourceRef: 40, emoji: "☯️",
    display: "Eastern Philosophy (Zen, Tao, Buddhism)",
    tagline: "Calm, evergreen, low-risk — monetizes well with a mature audience.",
    category: "Self-Improvement", costTier: "$$", risk: "🟢 Low", automation: "🛠 Light review recommended",
    vertical: true,
    description: "Short parables and teachings from Zen, Taoism, and Buddhism explained in plain modern language, ending with one practical takeaway. Calm pacing, works well as a recurring format.",
    systemPrompt: "You are a calm, wise narrator explaining one Eastern philosophy concept (Zen, Taoism, Buddhism) in plain, modern language. Write a 130-160 word script: a short story or parable, then one clear practical takeaway. Calm, slow pacing.",
    topics: ["The Zen parable of the full teacup", "The Taoist idea of wu wei (effortless action)", "The Buddhist concept of impermanence (anicca)", "The parable of the two monks and the river", "The Tao Te Ching's teaching on softness overcoming hardness"],
    voice: "en-US-ChristopherNeural", visualSourceLabel: "AI-generated ink-wash style art (Pollinations.ai, free) — prompt style: “serene minimalist zen painting, soft light”",
    cadence: "3–4 shorts/week",
    postTime: "6–7 AM IST (morning-reflection audience)",
    notes: [
      "Spiritual/religious teaching content — do a light accuracy pass so parables aren't garbled or misattributed to the wrong tradition.",
      "This audience skews toward longer engagement/comments — good for community-building, not just view farming.",
      "Avoid the LLM presenting any teaching as literal medical/psychological advice — keep it reflective, not prescriptive.",
    ],
  },
  {
    num: 7, folder: "ch07_egyptian_mythology", sourceRef: 10, emoji: "\u{1F4FF}",
    display: "Egyptian Mythology Breakdowns",
    tagline: "Same production pipeline as your other mythology channels — cross-promote easily.",
    category: "Mythology", costTier: "$$$", risk: "🟢 Low", automation: "🛠 Light review recommended",
    vertical: true,
    description: "Breakdowns of Egyptian gods, myths, and afterlife beliefs (Anubis, Osiris, Ra, the Duat) narrated with epic gold-and-sand-toned AI art.",
    systemPrompt: "You are a narrator breaking down Egyptian mythology for a curious general audience. Write a vivid 150-180 word script about one god, myth, or afterlife concept. Accurate to well-documented mythology, end on a compelling hook.",
    topics: ["Anubis and the weighing of the heart ceremony", "The myth of Osiris, Isis, and Set", "Ra's nightly battle against the serpent Apep", "The story of the Eye of Horus", "How ancient Egyptians believed the afterlife (Duat) worked"],
    voice: "en-GB-RyanNeural", visualSourceLabel: "AI-generated images (Pollinations.ai, free) — prompt style: “epic ancient egyptian mythology art, gold and sand tones”",
    cadence: "3–4 shorts/week",
    postTime: "7–8 PM IST",
    notes: [
      "Well-documented mythology with lots of reliable source material — easy for the LLM to stay accurate, but still skim before posting.",
      "High visual appeal (gold/sand palette) — good thumbnail material, invest a little extra in the AI image prompt quality.",
      "Shares a production pipeline with Norse and Hindu mythology channels — batch-generate all three in one sitting.",
    ],
  },
  {
    num: 8, folder: "ch08_ai_cooking_asmr", sourceRef: 31, emoji: "\u{1F373}",
    display: "AI Cooking / Food ASMR",
    tagline: "Same zero-script pipeline as channel 1, different visual asset library.",
    category: "ASMR", costTier: "$$", risk: "🟢 Low", automation: "⚡ Near-zero touch",
    vertical: true,
    description: "Satisfying food/cooking clips — melting cheese, sizzling pans, syrup pours — with one overlay caption. No narration, no factual claims, minimal editorial risk.",
    systemPrompt: "Write ONE short caption line (max 12 words) overlaying a satisfying cooking or food ASMR clip (sizzling, chopping, pouring, melting cheese). Sensory, minimal.",
    topics: ["Cheese slowly melting and stretching over noodles", "Crispy chicken being sliced open steaming", "Chocolate being poured over a cake", "Vegetables being chopped rhythmically on a board", "Syrup being drizzled over pancakes"],
    voice: "en-US-AriaNeural", visualSourceLabel: "Pixabay free stock video (search terms: “food asmr cooking”, “melting cheese”, “pouring sauce food”)",
    cadence: "1–2 shorts/day",
    postTime: "12–1 PM or 7–8 PM IST (lunch/dinner scroll windows)",
    notes: [
      "Do NOT make health or nutrition claims in captions — keep language purely sensory (“satisfying”, “crispy”) to avoid any food-safety/misinformation risk.",
      "Very shareable format — good candidate for cross-posting to Instagram Reels/TikTok using the same output/ MP4.",
      "Rotate Pixabay search terms regularly so consecutive uploads don't look identical to viewers or to YouTube's duplicate-content detection.",
    ],
  },
  {
    num: 9, folder: "ch09_forgotten_empires", sourceRef: 2, emoji: "\u{1F3F0}",
    display: "Forgotten Empires (Khmer, Mali, Sogdian)",
    tagline: "Less saturated than mainstream history content — a real content moat.",
    category: "History", costTier: "$$$$$", risk: "🟢 Low", automation: "🧪 Experimental — review recommended",
    vertical: true,
    description: "Documentary-style narrations covering lesser-known historical empires (Khmer, Mali, Sogdian) that get little mainstream coverage — an underexploited niche compared to Roman/Egyptian history content.",
    systemPrompt: "You are a documentary narrator specializing in lesser-known historical empires. Write a vivid, historically-grounded 150-180 word script about one moment or fact from a forgotten empire. End on a striking hook or 'why don't we learn about this in school' style close.",
    topics: ["The rise of the Khmer Empire and the building of Angkor Wat", "Mansa Musa of the Mali Empire and his legendary wealth", "The Sogdians who controlled the Silk Road for centuries", "The sudden collapse of the Khmer Empire", "The trans-Saharan gold and salt trade of the Mali Empire"],
    voice: "en-US-GuyNeural", visualSourceLabel: "AI-generated images (Pollinations.ai, free) — prompt style: “epic historical documentary painting, cinematic golden light”",
    cadence: "2–3/week — this niche rewards depth over volume.",
    postTime: "7–8 PM IST",
    notes: [
      "Because this covers less-documented history, do a quick fact-check pass — LLMs are more prone to filling gaps with plausible-sounding but wrong details on niche topics.",
      "Highest content-moat value on your list — far less competition than “Roman Empire” style channels.",
      "Higher cost tier reflects that quality AI art + careful prompts matter more here to look ‘documentary-grade’ rather than generic.",
    ],
  },
  {
    num: 10, folder: "ch10_space_documentary", sourceRef: 12, emoji: "\u{1F30C}",
    display: "Space Documentary Long-form",
    tagline: "Reliable long watch-time + strong ad revenue once monetized.",
    category: "Science", costTier: "$$$$$", risk: "🟢 Low", automation: "🧪 Experimental — review recommended",
    vertical: false,
    description: "Calm, awe-inspiring long-form narration (Sagan-style) on space topics — black holes, the observable universe, exoplanets — backed by cinematic AI nebula/cosmic visuals.",
    systemPrompt: "You are a calm, awe-inspiring space documentary narrator (Carl Sagan-esque). Write a 300-350 word long-form narration script exploring one space topic with scientific accuracy and wonder, structured with a hook, 2-3 explained facts, and a reflective closing line about our place in the universe.",
    topics: ["What would happen if you fell into a black hole", "How large the observable universe really is", "The search for life on Europa, Jupiter's icy moon", "How neutron stars form and why they're so extreme", "What the James Webb Space Telescope has revealed about early galaxies"],
    voice: "en-US-ChristopherNeural", visualSourceLabel: "AI-generated cosmic imagery (Pollinations.ai, free) — prompt style: “epic space nebula documentary visual, cinematic, ultra detailed”",
    cadence: "1–2/week — longer scripts, more visuals per episode, so lower volume by design.",
    postTime: "8–9 PM IST",
    notes: [
      "Scientific accuracy matters here more than any other channel — always skim-review the script against known facts before posting; LLMs occasionally overstate speculative science as settled fact.",
      "Long-form format means strong watch-time-hour accumulation toward the 4,000-hour monetization threshold.",
      "Consider pairing narration with real NASA/ESA public-domain imagery (nasa.gov media library, free to use) as an alternative or supplement to AI-generated visuals for extra credibility.",
    ],
  },
];

async function main() {
  const outDir = path.join(__dirname, "output_docs");
  fs.mkdirSync(outDir, { recursive: true });

  for (const ch of CHANNELS) {
    const doc = new Document({
      numbering,
      sections: [
        {
          properties: { page: { size: PAGE, margin: { top: 1000, bottom: 1000, left: 1100, right: 1100 } } },
          children: [
            ...titlePage(ch),
            ...commonSetup(),
            ...channelSpecific(ch),
            h1("Reference"),
            p("This document is part of a 10-channel free faceless-YouTube automation set, August 2026. All 10 channels share the same core/ Python toolkit (in the accompanying zip) — only the config.py per channel differs. Total software cost: $0 (Groq, Pixabay, edge-tts, Pollinations.ai, and the YouTube Data API are all free tiers)."),
          ],
        },
      ],
    });

    const buf = await Packer.toBuffer(doc);
    const filename = `Channel_${String(ch.num).padStart(2, "0")}_${ch.folder.replace(/^ch\d+_/, "")}.docx`;
    fs.writeFileSync(path.join(outDir, filename), buf);
    console.log("wrote", filename);
  }
}

main();
