# pylint: disable=too-few-public-methods
import re
from dataclasses import dataclass
from datetime import date

import pypdf

from src.settings import settings


@dataclass(frozen=True)
class PayslipData:
    date: date
    taxable_income: float
    net_to_bank: float


class PayslipProcessor:
    def __init__(self) -> None:
        self.reader: pypdf.PdfReader = pypdf.PdfReader(settings.payslip_file)

    def process(self) -> PayslipData:
        if self.reader.is_encrypted:
            if not settings.payslip_password:
                raise ValueError("PAYSLIP_PASSWORD is required for encrypted payslips")
            self._decrypt_pdf(settings.payslip_file, settings.payslip_password)
            self.reader = pypdf.PdfReader(settings.payslip_file)

        text = ""
        for page in self.reader.pages:
            text += page.extract_text() + "\n"

        return PayslipData(
            date=self._extract_payslip_date(text),
            taxable_income=self._extract_gross_pay(text),
            net_to_bank=self._extract_net_pay(text),
        )

    def _decrypt_pdf(self, pdf_path: str, password: str) -> None:
        if self.reader.is_encrypted:
            if not self.reader.decrypt(password):
                raise ValueError("Incorrect payslip password")
            writer = pypdf.PdfWriter()
            for page in self.reader.pages:
                _ = writer.add_page(page)
            with open(pdf_path, "wb") as f:
                _ = writer.write(f)

    def _extract_payslip_date(self, text: str) -> date:
        match = re.search(r"תלוש משכורת לחודש\n(\d{2}/\d{4})", text)
        if not match:
            raise ValueError("Could not find payslip date")

        month, year = map(int, match.group(1).split("/"))
        if month == 12:
            next_month = 1
            next_year = year + 1
        else:
            next_month = month + 1
            next_year = year
        return date(next_year, next_month, 1)

    def _extract_gross_pay(self, text: str) -> float:
        match = re.search(r"([\d,.]+)\nהכנסה חייבת", text)
        if match:
            return float(match.group(1).replace(",", ""))
        raise ValueError("Could not find gross income")

    def _extract_net_pay(self, text: str) -> float:
        match = re.search(r"נטו לבנק([\d,.]+)", text)
        if match:
            return float(match.group(1).replace(",", ""))
        raise ValueError("Could not find net income")
