import os
import random
from datetime import datetime

import numpy as np
import pandas as pd
from faker import Faker

fake = Faker()

COLUMNS = [
    "תאריך\nעסקה",
    "שם בית עסק",
    "סכום\nעסקה",
    "סכום\nחיוב",
    "סוג\nעסקה",
    "ענף",
    "הערות",
]

CATEGORIES = [
    "מסעדות",
    "תקשורת ומחשבים",
    "שונות",
    "מוסדות",
    "פנאי בילוי",
    "רפואה ובריאות",
    "ריהוט ובית",
    "מזון ומשקאות",
    "אופנה",
    "אנרגיה",
    "תעשיה ומכירות",
    "רכב ותחבורה",
    "טיפוח ויופי",
    "ביטוח ופיננסים",
    "אירועים",
]

NAMES = [
    "הייטקזון - הסעדה",
    "פרטנר תקשורת",
    "מרפיס פאב",
    "מדינה בשרים",
    "העברה ב BIT",
    "בזק בינלאומי",
    "מ.תחבורה רב-פס",
    "מנזה",
    "רול מי סושי",
    "Google YouTube",
    'עסק כללי בע"מ',
    "Wolt Delivery",
    "Paybox Transfer",
    "Apple.com/Bill",
    "Netflix",
    "iHerb.com",
    "work expenses",
    "shared bills",
    "paybox",
    "online home items",
    "booom",
    "poalim wonder",
    "מש - קר",
    "wolt",
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
    "parking",
    "חניון",
    "pango",
    "פנגו",
    "רב-פס",
    "clothing",
    "fashion",
    "salon",
    "barber",
    "haircut",
    "hotel",
    "airbnb",
    "booking",
    "flight",
    "travel",
    "el al",
    "נתבג",
    'חו"ל',
    "voye global connectivi",
    "gift",
    "donation",
    "charity",
    "מתנה",
    "תרומה",
    "bitwarden",
    "addy.io",
    "google",
    "netflix",
    "apple.com/bill",
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
    "קרמה +",
    "עיריית",
]


def generate_mock_excel(
    output_path: str,
    num_rows: int = 1000,
    missing_categories: int = 50,
    missing_amounts: int = 20,
):
    random.seed(42)

    data = []
    for i in range(num_rows):
        day = random.randint(1, 31)
        date = datetime(2026, 3, day)
        name = random.choice(NAMES)

        category = random.choice(CATEGORIES)
        amount = round(random.uniform(10.0, 5000.0), 2)

        if i < missing_categories:
            category = np.nan

        if missing_categories <= i < (missing_categories + missing_amounts):
            amount = np.nan

        row = {
            "תאריך\nעסקה": date,
            "שם בית עסק": name,
            "סכום\nעסקה": amount,
            "סכום\nחיוב": amount,
            "סוג\nעסקה": "רגילה",
            "ענף": category,
            "הערות": np.nan,
        }
        data.append(row)

    df = pd.DataFrame(data)

    with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
        pd.DataFrame().to_excel(writer, index=False, header=False, startrow=0)
        df.to_excel(writer, index=False, startrow=3)


if __name__ == "__main__":
    generate_mock_excel("golden_statement.xlsx")
