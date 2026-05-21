init:
    uv sync

clean:
    rm -f *.xlsx actual.csv *.pdf

lint:
    uv run basedpyright
    uv run mypy src explore
    uv run flake8 --ignore=E501 src explore
    uv run vulture src explore --exclude src/core/categories.py,src/models/actual.py
    uv run bandit -r src explore
    uv run pylint --disable=C0301,C0114,C0116 src explore

test:
    uv run pytest

explore:
    @uv run explore/explore_accounts.py
    @echo ""
    @uv run explore/explore_categories.py
