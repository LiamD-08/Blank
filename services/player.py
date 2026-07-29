"""Player state and portfolio management."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from config.balancing import INITIAL_CAPITAL, RENT_MARKUP_MIN, RENT_MARKUP_MAX
from models.business import Business, AcquisitionMode, BusinessStatus
from models.financial import Transaction, TransactionType


@dataclass
class AcquisitionRecord:
    """Records how/when/how much a business was acquired."""
    business_id: str
    mode: AcquisitionMode
    acquisition_cost: float   # amount spent at acquisition
    day_acquired: int
    lease_monthly: float = 0.0


class Player:
    """Tracks player capital, portfolio, and transaction ledger."""

    def __init__(self, starting_capital: float = INITIAL_CAPITAL) -> None:
        self.cash: float = starting_capital
        self.portfolio: List[Business] = []
        self.acquisition_records: Dict[str, AcquisitionRecord] = {}
        self.transaction_ledger: List[Transaction] = []
        self.total_days: int = 0

    # ------------------------------------------------------------------
    # Financial helpers
    # ------------------------------------------------------------------

    def record_transaction(self, txn: Transaction) -> None:
        self.cash += txn.amount
        self.transaction_ledger.append(txn)

    def can_afford(self, amount: float) -> bool:
        return self.cash >= amount

    # ------------------------------------------------------------------
    # Acquisition
    # ------------------------------------------------------------------

    def acquire_business(
        self,
        business: Business,
        mode: AcquisitionMode,
        price: float,
        lease_monthly: float = 0.0,
        current_day: int = 0,
    ) -> bool:
        """
        Attempt to acquire a business.
        Returns True on success, False if insufficient funds.
        """
        if mode == AcquisitionMode.BUYOUT:
            if not self.can_afford(price):
                return False
            txn = Transaction(
                day=current_day,
                amount=-price,
                type=TransactionType.ACQUISITION,
                description=f"Buyout: {business.name}",
                business_id=business.id,
            )
            self.record_transaction(txn)
            acq_cost = price

        else:  # RENT
            # No upfront cost for rent (just ongoing lease)
            acq_cost = 0.0

        business.status = BusinessStatus.OWNED
        business.acquisition_mode = mode
        business.lease_monthly = lease_monthly
        business.acquisition_day = current_day
        self.portfolio.append(business)
        self.acquisition_records[business.id] = AcquisitionRecord(
            business_id=business.id,
            mode=mode,
            acquisition_cost=acq_cost,
            day_acquired=current_day,
            lease_monthly=lease_monthly,
        )
        return True

    def release_rented_business(self, business: Business, current_day: int) -> str:
        """End a lease agreement (walk away from a rented business)."""
        if business.acquisition_mode != AcquisitionMode.RENT:
            return "This business was not acquired via rent/lease."
        business.status = BusinessStatus.AVAILABLE
        self.portfolio.remove(business)
        del self.acquisition_records[business.id]
        return f"Lease for {business.name} released."

    # ------------------------------------------------------------------
    # Portfolio stats
    # ------------------------------------------------------------------

    @property
    def owned_businesses(self) -> List[Business]:
        return [b for b in self.portfolio if b.status == BusinessStatus.OWNED]

    @property
    def total_monthly_cashflow(self) -> float:
        return sum(b.ebitda_monthly for b in self.owned_businesses)

    @property
    def portfolio_value(self) -> float:
        from economy.finance import compute_valuation
        return sum(compute_valuation(b) for b in self.owned_businesses)

    @property
    def net_worth(self) -> float:
        return self.cash + self.portfolio_value

    def summary(self) -> Dict:
        return {
            "cash": self.cash,
            "portfolio_count": len(self.owned_businesses),
            "portfolio_value": self.portfolio_value,
            "net_worth": self.net_worth,
            "monthly_cashflow": self.total_monthly_cashflow,
        }
