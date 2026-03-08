from datetime import date
from typing import Any

from actual import Actual
from actual.queries import (
    create_budget,
    create_transaction,
    get_accounts,
    get_budgets,
    get_categories,
    get_transactions,
)
from returns.result import safe

from src.models.actual import ActualConfig, Transaction


@safe
def import_transactions_to_actual(
    config: ActualConfig, transactions: list[Transaction]
) -> None:
    with Actual(base_url=config.server_url, password=config.password) as actual:
        actual.set_file(config.budget_id)
        actual.download_budget()
        session = actual.session

        accounts = get_accounts(session)
        categories = get_categories(session)
        cat_map = {c.name: c for c in categories}

        affected_months: set[int] = set()

        for trans in transactions:
            # Default to first account if not found
            account = next(
                (a for a in accounts if a.name == trans.account), accounts[0]
            )
            category = cat_map.get(trans.category) if trans.category else None

            create_transaction(
                session,
                date=trans.date,
                account=account,
                payee=trans.payee,
                category=category,
                amount=trans.amount,
                notes=trans.notes,
            )
            affected_months.add(int(trans.date.strftime("%Y%m")))

        # Zero out balances for affected months
        _zero_out_balances(session, categories, sorted(list(affected_months)))

        actual.commit()
        actual.sync()


def _zero_out_balances(session: Any, categories: Any, months_to_fix: list[int]) -> None:
    budgets = get_budgets(session)
    transactions = get_transactions(session)

    # Map budget data: (month_int, cat_id) -> (budgeted, carryover)
    budget_data: dict[tuple[int, str], tuple[int, int]] = {}
    for b in budgets:
        budget_data[(b.month, b.category_id)] = (b.amount, b.carryover)

    # Map spent amounts: (month_int, cat_id) -> amount
    spent_map: dict[tuple[int, str], int] = {}
    for t in transactions:
        if t.tombstone or not t.category_id:
            continue
        month_int = int(str(t.date)[:6])
        key = (month_int, t.category_id)
        spent_map[key] = spent_map.get(key, 0) + t.amount

    for month_int in months_to_fix:
        year = month_int // 100
        month = month_int % 100
        month_date = date(year, month, 1)

        for cat_obj in categories:
            if cat_obj.is_income or cat_obj.tombstone:
                continue

            _, carryover = budget_data.get((month_int, cat_obj.id), (0, 0))
            spent = spent_map.get((month_int, cat_obj.id), 0)

            # Budgeted = -(Carryover + Spent)
            new_budgeted_cents = -(carryover + spent)
            new_budgeted_units = new_budgeted_cents / 100.0

            current_budgeted_cents, _ = budget_data.get((month_int, cat_obj.id), (0, 0))
            if new_budgeted_cents != current_budgeted_cents:
                create_budget(session, month_date, cat_obj, new_budgeted_units)
