"""
Population Stability Index (PSI) calculation engine.
"""

import numpy as np
import pandas as pd
from typing import Tuple


def calculate_psi(
    baseline: np.ndarray,
    target: np.ndarray,
    num_bins: int = 10,
    epsilon: float = 1e-4,
) -> float:
    """Calculates the Population Stability Index (PSI) between baseline and target distributions."""
    baseline = np.asarray(baseline, dtype=float)
    target = np.asarray(target, dtype=float)

    # Filter out NaNs
    baseline = baseline[~np.isnan(baseline)]
    target = target[~np.isnan(target)]

    if len(baseline) == 0 or len(target) == 0:
        return 0.0

    if np.all(baseline == baseline[0]) and np.all(target == target[0]):
        return 0.0 if baseline[0] == target[0] else 1.0

    # Determine quantile bin edges based on baseline
    percentiles = np.linspace(0, 100, num_bins + 1)
    bin_edges = np.percentile(baseline, percentiles)

    # Ensure unique bin edges
    bin_edges = np.unique(bin_edges)
    if len(bin_edges) <= 1:
        bin_edges = np.linspace(np.min(baseline) - 1e-5, np.max(baseline) + 1e-5, num_bins + 1)

    # Compute histogram frequencies
    baseline_counts, _ = np.histogram(baseline, bins=bin_edges)
    target_counts, _ = np.histogram(target, bins=bin_edges)

    # Convert to proportions with epsilon smoothing
    baseline_pct = (baseline_counts + epsilon) / (len(baseline) + epsilon * len(baseline_counts))
    target_pct = (target_counts + epsilon) / (len(target) + epsilon * len(target_counts))

    # Calculate PSI
    psi_val = np.sum((target_pct - baseline_pct) * np.log(target_pct / baseline_pct))
    return float(psi_val)
