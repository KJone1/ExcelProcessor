import os
import sys

from dotenv import load_dotenv

from src.core.excel import (
    discard_row_if_amount_missing,
    format_date_column,
    remap_categories,
    sort_by_category,
    standardize_columns,
)
from src.io.actual import import_payslip_to_actual, import_transactions_to_actual
from src.io.console import print_error, print_payslip_report, print_transactions_report
from src.io.filesystem import decrypt_pdf, extract_payslip_data, read_excel, write_csv

load_dotenv()


def process_excel_pipeline(file_path: str) -> None:
    try:
        df = (
            read_excel(file_path)
            .pipe(standardize_columns)
            .pipe(discard_row_if_amount_missing)
            .pipe(format_date_column)
            .pipe(remap_categories)
            .pipe(sort_by_category)
        )
        
        csv_path = "actual.csv"
        write_csv(df, csv_path)
        print_transactions_report(csv_path)
        import_transactions_to_actual(csv_path)
    except Exception as e:
        print_error(f"Excel Pipeline Error: {e}")


def process_payslip_pipeline(file_path: str, password: str) -> None:
    try:
        decrypt_pdf(file_path, password)
        data = extract_payslip_data(file_path)
        print_payslip_report(data)
        import_payslip_to_actual(data)
    except Exception as e:
        print_error(f"Payslip Pipeline Error: {e}")


def main():
    required_vars = ["ACTUAL_SERVER_URL", "ACTUAL_PASSWORD", "ACTUAL_BUDGET_ID"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"Error: Missing required environment variables: {', '.join(missing_vars)}")
        sys.exit(1)

    if os.path.exists("data.xlsx"):
        process_excel_pipeline("data.xlsx")

    if os.path.exists("payslip.pdf"):
        password = os.getenv("PAYSLIP_PASSWORD")
        if password:
            process_payslip_pipeline("payslip.pdf", password)
        else:
            print("Error: PAYSLIP_PASSWORD environment variable is missing.")


if __name__ == "__main__":
    main()
