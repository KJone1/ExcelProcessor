# /// script
# dependencies = [
#   "actualpy>=0.17.0",
#   "python-dotenv>=1.2.1",
# ]
# ///

import os
import sys
from datetime import date
from collections.abc import Iterable
from typing import Any
from dotenv import load_dotenv
from actual import Actual
from actual.queries import (
    create_budget,
    get_budgets,
    get_categories,
    get_transactions,
)

sys.path.append(os.getcwd())
_loaded = load_dotenv()

server_url = os.getenv("ACTUAL_SERVER_URL")
password = os.getenv("ACTUAL_PASSWORD")
budget_id = os.getenv("ACTUAL_BUDGET_ID")

if not (server_url and password and budget_id):
    print("Error: Missing Actual Budget configuration in .env file.", file=sys.stderr)
    raise SystemExit(1)


def discover_budget_months(budgets: Iterable[Any], transactions: Iterable[Any]) -> list[int]:
    months_set: set[int] = set()
    for b in budgets:
        if b.month is not None:
            months_set.add(b.month)

    for t in transactions:
        if not t.tombstone and t.date is not None:
            date_str = str(t.date).replace("-", "")
            if len(date_str) >= 6 and date_str[:6].isdigit():
                months_set.add(int(date_str[:6]))

    return sorted(list(months_set))


def map_budget_data(budgets: Iterable[Any]) -> dict[tuple[int, str], tuple[int, int]]:
    budget_data: dict[tuple[int, str], tuple[int, int]] = {}
    for b in budgets:
        if b.month is not None and b.category_id is not None:
            budget_data[(b.month, b.category_id)] = (b.amount or 0, b.carryover or 0)
    return budget_data


def map_spent_by_category_and_month(transactions: Iterable[Any]) -> dict[tuple[int, str], int]:
    spent_map: dict[tuple[int, str], int] = {}
    for t in transactions:
        if t.tombstone or not t.category_id or t.date is None:
            continue
        date_str = str(t.date).replace("-", "")
        if len(date_str) >= 6 and date_str[:6].isdigit():
            month_int = int(date_str[:6])
            key = (month_int, t.category_id)
            spent_map[key] = spent_map.get(key, 0) + (t.amount or 0)
    return spent_map


with Actual(base_url=server_url, password=password) as actual:
    print(f"🔌 Connecting to budget: {budget_id}...")
    _file = actual.set_file(budget_id)
    _download = actual.download_budget()
    session = actual.session

    budgets = get_budgets(session)
    transactions = get_transactions(session)
    categories = get_categories(session)

    months_to_fix = discover_budget_months(budgets, transactions)

    if not months_to_fix:
        print("❌ No months found in budgets or transactions to process.")
        sys.exit(0)

    print(f"🔍 Analyzing {len(months_to_fix)} months in the budget database...")

    budget_data = map_budget_data(budgets)
    spent_map = map_spent_by_category_and_month(transactions)

    months_changed = set()
    for month_int in months_to_fix:
        year = month_int // 100
        month = month_int % 100
        month_date = date(year, month, 1)
        month_str = month_date.strftime("%Y-%m")

        changes_in_month = 0
        categories_changed = []
        for cat_obj in categories:
            if cat_obj.is_income or cat_obj.tombstone or cat_obj.id is None:
                continue

            _budgeted, carryover = budget_data.get((month_int, cat_obj.id), (0, 0))
            spent = spent_map.get((month_int, cat_obj.id), 0)

            # Budgeted = -(Carryover + Spent)
            new_budgeted_cents = -(carryover + spent)
            new_budgeted_units = new_budgeted_cents / 100.0

            current_budgeted_cents, _current_carryover = budget_data.get((month_int, cat_obj.id), (0, 0))
            if new_budgeted_cents != current_budgeted_cents:
                _new_budget = create_budget(session, month_date, cat_obj, new_budgeted_units)
                changes_in_month += 1
                current_budgeted_units = current_budgeted_cents / 100.0
                categories_changed.append(
                    (cat_obj.name, current_budgeted_units, new_budgeted_units)
                )

        if changes_in_month > 0:
            print(f"\n✨ Zeroing out balances for: {month_str}")

            # Format and align columns dynamically for premium output
            formatted_items = []
            for cat_name, current_val, new_val in categories_changed:
                curr_str = f"{current_val:+.2f}"
                new_str = f"{new_val:+.2f}"
                formatted_items.append((cat_name, curr_str, new_str))

            max_name_len = max(len(item[0]) for item in formatted_items)
            max_curr_len = max(len(item[1]) for item in formatted_items)
            max_new_len = max(len(item[2]) for item in formatted_items)

            for idx, (cat_name, curr_str, new_str) in enumerate(formatted_items):
                prefix = "   ├── " if idx < len(formatted_items) - 1 else "   └── "
                print(f"{prefix}{cat_name:<{max_name_len}}  |  {curr_str:>{max_curr_len}} ──> {new_str:>{max_new_len}}")

            months_changed.add(month_int)

    if months_changed:
        print("\n💾 Committing changes...")
        actual.commit()
        _ = actual.sync()
    else:
        print("\n✨ All category balances are already zeroed out. No changes were necessary.")
