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
from actual.queries import get_category_groups

sys.path.append(os.getcwd())
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

    print("CATEGORIES & GROUPS:")
    groups = get_category_groups(actual.session)
    active_groups = [group for group in groups if not getattr(group, "tombstone", False) and not getattr(group, "hidden", False)]

    for group in sorted(active_groups, key=lambda group: getattr(group, "sort_order", 0) or 0):
        categories = [category for category in getattr(group, "categories", []) if not getattr(category, "tombstone", False) and not getattr(category, "hidden", False)]
        if not categories:
            continue

        type_str = "Income" if getattr(group, "is_income", False) else "Expense"
        print(f"\n📂 {group.name} ({type_str}, ID: {group.id})")

        for category in sorted(categories, key=lambda category: getattr(category, "sort_order", 0) or 0):
            print(f"  - {category.name} (ID: {category.id})")
