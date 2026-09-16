"""
Portfolio Exposure & Leverage Risk Engine for Advanced Risk Engine OS.
"""

from typing import Dict, Any


class ExposureRiskEngine:
    """Evaluates Gross, Net, and Leverage Risk metrics."""

    @staticmethod
    def calculate_exposures(weights: Dict[str, float]) -> Dict[str, float]:
        long_exp = sum(w for w in weights.values() if w > 0)
        short_exp = sum(abs(w) for w in weights.values() if w < 0)

        gross = long_exp + short_exp
        net = long_exp - short_exp
        leverage = gross
        cash = max(0.0, 1.0 - net)

        return {
            "long_exposure": float(long_exp),
            "short_exposure": float(short_exp),
            "gross_exposure": float(gross),
            "net_exposure": float(net),
            "leverage": float(leverage),
            "cash_weight": float(cash),
        }
