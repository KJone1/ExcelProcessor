from dataclasses import dataclass
from datetime import date
from typing import Optional

@dataclass(frozen=True)
class ActualConfig:
    server_url: str
    password: str
    budget_id: str

@dataclass(frozen=True)
class Transaction:
    date: date
    payee: str
    amount: float
    category: Optional[str] = None
    account: Optional[str] = None
    notes: str = ""
