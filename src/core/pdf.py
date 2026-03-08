import re
from datetime import date


def extract_payslip_date(text: str) -> date:
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


def extract_gross_pay(text: str) -> float:
    match = re.search(r"([\d,.]+)\nהכנסה חייבת", text)
    if match:
        return float(match.group(1).replace(",", ""))
    raise ValueError("Could not find gross income")


def extract_net_pay(text: str) -> float:
    match = re.search(r"נטו לבנק([\d,.]+)", text)
    if match:
        return float(match.group(1).replace(",", ""))
    raise ValueError("Could not find net income")
