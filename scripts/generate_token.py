"""
generate_token.py — run this LOCALLY (on your own PC, once per channel) to
do the interactive Google OAuth consent and produce token_<channel>.json.
This step needs a real browser, so it can NEVER run inside GitHub Actions —
that's exactly why it's a separate one-time script.

Usage (run 8 times total, once per channel — pick the matching Google
account / brand channel in the browser popup each time):

    python scripts/generate_token.py hp01_betrayal_revenge
    python scripts/generate_token.py hp02_court_drama
    ... (all 8) ...

After this succeeds, upload the resulting token_<channel>.json content as a
GitHub secret (see SETUP.md step 6) — GitHub Actions uses the secret, never
the interactive flow.

To re-authorize a channel whose token already exists (e.g. to add a scope
that didn't exist yet, like yt-analytics.readonly), delete its
token_<channel>.json first, then re-run this script.
"""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.auth import get_credentials
from scripts.registry import get_channel


def main():
    if len(sys.argv) != 2:
        print("Usage: python scripts/generate_token.py <channel_name>")
        print("  e.g.: python scripts/generate_token.py hp01_betrayal_revenge")
        sys.exit(1)

    config = get_channel(sys.argv[1])
    token_file = config["channel_token_file"]
    client_secret_file = config.get("client_secret_file")

    if os.path.exists(token_file):
        print(f"{token_file} already exists. Delete it first if you want to re-authorize.")
        sys.exit(1)

    print(f"[generate_token] {config['name']} — opening a browser for Google sign-in...")
    print(f"[generate_token] using client secret: {client_secret_file}")
    print("[generate_token] IMPORTANT: pick the correct channel/brand account when prompted.")
    get_credentials(token_file, client_secret_file)
    print(f"[generate_token] saved {token_file} — keep this file secret, "
          f"upload its contents as a GitHub secret next (see SETUP.md).")


if __name__ == "__main__":
    main()
