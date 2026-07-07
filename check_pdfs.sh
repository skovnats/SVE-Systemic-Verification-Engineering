#!/usr/bin/env bash
set -euo pipefail

TARGET_DIR="${1:-.}"
REPORT="pdf_report.csv"

echo "Имя файла,Полный путь,Статус" > "$REPORT"
echo "🔍 Сканирование папки: $TARGET_DIR"

find "$TARGET_DIR" -type f -iname "*.pdf" -print0 | while IFS= read -r -d $'\0' file; do
    filename=$(basename "$file")
    
    # Ghostscript пытается отрендерить файл в пустоту. Если есть ошибки структуры - выдаст ошибку.
    if gs -q -dNOPAUSE -dBATCH -sDEVICE=nullpage "$file" >/dev/null 2>&1; then
        echo "✅ OK: $filename"
        echo "\"$filename\",\"$file\",\"OK\"" >> "$REPORT"
    else
        echo "❌ ОШИБКА: $filename"
        echo "\"$filename\",\"$file\",\"CORRUPTED\"" >> "$REPORT"
    fi
done

echo "📄 Готово! Отчет сохранен в $REPORT"