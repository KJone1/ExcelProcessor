import pandas as pd
import sys
import os

INPUT_FILE = "out.xlsx"
OUTPUT_FILE = "expense_report.md"
VALUE_COL = """סכום\nחיוב"""
CAT_COL = "ענף"
NAME_COL = "שם בית עסק"

CATEGORIES = [
    "Entertainment and Fun",
    "Eating Out",
    "Groceries",
    "Home and Decor",
    "Health and Cosmetics",
    "Transport and Car",
    "Telecom",
    "Appearance and Grooming",
    "Institutions",
    "Subscriptions",
    "Vacation and Travel",
    "Education and Learning",
    "Gifts and Charity",
    "Electronics and Gadgets",
    "Reimbursable Expenses",
    "Rent and Utilities",
    "Misc and One-offs"
]

def map_category(row):
    orig_cat = str(row[CAT_COL]) if pd.notna(row[CAT_COL]) else "Unknown"
    name = str(row[NAME_COL]) if pd.notna(row[NAME_COL]) else ""
    amount = row[VALUE_COL]
    
    name_lower = name.lower()

    if ("paybox" in name_lower):
        if 2900 <= amount <= 3100:
            return "Rent and Utilities"
        if 800 <= amount <= 900:
            return "Rent and Utilities"
    
    if orig_cat == 'אנרגיה':
        return "Transport and Car"

    if orig_cat == 'אירועים':
        return "Entertainment and Fun"

    if orig_cat == 'מסעדות':
        return "Eating Out"

    if orig_cat in ['מזון ומשקאות', 'מזון מהיר']:
        return "Groceries"

    if orig_cat == 'ריהוט ובית':
        return "Home and Decor"
    if "online home items" in name_lower: 
        return "Home and Decor"

    if orig_cat == 'רפואה ובריאות':
        return "Health and Cosmetics"

    if orig_cat == 'רכב ותחבורה':
        return "Transport and Car"
    if orig_cat == 'מוסדות' and any(x in name_lower for x in ['parking', 'חניון', 'pango', 'פנגו']):
        return "Transport and Car"
    if orig_cat == 'Unknown' and ('חניון' in name_lower or 'parking' in name_lower):
         return "Transport and Car"

    if orig_cat == 'תקשורת ומחשבים':
        return "Telecom"

    if orig_cat in ['אופנה', 'טיפוח ויופי']:
        return "Appearance and Grooming"
    if any(x in name_lower for x in ['clothing', 'fashion', 'salon', 'barber', 'haircut']):
        return "Appearance and Grooming"

    if orig_cat == 'מוסדות':
        return "Institutions"

    if orig_cat == 'Subscriptions':
        return "Subscriptions"

    if any(x in name_lower for x in ['hotel', 'airbnb', 'booking', 'flight', 'travel', 'el al', 'נתבג', 'חול']):
        return "Vacation and Travel"

    if any(x in name_lower for x in ['course', 'udemy', 'coursera', 'book', 'steimatzky', 'סטימצקי']):
        return "Education and Learning"

    if any(x in name_lower for x in ['gift', 'donation', 'charity', 'מתנה', 'תרומה']):
        return "Gifts and Charity"

    if any(x in name_lower for x in ['gadget', 'electronic', 'ksp', 'ivory']):
         return "Electronics and Gadgets"

    if "work expenses" in name_lower or "shared bills" in name_lower:
        return "Reimbursable Expenses"

    return "Misc and One-offs"

