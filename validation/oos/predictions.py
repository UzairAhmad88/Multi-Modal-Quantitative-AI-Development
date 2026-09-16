"""
Out-of-Sample Prediction Store & Signal Converter for Walk-Forward OS.
Stores out-of-sample predictions generated strictly without future information and passes them downstream.
"""

from typing import Dict, Any, List, Optional
import os
import json
import pandas as pd
import numpy as np


class OOSPredictionStore:
    """Manages out-of-sample prediction storage and downstream signal pipeline conversion."""

    def __init__(self, storage_dir: str = "artifacts/validation/predictions"):
        self.storage_dir = storage_dir
        os.makedirs(self.storage_dir, exist_ok=True)

    def save_predictions(
        self,
        experiment_id: str,
        predictions_df: pd.DataFrame,
        fold_id: str = "OOS-COMBINED",
    ) -> str:
        """Saves out-of-sample predictions DataFrame to JSON/Parquet artifact."""
        filepath = os.path.join(self.storage_dir, f"{experiment_id}_{fold_id}.json")
        records = predictions_df.to_dict(orient="records")
        with open(filepath, "w") as f:
            json.dump({
                "experiment_id": experiment_id,
                "fold_id": fold_id,
                "count": len(records),
                "predictions": records,
            }, f, indent=2)
        return filepath

    def load_predictions(self, experiment_id: str, fold_id: str = "OOS-COMBINED") -> Optional[pd.DataFrame]:
        """Loads out-of-sample predictions for downstream processing."""
        filepath = os.path.join(self.storage_dir, f"{experiment_id}_{fold_id}.json")
        if not os.path.exists(filepath):
            return None
        with open(filepath, "r") as f:
            data = json.load(f)
        return pd.DataFrame(data["predictions"])
