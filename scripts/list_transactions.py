# /// script
# dependencies = [
#   "actualpy>=0.17.0",
#   "python-dotenv>=1.2.1",
# ]
# ///
# pylint: disable=duplicate-code

import csv
import os
import sys
from collections.abc import Sequence
from datetime import date
from typing import Any

from actual import Actual
from actual.queries import get_transactions
from dotenv import load_dotenv

USAGE = "Usage: uv run scripts/list_transactions.py <month> [year]"
MONTHS = {
    "january": 1,
    "february": 2,
    "march": 3,
    "april": 4,
    "may": 5,
    "june": 6,
    "july": 7,
    "august": 8,
    "september": 9,
    "october": 10,
    "november": 11,
    "december": 12,
}
OUTPUT_FIELDS = (
    "date",
    "amount",
    "account",
    "payee",
    "category",
    "notes",
    "is_transfer",
)


def parse_month(value: str) -> int:
    normalized = value.casefold()
    if normalized in MONTHS:
        return MONTHS[normalized]

    if value.isdecimal():
        month = int(value)
        if 1 <= month <= 12:
            return month

    raise ValueError(f"Invalid month: {value}. Use 1-12 or an English month name.")


def parse_year(value: str) -> int:
    if not value.isdecimal():
        raise ValueError(f"Invalid year: {value}. Use a four-digit year.")

    year = int(value)
    if len(value) != 4 or not 1 <= year <= 9999:
        raise ValueError(f"Invalid year: {value}. Use a four-digit year.")
    return year


def month_boundaries(month: int, year: int) -> tuple[date, date]:
    start_date = date(year, month, 1)
    if month == 12:
        if year == 9999:
            raise ValueError("Invalid date range: December 9999 has no supported end date.")
        end_date = date(year + 1, 1, 1)
    else:
        end_date = date(year, month + 1, 1)
    return start_date, end_date


def parse_cli_args(
    arguments: Sequence[str], current_year: int | None = None
) -> tuple[date, date]:
    if len(arguments) not in (1, 2):
        raise ValueError(USAGE)

    month = parse_month(arguments[0])
    year = (
        parse_year(arguments[1])
        if len(arguments) == 2
        else current_year or date.today().year
    )
    return month_boundaries(month, year)


def load_configuration() -> tuple[str, str, str]:
    _ = load_dotenv()
    server_url = os.getenv("ACTUAL_SERVER_URL")
    password = os.getenv("ACTUAL_PASSWORD")
    budget_id = os.getenv("ACTUAL_BUDGET_ID")

    if not (server_url and password and budget_id):
        raise ValueError("Missing Actual Budget configuration in .env file.")
    return server_url, password, budget_id


def relationship_name(relationship: Any) -> str | None:
    if relationship is None:
        return None
    return getattr(relationship, "name", None)


def transaction_record(transaction: Any) -> dict[str, str | bool | None]:
    return {
        "date": transaction.get_date().isoformat(),
        "amount": str(transaction.get_amount()),
        "account": relationship_name(transaction.account),
        "payee": relationship_name(transaction.payee),
        "category": relationship_name(transaction.category),
        "notes": transaction.notes,
        "is_transfer": transaction.transferred_id is not None,
    }


def list_transactions(start_date: date, end_date: date) -> list[dict[str, str | bool | None]]:
    server_url, password, budget_id = load_configuration()
    with Actual(base_url=server_url, password=password) as actual:
        _ = actual.set_file(budget_id)
        _ = actual.download_budget()
        transactions = get_transactions(
            actual.session,
            start_date=start_date,
            end_date=end_date,
        )
        return [
            transaction_record(transaction)
            for transaction in transactions
            if not getattr(transaction, "tombstone", False)
        ]


def write_tsv(transactions: Sequence[dict[str, str | bool | None]]) -> None:
    writer = csv.writer(sys.stdout, delimiter="\t", lineterminator="\n")
    writer.writerow(OUTPUT_FIELDS)
    for transaction in transactions:
        writer.writerow(
            str(transaction[field]).lower()
            if field == "is_transfer"
            else transaction[field]
            for field in OUTPUT_FIELDS
        )


def main(arguments: Sequence[str] | None = None) -> int:
    try:
        start_date, end_date = parse_cli_args(
            sys.argv[1:] if arguments is None else arguments
        )
        transactions = list_transactions(start_date, end_date)
    except ValueError as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1

    write_tsv(transactions)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
