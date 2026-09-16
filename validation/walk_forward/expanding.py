"""
Expanding Window Walk-Forward Fold Generator for Walk-Forward OS.
Training set grows monotonically while validation/test windows move forward in time.
"""

from typing import List, Dict, Any, Optional
import pandas as pd
from validation.temporal.windows import ValidationWindow


class ExpandingWindowGenerator:
    """Generates expanding-window walk-forward fold definitions."""

    @staticmethod
    def generate_folds(
        df: pd.DataFrame,
        initial_train_size: int = 250,
        val_size: int = 50,
        test_size: int = 50,
        step_size: int = 50,
        purge_period: int = 5,
        embargo_period: int = 5,
        timestamp_col: str = "timestamp",
    ) -> List[ValidationWindow]:
        n = len(df)
        folds: List[ValidationWindow] = []
        current_train_end = initial_train_size
        fold_idx = 1

        while current_train_end + purge_period + val_size + embargo_period + test_size <= n:
            train_start = 0
            train_end = current_train_end

            val_start = train_end + purge_period
            val_end = val_start + val_size

            test_start = val_end + embargo_period
            test_end = test_start + test_size

            # Extract timestamps if available
            t_train_s = str(df.iloc[train_start][timestamp_col]) if timestamp_col in df.columns else str(train_start)
            t_train_e = str(df.iloc[train_end - 1][timestamp_col]) if timestamp_col in df.columns else str(train_end)
            t_val_s = str(df.iloc[val_start][timestamp_col]) if timestamp_col in df.columns else str(val_start)
            t_val_e = str(df.iloc[val_end - 1][timestamp_col]) if timestamp_col in df.columns else str(val_end)
            t_test_s = str(df.iloc[test_start][timestamp_col]) if timestamp_col in df.columns else str(test_start)
            t_test_e = str(df.iloc[min(n - 1, test_end - 1)][timestamp_col]) if timestamp_col in df.columns else str(test_end)

            w = ValidationWindow(
                window_id=f"FOLD-EXP-{fold_idx:03d}",
                fold_index=fold_idx,
                train_start=t_train_s,
                train_end=t_train_e,
                validation_start=t_val_s,
                validation_end=t_val_e,
                test_start=t_test_s,
                test_end=t_test_e,
                purge_period=purge_period,
                embargo_period=embargo_period,
                train_samples=train_end - train_start,
                val_samples=val_end - val_start,
                test_samples=test_end - test_start,
                purged_samples=purge_period,
                embargoed_samples=embargo_period,
            )
            folds.append(w)

            current_train_end += step_size
            fold_idx += 1

        return folds
