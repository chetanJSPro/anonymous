"""
publish_all.py — generate + upload ONE video to EACH active channel in
scripts/registry.py in a single run. This is what the desktop launcher
(Publish All Channels.bat) calls: one double-click -> one fresh video goes
out on every channel.

Continues past a single channel's failure (bad API response, quota hit,
missing OAuth token, etc.) instead of aborting the whole batch, and prints
a per-channel summary at the end so a failure on channel 6 doesn't hide
whether channels 1-5 and 7-11 actually succeeded.

Usage:
    python scripts/publish_all.py                # upload=True on every channel
    python scripts/publish_all.py --no-upload     # generate only, review before publishing
    python scripts/publish_all.py --privacy unlisted
"""

import os
import sys
import argparse
import traceback

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.pipeline import run_episode
from scripts.registry import all_channels


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--no-upload", action="store_true", help="generate only, skip YouTube upload")
    parser.add_argument("--privacy", default="public", choices=["public", "unlisted", "private"])
    args = parser.parse_args()

    results = []
    channels = all_channels()
    print(f"=== publish_all: {len(channels)} channels, upload={not args.no_upload} ===\n")

    for config in channels:
        name = config["name"]
        print(f"--- {name} ---")
        try:
            result = run_episode(config, upload=not args.no_upload, privacy_status=args.privacy)
            status = "uploaded" if result.get("video_id") else "generated (no upload)"
            print(f"[OK] {name}: {status} — {result['video_path']}")
            results.append({"channel": name, "status": "ok", **result})
        except Exception as e:
            print(f"[FAILED] {name}: {e}")
            traceback.print_exc()
            results.append({"channel": name, "status": "failed", "error": str(e)})
        print()

    ok = [r for r in results if r["status"] == "ok"]
    failed = [r for r in results if r["status"] == "failed"]
    print("=== SUMMARY ===")
    for r in ok:
        vid = f" (video_id={r['video_id']})" if r.get("video_id") else ""
        print(f"  OK     {r['channel']}{vid}")
    for r in failed:
        print(f"  FAILED {r['channel']}: {r['error']}")
    print(f"\n{len(ok)} succeeded, {len(failed)} failed, out of {len(results)} channels.")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
