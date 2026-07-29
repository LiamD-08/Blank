"""Debt & interest calculation helpers."""

from __future__ import annotations

import random
from config.balancing import (
    ANNUAL_INTEREST_RATE_MIN,
    ANNUAL_INTEREST_RATE_MAX,
    DEBT_RESTRUCTURE_FEE,
)


def generate_interest_rate() -> float:
    """Return a random annual interest rate within configured bounds."""
    return random.uniform(ANNUAL_INTEREST_RATE_MIN, ANNUAL_INTEREST_RATE_MAX)


def monthly_interest(principal: float, annual_rate: float) -> float:
    """Return the monthly interest on a given principal."""
    return principal * (annual_rate / 12)


def monthly_debt_payment(
    principal: float,
    annual_rate: float,
    remaining_months: int,
) -> float:
    """Calculate fixed monthly payment using standard amortization formula."""
    if remaining_months <= 0 or principal <= 0:
        return 0.0
    monthly_rate = annual_rate / 12
    if monthly_rate == 0:
        return principal / remaining_months
    factor = (1 + monthly_rate) ** remaining_months
    return principal * (monthly_rate * factor) / (factor - 1)


def restructure_debt(
    principal: float,
    current_rate: float,
    extend_months: int,
) -> tuple[float, float]:
    """
    Restructure debt by extending the term.
    Returns (new_principal_after_fee, new_rate).
    Fee is added to principal.
    """
    fee = principal * DEBT_RESTRUCTURE_FEE
    new_principal = principal + fee
    new_rate = max(current_rate * 0.9, ANNUAL_INTEREST_RATE_MIN)
    return new_principal, new_rate
