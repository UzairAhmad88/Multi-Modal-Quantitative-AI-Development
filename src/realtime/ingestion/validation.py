"""
Real-Time Data Quality & Staleness Validation Engine
Audits incoming tick and bar records for staleness, gaps, duplicates, and feed health.
"""

from datetime import datetime, timezone
from typing import Dict, List, Any, Optional, Set
import pandas as pd


class DataValidator:
    """Quantitative Real-Time Data Quality Validator."""

    def __init__(self, max_staleness_sec: float = 300.0):
        self.max_staleness_sec = max_staleness_sec
        self.seen_records: Set[str] = set()

    def validate_record(self, record: Dict[str, Any], current_time: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Audit a single data record for timestamp staleness, missing fields, and duplication.
        """
        now = current_time or datetime.now(timezone.utc)
        symbol = record.get("symbol", record.get("ticker", "UNKNOWN"))
        ts_str = record.get("timestamp", record.get("date"))

        # 1. Check duplicate
        record_key = f"{symbol}_{ts_str}_{record.get('close', 0.0)}"
        if record_key in self.seen_records:
            return {
                "status": "DUPLICATE",
                "is_valid": False,
                "reason": f"Duplicate record detected for {symbol} at {ts_str}"
            }
        self.seen_records.add(record_key)

        # 2. Check timestamp staleness
        if ts_str:
            try:
                rec_dt = pd.to_datetime(ts_str)
                if rec_dt.tzinfo is None:
                    rec_dt = rec_dt.tz_localize("UTC")
                diff_sec = (now - rec_dt).total_seconds()
                if diff_sec > self.max_staleness_sec:
                    return {
                        "status": "STALE",
                        "is_valid": False,
                        "staleness_sec": diff_sec,
                        "reason": f"Data timestamp is stale by {diff_sec:.1f} seconds (> {self.max_staleness_sec}s allowed)"
                    }
            except Exception:
                pass

        # 3. Check missing key price fields
        missing_keys = [k for k in ["close", "volume"] if k not in record or record[k] is None]
        if missing_keys:
            return {
                "status": "FAILED",
                "is_valid": False,
                "reason": f"Missing critical market fields: {missing_keys}"
            }

        return {
            "status": "HEALTHY",
            "is_valid": True,
            "reason": "Record passed validation checks"
        }

    def detect_gaps(self, df: pd.DataFrame, expected_freq_sec: float = 60.0) -> List[Dict[str, Any]]:
        """Detect gaps in real-time bar sequences."""
        gaps = []
        if "timestamp" not in df.columns or len(df) < 2:
            return gaps

        df_sorted = df.sort_values("timestamp")
        diffs = df_sorted["timestamp"].diff().dt.total_seconds()
        gap_rows = df_sorted[diffs > expected_freq_sec * 1.5]

        for idx, row in gap_rows.iterrows():
            gaps.append({
                "symbol": row.get("symbol", "UNKNOWN"),
                "timestamp": str(row["timestamp"]),
                "gap_sec": float(diffs.loc[idx])
            })
        return gaps
