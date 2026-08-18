const fs = require("fs");
const path = require("path");
const {
  Document, Packer, Paragraph, TextRun, HeadingLevel, Table, TableRow, TableCell,
  WidthType, ShadingType, BorderStyle, AlignmentType, LevelFormat, ExternalHyperlink,
} = require("docx");

const PAGE = { width: 12240, height: 15840 };
const ACCENT = "B3541E";
const LIGHT = "FBEFE6";

function h1(text) { return new Paragraph({ text, heading: HeadingLevel.HEADING_1, spacing: { before: 300, after: 150 } }); }
function h2(text) { return new Paragraph({ text, heading: HeadingLevel.HEADING_2, spacing: { before: 240, after: 120 } }); }
function p(text, opts = {}) { return new Paragraph({ children: [new TextRun({ text, ...opts })], spacing: { after: 120 } }); }
function bullet(text, opts = {}) {
  return new Paragraph({ children: [new TextRun({ text, ...opts })], numbering: { reference: "bullets", level: 0 }, spacing: { after: 60 } });
}
function numbered(text, opts = {}) {
  return new Paragraph({ children: [new TextRun({ text, ...opts })], numbering: { reference: "numbers", level: 0 }, spacing: { after: 60 } });
}
function link(text, url) {
  return new ExternalHyperlink({ link: url, children: [new TextRun({ text, style: "Hyperlink" })] });
}
function linkPara(text, url) {
  return new Paragraph({ children: [link(text, url)], spacing: { after: 100 } });
}
function codeText(lines) {
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
          new TableCell({ width: { size: colWidths[0], type: WidthType.DXA }, shading: { type: ShadingType.CLEAR, fill: LIGHT }, children: [new Paragraph({ children: [new TextRun({ text: k, bold: true })] })] }),
          new TableCell({ width: { size: colWidths[1], type: WidthType.DXA }, children: [new Paragraph({ children: [new TextRun({ text: v })] })] }),
        ],
      })
    ),
  });
}
function dataTable(headers, rows, widths) {
  const mk = (t, bold, fill) => new TableCell({
    width: { size: widths[0], type: WidthType.DXA },
    shading: fill ? { type: ShadingType.CLEAR, fill } : undefined,
    children: [new Paragraph({ children: [new TextRun({ text: t, bold })] })],
  });
  const headerRow = new TableRow({
    children: headers.map((hd, i) => new TableCell({
      width: { size: widths[i], type: WidthType.DXA },
      shading: { type: ShadingType.CLEAR, fill: ACCENT },
      children: [new Paragraph({ children: [new TextRun({ text: hd, bold: true, color: "FFFFFF" })] })],
    })),
  });
  const bodyRows = rows.map((r) => new TableRow({
    children: r.map((cell, i) => new TableCell({
      width: { size: widths[i], type: WidthType.DXA },
      children: [new Paragraph({ children: [new TextRun({ text: String(cell) })] })],
    })),
  }));
  return new Table({ width: { size: widths.reduce((a, b) => a + b, 0), type: WidthType.DXA }, columnWidths: widths, rows: [headerRow, ...bodyRows] });
}

const numbering = {
  config: [
    { reference: "bullets", levels: [{ level: 0, format: LevelFormat.BULLET, text: "•", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 400, hanging: 260 } } } }] },
    { reference: "numbers", levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 400, hanging: 260 } } } }] },
  ],
};

