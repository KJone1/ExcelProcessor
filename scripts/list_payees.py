# /// script
# dependencies = [
#   "actualpy>=0.17.0",
#   "python-dotenv>=1.2.1",
# ]
# ///
# pylint: disable=duplicate-code

import os
import sys

from actual import Actual
from actual.queries import get_payees
from dotenv import load_dotenv

_ = load_dotenv()

server_url = os.getenv("ACTUAL_SERVER_URL")
password = os.getenv("ACTUAL_PASSWORD")
budget_id = os.getenv("ACTUAL_BUDGET_ID")

if not (server_url and password and budget_id):
    print("Error: Missing Actual Budget configuration in .env file.", file=sys.stderr)
    raise SystemExit(1)

with Actual(base_url=server_url, password=password) as actual:
    _ = actual.set_file(budget_id)
    _ = actual.download_budget()

    print("BUDGET PAYEES:")
    payees = get_payees(actual.session)
    active_payees = [
        payee for payee in payees
        if not getattr(payee, "tombstone", False)
    ]

    for payee in sorted(active_payees, key=lambda p: p.name or ""):
        transfer_info = f" (Transfer Account ID: {payee.transfer_acct})" if payee.transfer_acct else ""
        print(f"- {payee.name} (ID: {payee.id}){transfer_info}")
