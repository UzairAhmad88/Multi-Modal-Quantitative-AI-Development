from __future__ import annotations
from typing import Dict, List, Any
import pandas as pd
import numpy as np
from src.utils.logger import get_logger

logger = get_logger("walk_forward")


class WalkForwardEvaluator:
    """Performs rolling walk-forward validation without data leakage."""

    def __init__(self, train_window_days: int = 504, test_window_days: int = 126):
        self.train_window_days = train_window_days
        self.test_window_days = test_window_days

    def generate_windows(self, dates: List[pd.Timestamp]) -> List[Dict[str, Any]]:
        windows = []
        n = len(dates)
        start_idx = 0
        step = self.test_window_days

        while start_idx + self.train_window_days + self.test_window_days <= n:
            tr_start = dates[start_idx]
            tr_end = dates[start_idx + self.train_window_days - 1]
            te_start = dates[start_idx + self.train_window_days]
            te_end = dates[min(n - 1, start_idx + self.train_window_days + self.test_window_days - 1)]

            windows.append({
                "window_index": len(windows) + 1,
                "train_start": tr_start,
                "train_end": tr_end,
                "test_start": te_start,
                "test_end": te_end
            })

            start_idx += step

        return windows
