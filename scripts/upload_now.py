"""
upload_now.py — manual one-off "generate + upload this channel's episode
right now" runner. Bypasses GitHub Actions entirely: runs the exact same
core.pipeline.run_episode used by the daily cron, but on YOUR machine, using
the .env / client_secret_*.json / token_*.json files already sitting in
this repo root. Prints the real YouTube URL when it's done.

Usage:
    python scripts/upload_now.py hp01_betrayal_revenge
    python scripts/upload_now.py hp01_betrayal_revenge --unlisted   # test without going public
    python scripts/upload_now.py --all                              # all 11, one after another

Requires the same local setup as GitHub Actions has via secrets: .env with
GROQ_API_KEY/PIXABAY_API_KEY/PEXELS_API_KEY/AGNES_API_KEY, plus
client_secret_a/b/c.json and all 11 token_<channel>.json in the repo root.
"""

import argparse
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


def _load_env_file(path=None):
    """Tiny, dependency-free .env loader — only sets vars not already in
    the real environment, so an explicit `set FOO=bar` still wins. MUST run
    before importing anything under core/ -- several modules (core/llm.py,
    core/visuals.py) read their API key env vars into module-level constants
    at import time, so loading .env after importing them is a no-op: the
    module's copy of the key is already frozen as empty."""
    path = path or os.path.join(os.path.dirname(__file__), "..", ".env")
    if not os.path.exists(path):
        print(f"WARNING: {path} not found — relying on already-set environment variables.")
        return
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            key, value = key.strip(), value.strip()
            if key and key not in os.environ:
                os.environ[key] = value


_load_env_file()  # must happen before the core/ imports below

from core.pipeline import run_episode
from scripts.registry import all_channels, get_channel


def upload_one(channel_name, privacy):
    config = get_channel(channel_name)
    print(f"\n=== {channel_name} (privacy={privacy}) ===")
    try:
        result = run_episode(config, upload=True, privacy_status=privacy)
    except Exception as e:
        print(f"FAILED: {channel_name} raised {e!r} -- skipping, continuing with the rest")
        return None
    video_id = result.get("video_id")
    if video_id:
        url = f"https://www.youtube.com/watch?v={video_id}"
        print(f"UPLOADED: {url}")
        return url
    else:
        print("No video_id returned -- upload likely failed, check the log above.")
        return None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("channel", nargs="?", help="e.g. hp01_betrayal_revenge (omit with --all)")
    parser.add_argument("--all", action="store_true", help="run all 11 channels one after another")
    parser.add_argument("--unlisted", action="store_true", help="upload as unlisted instead of public")
    args = parser.parse_args()

    if not args.channel and not args.all:
        parser.error("pass a channel name, or --all for all 11")

    privacy = "unlisted" if args.unlisted else "public"

    urls = {}
    if args.all:
        for cfg in all_channels():
            urls[cfg["name"]] = upload_one(cfg["name"], privacy)
    else:
        urls[args.channel] = upload_one(args.channel, privacy)

    print("\n=== Summary ===")
    for name, url in urls.items():
        print(f"{name}: {url or 'FAILED'}")


if __name__ == "__main__":
    main()
