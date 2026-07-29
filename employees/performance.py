"""Employee productivity & quality calculations."""

from __future__ import annotations

import random
from typing import List

from config.balancing import (
    ONBOARDING_WEEKS,
    TRAINING_PAYOFF_WEEKS_MIN,
    TRAINING_PAYOFF_WEEKS_MAX,
    UNCERTAINTY_FACTOR_MIN,
    UNCERTAINTY_FACTOR_MAX,
)
from models.employee import Employee, EmployeeStatus


def tick_employee(employee: Employee, days: int = 1) -> None:
    """
    Advance an employee's state by *days* days.
    Handles onboarding ramp-up, training payoff, morale drift, etc.
    """
    employee.days_employed += days

    # Onboarding ramp-up
    if employee.status == EmployeeStatus.ONBOARDING:
        employee.onboarding_days_remaining = max(
            0, employee.onboarding_days_remaining - days
        )
        if employee.onboarding_days_remaining <= 0:
            employee.status = EmployeeStatus.ACTIVE
            # Ramp up productivity to skill level
            employee.productivity = employee.skill_level * 0.8

    # Training progression
    if employee.is_being_trained and employee.training_weeks_remaining > 0:
        # Approximate: training tick in weeks, convert
        weeks_passed = days / 7
        employee.training_weeks_remaining = max(
            0, employee.training_weeks_remaining - weeks_passed
        )
        if employee.training_weeks_remaining <= 0:
            employee.is_being_trained = False
            employee.training_weeks_completed += 1
            _apply_training_payoff(employee)

    # Natural morale drift toward 0.7 baseline
    if employee.is_active:
        _drift_morale(employee, days)
        _natural_productivity_variation(employee, days)


def _apply_training_payoff(employee: Employee) -> None:
    """Boost skill, productivity, and quality after completed training."""
    skill_gain = random.uniform(0.03, 0.08)
    employee.skill_level = min(1.0, employee.skill_level + skill_gain)
    prod_gain = random.uniform(0.02, 0.06)
    employee.productivity = min(1.0, employee.productivity + prod_gain)
    quality_gain = random.uniform(0.02, 0.05)
    employee.quality_contribution = min(1.0, employee.quality_contribution + quality_gain)


def _drift_morale(employee: Employee, days: int) -> None:
    """Morale slowly reverts to ~0.7 baseline; add small random noise."""
    baseline = 0.7
    drift_rate = 0.005 * days  # slow reversion
    if employee.morale > baseline:
        employee.morale = max(baseline, employee.morale - drift_rate)
    elif employee.morale < baseline:
        employee.morale = min(baseline, employee.morale + drift_rate)

    noise = random.uniform(-0.01, 0.01) * days
    employee.morale = max(0.0, min(1.0, employee.morale + noise))


def _natural_productivity_variation(employee: Employee, days: int) -> None:
    """Small daily productivity noise."""
    noise_range = UNCERTAINTY_FACTOR_MIN * days / 30
    noise = random.uniform(-noise_range, noise_range)
    employee.productivity = max(0.1, min(1.0, employee.productivity + noise))


def aggregate_productivity(employees: List[Employee]) -> float:
    """Return mean effective productivity across all active employees."""
    active = [e for e in employees if e.is_active]
    if not active:
        return 0.0
    return sum(e.effective_productivity for e in active) / len(active)


def aggregate_quality(employees: List[Employee]) -> float:
    """Return mean quality contribution across all active employees (0-1)."""
    active = [e for e in employees if e.is_active]
    if not active:
        return 0.0
    return sum(e.quality_contribution for e in active) / len(active)


def check_turnover_risk(employee: Employee) -> float:
    """Return probability (0-1) that employee quits this month."""
    from config.balancing import TURNOVER_BASE_RATE
    # Low morale increases turnover; high morale reduces it
    morale_factor = 2.0 - employee.morale * 2  # 0 morale → 2x, 1.0 morale → 0x
    return min(1.0, TURNOVER_BASE_RATE * morale_factor)
