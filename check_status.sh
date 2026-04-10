#!/usr/bin/env bash
set -euo pipefail

LOCAL_MASTER=$(git rev-parse master)
LOCAL_STAGING=$(git rev-parse staging)
REMOTES=("origin" "gitlab" "codeberg" "sourceforge" "gitflic")

echo "Checking mirrors status..."

for remote in "${REMOTES[@]}"; do
    if git remote | grep -q "$remote"; then
        # Получаем хеши с сервера без скачивания объектов
        REMOTE_HASH=$(git ls-remote "$remote" refs/heads/master | awk '{print $1}' || echo "OFFLINE")
        
        if [ "$LOCAL_MASTER" == "$REMOTE_HASH" ]; then
            echo "✅ $remote: In sync"
        elif [ "$REMOTE_HASH" == "OFFLINE" ]; then
            echo "❌ $remote: Unreachable"
        else
            echo "🔄 $remote: Update needed"
        fi
    fi
done