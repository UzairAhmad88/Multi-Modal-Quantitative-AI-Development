"""
Feature Registry & Lineage Module
Registers quantitative features across groups (technical, momentum, volatility, sentiment, fundamental, macro)
and documents lineage from raw data transformations.
"""

from datetime import datetime, timezone
from typing import Dict, List, Any, Optional


class FeatureRegistry:
    """Quantitative Feature Definition & Lineage Registry."""

    def __init__(self):
        self.features: Dict[str, Dict[str, Any]] = {}

    def register_feature(
        self,
        feature_name: str,
        feature_group: str = "technical",
        definition: str = "Quantitative feature transformation",
        formula: str = "x_t",
        source_column: Optional[str] = None,
        source: Optional[str] = None,
        lookback_window: int = 1,
        version: str = "v1.0.0",
    ) -> Dict[str, Any]:
        """
        Register a quantitative feature definition and its transformation lineage.
        """
        src_col = source or source_column or "close"
        feature_id = f"FEAT-{feature_name.upper()}-{version}"
        feature_record = {
            "feature_id": feature_id,
            "feature_name": feature_name,
            "feature_group": feature_group,
            "definition": definition,
            "formula": formula,
            "source": src_col,
            "source_column": src_col,
            "lookback_window": lookback_window,
            "version": version,
            "lineage": {
                "raw_data": src_col,
                "transformation": formula,
                "feature": feature_name,
                "pipeline": f"{src_col} -> [{formula}] -> {feature_name}"
            },
            "registered_at": datetime.now(timezone.utc).isoformat(),
        }
        self.features[feature_id] = feature_record
        self.features[feature_name] = feature_record
        return feature_record

    def list_features(self) -> List[Dict[str, Any]]:
        unique_feats = {}
        for f in self.features.values():
            unique_feats[f["feature_id"]] = f
        return list(unique_feats.values())

    def get_feature(self, feature_id_or_name: str) -> Optional[Dict[str, Any]]:
        return self.features.get(feature_id_or_name)

    def get_features_by_group(self, feature_group: str) -> List[Dict[str, Any]]:
        """Filter feature definitions by group."""
        return [f for f in self.features.values() if f["feature_group"].lower() == feature_group.lower()]
