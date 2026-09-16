"""
Model Error Analyzer for Quantitative Research Intelligence.
Inspects false positives, false negatives, directional prediction failures, and multimodal signal disagreement.
"""

from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np


class ModelErrorAnalyzer:
    """Analyzes model failure modes and modal disagreement."""

    def analyze_errors(
        self,
        predictions: pd.Series,
        actuals: pd.Series,
        regimes: Optional[pd.Series] = None
    ) -> Dict[str, Any]:
        """Calculates direction accuracy, false positives, false negatives, and MSE."""
        if len(predictions) != len(actuals) or len(predictions) == 0:
            return {"status": "INVALID_INPUT", "metrics": {}}

        df = pd.DataFrame({"pred": predictions, "act": actuals}).dropna()
        if df.empty:
            return {"status": "EMPTY", "metrics": {}}

        df["pred_dir"] = np.sign(df["pred"])
        df["act_dir"] = np.sign(df["act"])
        df["correct"] = df["pred_dir"] == df["act_dir"]

        accuracy = float(df["correct"].mean())
        mse = float(((df["pred"] - df["act"]) ** 2).mean())

        # False positives (predicted positive, actual negative)
        fp = df[(df["pred_dir"] > 0) & (df["act_dir"] <= 0)]
        # False negatives (predicted negative, actual positive)
        fn = df[(df["pred_dir"] < 0) & (df["act_dir"] >= 0)]

        error_summary = {
            "total_predictions": len(df),
            "directional_accuracy": round(accuracy, 4),
            "mse": round(mse, 6),
            "false_positives_count": len(fp),
            "false_negatives_count": len(fn),
            "false_positive_rate": round(len(fp) / max(1, (df["pred_dir"] > 0).sum()), 4),
            "false_negative_rate": round(len(fn) / max(1, (df["pred_dir"] < 0).sum()), 4)
        }

        # Breakdown by regime if available
        regime_analysis = {}
        if regimes is not None:
            df["regime"] = regimes
            for reg, group in df.groupby("regime"):
                if len(group) > 0:
                    regime_analysis[str(reg)] = {
                        "count": len(group),
                        "directional_accuracy": round(float(group["correct"].mean()), 4),
                        "mse": round(float(((group["pred"] - group["act"]) ** 2).mean()), 6)
                    }

        return {
            "status": "SUCCESS",
            "metrics": error_summary,
            "regime_error_breakdown": regime_analysis
        }

    def analyze_multimodal_disagreement(
        self,
        market_signal: float,
        news_signal: float,
        fundamental_signal: float
    ) -> Dict[str, Any]:
        """Measures directional consensus and disagreement across individual modalities."""
        signals = {
            "market": np.sign(market_signal),
            "news": np.sign(news_signal),
            "fundamental": np.sign(fundamental_signal)
        }
        unique_dirs = set(signals.values())

        if len(unique_dirs) == 1:
            consensus = "FULL_CONSENSUS"
            desc = "All modalities agree on signal direction."
        elif len(unique_dirs) == 2:
            consensus = "PARTIAL_DISAGREEMENT"
            desc = "Two modalities agree while one disagrees."
        else:
            consensus = "HIGH_DISAGREEMENT"
            desc = "Modalities provide conflicting directional signals."

        std_dev = float(np.std([market_signal, news_signal, fundamental_signal]))

        return {
            "consensus_type": consensus,
            "description": desc,
            "modal_signals": {"market": market_signal, "news": news_signal, "fundamental": fundamental_signal},
            "disagreement_std_dev": round(std_dev, 4)
        }
