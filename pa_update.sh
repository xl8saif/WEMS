#!/usr/bin/env bash
# WEMS update script for PythonAnywhere.
# Pulls the latest code and reloads the web app in one command:
#   bash ~/WEMS/pa_update.sh
set -euo pipefail

APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$APP_DIR"

echo "==> Pulling latest code"
git pull --ff-only origin main

# Re-sync dependencies only when requirements.txt actually changed.
CHANGED=$(git diff --name-only "@{upstream}" HEAD~1 2>/dev/null || true)
if printf '%s\n' "$CHANGED" | grep -q "^requirements.txt$"; then
  echo "==> requirements.txt changed — pip install"
  if [ -n "${VIRTUAL_ENV:-}" ]; then
    pip install -r requirements.txt
  else
    # PythonAnywhere default virtualenv location
    pip install --user -r requirements.txt
  fi
fi

echo "==> Reloading web app"
WSGI_FILE="/var/www/${PYTHONANYWHERE_DOMAIN:-$USER.pythonanywhere.com}_wsgi.py"
touch "$WSGI_FILE" 2>/dev/null || {
  # Fallback: try the www.-prefixed layout, else ask for the button.
  touch "/var/www/www.${PYTHONANYWHERE_DOMAIN:-$USER.pythonanywhere.com}_wsgi.py" 2>/dev/null || {
    echo "NOTE: could not touch the WSGI file automatically."
    echo "Hit the green Reload button on the Web tab to finish."
    exit 0
  }
}

echo "==> Update complete."
