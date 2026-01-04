#!/usr/bin/env bash
set -euo pipefail

# ========= БАЗОВАЯ ПАПКА SVE (где лежит sync.sh) =========
BASE_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$BASE_DIR"

echo "BASE_DIR: $BASE_DIR"

# ===================== GitLab ============================
GITLAB_URL="https://gitlab.com"
GITLAB_PROJECT_PATH="opa-collective/sve"   # поменяй при необходимости

: "${GITLABsk_TOKEN:?need GITLABsk_TOKEN}"

echo "===> Sync to GitLab: https://gitlab.com/opa-collective/sve"

git remote remove gitlab 2>/dev/null || true
git remote add gitlab git@gitlab.com:opa-collective/sve.git

# пушим все локальные ветки
git push gitlab 'refs/heads/*:refs/heads/*' --prune

# пушим все теги
git push gitlab --tags

# ===================== MEGA S4 (S3) =======================
# Нужны:
#   MEGA_BUCKET   – имя бакета
: "${MEGA_BUCKET:?need MEGA_BUCKET}"
MEGA_ENDPOINT="${MEGA_ENDPOINT:-s3.g.s4.mega.io}"

: "${MEGA_KEY:?need MEGA_KEY}"
: "${MEGAKEY_SECRET:?need MEGAKEY_SECRET}"

# 
export MEGA_BUCKET="sve-backups"

echo "===> Sync to MEGA S4 (bucket: $MEGA_BUCKET"

# rclone remote megas4 через env (без файла конфига)
export RCLONE_CONFIG_MEGAS4_TYPE="s3"
export RCLONE_CONFIG_MEGAS4_PROVIDER="Other"
export RCLONE_CONFIG_MEGAS4_ACCESS_KEY_ID="${MEGA_KEY}"
export RCLONE_CONFIG_MEGAS4_SECRET_ACCESS_KEY="${MEGAKEY_SECRET}"
export RCLONE_CONFIG_MEGAS4_ENDPOINT="${MEGA_ENDPOINT}"
export RCLONE_CONFIG_MEGAS4_REGION="eu-central-1"
export RCLONE_CONFIG_MEGAS4_ACL="private"

MEGA_DEST="megas4:${MEGA_BUCKET}"

# rclone sync "$BASE_DIR" "$MEGA_DEST" \
rclone copy "$BASE_DIR" "$MEGA_DEST" \
  --exclude ".git/**" \
  --exclude ".github/**" \
  --exclude "artifacts/**" \
  --retries 3 \
  --low-level-retries 10 \
  --progress

# ===================== Google Drive =======================
# # В rclone.conf должен быть remote [gdrive]
# : "${RCLONE_CONFIG_FILE:?need RCLONE_CONFIG_FILE}"

# GDRIVE_REMOTE="gdrive:SVE"   # Папка SVE на Google Drive

# echo "===> Sync to Google Drive ($GDRIVE_REMOTE)"

# mkdir -p ~/.config/rclone
# cp "$RCLONE_CONFIG_FILE" ~/.config/rclone/rclone.conf

# rclone sync "$BASE_DIR" "$GDRIVE_REMOTE" \
#   --exclude ".git/**" \
#   --exclude ".github/**" \
#   --exclude "artifacts/**" \
#   --progress

# # В rclone.conf должен быть remote [gdrive]
# : "${RCLONE_CONFIG_FILE:?need RCLONE_CONFIG_FILE}"

# GDRIVE_REMOTE="gdrive:SVE"   # папка SVE в Google Drive

# echo "===> Sync to Google Drive ($GDRIVE_REMOTE)"

# mkdir -p ~/.config/rclone
# cp "$RCLONE_CONFIG_FILE" ~/.config/rclone/rclone.conf

# rclone sync "$BASE_DIR" "$GDRIVE_REMOTE" \
#   --exclude ".git/**" \
#   --exclude ".github/**" \
#   --exclude "artifacts/**" \
#   --retries 3 \
#   --low-level-retries 10 \
#   --progress

echo "===> Done"
