"""Marketplace listing data model."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from models.business import Business


@dataclass
class MarketListing:
    """A business available for acquisition in the marketplace."""

    business: Business
    asking_price: float          # asking price (may differ from fair value)
    days_on_market: int = 0      # how long it's been listed
    urgency_discount: float = 0.0  # discount growing with time on market

    @property
    def effective_price(self) -> float:
        return max(self.asking_price * (1 - self.urgency_discount), 1.0)

    @property
    def fair_value(self) -> float:
        return self.business.purchase_price

    @property
    def discount_pct(self) -> float:
        if self.asking_price == 0:
            return 0.0
        return (self.asking_price - self.effective_price) / self.asking_price

    def __repr__(self) -> str:
        return (
            f"MarketListing({self.business.name!r}, "
            f"ask=${self.effective_price:,.0f}, "
            f"on_market={self.days_on_market}d)"
        )
