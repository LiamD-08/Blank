"""Tests for business valuation logic."""

import pytest
from businesses.marketplace import generate_failing_business
from economy.finance import compute_valuation
from models.business import Business, BusinessStatus


def _make_business(**kwargs) -> Business:
    defaults = dict(
        id="val-001",
        name="Valuation Co",
        sector="service",
        size="small",
        purchase_price=150_000,
        outstanding_debt=20_000,
        annual_revenue_base=250_000,
        cogs_rate=0.25,
        overhead_monthly=5_000,
        maintenance_monthly=500,
        reputation=60.0,
        customer_satisfaction=60.0,
        capacity_utilization=0.70,
        quality_score=60.0,
        condition=0.7,
        status=BusinessStatus.OWNED,
    )
    defaults.update(kwargs)
    return Business(**defaults)


class TestValuationMultiples:
    def test_technology_higher_than_restaurant(self):
        """Technology sector should command higher multiples than restaurant."""
        tech = _make_business(sector="technology", outstanding_debt=0)
        rest = _make_business(sector="restaurant", outstanding_debt=0)
        assert compute_valuation(tech) > compute_valuation(rest)

    def test_reputation_boosts_valuation(self):
        high_rep = _make_business(reputation=90)
        low_rep = _make_business(reputation=10)
        assert compute_valuation(high_rep) > compute_valuation(low_rep)


class TestValuationGeneratedBusiness:
    def test_generated_business_valuation_positive(self):
        for sector in ("restaurant", "retail", "service", "technology"):
            biz = generate_failing_business(sector)
            # Failing businesses may have negative EBITDA; valuation floor is 0
            val = compute_valuation(biz)
            assert val >= 0, f"Negative valuation for {sector}: {val}"

    def test_valuation_decreases_with_more_debt(self):
        biz_a = _make_business(outstanding_debt=0)
        biz_b = _make_business(outstanding_debt=100_000)
        biz_c = _make_business(outstanding_debt=300_000)
        assert compute_valuation(biz_a) >= compute_valuation(biz_b)
        assert compute_valuation(biz_b) >= compute_valuation(biz_c)


class TestValuationAfterTurnaround:
    def test_improving_utilization_raises_valuation(self):
        biz_low = _make_business(capacity_utilization=0.3)
        biz_high = _make_business(capacity_utilization=0.85)
        assert compute_valuation(biz_high) > compute_valuation(biz_low)

    def test_ebitda_drives_valuation(self):
        """Higher EBITDA should mean higher valuation, all else equal."""
        biz_low_rev = _make_business(annual_revenue_base=100_000)
        biz_high_rev = _make_business(annual_revenue_base=500_000)
        assert compute_valuation(biz_high_rev) > compute_valuation(biz_low_rev)
