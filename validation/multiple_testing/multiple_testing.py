"""
Multiple Testing Correction Engine (Bonferroni, Holm, Benjamini-Hochberg).
"""

import numpy as np
from typing import List, Dict, Any
from validation.schemas.validation_schema import MultipleTestingResult


class MultipleTestingCorrector:
    """
    Applies multiple testing adjustments to raw p-values to control Family-Wise Error Rate (FWER) or False Discovery Rate (FDR).
    """

    @staticmethod
    def bonferroni(p_values: List[float], alpha: float = 0.05) -> MultipleTestingResult:
        m = len(p_values)
        if m == 0:
            return MultipleTestingResult(
                method="Bonferroni",
                number_of_tests=0,
                raw_p_values=[],
                adjusted_p_values=[],
                rejected_nulls=[],
            )

        adj_p = [min(1.0, float(p * m)) for p in p_values]
        rejected = [bool(p < alpha) for p in adj_p]

        return MultipleTestingResult(
            method="Bonferroni",
            number_of_tests=m,
            raw_p_values=[round(p, 6) for p in p_values],
            adjusted_p_values=[round(p, 6) for p in adj_p],
            rejected_nulls=rejected,
        )

    @staticmethod
    def holm(p_values: List[float], alpha: float = 0.05) -> MultipleTestingResult:
        m = len(p_values)
        if m == 0:
            return MultipleTestingResult(
                method="Holm-Bonferroni",
                number_of_tests=0,
                raw_p_values=[],
                adjusted_p_values=[],
                rejected_nulls=[],
            )

        sorted_indices = np.argsort(p_values)
        sorted_p = [p_values[i] for i in sorted_indices]

        adj_p_sorted = []
        for i, p in enumerate(sorted_p):
            k = m - i
            adj_p_sorted.append(min(1.0, float(p * k)))

        # Enforce monotonicity
        for i in range(1, m):
            adj_p_sorted[i] = max(adj_p_sorted[i], adj_p_sorted[i - 1])

        # Restore original order
        adj_p = [0.0] * m
        for orig_idx, sorted_idx in enumerate(sorted_indices):
            adj_p[sorted_idx] = adj_p_sorted[orig_idx]

        rejected = [bool(p < alpha) for p in adj_p]

        return MultipleTestingResult(
            method="Holm-Bonferroni",
            number_of_tests=m,
            raw_p_values=[round(p, 6) for p in p_values],
            adjusted_p_values=[round(p, 6) for p in adj_p],
            rejected_nulls=rejected,
        )

    @staticmethod
    def benjamini_hochberg(p_values: List[float], alpha: float = 0.05) -> MultipleTestingResult:
        m = len(p_values)
        if m == 0:
            return MultipleTestingResult(
                method="Benjamini-Hochberg (FDR)",
                number_of_tests=0,
                raw_p_values=[],
                adjusted_p_values=[],
                rejected_nulls=[],
            )

        sorted_indices = np.argsort(p_values)
        sorted_p = [p_values[i] for i in sorted_indices]

        adj_p_sorted = [0.0] * m
        for i in range(m - 1, -1, -1):
            rank = i + 1
            p_val = sorted_p[i]
            val = (p_val * m) / rank
            if i == m - 1:
                adj_p_sorted[i] = min(1.0, float(val))
            else:
                adj_p_sorted[i] = min(1.0, float(val), adj_p_sorted[i + 1])

        adj_p = [0.0] * m
        for orig_idx, sorted_idx in enumerate(sorted_indices):
            adj_p[sorted_idx] = adj_p_sorted[orig_idx]

        rejected = [bool(p < alpha) for p in adj_p]

        return MultipleTestingResult(
            method="Benjamini-Hochberg (FDR)",
            number_of_tests=m,
            raw_p_values=[round(p, 6) for p in p_values],
            adjusted_p_values=[round(p, 6) for p in adj_p],
            rejected_nulls=rejected,
        )
