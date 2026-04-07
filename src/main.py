import os

from dotenv import load_dotenv
from returns.result import Result, Success

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
from src.models.pdf import PayslipData

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


def process_payslip_pipeline(file_path: str, password: str) -> Result[PayslipData | None, Exception]:
    return (
        decrypt_pdf(file_path, password)
        .bind(lambda _: extract_payslip_data(file_path))
        .bind(lambda data: print_payslip_report(data).map(lambda _: data))
        .lash(lambda err: print_error(f"Payslip Pipeline Error: {err}"))  # type: ignore
    )


def main():
    excel_result = None
    payslip_result = None

    if os.path.exists("data.xlsx"):
        excel_result = process_excel_pipeline("data.xlsx")

    if os.path.exists("payslip.pdf"):
        password = os.getenv("PAYSLIP_PASSWORD")
        payslip_result = process_payslip_pipeline("payslip.pdf", password)

    excel_success = isinstance(excel_result, Success) and os.path.exists("actual.csv")
    payslip_success = isinstance(payslip_result, Success) and payslip_result.unwrap() is not None

    if excel_success or payslip_success:
        user_input = input("Do you want to upload to Actual Budget? (y/n): ")
        if user_input.lower() in ['y', 'yes']:
            if excel_success:
                import_transactions_to_actual("actual.csv")
            if payslip_success:
                import_payslip_to_actual(payslip_result.unwrap())


if __name__ == "__main__":
    main()
