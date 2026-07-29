"""Tests for financial calculations."""

import pytest
from economy.finance import (
    apply_noise,
    seasonal_demand_factor,
    compute_daily_pnl,
    compute_monthly_summary,
    compute_valuation,
    compute_sale_proceeds,
)
from models.business import Business, BusinessStatus
from models.financial import TransactionType


def _make_business(**kwargs) -> Business:
    defaults = dict(
        id="test-001",
        name="Test Bistro",
        sector="restaurant",
        size="small",
        purchase_price=100_000,
        outstanding_debt=30_000,
        annual_revenue_base=300_000,
        cogs_rate=0.32,
        overhead_monthly=6_000,
        maintenance_monthly=800,
        reputation=50.0,
        customer_satisfaction=50.0,
        capacity_utilization=0.6,
        quality_score=50.0,
        condition=0.5,
        status=BusinessStatus.OWNED,
    )
    defaults.update(kwargs)
    return Business(**defaults)


class TestApplyNoise:
    def test_noise_within_bounds(self):
        for _ in range(200):
            result = apply_noise(1000.0)
            assert 850 <= result <= 1150, f"Noise out of range: {result}"

    def test_noise_on_zero(self):
        assert apply_noise(0.0) == 0.0


class TestSeasonalDemandFactor:
    def test_returns_near_one(self):
        for sector in ("restaurant", "retail", "manufacturing", "service"):
            for month in range(12):
                factor = seasonal_demand_factor(sector, month)
                assert 0.5 <= factor <= 1.5, f"Unreasonable seasonal factor: {factor}"

    def test_peak_month_is_highest_for_retail(self):
        # retail peaks in December (month_index=11)
        dec = seasonal_demand_factor("retail", 11)
        jun = seasonal_demand_factor("retail", 5)
        assert dec > jun


class TestComputeDailyPnl:
    def test_returns_transactions(self):
        biz = _make_business()
        txns = compute_daily_pnl(biz, day=1, month_index=0)
        assert len(txns) >= 5

    def test_revenue_is_positive(self):
        biz = _make_business()
        txns = compute_daily_pnl(biz, day=1, month_index=0)
        rev = [t for t in txns if t.type == TransactionType.REVENUE]
        assert len(rev) == 1
        assert rev[0].amount > 0

    def test_expenses_are_negative(self):
        biz = _make_business()
        txns = compute_daily_pnl(biz, day=1, month_index=0)
        for t in txns:
            if t.type != TransactionType.REVENUE:
                assert t.amount <= 0

    def test_marketing_txn_when_spend_set(self):
        biz = _make_business(marketing_spend_monthly=2000)
        txns = compute_daily_pnl(biz, day=1, month_index=0)
        mkt = [t for t in txns if t.type == TransactionType.MARKETING]
        assert len(mkt) == 1

    def test_no_marketing_txn_when_zero(self):
        biz = _make_business(marketing_spend_monthly=0)
        txns = compute_daily_pnl(biz, day=1, month_index=0)
        mkt = [t for t in txns if t.type == TransactionType.MARKETING]
        assert len(mkt) == 0


class TestComputeMonthlySummary:
    def test_all_keys_present(self):
        biz = _make_business()
        txns = []
        for day in range(1, 31):
            txns.extend(compute_daily_pnl(biz, day=day, month_index=0))
        summary = compute_monthly_summary(txns)
        for key in ("revenue", "cogs", "gross_profit", "labor", "overhead",
                    "maintenance", "ebitda", "gross_margin", "operating_margin"):
            assert key in summary

    def test_gross_profit_calculation(self):
        biz = _make_business()
        txns = []
        for day in range(1, 31):
            txns.extend(compute_daily_pnl(biz, day=day, month_index=0))
        s = compute_monthly_summary(txns)
        assert abs(s["gross_profit"] - (s["revenue"] - s["cogs"])) < 1


class TestComputeValuation:
    def test_positive_valuation_for_profitable_business(self):
        # High-revenue, low-cost business should have positive valuation
        biz = _make_business(
            annual_revenue_base=600_000,
            cogs_rate=0.20,
            overhead_monthly=3_000,
            maintenance_monthly=200,
            capacity_utilization=0.8,
        )
        val = compute_valuation(biz)
        assert val > 0

    def test_debt_reduces_valuation(self):
        biz_low_debt = _make_business(outstanding_debt=0)
        biz_high_debt = _make_business(outstanding_debt=500_000)
        assert compute_valuation(biz_low_debt) > compute_valuation(biz_high_debt)

    def test_valuation_non_negative(self):
        # Even a terrible business shouldn't return negative
        biz = _make_business(
            annual_revenue_base=10_000,
            cogs_rate=0.90,
            overhead_monthly=20_000,
            outstanding_debt=200_000,
        )
        assert compute_valuation(biz) >= 0


class TestComputeSaleProceeds:
    def test_keys_present(self):
        biz = _make_business()
        result = compute_sale_proceeds(biz, 200_000, 100_000)
        for key in ("sale_price", "transaction_cost", "gross_gain", "tax", "net_proceeds"):
            assert key in result

    def test_profit_taxed(self):
        biz = _make_business()
        result = compute_sale_proceeds(biz, 200_000, 100_000)
        assert result["tax"] > 0

    def test_no_tax_on_loss(self):
        biz = _make_business()
        result = compute_sale_proceeds(biz, 50_000, 100_000)
        assert result["tax"] == 0

    def test_net_proceeds_less_than_sale_price(self):
        biz = _make_business()
        result = compute_sale_proceeds(biz, 200_000, 100_000)
        assert result["net_proceeds"] < result["sale_price"]
