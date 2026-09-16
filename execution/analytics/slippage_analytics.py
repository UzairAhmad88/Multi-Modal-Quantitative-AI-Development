"""
Slippage Analytics: Analyzes average, median, and breakdown of slippage across assets and order sizes.
"""

from typing import List, Dict, Any
import numpy as np
from execution.fills.fill_engine import Fill


class SlippageAnalytics:
    """Analyzes execution slippage distribution."""

    def analyze_slippage(self, fills: List[Fill]) -> Dict[str, Any]:
        """Calculates statistical slippage metrics across fills."""
        if not fills:
            return {"mean_slippage_cost": 0.0, "total_slippage_cost": 0.0, "max_slippage": 0.0}

        costs = [f.slippage for f in fills]
        total_cost = sum(costs)
        mean_cost = float(np.mean(costs))
        median_cost = float(np.median(costs))
        max_cost = float(np.max(costs))

        by_asset = {}
        for f in fills:
            if f.asset not in by_asset:
                by_asset[f.asset] = 0.0
            by_asset[f.asset] += f.slippage

        return {
            "total_slippage_cost": round(total_cost, 2),
            "mean_slippage_cost": round(mean_cost, 2),
            "median_slippage_cost": round(median_cost, 2),
            "max_slippage_cost": round(max_cost, 2),
            "slippage_by_asset": {a: round(c, 2) for a, c in by_asset.items()}
        }
