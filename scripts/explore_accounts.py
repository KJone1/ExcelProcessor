# /// script
# dependencies = [
#   "actualpy>=0.17.0",
#   "python-dotenv>=1.2.1",
# ]
# ///

import os
import sys
from dotenv import load_dotenv
from actual import Actual
from actual.queries import get_accounts

_ = load_dotenv()

server_url = os.getenv("ACTUAL_SERVER_URL")
password = os.getenv("ACTUAL_PASSWORD")
budget_id = os.getenv("ACTUAL_BUDGET_ID")

if not (server_url and password and budget_id):
    print("Error: Missing Actual Budget configuration in .env file.", file=sys.stderr)
    raise SystemExit(1)


def balance(account):
    return sum(transaction.amount for transaction in account.transactions if not transaction.tombstone) / 100.0


with Actual(base_url=server_url, password=password) as actual:
    _ = actual.set_file(budget_id)
    _ = actual.download_budget()

    accounts = get_accounts(actual.session)
    active_accounts = [account for account in accounts if not getattr(account, "closed", False) and not getattr(account, "tombstone", False)]

    for header, is_offbudget in [("BUDGET ACCOUNTS", False), ("OFF-BUDGET ACCOUNTS", True)]:
        group = [account for account in active_accounts if bool(getattr(account, "offbudget", False)) == is_offbudget]
        if group:
            if is_offbudget:
                print()
            print(f"{header}:")
            for account in group:
                print(f"- {account.name} (ID: {account.id}) | Balance: {balance(account):,.2f}")
