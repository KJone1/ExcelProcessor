from dataclasses import dataclass
from datetime import date

@dataclass(frozen=True)
class PayslipData:
    date: date
    taxable_income: float
    net_to_bank: float
