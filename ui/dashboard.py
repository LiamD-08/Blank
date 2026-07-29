"""Main dashboard – portfolio overview and marketplace display."""

from __future__ import annotations

from typing import List

from economy.finance import compute_valuation
from models.business import Business
from models.market import MarketListing
from services.player import Player

try:
    from tabulate import tabulate
    _HAS_TABULATE = True
except ImportError:
    _HAS_TABULATE = False


def _fmt_cash(v: float) -> str:
    sign = "-" if v < 0 else ""
    return f"{sign}${abs(v):,.0f}"


def show_player_summary(player: Player, date_str: str) -> None:
    """Print high-level player status."""
    print(f"\n{'='*60}")
    print(f"  Business Turnaround Simulation  |  {date_str}")
    print(f"{'='*60}")
    print(f"  Cash:            {_fmt_cash(player.cash)}")
    print(f"  Portfolio Value: {_fmt_cash(player.portfolio_value)}")
    print(f"  Net Worth:       {_fmt_cash(player.net_worth)}")
    print(f"  Monthly CF:      {_fmt_cash(player.total_monthly_cashflow)}")
    print(f"  Businesses:      {len(player.owned_businesses)}")
    print(f"{'='*60}")


def show_portfolio(player: Player) -> None:
    """Display owned businesses summary."""
    businesses = player.owned_businesses
    if not businesses:
        print("\n  Portfolio is empty.")
        return

    rows = []
    for b in businesses:
        val = compute_valuation(b)
        rows.append([
            b.name[:25],
            b.sector.title(),
            b.acquisition_mode.value.upper() if b.acquisition_mode else "-",
            _fmt_cash(b.monthly_revenue),
            _fmt_cash(b.ebitda_monthly),
            _fmt_cash(val),
            f"{b.reputation:.0f}",
            "YES" if b.is_profitable else "NO",
        ])

    headers = ["Name", "Sector", "Mode", "Rev/Mo", "EBITDA/Mo", "Value", "Rep", "Profit?"]
    print("\n  ── Your Portfolio ──")
    if _HAS_TABULATE:
        print(tabulate(rows, headers=headers, tablefmt="simple"))
    else:
        print("  " + "  ".join(f"{h:<14}" for h in headers))
        for row in rows:
            print("  " + "  ".join(f"{str(v):<14}" for v in row))


def show_marketplace(listings: List[MarketListing]) -> None:
    """Display available marketplace businesses."""
    if not listings:
        print("\n  Marketplace is empty. Advance time to refresh.")
        return

    rows = []
    for i, lst in enumerate(listings, 1):
        b = lst.business
        rows.append([
            i,
            b.name[:25],
            b.sector.title(),
            b.size.title(),
            _fmt_cash(lst.effective_price),
            _fmt_cash(b.outstanding_debt),
            _fmt_cash(b.annual_revenue_base / 12),
            f"{b.reputation:.0f}",
            f"{b.capacity_utilization:.0%}",
        ])

    headers = ["#", "Name", "Sector", "Size", "Price", "Debt", "Rev/Mo", "Rep", "Util"]
    print("\n  ── Marketplace ──")
    if _HAS_TABULATE:
        print(tabulate(rows, headers=headers, tablefmt="simple"))
    else:
        print("  " + "  ".join(f"{h:<14}" for h in headers))
        for row in rows:
            print("  " + "  ".join(f"{str(v):<14}" for v in row))
