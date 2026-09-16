"""
Performance and Factor Attribution Engine.
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, List


class PerformanceAttributionEngine:
    """Calculates asset-level and model-level return attribution breakdown."""

    @staticmethod
    def calculate_asset_attribution(
        weights: Dict[str, float],
        realized_returns: Dict[str, float]
    ) -> Dict[str, Any]:
        """Calculates realized return contributions per asset: w_i * r_i."""
        total_return = 0.0
        attrib = {}
        for a, w in weights.items():
            r = realized_returns.get(a, 0.0)
            contrib = w * r
            total_return += contrib
            attrib[a] = {
                "weight": round(w, 4),
                "realized_return": round(r, 4),
                "contribution": round(contrib, 6)
            }

        return {
            "portfolio_realized_return": round(total_return, 4),
            "asset_attribution": attrib
        }