def main():
    if not os.path.exists(INPUT_FILE):
        print(f"Error: {INPUT_FILE} not found.")
        sys.exit(1)

    df = pd.read_excel(INPUT_FILE, sheet_name="Processed Data")
    
    req_cols = [NAME_COL, VALUE_COL, CAT_COL]
    for col in req_cols:
        if col not in df.columns:
            print(f"Error: Column '{col}' not found in {INPUT_FILE}")
            sys.exit(1)

    df['MappedCategory'] = df.apply(map_category, axis=1)

    total_spent = df[VALUE_COL].sum()
    total_transactions = len(df)
        
    report_lines = []
    
    cat_summary = {}
    for c in CATEGORIES:
        cat_summary[c] = {
            'total': 0.0,
            'count': 0,
            'avg': 0.0,
            'percent': 0.0,
            'transactions': []
        }
        
    for cat, group in df.groupby('MappedCategory'):
        total = group[VALUE_COL].sum()
        count = len(group)
        avg = total / count if count > 0 else 0
        percent = (total / total_spent * 100) if total_spent > 0 else 0
        
        trans_list = []
        for _, row in group.iterrows():
            trans_list.append((row[NAME_COL], row[VALUE_COL]))
        
        cat_summary[cat] = {
            'total': total,
            'count': count,
            'avg': avg,
            'percent': percent,
            'transactions': trans_list
        }
        
    sorted_categories = sorted(CATEGORIES, key=lambda x: cat_summary[x]['total'], reverse=True)

    wolt_df = df[df[NAME_COL].str.contains("wolt", case=False, na=False)]
    wolt_total = wolt_df[VALUE_COL].sum()
    wolt_count = len(wolt_df)
    
    eating_out_total = cat_summary["Eating Out"]['total']
    wolt_portion_eating_out = (wolt_total / eating_out_total * 100) if eating_out_total > 0 else 0.0

    report_lines.append("# Expense Report Summary")
    report_lines.append("")
    report_lines.append("## Overall Totals")
    for cat in sorted_categories:
        d = cat_summary[cat]
        line = f"- **{cat}**: {d['total']:.2f}₪ ({d['percent']:.1f}%) | {d['count']} transactions ({d['count']/total_transactions*100:.1f}%) | avg {d['avg']:.2f}₪"
        report_lines.append(line)
        
    report_lines.append("")
    report_lines.append(f"**TOTAL SPENT:** {total_spent:.2f}₪")
    report_lines.append(f"**TOTAL TRANSACTIONS:** {total_transactions}")
    report_lines.append("")
    
    for cat in sorted_categories:
        d = cat_summary[cat]
        report_lines.append(f"## {cat}")
        report_lines.append("")
        
        prices = []
        if d['count'] > 0:
            for name, price in d['transactions']:
                display_name = name
                if cat == "Rent and Utilities" and 2900 <= price <= 3100 and "paybox" in name.lower():
                     display_name = "Rent"
                     
                report_lines.append(f"- {display_name}: {price:.2f}₪")
                prices.append(f"{price:.2f}")
        else:
             report_lines.append("_No entries in this category_")

        report_lines.append("")
        
        if prices:
            sum_formula = f"=SUM({','.join(prices)})"
        else:
            sum_formula = "=SUM(0)"
            
        report_lines.append(f"**Category Total:** {d['total']:.2f}₪ ({d['percent']:.1f}%) | {d['count']} transactions | avg {d['avg']:.2f}₪")
        report_lines.append(f"**Sum Formula:** `{sum_formula}`")
        report_lines.append("")

    report_lines.append("## Top Individual Expenses")
    report_lines.append("")
    report_lines.append("> Excludes Rent and Utilities")
    report_lines.append("")
    
    filtered_df = df[df['MappedCategory'] != "Rent and Utilities"]
    if not filtered_df.empty:
        top_5_exp = filtered_df.nlargest(5, VALUE_COL)
        for i, (_, row) in enumerate(top_5_exp.iterrows(), 1):
            report_lines.append(f"{i}. {row[NAME_COL]}: **{row[VALUE_COL]:.2f}₪**")
    else:
        report_lines.append("No expenses found (excluding rent/utils)")
        
    report_lines.append("")
    
    report_lines.append("## Top Spending Categories")
    report_lines.append("")
    report_lines.append("> Excludes Rent and Utilities")
    report_lines.append("")
    
    cats_no_rent = [c for c in CATEGORIES if c != "Rent and Utilities"]
    sorted_cats_no_rent = sorted(cats_no_rent, key=lambda x: cat_summary[x]['total'], reverse=True)
    
    for i, cat in enumerate(sorted_cats_no_rent[:5], 1):
        d = cat_summary[cat]
        report_lines.append(f"{i}. **{cat}**: {d['total']:.2f}₪ | {d['percent']:.1f}% of total | {d['count']} transactions")

    report_lines.append("")

    report_lines.append("## Key Insights")
    report_lines.append("")
    
    report_lines.append("### Wolt Analytics")
    report_lines.append(f"- **Total Spent on Wolt:** {wolt_total:.2f}₪")
    report_lines.append(f"- **Total Transactions:** {wolt_count}")
    report_lines.append(f"- **Share of 'Eating Out':** {wolt_portion_eating_out:.1f}%")
    report_lines.append("")

    report_lines.append("### Notable Spending")
    
    notable_count = 0
    for cat in CATEGORIES:
        if cat == "Rent and Utilities": continue
        d = cat_summary[cat]
        if d['percent'] > 15.0:
            report_lines.append(f"- **{cat}** accounts for {d['percent']:.1f}% of total expenses ({d['count']} transactions).")
            notable_count += 1
    
    if notable_count == 0:
        report_lines.append("- No single category (excluding rent) exceeds 15% of total spending.")
            
    subs_df = df[df['MappedCategory'] == "Subscriptions"]
    if not subs_df.empty:
        largest_sub = subs_df.loc[subs_df[VALUE_COL].idxmax()]
        report_lines.append(f"- **Largest Subscription:** {largest_sub[NAME_COL]} (`{largest_sub[VALUE_COL]:.2f}₪`)")
        
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines))
        
    print(f"Successfully generated {OUTPUT_FILE}")
    print(f"Total Spending: {total_spent:.2f}")
    print(f"Total Transactions: {total_transactions}")


if __name__ == "__main__":
    main()
