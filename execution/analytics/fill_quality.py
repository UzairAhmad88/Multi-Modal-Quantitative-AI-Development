"""
Fill Quality Analytics: Evaluates fill prices against benchmarks (Arrival Price, VWAP, TWAP).
"""

from typing import List, Dict, Any
from execution.fills.fill_engine import Fill


class FillQualityAnalytics:
    """Benchmarking fill execution against Arrival Price, VWAP, and TWAP."""

    def evaluate_quality(
        self,
        fills: List[Fill],
        benchmarks: Dict[str, Dict[str, float]]
    ) -> Dict[str, Any]:
        """Compares realized fill prices against reference benchmarks."""
        if not fills:
            return {"avg_slippage_vs_arrival_bps": 0.0, "quality_score": 100.0}

        results = []
        for fill in fills:
            b = benchmarks.get(fill.asset, {})
            p_arr = b.get("arrival_price", fill.fill_price)
            p_vwap = b.get("vwap", fill.fill_price)
            p_twap = b.get("twap", fill.fill_price)

            p_fill = fill.fill_price

            vs_arr_bps = ((p_fill - p_arr) / p_arr * 10000.0) if p_arr > 0 else 0.0
            vs_vwap_bps = ((p_fill - p_vwap) / p_vwap * 10000.0) if p_vwap > 0 else 0.0
            vs_twap_bps = ((p_fill - p_twap) / p_twap * 10000.0) if p_twap > 0 else 0.0

            results.append({
                "asset": fill.asset,
                "fill_price": p_fill,
                "arrival_price": p_arr,
                "vs_arrival_bps": round(vs_arr_bps, 2),
                "vs_vwap_bps": round(vs_vwap_bps, 2),
                "vs_twap_bps": round(vs_twap_bps, 2)
            })

        avg_vs_arr = sum(r["vs_arrival_bps"] for r in results) / len(results) if results else 0.0

        return {
            "avg_vs_arrival_bps": round(avg_vs_arr, 2),
            "benchmark_details": results
        }
