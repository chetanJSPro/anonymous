#!/bin/bash
# YouTube Automation Setup — RUN THIS ON YOUR LOCAL PC, from inside anonymous-master/.
# Does everything that can be scripted, back to back.
# You will be dropped into a browser 11 times (channel auth) — that part
# cannot be skipped, it's Google's OAuth consent screen.
#
# Prerequisites (still manual — Google/GitHub require a human click for each):
#   1. The 11 YouTube channels already created (YouTube Studio).
#   2. client_secret_a.json, client_secret_b.json, client_secret_c.json
#      already downloaded from the 3 GCP OAuth projects, sitting in this
#      same directory (next to this script).
#   3. `gh auth login` already done.

set -e
cd "$(dirname "$0")"

echo "== 1/4: Installing dependencies =="
pip install -r requirements.txt

echo ""
echo "== 2/4: Authorizing 11 channels (browser will open each time) =="
echo "Sign in and pick the matching channel when the browser opens."
for ch in \
  hp01_betrayal_revenge \
  hp02_court_drama \
  hp03_karma_justice \
  hp04_veteran_kindness \
  hp05_sleep_soundscapes \
  hp06_literary_analysis \
  hp07_senior_longevity \
  hp08_english_learning \
  ch01_ai_asmr \
  ch03_hindu_mythology \
  ch06_eastern_philosophy
do
  echo "--- authorizing $ch ---"
  python scripts/generate_token.py "$ch"
done

echo ""
echo "== 3/4: Uploading GitHub secrets (to this repo's own remote, not Peace Reels) =="
python scripts/make_secret_commands.py > set_secrets.sh
bash set_secrets.sh
rm set_secrets.sh

read -p "Groq API key: " GROQ_KEY
gh secret set GROQ_API_KEY --body "$GROQ_KEY"

read -p "Pexels API key (blank to skip): " PEXELS_KEY
[ -n "$PEXELS_KEY" ] && gh secret set PEXELS_API_KEY --body "$PEXELS_KEY"

read -p "Pixabay API key (blank to skip): " PIXABAY_KEY
[ -n "$PIXABAY_KEY" ] && gh secret set PIXABAY_API_KEY --body "$PIXABAY_KEY"

echo ""
echo "== 4/4: Enabling GitHub Pages via API =="
REPO=$(gh repo view --json nameWithOwner -q .nameWithOwner)
BRANCH=$(gh repo view --json defaultBranchRef -q .defaultBranchRef.name)
gh api -X POST "repos/$REPO/pages" -f "source[branch]=$BRANCH" -f "source[path]=/docs" || \
  echo "(Pages may already be enabled — check Settings > Pages manually if this failed)"

echo ""
echo "DONE. Still manual (Google won't allow scripting these):"
echo "  - Creating the 11 YouTube channels themselves (Studio UI)"
echo "  - Creating the 3 GCP OAuth client_secret_{a,b,c}.json files"
echo "Everything else is now wired up. Test in the Actions tab:"
echo "  gh workflow run publish.yml -f channel=hp01_betrayal_revenge -f upload=false"
