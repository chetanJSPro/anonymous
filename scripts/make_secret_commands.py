"""
make_secret_commands.py — after you've run scripts/generate_token.py for all
8 channels and have client_secret_a.json / client_secret_b.json in the
project root, run this to print the exact `gh secret set` commands that
upload everything to your GitHub repo as encrypted secrets.

This only PRINTS commands — it never sends anything anywhere itself, and it
never prints your key material to the terminal (base64 goes straight into
each command's argument, not shown separately). Copy the output and run it
yourself from this same folder, or pipe straight to a shell:

    python scripts/make_secret_commands.py > set_secrets.sh
    bash set_secrets.sh
    rm set_secrets.sh   # delete afterwards, it contains your secrets in plain text

Requires the GitHub CLI (`gh`) authenticated (`gh auth login`) and run from
inside the git repo you created for this project.
"""

import os
import sys
import base64

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from scripts.registry import all_channels
from scripts.write_secrets import FILE_ENV_MAP, _token_env_name


def _b64_of(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("ascii")


def main():
    lines = ["#!/usr/bin/env bash", "set -e", ""]
    missing = []

    for filename, env_name in FILE_ENV_MAP.items():
        if os.path.exists(filename):
            lines.append(f'gh secret set {env_name} --body "{_b64_of(filename)}"')
        else:
            missing.append(filename)

    for config in all_channels():
        token_file = config["channel_token_file"]
        env_name = _token_env_name(config["name"])
        if os.path.exists(token_file):
            lines.append(f'gh secret set {env_name} --body "{_b64_of(token_file)}"')
        else:
            missing.append(token_file)

    lines.append("")
    lines.append('echo "Now also run:"')
    lines.append('echo "  gh secret set GROQ_API_KEY --body YOUR_GROQ_KEY"')
    lines.append('echo "  gh secret set PIXABAY_API_KEY --body YOUR_PIXABAY_KEY"')

    print("\n".join(lines))

    if missing:
        print("\n# WARNING: these files are missing, their secrets were skipped:",
              file=sys.stderr)
        for m in missing:
            print(f"#   {m}", file=sys.stderr)


if __name__ == "__main__":
    main()
