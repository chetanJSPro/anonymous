"""
write_secrets.py — used only inside GitHub Actions. Reads the base64-encoded
secrets injected as env vars and writes them back out as the plain files the
toolkit expects (client_secret_a.json, client_secret_b.json,
token_hp01_betrayal_revenge.json, ...), then exits. See
.github/workflows/*.yml for how the env vars are populated from GitHub
Secrets, and SETUP.md step 6 for how to create those secrets.
"""

import os
import sys
import base64

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from scripts.registry import all_channels

FILE_ENV_MAP = {
    "client_secret_a.json": "CLIENT_SECRET_A_B64",
    "client_secret_b.json": "CLIENT_SECRET_B_B64",
    "client_secret_c.json": "CLIENT_SECRET_C_B64",
}


def _token_env_name(channel_name):
    return f"TOKEN_{channel_name.upper()}_B64"


def main():
    wrote = []
    for filename, env_name in FILE_ENV_MAP.items():
        b64 = os.environ.get(env_name)
        if b64:
            with open(filename, "wb") as f:
                f.write(base64.b64decode(b64))
            wrote.append(filename)

    for config in all_channels():
        env_name = _token_env_name(config["name"])
        b64 = os.environ.get(env_name)
        if not b64:
            print(f"[write_secrets] WARNING: no {env_name} secret set, "
                  f"skipping {config['channel_token_file']} "
                  f"({config['name']} will fail to authenticate)")
            continue
        with open(config["channel_token_file"], "wb") as f:
            f.write(base64.b64decode(b64))
        wrote.append(config["channel_token_file"])

    print(f"[write_secrets] wrote {len(wrote)} file(s): {', '.join(wrote)}")


if __name__ == "__main__":
    main()
