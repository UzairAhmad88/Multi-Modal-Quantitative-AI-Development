"""
Confidence-Based Position Sizer for Portfolio Construction OS.
"""

from typing import Dict, Any, Optional
import numpy as np
from portfolio.sizing.base import BasePositionSizer


class ConfidenceBasedSizer(BasePositionSizer):
    """Scales raw position weights by AI model confidence estimates."""

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
        conf = confidence_scores or {}

        # Scale alpha score by confidence
        scaled_scores = []
        for a in assets:
            score = alpha_scores[a]
            c = conf.get(a, 1.0)  # Default 1.0 if no confidence score
            c = float(np.clip(c, 0.0, 1.0))
            scaled_scores.append(score * c)

        scaled_scores = np.array(scaled_scores, dtype=float)
        positive_scores = np.maximum(0.0, scaled_scores)

        total = np.sum(positive_scores)
        if total <= 1e-12:
            n = len(assets)
            return {a: 1.0 / n for a in assets}

        weights = positive_scores / total
        return {assets[i]: float(weights[i]) for i in range(len(assets))}