// ---------- Doc 0: Research summary ----------
function researchSummaryDoc() {
  return new Document({
    numbering,
    sections: [{
      properties: { page: { size: PAGE, margin: { top: 1000, bottom: 1000, left: 1100, right: 1100 } } },
      children: [
        new Paragraph({ children: [new TextRun({ text: "High-Pay Niche Research Summary", bold: true, size: 44, color: ACCENT })], spacing: { after: 100 } }),
        new Paragraph({ children: [new TextRun({ text: "Why these 8 channels were added, and an honest note on the two Reddit threads you shared.", italics: true, size: 24, color: "555555" })], spacing: { after: 300 } }),

        h1("What happened with the two Reddit links"),
        p("Both Reddit threads you shared (r/passive_income and r/ReelFarmer) could not be fetched directly — Reddit blocks this tool's fetcher with a 403/challenge response on both the original request and a retry. This is a platform-side block, not something I can route around (I don't use workarounds like raw curl/browser automation to bypass fetch restrictions). Search also didn't surface the actual thread content, only unrelated gumroad ‘buy my guide’ listings."),
        p("So the 8 channels below are NOT pulled from those threads. They're built from current (Aug 2026) faceless-YouTube RPM/niche research aggregators, cited below. If you can copy-paste the actual text of either Reddit post/comment into the chat, I can fold in anything genuinely different from what's here.", { bold: true }),

        h1("Why the original 10 channels felt ‘outdated’"),
        p("Mythology, ancient history, and space documentary content is real and can work, but it's a slow-build niche — long average watch time needed, smaller total search demand, and it competes with well-established channels that have years of head start. It's a reasonable long-term bet, not a fast one. It's kept intact in channels/ in case you want to run it in parallel."),

        h1("Selection criteria for the new 8"),
        p("Picked for the combination of: higher RPM (creator revenue per 1,000 views, not just ad CPM), lower current channel-count/competition, format proven to drive fast view velocity (first-person story/confession narration is one of the highest-retention formats on Shorts and long-form right now), and still simple enough for the same free automation pipeline."),

        dataTable(
          ["Niche", "Est. RPM", "Competition", "Why it's faster"],
          [
            ["Betrayal & Revenge Stories", "$12.82", "Low", "21x growth rate; highest retention story format right now"],
            ["English Learning Podcasts", "$11.88", "Low-Med", "21x growth; evergreen — old episodes keep earning views for years"],
            ["Sleep & Healing Soundscapes", "$10.92", "Low", "Near-zero editing once template exists; huge search volume"],
            ["Literary Analysis & Reviews", "$9.15", "Low", "~10K competing channels, older/affluent audience, low saturation"],
            ["Court Drama Stories", "$9.03", "Low", "High retention, low competition, easy to template"],
            ["Veteran Kindness Stories", "$7.13", "Low", "Feel-good format shares heavily, low competition"],
            ["Senior Health & Longevity", "$6.17", "Low", "19x growth rate, underserved older-adult audience"],
            ["Karma & Justice Stories", "$5.70", "Medium", "Extremely proven viral format (AITA/petty revenge style)"],
          ],
          [3400, 1600, 1700, 3100]
        ),
        new Paragraph({ text: "", spacing: { after: 200 } }),

        h1("Sources"),
        linkPara("OutlierKit — Most Profitable YouTube Niches 2026 (Real RPM Data)", "https://outlierkit.com/blog/most-profitable-youtube-niches"),
        linkPara("Faceless.my — Top Faceless YouTube Niches 2026", "https://faceless.my/niches/top-faceless-youtube-niches/"),

        h1("The one honest caveat"),
        p("“Instant views” isn't something any content format can guarantee — RPM and growth-rate numbers describe what happens AFTER a channel gets traction, not a promise that any specific video goes viral. These 8 niches are picked because the format (short, emotionally hooky, first-person story) has the best realistic odds of fast early traction with zero subscriber base, not because success is automatic. Post consistently, watch your first 10-15 videos' retention graphs in YouTube Studio, and double down on whichever channel's numbers move first."),
      ],
    }],
  });
}

