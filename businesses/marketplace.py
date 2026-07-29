"""Business generation and marketplace logic."""

from __future__ import annotations

import json
import os
import random
import uuid
from typing import List

from businesses.archetypes import ARCHETYPES, ALL_SECTORS, BusinessArchetype
from config.balancing import (
    MARKET_BUSINESS_COUNT_MIN,
    MARKET_BUSINESS_COUNT_MAX,
    RENT_MARKUP_MIN,
    RENT_MARKUP_MAX,
)
from models.business import Business, BusinessStatus
from models.market import MarketListing

_NAMES_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "business_names.json")

with open(_NAMES_PATH) as _f:
    _NAME_DATA = json.load(_f)


def _generate_name(sector: str) -> str:
    prefix = random.choice(_NAME_DATA["prefixes"])
    suffix_key = f"{sector}_names"
    suffixes = _NAME_DATA.get(suffix_key, _NAME_DATA["service_names"])
    suffix = random.choice(suffixes)
    return f"{prefix} {suffix}"


def _rand(lo: float, hi: float) -> float:
    return random.uniform(lo, hi)


def generate_failing_business(sector: str | None = None) -> Business:
    """Create a randomly generated failing business."""
    if sector is None:
        sector = random.choice(ALL_SECTORS)

    sizes = list(ARCHETYPES.get(sector, ARCHETYPES["service"]).keys())
    size = random.choice(sizes)
    arch: BusinessArchetype = ARCHETYPES[sector][size]

    purchase_price = _rand(*arch.price_range)
    annual_revenue = _rand(*arch.annual_revenue_range)
    debt = purchase_price * _rand(*arch.debt_ratio_range)
    cogs_rate = _rand(*arch.cogs_rate_range)
    overhead = _rand(*arch.overhead_monthly_range)
    maintenance = _rand(*arch.maintenance_monthly_range)

    # Failing businesses have poor KPIs
    reputation = _rand(20, 50)
    satisfaction = _rand(20, 50)
    utilization = _rand(0.25, 0.60)
    quality = _rand(20, 50)
    condition = _rand(0.30, 0.65)

    biz = Business(
        id=str(uuid.uuid4()),
        name=_generate_name(sector),
        sector=sector,
        size=size,
        purchase_price=round(purchase_price, -2),
        outstanding_debt=round(debt, -2),
        annual_revenue_base=round(annual_revenue, -2),
        cogs_rate=round(cogs_rate, 3),
        overhead_monthly=round(overhead, -1),
        maintenance_monthly=round(maintenance, -1),
        reputation=round(reputation, 1),
        customer_satisfaction=round(satisfaction, 1),
        capacity_utilization=round(utilization, 3),
        quality_score=round(quality, 1),
        condition=round(condition, 3),
        status=BusinessStatus.AVAILABLE,
    )
    return biz


def compute_lease_cost(business: Business) -> float:
    """Monthly lease cost for rent/lease acquisition mode."""
    annual_markup = _rand(RENT_MARKUP_MIN, RENT_MARKUP_MAX)
    return round(business.purchase_price * annual_markup / 12, -1)


class Marketplace:
    """Holds the current set of businesses available for acquisition."""

    def __init__(self) -> None:
        self.listings: List[MarketListing] = []
        self.refresh()

    def refresh(self) -> None:
        """Generate a fresh batch of failing businesses."""
        count = random.randint(MARKET_BUSINESS_COUNT_MIN, MARKET_BUSINESS_COUNT_MAX)
        self.listings = []
        for _ in range(count):
            biz = generate_failing_business()
            # Asking price is slightly above fair value for failing biz
            asking = biz.purchase_price * _rand(0.85, 1.05)
            self.listings.append(MarketListing(
                business=biz,
                asking_price=round(asking, -2),
            ))

    def age_listings(self, days: int = 1) -> None:
        """Age all listings, increasing urgency discount over time."""
        for listing in self.listings:
            listing.days_on_market += days
            # Discount increases by 0.5% per week on market, capped at 20%
            listing.urgency_discount = min(
                listing.days_on_market / 7 * 0.005, 0.20
            )

    def remove_listing(self, business_id: str) -> None:
        self.listings = [l for l in self.listings if l.business.id != business_id]

    def get_listing(self, business_id: str) -> MarketListing | None:
        for l in self.listings:
            if l.business.id == business_id:
                return l
        return None
