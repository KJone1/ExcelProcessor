import os
import sys

from dotenv import load_dotenv
from returns.result import Result

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


def process_excel_pipeline(file_path: str) -> Result[None, Exception]:
    return (
        read_excel(file_path)
        .map(standardize_columns)
        .map(discard_row_if_amount_missing)
        .map(format_date_column)
        .map(remap_categories)
        .map(sort_by_category)
        .bind(lambda df: write_csv(df, "actual.csv").map(lambda _: "actual.csv"))
        .bind(lambda csv_path: print_transactions_report(csv_path).map(lambda _: csv_path))
        .bind(import_transactions_to_actual)
        .lash(lambda err: print_error(f"Excel Pipeline Error: {err}"))
    )


def process_payslip_pipeline(file_path: str, password: str) -> Result[None, Exception]:
    return (
        decrypt_pdf(file_path, password)
        .bind(lambda _: extract_payslip_data(file_path))
        .bind(lambda data: print_payslip_report(data).map(lambda _: data))
        .bind(import_payslip_to_actual)
        .lash(lambda err: print_error(f"Payslip Pipeline Error: {err}"))  # type: ignore
    )


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
