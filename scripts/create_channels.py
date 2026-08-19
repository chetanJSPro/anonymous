"""
One-time local script: create the remaining YouTube channels on your Google
account. Zero AI involved -- plain Playwright automation, deterministic
clicks. Attaches to your REAL logged-in Chrome (via remote debugging) so it
uses your real session instead of a fresh automated login.

Setup (once):
    pip install playwright

Run (Chrome must already be open with --remote-debugging-port=9222 and you
must already be signed into the target Google account -- verified manually):
    python scripts/create_channels.py

All 11 channels created manually as of 2026-08-19 -- this script is no
longer needed, kept only for reference.
"""

import sys
import time
from playwright.sync_api import sync_playwright

CHANNEL_NAMES = [
    # ("display name", "handle", "already exists?")
    ("Told You So", "hp01_betrayal_revenge", True),
    ("Order In The Court", "hp02_court_drama", True),
    ("Instant Karma", "hp03_karma_justice", True),
    ("Salute", "hp04_veteran_kindness", False),
    ("Deep Sleep Sounds", "hp05_sleep_soundscapes", False),
    ("Between The Lines", "hp06_literary_analysis", False),
    ("Live Longer", "hp07_senior_longevity", False),
    ("Speak Fluent English", "hp08_english_learning", False),
    ("Satisfying Cuts", "ch01_ai_asmr", False),
    ("Sacred Stories", "ch03_hindu_mythology", False),
    ("Still Mind", "ch06_eastern_philosophy", False),
]


def create_one_channel(page, name: str, handle: str):
    page.goto("https://www.youtube.com/channel_switcher", wait_until="domcontentloaded")
    time.sleep(1.5)
    page.get_by_text("Create a channel", exact=False).click()
    time.sleep(1.5)
    page.get_by_placeholder("Name").fill(name)
    time.sleep(0.3)
    try:
        page.get_by_placeholder("Handle").fill(handle)
        time.sleep(0.3)
    except Exception:
        pass  # handle field is optional / may already be auto-filled
    page.get_by_role("button", name="Create channel").click()
    time.sleep(3)
    print(f"  created: {name} (@{handle})")


def main():
    with sync_playwright() as p:
        try:
            browser = p.chromium.connect_over_cdp("http://localhost:9222")
        except Exception as e:
            print("Could not attach to Chrome on port 9222.")
            print(f"Details: {e}")
            sys.exit(1)

        context = browser.contexts[0] if browser.contexts else browser.new_context()
        page = context.new_page()

        todo = [(n, h) for n, h, exists in CHANNEL_NAMES if not exists]
        print(f"{len(todo)} channels left to create "
              f"({len(CHANNEL_NAMES) - len(todo)} already exist, skipping)")

        for i, (name, handle) in enumerate(todo, 1):
            print(f"[{i}/{len(todo)}] creating: {name}")
            try:
                create_one_channel(page, name, handle)
            except Exception as e:
                print(f"  FAILED on '{name}': {e}")
                print("  Inspect the open tab, adjust the selector, then re-run "
                      "(safe to re-run -- mark completed ones True in CHANNEL_NAMES).")
                sys.exit(1)

        print("\nDone. Verify at https://www.youtube.com/channel_switcher")


if __name__ == "__main__":
    main()
