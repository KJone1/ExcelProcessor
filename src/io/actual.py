import csv
import os
from datetime import date, datetime
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
from dotenv import load_dotenv

from src.models.pdf import PayslipData


def import_payslip_to_actual(payslip_data: PayslipData) -> None:
    load_dotenv()

    server_url = os.getenv("ACTUAL_SERVER_URL")
    password = os.getenv("ACTUAL_PASSWORD")
    budget_id = os.getenv("ACTUAL_BUDGET_ID")

    assert server_url and password and budget_id, "Missing Actual Budget configuration"

    with Actual(base_url=server_url, password=password) as actual:
        print(f"Connecting to budget: {budget_id}")
        actual.set_file(budget_id)
        actual.download_budget()
        session = actual.session

        accounts = get_accounts(session)
        account = next(a for a in accounts if a.name and "Poalim" in a.name)
        print(f"Importing to account: {account.name}")

        categories = get_categories(session)
        category = next(c for c in categories if c.name == "Income")

        # The transaction date is already calculated as the 1st of the next month in extract_payslip_date
        trans_date = payslip_data.date

        # The salary is for the previous month
        if trans_date.month == 1:
            salary_month = 12
            salary_year = trans_date.year - 1
        else:
            salary_month = trans_date.month - 1
            salary_year = trans_date.year
            
        salary_date = date(salary_year, salary_month, 1)
        month_name = salary_date.strftime("%B")
        description = f"Salary for {month_name}"

        create_transaction(
            session,
            date=trans_date,
            account=account,
            payee="Salary",
            category=category,
            amount=payslip_data.net_to_bank,
            notes=description,
        )

        print("Committing changes...")
        actual.commit()
        actual.sync()
        print("Done.")


def import_transactions_to_actual(csv_path: str) -> None:
    load_dotenv()

    server_url = os.getenv("ACTUAL_SERVER_URL")
    password = os.getenv("ACTUAL_PASSWORD")
    budget_id = os.getenv("ACTUAL_BUDGET_ID")

    assert server_url and password and budget_id, "Missing Actual Budget configuration"

    with Actual(base_url=server_url, password=password) as actual:
        print(f"Connecting to budget: {budget_id}")
        actual.set_file(budget_id)
        actual.download_budget()
        session = actual.session

        # Get Account
        accounts = get_accounts(session)
        account = next(a for a in accounts if a.name and "Poalim" in a.name)
        print(f"Importing to account: {account.name}")

        # Get Categories map
        categories = get_categories(session)
        cat_map = {c.name: c for c in categories}

        affected_months: set[int] = set()

        # Read CSV
        print(f"Reading {csv_path}...")
        count = 0
        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    date_str = row.get("Date")
                    payee = row.get("Payee")
                    amount_str = row.get("Amount")
                    category_name = row.get("Category")

                    if not date_str or not amount_str:
                        continue

                    date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
                    amount_float = float(amount_str)

                    # Invert sign: CSV (Positive=Expense) -> Actual (Negative=Expense)
                    actual_amount = amount_float * -1

                    category = cat_map.get(category_name) if category_name else None

                    create_transaction(
                        session,
                        date=date_obj,
                        account=account,
                        payee=payee,
                        category=category,
                        amount=actual_amount,
                        notes="Imported via script",
                    )

                    affected_months.add(int(date_obj.strftime("%Y%m")))
                    count += 1
                except Exception as e:
                    print(f"Error processing row {row}: {e}")

        if count > 0:
            print(f"Imported {count} transactions. Adjusting budgets...")

            # Zero out balances for all affected months
            _zero_out_balances(session, categories, sorted(list(affected_months)))

            print("Committing changes...")
            actual.commit()
            actual.sync()
            print("Done.")
        else:
            print("No transactions found to import.")


def _zero_out_balances(session: Any, categories: Any, months_to_fix: list[int]) -> None:
    budgets = get_budgets(session)
    transactions = get_transactions(session)

    # Map budget data: (month_int, cat_id) -> (budgeted, carryover)
    budget_data: dict[tuple[int, str], tuple[int, int]] = {}
    for b in budgets:
        if b.month is not None and b.category_id is not None:
            budget_data[(b.month, b.category_id)] = (b.amount or 0, b.carryover or 0)

    # Map spent amounts: (month_int, cat_id) -> amount
    spent_map: dict[tuple[int, str], int] = {}
    for t in transactions:
        if t.tombstone or not t.category_id or t.date is None:
            continue
        month_int = int(str(t.date).replace("-", "")[:6])
        key = (month_int, t.category_id)
        spent_map[key] = spent_map.get(key, 0) + (t.amount or 0)

    for month_int in months_to_fix:
        year = month_int // 100
        month = month_int % 100
        month_date = date(year, month, 1)

        print(f"Zeroing out balances for: {month_date.strftime('%Y-%m')}")

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
