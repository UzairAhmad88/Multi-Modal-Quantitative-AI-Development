"""
Raw Data Storage Manager for Immutable Payload Persistence.
"""

from pathlib import Path
import pandas as pd
import datetime
from typing import Dict, Any, Optional


class RawDataStore:
    """Manages immutable raw data storage by source category."""

    def __init__(self, raw_dir: str = "data/raw"):
        self.raw_dir = Path(raw_dir)
        self.raw_dir.mkdir(parents=True, exist_ok=True)

    def save_raw(self, df: pd.DataFrame, source: str) -> str:
        """Saves raw data payload under timestamped file."""
        sub_dir = self.raw_dir / source
        sub_dir.mkdir(parents=True, exist_ok=True)
        ts_str = datetime.datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filepath = sub_dir / f"{source}_raw_{ts_str}.csv"
        df.to_csv(filepath, index=False)
        return str(filepath)

    def load_latest_raw(self, source: str) -> pd.DataFrame:
        """Loads latest raw dataset for specified source."""
        sub_dir = self.raw_dir / source
        if not sub_dir.exists():
            return pd.DataFrame()
        files = list(sub_dir.glob("*.csv"))
        if not files:
            return pd.DataFrame()
        files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        return pd.read_csv(files[0])
