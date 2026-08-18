# Free Faceless YouTube Automation — 11 Active Channels (18 built)

100% free-tier Python toolkit for automated faceless YouTube channels.
18 channels' worth of code exists (10 original + 8 higher-RPM additions),
but the **active pilot running right now is 11**: all 8 higher-RPM channels
plus 3 kept from the original 10, chosen for reach/format diversity. Script
generation, voice, real stock **video** visuals + burned-in subtitles, and
upload — all free tools, no paid subscriptions required.

**Running the 11-niche pilot 24x7 for free?** Start with
[`SETUP.md`](SETUP.md) — it's the one-time manual checklist (create the 11
channels, get free API keys — Pixabay/Pexels can be reused from the sibling
`peace_reels_automation` project's `.env` — authorize each channel) that
wires this up to run daily on GitHub Actions (no PC left on), with a live
comparison dashboard at `docs/index.html` (published via GitHub Pages) so
you can see which niches are winning, with a plan to keep the top 3
long-term.

**Two channel sets, kept separate on purpose:**
- `channels/` — the original 10 (mythology, history, ASMR, quiz, space). Only
  3 are currently active in the pilot — `ch01_ai_asmr`, `ch03_hindu_mythology`,
  `ch06_eastern_philosophy` (see `scripts/registry.py`) — upgraded from AI
  still images to real stock video ("mixed"/"pixabay_video") to match the
  quality bar below. The other 7 still exist, just not in the active registry.
- `channels_highpay/` — 8 channels added Aug 2026, picked for higher RPM, lower
  competition, and faster view velocity (mostly first-person story-narration formats:
  betrayal/revenge, court drama, karma, veteran kindness, plus sleep soundscapes,
  literary analysis, senior wellness, and English learning). All 8 already used
  real stock video from the start. **Read
  `channel_docs_highpay/00_Niche_Research_Summary.docx` first** — it explains the
  research behind these picks and an honest note on the two Reddit threads that
  couldn't be fetched directly (Reddit blocked this tool both times).

## What's in here

- `core/` — shared toolkit used by ALL 18 channels (do not duplicate per channel):
  - `llm.py` — free script generation (Groq API, free tier; falls back to keyless Pollinations.ai)
  - `tts.py` — free narration voice + auto-generated captions (edge-tts, no key needed)
  - `visuals.py` — free stock video/images (Pixabay, free key) + free AI image generation (Pollinations.ai, no key)
  - `assemble.py` — free local video assembly with MoviePy (Ken Burns pans, burned-in captions)
  - `upload.py` — free YouTube upload via the official YouTube Data API v3
  - `pipeline.py` — glues all of the above into one `run_episode()` call
- `channels/ch01_ai_asmr/` … `channels/ch10_space_documentary/` — the original 10.
- `channels_highpay/hp01_betrayal_revenge/` … `channels_highpay/hp08_english_learning/`
  — the 8 new higher-RPM channels. Same `config.py` + `run.py` pattern, same `core/`.
- `channel_docs/` — one Word doc per original channel.
- `channel_docs_highpay/` — one Word doc per new channel, plus
  `00_Niche_Research_Summary.docx` (read this one first).
- `generate_channels.py` / `generate_highpay_channels.py` — regenerate either
  channel set's `config.py` + `run.py` files from one place if you want to tweak
  many channels at once.
- `requirements.txt`, `.env.example` — dependencies and free API key placeholders.

## Quick start

```bash
pip install -r requirements.txt
cp .env.example .env        # fill in your free GROQ_API_KEY / PIXABAY_API_KEY, then:
export $(cat .env | xargs)

# generate one video for a channel (no upload yet — review it first)
python3 -m channels.ch01_ai_asmr.run
python3 -m channels_highpay.hp01_betrayal_revenge.run

# once you're happy with the output, upload it
python3 -m channels.ch01_ai_asmr.run --upload
python3 -m channels_highpay.hp01_betrayal_revenge.run --upload
```

Every channel folder works the same way — swap the folder name for any of the
other active 10 (see `scripts/registry.py` for the full list of 11). Full
step-by-step setup (including how to get each free API key and set up
YouTube upload) is in each channel's Word doc under `channel_docs/` or
`channel_docs_highpay/`.

## The active pilot: 11 channels

All 11 now share the same rendering engine as `peace_reels_automation`:
Kokoro TTS (local, free neural voice — replacing edge-tts), real stock
**video** clips only via `core/visuals.py::fetch_stock_videos` (Pexels
first, Pixabay fallback — no AI still images anywhere in the active set),
normalized/color-graded/concatenated with ffmpeg
(`core/video_builder.py`), and ASS subtitles burned in via ffmpeg's `ass=`
filter (`core/captions.py`) — properly timed to line length, wrapped,
faded in/out, with outline/shadow styling, instead of the old MoviePy
plain-white `TextClip` captions.

### The 8 high-RPM channels (added Aug 2026)

| # | Folder | Niche | Est. RPM |
|---|---|---|---|
| 1 | hp01_betrayal_revenge | Betrayal & revenge stories | $12.82 |
| 2 | hp02_court_drama | Court drama stories | $9.03 |
| 3 | hp03_karma_justice | Karma & justice (petty revenge) stories | $5.70 |
| 4 | hp04_veteran_kindness | Veteran kindness stories | $7.13 |
| 5 | hp05_sleep_soundscapes | Sleep & healing soundscapes | $10.92 |
| 6 | hp06_literary_analysis | Literary analysis & book reviews | $9.15 |
| 7 | hp07_senior_longevity | Senior health & longevity habits | $6.17 |
| 8 | hp08_english_learning | English learning podcast shorts | $11.88 |

See `channel_docs_highpay/00_Niche_Research_Summary.docx` for the sourcing
behind these RPM figures and why they were chosen over the original 10.

### 3 kept from the original 10 (upgraded to video)

| # | Folder | Niche | Format |
|---|---|---|---|
| 9 | ch01_ai_asmr | AI ASMR (soap/slime/glass) — real stock video | Shorts |
| 10 | ch03_hindu_mythology | Hindu mythology — now real video + AI stills mixed | Shorts |
| 11 | ch06_eastern_philosophy | Zen/Tao/Buddhism — now real video + AI stills mixed | Shorts |

### The other 7 (built, currently inactive)

`ch02_nature_ambient`, `ch04_geography_quiz`, `ch05_norse_sagas`,
`ch07_egyptian_mythology`, `ch08_ai_cooking_asmr`, `ch09_forgotten_empires`,
`ch10_space_documentary` — code still exists under `channels/`, just not
listed in `scripts/registry.py`, so they don't publish or show on the
dashboard. Add them back to the registry (and the workflow matrix) any time.

## Important notes

- **This code was written and smoke-tested in a sandboxed environment with
  restricted outbound network access**, so the live API calls (Groq, Pixabay,
  edge-tts, YouTube) could not be executed end-to-end here. The local video
  assembly step (`core/assemble.py`, the part with the most moving pieces) WAS
  verified end-to-end with synthetic audio/images and produced a correct
  1080×1920 MP4 with burned-in captions. Run the network-dependent steps once
  on your own machine to confirm your API keys are wired correctly.
- Each channel needs its own free Google Cloud OAuth setup for upload — see
  Part 1, Step 4 of any channel's Word doc.
- Review output before posting, especially for the mythology/history/space
  channels — treat this as assisted automation, not unsupervised publishing,
  until you've seen enough episodes to trust the prompts.
