"""
Timing Analytics: Analyzes latency breakdown from signal to fill completion.
"""

from typing import List, Dict, Any
import numpy as np
from execution.fills.fill_engine import Fill


class TimingAnalytics:
    """Analyzes execution timing and latency breakdown."""

    def analyze_timing(self, fills: List[Fill]) -> Dict[str, Any]:
        """Calculates latency statistics across fills."""
        if not fills:
            return {"mean_latency_ms": 0.0, "max_latency_ms": 0.0}

        latencies = [f.execution_latency_ms for f in fills]
        return {
            "mean_latency_ms": round(float(np.mean(latencies)), 2),
            "median_latency_ms": round(float(np.median(latencies)), 2),
            "max_latency_ms": round(float(np.max(latencies)), 2),
            "min_latency_ms": round(float(np.min(latencies)), 2)
        }
