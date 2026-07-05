#!/usr/bin/env bash
set -euo pipefail

if [ ! -f "hashsum.md" ]; then
    echo "❌ hashsum.md не найден."
    exit 1
fi

echo "🔍 Проверка измененных файлов..."

# -a (audit): режим сверки
# -k: путь к файлу с известными хэшами
# -r .: рекурсивная проверка текущей директории[cite: 2, 3]
hashdeep -a -k hashsum.md -r . 2>&1 | grep -i "FAILED" || echo "✅ Все файлы совпадают с hashsum.md"