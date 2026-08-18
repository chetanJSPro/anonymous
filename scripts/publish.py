"""
publish.py — generic "run one channel's episode" entrypoint used by the
GitHub Actions publish workflow (so the workflow only needs a channel name
string, not a different module path per channel).

Usage:
    python scripts/publish.py hp01_betrayal_revenge --upload
    python scripts/publish.py hp01_betrayal_revenge            # generate only, no upload
"""

import os
import sys
import argparse

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.pipeline import run_episode
from scripts.registry import get_channel


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("channel", help="channel name, e.g. hp01_betrayal_revenge")
    parser.add_argument("--upload", action="store_true")
    parser.add_argument("--topic", default=None)
    parser.add_argument("--privacy", default="public", choices=["public", "unlisted", "private"])
    args = parser.parse_args()

    config = get_channel(args.channel)
    result = run_episode(config, topic=args.topic, upload=args.upload, privacy_status=args.privacy)
    print(result)


if __name__ == "__main__":
    main()