// ---------- Channel docs ----------
function titlePage(ch) {
  return [
    new Paragraph({ children: [new TextRun({ text: ch.emoji + "  " + ch.display, bold: true, size: 44, color: ACCENT })], spacing: { before: 200, after: 100 } }),
    new Paragraph({ children: [new TextRun({ text: ch.tagline, italics: true, size: 24, color: "555555" })], spacing: { after: 300 } }),
    infoTable([
      ["Est. RPM", ch.rpm + " (creator revenue per 1,000 views — see research summary doc for sources)"],
      ["Competition", ch.competition],
      ["Format", ch.vertical ? "YouTube Shorts (1080×1920, vertical)" : "Long-form (1920×1080, horizontal)"],
      ["Code folder", `channels_highpay/${ch.folder}/`],
    ]),
    new Paragraph({ text: "", spacing: { after: 200 } }),
  ];
}

function commonSetup() {
  return [
    h1("Part 1 — One-Time Setup (shared with your other 18 channels)"),
    p("This uses the exact same free core/ toolkit as your original 10 channels — if you already set up Groq, Pixabay, and YouTube OAuth for those, skip to Part 2."),
    h2("1. Install dependencies"),
    codeText(["cd faceless_automation", "python3 -m pip install -r requirements.txt"]),
    h2("2. Free script-writing key (Groq)"),
    numbered("https://console.groq.com → sign up free → API Keys → create key."),
    codeText(["export GROQ_API_KEY=\"your-key-here\""]),
    h2("3. Free visuals — no key needed for this channel's AI art"),
    p("This channel uses Pollinations.ai for AI-generated visuals — zero signup, zero key, nothing to configure.", { italics: true, color: "555555" }),
    h2("4. One-time YouTube upload authorization (per channel/account)"),
    numbered("https://console.cloud.google.com → new project → enable “YouTube Data API v3”."),
    numbered("OAuth consent screen → External → add this channel's Google account as a test user."),
    numbered("Credentials → OAuth client ID → Desktop app → download JSON → save as client_secret.json."),
    numbered("First run with --upload opens a browser to authorize once; silent after that."),
  ];
}

function channelSpecific(ch) {
  const runCmd = `python3 -m channels_highpay.${ch.folder}.run`;
  return [
    h1("Part 2 — This Channel's Setup"),
    h2("What this channel is"),
    p(ch.description),
    h2("Why it's a stronger bet than the mythology/history/space channels"),
    p(ch.whyBetter),
    h2("Content style / prompt"),
    p("Edit anytime in channels_highpay/" + ch.folder + "/config.py:", { italics: true, color: "555555" }),
    codeText(wrapLines(ch.systemPrompt, 90)),
    h2("Example topics in the rotation"),
    ...ch.topics.map((t) => bullet(t)),
    h2("Voice & visuals"),
    infoTable([
      ["TTS voice", ch.voice],
      ["Visual source", ch.visualSourceLabel],
      ["Video shape", ch.vertical ? "Vertical 1080×1920 (Shorts)" : "Horizontal 1920×1080 (long-form)"],
    ]),
    h1("Part 3 — Generating an Episode"),
    codeText([runCmd + "                      # generate only, review first"]),
    codeText([runCmd + " --upload             # generate + upload"]),
    codeText([runCmd + ' --topic "..."         # force a specific topic']),
    h1("Part 4 — Posting Schedule"),
    infoTable([
      ["Suggested cadence", ch.cadence],
      ["Best posting time (IST)", ch.postTime],
    ]),
    h1("Part 5 — Notes"),
    ...ch.notes.map((n) => bullet(n)),
    new Paragraph({ text: "", pageBreakBefore: true }),
  ];
}

function wrapLines(text, width) {
  const words = text.split(" ");
  const lines = []; let cur = "";
  for (const w of words) {
    if ((cur + " " + w).trim().length > width) { lines.push(cur.trim()); cur = w; }
    else cur = (cur + " " + w).trim();
  }
  if (cur) lines.push(cur);
  return lines;
}

