"""
Feature Store Registry for Cataloging Features, Formulas, Versions, Dependencies, and Lineage.
"""

import json
from pathlib import Path
from typing import Dict, Any, List, Optional
import datetime


class FeatureStoreRegistry:
    """Persistent Registry for Quantitative Features and Feature Sets."""

    def __init__(self, registry_file: str = "artifacts/feature_store_registry.json"):
        self.registry_path = Path(registry_file)
        self.registry_path.parent.mkdir(parents=True, exist_ok=True)
        self._data: Dict[str, Any] = self._load()

    def _load(self) -> Dict[str, Any]:
        if self.registry_path.exists():
            try:
                with open(self.registry_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {
            "features": {
                "RSI_14": {
                    "id": "RSI_14",
                    "name": "Relative Strength Index (14)",
                    "version": "1.0.0",
                    "category": "technical",
                    "formula": "100 - (100 / (1 + RS))",
                    "dependencies": ["close"],
                    "created_at": datetime.datetime.utcnow().isoformat()
                },
                "Volatility_20": {
                    "id": "Volatility_20",
                    "name": "Rolling Volatility (20D)",
                    "version": "1.0.0",
                    "category": "volatility",
                    "formula": "std(returns, 20)",
                    "dependencies": ["close"],
                    "created_at": datetime.datetime.utcnow().isoformat()
                },
                "News_Sentiment_7D": {
                    "id": "News_Sentiment_7D",
                    "name": "News Sentiment Mean (7D)",
                    "version": "1.0.0",
                    "category": "sentiment",
                    "formula": "mean(finbert_sentiment, 7)",
                    "dependencies": ["headline", "published_at"],
                    "created_at": datetime.datetime.utcnow().isoformat()
                },
                "PE_Ratio": {
                    "id": "PE_Ratio",
                    "name": "Price to Earnings Ratio",
                    "version": "1.0.0",
                    "category": "fundamental",
                    "formula": "close / eps",
                    "dependencies": ["eps", "announcement_date"],
                    "created_at": datetime.datetime.utcnow().isoformat()
                }
            },
            "feature_sets": {
                "technical_v1": ["RSI_14", "Volatility_20"],
                "multimodal_v1": ["RSI_14", "Volatility_20", "News_Sentiment_7D", "PE_Ratio"]
            }
        }

    def _save(self) -> None:
        with open(self.registry_path, "w", encoding="utf-8") as f:
            json.dump(self._data, f, indent=2)

    def register_feature(self, feature_id: str, name: str, category: str, formula: str, dependencies: List[str], version: str = "1.0.0") -> Dict[str, Any]:
        entry = {
            "id": feature_id,
            "name": name,
            "version": version,
            "category": category,
            "formula": formula,
            "dependencies": dependencies,
            "created_at": datetime.datetime.utcnow().isoformat()
        }
        self._data["features"][feature_id] = entry
        self._save()
        return entry

    def get_feature(self, feature_id: str) -> Optional[Dict[str, Any]]:
        return self._data["features"].get(feature_id)

    def list_features(self) -> List[Dict[str, Any]]:
        return list(self._data["features"].values())

    def get_feature_set(self, set_name: str) -> List[str]:
        return self._data["feature_sets"].get(set_name, [])
