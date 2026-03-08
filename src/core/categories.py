import re
import pandas as pd

from returns.maybe import Maybe, Nothing, Some


def check_reimbursable(row: pd.Series) -> Maybe[str]:
    transaction_name = row["Payee"].lower()
    amount = row["Amount"]
    keywords = ["work expenses", "shared bills"]
    if amount < 0 or any(x in transaction_name for x in keywords):
        return Some("Reimbursable Expenses")
    return Nothing


def check_rent(row: pd.Series) -> Maybe[str]:
    transaction_name = row["Payee"].lower()
    amount = row["Amount"]
    keywords = ["paybox"]
    if any(x in transaction_name for x in keywords):
        if 2900 <= amount <= 3100 or 800 <= amount <= 900:
            return Some("Rent and Utilities")
    return Nothing


def check_home_decor(row: pd.Series) -> Maybe[str]:
    transaction_name = row["Payee"].lower()
    orig_cat = row["Category"]
    keywords = ["online home items", "booom"]
    category = ["ריהוט ובית"]
    if any(x in transaction_name for x in keywords) or orig_cat in category:
        return Some("Home and Decor")
    return Nothing


def check_eating_out(row: pd.Series) -> Maybe[str]:
    transaction_name = row["Payee"].lower()
    orig_cat = row["Category"]
    keywords = ["poalim wonder", "מש - קר", "wolt"]
    category = ["מסעדות", "מזון מהיר"]
    if any(x in transaction_name for x in keywords) or orig_cat in category:
        return Some("Eating Out")
    return Nothing


def check_education(row: pd.Series) -> Maybe[str]:
    transaction_name = row["Payee"].lower()
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
    if any(x in transaction_name for x in keywords) or re.search(r"\bhit\b", transaction_name):
        return Some("Education and Learning")
    return Nothing


def check_transport(row: pd.Series) -> Maybe[str]:
    transaction_name = row["Payee"].lower()
    orig_cat = row["Category"]
    keywords = ["parking", "חניון", "pango", "פנגו", "רב-פס"]
    category = ["אנרגיה", "רכב ותחבורה"]
    if any(x in transaction_name for x in keywords) or orig_cat in category:
        return Some("Transport and Car")
    return Nothing


def check_appearance(row: pd.Series) -> Maybe[str]:
    transaction_name = row["Payee"].lower()
    orig_cat = row["Category"]
    keywords = ["clothing", "fashion", "salon", "barber", "haircut"]
    category = ["אופנה", "טיוח ויופי"]
    if any(x in transaction_name for x in keywords) or orig_cat in category:
        return Some("Appearance and Grooming")
    return Nothing


def check_vacation(row: pd.Series) -> Maybe[str]:
    transaction_name = row["Payee"].lower()
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
    if any(x in transaction_name for x in keywords) or re.search(r"\bחול\b", transaction_name):
        return Some("Vacation and Travel")
    return Nothing


def check_gifts(row: pd.Series) -> Maybe[str]:
    transaction_name = row["Payee"].lower()
    keywords = ["gift", "donation", "charity", "מתנה", "תרומה"]
    if any(x in transaction_name for x in keywords):
        return Some("Gifts and Charity")
    return Nothing


def check_subscriptions(row: pd.Series) -> Maybe[str]:
    transaction_name = row["Payee"].lower()
    orig_cat = row["Category"]
    keywords = ["bitwarden", "addy.io", "google", "netflix", "apple.com/bill"]
    category = ["Subscriptions"]
    if any(x in transaction_name for x in keywords) or orig_cat in category:
        return Some("Subscriptions")
    return Nothing


def check_electronics(row: pd.Series) -> Maybe[str]:
    transaction_name = row["Payee"].lower()
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
    if any(x in transaction_name for x in keywords):
        return Some("Electronics and Gadgets")
    return Nothing


def check_groceries(row: pd.Series) -> Maybe[str]:
    transaction_name = row["Payee"].lower()
    orig_cat = row["Category"]
    keywords = ["קרמה +"]
    category = ["מזון ומשקאות", "מזון מהיר"]
    if any(x in transaction_name for x in keywords) or orig_cat in category:
        return Some("Groceries")
    return Nothing


def check_government(row: pd.Series) -> Maybe[str]:
    transaction_name = row["Payee"].lower()
    orig_cat = row["Category"]
    keywords = ["עיריית"]
    category = ["מוסדות"]
    if any(x in transaction_name for x in keywords) or orig_cat in category:
        return Some("Government & Municipal")
    return Nothing


def check_health(row: pd.Series) -> Maybe[str]:
    transaction_name = row["Payee"].lower()
    orig_cat = row["Category"]
    keywords = ["iherb"]
    category = ["רפואה ובריאות"]
    if any(x in transaction_name for x in keywords) or orig_cat in category:
        return Some("Health and Cosmetics")
    return Nothing


def check_telecom(row: pd.Series) -> Maybe[str]:
    orig_cat = row["Category"]
    category = ["תקשורת ומחשבים"]
    if orig_cat in category:
        return Some("Telecom")
    return Nothing


def check_entertainment(row: pd.Series) -> Maybe[str]:
    orig_cat = row["Category"]
    category = ["אירועים"]
    if orig_cat in category:
        return Some("Entertainment and Fun")
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
        .value_or("Misc and One-offs")
    )
