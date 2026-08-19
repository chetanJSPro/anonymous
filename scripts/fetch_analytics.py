"""
fetch_analytics.py — pulls daily performance stats for all 8 niche channels
from the YouTube Analytics API and appends them to data/stats.json, the file
build_dashboard.py reads to render the comparison dashboard.

Run daily (see .github/workflows/analytics.yml). Needs each channel's
token_<channel>.json to already include the yt-analytics.readonly scope
(core/auth.py requests it) — re-run scripts/generate_token.py once per
channel if your tokens predate that.

Usage:
    python scripts/fetch_analytics.py
"""

import os
import sys
import json
import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import googleapiclient.discovery
from core.auth import get_credentials
from scripts.registry import all_channels

DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "docs", "data", "stats.json")


def _load_existing():
    if os.path.exists(DATA_PATH):
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"channels": {}, "records": [], "pilot_start": datetime.date.today().isoformat()}


def _save(data):
    os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)
    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def fetch_channel_stats(config, days=14):
    """Pull daily views/watch-time/subs for one channel over the last `days`
    days via the YouTube Analytics API (channel==MINE, scoped by its own
    OAuth token). Returns a list of {date, views, watch_minutes, subs_gained,
    likes} dicts, one per day."""
    creds = get_credentials(config["channel_token_file"], config.get("client_secret_file"))
    yta = googleapiclient.discovery.build("youtubeAnalytics", "v2", credentials=creds)

    end = datetime.date.today()
    start = end - datetime.timedelta(days=days)

    resp = yta.reports().query(
        ids="channel==MINE",
        startDate=start.isoformat(),
        endDate=end.isoformat(),
        metrics="views,estimatedMinutesWatched,subscribersGained,likes",
        dimensions="day",
        sort="day",
    ).execute()

    rows = resp.get("rows", []) or []
    out = []
    for r in rows:
        out.append({
            "date": r[0],
            "views": r[1],
            "watch_minutes": r[2],
            "subs_gained": r[3],
            "likes": r[4],
        })
    return out


def channel_snapshot(config):
    """Current channel totals via YouTube Data API (needs youtube.readonly,
    already in core/auth.py's SCOPES) -- videoCount, viewCount,
    subscriberCount. Unlike the Analytics API's per-day reports (which have
    a well-documented 24-48h processing lag before "today" shows up), this
    is close to real-time -- it's the same number YouTube shows on the
    channel page itself. Used as the dashboard's headline number so it
    doesn't look like "0 views" right after a fresh upload."""
    creds = get_credentials(config["channel_token_file"], config.get("client_secret_file"))
    yt = googleapiclient.discovery.build("youtube", "v3", credentials=creds)
    resp = yt.channels().list(part="statistics", mine=True).execute()
    items = resp.get("items", [])
    if not items:
        return None
    stats = items[0]["statistics"]
    return {
        "video_count": int(stats.get("videoCount", 0)),
        "current_total_views": int(stats.get("viewCount", 0)),
        "current_subscribers": int(stats.get("subscriberCount", 0)),
    }


def main():
    data = _load_existing()
    existing_keys = {(r["channel"], r["date"]) for r in data["records"]}

    for config in all_channels():
        name = config["name"]
        print(f"[fetch_analytics] {name} ...")
        data["channels"][name] = {
            "niche": config.get("niche", name),
            "est_rpm": config.get("est_rpm"),
        }
        try:
            daily = fetch_channel_stats(config)
        except Exception as e:
            print(f"[fetch_analytics] {name} FAILED: {e}")
            continue

        for day in daily:
            key = (name, day["date"])
            if key in existing_keys:
                continue  # already recorded, keep history append-only
            data["records"].append({"channel": name, **day})
            existing_keys.add(key)

        try:
            snapshot = channel_snapshot(config)
            if snapshot:
                data["channels"][name].update(snapshot)
        except Exception as e:
            print(f"[fetch_analytics] {name} channel_snapshot FAILED: {e}")

    data["last_updated"] = datetime.datetime.utcnow().isoformat() + "Z"
    _save(data)
    print(f"[fetch_analytics] wrote {DATA_PATH} ({len(data['records'])} total daily records)")


if __name__ == "__main__":
    main()
