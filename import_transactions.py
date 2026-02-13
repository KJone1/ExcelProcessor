import os
import csv
import sys
from datetime import datetime
from dotenv import load_dotenv
from actual import Actual
from actual.queries import get_accounts, get_categories, create_transaction

# Load environment variables
load_dotenv()

SERVER_URL = os.getenv("ACTUAL_SERVER_URL")
PASSWORD = os.getenv("ACTUAL_PASSWORD")
BUDGET_ID = os.getenv("ACTUAL_BUDGET_ID")
INPUT_FILE = "actual.csv"

def main():
    if not SERVER_URL or not PASSWORD or not BUDGET_ID:
        print("Error: Missing configuration in .env")
        print("Please ensure ACTUAL_SERVER_URL, ACTUAL_PASSWORD, and ACTUAL_BUDGET_ID are set.")
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

        # Read CSV
        print(f"Reading {INPUT_FILE}...")
        with open(INPUT_FILE, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            count = 0
            for row in reader:
                # Expected headers: Date, Payee, Amount, Category
                try:
                    date_str = row['Date']
                    payee = row['Payee']
                    amount_str = row['Amount']
                    category_name = row['Category']
                    
                    if not date_str or not amount_str:
                        continue

                    date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
                    amount_float = float(amount_str)
                    
                    # Convert to cents and invert sign
                    # CSV: Positive = Expense, Negative = Income
                    # Actual: Negative = Expense, Positive = Income
                    amount_cents = int(round(amount_float * 100)) * -1
                    
                    category = cat_map.get(category_name)
                    
                    create_transaction(
                        session,
                        date=date_obj,
                        account=account,
                        payee=payee,
                        category=category,
                        amount=amount_cents,
                        notes="Imported via script"
                    )
                    count += 1
                except Exception as e:
                    print(f"Error processing row {row}: {e}")
        
        if count > 0:
            print(f"Committing {count} transactions...")
            actual.commit()
            actual.sync()
            print("Done.")
        else:
            print("No transactions found to import.")

if __name__ == "__main__":
    main()
