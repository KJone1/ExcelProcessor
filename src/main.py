import os

from dotenv import load_dotenv
from returns.result import Result

from src.core.excel import (
    discard_row_if_amount_missing,
    format_date_column,
    remap_categories,
    sort_by_category,
    standardize_columns,
)
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
        .bind(print_transactions_report)
        .lash(lambda err: print_error(f"Excel Pipeline Error: {err}"))
    )


def process_payslip_pipeline(file_path: str, password: str) -> Result[None, Exception]:
    return (
        decrypt_pdf(file_path, password)
        .bind(lambda _: extract_payslip_data(file_path))
        .bind(print_payslip_report)
        .lash(lambda err: print_error(f"Payslip Pipeline Error: {err}"))
    )


def main():
    if os.path.exists("data.xlsx"):
        process_excel_pipeline("data.xlsx")

    if os.path.exists("payslip.pdf"):
        password = os.getenv("PAYSLIP_PASSWORD")
        process_payslip_pipeline("payslip.pdf", password)


if __name__ == "__main__":
    main()
