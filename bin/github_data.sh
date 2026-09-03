#!/usr/bin/env bash
# Automated Crawler & Web Data Pipeline for Vietlott Data

set -e

DATA_FOLDER="data"
DOCS_FOLDER="docs"
VENV=".venv"

# Activate virtual environment if present
if [ -d "$VENV" ]; then
  source "$VENV/bin/activate"
fi

echo "Running from directory: $(pwd)"
export PYTHONPATH="src"
export LOGURU_LEVEL="INFO"

echo "=== 1. SYNCING & CRAWLING RECENT LOTTERY RESULTS ==="
python src/vietlott/sync_live_data.py || true

python src/vietlott/cli/crawl.py keno || true
python src/vietlott/cli/missing.py keno || true

python src/vietlott/cli/crawl.py power_655 || true
python src/vietlott/cli/missing.py power_655 || true

python src/vietlott/cli/crawl.py power_645 || true
python src/vietlott/cli/missing.py power_645 || true

python src/vietlott/cli/crawl.py power_535 || true
python src/vietlott/cli/missing.py power_535 || true

python src/vietlott/cli/crawl.py 3d || true
python src/vietlott/cli/missing.py 3d || true

python src/vietlott/cli/crawl.py 3d_pro || true
python src/vietlott/cli/missing.py 3d_pro || true

python src/vietlott/cli/crawl.py bingo18 || true
python src/vietlott/cli/missing.py bingo18 || true

echo "=== 2. GENERATING README STATS & WEB DATA ==="
python src/render_readme.py || true
python src/vietlott/render_web_data.py

# Sync index.html and json to root
cp -f docs/index.html index.html || true
cp -f docs/data/vietlott_summary.json data/vietlott_summary.json || true

echo "=== 3. COMMITTING AND PUSHING UPDATES ==="
if [ -d ".git" ]; then
  # Configure git user if running in CI or not set
  if [ -z "$(git config user.name)" ]; then
    git config user.name "github-actions[bot]"
    git config user.email "github-actions[bot]@users.noreply.github.com"
  fi

  git status
  git add "$DATA_FOLDER" "$DOCS_FOLDER" readme.md index.html

  # Only commit if there are staged changes
  if ! git diff --staged --quiet; then
    COMMIT_MSG="chore(data): auto-update Vietlott data & web UI @ $(date '+%Y-%m-%d %H:%M:%S') [skip ci]"
    git commit -m "$COMMIT_MSG"
    
    # Try push to current branch if remote exists
    if git remote get-url origin >/dev/null 2>&1; then
      echo "Pushing changes to remote origin..."
      git push origin HEAD
    else
      echo "No remote origin configured, skipping push."
    fi
  else
    echo "No new data changes to commit."
  fi
fi

echo "=== Pipeline completed successfully! ==="
