#!/usr/bin/env bash
set -e

# === настройки ===
GITLAB_URL="https://gitlab.com"
GITLAB_PROJECT_PATH="your-group/your-repo"   # поменяй
MEGA_REMOTE_PATH="/backups/github/your-repo" # поменяй
GDRIVE_REMOTE="gdrive:github-backups/your-repo" # поменяй

# токены / логины берём из переменных окружения
: "${GITLAB_TOKEN:?need GITLAB_TOKEN}"
: "${MEGA_EMAIL:?need MEGA_EMAIL}"
: "${MEGA_PASSWORD:?need MEGA_PASSWORD}"
: "${RCLONE_CONFIG_FILE:?need RCLONE_CONFIG_FILE}"   # путь к rclone.conf

# === GitLab mirror ===
git remote remove gitlab 2>/dev/null || true
git remote add gitlab "https://oauth2:${GITLAB_TOKEN}@${GITLAB_URL#https://}/${GITLAB_PROJECT_PATH}.git"
git push gitlab --mirror

# === архив ===
mkdir -p artifacts
ts="$(date -u +'%Y%m%dT%H%M%SZ')"
ARCHIVE="artifacts/repo-${ts}.tar.gz"
tar --exclude='./.git' -czf "$ARCHIVE" .

# === MEGA ===
mega-logout || true
mega-login "$MEGA_EMAIL" "$MEGA_PASSWORD"
mega-mkdir -p "$MEGA_REMOTE_PATH" || true
mega-put "$ARCHIVE" "$MEGA_REMOTE_PATH"

# === Google Drive через rclone ===
mkdir -p ~/.config/rclone
cp "$RCLONE_CONFIG_FILE" ~/.config/rclone/rclone.conf
rclone copy "$ARCHIVE" "$GDRIVE_REMOTE" --progress


# chmod +x sync.sh

# export GITLAB_TOKEN=...
# export MEGA_EMAIL=...
# export MEGA_PASSWORD=...
# export RCLONE_CONFIG_FILE=/path/to/rclone.conf

# ./sync.sh
