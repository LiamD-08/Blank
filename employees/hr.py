"""HR system – compensation, morale management, turnover, termination."""

from __future__ import annotations

import random
from typing import Dict, List, Tuple

from config.balancing import (
    BENEFITS_COST_RATE,
    LAYOFF_COST_WEEKS,
    TURNOVER_BASE_RATE,
)
from employees.performance import check_turnover_risk
from models.employee import Employee, EmployeeStatus


def monthly_total_compensation(employee: Employee) -> float:
    """Total monthly cost including benefits."""
    return employee.monthly_salary * (1 + BENEFITS_COST_RATE)


def total_monthly_labor_cost(employees: List[Employee]) -> float:
    """Sum of all active employee monthly comp including benefits."""
    return sum(
        monthly_total_compensation(e)
        for e in employees
        if e.status in (EmployeeStatus.ACTIVE, EmployeeStatus.ONBOARDING)
    )


def give_raise(employee: Employee, raise_pct: float) -> Tuple[str, float]:
    """
    Give an employee a raise.
    Returns (description, annual cost increase).
    """
    raise_pct = max(0.0, raise_pct)
    old_salary = employee.annual_salary
    employee.annual_salary *= (1 + raise_pct)
    cost_increase = employee.annual_salary - old_salary
    # Morale boost
    employee.morale = min(1.0, employee.morale + raise_pct * 0.5)
    return (
        f"{employee.name}'s salary raised by {raise_pct*100:.1f}% "
        f"(${old_salary:,.0f} → ${employee.annual_salary:,.0f})."
    ), cost_increase


def terminate_employee(employee: Employee) -> Tuple[str, float]:
    """
    Terminate an employee. Returns (description, severance_cost).
    Severance = LAYOFF_COST_WEEKS weeks of salary.
    """
    severance = employee.weekly_salary * LAYOFF_COST_WEEKS
    employee.status = EmployeeStatus.TERMINATED
    return (
        f"{employee.name} terminated. Severance: ${severance:,.0f}."
    ), severance


def process_monthly_turnover(employees: List[Employee]) -> Tuple[List[Employee], float]:
    """
    Check each employee for voluntary turnover. Remove those who quit.
    Returns (remaining_employees, total_replacement_cost_estimate).
    """
    remaining = []
    total_cost = 0.0
    for emp in employees:
        if emp.status != EmployeeStatus.ACTIVE:
            remaining.append(emp)
            continue
        risk = check_turnover_risk(emp)
        if random.random() < risk:
            # Employee quits; rough cost = 1 month salary to find replacement
            total_cost += emp.monthly_salary
            # Don't add to remaining (they've left)
        else:
            remaining.append(emp)
    return remaining, total_cost


def boost_team_morale(employees: List[Employee], amount: float) -> str:
    """Boost morale for all active employees by *amount* (0-1 scale)."""
    affected = 0
    for emp in employees:
        if emp.is_active:
            emp.morale = min(1.0, emp.morale + amount)
            affected += 1
    return f"Morale boosted for {affected} employees (+{amount*100:.0f}%)."
