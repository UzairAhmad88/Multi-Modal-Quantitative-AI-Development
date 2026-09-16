"""
Kolmogorov-Smirnov 2-sample statistical test.
"""

import numpy as np
from scipy import stats
from typing import Tuple


def calculate_ks_test(
    baseline: np.ndarray,
    target: np.ndarray,
) -> Tuple[float, float]:
    """Calculates 2-sample Kolmogorov-Smirnov statistic and p-value."""
    baseline = np.asarray(baseline, dtype=float)
    target = np.asarray(target, dtype=float)

    baseline = baseline[~np.isnan(baseline)]
    target = target[~np.isnan(target)]

    if len(baseline) == 0 or len(target) == 0:
        return 0.0, 1.0

    res = stats.ks_2samp(baseline, target)
    return float(res.statistic), float(res.pvalue)
