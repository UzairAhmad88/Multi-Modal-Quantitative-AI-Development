"""
Drawdown & Tail Distribution Analytics for Advanced Risk Engine OS.
"""

from typing import Dict, Any, List, Optional
import numpy as np
import pandas as pd
from risk.core.risk_result import DrawdownEvent


class DrawdownAnalyzer:
    """Extracts maximum drawdown, current drawdown, duration, and DrawdownEvents from return series."""

    @staticmethod
    def analyze_drawdown(
        portfolio_returns: np.ndarray,
        dates: Optional[List[str]] = None,
        initial_value: float = 100000.0,
    ) -> Dict[str, Any]:
        r = np.array(portfolio_returns, dtype=float)
        if len(r) == 0:
            return {
                "max_drawdown": 0.0,
                "current_drawdown": 0.0,
                "max_duration_days": 0,
                "drawdown_events": [],
            }

        cumulative = initial_value * np.cumprod(1.0 + r)
        cum_max = np.maximum.accumulate(cumulative)
        drawdowns = (cum_max - cumulative) / cum_max

        max_dd = float(np.max(drawdowns))
        curr_dd = float(drawdowns[-1])

        dt_strings = dates or [f"T_{i}" for i in range(len(r))]

        # Extract Drawdown Events
        events: List[DrawdownEvent] = []
        in_dd = False
        peak_idx = 0
        trough_idx = 0

        for i in range(len(cumulative)):
            if cumulative[i] < cum_max[i]:
                if not in_dd:
                    in_dd = True
                    peak_idx = max(0, i - 1)
                    trough_idx = i
                elif cumulative[i] < cumulative[trough_idx]:
                    trough_idx = i
            else:
                if in_dd:
                    in_dd = False
                    recovery_idx = i
                    dd_val = float((cumulative[peak_idx] - cumulative[trough_idx]) / cumulative[peak_idx])
                    if dd_val >= 0.02:  # Only log material drawdowns >= 2%
                        events.append(DrawdownEvent(
                            start_date=dt_strings[peak_idx],
                            trough_date=dt_strings[trough_idx],
                            recovery_date=dt_strings[recovery_idx],
                            peak_value=float(cumulative[peak_idx]),
                            trough_value=float(cumulative[trough_idx]),
                            drawdown=dd_val,
                            duration=trough_idx - peak_idx,
                            recovery_duration=recovery_idx - trough_idx,
                        ))

        # Handle ongoing unrecovered drawdown
        if in_dd:
            dd_val = float((cumulative[peak_idx] - cumulative[trough_idx]) / cumulative[peak_idx])
            if dd_val >= 0.02:
                events.append(DrawdownEvent(
                    start_date=dt_strings[peak_idx],
                    trough_date=dt_strings[trough_idx],
                    recovery_date=None,
                    peak_value=float(cumulative[peak_idx]),
                    trough_value=float(cumulative[trough_idx]),
                    drawdown=dd_val,
                    duration=trough_idx - peak_idx,
                    recovery_duration=None,
                ))

        max_dur = max([ev.duration for ev in events], default=0)

        return {
            "max_drawdown": max_dd,
            "current_drawdown": curr_dd,
            "max_duration_days": max_dur,
            "drawdown_events": [ev.to_dict() for ev in events],
            "cumulative_series": cumulative.tolist(),
            "drawdown_series": drawdowns.tolist(),
        }
