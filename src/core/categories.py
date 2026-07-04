import pandas as pd
import yaml

CATEGORIES_PATH = "src/core/categories.yaml"


def load_categories() -> dict[str, list[str]]:
    try:
        with open(CATEGORIES_PATH, "r", encoding="utf-8") as f:
            loaded = yaml.safe_load(f)
            if isinstance(loaded, dict):
                return loaded
    except (OSError, yaml.YAMLError):
        pass
    return {}


_categories: dict[str, list[str]] = load_categories()


def check_reimbursable(row: pd.Series) -> str | None:
    name = row["Payee"].lower()
    amount = row["Amount"]
    keywords = ["work expenses", "shared bills"]
    if amount < 0 or any(x in name for x in keywords):
        return "Reimburseable"
    return None


def check_rent(row: pd.Series) -> str | None:
    name = row["Payee"].lower()
    amount = row["Amount"]
    keywords = ["paybox"]
    if any(x in name for x in keywords):
        if 2900 <= amount <= 3100 or 800 <= amount <= 900:
            return "Home & Decor"
    return None


def check_keywords(row: pd.Series, category: str) -> str | None:
    name = row["Payee"].lower()
    cat = row["Category"]
    keywords = _categories.get(category, [])
    for keyword in keywords:
        if keyword.startswith("e:"):
            if name == keyword[2:]:
                return category
        elif keyword in name or cat == keyword:
            return category
    return None


def map_category(row: pd.Series) -> str:
    res = check_reimbursable(row)
    if res:
        return res

    res = check_rent(row)
    if res:
        return res

    for category in _categories:
        res = check_keywords(row, category)
        if res:
            return res

    return "Misc & One-offs"
