#!/usr/bin/env bash

if [ ! -f "hashsum.md" ]; then
    echo "❌ hashsum.md не найден."
    exit 1
fi

echo "🔍 Проверка измененных файлов..."

# Запуск аудита (выведет конкретные файлы с несовпадающим хэшем или новые)
hashdeep -a -k hashsum.md -r . 2>&1 | grep -E -i "no match|not found|audit failed" || echo "✅ Все файлы совпадают с hashsum.md"