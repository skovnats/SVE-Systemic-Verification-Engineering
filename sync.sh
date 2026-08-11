#!/usr/bin/env bash
set -euo pipefail

BASE_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$BASE_DIR"

# 0. Check PDFs
echo "--> Проверка целостности PDF..."
if [ -f "./check_pdfs.sh" ]; then
    bash ./check_pdfs.sh .
else
    echo "⚠️ Скрипт check_pdfs.sh не найден, пропускаем."
fi

# 1. hashdeep — генерируем карту хэшей в реальном времени
echo "--> Generating system file hashes..."
hashdeep -r . > hashsum.md

# 2. Фиксируем изменения в Git
bash ./generate_passport.sh
git add hashsum.md pdf_report.csv passport.txt
git commit -m "chore: update system integrity passport [Temporal Integrity Block]" || echo "No hash changes detected."

#------------------------------------------
# Инициализация флагов (по умолчанию всё выключено)
ALL=true
GITHUB_SKOVNATS=false
GITHUB_OPA=false
GITLAB=false
CODEBERG=false
GITFLIC=false
RADICLE=false
MEGA=false
PROTON=false
SOURCEFORGE=false

# Если переданы аргументы, выключаем режим "все" и переходим к выборочному
if [ $# -gt 0 ]; then
    ALL=false
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --all) ALL=true; shift ;;
            --github-skovnats) GITHUB_SKOVNATS=true; shift ;;
            --github-opa) GITHUB_OPA=true; shift ;;
            --gitlab) GITLAB=true; shift ;;
            --codeberg) CODEBERG=true; shift ;; # Добавьте true если нужно
            --gitflic) GITFLIC=true; shift ;;
            --radicle) RADICLE=true; shift ;;
            --mega) MEGA=true; shift ;;
            --proton) PROTON=true; shift ;;
            --sourceforge) SOURCEFORGE=true; shift ;;
            *) echo "Unknown option: $1"; exit 1 ;;
        esac
    done
fi

# Функция-помощник для проверки, нужно ли запускать сервис
should_run() {
    [[ "$ALL" == "true" ]] || [[ "$1" == "true" ]]
}
#------------------------------------------

echo "BASE_DIR: $BASE_DIR"

# ===================== GitHub (skovnats) =================
if should_run "$GITHUB_SKOVNATS"; then
    echo "===> Sync to GitHub: skovnats"
    echo "===> Sync to GitHub: https://codeberg.org/skovnats/SVE-Systemic-Verification-Engineering"
    git remote remove origin 2>/dev/null || true
    git remote add origin git@github.com:skovnats/SVE-Systemic-Verification-Engineering.git
    git push origin 'refs/heads/*:refs/heads/*' --prune --force
    git push origin --tags -f
fi

# ===================== GitHub Opa-Org (skovnats) =========
if should_run "$GITHUB_OPA"; then
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
fi

# ===================== GitLab ============================
if should_run "$GITLAB"; then
    echo "===> Sync to GitLab"
    git remote remove gitlab 2>/dev/null || true
    git remote add gitlab git@gitlab.com:opa-collective/sve.git
    git push gitlab 'refs/heads/*:refs/heads/*' --prune --force
    git push gitlab --tags -f
fi

# ===================== Codeberg ==========================
if should_run "$CODEBERG"; then
    echo "===> Sync to Codeberg"
    git remote remove codeberg 2>/dev/null || true
    git remote add codeberg "https://$CODEBERG_USER:$CODEBERG_API@codeberg.org/$CODEBERG_USER/$CODEBERG_REPO.git"
    git push codeberg 'refs/heads/*:refs/heads/*' --prune --force
    git push codeberg --tags -f
fi

# ===================== SourceForge =======================
if should_run "$SOURCEFORGE"; then
    echo "===> Sync to SourceForge"
    SF_USER="skovnats"         # Ваш логин
    SF_PROJECT="sve"  # Имя проекта (URL-адрес проекта)

    git remote remove sourceforge 2>/dev/null || true
    # git remote add sourceforge "ssh://$SF_USER@git.code.sf.net/p/$SF_PROJECT/code"
    git remote add sourceforge "https://skovnats@git.code.sf.net/p/sve/code" 2>/dev/null || true

    # Первая синхронизация требует --force из-за перезаписи истории
    git push sourceforge 'refs/heads/*:refs/heads/*' --prune --force
    git push sourceforge --tags -f
    git push sourceforge master --force
fi


# ===================== MEGA S4 (S3) =======================
if should_run "$MEGA"; then
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
      --exclude "*.DS_Store" \
      --exclude "*.DS_Store/**" \
      --progress
fi

# ===================== PROTON =======================
if should_run "$PROTON"; then
    echo "===> Sync to Proton Drive"
    rclone copy "$BASE_DIR" "proton:sve-backups/" \
        --exclude ".git/**" \
        --exclude ".github/**" \
        --exclude "artifacts/**" \
        --exclude "*.DS_Store" \
        --exclude "*.DS_Store/**" \
        --exclude "._*" \
        --progress \
        --transfers 4 \
        --checkers 8 \
        --buffer-size 64M
fi

# ===================== Radicle (P2P) =====================
if should_run "$RADICLE"; then
    echo "===> Sync to Radicle"
    if command -v rad >/dev/null 2>&1; then
        git push rad master -f --quiet || true
        rad sync --announce
    fi
fi

# ===================== GitFlic ===========================
if should_run "$GITFLIC"; then
    echo "===> Sync to GitFlic"
    git remote remove gitflic 2>/dev/null || true
    git remote add gitflic "git@gitflic.ru:$GITFLIC_USER/$GITFLIC_REPO.git"

    # Пробуем пуш веток. Если падает (из-за лимита), пропускаем, чтобы не стопорить MEGA
    git push gitflic 'refs/heads/*:refs/heads/*' --prune --force -q || echo "GitFlic branches failed (limit?)"

    for tag in $(git tag); do
        git push gitflic "$tag" -f -q 2>/dev/null || true
    done
fi

echo "===> ALL DONE"

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