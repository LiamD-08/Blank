"""Dynamic pricing logic for businesses."""

from __future__ import annotations

import math


def price_elasticity_multiplier(price_change_pct: float, elasticity: float = -1.5) -> float:
    """
    Estimate demand multiplier from a price change percentage.

    Args:
        price_change_pct: fractional change in price (e.g. 0.10 = 10% increase).
        elasticity: price elasticity of demand (negative means higher price → less demand).
    Returns:
        Demand multiplier (e.g. 0.85 = 15% demand drop).
    """
    return (1 + price_change_pct) ** elasticity


def revenue_from_pricing(
    base_revenue: float,
    price_change_pct: float,
    elasticity: float = -1.5,
) -> float:
    """
    Compute new revenue after a price change, accounting for demand elasticity.

    Revenue = base_revenue * (1 + price_change_pct) * demand_multiplier
    """
    demand_mult = price_elasticity_multiplier(price_change_pct, elasticity)
    return base_revenue * (1 + price_change_pct) * demand_mult


def marketing_demand_boost(
    monthly_spend: float,
    base_demand: float,
    saturation_spend: float = 5000.0,
) -> float:
    """
    Calculate demand multiplier from marketing spend using a log curve.

    Returns a multiplier >= 1.0.
    """
    if monthly_spend <= 0:
        return 1.0
    boost = 0.2 * math.log1p(monthly_spend / saturation_spend)
    return 1.0 + boost
