"""
Embargo Period Excluder for Walk-Forward OS.
Excludes training samples following test/validation periods to prevent serial correlation leakage.
"""

from typing import Tuple, List, Dict, Any
import numpy as np
import pandas as pd


class EmbargoExcluder:
    """Applies embargo period exclusions following validation or test evaluation bounds."""

    @staticmethod
    def apply_embargo(
        candidate_indices: List[int],
        evaluation_end_idx: int,
        embargo_steps: int = 5,
    ) -> Tuple[List[int], int]:
        """Excludes indices in [evaluation_end_idx, evaluation_end_idx + embargo_steps)."""
        embargo_cutoff = evaluation_end_idx + embargo_steps
        filtered = []
        embargoed_count = 0

        for idx in candidate_indices:
            if evaluation_end_idx <= idx < embargo_cutoff:
                embargoed_count += 1
            else:
                filtered.append(idx)

        return filtered, embargoed_count
