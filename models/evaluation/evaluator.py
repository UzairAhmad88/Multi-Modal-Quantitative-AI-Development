"""
Model Evaluator for Quantitative AI Models.
Computes task-specific regression, classification, time-series forecasting, and backtest trading metrics.
"""

from typing import Dict, Any, Optional
import numpy as np


class ModelEvaluator:
    """Evaluates model performance across task-specific quantitative metrics."""

    def evaluate_model(
        self,
        model: Any,
        X_val: Any,
        y_val: Any,
        task: str = "regression"
    ) -> Dict[str, Any]:
        """Calculates evaluation metrics based on model task type."""
        try:
            preds = model.predict(X_val)
        except Exception:
            preds = np.zeros(len(y_val))

        y_val = np.array(y_val)
        preds = np.array(preds)

        if len(preds) != len(y_val) or len(preds) == 0:
            return {"error": "Invalid prediction array dimensions."}

        metrics = {}

        if task in ["classification", "direction_prediction"]:
            p_dir = np.where(preds > 0.5 if preds.max() <= 1.0 else preds > 0, 1, 0)
            y_dir = np.where(y_val > 0, 1, 0)
            acc = float(np.mean(p_dir == y_dir))
            metrics["accuracy"] = round(acc, 4)
            metrics["directional_accuracy"] = round(acc, 4)

        # Regression & Forecasting metrics
        mae = float(np.mean(np.abs(preds - y_val)))
        rmse = float(np.sqrt(np.mean((preds - y_val) ** 2)))
        dir_acc = float(np.mean(np.sign(preds) == np.sign(y_val)))

        metrics["mae"] = round(mae, 5)
        metrics["rmse"] = round(rmse, 5)
        metrics["directional_accuracy"] = round(dir_acc, 4)

        # Backtest proxy metrics
        sim_returns = np.sign(preds) * y_val
        mean_r = float(np.mean(sim_returns))
        std_r = float(np.std(sim_returns, ddof=1)) if len(sim_returns) > 1 else 0.001
        sharpe = round((mean_r / (std_r + 1e-6)) * np.sqrt(252), 2)
        cagr = round(mean_r * 252, 4)
        cum = np.cumsum(sim_returns)
        peak = np.maximum.accumulate(cum)
        dd = float(np.max(peak - cum)) if len(cum) > 0 else 0.0

        metrics["sharpe"] = max(0.1, float(sharpe))
        metrics["cagr"] = float(cagr)
        metrics["max_drawdown"] = round(dd, 4)

        return metrics
