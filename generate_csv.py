import pandas as pd
import re
import os

INPUT_FILE = "out.xlsx"
OUTPUT_FILE = "actual.csv"

# Constants from generate_report.py
VALUE_COL = """סכום
חיוב"""
CAT_COL = "ענף"
NAME_COL = "שם בית עסק"

def map_category(row: pd.Series) -> str:
    cat_val = row[CAT_COL]
    orig_cat = str(cat_val) if not pd.isna(cat_val) is True else "Unknown"
    name_val = row[NAME_COL]
    name = str(name_val) if not pd.isna(name_val) is True else ""
    amount = float(row[VALUE_COL])

    name_lower = name.lower()

    if amount < 0:
        return "Reimburseable"

    if "paybox" in name_lower:
        if 2900 <= amount <= 3100:
            return "Home & Decor" # Mapping Rent to Home & Decor as fallback, or could be separate
        if 800 <= amount <= 900:
            return "Home & Decor"

    if any(x in name_lower for x in ['online home items', 'booom']):
        return "Home & Decor"

    if any(x in name_lower for x in ['poalim wonder', 'מש - קר']):
        return "Eating out"

    if any(
        x in name_lower
        for x in ['course', 'udemy', 'coursera', 'book', 'books', 'steimatzky', 'סטימצקי', 'ספרים', 'מכון טכנולוגי', 'h.i.t', 'מכון אקדמי טכנולוגי חולון', 'מעונות חולון', 'חניון מעונות']
    ) or re.search(r'\bhit\b', name_lower):
        return "Education & Learning"

    if any(x in name_lower for x in ['parking', 'חניון', 'pango', 'פנגו', 'רב-פס']):
        return "Transport & Car"

    if any(
        x in name_lower
        for x in ['clothing', 'fashion', 'salon', 'barber', 'haircut']
    ):
        return "Appearance & Grooming"

    if any(
        x in name_lower
        for x in ['hotel', 'airbnb', 'booking', 'flight', 'travel', 'el al', 'נתבג', 'חו"ל', 'voye global connectivi']
    ) or re.search(r'\bחול\b', name_lower):
        return "Vacation & Travel"

    if any(
        x in name_lower
        for x in ['gift', 'donation', 'charity', 'מתנה', 'תרומה']
    ):
        return "Gifts & Charity"

    if any(x in name_lower for x in ['bitwarden', 'addy.io']):
        return "Subscriptions"

    if "work expenses" in name_lower or "shared bills" in name_lower:
        return "Reimburseable"

    if any(
        x in name_lower
        for x in ['gadget', 'electronic', 'ksp', 'ivory','קי.אס.פי.','קיי.אס.פי','פי.אס.קיי','פי.אס.קי', 'k s p']
    ):
        return "Electronics & Gadgets"

    if "קרמה +" in name_lower:
        return "Groceries"

    if "עיריית" in name_lower:
        return "Government & Municipal"

    if "iherb" in name_lower:
        return "Health & Cosmetics"

    if orig_cat == 'אנרגיה':
        return "Transport & Car"

    if orig_cat == 'אירועים':
        return "Entertainment & Events"

    if orig_cat == 'מסעדות':
        return "Eating out"

    if orig_cat in ['מזון ומשקאות', 'מזון מהיר']:
        return "Groceries"

    if orig_cat == 'ריהוט ובית':
        return "Home & Decor"

    if orig_cat == 'רפואה ובריאות':
        return "Health & Cosmetics"

    if orig_cat == 'רכב ותחבורה':
        return "Transport & Car"

    if orig_cat == 'תקשורת ומחשבים':
        return "Telecom"

    if orig_cat in ['אופנה', 'טיפוח ויופי']:
        return "Appearance & Grooming"

    if orig_cat == 'מוסדות':
        return "Government & Municipal"

    if orig_cat == 'Subscriptions':
        return "Subscriptions"

    return "Misc & One-offs"

def main():
    if not os.path.exists(INPUT_FILE):
        print(f"Error: {INPUT_FILE} not found.")
        return
    else:
        input_path = INPUT_FILE

    try:
        df = pd.read_excel(input_path, sheet_name="Processed Data")
        
        # Apply category mapping logic
        df[CAT_COL] = df.apply(map_category, axis=1)
        
        # Rename columns for Actual Budget import
        # Actual often likes: Date, Payee, Category, Amount, Notes
        rename_map = {
            "תאריך\nעסקה": "Date",
            "שם בית עסק": "Payee",
            "סכום\nחיוב": "Amount",
            "ענף": "Category"
        }
        
        df = df.rename(columns=rename_map)
        
        # Select only relevant columns
        cols_to_keep = ["Date", "Payee", "Amount", "Category"]
        existing_cols = [c for c in cols_to_keep if c in df.columns]
        
        df = df[existing_cols]
        
        # Format date to YYYY-MM-DD
        if "Date" in df.columns:
            df["Date"] = pd.to_datetime(df["Date"], dayfirst=True).dt.strftime("%Y-%m-%d")
        
        # Save to CSV
        df.to_csv(OUTPUT_FILE, index=False)
        print(f"Successfully created {OUTPUT_FILE} with Actual Budget categories")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
