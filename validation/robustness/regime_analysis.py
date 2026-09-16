"""
Regime-Annotated OOS Performance Analyzer for Walk-Forward OS.
Decomposes out-of-sample metrics across market regimes (Bull, Bear, High Volatility, Low Volatility).
"""

from typing import Dict, Any, List, Optional
import numpy as np
import pandas as pd


class RegimeOOSAnalyzer:
    """Annotates OOS predictions and returns with regime classifications."""

    @staticmethod
    def analyze_regime_performance(
        fold_returns: np.ndarray,
        regime_labels: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        rets = np.array(fold_returns, dtype=float)
        n = len(rets)

        if regime_labels is None or len(regime_labels) != n:
            # Generate synthetic regime labels based on rolling vol/return
            regimes = []
            for i in range(n):
                if i < 10:
                    regimes.append("NORMAL_VOL")
                else:
                    vol = float(np.std(rets[max(0, i - 10) : i + 1]))
                    ret = float(np.mean(rets[max(0, i - 10) : i + 1]))
                    if vol > 0.02:
                        regimes.append("HIGH_VOLATILITY")
                    elif ret < -0.001:
                        regimes.append("BEAR_MARKET")
                    elif ret > 0.001:
                        regimes.append("BULL_MARKET")
                    else:
                        regimes.append("NORMAL_VOL")
            regime_labels = regimes

        df = pd.DataFrame({"return": rets, "regime": regime_labels})
        grouped = df.groupby("regime")

        regime_breakdown = {}
        for name, group in grouped:
            r = group["return"].values
            mean_r = float(np.mean(r)) if len(r) > 0 else 0.0
            std_r = float(np.std(r)) if len(r) > 1 else 1e-8
            sharpe = float((mean_r * np.sqrt(252)) / (std_r * np.sqrt(252))) if std_r > 0 else 0.0
            win_rate = float(np.mean(r > 0)) if len(r) > 0 else 0.0

            regime_breakdown[name] = {
                "sample_count": len(group),
                "mean_return": round(mean_r, 6),
                "sharpe_ratio": round(sharpe, 2),
                "win_rate_pct": round(win_rate * 100.0, 2),
            }

        return {
            "status": "COMPLETED",
            "total_observations": n,
            "regimes_detected": list(regime_breakdown.keys()),
            "regime_breakdown": regime_breakdown,
        }
