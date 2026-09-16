"""
Feature Cache Manager for Reusing Precomputed Quantitative Features.
"""

from pathlib import Path
import pandas as pd
import hashlib
import json
from typing import Dict, Any, Optional


class FeatureCache:
    """Disk-backed Feature Cache keyed by Feature, Symbol, Date Range, and Versions."""

    def __init__(self, cache_dir: str = "artifacts/feature_cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _generate_key(self, feature_id: str, symbol: str, start_date: str, end_date: str, version: str) -> str:
        raw = f"{feature_id}_{symbol}_{start_date}_{end_date}_{version}"
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]

    def get(self, feature_id: str, symbol: str, start_date: str, end_date: str, version: str = "1.0.0") -> Optional[pd.DataFrame]:
        key = self._generate_key(feature_id, symbol, start_date, end_date, version)
        filepath = self.cache_dir / f"feat_{key}.parquet"
        if filepath.exists():
            try:
                return pd.read_parquet(filepath)
            except Exception:
                pass
        return None

    def put(self, df: pd.DataFrame, feature_id: str, symbol: str, start_date: str, end_date: str, version: str = "1.0.0") -> str:
        key = self._generate_key(feature_id, symbol, start_date, end_date, version)
        filepath = self.cache_dir / f"feat_{key}.parquet"
        df.to_parquet(filepath, index=False)
        return str(filepath)
