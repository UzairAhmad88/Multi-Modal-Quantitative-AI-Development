"""
Feature Importance Shift Auditor.
"""

import numpy as np
from scipy import stats
from typing import Dict, List, Tuple


def calculate_importance_shift(
    baseline_importance: Dict[str, float],
    target_importance: Dict[str, float],
    top_k: int = 10,
) -> Tuple[float, float, float]:
    """Calculates cosine similarity, Spearman rank correlation, and top-K overlap ratio for feature importances."""
    common_features = sorted(list(set(baseline_importance.keys()).intersection(set(target_importance.keys()))))
    if len(common_features) == 0:
        return 0.0, 0.0, 0.0

    b_vec = np.array([baseline_importance[f] for f in common_features], dtype=float)
    t_vec = np.array([target_importance[f] for f in common_features], dtype=float)

    norm_b = np.linalg.norm(b_vec)
    norm_t = np.linalg.norm(t_vec)
    if norm_b == 0 or norm_t == 0:
        cosine_sim = 1.0 if norm_b == norm_t else 0.0
    else:
        cosine_sim = float(np.dot(b_vec, t_vec) / (norm_b * norm_t))

    if len(common_features) > 1:
        rank_corr, _ = stats.spearmanr(b_vec, t_vec)
        rank_corr = float(rank_corr) if not np.isnan(rank_corr) else 0.0
    else:
        rank_corr = 1.0

    # Top-K overlap ratio
    b_top_k = set(sorted(baseline_importance.keys(), key=lambda f: baseline_importance[f], reverse=True)[:top_k])
    t_top_k = set(sorted(target_importance.keys(), key=lambda f: target_importance[f], reverse=True)[:top_k])
    top_k_overlap = len(b_top_k.intersection(t_top_k)) / max(len(b_top_k), 1)

    return float(cosine_sim), float(rank_corr), float(top_k_overlap)
