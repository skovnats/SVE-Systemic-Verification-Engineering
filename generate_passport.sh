#!/usr/bin/env bash
set -euo pipefail

echo "🔐 Генерация криптографического паспорта проекта..."

if [ ! -f "hashsum.md" ]; then
    echo "❌ Ошибка: hashsum.md не найден."
    exit 1
fi

# Проверка статуса PDF
PDF_STATUS="OK"
if [ -f "pdf_report.csv" ]; then
    if grep -q "CORRUPTED" "pdf_report.csv"; then
        PDF_STATUS="CORRUPTED (Вмешательство или сбой)"
        echo "⚠️ ВНИМАНИЕ: Обнаружены битые PDF файлы! Паспорт зафиксирует ошибку."
    fi
else
    PDF_STATUS="NO_PDF_REPORT"
fi

# Вычисление корневого хэша
HASHSUM_SHA=$(shasum -a 256 hashsum.md | awk '{print $1}')
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

# Запись паспорта
cat <<EOF > passport.txt
SVE INTEGRITY PASSPORT
======================
Date (UTC): $TIMESTAMP
PDF Status: $PDF_STATUS
Root Hash (hashsum.md SHA256): $HASHSUM_SHA
EOF

echo "✅ Паспорт создан: passport.txt"