"""Recruitment – job posting, applicants, hiring pipeline."""

from __future__ import annotations

import random
import uuid
from typing import Dict, List, Optional, Tuple

from config.balancing import (
    EMPLOYEE_SALARY_RANGES,
    HIRING_SUCCESS_RATE_MIN,
    HIRING_SUCCESS_RATE_MAX,
    ONBOARDING_WEEKS,
)
from models.employee import Employee, EmployeeRole, EmployeeStatus

_FIRST_NAMES = [
    "Alex", "Jordan", "Morgan", "Casey", "Taylor", "Riley", "Drew", "Quinn",
    "Avery", "Blake", "Cameron", "Dana", "Emery", "Finley", "Harper", "Jamie",
]
_LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Davis", "Miller",
    "Wilson", "Moore", "Taylor", "Anderson", "Thomas", "Jackson", "White",
]


def _random_name() -> str:
    return f"{random.choice(_FIRST_NAMES)} {random.choice(_LAST_NAMES)}"


def _role_from_str(role_str: str) -> EmployeeRole:
    for role in EmployeeRole:
        if role.value == role_str:
            return role
    return EmployeeRole.UNSKILLED_WORKER


def generate_applicant(role: EmployeeRole) -> Employee:
    """Generate a random job applicant for a given role."""
    salary_range = EMPLOYEE_SALARY_RANGES.get(
        role.value, EMPLOYEE_SALARY_RANGES["unskilled_worker"]
    )
    salary = random.uniform(*salary_range)
    skill = random.uniform(0.3, 0.9)
    morale = random.uniform(0.6, 0.9)  # applicants start motivated
    return Employee(
        id=str(uuid.uuid4()),
        name=_random_name(),
        role=role,
        annual_salary=round(salary, -2),
        skill_level=round(skill, 2),
        productivity=round(skill * 0.8, 2),
        morale=round(morale, 2),
        quality_contribution=round(skill * 0.7, 2),
        status=EmployeeStatus.APPLICANT,
        onboarding_days_remaining=ONBOARDING_WEEKS * 7,
    )


def get_applicants(role: EmployeeRole, count: int = 3) -> List[Employee]:
    """Return a pool of applicants for a given role."""
    return [generate_applicant(role) for _ in range(count)]


def make_offer(applicant: Employee) -> Tuple[bool, str]:
    """
    Simulate making a job offer. Returns (accepted, message).
    Success rate depends on balancing constants.
    """
    success_rate = random.uniform(HIRING_SUCCESS_RATE_MIN, HIRING_SUCCESS_RATE_MAX)
    if random.random() < success_rate:
        applicant.status = EmployeeStatus.ONBOARDING
        return True, f"{applicant.name} accepted the offer!"
    return False, f"{applicant.name} declined the offer."


def hire_employee(
    role: EmployeeRole,
    business_employees: List[Employee],
    salary_override: Optional[float] = None,
) -> Tuple[Optional[Employee], str]:
    """
    Post a job, pick the best applicant, and try to hire them.
    Returns (hired_employee_or_None, message).
    """
    applicants = get_applicants(role)
    # Pick best by skill
    applicants.sort(key=lambda e: e.skill_level, reverse=True)
    best = applicants[0]

    if salary_override is not None:
        best.annual_salary = salary_override

    accepted, msg = make_offer(best)
    if accepted:
        best.status = EmployeeStatus.ONBOARDING
        business_employees.append(best)
        return best, msg
    return None, msg


def start_training(employee: Employee) -> Tuple[str, float]:
    """
    Start a training program for an employee.
    Returns (description, cost).
    """
    from config.balancing import TRAINING_PAYOFF_WEEKS_MIN, TRAINING_PAYOFF_WEEKS_MAX, TRAINING_COST_PER_WEEK
    if employee.is_being_trained:
        return f"{employee.name} is already in training.", 0.0
    if not employee.is_active:
        return f"{employee.name} is not an active employee.", 0.0
    weeks = random.randint(TRAINING_PAYOFF_WEEKS_MIN, TRAINING_PAYOFF_WEEKS_MAX)
    cost = weeks * TRAINING_COST_PER_WEEK
    employee.is_being_trained = True
    employee.training_weeks_remaining = weeks
    return (
        f"{employee.name} enrolled in {weeks}-week training (${cost:,.0f})."
    ), float(cost)
