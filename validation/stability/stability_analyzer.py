"""
Stability Analyzer for Subperiod Windows, Rolling Metrics, and Regime Analysis.
"""

import numpy as np
from typing import List, Dict, Any
from validation.schemas.validation_schema import StabilityResult, SubperiodWindow


class StabilityAnalyzer:
    """
    Analyzes temporal stability across subperiods, rolling windows, and market regimes.
    """

    @staticmethod
    def analyze_subperiods(
        returns: np.ndarray, num_windows: int = 5, annual_factor: float = 252.0
    ) -> StabilityResult:
        n = len(returns)
        if n < num_windows * 5:
            return StabilityResult(subperiods=[], sharpe_std=0.0, drawdown_std=0.0, stability_score=0.0)

        window_size = n // num_windows
        subperiods: List[SubperiodWindow] = []
        sharpes: List[float] = []
        drawdowns: List[float] = []

        for i in range(num_windows):
            start = i * window_size
            end = n if i == num_windows - 1 else (i + 1) * window_size
            w_ret = returns[start:end]

            # Metrics calculation
            cum_ret = np.prod(1.0 + w_ret) - 1.0
            years = len(w_ret) / annual_factor
            cagr = (1.0 + cum_ret) ** (1.0 / max(years, 0.001)) - 1.0 if cum_ret > -1.0 else -1.0

            vol = np.std(w_ret, ddof=1) * np.sqrt(annual_factor) if len(w_ret) > 1 else 0.0
            mean_ret = np.mean(w_ret) * annual_factor
            sharpe = (mean_ret / vol) if vol > 0 else 0.0

            # Drawdown
            equity = np.cumprod(1.0 + w_ret)
            peak = np.maximum.accumulate(equity)
            dd = (equity - peak) / peak
            max_dd = float(np.min(dd)) if len(dd) > 0 else 0.0

            sharpes.append(sharpe)
            drawdowns.append(abs(max_dd))

            subperiods.append(
                SubperiodWindow(
                    window_index=i + 1,
                    start_date=f"Window {i+1} Start",
                    end_date=f"Window {i+1} End",
                    sample_size=len(w_ret),
                    cagr=round(float(cagr), 4),
                    volatility=round(float(vol), 4),
                    sharpe_ratio=round(float(sharpe), 4),
                    max_drawdown=round(float(max_dd), 4),
                )
            )

        sharpe_std = float(np.std(sharpes)) if len(sharpes) > 1 else 0.0
        drawdown_std = float(np.std(drawdowns)) if len(drawdowns) > 1 else 0.0

        # Stability score calculation (0 to 100)
        positive_ratio = sum(1 for s in sharpes if s > 0) / float(len(sharpes))
        score = max(0.0, min(100.0, (positive_ratio * 70.0) + max(0.0, 30.0 - (sharpe_std * 20.0))))

        return StabilityResult(
            subperiods=subperiods,
            sharpe_std=round(sharpe_std, 4),
            drawdown_std=round(drawdown_std, 4),
            stability_score=round(score, 1),
        )
