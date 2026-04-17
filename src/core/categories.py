import re
from typing import Optional
import pandas as pd


def check_reimbursable(row: pd.Series) -> Optional[str]:
    name = row["Payee"].lower()
    amount = row["Amount"]
    keywords = ["work expenses", "shared bills"]
    if amount < 0 or any(x in name for x in keywords):
        return "Reimburseable"
    return None


def check_rent(row: pd.Series) -> Optional[str]:
    name = row["Payee"].lower()
    amount = row["Amount"]
    keywords = ["paybox"]
    if any(x in name for x in keywords):
        if 2900 <= amount <= 3100 or 800 <= amount <= 900:
            return "Home & Decor"
    return None


def check_health(row: pd.Series) -> Optional[str]:
    name = row["Payee"].lower()
    cat = row["Category"]
    keywords = ["iherb", "רפואה ובריאות"]
    if any(x in name for x in keywords) or cat in keywords:
        return "Health & Cosmetics"
    return None


def check_home_decor(row: pd.Series) -> Optional[str]:
    name = row["Payee"].lower()
    cat = row["Category"]
    keywords = ["online home items", "booom", "ריהוט ובית"]
    if any(x in name for x in keywords) or cat in keywords:
        return "Home & Decor"
    return None


def check_eating_out(row: pd.Series) -> Optional[str]:
    name = row["Payee"].lower()
    cat = row["Category"]
    keywords = ["poalim wonder", "מש - קר", "wolt", "מסעדות", "מזון מהיר"]
    if any(x in name for x in keywords) or cat in keywords:
        return "Eating out"
    return None


def check_education(row: pd.Series) -> Optional[str]:
    name = row["Payee"].lower()
    keywords = [
        "course",
        "udemy",
        "coursera",
        "book",
        "books",
        "steimatzky",
        "סטימצקי",
        "ספרים",
        "מכון טכנולוגי",
        "h.i.t",
        "מכון אקדמי טכנולוגי חולון",
        "מעונות חולון",
        "חניון מעונות",
    ]
    if any(x in name for x in keywords) or re.search(r"\bhit\b", name):
        return "Education & Learning"
    return None


def check_transport(row: pd.Series) -> Optional[str]:
    name = row["Payee"].lower()
    cat = row["Category"]
    keywords = ["parking", "חניון", "pango", "פנגו", "רב-פס", "אנרגיה", "רכב ותחבורה"]
    if any(x in name for x in keywords) or cat in keywords:
        return "Transport & Car"
    return None


def check_appearance(row: pd.Series) -> Optional[str]:
    name = row["Payee"].lower()
    cat = row["Category"]
    keywords = ["clothing", "fashion", "salon", "barber", "haircut", "אופנה", "טיוח ויופי"]
    if any(x in name for x in keywords) or cat in keywords:
        return "Appearance & Grooming"
    return None


def check_vacation(row: pd.Series) -> Optional[str]:
    name = row["Payee"].lower()
    keywords = [
        "hotel",
        "airbnb",
        "booking",
        "flight",
        "travel",
        "el al",
        "נתבג",
        'חו"ל',
        "voye global connectivi",
    ]
    if any(x in name for x in keywords) or re.search(r"\bחול\b", name):
        return "Vacation & Travel"
    return None


def check_gifts(row: pd.Series) -> Optional[str]:
    name = row["Payee"].lower()
    keywords = ["gift", "donation", "charity", "מתנה", "תרומה"]
    if any(x in name for x in keywords):
        return "Gifts & Charity"
    return None


def check_subscriptions(row: pd.Series) -> Optional[str]:
    name = row["Payee"].lower()
    cat = row["Category"]
    keywords = ["bitwarden", "addy.io", "google", "netflix", "apple.com/bill", "Subscriptions"]
    if any(x in name for x in keywords) or cat in keywords:
        return "Subscriptions"
    return None


def check_electronics(row: pd.Series) -> Optional[str]:
    name = row["Payee"].lower()
    keywords = [
        "gadget",
        "electronic",
        "ksp",
        "ivory",
        "קי.אס.פי.",
        "קיי.אס.פי",
        "פי.אס.קיי",
        "פי.אס.קי",
        "k s p",
        "aliexpress",
    ]
    if any(x in name for x in keywords):
        return "Electronics & Gadgets"
    return None


def check_groceries(row: pd.Series) -> Optional[str]:
    name = row["Payee"].lower()
    cat = row["Category"]
    keywords = ["קרמה +", "מזון ומשקאות", "מזון מהיר"]
    if any(x in name for x in keywords) or cat in keywords:
        return "Groceries"
    return None


def check_government(row: pd.Series) -> Optional[str]:
    name = row["Payee"].lower()
    cat = row["Category"]
    keywords = ["עיריית", "מוסדות"]
    if any(x in name for x in keywords) or cat in keywords:
        return "Government & Municipal"
    return None


def check_telecom(row: pd.Series) -> Optional[str]:
    name = row["Payee"].lower()
    cat = row["Category"]
    keywords = ["תקשורת ומחשבים"]
    if any(x in name for x in keywords) or cat in keywords:
        return "Telecom"
    return None


def check_entertainment(row: pd.Series) -> Optional[str]:
    name = row["Payee"].lower()
    cat = row["Category"]
    keywords = ["אירועים"]
    if any(x in name for x in keywords) or cat in keywords:
        return "Entertainment & Events"
    return None


def map_category(row: pd.Series) -> str:
    checks = [
        func for name, func in globals().items()
        if name.startswith("check_") and callable(func)
    ]
    
    for check in checks:
        result = check(row)
        if result is not None:
            return result
            
    return "Misc & One-offs"
