from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class PayslipData:
    date: date
    taxable_income: float
    net_to_bank: float


@dataclass(frozen=True)
class PayslipSyncRequest:
    """Request model for syncing an encrypted payslip PDF."""
    password: str | None = None
