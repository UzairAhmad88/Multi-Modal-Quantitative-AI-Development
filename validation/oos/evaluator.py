"""
Out-of-Sample Performance Evaluator Engine for Walk-Forward OS.
Evaluates model fold predictions and aggregates out-of-sample metrics.
"""

from typing import Dict, Any, List, Optional
import numpy as np
import pandas as pd
from validation.oos.metrics import OOSMetricsCalculator


class OOSEvaluator:
    """Evaluates out-of-sample predictions across folds and aggregates performance statistics."""

    @staticmethod
    def evaluate_fold(
        fold_id: str,
        y_true: np.ndarray,
        y_pred: np.ndarray,
        fold_returns: Optional[np.ndarray] = None,
    ) -> Dict[str, Any]:
        pred_metrics = OOSMetricsCalculator.compute_prediction_metrics(y_true, y_pred)
        trade_metrics = {}
        if fold_returns is not None and len(fold_returns) > 0:
            trade_metrics = OOSMetricsCalculator.compute_trading_metrics(fold_returns)

        return {
            "fold_id": fold_id,
            "prediction_count": len(y_true),
            "prediction_metrics": pred_metrics,
            "trading_metrics": trade_metrics,
        }

    @staticmethod
    def aggregate_folds(fold_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Aggregates metrics across all walk-forward folds without destroying temporal fold structure."""
        if not fold_results:
            return {"status": "EMPTY"}

        sharpes = [f["trading_metrics"]["sharpe_ratio"] for f in fold_results if "trading_metrics" in f and "sharpe_ratio" in f["trading_metrics"]]
        cagrs = [f["trading_metrics"]["annualized_return"] for f in fold_results if "trading_metrics" in f and "annualized_return" in f["trading_metrics"]]
        maes = [f["prediction_metrics"]["mae"] for f in fold_results if "prediction_metrics" in f and "mae" in f["prediction_metrics"]]
        rmses = [f["prediction_metrics"]["rmse"] for f in fold_results if "prediction_metrics" in f and "rmse" in f["prediction_metrics"]]

        return {
            "total_folds": len(fold_results),
            "mean_out_of_sample_sharpe": float(round(np.mean(sharpes), 2)) if sharpes else 0.0,
            "std_out_of_sample_sharpe": float(round(np.std(sharpes), 2)) if sharpes else 0.0,
            "min_out_of_sample_sharpe": float(round(np.min(sharpes), 2)) if sharpes else 0.0,
            "max_out_of_sample_sharpe": float(round(np.max(sharpes), 2)) if sharpes else 0.0,
            "positive_fold_pct": float(round(np.mean(np.array(sharpes) > 0) * 100.0, 2)) if sharpes else 0.0,
            "mean_annualized_return": float(round(np.mean(cagrs), 4)) if cagrs else 0.0,
            "mean_mae": float(round(np.mean(maes), 6)) if maes else 0.0,
            "mean_rmse": float(round(np.mean(rmses), 6)) if rmses else 0.0,
        }
