"""
Autocorrelation Engine: ACF and PACF return autocorrelation analysis.
"""

import numpy as np
from typing import List, Dict, Any


class AutocorrelationAnalyzer:
    """Calculates return autocorrelation structure."""

    def compute_autocorrelation(self, returns: List[float], max_lag: int = 5) -> Dict[str, Any]:
        """Calculates autocorrelation coefficients up to max_lag."""
        rets = np.array(returns, dtype=float)
        if len(rets) < max_lag + 2:
            return {"acf": [1.0] + [0.0] * max_lag, "has_serial_correlation": False}

        mean = np.mean(rets)
        var = np.var(rets)
        if var < 1e-12:
            return {"acf": [1.0] + [0.0] * max_lag, "has_serial_correlation": False}

        n = len(rets)
        acf = [1.0]
        for lag in range(1, max_lag + 1):
            cov = np.sum((rets[:n - lag] - mean) * (rets[lag:] - mean)) / n
            acf.append(float(cov / var))

        has_serial = any(abs(r) > (2.0 / np.sqrt(n)) for r in acf[1:])
        return {
            "acf": [round(float(r), 4) for r in acf],
            "has_serial_correlation": bool(has_serial),
            "max_lag": max_lag
        }
