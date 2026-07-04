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
from actual.queries import get_tags
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

    print("BUDGET TAGS:")
    tags = get_tags(actual.session)
    active_tags = [
        tag for tag in tags
        if not getattr(tag, "tombstone", False)
    ]

    for tag in sorted(active_tags, key=lambda t: t.tag or ""):
        desc_info = f" - {tag.description}" if tag.description else ""
        color_info = f" [Color: {tag.color}]" if tag.color else ""
        print(f"- {tag.tag} (ID: {tag.id}){desc_info}{color_info}")
