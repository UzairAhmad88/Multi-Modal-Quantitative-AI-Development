"""
Label Horizon Purger Engine for Walk-Forward OS.
Purges training samples whose label prediction horizon overlaps validation/test evaluation periods.
"""

from typing import Tuple, List, Dict, Any
import numpy as np
import pandas as pd


class LabelHorizonPurger:
    """Removes training observations overlapping future label evaluation windows."""

    @staticmethod
    def purge_train_indices(
        train_indices: List[int],
        evaluation_start_idx: int,
        label_horizon_steps: int = 5,
    ) -> Tuple[List[int], int]:
        """Purges any training index t where t + label_horizon_steps > evaluation_start_idx."""
        purged = []
        purged_count = 0

        for idx in train_indices:
            if idx + label_horizon_steps >= evaluation_start_idx:
                purged_count += 1
            else:
                purged.append(idx)

        return purged, purged_count
