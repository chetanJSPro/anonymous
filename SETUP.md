# Setup checklist — 11-niche pilot, one Google account, 24x7 via GitHub Actions

Everything code-side is done. What's left are steps that need YOUR login —
I can't click through Google/GitHub UI on your behalf. Work through this in
order; each step says how long it takes. Total: ~1.5–2 hours, once.

Read `channel_docs_highpay/00_Niche_Research_Summary.docx` for why the 8
`hp0X` niches were picked, and each `channel_docs_highpay/HP0X_*.docx` /
`channel_docs/Channel_0X_*.docx` for that channel's specific setup notes.

**Why 11:** the 8 `hp0X` story channels (highest researched RPM) plus 3 kept
from the original 10 (`ch01_ai_asmr`, `ch03_hindu_mythology`,
`ch06_eastern_philosophy` — picked for reach/format diversity: fast-growth
ASMR, and two spiritual niches that pair well with the peace_reels_automation
audience). All 11 now use `visual_source: "mixed"` (or `pixabay_video` for
ch01) — real stock **video**, not AI still images — plus burned-in subtitles,
same quality bar across the board. The other 7 in `channels/` still exist but
are inactive (not in `scripts/registry.py`) — the plan is to run these 11,
compare the dashboard after the pilot window, and keep the top 3.

---

## 1. Create 11 channels on your one Google account (~20 min)

On YouTube (signed into your one Google account): profile picture →
**Settings → Add or manage your channel(s) → Create a new channel**. Do
this 11 times. Suggested names (edit freely):

| Folder | Suggested channel name |
|---|---|
| hp01_betrayal_revenge | e.g. "Told You So" |
| hp02_court_drama | e.g. "Order In The Court" |
| hp03_karma_justice | e.g. "Instant Karma" |
| hp04_veteran_kindness | e.g. "Salute" |
| hp05_sleep_soundscapes | e.g. "Deep Sleep Sounds" |
| hp06_literary_analysis | e.g. "Between The Lines" |
| hp07_senior_longevity | e.g. "Live Longer" |
| hp08_english_learning | e.g. "Speak Fluent English" |
| ch01_ai_asmr | e.g. "Satisfying Cuts" |
| ch03_hindu_mythology | e.g. "Sacred Stories" |
| ch06_eastern_philosophy | e.g. "Still Mind" |

Each is a separate channel, all owned by your one Google account — no extra
Gmail signups needed.

## 2. Get free API keys (~5 min)

- **Groq** (script generation, required): https://console.groq.com → API Keys → create key.
  Unique to this project — the sibling `peace_reels_automation` project doesn't use Groq.
- **Pexels** (real stock video, recommended): https://www.pexels.com/api/ → instant key, no approval wait.
- **Pixabay** (real stock video, recommended as a 2nd source): https://pixabay.com/accounts/register/
  → your account → API docs page has your key. **If you already run
  `peace_reels_automation`, reuse its `PIXABAY_API_KEY`/`PEXELS_API_KEY`
  values from that project's `.env` instead of registering again** — same
  free-tier key works for both projects, just paste the same value into
  this project's `.env`.
