import pandas as pd
import pypdf
from returns.result import safe

from src.core.pdf import extract_gross_pay, extract_net_pay, extract_payslip_date
from src.models.pdf import PayslipData


@safe
def read_excel(file_path: str, skiprows: int = 3) -> pd.DataFrame:
    return pd.read_excel(file_path, skiprows=skiprows)


@safe
def write_csv(dataframe: pd.DataFrame, output_path: str) -> None:
    dataframe.to_csv(output_path, index=False)


@safe
def decrypt_pdf(pdf_path: str, password: str) -> None:
    reader = pypdf.PdfReader(pdf_path)
    if reader.is_encrypted:
        reader.decrypt(password)
        writer = pypdf.PdfWriter()
        for page in reader.pages:
            writer.add_page(page)
        with open(pdf_path, "wb") as f:
            writer.write(f)


@safe
def extract_payslip_data(pdf_path: str) -> PayslipData:
    reader = pypdf.PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"

    return PayslipData(
        date=extract_payslip_date(text),
        taxable_income=extract_gross_pay(text),
        net_to_bank=extract_net_pay(text),
    )
