"""Business lifecycle management – turnaround actions and state transitions."""

from __future__ import annotations

from typing import Dict, List, Optional

from config.balancing import (
    SECTOR_EBITDA_MULTIPLES,
    DEFAULT_EBITDA_MULTIPLE,
    INITIAL_CAPITAL,
)
from economy.finance import compute_valuation, compute_sale_proceeds
from economy.pricing import marketing_demand_boost, revenue_from_pricing
from models.business import Business, AcquisitionMode, BusinessStatus
from models.financial import Transaction, TransactionType


class BusinessManager:
    """Manages turnaround actions and lifecycle for a single owned business."""

    def __init__(self, business: Business) -> None:
        self.business = business

    # ------------------------------------------------------------------
    # Turnaround actions
    # ------------------------------------------------------------------

    def adjust_pricing(self, price_change_pct: float) -> str:
        """
        Change prices by *price_change_pct* (e.g. 0.10 = +10%).
        Updates demand_factor using price elasticity model.
        Returns a description string.
        """
        from economy.pricing import price_elasticity_multiplier
        old_factor = self.business.demand_factor
        demand_change = price_elasticity_multiplier(price_change_pct)
        self.business.demand_factor = max(0.05, old_factor * demand_change)
        direction = "increased" if price_change_pct > 0 else "decreased"
        return (
            f"Prices {direction} by {abs(price_change_pct)*100:.1f}%. "
            f"Demand factor: {old_factor:.2f} → {self.business.demand_factor:.2f}"
        )

    def set_marketing_spend(self, monthly_spend: float) -> str:
        """Set monthly marketing spend; updates demand_factor."""
        old_spend = self.business.marketing_spend_monthly
        self.business.marketing_spend_monthly = max(0.0, monthly_spend)
        boost = marketing_demand_boost(monthly_spend, self.business.demand_factor)
        # Apply boost relative to base (reset each call)
        base_demand = self.business.demand_factor / marketing_demand_boost(old_spend, 1.0)
        self.business.demand_factor = base_demand * boost
        return (
            f"Marketing spend set to ${monthly_spend:,.0f}/mo. "
            f"Demand factor: {self.business.demand_factor:.2f}"
        )

    def invest_maintenance(self, amount: float) -> str:
        """One-time maintenance investment improves condition."""
        gain = min(amount / 10_000 * 0.05, 0.20)
        old_cond = self.business.condition
        self.business.condition = min(1.0, self.business.condition + gain)
        # Improved condition reduces ongoing maintenance costs
        self.business.maintenance_monthly = max(
            100, self.business.maintenance_monthly * (1 - gain * 0.5)
        )
        return (
            f"Invested ${amount:,.0f} in maintenance. "
            f"Condition: {old_cond:.2f} → {self.business.condition:.2f}"
        )

    def improve_processes(self) -> tuple[str, float]:
        """
        Improve operational processes (costs $5,000).
        Reduces COGS rate and improves quality.
        Returns (description, cost).
        """
        if self.business.process_improvement_level >= 5:
            return "Process improvements already at maximum level.", 0.0
        cost = 5_000.0
        self.business.process_improvement_level += 1
        cogs_reduction = 0.01  # 1% cogs reduction per level
        self.business.cogs_rate = max(0.05, self.business.cogs_rate - cogs_reduction)
        quality_gain = 3.0
        self.business.quality_score = min(100, self.business.quality_score + quality_gain)
        lvl = self.business.process_improvement_level
        return (
            f"Process improvement level {lvl}/5 applied. "
            f"COGS rate reduced by 1%, quality +{quality_gain:.0f}."
        ), cost

    def upgrade_equipment(self) -> tuple[str, float]:
        """
        Upgrade equipment (costs 10% of purchase price per level, max 5 levels).
        Increases capacity utilization and quality.
        Returns (description, cost).
        """
        if self.business.equipment_upgrade_level >= 5:
            return "Equipment already at maximum upgrade level.", 0.0
        cost = self.business.purchase_price * 0.10
        self.business.equipment_upgrade_level += 1
        util_gain = 0.05
        self.business.capacity_utilization = min(
            0.95, self.business.capacity_utilization + util_gain
        )
        quality_gain = 4.0
        self.business.quality_score = min(100, self.business.quality_score + quality_gain)
        lvl = self.business.equipment_upgrade_level
        return (
            f"Equipment upgrade level {lvl}/5 applied. "
            f"Utilization +{util_gain*100:.0f}%, quality +{quality_gain:.0f}."
        ), cost

    def negotiate_debt(self, extend_months: int = 12) -> tuple[str, float]:
        """
        Restructure outstanding debt (reduce interest rate / extend term).
        Returns (description, fee_charged).
        """
        from economy.debt import restructure_debt
        if self.business.outstanding_debt <= 0:
            return "No outstanding debt to restructure.", 0.0
        new_principal, _ = restructure_debt(
            self.business.outstanding_debt,
            current_rate=0.10,
            extend_months=extend_months,
        )
        fee = new_principal - self.business.outstanding_debt
        self.business.outstanding_debt = new_principal
        return (
            f"Debt restructured. New principal: ${new_principal:,.0f} "
            f"(fee: ${fee:,.0f})."
        ), fee

    # ------------------------------------------------------------------
    # Valuation & exit
    # ------------------------------------------------------------------

    def get_valuation(self) -> float:
        return compute_valuation(self.business)

    def sell_business(self, sale_price: float, acquisition_cost: float) -> Dict:
        proceeds = compute_sale_proceeds(self.business, sale_price, acquisition_cost)
        self.business.status = BusinessStatus.SOLD
        return proceeds