const CHANNELS = [
  {
    folder: "hp01_betrayal_revenge", emoji: "\u{1F4A5}", display: "Betrayal & Revenge Stories", rpm: "$12.82", competition: "Low",
    tagline: "The single highest-RPM, fastest-growing faceless niche in this research — proven viral story format.",
    vertical: true,
    description: "First-person 'confession' style stories about betrayal (cheating, backstabbing, scheming family members) with a satisfying karmic twist ending. This is the reddit-story-narration format that dominates faceless Shorts right now.",
    whyBetter: "Growth rate ~21x vs the low-single-digit growth of mythology/history channels in the same research, plus meaningfully higher RPM. The format is also inherently more shareable — people send revenge/betrayal stories to friends, which mythology explainers rarely trigger.",
    systemPrompt: "You write a viral first-person 'reddit confession' style story about betrayal and a satisfying karmic payoff (a cheating partner exposed, a backstabbing friend or coworker caught, a family member's scheme unraveling). Write 180-220 words: a clear setup, rising tension, and a satisfying twist or comeuppance ending. Sound like a real anonymous confession — plain, specific, emotionally honest — never like a lecture or moral. No real names, keep it clearly a story, not targeting any real identifiable person.",
    topics: ["A maid of honor who stole the wedding date and got exposed at the reception", "A coworker who took credit for a project until the client called out the truth", "A roommate who secretly rented out the apartment until the landlord found out", "A sibling who forged a parent's signature on an inheritance document", "A business partner who was skimming money until the accountant noticed"],
    voice: "en-US-GuyNeural (deep, dramatic)", visualSourceLabel: "AI-generated cinematic photorealistic scenes (Pollinations.ai, free)",
    cadence: "1/day — this format supports high posting frequency without feeling repetitive.",
    postTime: "7-9 PM IST",
    notes: [
      "Keep every story clearly fictionalized — no real names, no identifiable real people, frame as ‘a story’ not a real report about someone specific.",
      "This is the format most likely to get you views fast, but also has more channels competing for attention than mythology — differentiate with a consistent voice/thumbnail style.",
      "Watch retention graphs in YouTube Studio closely on your first 10 videos — if people drop off before the twist, tighten the setup section in config.py's system prompt.",
    ],
  },
  {
    folder: "hp02_court_drama", emoji: "⚖️", display: "Court Drama Stories", rpm: "$9.03", competition: "Low",
    tagline: "High-retention legal drama format, low competition, easy to keep fresh.",
    vertical: true,
    description: "Fictionalized courtroom stories — small claims disputes, wild legal cases, decisive judge rulings — with tension and a satisfying resolution.",
    whyBetter: "Low competition (fewer faceless channels have saturated this vs. mainstream true crime), and the courtroom-tension structure has consistently strong retention on Shorts.",
    systemPrompt: "You write a viral first-person 'courtroom story' script — a small claims dispute, a wild legal case, or a judge calling out an obviously dishonest party. Write 180-220 words with a clear conflict, a tense back-and-forth, and a decisive, satisfying ruling. Plausible and specific, never a real identifiable case or person — write it as a fictionalized dramatization.",
    topics: ["A small claims case over a neighbor's fence built two feet into the wrong yard", "A landlord suing a tenant who then produced texts proving retaliation", "A dispute over a wedding photographer who never delivered the photos", "A dog walker sued after a dog went missing, then video evidence changed everything", "A contractor sued for a bad renovation who had secretly recorded every conversation"],
    voice: "en-US-ChristopherNeural", visualSourceLabel: "AI-generated cinematic courtroom scenes (Pollinations.ai, free)",
    cadence: "4-5/week",
    postTime: "7-9 PM IST",
    notes: [
      "Always frame as a fictionalized dramatization — never imply it's a real documented case unless you're sourcing genuinely public-record cases and citing them.",
      "Pairs well cross-promotionally with the Karma & Justice channel — similar audience.",
    ],
  },
  {
    folder: "hp03_karma_justice", emoji: "⚖️", display: "Karma & Justice Stories", rpm: "$5.70", competition: "Medium",
    tagline: "The most proven viral story format on the internet — petty revenge / instant karma.",
    vertical: true,
    description: "Short, satisfying 'instant karma' stories — entitled customers, rude neighbors, workplace bullies getting a clean comeuppance. Lower RPM than the others but the single most reliably shareable format (AITA/pettyrevenge-style content routinely goes viral).",
    whyBetter: "Medium competition but the highest raw view-velocity potential of the set — this is the format most likely to actually deliver the 'instant views' you're after, even though its RPM is the lowest of the 8.",
    systemPrompt: "You write a viral first-person 'petty revenge' or 'instant karma' story (a rude customer, an entitled neighbor, a bully getting an unexpected comeuppance). Write 160-200 words: relatable setup, escalating rudeness or unfairness, then a clean, satisfying karmic resolution. Keep it light enough to be shareable, not mean-spirited or targeting real people.",
    topics: ["An entitled customer who demanded a refund and got caught lying on camera", "A neighbor who kept stealing parking spots until the HOA got involved", "A bully in a group chat exposed by a screenshot they forgot existed", "A coworker who mocked someone's side hustle until it became the company's biggest client", "A person who cut in line at the airport and the gate agent had the perfect response"],
    voice: "en-US-JennyNeural", visualSourceLabel: "AI-generated everyday-life dramatic scenes (Pollinations.ai, free)",
    cadence: "1/day — cheapest-feeling format to produce at volume.",
    postTime: "12-2 PM or 7-9 PM IST",
    notes: [
      "If you only start ONE of these 8 channels first to test view velocity fast, this is the one — it's the most proven mass-shareable format, even though the per-view payout is the lowest here.",
      "Keep endings light/satisfying rather than cruel — that's what makes it shareable instead of just mean.",
    ],
  },
  {
    folder: "hp04_veteran_kindness", emoji: "\u{1F396}️", display: "Veteran Kindness Stories", rpm: "$7.13", competition: "Low",
    tagline: "Feel-good format that shares heavily — low competition.",
    vertical: true,
    description: "Warm, uplifting stories of veterans receiving unexpected kindness or recognition from strangers. Emotionally different register from the revenge/karma channels — good portfolio diversity.",
    whyBetter: "Feel-good content shares at very high rates (people share things that make them feel something positive), and this specific angle has low channel saturation.",
    systemPrompt: "You write a heartfelt, uplifting true-feeling story about a veteran being shown unexpected kindness, respect, or recognition by a stranger (a free meal, an upgraded flight, a small business honoring them). Write 160-200 words, warm and sincere tone, ending on an emotional, feel-good note. Respectful and dignified — never pitying.",
    topics: ["A diner owner who quietly comps every veteran's meal on their anniversary", "A stranger at an airport who gave up a first class seat to a veteran flying home", "A young cashier who noticed a veteran's hat and paid for their groceries", "A small town that surprises a returning veteran with a welcome home parade", "A mechanic who fixed a veteran's truck for free after hearing their story"],
    voice: "en-US-ChristopherNeural", visualSourceLabel: "AI-generated warm cinematic scenes (Pollinations.ai, free)",
    cadence: "3-4/week",
    postTime: "6-8 PM IST",
    notes: [
      "Keep tone respectful and dignified, never pitying or exploitative — this audience is sensitive to anything that feels like it's using veterans for clicks.",
      "Good channel for community/comments engagement, not just raw view count.",
    ],
  },
  {
    folder: "hp05_sleep_soundscapes", emoji: "\u{1F319}", display: "Sleep & Healing Soundscapes", rpm: "$10.92", competition: "Low",
    tagline: "Near-zero editing once a template exists — reuses your ambient pipeline almost as-is.",
    vertical: false,
    description: "Long-form ambient sleep/relaxation videos (rain, calm ocean, soft night ambience) — same production pattern as your existing Nature Ambient channel, just repositioned toward sleep/healing search terms which carry higher RPM.",
    whyBetter: "Same effort as a channel you're already running, but the 'sleep/healing' framing carries meaningfully higher RPM than generic 'nature ambient' according to this research, and near-zero incremental editing per video.",
    systemPrompt: "Write ONE short on-screen title (max 10 words) for a long-form sleep/healing ambient soundscape video (rain, soft drones, deep sleep tones, healing frequencies framing). No spoken narration — just a calming title.",
    topics: ["Deep sleep rain sounds for relaxation and healing", "Calming ocean waves for stress relief and sleep", "Gentle forest ambience for deep relaxation", "Soft thunderstorm sounds for undisturbed sleep", "Peaceful night ambience with distant wind for sleep"],
    voice: "n/a (no narration)", visualSourceLabel: "Pixabay free stock video, looped to fill 30-60+ minutes",
    cadence: "2-3/week",
    postTime: "9-10 PM IST",
    notes: [
      "Don't claim actual healing/therapeutic/medical effects in titles or descriptions — keep language to 'relaxation' and 'calming', not medical claims.",
      "Make 1-hour and 8-hour versions of top performers using core/assemble.py — same source clips, longer loop, more watch-time hours toward monetization.",
    ],
  },
  {
    folder: "hp06_literary_analysis", emoji: "\u{1F4DA}", display: "Literary Analysis & Book Reviews", rpm: "$9.15", competition: "Low",
    tagline: "~10K competing channels, older/affluent audience, genuinely low saturation.",
    vertical: true,
    description: "Short breakdowns of classic novels, famous authors, and the meaning behind well-known books, aimed at a curious general audience.",
    whyBetter: "Low competition despite solid RPM — books/classic literature content hasn't been saturated by faceless channels the way finance/motivation content has.",
    systemPrompt: "You are a thoughtful literary narrator breaking down one book, author, or literary theme for a curious general audience (classic novels, famous authors' lives, the meaning behind a well-known book). Write a 160-190 word script: a hook, the core insight, and a closing thought that makes people want to read the book.",
    topics: ["The real meaning behind George Orwell's 1984", "Why The Great Gatsby's ending still divides readers", "The dark true story that inspired Mary Shelley's Frankenstein", "What Pride and Prejudice actually says about class and marriage", "Why Kafka's The Metamorphosis is still so unsettling today"],
    voice: "en-US-ChristopherNeural", visualSourceLabel: "AI-generated moody library-aesthetic scenes (Pollinations.ai, free)",
    cadence: "3-4/week",
    postTime: "7-9 PM IST",
    notes: [
      "Stick to well-documented public-domain classics at first (Orwell, Austen, Shelley, Kafka) — easiest for the LLM to stay factually accurate.",
      "Good candidate for a companion 'reading list' pinned comment or community post to build return viewers.",
    ],
  },
  {
    folder: "hp07_senior_longevity", emoji: "\u{1F33F}", display: "Senior Health & Longevity Habits", rpm: "$6.17", competition: "Low",
    tagline: "19x growth rate, underserved older-adult audience.",
    vertical: true,
    description: "General wellness and lifestyle habits linked to healthy aging (walking, sleep routines, social connection, staying active) — framed as everyday lifestyle content, not medical advice.",
    whyBetter: "Growth rate of ~19x with only a small number of channels serving this specific older-adult audience directly — most wellness content skews younger.",
    systemPrompt: "You write general wellness and longevity lifestyle content for an older adult audience — everyday habits linked to healthy aging (walking, sleep routines, social connection, balanced meals, staying mentally active). Write a 150-180 word script sharing ONE practical, non-medical lifestyle habit and why it helps healthy aging. Do not give medical advice, do not mention specific conditions, medications, or diagnoses — keep it general wellness and lifestyle only, and suggest viewers consult a doctor for personal advice.",
    topics: ["Why a short daily walk after meals supports healthy aging", "The longevity benefits of staying socially connected in later life", "How a consistent sleep routine supports healthy aging", "Why staying mentally active with new hobbies matters for older adults", "The value of stretching and light mobility work for older adults"],
    voice: "en-US-AriaNeural", visualSourceLabel: "AI-generated warm lifestyle scenes (Pollinations.ai, free)",
    cadence: "3/week",
    postTime: "8-10 AM IST",
    notes: [
      "⚠️ Hard rule: never let this channel drift into medical advice, specific conditions, or medication content — keep it strictly general lifestyle habits, and end videos suggesting viewers consult a doctor for anything personal. This is both an ethical requirement and a YouTube monetization-policy requirement (medical misinformation is demonetized/removed).",
      "Review every script before posting — this is the one channel here where getting it wrong has real downside for an older, trusting audience.",
    ],
  },
  {
    folder: "hp08_english_learning", emoji: "\u{1F1EC}\u{1F1E7}", display: "English Learning Podcast Shorts", rpm: "$11.88", competition: "Low-Medium",
    tagline: "21x growth rate, evergreen — old episodes keep earning views for years.",
    vertical: true,
    description: "Bite-sized spoken-English lessons (idioms, phrases, common mistakes) for intermediate ESL learners worldwide — one of the largest evergreen search audiences on YouTube.",
    whyBetter: "Second-highest RPM in this set, ~21x growth rate, and genuinely evergreen — a lesson on 'make vs do' is just as useful in three years, so your back catalog keeps compounding views instead of going stale like news-adjacent content would.",
    systemPrompt: "You write a short spoken-English learning lesson for intermediate ESL learners. Teach ONE common phrase, idiom, or grammar point: explain it in very simple English, give 2 example sentences, and note when to use it. Write 120-150 words, warm and encouraging teacher tone, simple vocabulary.",
    topics: ["The phrase 'get the hang of it' and how to use it naturally", "The difference between 'make' and 'do' in everyday English", "The idiom 'hit the books' and when native speakers use it", "How to politely disagree in English using softening phrases", "The phrasal verb 'look forward to' and common mistakes learners make"],
    voice: "en-US-JennyNeural (clear, friendly)", visualSourceLabel: "AI-generated clean educational illustrations (Pollinations.ai, free)",
    cadence: "1/day — this format rewards volume since each video is a standalone evergreen lesson.",
    postTime: "6-8 AM IST (also strong across other timezones — global audience)",
    notes: [
      "Huge global search volume for 'learn english' content — genuinely one of the largest evergreen niches on YouTube.",
      "Consider grouping episodes into themed playlists (idioms, phrasal verbs, business English) — ESL audiences binge-watch by theme.",
    ],
  },
];

async function main() {
  const outDir = path.join(__dirname, "output_docs_highpay");
  fs.mkdirSync(outDir, { recursive: true });

  const summary = researchSummaryDoc();
  fs.writeFileSync(path.join(outDir, "00_Niche_Research_Summary.docx"), await Packer.toBuffer(summary));
  console.log("wrote 00_Niche_Research_Summary.docx");

  let i = 1;
  for (const ch of CHANNELS) {
    const doc = new Document({
      numbering,
      sections: [{
        properties: { page: { size: PAGE, margin: { top: 1000, bottom: 1000, left: 1100, right: 1100 } } },
        children: [
          ...titlePage(ch),
          ...commonSetup(),
          ...channelSpecific(ch),
        ],
      }],
    });
    const buf = await Packer.toBuffer(doc);
    const filename = `HP${String(i).padStart(2, "0")}_${ch.folder.replace(/^hp\d+_/, "")}.docx`;
    fs.writeFileSync(path.join(outDir, filename), buf);
    console.log("wrote", filename);
    i++;
  }
}

main();
