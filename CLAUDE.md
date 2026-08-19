# Project: 11-niche faceless YouTube automation (pilot)

This repo is a complete, working automation for 11 faceless YouTube channels
("niches") on one Google account, meant to run 24x7 via GitHub Actions (free
tier) with zero paid tools. A 2-week performance dashboard compares the 11
niches so the underperformers can be dropped after the trial (aiming to keep
the top 3 for the long-term "high quality" tier).

The 11 = the original 8 `channels_highpay/hp0X` story channels (highest
researched RPM) + 3 kept from the original 10 in `channels/`
(`ch01_ai_asmr`, `ch03_hindu_mythology`, `ch06_eastern_philosophy` — the
other 7 in `channels/` still exist but are inactive, i.e. not listed in
`scripts/registry.py`). All 11 use real stock **video** (`visual_source:
"mixed"` or `"pixabay_video"`) with burned-in subtitles — the 3 `ch0X`
channels were just upgraded off AI still images to match. `PIXABAY_API_KEY`/
`PEXELS_API_KEY` in this project's `.env` are meant to be the same values as
the sibling `peace_reels_automation` project's `.env` (same free-tier keys,
no need to register twice) — `GROQ_API_KEY` is unique to this project.

**Read [`SETUP.md`](SETUP.md) first — it is the authoritative, ordered
checklist.** This file is oriented at you (Claude Code), running on whatever
machine/account this repo has now been copied to, to help the human finish
the parts of SETUP.md that need their login.

## What already exists (do not rebuild)

- `core/` — shared pipeline: `llm.py` (Groq, free tier — the model default
  was already fixed once when `llama-3.3-70b-versatile` got deprecated;
  if Groq calls 404 on a model, call the Groq `/v1/models` endpoint and
  update `GROQ_MODEL` in `core/llm.py`; the free keyless Pollinations
  fallback stopped actually being free — 402 Payment Required as of Aug
  2026 — so `GROQ_API_KEY` is effectively required now), `tts_kokoro.py`
  (`tts_chatterbox.py`, Chatterbox TTS — MIT license, commercial-safe,
  primary voice engine; `tts_kokoro.py` is the automatic fallback if
  Chatterbox fails/times out — the peace_reels_automation voice engine,
  needs espeak-ng on the OS. Do NOT add XTTS-v2: its weights are CPML,
  non-commercial-only, and Coqui Inc shut down so there's no commercial
  license to buy anymore — a real problem for these ad-monetized channels),
  `visuals.py::fetch_hybrid_stock_agnes_videos`
  (used by pipeline.py: mostly real AI-generated clips via Agnes AI —
  6 of 8 per episode by default, `agnes_clip_count` in pipeline.py — optional,
  needs AGNES_API_KEY, silently falls back to 100% stock if unset or it
  fails/rate-limits — topped up with `fetch_stock_videos`, Pexels first,
  Pixabay fallback),
  `captions.py` + `video_builder.py` (ported from peace_reels_automation:
  ffmpeg-based background build with color grading + ASS subtitle burn-in
  via ffmpeg's `ass=` filter), `upload.py` + `auth.py` (YouTube Data +
  Analytics API OAuth). `pipeline.py` wires all of this together — see its
  docstring. The old `tts.py` (edge-tts) and `assemble.py` (MoviePy) are
  unused dead code now, kept only in case of rollback.
- `channels_highpay/hp01..hp08/` + `channels/ch01_ai_asmr`,
  `channels/ch03_hindu_mythology`, `channels/ch06_eastern_philosophy` — the
  11 active niche channels' configs. Each has `client_secret_file` (split
  across three Google Cloud projects: `client_secret_a.json` for hp01–04,
  `client_secret_b.json` for hp05–08, `client_secret_c.json` for the 3
  `ch0X` channels, to stay under YouTube's daily upload quota), and
  `channel_token_file`.
- `scripts/registry.py` — the single source of truth listing the 11 active
  channels. Drop a channel here (and from the workflow matrix) to retire it.
- `scripts/generate_token.py` — interactive, local-only OAuth (needs a
  browser — never run in CI).
- `scripts/write_secrets.py` / `make_secret_commands.py` — turn local
  secret files into GitHub Actions secrets (base64-encoded env vars) without
  ever printing key material to a terminal transcript.
- `scripts/publish.py` — generate (+ optionally upload) one episode for one
  channel; used by `.github/workflows/publish.yml` (daily cron, 03:00 UTC).
- `scripts/fetch_analytics.py` — pulls YouTube Analytics into
  `docs/data/stats.json`; used by `.github/workflows/analytics.yml` (daily
  cron, 05:00 UTC), which also commits the updated stats file.
- `docs/index.html` — the dashboard (static page, no build step, reads
  `docs/data/stats.json` at runtime). Served via GitHub Pages from `/docs`.
- `scripts/generate_previews.py` — generates 2 sample episodes per niche
  locally (no upload, no OAuth) so output quality can be reviewed before
  trusting the schedule. Useful any time output quality is in question.

## What you're here to do

1. If secrets/tokens/channels don't exist yet on this account: walk the
   human through `SETUP.md` steps 1–4 (create 11 YouTube channels, get free
   Groq + Pixabay/Pexels keys — Pixabay/Pexels can be reused from the sibling
   `peace_reels_automation` project's `.env` — set up 3 Google Cloud OAuth
   projects, run `scripts/generate_token.py` per channel — **that one needs
   their browser, you can't do it for them**).
2. Once secrets exist locally, do steps 5–8 for them: push/confirm the repo,
   run `scripts/make_secret_commands.py` and the resulting `gh secret set`
   commands, enable GitHub Pages on `/docs`, and trigger both workflows once
   via `workflow_dispatch` to confirm they work before trusting the cron.
3. If asked to preview output quality first, run
   `python scripts/generate_previews.py` (needs `GROQ_API_KEY` in the
   environment; `PIXABAY_API_KEY`/`PEXELS_API_KEY` for real stock video on
   all "mixed"-source channels, otherwise those fall back to AI stills) and
   report back which of the 22 videos succeeded/failed and why.
4. After the 2-week pilot, when the human decides which niches to keep:
   remove the dropped ones from `scripts/registry.py`'s `CHANNEL_MODULES`
   and from the `matrix.channel` list in
   `.github/workflows/publish.yml` — leave their historical rows in
   `docs/data/stats.json` alone (the dashboard just stops publishing new
   episodes for them, keeps the comparison history).

## Known gotchas already hit once (save yourself the retry)

- Groq/Pollinations requests need an explicit `User-Agent` header or some
  networks/Cloudflare 403 them — already fixed in `core/llm.py`, don't
  revert it.
- `output/` fills up fast (video files) — it's gitignored on purpose, never
  force-add it.
- Never commit `client_secret*.json`, `token_*.json`, or `.env` — `.gitignore`
  already excludes them; if `git status` ever shows one of these as
  untracked-but-about-to-be-added, stop and check `.gitignore` before
  committing.
