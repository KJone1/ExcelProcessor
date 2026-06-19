init:
    uv sync

run:
    ./run.sh

clean:
    rm -f *.xlsx actual.csv *.pdf

lint:
    uv run basedpyright
    uv run mypy src scripts
    uv run flake8 --ignore=E501 src scripts
    uv run vulture src scripts --exclude src/core/categories.py,src/models/actual.py
    uv run bandit -r src scripts
    uv run pylint --disable=C0301,C0114,C0116 src scripts

test:
    uv run pytest

explore:
    @uv run scripts/explore_accounts.py
    @echo ""
    @uv run scripts/explore_categories.py

zero-out:
    @uv run scripts/zero_out_balances.py
