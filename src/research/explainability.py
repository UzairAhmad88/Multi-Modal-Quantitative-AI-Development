"""
Model Explainability Module
Provides tree feature importance, SHAP global/local explanations, and multimodal modality attribution.
"""

from typing import Dict, List, Any, Optional, Tuple
import numpy as np
import pandas as pd


class ModelExplainer:
    """Quantitative Model Explainability and Feature Attribution Engine."""

    def __init__(self, model: Any, feature_names: List[str]):
        """
        Initialize ModelExplainer.
        :param model: Trained ML model instance (XGBoost, RandomForest, or pipeline).
        :param feature_names: List of input feature names in exact order.
        """
        self.model = model
        self.feature_names = feature_names

    def get_feature_importance(self) -> Dict[str, float]:
        """Extract tree feature importance (Gini / Gain) normalized to sum to 1."""
        try:
            if hasattr(self.model, "feature_importances_"):
                importances = self.model.feature_importances_
            elif hasattr(self.model, "get_score"):
                scores = self.model.get_score(importance_type="gain")
                importances = np.array([scores.get(f, 0.0) for f in self.feature_names])
            else:
                # Fallback: Uniform equal importances
                importances = np.ones(len(self.feature_names)) / len(self.feature_names)

            total = np.sum(importances) + 1e-8
            normalized = importances / total

            return {feat: float(imp) for feat, imp in zip(self.feature_names, normalized)}
        except Exception:
            return {feat: 1.0 / len(self.feature_names) for feat in self.feature_names}

    def compute_shap_explanations(
        self, X: pd.DataFrame, num_samples: int = 100
    ) -> Dict[str, Any]:
        """
        Compute SHAP global importance and local attribution scores.
        Fallback to feature importances if SHAP package is unavailable.
        """
        X_sample = X.iloc[:num_samples] if len(X) > num_samples else X
        shap_available = False
        shap_values = None

        try:
            import shap
            shap_available = True
            explainer = shap.Explainer(self.model, X_sample)
            shap_output = explainer(X_sample)
            shap_values = shap_output.values
            if len(shap_values.shape) == 3:  # Multi-class or 2D output
                shap_values = shap_values[:, :, 1]
        except Exception:
            shap_available = False

        if not shap_available or shap_values is None:
            # Fallback SHAP estimation via feature importance * standardized values
            fi = self.get_feature_importance()
            weights = np.array([fi.get(f, 0.0) for f in self.feature_names])
            X_std = (X_sample[self.feature_names] - X_sample[self.feature_names].mean()) / (
                X_sample[self.feature_names].std() + 1e-8
            )
            shap_values = X_std.values * weights

        # Global importance: mean absolute SHAP value per feature
        global_importance = np.abs(shap_values).mean(axis=0)
        total_g = np.sum(global_importance) + 1e-8
        global_dict = {
            feat: float(val / total_g) for feat, val in zip(self.feature_names, global_importance)
        }

        # Local explanation for the latest/last row
        last_row_shap = shap_values[-1]
        local_contributions = [
            {"feature": feat, "shap_value": float(val), "direction": "positive" if val > 0 else "negative"}
            for feat, val in zip(self.feature_names, last_row_shap)
        ]
        local_contributions.sort(key=lambda x: abs(x["shap_value"]), reverse=True)

        return {
            "shap_method": "shap_tree" if shap_available else "feature_importance_approximation",
            "global_importance": global_dict,
            "local_explanation": local_contributions[:10],  # Top 10 factors
        }

    def compute_modality_attribution(
        self, feature_importance_dict: Dict[str, float]
    ) -> Dict[str, float]:
        """
        Aggregate feature importances into Market, News, and Fundamental modality groups.
        """
        modality_totals = {"Market": 0.0, "News": 0.0, "Fundamentals": 0.0}

        for feat, weight in feature_importance_dict.items():
            feat_lower = feat.lower()
            if any(k in feat_lower for k in ["sentiment", "news", "bert", "nlp", "polarity"]):
                modality_totals["News"] += weight
            elif any(k in feat_lower for k in ["pe_", "roe", "pb_", "ebitda", "revenue", "debt", "margin", "fundamental"]):
                modality_totals["Fundamentals"] += weight
            else:
                modality_totals["Market"] += weight

        total = sum(modality_totals.values()) + 1e-8
        return {k: float(v / total) for k, v in modality_totals.items()}
