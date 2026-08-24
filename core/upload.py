"""
upload.py — FREE YouTube upload via the official YouTube Data API v3.

Free quota: 10,000 units/day (an upload costs ~1,600 units -> ~6 uploads/day
per channel, per Google Cloud project). No cost, just a one-time OAuth setup
PER CHANNEL/ACCOUNT (each Google account needs its own consent + token file).

One-time setup (repeat per channel/account):
  1. Go to https://console.cloud.google.com/ -> create a project (free).
  2. Enable "YouTube Data API v3" (APIs & Services -> Library).
  3. Configure OAuth consent screen (External, add your channel's Google
     account as a test user if the app is unverified — fine for personal use).
  4. Credentials -> Create Credentials -> OAuth client ID -> Desktop app.
  5. Download the JSON, save as client_secret.json next to this script
     (or point CLIENT_SECRET_FILE at it).
  6. First run of upload_video() opens a browser to authorize; a
     token_<channel>.json is saved so future runs are silent.

Usage:
    from core.upload import upload_video
    upload_video(
        video_path="out/final.mp4",
        title="What If the Roman Empire Had Nukes?",
        description="...",
        tags=["history", "whatif"],
        category_id="27",   # Education
        privacy_status="public",
        channel_token_file="token_history_channel.json",
    )
"""

import os
import googleapiclient.discovery
import googleapiclient.errors
from googleapiclient.http import MediaFileUpload
from core.auth import get_credentials


def upload_video(video_path, title, description, tags=None, category_id="27",
                  privacy_status="public", channel_token_file="token.json",
                  client_secret_file=None, thumbnail_path=None, made_for_kids=False):
    """Upload a finished MP4 to a specific channel (identified by its own
    token_file, created on first-run OAuth for that channel's Google account).

    client_secret_file lets different channels use different Google Cloud
    projects (recommended: split 8 channels across 2 projects so daily
    upload quota — 10,000 units/project, ~1,600/upload — doesn't run out)."""
    creds = get_credentials(channel_token_file, client_secret_file)
    youtube = googleapiclient.discovery.build("youtube", "v3", credentials=creds)

    body = {
        "snippet": {
            "title": title[:100],
            "description": description[:5000],
            "tags": tags or [],
            "categoryId": category_id,
        },
        "status": {"privacyStatus": privacy_status, "selfDeclaredMadeForKids": bool(made_for_kids)},
    }

    media = MediaFileUpload(video_path, chunksize=-1, resumable=True, mimetype="video/mp4")
    request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)

    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"[upload] {int(status.progress() * 100)}%")

    video_id = response["id"]
    print(f"[upload] done: https://youtube.com/watch?v={video_id}")

    if thumbnail_path and os.path.exists(thumbnail_path):
        youtube.thumbnails().set(videoId=video_id, media_body=MediaFileUpload(thumbnail_path)).execute()

    return video_id


if __name__ == "__main__":
    print("Import and call upload_video(...) — see module docstring for one-time OAuth setup.")
