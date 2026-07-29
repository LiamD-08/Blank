"""Random event system for the simulation."""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Callable, List, Optional

from models.business import Business


@dataclass
class GameEvent:
    name: str
    description: str
    financial_impact: float    # one-time cash effect (negative = cost)
    morale_impact: float       # -1 to +1 on all employees
    utilization_impact: float  # -0.x to +0.x on capacity_utilization
    reputation_impact: float   # -x to +x on reputation
    condition_impact: float    # -x to +x on condition


_POSITIVE_EVENTS = [
    GameEvent(
        name="Rave Review",
        description="A local blogger wrote a glowing review of your business.",
        financial_impact=0,
        morale_impact=0.05,
        utilization_impact=0.05,
        reputation_impact=8,
        condition_impact=0,
    ),
    GameEvent(
        name="Local Award",
        description="Your business won a local excellence award.",
        financial_impact=0,
        morale_impact=0.10,
        utilization_impact=0.08,
        reputation_impact=12,
        condition_impact=0,
    ),
    GameEvent(
        name="Bulk Order",
        description="A large client placed an unusually large one-time order.",
        financial_impact=5_000,
        morale_impact=0.03,
        utilization_impact=0.0,
        reputation_impact=2,
        condition_impact=0,
    ),
]

_NEGATIVE_EVENTS = [
    GameEvent(
        name="Equipment Failure",
        description="A key piece of equipment broke down unexpectedly.",
        financial_impact=-3_000,
        morale_impact=-0.05,
        utilization_impact=-0.08,
        reputation_impact=-3,
        condition_impact=-0.05,
    ),
    GameEvent(
        name="Bad Review",
        description="An unhappy customer left a scathing online review.",
        financial_impact=0,
        morale_impact=-0.03,
        utilization_impact=-0.04,
        reputation_impact=-6,
        condition_impact=0,
    ),
    GameEvent(
        name="Key Employee Quit",
        description="A high-performing employee resigned unexpectedly.",
        financial_impact=-2_000,
        morale_impact=-0.08,
        utilization_impact=-0.05,
        reputation_impact=-2,
        condition_impact=0,
    ),
    GameEvent(
        name="Supply Chain Disruption",
        description="A supplier issue caused delivery delays.",
        financial_impact=-1_500,
        morale_impact=-0.02,
        utilization_impact=-0.06,
        reputation_impact=-4,
        condition_impact=0,
    ),
]


def maybe_trigger_event(business: Business, portfolio_size: int) -> Optional[GameEvent]:
    """
    Randomly trigger an event for *business*.
    Chaos increases with portfolio size (max 30% chance per month).
    Returns the triggered GameEvent or None.
    """
    base_chance = 0.10 + (portfolio_size - 1) * 0.03
    base_chance = min(0.30, base_chance)

    if random.random() > base_chance:
        return None

    # 40% chance of positive, 60% negative
    pool = _POSITIVE_EVENTS if random.random() < 0.4 else _NEGATIVE_EVENTS
    event = random.choice(pool)
    _apply_event(business, event)
    return event


def _apply_event(business: Business, event: GameEvent) -> None:
    """Apply event effects to the business."""
    business.reputation = max(0, min(100, business.reputation + event.reputation_impact))
    business.condition = max(0, min(1, business.condition + event.condition_impact))
    business.capacity_utilization = max(
        0, min(0.95, business.capacity_utilization + event.utilization_impact)
    )
    # Apply morale to employees
    for emp in business.employees:
        if emp.is_active:
            emp.morale = max(0.0, min(1.0, emp.morale + event.morale_impact))
