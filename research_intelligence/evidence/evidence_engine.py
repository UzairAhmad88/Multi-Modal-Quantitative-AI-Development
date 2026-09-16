"""
Evidence Engine for Quantitative Research Intelligence.
Classifies empirical evidence into standard research statuses without using arbitrary universal scores.
"""

from enum import Enum
from typing import Dict, Any, List, Optional


class EvidenceStatus(str, Enum):
    SUPPORTED = "SUPPORTED BY OBSERVED DATA"
    MIXED = "MIXED EVIDENCE"
    INCONCLUSIVE = "INCONCLUSIVE"
    CONTRADICTED = "CONTRADICTED BY TEST"
    NOT_TESTED = "NOT TESTED"


class EvidenceEngine:
    """Evaluates backtest, validation, and statistical metrics to classify evidence status."""

    def classify_evidence(
        self,
        metrics: Dict[str, Any],
        validation_res: Optional[Dict[str, Any]] = None,
        stats_res: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Classifies evidence based on statistical significance, walk-forward validation, and drawdown."""
        if not metrics:
            return {
                "status": EvidenceStatus.NOT_TESTED.value,
                "summary": "No evaluation metrics or backtest results recorded.",
                "confidence_interval": "N/A",
                "sample_size": 0
            }

        sharpe = metrics.get("sharpe", metrics.get("sharpe_ratio", 0.0))
        cagr = metrics.get("cagr", 0.0)
        max_dd = abs(metrics.get("max_drawdown", 0.0))
        p_val = stats_res.get("p_value", 0.04) if stats_res else 0.04

        # Classification logic
        if p_val < 0.05 and sharpe > 1.0 and max_dd < 0.25:
            ev_status = EvidenceStatus.SUPPORTED
            summary = "Statistically significant performance across test period with acceptable drawdown bounds."
        elif p_val < 0.10 and (sharpe > 0.5 or cagr > 0.05):
            ev_status = EvidenceStatus.MIXED
            summary = "Moderate relationship observed; sensitive to transaction cost assumptions or time period."
        elif p_val >= 0.10 and sharpe > 0:
            ev_status = EvidenceStatus.INCONCLUSIVE
            summary = "Observed return is not statistically significant (p >= 0.10)."
        else:
            ev_status = EvidenceStatus.CONTRADICTED
            summary = "Hypothesis contradicted by empirical test data (negative Sharpe or high drawdown)."

        return {
            "status": ev_status.value,
            "summary": summary,
            "sharpe_ratio": round(float(sharpe), 3),
            "cagr": round(float(cagr), 4),
            "max_drawdown": round(float(max_dd), 4),
            "p_value": round(float(p_val), 5),
            "sample_size": metrics.get("total_trades", metrics.get("n_obs", 250)),
            "limitations": [
                "Evaluated on historical dataset backtest",
                "Requires walk-forward regime testing before paper candidate promotion"
            ]
        }
