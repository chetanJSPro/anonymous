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
]

# Superset of SCOPES adding videos().update()/delete() access -- confirmed
# 2026-08-24 that youtube.upload alone does NOT cover editing/deleting
# existing videos (403 insufficientPermissions), despite some docs implying
# otherwise. NOT the default SCOPES: adding it there broke every existing
# channel's CI token refresh with invalid_scope (2026-08-25 incident) --
# Credentials.from_authorized_user_file+refresh() rejects a refresh token
# that was never actually granted a scope now being requested, even though
# the token file itself didn't change. Only pass MANAGE_SCOPES explicitly
# to get_credentials() for one-off manual cleanup scripts (video delete/
# update) run against a freshly re-authorized token -- never make it the
# pipeline's default.
MANAGE_SCOPES = SCOPES + ["https://www.googleapis.com/auth/youtube"]


def get_credentials(token_file, client_secret_file=None, scopes=None):
    """Load/refresh credentials from token_file. Only opens a browser
    (interactive) if no valid token exists yet and refresh fails — in CI
    (GitHub Actions) the token file MUST already exist and be refreshable,
    since there is no browser there.

    `scopes`: defaults to SCOPES (upload/readonly/analytics -- what every
    channel's CI token was actually authorized with). Pass MANAGE_SCOPES
    only for a manual one-off script that needs videos().update()/delete()
    against a token freshly re-authorized with that scope -- see SCOPES'
    docstring above for why this must never be the pipeline default."""
    scopes = scopes or SCOPES
    client_secret_file = client_secret_file or os.environ.get(
        "YT_CLIENT_SECRET_FILE", "client_secret.json")

    creds = None
    if os.path.exists(token_file):
        creds = Credentials.from_authorized_user_file(token_file, scopes)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
                client_secret_file, scopes)
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
