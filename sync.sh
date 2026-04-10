#!/usr/bin/env bash
set -euo pipefail

BASE_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$BASE_DIR"

echo "BASE_DIR: $BASE_DIR"

# ===================== GitHub (skovnats) =================
echo "===> Sync to GitHub: https://github.com/skovnats/SVE-Systemic-Verification-Engineering"
git remote remove origin 2>/dev/null || true
git remote add origin git@github.com:skovnats/SVE-Systemic-Verification-Engineering.git
git push origin 'refs/heads/*:refs/heads/*' --prune --force
git push origin --tags -f

# ===================== GitHub Opa-Org (skovnats) =========
echo "===> Sync to GitHub Org: https://github.com/Opa-Collective/SVE-Systemic-Verification-Engineering"
git branch -D temp-org-sync 2>/dev/null || true
git checkout -B temp-org-sync
# Удаляем приватную папку только для этого пуша
git rm -rf "Applications/Ангелы-Хранетили" --ignore-unmatch
git commit -m "Exclude private applications for Org mirror" --quiet || echo "Already clean"

git remote remove org-mirror 2>/dev/null || true
git remote add org-mirror git@github.com:Opa-Collective/SVE-Systemic-Verification-Engineering.git
git push org-mirror temp-org-sync:master --force
git checkout master
git branch -D temp-org-sync

# ===================== GitLab ============================
echo "===> Sync to GitLab"
git remote remove gitlab 2>/dev/null || true
git remote add gitlab git@gitlab.com:opa-collective/sve.git
git push gitlab 'refs/heads/*:refs/heads/*' --prune --force
git push gitlab --tags -f

# ===================== Codeberg ==========================
echo "===> Sync to Codeberg"
git remote remove codeberg 2>/dev/null || true
git remote add codeberg "https://$CODEBERG_USER:$CODEBERG_API@codeberg.org/$CODEBERG_USER/$CODEBERG_REPO.git"
git push codeberg 'refs/heads/*:refs/heads/*' --prune --force
git push codeberg --tags -f

# ===================== GitFlic ===========================
echo "===> Sync to GitFlic"
git remote remove gitflic 2>/dev/null || true
git remote add gitflic "git@gitflic.ru:$GITFLIC_USER/$GITFLIC_REPO.git"

# Пробуем пуш веток. Если падает (из-за лимита), пропускаем, чтобы не стопорить MEGA
git push gitflic 'refs/heads/*:refs/heads/*' --prune --force -q || echo "GitFlic branches failed (limit?)"

for tag in $(git tag); do
    git push gitflic "$tag" -f -q 2>/dev/null || true
done

# ===================== Radicle (P2P) =====================
echo "===> Sync to Radicle"
if command -v rad >/dev/null 2>&1; then
    git push rad master -f --quiet || true
    rad sync --announce
fi

# ===================== MEGA S4 (S3) =======================
echo "===> Sync to MEGA S4"
export RCLONE_CONFIG_MEGAS4_TYPE="s3"
export RCLONE_CONFIG_MEGAS4_PROVIDER="Other"
export RCLONE_CONFIG_MEGAS4_ACCESS_KEY_ID="${MEGA_KEY}"
export RCLONE_CONFIG_MEGAS4_SECRET_ACCESS_KEY="${MEGAKEY_SECRET}"
export RCLONE_CONFIG_MEGAS4_ENDPOINT="${MEGA_ENDPOINT:-s3.g.s4.mega.io}"
export RCLONE_CONFIG_MEGAS4_REGION="eu-central-1"
export RCLONE_CONFIG_MEGAS4_ACL="private"

rclone copy "$BASE_DIR" "megas4:${MEGA_BUCKET}" \
  --exclude ".git/**" \
  --exclude ".github/**" \
  --exclude "artifacts/**" \
  --progress

echo "===> ALL DONE"


# ===================== SourceForge =======================
echo "===> Sync to SourceForge"
SF_USER="skovnats"         # Ваш логин
SF_PROJECT="sve"  # Имя проекта (URL-адрес проекта)

git remote remove sourceforge 2>/dev/null || true
git remote add sourceforge "ssh://$SF_USER@git.code.sf.net/p/$SF_PROJECT/code"

# Первая синхронизация требует --force из-за перезаписи истории
git push sourceforge 'refs/heads/*:refs/heads/*' --prune --force
git push sourceforge --tags -f
git push sourceforge master --force

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

# # ===================== Cloud Backups (MEGA & GDrive) ======
# echo "===> Sync to Cloud Storage"

# # MEGA
# rclone copy "$BASE_DIR" "megas4:${MEGA_BUCKET}" \
#   --exclude ".git/**" --exclude ".github/**" --exclude "artifacts/**" --progress

# # Google Drive
# if [ -f "${RCLONE_CONFIG_FILE:-}" ]; then
#     mkdir -p ~/.config/rclone
#     cp "$RCLONE_CONFIG_FILE" ~/.config/rclone/rclone.conf
#     rclone sync "$BASE_DIR" "gdrive:SVE" \
#       --exclude ".git/**" --exclude ".github/**" --exclude "artifacts/**" \
#       --progress
# fi

# echo "===> ALL DONE"

echo "===> Done"
