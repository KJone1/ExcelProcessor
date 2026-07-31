import csv
import io
from datetime import date
from decimal import Decimal
from types import SimpleNamespace

import pytest

from scripts import list_transactions


@pytest.mark.parametrize("month", ["6", "06", "june", "JUNE", "June"])
def test_numeric_and_named_months_use_current_year(month):
    assert list_transactions.parse_cli_args([month], current_year=2026) == (
        date(2026, 6, 1),
        date(2026, 7, 1),
    )


def test_explicit_year_selects_complete_month():
    assert list_transactions.parse_cli_args(["june", "2025"]) == (
        date(2025, 6, 1),
        date(2025, 7, 1),
    )


def test_december_boundary_rolls_into_next_year():
    assert list_transactions.parse_cli_args(["12", "2025"]) == (
        date(2025, 12, 1),
        date(2026, 1, 1),
    )


@pytest.mark.parametrize(
    "arguments",
    [
        [],
        ["june", "2025", "extra"],
        ["0"],
        ["13"],
        ["not-a-month"],
        ["june", "twenty-five"],
        ["june", "25"],
    ],
)
def test_invalid_arguments_exit_nonzero(arguments, capsys):
    assert list_transactions.main(arguments) == 1
    assert capsys.readouterr().err.startswith("Error: ")


def test_transaction_record_exposes_required_fields():
    transaction = SimpleNamespace(
        get_date=lambda: date(2025, 6, 15),
        get_amount=lambda: Decimal("-12.34"),
        account=SimpleNamespace(name="Checking"),
        payee=SimpleNamespace(name="Coffee Shop"),
        category=SimpleNamespace(name="Eating out"),
        notes="Breakfast",
        transferred_id="transfer-id",
    )

    assert list_transactions.transaction_record(transaction) == {
        "date": "2025-06-15",
        "amount": "-12.34",
        "account": "Checking",
        "payee": "Coffee Shop",
        "category": "Eating out",
        "notes": "Breakfast",
        "is_transfer": True,
    }


def test_main_queries_exact_range_and_prints_transactions(monkeypatch, capsys):
    transaction = SimpleNamespace(
        get_date=lambda: date(2025, 6, 30),
        get_amount=lambda: Decimal("42.00"),
        account=SimpleNamespace(name="Checking"),
        payee=None,
        category=None,
        notes=None,
        transferred_id=None,
        tombstone=False,
    )
    query_arguments = {}

    class FakeActual:
        """Minimal Actual context manager used by this test."""

        session = object()

        def __init__(self, base_url, password):
            assert base_url == "https://actual.example"
            assert password == "secret"

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_value, traceback):
            return False

        def set_file(self, budget_id):
            assert budget_id == "budget-id"

        def download_budget(self):
            return None

    def fake_get_transactions(session, **kwargs):
        assert session is FakeActual.session
        query_arguments.update(kwargs)
        return [transaction]

    monkeypatch.setattr(
        list_transactions,
        "load_configuration",
        lambda: ("https://actual.example", "secret", "budget-id"),
    )
    monkeypatch.setattr(list_transactions, "Actual", FakeActual)
    monkeypatch.setattr(list_transactions, "get_transactions", fake_get_transactions)

    assert list_transactions.main(["june", "2025"]) == 0
    assert query_arguments == {
        "start_date": date(2025, 6, 1),
        "end_date": date(2025, 7, 1),
    }
    output = list(
        csv.DictReader(io.StringIO(capsys.readouterr().out), delimiter="\t")
    )
    assert output == [
        {
            "date": "2025-06-30",
            "amount": "42.00",
            "account": "Checking",
            "payee": "",
            "category": "",
            "notes": "",
            "is_transfer": "false",
        }
    ]


def test_empty_month_succeeds_and_reports_empty_result(monkeypatch, capsys):
    monkeypatch.setattr(list_transactions, "list_transactions", lambda *_: [])

    assert list_transactions.main(["june", "2025"]) == 0
    assert capsys.readouterr().out == "\t".join(list_transactions.OUTPUT_FIELDS) + "\n"


def test_missing_configuration_exits_nonzero(monkeypatch, capsys):
    for variable in (
        "ACTUAL_SERVER_URL",
        "ACTUAL_PASSWORD",
        "ACTUAL_BUDGET_ID",
    ):
        monkeypatch.delenv(variable, raising=False)
    monkeypatch.setattr(list_transactions, "load_dotenv", lambda: False)

    assert list_transactions.main(["june", "2025"]) == 1
    assert "Missing Actual Budget configuration" in capsys.readouterr().err
