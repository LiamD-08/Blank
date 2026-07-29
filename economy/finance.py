"""P&L, cashflow, and business valuation helpers."""

from __future__ import annotations

import random
from typing import Dict, List, Optional

from config.balancing import (
    SECTOR_EBITDA_MULTIPLES,
    DEFAULT_EBITDA_MULTIPLE,
    SALE_TRANSACTION_COST,
    CAPITAL_GAINS_TAX,
    UNCERTAINTY_FACTOR_MIN,
    UNCERTAINTY_FACTOR_MAX,
    SEASONAL_AMPLITUDE,
)
from models.business import Business
from models.financial import Transaction, TransactionType


def apply_noise(value: float) -> float:
    """Apply random ±(5-10%) noise to a value."""
    noise_pct = random.uniform(UNCERTAINTY_FACTOR_MIN, UNCERTAINTY_FACTOR_MAX)
    direction = random.choice([-1, 1])
    return value * (1 + direction * noise_pct)


def seasonal_demand_factor(sector: str, month_index: int) -> float:
    """
    Return a seasonal demand multiplier (centred at 1.0).
    Uses a simple sinusoidal model peaking in mid-year for most sectors.
    """
    amplitude = SEASONAL_AMPLITUDE.get(sector, 0.05)
    # hospitality and retail peak in winter months (month 11–12, 0)
    if sector in ("retail", "hospitality"):
        peak_month = 11  # December
    elif sector == "restaurant":
        peak_month = 6  # July
    else:
        peak_month = 6
    import math
    angle = 2 * math.pi * (month_index - peak_month) / 12
    return 1.0 + amplitude * math.cos(angle)


def compute_daily_pnl(business: Business, day: int, month_index: int) -> List[Transaction]:
    """
    Compute all P&L transactions for a single day.
    Returns a list of Transaction objects.
    """
    txns: List[Transaction] = []
    daily_factor = 1 / 30  # approximate

    # Revenue (with noise and seasonality)
    season = seasonal_demand_factor(business.sector, month_index)
    raw_revenue = business.monthly_revenue * daily_factor * season
    revenue = apply_noise(raw_revenue)
    txns.append(Transaction(
        day=day,
        amount=revenue,
        type=TransactionType.REVENUE,
        description="Daily revenue",
        business_id=business.id,
    ))

    # COGS
    cogs = revenue * business.cogs_rate
    txns.append(Transaction(
        day=day,
        amount=-cogs,
        type=TransactionType.COGS,
        description="Cost of goods sold",
        business_id=business.id,
    ))

    # Labor (spread daily)
    labor = business.monthly_labor_cost * daily_factor
    txns.append(Transaction(
        day=day,
        amount=-labor,
        type=TransactionType.LABOR,
        description="Daily labor cost",
        business_id=business.id,
    ))

    # Overhead (spread daily)
    overhead = business.overhead_monthly * daily_factor
    txns.append(Transaction(
        day=day,
        amount=-overhead,
        type=TransactionType.OVERHEAD,
        description="Daily overhead",
        business_id=business.id,
    ))

    # Maintenance
    maintenance = business.maintenance_monthly * daily_factor
    txns.append(Transaction(
        day=day,
        amount=-maintenance,
        type=TransactionType.MAINTENANCE,
        description="Daily maintenance",
        business_id=business.id,
    ))

    # Marketing
    if business.marketing_spend_monthly > 0:
        marketing = business.marketing_spend_monthly * daily_factor
        txns.append(Transaction(
            day=day,
            amount=-marketing,
            type=TransactionType.MARKETING,
            description="Daily marketing spend",
            business_id=business.id,
        ))

    return txns


def compute_monthly_summary(transactions: List[Transaction]) -> Dict:
    """Aggregate a month's worth of transactions into a summary dict."""
    revenue = sum(t.amount for t in transactions if t.type == TransactionType.REVENUE)
    cogs = abs(sum(t.amount for t in transactions if t.type == TransactionType.COGS))
    labor = abs(sum(t.amount for t in transactions if t.type == TransactionType.LABOR))
    overhead = abs(sum(t.amount for t in transactions if t.type == TransactionType.OVERHEAD))
    maintenance = abs(sum(t.amount for t in transactions if t.type == TransactionType.MAINTENANCE))
    marketing = abs(sum(t.amount for t in transactions if t.type == TransactionType.MARKETING))
    debt_service = abs(sum(t.amount for t in transactions if t.type == TransactionType.DEBT_SERVICE))

    gross_profit = revenue - cogs
    ebitda = gross_profit - labor - overhead - maintenance - marketing - debt_service
    gross_margin = gross_profit / revenue if revenue else 0.0
    operating_margin = ebitda / revenue if revenue else 0.0

    return {
        "revenue": revenue,
        "cogs": cogs,
        "gross_profit": gross_profit,
        "labor": labor,
        "overhead": overhead,
        "maintenance": maintenance,
        "marketing": marketing,
        "debt_service": debt_service,
        "ebitda": ebitda,
        "gross_margin": gross_margin,
        "operating_margin": operating_margin,
    }


def compute_valuation(business: Business) -> float:
    """
    Estimate business sale value.
    Formula: (annualised_EBITDA × sector_multiple) − debt + asset_adjustments
    """
    annual_ebitda = business.ebitda_monthly * 12
    multiple = SECTOR_EBITDA_MULTIPLES.get(business.sector, DEFAULT_EBITDA_MULTIPLE)

    # Adjust multiple for reputation and recent profitability trend
    rep_adj = (business.reputation - 50) / 100  # -0.5 to +0.5
    multiple = multiple * (1 + rep_adj * 0.2)

    # Asset value: rough approximation from purchase_price * condition
    asset_value = business.purchase_price * business.condition * 0.3

    raw_value = annual_ebitda * multiple - business.outstanding_debt + asset_value
    return max(raw_value, 0.0)


def compute_sale_proceeds(
    business: Business,
    sale_price: float,
    acquisition_cost: float,
) -> Dict:
    """
    Calculate net proceeds from selling a business.
    """
    transaction_cost = sale_price * SALE_TRANSACTION_COST
    gross_gain = sale_price - acquisition_cost
    tax = max(gross_gain, 0) * CAPITAL_GAINS_TAX
    net_proceeds = sale_price - transaction_cost - tax
    return {
        "sale_price": sale_price,
        "transaction_cost": transaction_cost,
        "gross_gain": gross_gain,
        "tax": tax,
        "net_proceeds": net_proceeds,
    }
