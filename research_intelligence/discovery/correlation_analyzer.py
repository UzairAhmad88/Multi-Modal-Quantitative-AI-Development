"""
Correlation Analyzer for Quantitative Research Intelligence.
Computes Pearson and Spearman rank correlations across multi-modal feature series without claiming causation.
"""

from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np
from scipy import stats


class CorrelationAnalyzer:
    """Computes statistical correlation metrics across multi-modal variables."""

    @staticmethod
    def analyze_correlations(
        df: pd.DataFrame,
        variables: Optional[List[str]] = None,
        target_col: Optional[str] = None
    ) -> Dict[str, Any]:
        """Computes pairwise Pearson and Spearman correlation coefficients and p-values."""
        if df.empty:
            return {"status": "EMPTY", "correlations": []}

        numeric_df = df.select_dtypes(include=[np.number]).dropna()
        if numeric_df.empty or len(numeric_df) < 5:
            return {"status": "INSUFFICIENT_DATA", "correlations": []}

        target_vars = variables or [c for c in numeric_df.columns if c != target_col]
        target = target_col or (numeric_df.columns[-1] if len(numeric_df.columns) > 1 else numeric_df.columns[0])

        results = []
        for var in target_vars:
            if var in numeric_df.columns and var != target:
                x = numeric_df[var].values
                y = numeric_df[target].values

                # Pearson
                p_corr, p_val = stats.pearsonr(x, y)
                # Spearman
                s_corr, s_val = stats.spearmanr(x, y)

                results.append({
                    "variable": var,
                    "target": target,
                    "pearson_corr": round(float(p_corr), 4),
                    "pearson_pvalue": round(float(p_val), 6),
                    "spearman_corr": round(float(s_corr), 4),
                    "spearman_pvalue": round(float(s_val), 6),
                    "sample_size": len(numeric_df),
                    "is_significant": bool(p_val < 0.05 or s_val < 0.05)
                })

        # Sort by absolute Pearson correlation
        results.sort(key=lambda r: abs(r["pearson_corr"]), reverse=True)

        return {
            "status": "SUCCESS",
            "target": target,
            "sample_size": len(numeric_df),
            "correlations": results,
            "multiple_testing_warning": len(results) > 10
        }
