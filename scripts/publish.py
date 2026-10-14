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
import datetime
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.pipeline import run_episode
from scripts.registry import get_channel, all_channels

# Each Google Cloud project allows ~6 uploads/day (10,000 units, ~1,600 per
# upload), but publish.yml schedules 3 runs/day for every channel -- 12 on
# client_secret_a's 4 channels, so half failed with quota-exceeded at random,
# often starving the best channel. Instead, slots are handed out daily by
# recent views: every channel keeps 1/day, the rest go to the winners.
PROJECT_DAILY_UPLOADS = 6
RUNS_PER_DAY = 3
STATS_PATH = os.path.join(os.path.dirname(__file__), "..", "docs", "data", "stats.json")


def _recent_views(days=7):
    try:
        with open(STATS_PATH, encoding="utf-8") as f:
            records = json.load(f).get("records", [])
    except Exception:
        return {}
    dates = sorted({r["date"] for r in records if r.get("views")})[-days:]
    views = {}
    for r in records:
        if r["date"] in dates:
            views[r["channel"]] = views.get(r["channel"], 0) + (r.get("views") or 0)
    return views


def allocated_runs(channel_name):
    """Uploads/day this channel gets among the channels sharing its OAuth
    project, ranked by last-7-day views."""
    configs = {c["name"]: c for c in all_channels()}
    project = configs[channel_name].get("client_secret_file")
    peers = [n for n, c in configs.items() if c.get("client_secret_file") == project]
    views = _recent_views()
    alloc = {n: 1 for n in peers}
    spare = PROJECT_DAILY_UPLOADS - len(peers)
    for n in sorted(peers, key=lambda n: views.get(n, 0), reverse=True):
        extra = min(RUNS_PER_DAY - alloc[n], max(0, spare))
        alloc[n] += extra
        spare -= extra
    print(f"[publish] daily upload allocation for {project}: {alloc} (7d views: "
          f"{ {n: views.get(n, 0) for n in peers} })")
    return alloc[channel_name]


def run_slot(now=None):
    """Which of the 3 daily cron runs this is (00:30/08:30/16:30 UTC);
    8-hour windows absorb GitHub's multi-hour cron delays."""
    hour = (now or datetime.datetime.utcnow()).hour
    return hour // 8


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("channel", help="channel name, e.g. hp01_betrayal_revenge")
    parser.add_argument("--upload", action="store_true")
    parser.add_argument("--topic", default=None)
    parser.add_argument("--privacy", default="public", choices=["public", "unlisted", "private"])
    args = parser.parse_args()

    config = get_channel(args.channel)
    if args.upload and os.environ.get("GITHUB_EVENT_NAME") == "schedule":
        slot, runs = run_slot(), allocated_runs(args.channel)
        if slot >= runs:
            print(f"[publish] {args.channel}: run slot {slot} not allocated "
                  f"(gets {runs}/day by recent views) -- skipping to save quota for winners")
            return
    result = run_episode(config, topic=args.topic, upload=args.upload, privacy_status=args.privacy)
    print(result)


if __name__ == "__main__":
    main()
