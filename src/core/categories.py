import re
import pandas as pd

from returns.maybe import Maybe, Nothing, Some


def check_reimbursable(row: pd.Series) -> Maybe[str]:
    name = row["Payee"].lower()
    amount = row["Amount"]
    keywords = ["work expenses", "shared bills"]
    if amount < 0 or any(x in name for x in keywords):
        return Some("Reimburseable")
    return Nothing


def check_rent(row: pd.Series) -> Maybe[str]:
    name = row["Payee"].lower()
    amount = row["Amount"]
    keywords = ["paybox"]
    if any(x in name for x in keywords):
        if 2900 <= amount <= 3100 or 800 <= amount <= 900:
            return Some("Home & Decor")
    return Nothing


def check_home_decor(row: pd.Series) -> Maybe[str]:
    name = row["Payee"].lower()
    cat = row["Category"]
    keywords = ["online home items", "booom", "ריהוט ובית"]
    if any(x in name for x in keywords) or cat in keywords:
        return Some("Home & Decor")
    return Nothing


def check_eating_out(row: pd.Series) -> Maybe[str]:
    name = row["Payee"].lower()
    cat = row["Category"]
    keywords = ["poalim wonder", "מש - קר", "wolt", "מסעדות", "מזון מהיר"]
    if any(x in name for x in keywords) or cat in keywords:
        return Some("Eating out")
    return Nothing


def check_education(row: pd.Series) -> Maybe[str]:
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
        return Some("Education & Learning")
    return Nothing


def check_transport(row: pd.Series) -> Maybe[str]:
    name = row["Payee"].lower()
    cat = row["Category"]
    keywords = ["parking", "חניון", "pango", "פנגו", "רב-פס", "אנרגיה", "רכב ותחבורה"]
    if any(x in name for x in keywords) or cat in keywords:
        return Some("Transport & Car")
    return Nothing


def check_appearance(row: pd.Series) -> Maybe[str]:
    name = row["Payee"].lower()
    cat = row["Category"]
    keywords = ["clothing", "fashion", "salon", "barber", "haircut", "אופנה", "טיוח ויופי"]
    if any(x in name for x in keywords) or cat in keywords:
        return Some("Appearance & Grooming")
    return Nothing


def check_vacation(row: pd.Series) -> Maybe[str]:
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
        return Some("Vacation & Travel")
    return Nothing


def check_gifts(row: pd.Series) -> Maybe[str]:
    name = row["Payee"].lower()
    keywords = ["gift", "donation", "charity", "מתנה", "תרומה"]
    if any(x in name for x in keywords):
        return Some("Gifts & Charity")
    return Nothing


def check_subscriptions(row: pd.Series) -> Maybe[str]:
    name = row["Payee"].lower()
    cat = row["Category"]
    keywords = ["bitwarden", "addy.io", "google", "netflix", "apple.com/bill", "Subscriptions"]
    if any(x in name for x in keywords) or cat in keywords:
        return Some("Subscriptions")
    return Nothing


def check_electronics(row: pd.Series) -> Maybe[str]:
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
        return Some("Electronics & Gadgets")
    return Nothing


def check_groceries(row: pd.Series) -> Maybe[str]:
    name = row["Payee"].lower()
    cat = row["Category"]
    keywords = ["קרמה +", "מזון ומשקאות", "מזון מהיר"]
    if any(x in name for x in keywords) or cat in keywords:
        return Some("Groceries")
    return Nothing


def check_government(row: pd.Series) -> Maybe[str]:
    name = row["Payee"].lower()
    cat = row["Category"]
    keywords = ["עיריית", "מוסדות"]
    if any(x in name for x in keywords) or cat in keywords:
        return Some("Government & Municipal")
    return Nothing


def check_health(row: pd.Series) -> Maybe[str]:
    name = row["Payee"].lower()
    cat = row["Category"]
    keywords = ["iherb", "רפואה ובריאות"]
    if any(x in name for x in keywords) or cat in keywords:
        return Some("Health & Cosmetics")
    return Nothing


def check_telecom(row: pd.Series) -> Maybe[str]:
    name = row["Payee"].lower()
    cat = row["Category"]
    keywords = ["תקשורת ומחשבים"]
    if any(x in name for x in keywords) or cat in keywords:
        return Some("Telecom")
    return Nothing


def check_entertainment(row: pd.Series) -> Maybe[str]:
    name = row["Payee"].lower()
    cat = row["Category"]
    keywords = ["אירועים"]
    if any(x in name for x in keywords) or cat in keywords:
        return Some("Entertainment & Events")
    return Nothing


def map_category(row: pd.Series) -> str:
    return (
        check_reimbursable(row)
        .lash(lambda _: check_rent(row))
        .lash(lambda _: check_health(row))
        .lash(lambda _: check_home_decor(row))
        .lash(lambda _: check_eating_out(row))
        .lash(lambda _: check_education(row))
        .lash(lambda _: check_transport(row))
        .lash(lambda _: check_appearance(row))
        .lash(lambda _: check_vacation(row))
        .lash(lambda _: check_gifts(row))
        .lash(lambda _: check_subscriptions(row))
        .lash(lambda _: check_electronics(row))
        .lash(lambda _: check_groceries(row))
        .lash(lambda _: check_government(row))
        .lash(lambda _: check_telecom(row))
        .lash(lambda _: check_entertainment(row))
        .value_or("Misc & One-offs")
    )
