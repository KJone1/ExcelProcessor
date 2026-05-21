from dataclasses import dataclass
from datetime import date


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
    category: str | None = None
    account: str | None = None
    notes: str = ""
