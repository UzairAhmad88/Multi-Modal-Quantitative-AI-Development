"""
Purged Time-Series Splitter for Walk-Forward OS.
Implements Marcos López de Prado's Purged & Embargoed Cross-Validation.
"""

from typing import Dict, Any, List, Tuple, Optional
import numpy as np
import pandas as pd
from validation.purged.purge import LabelHorizonPurger
from validation.purged.embargo import EmbargoExcluder


class PurgedTimeSeriesSplitter:
    """Splits financial time series into train, validation, and test folds with strict purging and embargo."""

    @staticmethod
    def split(
        df: pd.DataFrame,
        n_splits: int = 5,
        val_ratio: float = 0.15,
        test_ratio: float = 0.15,
        label_horizon_steps: int = 5,
        embargo_steps: int = 5,
    ) -> Dict[str, Any]:
        n = len(df)
        indices = np.arange(n)
        folds = []

        fold_size = n // n_splits

        for i in range(n_splits):
            test_start = i * fold_size
            test_end = min(n, (i + 1) * fold_size)

            val_start = max(0, test_start - int(n * val_ratio))
            val_end = test_start

            # Candidate train indices are all indices outside [val_start, test_end]
            raw_train_indices = [idx for idx in range(n) if idx < val_start or idx >= test_end + embargo_steps]

            # Purge train indices prior to val_start
            purged_train_indices, purged_count = LabelHorizonPurger.purge_train_indices(
                raw_train_indices,
                evaluation_start_idx=val_start if val_start > 0 else test_start,
                label_horizon_steps=label_horizon_steps,
            )

            # Embargo train indices post test_end
            final_train_indices, embargoed_count = EmbargoExcluder.apply_embargo(
                purged_train_indices,
                evaluation_end_idx=test_end,
                embargo_steps=embargo_steps,
            )

            val_indices = list(range(val_start, val_end))
            test_indices = list(range(test_start, test_end))

            folds.append({
                "fold": i + 1,
                "train_samples": len(final_train_indices),
                "val_samples": len(val_indices),
                "test_samples": len(test_indices),
                "purged_count": purged_count,
                "embargoed_count": embargoed_count,
                "train_indices": final_train_indices,
                "val_indices": val_indices,
                "test_indices": test_indices,
            })

        return {
            "status": "PASSED",
            "n_splits": n_splits,
            "total_observations": n,
            "label_horizon_steps": label_horizon_steps,
            "embargo_steps": embargo_steps,
            "folds": folds,
        }
