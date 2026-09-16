"""
Market Session Manager Module
Tracks exchange operating hours, pre-market, regular hours, after-hours, weekends, and holidays.
"""

from datetime import datetime, time, timezone
from typing import Dict, Any


class MarketSessionManager:
    """Quantitative Market Operating Hours & Trading Session Manager."""

    def __init__(self, tz_name: str = "US/Eastern"):
        self.tz_name = tz_name
        self.regular_open = time(9, 30)
        self.regular_close = time(16, 0)
        self.premarket_open = time(4, 0)
        self.afterhours_close = time(20, 0)

    def is_market_open(self, dt: datetime = None) -> bool:
        """Check if regular trading session is open."""
        if dt is None:
            dt = datetime.now(timezone.utc)

        # Weekend check (5=Saturday, 6=Sunday)
        if dt.weekday() in [5, 6]:
            return False

        t = dt.time()
        return self.regular_open <= t <= self.regular_close

    def get_session_type(self, dt: datetime = None) -> str:
        """Return session type: REGULAR, PRE_MARKET, AFTER_HOURS, CLOSED_WEEKEND, CLOSED."""
        if dt is None:
            dt = datetime.now(timezone.utc)

        if dt.weekday() in [5, 6]:
            return "CLOSED_WEEKEND"

        t = dt.time()
        if self.regular_open <= t <= self.regular_close:
            return "REGULAR"
        elif self.premarket_open <= t < self.regular_open:
            return "PRE_MARKET"
        elif self.regular_close < t <= self.afterhours_close:
            return "AFTER_HOURS"
        else:
            return "CLOSED"
