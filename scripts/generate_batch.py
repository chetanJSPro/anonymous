"""
generate_batch.py — generate N episodes for EACH active channel, no upload
(review the footage/quality before any of these get published — none of
the 11 channels are authorized for upload yet anyway, since that step
needs a real browser per channel). Each episode gets its own output folder
(output/<channel>/batch_1, batch_2, ...) so N videos per channel don't
overwrite each other, and uses core/topics.py's dynamic topic picker so
all N are on different topics, not the same one N times.

Usage:
    python scripts/generate_batch.py --count 4                 # all channels, 4 each
    python scripts/generate_batch.py --count 4 hp01_betrayal_revenge   # just one channel
"""

import os
import sys
import copy
import argparse
import traceback

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.pipeline import run_episode
from core.topics import pick_topic
from scripts.registry import all_channels


def generate_n(config, n, skip_existing=True):
    results = []
    for i in range(1, n + 1):
        final_path = os.path.join("output", config["name"], f"batch_{i}", "final.mp4")
        if skip_existing and os.path.exists(final_path) and os.path.getsize(final_path) > 0:
            print(f"[SKIP] {config['name']} batch {i} already exists: {final_path}")
            results.append({"channel": config["name"], "batch": i, "status": "ok", "path": final_path})
            continue

        batch_config = copy.deepcopy(config)
        batch_config["title_fn"] = config["title_fn"]
        batch_config["description_fn"] = config["description_fn"]
        batch_config["visual_query_fn"] = config["visual_query_fn"]
        batch_config["name"] = f"{config['name']}/batch_{i}"

        try:
            topic = pick_topic(config)  # recorded under the real channel name, not the batch subfolder
            print(f"\n=== {config['name']} {i}/{n} — topic: {topic} ===")
            result = run_episode(batch_config, topic=topic, upload=False)
            print(f"[OK] {result['video_path']}")
            results.append({"channel": config["name"], "batch": i, "status": "ok", "path": result["video_path"]})
        except Exception as e:
            print(f"[FAILED] {config['name']} batch {i}: {e}")
            traceback.print_exc()
            results.append({"channel": config["name"], "batch": i, "status": "failed", "error": str(e)})
    return results


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("channel", nargs="?", default=None, help="only this channel (default: all)")
    parser.add_argument("--count", type=int, default=4)
    parser.add_argument("--no-skip-existing", action="store_true",
                         help="regenerate batches even if final.mp4 already exists")
    args = parser.parse_args()

    channels = all_channels()
    if args.channel:
        channels = [c for c in channels if c["name"] == args.channel]
        if not channels:
            print(f"no channel named {args.channel!r}")
            sys.exit(1)

    all_results = []
    for config in channels:
        all_results += generate_n(config, args.count, skip_existing=not args.no_skip_existing)

    ok = [r for r in all_results if r["status"] == "ok"]
    failed = [r for r in all_results if r["status"] == "failed"]
    print("\n\n=== SUMMARY ===")
    for r in ok:
        print(f"  OK     {r['channel']} batch {r['batch']}: {r['path']}")
    for r in failed:
        print(f"  FAILED {r['channel']} batch {r['batch']}: {r['error']}")
    print(f"\n{len(ok)} succeeded, {len(failed)} failed, out of {len(all_results)} total.")


if __name__ == "__main__":
    main()
