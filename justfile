init:
    uv sync

clean:
    rm -f *.xlsx actual.csv *.pdf

lint:
    uv run basedpyright .
    uv run pyright .
    uv run mypy .
    uv run flake8 --ignore=E501 .
    uv run vulture .
    uv run bandit -r . --exclude .venv
    uv run pylint --disable=C0301 src tests *.py

test:
    uv run pytest
