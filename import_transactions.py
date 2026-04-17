import csv
import os
from datetime import datetime, date

from actual import Actual
from actual.queries import (
    create_transaction,
    get_accounts,
    get_categories,
    get_budgets,
    get_transactions,
    create_budget,
)
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

SERVER_URL = os.getenv("ACTUAL_SERVER_URL")
PASSWORD = os.getenv("ACTUAL_PASSWORD")
BUDGET_ID = os.getenv("ACTUAL_BUDGET_ID")
INPUT_FILE = "actual.csv"


def zero_out_balances(session, categories, months_to_fix):
    """Adjusts budgeted amounts so that Available balance becomes zero."""
    budgets = get_budgets(session)
    transactions = get_transactions(session)

    # Map budget data: (month_int, cat_id) -> (budgeted, carryover)
    budget_data = {}
    for b in budgets:
        budget_data[(b.month, b.category_id)] = (b.amount, b.carryover)

    # Map spent amounts: (month_int, cat_id) -> amount
    spent_map = {}
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


def main():
    if not SERVER_URL or not PASSWORD or not BUDGET_ID:
        print("Error: Missing configuration in .env")
        print(
            "Please ensure ACTUAL_SERVER_URL, ACTUAL_PASSWORD, and ACTUAL_BUDGET_ID are set."
        )
        return

    if not os.path.exists(INPUT_FILE):
        print(f"Error: {INPUT_FILE} not found. Please run generate_csv.py first.")
        return

    with Actual(base_url=SERVER_URL, password=PASSWORD) as actual:
        print(f"Connecting to budget: {BUDGET_ID}")
        actual.set_file(BUDGET_ID)
        actual.download_budget()
        session = actual.session

        # Get Account
        accounts = get_accounts(session)
        if not accounts:
            print("Error: No accounts found.")
            return

        # TODO: Allow selecting account via env var or arg? Defaulting to first one.
        account = accounts[0]
        print(f"Importing to account: {account.name}")

        # Get Categories map
        categories = get_categories(session)
        cat_map = {c.name: c for c in categories}

        affected_months = set()

        # Read CSV
        print(f"Reading {INPUT_FILE}...")
        with open(INPUT_FILE, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            count = 0
            for row in reader:
                # Expected headers: Date, Payee, Amount, Category
                try:
                    date_str = row["Date"]
                    payee = row["Payee"]
                    amount_str = row["Amount"]
                    category_name = row["Category"]

                    if not date_str or not amount_str:
                        continue

                    date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
                    amount_float = float(amount_str)

                    # Invert sign: CSV (Positive=Expense) -> Actual (Negative=Expense)
                    actual_amount = amount_float * -1

                    category = cat_map.get(category_name)

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
            zero_out_balances(session, categories, sorted(list(affected_months)))
            
            print("Committing changes...")
            actual.commit()
            actual.sync()
            print("Done.")
        else:
            print("No transactions found to import.")


if __name__ == "__main__":
    main()
