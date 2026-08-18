"""
generate_previews.py — generate 2 sample episodes per niche channel LOCALLY
(no YouTube upload, no OAuth needed) so you can review the output quality
before committing to the full automation.

Writes to output/<channel>/preview_1/final.mp4 and .../preview_2/final.mp4
for all 11 niche channels (22 videos total).

Usage:
    python scripts/generate_previews.py                # all 11 channels, 2 each
    python scripts/generate_previews.py hp01_betrayal_revenge   # just one channel
"""

import os
import sys
import copy
import traceback

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.pipeline import run_episode
from scripts.registry import all_channels


def generate_two(config):
    results = []
    topics = config["topic_prompts"][:2] or [None, None]
    if len(topics) < 2:
        topics = (topics * 2)[:2]

    for i, topic in enumerate(topics, start=1):
        preview_config = copy.deepcopy(config)
        # keep functions (deepcopy of a dict with functions as values keeps
        # the function references, only the plain data gets copied)
        preview_config["title_fn"] = config["title_fn"]
        preview_config["description_fn"] = config["description_fn"]
        preview_config["visual_query_fn"] = config["visual_query_fn"]
        preview_config["name"] = f"{config['name']}/preview_{i}"

        print(f"\n=== {config['name']} preview {i}/2 — topic: {topic} ===")
        try:
            result = run_episode(preview_config, topic=topic, upload=False)
            print(f"[OK] {result['video_path']}")
            results.append({"channel": config["name"], "preview": i, "status": "ok",
                             "path": result["video_path"]})
        except Exception as e:
            print(f"[FAILED] {config['name']} preview {i}: {e}")
            traceback.print_exc()
            results.append({"channel": config["name"], "preview": i, "status": "failed",
                             "error": str(e)})
    return results


def main():
    target = sys.argv[1] if len(sys.argv) > 1 else None
    channels = all_channels()
    if target:
        channels = [c for c in channels if c["name"] == target]
        if not channels:
            print(f"no channel named {target!r}")
            sys.exit(1)

    all_results = []
    for config in channels:
        all_results += generate_two(config)

    print("\n\n=== SUMMARY ===")
    ok = [r for r in all_results if r["status"] == "ok"]
    failed = [r for r in all_results if r["status"] == "failed"]
    for r in ok:
        print(f"  OK     {r['channel']} preview {r['preview']}: {r['path']}")
    for r in failed:
        print(f"  FAILED {r['channel']} preview {r['preview']}: {r['error']}")
    print(f"\n{len(ok)} succeeded, {len(failed)} failed, out of {len(all_results)} total.")


if __name__ == "__main__":
    main()
