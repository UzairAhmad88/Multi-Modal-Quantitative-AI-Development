"""
Concentration & Diversity Analyzer for Portfolio Construction OS.
"""

from typing import Dict, Any, List
import numpy as np


class ConcentrationAnalyzer:
    """Computes HHI, effective number of positions, and top position concentration ratios."""

    @staticmethod
    def analyze_concentration(weights: Dict[str, float]) -> Dict[str, Any]:
        if not weights:
            return {
                "hhi": 0.0,
                "effective_n": 0.0,
                "largest_position": 0.0,
                "top5_exposure": 0.0,
                "top10_exposure": 0.0,
            }

        w_vals = np.array([abs(w) for w in weights.values()], dtype=float)
        total = np.sum(w_vals)
        if total > 0:
            norm_w = w_vals / total
        else:
            norm_w = np.zeros_like(w_vals)

        hhi = float(np.sum(norm_w**2))
        effective_n = float(1.0 / hhi) if hhi > 1e-12 else 0.0

        sorted_w = np.sort(norm_w)[::-1]
        largest = float(sorted_w[0]) if len(sorted_w) > 0 else 0.0
        top5 = float(np.sum(sorted_w[:5]))
        top10 = float(np.sum(sorted_w[:10]))

        return {
            "hhi": hhi,
            "effective_n": effective_n,
            "largest_position": largest,
            "top5_exposure": top5,
            "top10_exposure": top10,
        }
