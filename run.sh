#!/usr/bin/env bash
set -euo pipefail

for file in data.xlsx expense_report.md out.xlsx; do
    [ -f "$file" ] && rm "$file"
done

DOWNLOADS_DIR="$HOME/Downloads"

shopt -s nullglob
files=("$DOWNLOADS_DIR"/*.xlsx)
shopt -u nullglob

count=${#files[@]}

if [ "$count" -gt 1 ]; then
    echo "Error: Multiple .xlsx files found in $DOWNLOADS_DIR:"
    for file in "${files[@]}"; do
        echo "  - $(basename "$file")"
    done
    echo "Please remove the old ones and keep only the up-to-date one."
    exit 1
elif [ "$count" -eq 0 ]; then
    echo "Error: No .xlsx files found in $DOWNLOADS_DIR."
    exit 1
fi

target_file="${files[0]}"
echo "Found file: $target_file"
cp "$target_file" data.xlsx
echo "Copied $(basename "$target_file") to data.xlsx."

uv sync
uv run main.py
uv run generate_csv.py
uv run import_transactions.py

echo "Transactions imported successfully"

