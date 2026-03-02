import pypdf
import re
import os
from datetime import datetime
from dotenv import load_dotenv
from actual import Actual
from actual.queries import get_accounts, get_categories, create_transaction

load_dotenv()

SERVER_URL = os.getenv("ACTUAL_SERVER_URL")
ACTUAL_PASSWORD = os.getenv("ACTUAL_PASSWORD")
BUDGET_ID = os.getenv("ACTUAL_BUDGET_ID")

def extract_payslip_data(pdf_path):
    password = os.getenv("PAYSLIP_PASSWORD")
    if not password:
        print("Error: PAYSLIP_PASSWORD not found in environment variables.")
        return

    try:
        reader = pypdf.PdfReader(pdf_path)
    except FileNotFoundError:
        print(f"Error: File {pdf_path} not found.")
        return

    if reader.is_encrypted:
        try:
            reader.decrypt(password)
            # Save unlocked version
            writer = pypdf.PdfWriter()
            for page in reader.pages:
                writer.add_page(page)
            with open(pdf_path, "wb") as f:
                writer.write(f)
            print(f"PDF unlocked and saved to {pdf_path}")
        except Exception as e:
            print(f"Error decrypting PDF: {e}")
            return

    full_text = ""
    for page in reader.pages:
        full_text += page.extract_text() + "\n"

    # Keywords to search for
    keywords = {
        "taxable_income": "הכנסה חייבת",
        "net_to_bank": "נטו לבנק"
    }

    results = {}
    lines = full_text.split('\n')
    
    # Extract Date
    # Look for MM/YYYY pattern
    date_pattern = r'\b(\d{2}/\d{4})\b'
    payslip_date = None
    
    for line in lines:
        match = re.search(date_pattern, line)
        if match:
            try:
                # Verify it's a valid date
                d_str = match.group(1)
                datetime.strptime(d_str, "%m/%Y")
                payslip_date = d_str
                break
            except ValueError:
                continue
    
    if not payslip_date:
        print("Warning: Could not find payslip date (MM/YYYY).")
    else:
        print(f"Found Payslip Date: {payslip_date}")

    # Extract Values
    for key, search_term in keywords.items():
        found = False
        for i, line in enumerate(lines):
            if search_term in line:
                candidates = []
                def get_numbers(s):
                    return re.findall(r'\d{1,3}(?:,\d{3})*(?:\.\d+)?', s)

                nums = get_numbers(line)
                if nums: candidates.extend(nums)
                if i > 0:
                    nums_prev = get_numbers(lines[i-1])
                    if nums_prev: candidates.extend(nums_prev)
                if i < len(lines) - 1:
                    nums_next = get_numbers(lines[i+1])
                    if nums_next: candidates.extend(nums_next)
                
                if candidates:
                    try:
                        best_val = max(candidates, key=lambda x: float(x.replace(',', '')))
                        results[key] = {
                            "line": line.strip(),
                            "value": best_val
                        }
                        found = True
                        break
                    except ValueError:
                        continue
        
        if not found:
            reversed_term = search_term[::-1]
            for i, line in enumerate(lines):
                if reversed_term in line:
                    candidates = []
                    def get_numbers(s):
                        return re.findall(r'\d{1,3}(?:,\d{3})*(?:\.\d+)?', s)

                    nums = get_numbers(line)
                    if nums: candidates.extend(nums)
                    if i > 0:
                        nums_prev = get_numbers(lines[i-1])
                        if nums_prev: candidates.extend(nums_prev)
                    if i < len(lines) - 1:
                        nums_next = get_numbers(lines[i+1])
                        if nums_next: candidates.extend(nums_next)

                    if candidates:
                        try:
                            best_val = max(candidates, key=lambda x: float(x.replace(',', '')))
                            results[key] = {
                                "line": line.strip(),
                                "value": best_val,
                                "note": "(found via reversed text)"
                            }
                            found = True
                            break
                        except ValueError:
                            continue

    # Print results
    print("-" * 30)
    print("Payslip Data Extraction")
    print("-" * 30)
    
    net_income = None
    
    if "taxable_income" in results:
        print(f"הכנסה חייבת (Taxable Income): {results['taxable_income']['value']}")
    else:
        print("הכנסה חייבת: Not found")

    if "net_to_bank" in results:
        val_str = results['net_to_bank']['value']
        print(f"נטו לבנק (Net to Bank):     {val_str}")
        try:
            net_income = float(val_str.replace(',', ''))
        except ValueError:
            print("Error parsing net income value.")
    else:
        print("נטו לבנק: Not found")
    
    print("-" * 30)

    # Import to Actual
    if net_income and payslip_date:
        import_to_actual(net_income, payslip_date)

def import_to_actual(amount, date_str):
    if not SERVER_URL or not ACTUAL_PASSWORD or not BUDGET_ID:
        print("Skipping Actual import: Missing configuration.")
        return

    try:
        month, year = map(int, date_str.split('/'))
        
        if month == 12:
            next_month = 1
            next_year = year + 1
        else:
            next_month = month + 1
            next_year = year
            
        trans_date = datetime(next_year, next_month, 1).date()
        print(f"Transaction Date: {trans_date}")

        with Actual(base_url=SERVER_URL, password=ACTUAL_PASSWORD) as actual:
            print(f"Connecting to budget: {BUDGET_ID}")
            actual.set_file(BUDGET_ID)
            actual.download_budget()
            session = actual.session

            accounts = get_accounts(session)
            account = next((a for a in accounts if "Poalim" in a.name), None)
            if not account:
                print("Error: 'Poalim' account not found.")
                if accounts:
                    account = accounts[0]
                    print(f"Fallback to account: {account.name}")
                else:
                    return
            else:
                print(f"Using account: {account.name}")

            categories = get_categories(session)
            category = next((c for c in categories if c.name == "Income"), None)
            if not category:
                print("Error: 'Income' category not found.")
                return
            print(f"Using category: {category.name}")

            payslip_dt = datetime.strptime(date_str, "%m/%Y")
            month_name = payslip_dt.strftime("%B")
            description = f"Salary for {month_name}"
            
            print(f"Creating transaction: {amount:,.2f}")
            print(f"Description: {description}")
            
            create_transaction(
                session,
                date=trans_date,
                account=account,
                payee="Salary",
                category=category,
                amount=amount,
                notes=description
            )
            
            actual.commit()
            actual.sync()
            print("Transaction imported successfully.")

    except Exception as e:
        print(f"Error importing to Actual: {e}")

if __name__ == "__main__":
    extract_payslip_data("payslip.pdf")
