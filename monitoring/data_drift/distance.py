"""
Wasserstein and Jensen-Shannon continuous distance calculators.
"""

import numpy as np
from scipy import stats
from scipy.spatial import distance


def calculate_wasserstein_distance(
    baseline: np.ndarray,
    target: np.ndarray,
) -> float:
    """Calculates 1D Wasserstein (Earth Mover's) distance."""
    baseline = np.asarray(baseline, dtype=float)
    target = np.asarray(target, dtype=float)

    baseline = baseline[~np.isnan(baseline)]
    target = target[~np.isnan(target)]

    if len(baseline) == 0 or len(target) == 0:
        return 0.0

    return float(stats.wasserstein_distance(baseline, target))


def calculate_jensen_shannon_distance(
    baseline: np.ndarray,
    target: np.ndarray,
    num_bins: int = 20,
) -> float:
    """Calculates Jensen-Shannon distance between histograms of baseline and target."""
    baseline = np.asarray(baseline, dtype=float)
    target = np.asarray(target, dtype=float)

    baseline = baseline[~np.isnan(baseline)]
    target = target[~np.isnan(target)]

    if len(baseline) == 0 or len(target) == 0:
        return 0.0

    min_val = min(np.min(baseline), np.min(target))
    max_val = max(np.max(baseline), np.max(target))
    if min_val == max_val:
        return 0.0

    bins = np.linspace(min_val, max_val, num_bins + 1)
    p_hist, _ = np.histogram(baseline, bins=bins, density=True)
    q_hist, _ = np.histogram(target, bins=bins, density=True)

    # Normalize to probabilities
    p = p_hist / (np.sum(p_hist) + 1e-12)
    q = q_hist / (np.sum(q_hist) + 1e-12)

    return float(distance.jensenshannon(p, q))
