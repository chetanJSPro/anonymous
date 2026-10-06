"""
trending.py — signals that steer core/topics.py's topic generation toward
what actually gets views, instead of the LLM inventing topics blind:

  1. trending_titles(): titles of the most-viewed Shorts in this niche
     published in the last 7 days (YouTube Data API search via the
     channel's own OAuth token, ~100 quota units). Reddit was tried first
     but blocks unauthenticated requests (403/429). Used only as
     *inspiration* in the topic prompt — the LLM writes an original story.
  2. winning_titles(): this channel's own best-performing recent videos,
     written daily by scripts/fetch_analytics.py into docs/data/stats.json["top_videos"].

Both are best-effort: any failure returns [] and topic generation proceeds
exactly as before.
"""

import html
import json
import os

SEARCH_TERMS = {
    "hp01_betrayal_revenge": "revenge story",
    "hp02_court_drama": "courtroom story",
    "hp03_karma_justice": "instant karma story",
    "hp04_veteran_kindness": "veteran kindness story",
    "hp06_literary_analysis": "book recommendation",
    "hp07_senior_longevity": "longevity tips over 60",
    "hp08_english_learning": "english vocabulary",
    "hp09_kids_cartoon_stories": "bedtime story for kids",
    "ch01_ai_asmr": "satisfying asmr",
    "ch03_hindu_mythology": "mahabharata story",
    "ch06_eastern_philosophy": "zen story",
}

TOP_VIDEOS_PATH = os.path.join(os.path.dirname(__file__), "..", "docs", "data", "stats.json")


def trending_titles(config, limit=12):
    term = config.get("trending_search") or SEARCH_TERMS.get(config["name"])
    if not term:
        return []
    try:
        import datetime
        import googleapiclient.discovery
        from core.auth import get_credentials
        creds = get_credentials(config["channel_token_file"], config.get("client_secret_file"))
        yt = googleapiclient.discovery.build("youtube", "v3", credentials=creds)
        since = (datetime.datetime.utcnow() - datetime.timedelta(days=7)).strftime("%Y-%m-%dT%H:%M:%SZ")
        resp = yt.search().list(part="snippet", q=term + " #shorts", type="video",
                                videoDuration="short", order="viewCount",
                                publishedAfter=since, maxResults=limit,
                                relevanceLanguage="en").execute()
        return [html.unescape(i["snippet"]["title"]) for i in resp.get("items", [])]
    except Exception as e:
        print(f"[trending] search failed for {config['name']}: {e}")
        return []


def winning_titles(channel_name, limit=5):
    try:
        with open(TOP_VIDEOS_PATH, encoding="utf-8") as f:
            vids = json.load(f).get("top_videos", {}).get(channel_name, [])
        return [v["title"] for v in vids[:limit] if v.get("title")]
    except Exception:
        return []