- **Agnes AI** (optional, real AI-generated video clips, 6 of 8 per episode
  by default — the majority of each video's visuals): https://agnes-ai.com →
  sign up → API key. Free tier, ~16 requests/min shared across all callers,
  so under load (e.g. 4 channels publishing in parallel) some clips will
  silently fall back to stock video rather than actually hit that limit.
  Leave the key blank and every channel just runs on 100% stock video —
  nothing breaks without it.

All 11 channels use `visual_source: "mixed"` (real stock video clips from
Pexels, falling back to Pixabay, interleaved with a couple of AI-generated
images for shots stock footage can't cover) or `pixabay_video` for
`ch01_ai_asmr` (real ASMR footage only, no AI stills needed there). Without
either stock key it still works for the "mixed" channels — falls back to AI
images only — but the whole point of this upgrade is real video, so add at
least one stock key before running for real.

Keep both handy for step 6.

## 3. Three Google Cloud projects for YouTube API quota (~20 min)

YouTube's free upload quota is 10,000 units/day **per Google Cloud project**,
and one upload costs ~1,600 units — so 11 uploads/day from one project would
run out. Splitting into 3 projects (4 + 4 + 3 channels, ~6,400 / 6,400 /
4,800 units/day) keeps everyone comfortably under the limit.

Repeat this three times (call them Project A → hp01–04, Project B → hp05–08,
Project C → ch01, ch03, ch06):

1. https://console.cloud.google.com/ → New Project.
2. **APIs & Services → Library** → enable **YouTube Data API v3** AND
   **YouTube Analytics API** (the dashboard needs the second one).
3. **APIs & Services → OAuth consent screen** → External → fill app name
   (anything) → add your Google account's email as a **test user**. Unverified
   apps are fine for personal use, this just means only test users can
   authorize it.
4. **Credentials → Create Credentials → OAuth client ID → Desktop app** →
   download the JSON.
5. Rename the downloads `client_secret_a.json`, `client_secret_b.json`, and
   `client_secret_c.json` and put all three in this project's root folder
   (next to `requirements.txt`).

## 4. Install locally + authorize each channel (~25 min)

This step needs a real browser, so it must run on your PC, once, per channel.

```bash
pip install -r requirements.txt
python scripts/generate_token.py hp01_betrayal_revenge
python scripts/generate_token.py hp02_court_drama
python scripts/generate_token.py hp03_karma_justice
python scripts/generate_token.py hp04_veteran_kindness
python scripts/generate_token.py hp05_sleep_soundscapes
python scripts/generate_token.py hp06_literary_analysis
python scripts/generate_token.py hp07_senior_longevity
python scripts/generate_token.py hp08_english_learning
python scripts/generate_token.py ch01_ai_asmr
python scripts/generate_token.py ch03_hindu_mythology
python scripts/generate_token.py ch06_eastern_philosophy
```

Each command opens a browser — **sign in and pick the matching channel** (the
account chooser shows all channels on your Google account; pick the right one
each time). This produces `token_hp0X_....json` files — these are what let
the automation post as that specific channel without asking again.

## 5. Push this project to a GitHub repo

This project is already pushed to a private staging repo named `anonymous`.
To run it under a different/second GitHub account: on that account, either
accept a collaborator invite to the `anonymous` repo, or use GitHub's
**Import repository** / **Transfer ownership** to move it there, then clone
it locally on whichever machine will run Claude Code for the rest of setup.
The commit history has no personal names/emails in it by design.

## 6. Upload your keys as GitHub secrets (~5 min)

This keeps every key out of the code and out of this chat. From the project
folder, with `client_secret_a.json`, `client_secret_b.json`,
`client_secret_c.json`, and all 11 `token_*.json` files present:

```bash
python scripts/make_secret_commands.py > set_secrets.sh
bash set_secrets.sh
rm set_secrets.sh
gh secret set GROQ_API_KEY --body "YOUR_GROQ_KEY_HERE"
gh secret set PEXELS_API_KEY --body "YOUR_PEXELS_KEY_HERE"
gh secret set PIXABAY_API_KEY --body "YOUR_PIXABAY_KEY_HERE"
gh secret set AGNES_API_KEY --body "YOUR_AGNES_KEY_HERE"   # optional
```

## 7. Turn on GitHub Pages for the dashboard (~2 min)

Repo → **Settings → Pages** → Source: **Deploy from a branch** → Branch:
`main` (or `master`, whichever this repo uses), folder **/docs** → Save.
Your dashboard will be live at `https://<account>.github.io/<repo>/` within
a minute or two (it'll say "no data yet" until the first analytics run).

## 8. Test before trusting the schedule (~10 min)

Repo → **Actions** tab →
- Run **"Publish niche episodes"** manually (▶ Run workflow), with a single
  `channel` input, `upload: false` first, to confirm generation works without
  posting anything. Then try one with `upload: true`.
- Run **"Update dashboard stats"** manually once uploads exist, then check
  the Pages URL updates.

Once both work, you're done — `publish.yml` runs daily at 03:00 UTC (1 new
video per channel), `analytics.yml` at 05:00 UTC (refreshes the dashboard).
Both run in GitHub's cloud — your PC can be off.

## After the 2-week pilot

The dashboard tracks views, watch time, subs gained, and estimated revenue
(views × RPM assumption) per niche from day 1. To drop underperformers:
delete their entry from `scripts/registry.py`'s `CHANNEL_MODULES` list and
their line from the `matrix.channel` list in
`.github/workflows/publish.yml` — the dashboard keeps their historical data
for comparison, it just stops publishing new episodes for them.
