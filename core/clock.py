"""Game clock – tracks in-game date and provides calendar helpers."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple


_MONTHS = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
]

_DAYS_IN_MONTH = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]


@dataclass
class GameClock:
    """Tracks the current in-game date starting from day 1, month 1, year 1."""

    year: int = 1
    month: int = 1      # 1-12
    day: int = 1        # 1-days_in_month
    total_days: int = 0  # cumulative days elapsed since start

    def advance(self, days: int = 1) -> None:
        """Advance the clock by *days* days."""
        for _ in range(days):
            self._advance_one_day()

    def _advance_one_day(self) -> None:
        self.total_days += 1
        self.day += 1
        days_in_current = _DAYS_IN_MONTH[self.month - 1]
        if self.day > days_in_current:
            self.day = 1
            self.month += 1
            if self.month > 12:
                self.month = 1
                self.year += 1

    @property
    def month_name(self) -> str:
        return _MONTHS[self.month - 1]

    @property
    def date_str(self) -> str:
        return f"Year {self.year}, {self.month_name} {self.day}"

    @property
    def month_index(self) -> int:
        """Zero-based month index (0 = January)."""
        return self.month - 1

    def days_until_next_month(self) -> int:
        return _DAYS_IN_MONTH[self.month - 1] - self.day + 1

    def is_first_day_of_month(self) -> bool:
        return self.day == 1

    def total_months_elapsed(self) -> int:
        return (self.year - 1) * 12 + (self.month - 1)

    def __str__(self) -> str:
        return self.date_str
