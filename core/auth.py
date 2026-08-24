"""
auth.py — shared Google OAuth credential helper, used by both upload.py
(YouTube Data API — publishing) and scripts/fetch_analytics.py (YouTube
Analytics API — dashboard stats).

One token file per channel, authorized ONCE with BOTH scopes below, so the
same token_<channel>.json powers uploads AND the performance dashboard.

Re-running the interactive auth (scripts/generate_token.py) after this file
was added will upgrade an old upload-only token to include the analytics
scope — do that once per channel if you set channels up before this existed.
"""

import os
import google_auth_oauthlib.flow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube.readonly",
    "https://www.googleapis.com/auth/yt-analytics.readonly",
    # Needed for videos().update()/delete() -- confirmed 2026-08-24 that
    # youtube.upload alone does NOT cover editing/deleting existing videos
    # (403 insufficientPermissions on both update and delete with only the
    # scopes above), despite some docs implying otherwise. Only needed for
    # manual cleanup scripts, not the normal publish pipeline.
    "https://www.googleapis.com/auth/youtube",
]


def get_credentials(token_file, client_secret_file=None):
    """Load/refresh credentials from token_file. Only opens a browser
    (interactive) if no valid token exists yet and refresh fails — in CI
    (GitHub Actions) the token file MUST already exist and be refreshable,
    since there is no browser there."""
    client_secret_file = client_secret_file or os.environ.get(
        "YT_CLIENT_SECRET_FILE", "client_secret.json")

    creds = None
    if os.path.exists(token_file):
        creds = Credentials.from_authorized_user_file(token_file, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
                client_secret_file, SCOPES)
            # Port defaults to 0 (any free port) for the usual "Desktop app"
            # OAuth clients, which Google allows on any localhost port. A
            # "Web application" type client (fixed registered redirect URIs,
            # e.g. reused from another project) needs OAUTH_LOCAL_PORT set to
            # one of its exact registered ports instead, or the callback is
            # rejected as a redirect_uri mismatch.
            port = int(os.environ.get("OAUTH_LOCAL_PORT", "0"))
            creds = flow.run_local_server(port=port)
        with open(token_file, "w") as f:
            f.write(creds.to_json())

    return creds
