init: clean
    #!/usr/bin/env bash
    set -euo pipefail
    DOWNLOADS_DIR="$HOME/Downloads"

    shopt -s nullglob
    files=("$DOWNLOADS_DIR"/*.xlsx)
    payslip_files=("$DOWNLOADS_DIR"/payslip*.pdf)
    shopt -u nullglob

    count=${#files[@]}
    if [ "$count" -gt 1 ]; then
        echo "Error: Multiple .xlsx files found in $DOWNLOADS_DIR:"
        for file in "${files[@]}"; do
            echo "  - $(basename "$file")"
        done
        echo "Please remove the old ones."
        exit 1
    elif [ "$count" -eq 0 ]; then
        echo "Error: No .xlsx files found in $DOWNLOADS_DIR."
        exit 1
    fi

    target_file="${files[0]}"
    echo "Found file: $target_file"
    cp "$target_file" data.xlsx
    echo "Copied $(basename "$target_file") to data.xlsx."

    payslip_count=${#payslip_files[@]}
    if [ "$payslip_count" -gt 1 ]; then
        echo "Error: Multiple payslip*.pdf files found in $DOWNLOADS_DIR:"
        for file in "${payslip_files[@]}"; do
            echo "  - $(basename "$file")"
        done
        echo "Please remove the old ones."
        exit 1
    elif [ "$payslip_count" -eq 0 ]; then
        echo "Warning: No payslip*.pdf files found in $DOWNLOADS_DIR."
    else
        target_payslip="${payslip_files[0]}"
        echo "Found payslip: $target_payslip"
        cp "$target_payslip" payslip.pdf
        echo "Copied $(basename "$target_payslip") to payslip.pdf."
    fi

    uv sync

run: init
    uv run python -m src.main
    @echo "Pipeline executed successfully"

clean:
    rm -f *.xlsx actual.csv *.pdf expense_report.md out.xlsx


lint:
    uv run basedpyright
    uv run mypy src scripts
    uv run flake8 --ignore=E501 src scripts
    uv run pylint --disable=C0301,C0114,C0116 src scripts

test:
    uv run pytest

[default]
explore:
    @uv run scripts/list_accounts.py
    @echo ""
    @uv run scripts/list_categories.py
    @echo ""
    @uv run scripts/list_tags.py
    @echo ""
    @uv run scripts/list_payees.py

zero-out:
    @uv run scripts/zero_out_balances.py
