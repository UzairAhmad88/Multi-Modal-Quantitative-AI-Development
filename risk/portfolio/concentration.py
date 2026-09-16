"""
Concentration & Sector Risk Analyzer for Advanced Risk Engine OS.
"""

from typing import Dict, Any, List, Optional
import numpy as np


class ConcentrationRiskAnalyzer:
    """Computes HHI, effective number of positions, top-N exposures, and sector risk concentration."""

    @staticmethod
    def analyze(weights: Dict[str, float], asset_metadata: Optional[Dict[str, Dict[str, Any]]] = None) -> Dict[str, Any]:
        if not weights:
            return {"hhi": 0.0, "effective_n": 0.0, "largest_position": 0.0, "top5_exposure": 0.0, "top10_exposure": 0.0}

        w_vals = np.array([abs(w) for w in weights.values()], dtype=float)
        tot = float(np.sum(w_vals))
        norm_w = w_vals / tot if tot > 0 else np.zeros_like(w_vals)

        hhi = float(np.sum(norm_w**2))
        effective_n = float(1.0 / hhi) if hhi > 1e-12 else 0.0

        sorted_w = np.sort(norm_w)[::-1]
        largest = float(sorted_w[0]) if len(sorted_w) > 0 else 0.0
        top5 = float(np.sum(sorted_w[:5]))
        top10 = float(np.sum(sorted_w[:10]))

        # Sector breakdown
        sector_exposures: Dict[str, float] = {}
        if asset_metadata:
            for a, w in weights.items():
                sec = asset_metadata.get(a, {}).get("sector", "Unassigned")
                sector_exposures[sec] = sector_exposures.get(sec, 0.0) + abs(w)

        return {
            "hhi": hhi,
            "effective_n": effective_n,
            "largest_position": largest,
            "top5_exposure": top5,
            "top10_exposure": top10,
            "sector_exposures": sector_exposures,
        }
