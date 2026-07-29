"""Business data model."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Dict, List, Optional

from models.employee import Employee


class AcquisitionMode(Enum):
    RENT = "rent"
    BUYOUT = "buyout"


class BusinessStatus(Enum):
    AVAILABLE = auto()    # in marketplace
    OWNED = auto()        # player owns/leases it
    SOLD = auto()         # exited


@dataclass
class Business:
    """Core business data model."""

    id: str
    name: str
    sector: str           # restaurant, retail, manufacturing, etc.
    size: str             # small, medium, large

    # Financials
    purchase_price: float          # fair-market (or asking) price
    outstanding_debt: float        # existing debt on the books
    annual_revenue_base: float     # baseline revenue before adjustments
    cogs_rate: float               # cost of goods as % of revenue (0-1)
    overhead_monthly: float        # fixed monthly overhead (rent, utilities)
    maintenance_monthly: float     # baseline monthly maintenance cost

    # Reputation / demand
    reputation: float = 50.0      # 0-100
    customer_satisfaction: float = 50.0  # 0-100
    capacity_utilization: float = 0.5    # 0-1
    quality_score: float = 50.0    # 0-100
    demand_factor: float = 1.0     # multiplier on revenue

    # Condition
    condition: float = 0.5         # 0-1 (1 = perfect)
    marketing_spend_monthly: float = 0.0

    # Acquisition state
    status: BusinessStatus = BusinessStatus.AVAILABLE
    acquisition_mode: Optional[AcquisitionMode] = None
    lease_monthly: float = 0.0     # if rented
    acquisition_day: Optional[int] = None

    # Employees
    employees: List[Employee] = field(default_factory=list)

    # History (list of monthly summary dicts)
    monthly_history: List[Dict] = field(default_factory=list)

    # Turnaround investments applied
    process_improvement_level: int = 0   # 0-5
    equipment_upgrade_level: int = 0     # 0-5

    @property
    def headcount(self) -> int:
        return len([e for e in self.employees if e.is_active])

    @property
    def monthly_labor_cost(self) -> float:
        return sum(e.monthly_salary * (1 + 0.15) for e in self.employees if e.is_active)

    @property
    def monthly_revenue(self) -> float:
        """Rough monthly revenue at current utilization and demand."""
        base = self.annual_revenue_base / 12
        return base * self.capacity_utilization * self.demand_factor

    @property
    def monthly_cogs(self) -> float:
        return self.monthly_revenue * self.cogs_rate

    @property
    def monthly_gross_profit(self) -> float:
        return self.monthly_revenue - self.monthly_cogs

    @property
    def ebitda_monthly(self) -> float:
        return (
            self.monthly_gross_profit
            - self.monthly_labor_cost
            - self.overhead_monthly
            - self.maintenance_monthly
            - self.marketing_spend_monthly
        )

    @property
    def is_profitable(self) -> bool:
        return self.ebitda_monthly > 0

    def __repr__(self) -> str:
        return (
            f"Business({self.name!r}, sector={self.sector}, "
            f"status={self.status.name}, "
            f"EBITDA/mo=${self.ebitda_monthly:,.0f})"
        )
