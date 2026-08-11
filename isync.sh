#!/usr/bin/env bash
set -euo pipefail

BASE_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$BASE_DIR"
git checkout master -q

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

echo "===> Starting Incremental Sync"

# 1. Настройка Remotes (если их нет)
git remote add org-mirror git@github.com:Opa-Collective/SVE-Systemic-Verification-Engineering.git 2>/dev/null || true
# git remote add sourceforge "ssh://skovnats@git.code.sf.net/p/sve-systemic/code" 2>/dev/null || true
git remote add sourceforge "https://skovnats@git.code.sf.net/p/sve/code" 2>/dev/null || true

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
        echo "--> [$(date +%T)] Pushing to $remote... (Hold on, I'm checking)"
        
        # Убираем -q и добавляем --verbose, чтобы видеть каждый байт
        # Добавляем тайм-аут через SSH, чтобы не висело вечно
        # export GIT_SSH_COMMAND="ssh -o ConnectTimeout=10 -o BatchMode=yes"
        # Увеличиваем таймаут до 30 секунд и добавляем 2 повторные попытки соединения
        # export GIT_SSH_COMMAND="ssh -o ConnectTimeout=30 -o ConnectionAttempts=2 -o BatchMode=yes"
        export GIT_SSH_COMMAND="ssh -o ConnectTimeout=60 -o ServerAliveInterval=30 -o ServerAliveCountMax=10 -o ConnectionAttempts=3 -o BatchMode=yes -o IPQoS=throughput"
        
        git push "$remote" master --progress || echo "❌ Master FAILED for $remote"
        git push "$remote" staging --progress || echo "❌ Staging FAILED for $remote"
        git push "$remote" --tags -f || true
        
        echo "--> [$(date +%T)] Done with $remote."
    fi
done



# === GitHub Opa-Org ===
if should_run "$GITHUB_OPA"; then
    echo "--> [$(date +%T)] Starting Sync to GitHub Opa-Org (org-mirror)..."
    
    echo "    - Switching to temp-org-sync branch..."
    git checkout -B temp-org-sync || echo "❌ Failed to checkout"
    
    echo "    - Removing unwanted directories..."
    git rm -rf "Applications/Ангелы-Хранетили" --ignore-unmatch || true
    
    echo "    - Committing incremental update..."
    git commit -m "chore: incremental update [HoneyBadger Mode]" || echo "    - Nothing to commit"
    
    echo "    - Pushing code to org-mirror..."
    git push org-mirror temp-org-sync:master --force --progress
    
    echo "    - Pushing tags to org-mirror (Operation Ы)..."
    git push org-mirror --tags -f --verbose
    
    echo "    - Returning to master..."
    git checkout master -q
    echo "--> [$(date +%T)] GitHub Opa-Org Sync COMPLETED! ША!"
fi
git checkout master -q

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

# === GitFlic ===
if should_run "$GITFLIC"; then
    echo "===> Sync to GitFlic"
    git push gitflic master -f -q || echo "❌ GitFlic master failed"
    git push gitflic --tags -f -q || true
fi
git checkout master -q
echo "===> ALL MIRRORS UPDATED!"


# # 4. Облака (MEGA & GDrive)
# # rclone по умолчанию инкрементален — он докачивает только разницу
# echo "--> Syncing Cloud Storage..."
# rclone sync "$BASE_DIR" "megas4:${MEGA_BUCKET}" \
#   --exclude ".git/**" --exclude ".github/**" --exclude "artifacts/**" \
#   --fast-list --progress

# echo "===> All mirrors updated!"