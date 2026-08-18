"""
run.py for hp06_literary_analysis — auto-generated. Run with:
    python3 -m channels_highpay.hp06_literary_analysis.run
    python3 -m channels_highpay.hp06_literary_analysis.run --upload
    python3 -m channels_highpay.hp06_literary_analysis.run --topic "..."
"""
import argparse
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from core.pipeline import run_episode
from channels_highpay.hp06_literary_analysis.config import CONFIG

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--upload", action="store_true")
    parser.add_argument("--topic", default=None)
    parser.add_argument("--privacy", default="public", choices=["public", "unlisted", "private"])
    args = parser.parse_args()

    result = run_episode(CONFIG, topic=args.topic, upload=args.upload, privacy_status=args.privacy)
    print(result)
