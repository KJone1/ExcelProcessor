from datetime import date
import pytest
from src.core.pdf import extract_payslip_date, extract_gross_pay, extract_net_pay

def test_extract_payslip_date():
    text = "תלוש משכורת לחודש\n01/2026"
    assert extract_payslip_date(text) == date(2026, 2, 1)

def test_extract_payslip_date_invalid():
    with pytest.raises(ValueError):
        extract_payslip_date("No date here")

def test_extract_gross_pay():
    text = "10,000.00\nהכנסה חייבת"
    assert extract_gross_pay(text) == 10000.0

def test_extract_gross_pay_invalid():
    with pytest.raises(ValueError):
        extract_gross_pay("No pay here")

def test_extract_net_pay():
    text = "נטו לבנק8,500.50"
    assert extract_net_pay(text) == 8500.5

def test_extract_net_pay_invalid():
    with pytest.raises(ValueError):
        extract_net_pay("No net pay here")
