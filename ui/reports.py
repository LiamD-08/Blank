"""Financial report rendering."""

from __future__ import annotations

from typing import Dict, List

try:
    from tabulate import tabulate
    _HAS_TABULATE = True
except ImportError:
    _HAS_TABULATE = False

from models.business import Business
from models.financial import Transaction


def _fmt(val: float, currency: bool = True) -> str:
    if currency:
        sign = "-" if val < 0 else ""
        return f"{sign}${abs(val):>12,.0f}"
    return f"{val:.1%}"


def print_monthly_pnl(summary: Dict, business_name: str) -> None:
    """Print a P&L summary for a single business month."""
    rows = [
        ["Revenue",                      _fmt(summary["revenue"])],
        ["  Cost of Goods Sold",         _fmt(-summary["cogs"])],
        ["Gross Profit",                 _fmt(summary["gross_profit"])],
        ["  Labor",                      _fmt(-summary["labor"])],
        ["  Overhead",                   _fmt(-summary["overhead"])],
        ["  Maintenance",                _fmt(-summary["maintenance"])],
        ["  Marketing",                  _fmt(-summary["marketing"])],
        ["  Debt Service",               _fmt(-summary["debt_service"])],
        ["EBITDA",                        _fmt(summary["ebitda"])],
        ["Gross Margin",                  _fmt(summary["gross_margin"], currency=False)],
        ["Operating Margin",              _fmt(summary["operating_margin"], currency=False)],
    ]
    print(f"\n  ── P&L: {business_name} ──")
    if _HAS_TABULATE:
        print(tabulate(rows, headers=["Line Item", "Amount"], tablefmt="simple"))
    else:
        for row in rows:
            print(f"  {row[0]:<35} {row[1]}")


def print_kpi_table(business: Business) -> None:
    """Print KPI table for a business."""
    rows = [
        ["Reputation",            f"{business.reputation:.1f}/100"],
        ["Customer Satisfaction", f"{business.customer_satisfaction:.1f}/100"],
        ["Capacity Utilization",  f"{business.capacity_utilization:.1%}"],
        ["Quality Score",         f"{business.quality_score:.1f}/100"],
        ["Condition",             f"{business.condition:.1%}"],
        ["Headcount",             str(business.headcount)],
        ["Process Lvl",           f"{business.process_improvement_level}/5"],
        ["Equipment Lvl",         f"{business.equipment_upgrade_level}/5"],
    ]
    print(f"\n  ── KPIs: {business.name} ──")
    if _HAS_TABULATE:
        print(tabulate(rows, headers=["Metric", "Value"], tablefmt="simple"))
    else:
        for row in rows:
            print(f"  {row[0]:<30} {row[1]}")


def print_transaction_history(
    transactions: List[Transaction],
    limit: int = 20,
) -> None:
    """Print recent transactions."""
    recent = transactions[-limit:]
    rows = [
        [t.day, t.type.name, _fmt(t.amount), t.description[:40]]
        for t in reversed(recent)
    ]
    print("\n  ── Recent Transactions ──")
    if _HAS_TABULATE:
        print(tabulate(rows, headers=["Day", "Type", "Amount", "Description"], tablefmt="simple"))
    else:
        for row in rows:
            print(f"  Day {row[0]:>4}  {row[1]:<20} {row[2]}  {row[3]}")
