# Hook sound effects

Short (<=3.5s) attention-grabbing stingers mixed in at t=0 of every episode
(see `core/pipeline.py::_pick_intro_sfx` and
`core/video_builder.py::build_final_video`'s `intro_sfx_path` param) — a
random one is picked per episode. This is the audio equivalent of the
"scroll-stopping hook" instruction already in every channel's script
system_prompt: a sudden, punchy sound in the first second to stop a thumb
mid-scroll, the same trick meme/reaction clips use.

Sourced from https://mixkit.co/free-sound-effects/ (free for commercial use,
no attribution required, no account needed — confirmed via Mixkit's own
license page, 2026-09-12). Do NOT add files scraped from sites whose terms
don't clearly allow redistribution/commercial reuse (e.g. myinstants.com has
no bulk-download API and unclear reuse terms per clip) — stick to Mixkit,
Pixabay's sound-effects section, or freesound.org clips explicitly marked
CC0.

To add more: browse a mixkit.co/free-sound-effects/<category>/ page, note
the sound's `-preview.mp3` URL (right-click the waveform player -> or view
page source and search for `preview-url-value`), and drop the downloaded
file here. Keep each clip short (under ~3s) — this plays under the
narration's opening line, not instead of it.

Set `config["hook_sfx"] = False` on a channel to disable (already the
default for any channel with `keep_background_audio: True`, e.g.
ch01_ai_asmr, where the real trigger-sound audio is the content and an
unrelated stinger would just compete with it).
