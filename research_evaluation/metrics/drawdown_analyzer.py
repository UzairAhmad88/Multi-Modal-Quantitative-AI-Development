"""
Drawdown Analyzer: Peak-to-trough analysis, max drawdown, duration, recovery date.
"""

import numpy as np
import pandas as pd
from typing import Union, List, Dict, Any


class DrawdownAnalyzer:
    """Analyzes drawdown series, peak-trough dynamics, and recovery durations."""

    def analyze_drawdowns(self, equity_curve: Union[List[float], pd.Series, np.ndarray]) -> Dict[str, Any]:
        """Calculates maximum drawdown, average drawdown, and drawdown durations."""
        eq = np.array(equity_curve, dtype=float)
        if len(eq) == 0:
            return {"max_drawdown": 0.0, "avg_drawdown": 0.0, "max_duration": 0}

        running_max = np.maximum.accumulate(eq)
        drawdowns = (eq - running_max) / running_max
        max_dd = abs(float(np.min(drawdowns))) if len(drawdowns) > 0 else 0.0
        avg_dd = abs(float(np.mean(drawdowns[drawdowns < 0]))) if np.any(drawdowns < 0) else 0.0

        # Duration analysis
        in_drawdown = drawdowns < 0
        durations = []
        curr_dur = 0
        for is_dd in in_drawdown:
            if is_dd:
                curr_dur += 1
            else:
                if curr_dur > 0:
                    durations.append(curr_dur)
                    curr_dur = 0
        if curr_dur > 0:
            durations.append(curr_dur)

        max_dur = max(durations) if durations else 0
        avg_dur = float(np.mean(durations)) if durations else 0.0

        return {
            "max_drawdown": round(max_dd, 4),
            "avg_drawdown": round(avg_dd, 4),
            "drawdown_series": drawdowns.tolist(),
            "max_duration_periods": max_dur,
            "avg_duration_periods": round(avg_dur, 1),
            "number_of_drawdowns": len(durations)
        }
