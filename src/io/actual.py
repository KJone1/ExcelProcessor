import csv
import os
from datetime import date, datetime

from actual import Actual
from actual.queries import (
    create_transaction,
    get_accounts,
    get_categories,
)
from dotenv import load_dotenv

from src.models.pdf import PayslipData


def import_payslip_to_actual(payslip_data: PayslipData) -> None:
    _ = load_dotenv()

    server_url = os.getenv("ACTUAL_SERVER_URL")
    password = os.getenv("ACTUAL_PASSWORD")
    budget_id = os.getenv("ACTUAL_BUDGET_ID")

    if not (server_url and password and budget_id):
        raise ValueError("Missing Actual Budget configuration")

    with Actual(base_url=server_url, password=password) as actual:
        print(f"Connecting to budget: {budget_id}")
        _ = actual.set_file(budget_id)
        _ = actual.download_budget()
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

        _ = create_transaction(
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
        _ = actual.sync()
        print("Done.")


def import_transactions_to_actual(csv_path: str) -> None:
    _ = load_dotenv()

    server_url = os.getenv("ACTUAL_SERVER_URL")
    password = os.getenv("ACTUAL_PASSWORD")
    budget_id = os.getenv("ACTUAL_BUDGET_ID")

    if not (server_url and password and budget_id):
        raise ValueError("Missing Actual Budget configuration")

    with Actual(base_url=server_url, password=password) as actual:
        print(f"Connecting to budget: {budget_id}")
        _ = actual.set_file(budget_id)
        _ = actual.download_budget()
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

                _ = create_transaction(
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

        if count > 0:
            print(f"Imported {count} transactions.")

            print("Committing changes...")
            actual.commit()
            _ = actual.sync()
            print("Done.")
        else:
            print("No transactions found to import.")
