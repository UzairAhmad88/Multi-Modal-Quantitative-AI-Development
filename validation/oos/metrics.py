"""
Out-of-Sample Metric Calculators for Walk-Forward OS.
Computes machine learning regression/classification metrics and trading performance metrics across OOS folds.
"""

from typing import Dict, Any, List, Optional
import numpy as np
import pandas as pd


class OOSMetricsCalculator:
    """Computes statistics across out-of-sample predictions and fold trading returns."""

    @staticmethod
    def compute_prediction_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
        """Calculates MAE, RMSE, MAPE, and Directional Accuracy."""
        yt = np.array(y_true, dtype=float)
        yp = np.array(y_pred, dtype=float)
        n = len(yt)

        if n == 0:
            return {"mae": 0.0, "rmse": 0.0, "mape": 0.0, "directional_accuracy": 0.0}

        mae = float(np.mean(np.abs(yt - yp)))
        rmse = float(np.sqrt(np.mean((yt - yp) ** 2)))

        # MAPE (epsilon protection for zero division)
        denom = np.where(np.abs(yt) < 1e-8, 1e-8, np.abs(yt))
        mape = float(np.mean(np.abs((yt - yp) / denom))) * 100.0

        # Directional accuracy (% same sign)
        same_sign = np.sign(yt) == np.sign(yp)
        dir_acc = float(np.mean(same_sign)) * 100.0

        return {
            "mae": round(mae, 6),
            "rmse": round(rmse, 6),
            "mape_pct": round(mape, 2),
            "directional_accuracy_pct": round(dir_acc, 2),
        }

    @staticmethod
    def compute_trading_metrics(returns: np.ndarray, annualization: int = 252) -> Dict[str, float]:
        """Calculates cumulative return, Sharpe ratio, Sortino ratio, max drawdown, and volatility."""
        r = np.array(returns, dtype=float)
        if len(r) == 0:
            return {
                "cumulative_return": 0.0,
                "annualized_return": 0.0,
                "volatility": 0.0,
                "sharpe_ratio": 0.0,
                "sortino_ratio": 0.0,
                "max_drawdown": 0.0,
            }

        cum_return = float(np.prod(1.0 + r) - 1.0)
        ann_return = float(np.mean(r) * annualization)
        vol = float(np.std(r, ddof=1) * np.sqrt(annualization)) if len(r) > 1 else 0.0

        sharpe = float(ann_return / vol) if vol > 1e-8 else 0.0

        downside_returns = r[r < 0]
        downside_vol = float(np.std(downside_returns, ddof=1) * np.sqrt(annualization)) if len(downside_returns) > 1 else 1e-8
        sortino = float(ann_return / downside_vol) if downside_vol > 1e-8 else 0.0

        # Max drawdown
        cum_equity = np.cumprod(1.0 + r)
        running_max = np.maximum.accumulate(cum_equity)
        drawdowns = (cum_equity - running_max) / running_max
        max_dd = float(np.abs(np.min(drawdowns))) if len(drawdowns) > 0 else 0.0

        return {
            "cumulative_return": round(cum_return, 4),
            "annualized_return": round(ann_return, 4),
            "volatility": round(vol, 4),
            "sharpe_ratio": round(sharpe, 2),
            "sortino_ratio": round(sortino, 2),
            "max_drawdown": round(max_dd, 4),
        }
