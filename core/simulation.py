"""Main simulation loop – drives daily ticks and monthly summaries."""

from __future__ import annotations

from typing import List, Optional

from core.clock import GameClock
from economy.finance import compute_daily_pnl, compute_monthly_summary
from employees.hr import process_monthly_turnover, total_monthly_labor_cost
from employees.performance import tick_employee, aggregate_productivity, aggregate_quality
from models.business import Business, AcquisitionMode
from models.financial import Transaction, TransactionType
from services.events import maybe_trigger_event
from services.player import Player


class Simulation:
    """Drives the game forward tick by tick."""

    def __init__(self, player: Player, clock: GameClock) -> None:
        self.player = player
        self.clock = clock
        self._month_transactions: List[Transaction] = []
        self._month_events: List[str] = []

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def advance_days(self, days: int = 1) -> List[str]:
        """
        Advance simulation by *days* days.
        Returns a list of event/notification strings.
        """
        notifications: List[str] = []
        for _ in range(days):
            msgs = self._tick_one_day()
            notifications.extend(msgs)
        return notifications

    def advance_month(self) -> dict:
        """
        Advance simulation to the end of the current month.
        Returns monthly summary dict.
        """
        days_left = self.clock.days_until_next_month()
        notifications = self.advance_days(days_left)
        summary = self._build_monthly_summary()
        self._month_transactions.clear()
        self._month_events.clear()
        return {"notifications": notifications, "summary": summary}

    # ------------------------------------------------------------------
    # Internal tick logic
    # ------------------------------------------------------------------

    def _tick_one_day(self) -> List[str]:
        notifications: List[str] = []
        self.clock.advance(1)
        day = self.clock.total_days
        month_idx = self.clock.month_index

        for business in self.player.owned_businesses:
            # Daily P&L
            txns = compute_daily_pnl(business, day, month_idx)
            for txn in txns:
                self.player.record_transaction(txn)
                self._month_transactions.append(txn)

            # Lease cost (spread daily)
            if business.acquisition_mode == AcquisitionMode.RENT and business.lease_monthly > 0:
                lease_daily = business.lease_monthly / 30
                txn = Transaction(
                    day=day,
                    amount=-lease_daily,
                    type=TransactionType.OVERHEAD,
                    description=f"Lease: {business.name}",
                    business_id=business.id,
                )
                self.player.record_transaction(txn)
                self._month_transactions.append(txn)

            # Tick employees
            for emp in business.employees:
                tick_employee(emp, days=1)

            # Monthly events (once per month on day 1)
            if self.clock.is_first_day_of_month():
                self._run_monthly_business_logic(business, notifications)

        return notifications

    def _run_monthly_business_logic(
        self, business: Business, notifications: List[str]
    ) -> None:
        """Logic that runs once per month per business."""
        # Update KPIs from employee performance
        prod = aggregate_productivity(business.employees)
        qual = aggregate_quality(business.employees)
        if business.employees:
            business.capacity_utilization = max(
                0.05,
                min(0.95, business.capacity_utilization * 0.95 + prod * 0.05),
            )
            business.quality_score = max(
                0,
                min(100, business.quality_score * 0.95 + qual * 100 * 0.05),
            )
        # Customer satisfaction drifts toward quality + reputation average
        target_sat = (business.quality_score + business.reputation) / 2
        business.customer_satisfaction = (
            business.customer_satisfaction * 0.9 + target_sat * 0.1
        )
        # Condition degrades slightly unless maintained
        business.condition = max(0.05, business.condition - 0.005)

        # Debt service
        if business.outstanding_debt > 0:
            from economy.debt import monthly_interest
            interest = monthly_interest(business.outstanding_debt, 0.10)
            principal_payment = min(business.outstanding_debt * 0.02, business.outstanding_debt)
            total_payment = interest + principal_payment
            business.outstanding_debt = max(0, business.outstanding_debt - principal_payment)
            txn = Transaction(
                day=self.clock.total_days,
                amount=-total_payment,
                type=TransactionType.DEBT_SERVICE,
                description=f"Debt service: {business.name}",
                business_id=business.id,
            )
            self.player.record_transaction(txn)
            self._month_transactions.append(txn)

        # Employee turnover
        business.employees, turnover_cost = process_monthly_turnover(business.employees)
        if turnover_cost > 0:
            notifications.append(
                f"[{business.name}] Employee turnover: ${turnover_cost:,.0f} replacement cost."
            )
            txn = Transaction(
                day=self.clock.total_days,
                amount=-turnover_cost,
                type=TransactionType.SEVERANCE,
                description=f"Turnover cost: {business.name}",
                business_id=business.id,
            )
            self.player.record_transaction(txn)

        # Random events
        event = maybe_trigger_event(business, len(self.player.owned_businesses))
        if event:
            self.player.cash += event.financial_impact
            msg = f"[{business.name}] EVENT: {event.name} – {event.description}"
            notifications.append(msg)
            self._month_events.append(msg)

    def _build_monthly_summary(self) -> dict:
        """Aggregate month's transactions into per-business and total summaries."""
        result = {}
        for business in self.player.owned_businesses:
            biz_txns = [t for t in self._month_transactions if t.business_id == business.id]
            result[business.id] = {
                "name": business.name,
                "summary": compute_monthly_summary(biz_txns),
            }
        return result
