"""
Dataset Snapshot Manager for Creating Immutable Reproducible Dataset Snapshots.
"""

from pathlib import Path
import pandas as pd
import json
import hashlib
import datetime
from typing import Dict, Any, Optional


class SnapshotManager:
    """Manages immutable dataset snapshots and reproduction metadata."""

    def __init__(self, snapshots_dir: str = "data/snapshots"):
        self.snapshots_dir = Path(snapshots_dir)
        self.snapshots_dir.mkdir(parents=True, exist_ok=True)

    def create_snapshot(self, df: pd.DataFrame, dataset_id: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Creates an immutable parquet snapshot with hash signature."""
        ts_str = datetime.datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        snap_id = f"SNAP-{dataset_id}-{ts_str}"

        # Hash payload
        content_bytes = df.to_json(orient="records").encode("utf-8")
        data_hash = hashlib.sha256(content_bytes).hexdigest()

        file_path = self.snapshots_dir / f"{snap_id}.parquet"
        meta_path = self.snapshots_dir / f"{snap_id}_meta.json"

        df.to_parquet(file_path, index=False)

        snap_meta = {
            "snapshot_id": snap_id,
            "dataset_id": dataset_id,
            "rows": len(df),
            "cols": len(df.columns),
            "sha256_hash": data_hash,
            "file_path": str(file_path),
            "created_at": datetime.datetime.utcnow().isoformat(),
            "user_metadata": metadata
        }

        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(snap_meta, f, indent=2)

        return snap_meta

    def restore_snapshot(self, snapshot_id: str) -> Optional[pd.DataFrame]:
        file_path = self.snapshots_dir / f"{snapshot_id}.parquet"
        if file_path.exists():
            return pd.read_parquet(file_path)
        return None
