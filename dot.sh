#!/usr/bin/env bash
set -euo pipefail

BASE_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$BASE_DIR"

echo "--> 0. Сохранение чекпоинта..."
git checkout master -q
git branch checkpoint_12082026 2>/dev/null || true

echo "--> 1. Полный сброс master и создание чистой истории..."
git checkout --orphan temp_master -q
git rm -rf --cached . -q

# Удаляем конфигурацию LFS, так как вы от него отказываетесь
rm -f .gitattributes

echo "--> Выполнение пофайловых коммитов (это займет время)..."
git ls-files --others --exclude-standard | while read -r file; do
    if [ -f "$file" ]; then
        echo "--> Staging & committing: $file"
        git add "$file"
        git commit -m "Opa-init: add $(basename "$file")" --quiet
    fi
done

echo "--> Замена старой ветки master..."
git branch -D master || true
git branch -m temp_master master

echo "--> 2. Принудительная синхронизация со всеми зеркалами..."
# Вызов вашего существующего sync.sh, который поддерживает force-push всех веток
if [ -f "./sync.sh" ]; then
    bash ./sync.sh --all
else
    echo "❌ Ошибка: sync.sh не найден."
    exit 1
fi

echo "✅ Точка поставлена. Проект перезапущен."