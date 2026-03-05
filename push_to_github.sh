#!/usr/bin/env bash
# Run this from the repo root (testing/Image_search/) to push to VLM_eval.
# Requires: git, and that backend/.env and backend/Mimir_key.json are not tracked.
set -e
cd "$(dirname "$0")"

if [ ! -d .git ]; then
  git init
fi

# Commit .gitignore first so secrets are never tracked
git add .gitignore
if ! git diff --cached --quiet 2>/dev/null; then
  git commit -m "Add .gitignore (exclude API keys)"
fi

# Add all other files (.gitignore excludes backend/.env and backend/*_key.json)
git add .
STAGED=$(git diff --cached --name-only)
if echo "$STAGED" | grep -q 'backend/\.env$'; then
  echo "ERROR: backend/.env is staged. Ensure .gitignore contains backend/.env"
  exit 1
fi
if echo "$STAGED" | grep -q 'backend/.*_key\.json'; then
  echo "ERROR: A backend *_key.json file is staged. Ensure .gitignore contains backend/*_key.json"
  exit 1
fi
if git diff --cached --quiet; then
  echo "Nothing to commit (all changes already committed)."
else
  git commit -m "Add VLM_eval evaluation framework (README, backend, Evaluation, results, scripts)"
fi

git branch -M main
git remote remove origin 2>/dev/null || true
git remote add origin https://github.com/andreasklae/VLM_eval.git
git push -u origin main

echo "Done. Repo pushed to https://github.com/andreasklae/VLM_eval"
