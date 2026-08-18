"""
registry.py — single source of truth for "the 11 niche channels" used by
every automation/analytics script. Add/remove a channel here and every
script (publish workflow, analytics fetch, dashboard, previews) picks it up.

11 = the original 8 higher-RPM story channels (channels_highpay/, already
video-based via visual_source="mixed") + 3 kept from the original 10
(channels/ch01_ai_asmr, ch03_hindu_mythology, ch06_eastern_philosophy —
upgraded from AI-still images to "mixed" real stock video + burned-in
subtitles, same quality bar as the rest). The other 7 in channels/ are
left in place but inactive (not in this list) — re-add any of them here
if you want to run more than 11 at once.

client_secret_file is split across THREE Google Cloud OAuth projects to
stay under YouTube's 10,000 units/day upload quota (~1,600 units/upload):
  client_secret_a.json -> hp01-04   (4 channels, ~6,400 units/day)
  client_secret_b.json -> hp05-08   (4 channels, ~6,400 units/day)
  client_secret_c.json -> ch01, ch03, ch06   (3 channels, ~4,800 units/day)
"""

import importlib

CHANNEL_MODULES = [
    "channels_highpay.hp01_betrayal_revenge.config",
    "channels_highpay.hp02_court_drama.config",
    "channels_highpay.hp03_karma_justice.config",
    "channels_highpay.hp04_veteran_kindness.config",
    "channels_highpay.hp05_sleep_soundscapes.config",
    "channels_highpay.hp06_literary_analysis.config",
    "channels_highpay.hp07_senior_longevity.config",
    "channels_highpay.hp08_english_learning.config",
    "channels.ch01_ai_asmr.config",
    "channels.ch03_hindu_mythology.config",
    "channels.ch06_eastern_philosophy.config",
]


def all_channels():
    """Returns a list of CONFIG dicts for all 11 active niche channels."""
    return [importlib.import_module(m).CONFIG for m in CHANNEL_MODULES]


def get_channel(name):
    for cfg in all_channels():
        if cfg["name"] == name:
            return cfg
    raise KeyError(f"no channel named {name!r} in registry")
