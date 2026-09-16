"""
Signal-Based Position Sizer for Portfolio Construction OS.
"""

from typing import Dict, Any, Optional
import numpy as np
from portfolio.sizing.base import BasePositionSizer


class SignalBasedSizer(BasePositionSizer):
    """Maps continuous alpha predictions into raw normalized portfolio weights."""

    def __init__(self, long_only: bool = True, scale: str = "softmax"):
        self.long_only = long_only
        self.scale = scale

    def calculate_weights(
        self,
        alpha_scores: Dict[str, float],
        volatilities: Optional[Dict[str, float]] = None,
        confidence_scores: Optional[Dict[str, float]] = None,
        target_volatility: Optional[float] = None,
    ) -> Dict[str, float]:
        if not alpha_scores:
            return {}

        assets = list(alpha_scores.keys())
        scores = np.array([alpha_scores[a] for a in assets], dtype=float)

        if self.long_only:
            scores = np.maximum(0.0, scores)

        total = np.sum(np.abs(scores))
        if total <= 1e-12:
            n = len(assets)
            return {a: 1.0 / n for a in assets}

        weights = scores / total
        return {assets[i]: float(weights[i]) for i in range(len(assets))}
