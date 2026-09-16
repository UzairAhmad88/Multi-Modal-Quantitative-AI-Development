"""
Market Calendar Module
Determines market session open/close status, trading hours, weekends, and holidays.
"""

from datetime import datetime, time, timezone, date
from typing import Dict, Any, Optional


class MarketCalendar:
    """Quantitative Market Calendar Engine for US Equities."""

    def __init__(self, tz_name: str = "UTC"):
        self.tz_name = tz_name
        self.market_open_time = time(13, 30)  # 13:30 UTC (09:30 EST)
        self.market_close_time = time(20, 0)   # 20:00 UTC (16:00 EST)

        self.holidays = {
            date(2023, 1, 1),   # New Year's Day
            date(2023, 1, 16),  # MLK Day
            date(2023, 2, 20),  # Presidents Day
            date(2023, 4, 7),   # Good Friday
            date(2023, 5, 29),  # Memorial Day
            date(2023, 6, 19),  # Juneteenth
            date(2023, 7, 4),   # Independence Day
            date(2023, 9, 4),   # Labor Day
            date(2023, 11, 23), # Thanksgiving
            date(2023, 12, 25), # Christmas
        }

    def is_market_open(self, dt: Optional[datetime] = None) -> bool:
        """Check if market is open at given datetime (UTC)."""
        dt = dt or datetime.now(timezone.utc)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)

        # Check weekend (5 = Saturday, 6 = Sunday)
        if dt.weekday() in (5, 6):
            return False

        # Check holiday
        if dt.date() in self.holidays:
            return False

        # Check trading hours
        curr_time = dt.time()
        return self.market_open_time <= curr_time <= self.market_close_time

    def get_session_status(self, dt: Optional[datetime] = None) -> Dict[str, Any]:
        """Return comprehensive market session metadata."""
        dt = dt or datetime.now(timezone.utc)
        open_status = self.is_market_open(dt)
        return {
            "timestamp": dt.isoformat(),
            "is_open": open_status,
            "status": "OPEN" if open_status else "CLOSED",
            "day_of_week": dt.strftime("%A"),
            "is_weekend": dt.weekday() in (5, 6),
            "is_holiday": dt.date() in self.holidays
        }
