"""Financial transaction model."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Optional


class TransactionType(Enum):
    REVENUE = auto()
    COGS = auto()
    LABOR = auto()
    OVERHEAD = auto()
    MAINTENANCE = auto()
    DEBT_SERVICE = auto()
    DEPRECIATION = auto()
    MARKETING = auto()
    TRAINING = auto()
    ACQUISITION = auto()
    SALE_PROCEEDS = auto()
    TAX = auto()
    SEVERANCE = auto()
    OTHER = auto()


@dataclass
class Transaction:
    """Records a single financial event."""

    day: int
    amount: float          # positive = inflow, negative = outflow
    type: TransactionType
    description: str
    business_id: Optional[str] = None

    @property
    def is_income(self) -> bool:
        return self.amount > 0

    @property
    def is_expense(self) -> bool:
        return self.amount < 0

    def __repr__(self) -> str:
        sign = "+" if self.amount >= 0 else ""
        return (
            f"Transaction(day={self.day}, {sign}{self.amount:,.2f}, "
            f"{self.type.name}, '{self.description}')"
        )
