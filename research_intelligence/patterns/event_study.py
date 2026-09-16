"""
Event Study Engine for Quantitative Research Intelligence.
Analyzes asset behavior around discrete event triggers (earnings, news spikes, price shocks)
across configurable event windows [-1,+1], [-3,+3], [-5,+5], [-10,+10].
"""

from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np
from scipy import stats


class EventStudyEngine:
    """Executes quantitative event studies surrounding discrete event timestamps."""

    DEFAULT_WINDOWS = [[-1, 1], [-3, 3], [-5, 5], [-10, 10]]

    def analyze_events(
        self,
        returns_df: pd.DataFrame,
        event_timestamps: List[Any],
        windows: Optional[List[List[int]]] = None,
        return_col: str = "returns"
    ) -> Dict[str, Any]:
        """Calculates cumulative excess returns and stats around event dates."""
        windows_to_use = windows or self.DEFAULT_WINDOWS
        if returns_df.empty or return_col not in returns_df.columns:
            return {"status": "INVALID_INPUT", "event_results": []}

        df = returns_df.copy()
        if not isinstance(df.index, pd.DatetimeIndex):
            try:
                df.index = pd.to_datetime(df.index)
            except Exception:
                pass

        results_by_window = []

        for win in windows_to_use:
            pre, post = win[0], win[1]
            window_returns = []

            for evt in event_timestamps:
                try:
                    evt_dt = pd.to_datetime(evt)
                    if evt_dt in df.index:
                        idx_pos = df.index.get_loc(evt_dt)
                    else:
                        # Find closest preceding index
                        sub = df.index[df.index <= evt_dt]
                        if len(sub) == 0:
                            continue
                        idx_pos = df.index.get_loc(sub[-1])

                    start_pos = max(0, idx_pos + pre)
                    end_pos = min(len(df), idx_pos + post + 1)

                    sub_series = df[return_col].iloc[start_pos:end_pos]
                    if len(sub_series) == (post - pre + 1):
                        cum_ret = float((1 + sub_series).prod() - 1)
                        window_returns.append(cum_ret)
                except Exception:
                    continue

            if window_returns:
                arr = np.array(window_returns)
                mean_ret = float(np.mean(arr))
                median_ret = float(np.median(arr))
                vol = float(np.std(arr, ddof=1)) if len(arr) > 1 else 0.0
                t_stat, p_val = stats.ttest_1samp(arr, 0.0) if len(arr) > 2 else (0.0, 1.0)

                results_by_window.append({
                    "window": f"[{pre},+{post}]",
                    "sample_events": len(arr),
                    "mean_cumulative_return": round(mean_ret, 4),
                    "median_cumulative_return": round(median_ret, 4),
                    "volatility": round(vol, 4),
                    "t_statistic": round(float(t_stat), 3),
                    "p_value": round(float(p_val), 5),
                    "is_significant": bool(p_val < 0.05)
                })

        return {
            "status": "SUCCESS",
            "total_events_analyzed": len(event_timestamps),
            "window_results": results_by_window
        }
