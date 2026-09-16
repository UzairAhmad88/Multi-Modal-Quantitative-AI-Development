"""
Dataset Builder for Constructing Versioned Multi-Modal Quantitative Datasets.
"""

from pathlib import Path
import pandas as pd
import numpy as np
import hashlib
import json
import datetime
from typing import Dict, Any, List, Optional, Tuple

from data_platform.features.feature_engine import FeatureEngine
from data_platform.versioning.snapshot_manager import SnapshotManager
from data_platform.lineage.lineage_tracer import DataLineageTracer


class DatasetBuilder:
    """Constructs versioned, point-in-time aligned, hash-verified datasets for training and backtesting."""

    def __init__(self, datasets_dir: str = "data/datasets"):
        self.datasets_dir = Path(datasets_dir)
        self.datasets_dir.mkdir(parents=True, exist_ok=True)
        self.feat_engine = FeatureEngine()
        self.snapshot_mgr = SnapshotManager()
        self.lineage_tracer = DataLineageTracer()

    def build_dataset(
        self,
        market_df: pd.DataFrame,
        news_df: Optional[pd.DataFrame] = None,
        fund_df: Optional[pd.DataFrame] = None,
        config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Builds versioned dataset from market, news, and fundamentals."""
        config = config or {}
        dataset_name = config.get("name", "multimodal_dataset")
        target_horizon = config.get("target_horizon", 5)

        # 1. Feature computation
        df = self.feat_engine.compute_features(market_df, news_df, fund_df)

        if df.empty:
            return {"status": "FAILED", "reason": "Empty dataset produced"}

        # 2. Target generation: forward return over horizon
        if "close" in df.columns:
            df["target_return"] = df.groupby("symbol")["close"].pct_change(target_horizon).shift(-target_horizon)
            df["target_direction"] = (df["target_return"] > 0).astype(int)

        df = df.dropna(subset=["target_return"]).reset_index(drop=True)

        # 3. ID and Metadata
        date_str = datetime.datetime.utcnow().strftime("%Y%m%d")
        rand_hex = hashlib.md5(f"{dataset_name}_{len(df)}".encode("utf-8")).hexdigest()[:4].upper()
        dataset_id = f"DATASET-{date_str}-{rand_hex}"

        # 4. Save to Disk
        file_path = self.datasets_dir / f"{dataset_id}.parquet"
        meta_path = self.datasets_dir / f"{dataset_id}_meta.json"

        df.to_parquet(file_path, index=False)

        # Hash payload
        content_hash = hashlib.sha256(df.to_json(orient="records").encode("utf-8")).hexdigest()

        meta = {
            "dataset_id": dataset_id,
            "name": dataset_name,
            "version": "1.0.0",
            "rows": len(df),
            "columns": len(df.columns),
            "symbols": list(df["symbol"].unique()) if "symbol" in df.columns else [],
            "date_start": str(df["date"].min()) if "date" in df.columns else "",
            "date_end": str(df["date"].max()) if "date" in df.columns else "",
            "hash": content_hash,
            "file_path": str(file_path),
            "created_at": datetime.datetime.utcnow().isoformat(),
            "config": config
        }

        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(meta, f, indent=2)

        # Create Snapshot
        snap_meta = self.snapshot_mgr.create_snapshot(df, dataset_id, meta)

        # Record Lineage
        self.lineage_tracer.record_node(dataset_id, "DATASET", meta)
        for sym in meta["symbols"]:
            self.lineage_tracer.record_node(f"RAW_{sym}", "RAW_MARKET", {"symbol": sym})
            self.lineage_tracer.record_edge(f"RAW_{sym}", dataset_id, "CONSTRUCTED_FROM")

        return {
            "status": "SUCCESS",
            "dataset_id": dataset_id,
            "rows": len(df),
            "columns": len(df.columns),
            "hash": content_hash,
            "snapshot_id": snap_meta["snapshot_id"],
            "file_path": str(file_path),
            "meta": meta
        }

    def split_dataset(self, df: pd.DataFrame, train_ratio: float = 0.7, val_ratio: float = 0.15) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """Performs temporal splitting strictly preserving date ordering."""
        if df.empty or "date" not in df.columns:
            return df, pd.DataFrame(), pd.DataFrame()

        df_sorted = df.sort_values(by="date").reset_index(drop=True)
        n = len(df_sorted)
        train_end = int(n * train_ratio)
        val_end = int(n * (train_ratio + val_ratio))

        train_df = df_sorted.iloc[:train_end]
        val_df = df_sorted.iloc[train_end:val_end]
        test_df = df_sorted.iloc[val_end:]

        return train_df, val_df, test_df
