"""
Rebalance Scheduler Module for Portfolio Construction OS.
"""

from typing import Dict, Any, Optional
import pandas as pd


class RebalanceScheduler:
    """Determines calendar-based rebalancing schedule execution."""

    @staticmethod
    def should_rebalance_calendar(
        current_timestamp: str,
        last_rebalance_timestamp: Optional[str] = None,
        frequency: str = "weekly",
    ) -> bool:
        if last_rebalance_timestamp is None:
            return True

        curr_dt = pd.to_datetime(current_timestamp)
        last_dt = pd.to_datetime(last_rebalance_timestamp)

        freq_lower = frequency.lower()
        if freq_lower == "daily":
            return (curr_dt - last_dt).days >= 1
        elif freq_lower == "weekly":
            return (curr_dt - last_dt).days >= 7
        elif freq_lower == "monthly":
            return (curr_dt - last_dt).days >= 30
        elif freq_lower == "quarterly":
            return (curr_dt - last_dt).days >= 90
        return False
