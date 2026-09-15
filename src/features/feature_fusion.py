from __future__ import annotations
import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any
import pandas as pd
import numpy as np
from src.utils.logger import get_logger
from src.utils.paths import DATA_DIR
from src.data.data_synchronizer import align_modalities
from src.features.technical import add_technical_features
from src.features.sentiment_features import aggregate_daily_sentiment, add_rolling_sentiment_features
from src.features.fundamental_features import build_fundamental_features
from src.features.price_features import add_target_features

logger = get_logger("feature_fusion")


class FeatureValidator:
    """Validates completeness, absence of invalid NaNs in features, and target integrity."""

    @staticmethod
    def validate(df: pd.DataFrame, feature_cols: List[str], target_col: str = "target_return") -> bool:
        if df.empty:
            raise ValueError("Feature dataset is empty.")
        if target_col not in df.columns:
            raise ValueError(f"Target column '{target_col}' missing from dataset.")

        missing_feats = [c for c in feature_cols if c not in df.columns]
        if missing_feats:
            raise ValueError(f"Feature dataset missing expected features: {missing_feats}")

        return True


class FeatureManifest:
    """Metadata manifest recording feature dataset versioning and creation details."""

    @staticmethod
    def create(
        dataset_name: str,
        feature_cols: List[str],
        target_col: str,
        num_rows: int,
        universe: List[str],
        version: str = "v1.0"
    ) -> Dict[str, Any]:
        return {
            "manifest_id": str(uuid.uuid4())[:8],
            "dataset_name": dataset_name,
            "version": version,
            "created_at": datetime.utcnow().isoformat(),
            "num_rows": num_rows,
            "num_features": len(feature_cols),
            "feature_names": feature_cols,
            "target_column": target_col,
            "universe": universe
        }


class FeatureBuilder:
    """Orchestrates end-to-end multi-modal feature engineering, temporal fusion, and target creation."""

    def __init__(self, output_dir: Path | None = None):
        self.output_dir = output_dir or (DATA_DIR / "features")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def build_dataset(
        self,
        market_df: pd.DataFrame,
        news_df: pd.DataFrame | None = None,
        fundamentals_df: pd.DataFrame | None = None,
        horizon_days: int = 5,
        version: str = "v1.0"
    ) -> tuple[pd.DataFrame, Dict[str, Any]]:
        logger.info("Building multi-modal features...")

        # 1. Technical Market Features
        market_feats = add_technical_features(market_df)

        # 2. News NLP & Sentiment Features
        daily_sentiment = None
        if news_df is not None and not news_df.empty:
            agg_sentiment = aggregate_daily_sentiment(news_df)
            daily_sentiment = add_rolling_sentiment_features(agg_sentiment)

        # 3. Fundamental Features & Ratios
        fund_feats = None
        if fundamentals_df is not None and not fundamentals_df.empty:
            fund_feats = build_fundamental_features(fundamentals_df, market_df)

        # 4. Temporal Alignment (Asof Backward Join)
        fused = align_modalities(market_feats, daily_sentiment, fund_feats, on_col="date")

        # 5. Target Engineering
        fused_with_targets = add_target_features(fused, horizon_days=horizon_days)

        # Exclude non-feature identifier and datetime metadata columns
        exclude_cols = {
            "date", "ticker", "target_return", "target_class",
            f"target_return_{horizon_days}d", "available_date", "public_release_date",
            "quarter_end_date", "headline", "url", "source", "article_text", "article_id"
        }

        # Ensure feature columns contain strictly numeric dtypes (float/int)
        numeric_cols = set(fused_with_targets.select_dtypes(include=[np.number]).columns)
        feature_cols = [c for c in fused_with_targets.columns if c in numeric_cols and c not in exclude_cols]

        # Clean remaining NaNs in numeric features
        fused_with_targets[feature_cols] = fused_with_targets[feature_cols].ffill().bfill().fillna(0.0)

        # Validation
        FeatureValidator.validate(fused_with_targets, feature_cols, "target_return")

        universe = list(fused_with_targets["ticker"].unique())
        manifest = FeatureManifest.create(
            dataset_name="multi_modal_features",
            feature_cols=feature_cols,
            target_col="target_return",
            num_rows=len(fused_with_targets),
            universe=universe,
            version=version
        )

        # Save dataset (convert object columns to string for parquet compatibility)
        for col in fused_with_targets.select_dtypes(include=['object']).columns:
            fused_with_targets[col] = fused_with_targets[col].astype(str)

        parquet_path = self.output_dir / "features_dataset.parquet"
        manifest_path = self.output_dir / "features_manifest.json"

        try:
            fused_with_targets.to_parquet(parquet_path, index=False)
        except Exception:
            fused_with_targets.to_csv(self.output_dir / "features_dataset.csv", index=False)

        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2)

        logger.info(f"Successfully built feature dataset with {len(fused_with_targets)} rows and {len(feature_cols)} features.")
        return fused_with_targets, manifest
