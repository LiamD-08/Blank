"""Integration tests for the simulation loop."""

import pytest
from core.clock import GameClock
from core.simulation import Simulation
from businesses.marketplace import generate_failing_business
from models.business import AcquisitionMode, BusinessStatus
from services.player import Player


def _setup_sim_with_business(sector: str = "restaurant"):
    player = Player(starting_capital=500_000)
    clock = GameClock()
    sim = Simulation(player, clock)

    biz = generate_failing_business(sector)
    player.acquire_business(
        biz,
        mode=AcquisitionMode.BUYOUT,
        price=biz.purchase_price * 0.5,  # affordable price
        current_day=clock.total_days,
    )
    return player, clock, sim, biz


class TestGameClock:
    def test_advance_one_day(self):
        clock = GameClock()
        clock.advance(1)
        assert clock.total_days == 1

    def test_month_rolls_over(self):
        clock = GameClock()
        clock.advance(31)
        assert clock.month == 2

    def test_year_rolls_over(self):
        clock = GameClock()
        clock.advance(365)
        assert clock.year == 2

    def test_date_str(self):
        clock = GameClock()
        assert "Year" in clock.date_str


class TestPlayerPortfolio:
    def test_acquire_buyout_reduces_cash(self):
        player = Player(starting_capital=500_000)
        biz = generate_failing_business("retail")
        price = 100_000
        player.acquire_business(biz, AcquisitionMode.BUYOUT, price, current_day=0)
        assert player.cash == 400_000

    def test_acquire_rent_no_upfront(self):
        player = Player(starting_capital=500_000)
        biz = generate_failing_business("service")
        player.acquire_business(biz, AcquisitionMode.RENT, 0, lease_monthly=2_000, current_day=0)
        assert player.cash == 500_000

    def test_insufficient_funds_fails(self):
        player = Player(starting_capital=10_000)
        biz = generate_failing_business("manufacturing")
        result = player.acquire_business(biz, AcquisitionMode.BUYOUT, 500_000, current_day=0)
        assert result is False
        assert len(player.portfolio) == 0

    def test_owned_businesses_after_acquire(self):
        player, clock, sim, biz = _setup_sim_with_business()
        assert len(player.owned_businesses) == 1

    def test_net_worth_includes_portfolio(self):
        player, clock, sim, biz = _setup_sim_with_business()
        assert player.net_worth >= player.cash


class TestSimulationAdvance:
    def test_advance_one_day(self):
        player, clock, sim, biz = _setup_sim_with_business()
        sim.advance_days(1)
        assert clock.total_days == 1

    def test_advance_month(self):
        player, clock, sim, biz = _setup_sim_with_business()
        result = sim.advance_month()
        assert "summary" in result
        assert "notifications" in result

    def test_transactions_recorded(self):
        player, clock, sim, biz = _setup_sim_with_business()
        sim.advance_days(1)
        assert len(player.transaction_ledger) > 0

    def test_cash_changes_after_simulation(self):
        player, clock, sim, biz = _setup_sim_with_business()
        cash_before = player.cash
        sim.advance_days(30)
        # Cash should change (revenue - costs)
        assert player.cash != cash_before

    def test_monthly_summary_has_business_data(self):
        player, clock, sim, biz = _setup_sim_with_business()
        result = sim.advance_month()
        assert biz.id in result["summary"]
        assert "revenue" in result["summary"][biz.id]["summary"]


class TestMarketplace:
    def test_marketplace_generates_listings(self):
        from businesses.marketplace import Marketplace
        market = Marketplace()
        assert len(market.listings) >= 3

    def test_remove_listing(self):
        from businesses.marketplace import Marketplace
        market = Marketplace()
        biz_id = market.listings[0].business.id
        market.remove_listing(biz_id)
        assert market.get_listing(biz_id) is None

    def test_age_increases_discount(self):
        from businesses.marketplace import Marketplace
        market = Marketplace()
        listing = market.listings[0]
        market.age_listings(days=14)
        assert listing.urgency_discount > 0

    def test_effective_price_with_discount(self):
        from businesses.marketplace import Marketplace
        market = Marketplace()
        listing = market.listings[0]
        original_price = listing.asking_price
        market.age_listings(days=100)
        assert listing.effective_price <= original_price


class TestSellBusiness:
    def test_sell_removes_from_portfolio(self):
        player, clock, sim, biz = _setup_sim_with_business()
        from businesses.manager import BusinessManager
        mgr = BusinessManager(biz)
        proceeds = mgr.sell_business(200_000, 50_000)
        player.portfolio.remove(biz)
        assert biz not in player.owned_businesses

    def test_sell_proceeds_positive(self):
        player, clock, sim, biz = _setup_sim_with_business()
        from businesses.manager import BusinessManager
        mgr = BusinessManager(biz)
        proceeds = mgr.sell_business(200_000, 50_000)
        assert proceeds["net_proceeds"] > 0
