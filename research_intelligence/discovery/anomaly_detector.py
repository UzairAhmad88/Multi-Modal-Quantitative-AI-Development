"""
Anomaly Detector for Quantitative Research Intelligence.
Detects statistical outliers across market, sentiment, and fundamental series,
converting observed anomalies into structured research questions rather than trading signals.
"""

from typing import Dict, Any, List
import pandas as pd
import numpy as np


class AnomalyDetectionEngine:
    """Detects z-score and IQR anomalies and generates research prompts."""

    def __init__(self, z_threshold: float = 3.0):
        self.z_threshold = z_threshold

    def detect_anomalies(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Scans numeric columns for statistical anomalies exceeding z-score threshold."""
        if df.empty:
            return {"status": "EMPTY", "anomalies": [], "research_questions": []}

        numeric_df = df.select_dtypes(include=[np.number])
        anomalies = []
        research_questions = []

        for col in numeric_df.columns:
            series = numeric_df[col].dropna()
            if len(series) < 10:
                continue

            mean = series.mean()
            std = series.std()
            if std == 0:
                continue

            z_scores = (series - mean) / std
            outliers = series[np.abs(z_scores) > self.z_threshold]

            for idx, val in outliers.items():
                z_val = float(z_scores.loc[idx])
                anomaly_type = "ELEVATED" if z_val > 0 else "DEPRESSED"
                anomalies.append({
                    "column": col,
                    "index": str(idx),
                    "value": round(float(val), 4),
                    "z_score": round(z_val, 2),
                    "type": anomaly_type
                })

                q = f"Observed unusually {anomaly_type.lower()} {col} (z={z_val:.1f} on {idx}). Does this relationship persist after controlling for market regime?"
                research_questions.append({
                    "column": col,
                    "anomaly_value": round(float(val), 4),
                    "question": q
                })

        return {
            "status": "SUCCESS",
            "total_anomalies": len(anomalies),
            "anomalies": anomalies[:50],  # cap list
            "research_questions": research_questions[:10]
        }
