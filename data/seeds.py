"""Sample business data for seeding the marketplace."""

from __future__ import annotations

from businesses.marketplace import generate_failing_business
from models.market import MarketListing


def get_seed_businesses() -> list:
    """Return a list of pre-generated failing businesses for demos."""
    sectors = ["restaurant", "retail", "manufacturing", "service", "hospitality"]
    businesses = []
    for sector in sectors:
        biz = generate_failing_business(sector)
        asking = biz.purchase_price * 0.95
        businesses.append(MarketListing(business=biz, asking_price=round(asking, -2)))
    return businesses
