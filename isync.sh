#!/usr/bin/env bash
set -euo pipefail

BASE_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$BASE_DIR"

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
            --codeberg) CODEBERG=false; shift ;; # Добавьте true если нужно
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

echo "===> Starting Incremental Sync"

# 1. Настройка Remotes (если их нет)
git remote add org-mirror git@github.com:Opa-Collective/SVE-Systemic-Verification-Engineering.git 2>/dev/null || true
git remote add sourceforge "ssh://skovnats@git.code.sf.net/p/sve-systemic/code" 2>/dev/null || true

# 2. Основной инкрементальный цикл
# Добавили sourceforge в общий список — теперь он пушится быстро
# REMOTES=("origin" "gitlab" "codeberg" "sourceforge")
REMOTES=()
if should_run "$GITHUB_SKOVNATS"; then REMOTES+=("origin"); fi
if should_run "$GITLAB"; then REMOTES+=("gitlab"); fi
if should_run "$CODEBERG"; then REMOTES+=("codeberg"); fi
if should_run "$SOURCEFORGE"; then REMOTES+=("sourceforge"); fi

for remote in "${REMOTES[@]}"; do
    if git remote | grep -q "$remote"; then
        echo "--> Pushing to $remote..."
        # Стандартный пуш без --force — это и есть инкрементальное добавление
        git push "$remote" master -q || echo "⚠️ Master failed for $remote"
        git push "$remote" staging -q || echo "⚠️ Staging failed for $remote"
        git push "$remote" --tags -q || true
    fi
done


# === GitFlic ===
if should_run "$GITFLIC"; then
    echo "===> Sync to GitFlic"
    git push gitflic master -f -q || echo "❌ GitFlic master failed"
    git push gitflic --tags -q || true
fi

# === GitHub Opa-Org ===
if should_run "$GITHUB_OPA"; then
    echo "--> Syncing GitHub Opa-Org..."
    git checkout -B temp-org-sync -q
    git rm -rf "Applications/Ангелы-Хранетили" --ignore-unmatch -q
    git commit -m "chore: incremental update" --quiet || true
    git push org-mirror temp-org-sync:master --force -q
    git push org-mirror --tags -f -q || true # Пушим теги принудительно
    git checkout master -q
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
    # 4. Radicle (P2P)
    if command -v rad >/dev/null 2>&1; then
        echo "--> Syncing Radicle..."
        git push rad master -q 2>/dev/null || true
        rad sync --announce
    fi
fi

echo "===> ALL MIRRORS UPDATED!"


# # 4. Облака (MEGA & GDrive)
# # rclone по умолчанию инкрементален — он докачивает только разницу
# echo "--> Syncing Cloud Storage..."
# rclone sync "$BASE_DIR" "megas4:${MEGA_BUCKET}" \
#   --exclude ".git/**" --exclude ".github/**" --exclude "artifacts/**" \
#   --fast-list --progress

# echo "===> All mirrors updated!"