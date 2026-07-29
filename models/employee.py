"""Employee data model."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Optional


class EmployeeRole(Enum):
    MANAGER = "manager"
    SKILLED_WORKER = "skilled_worker"
    UNSKILLED_WORKER = "unskilled_worker"
    SALESPERSON = "salesperson"
    TECHNICIAN = "technician"


class EmployeeStatus(Enum):
    APPLICANT = auto()
    ONBOARDING = auto()
    ACTIVE = auto()
    UNDER_PERFORMANCE_REVIEW = auto()
    TERMINATED = auto()


@dataclass
class Employee:
    """Represents a single employee."""

    id: str
    name: str
    role: EmployeeRole
    annual_salary: float

    # Performance attributes (0.0 – 1.0)
    skill_level: float = 0.5       # base competency
    productivity: float = 0.5      # current output rate
    morale: float = 0.7            # job satisfaction
    quality_contribution: float = 0.5  # effect on product/service quality

    # Lifecycle
    status: EmployeeStatus = EmployeeStatus.ONBOARDING
    days_employed: int = 0
    onboarding_days_remaining: int = 0
    training_weeks_completed: int = 0

    # Flags
    is_being_trained: bool = False
    training_weeks_remaining: int = 0

    @property
    def weekly_salary(self) -> float:
        return self.annual_salary / 52

    @property
    def monthly_salary(self) -> float:
        return self.annual_salary / 12

    @property
    def daily_salary(self) -> float:
        return self.annual_salary / 365

    @property
    def is_active(self) -> bool:
        return self.status == EmployeeStatus.ACTIVE

    @property
    def effective_productivity(self) -> float:
        """Productivity adjusted for morale."""
        return self.productivity * (0.7 + 0.3 * self.morale)

    def __repr__(self) -> str:
        return (
            f"Employee({self.name!r}, {self.role.value}, "
            f"salary=${self.annual_salary:,.0f}, "
            f"productivity={self.productivity:.2f}, morale={self.morale:.2f})"
        )
