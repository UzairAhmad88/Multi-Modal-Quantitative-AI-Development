"""
Constraint Engine for Validating and Enforcing Portfolio Bounds and Feasibility Rules.
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional, Tuple


class ConstraintEngine:
    """Enforces position limits, exposure bounds, turnover constraints, and long-only/long-short rules."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.long_only = self.config.get("long_only", True)
        self.max_weight = self.config.get("max_weight", 0.35)
        self.min_weight = self.config.get("min_weight", 0.00 if self.long_only else -0.35)
        self.max_gross_exposure = self.config.get("max_gross_exposure", 1.0)
        self.max_turnover = self.config.get("max_turnover", 1.0)

    def validate_weights(
        self,
        weights: Dict[str, float],
        current_weights: Optional[Dict[str, float]] = None
    ) -> Tuple[bool, List[str]]:
        """Validates proposed portfolio weight dictionary against all configured constraints."""
        if not weights:
            return False, ["Empty weights dictionary"]

        issues = []
        w_arr = np.array(list(weights.values()), dtype=float)

        # 1. Long-only constraint
        if self.long_only and np.any(w_arr < -1e-5):
            issues.append(f"Long-only violation: found negative weight ({np.min(w_arr):.4f})")

        # 2. Position bounds
        if np.any(w_arr > self.max_weight + 1e-5):
            issues.append(f"Max weight breach: weight ({np.max(w_arr):.4f}) exceeds max_weight {self.max_weight:.4f}")
        if np.any(w_arr < self.min_weight - 1e-5):
            issues.append(f"Min weight breach: weight ({np.min(w_arr):.4f}) below min_weight {self.min_weight:.4f}")

        # 3. Gross exposure
        gross_exp = float(np.sum(np.abs(w_arr)))
        if gross_exp > self.max_gross_exposure + 1e-4:
            issues.append(f"Gross exposure breach: gross ({gross_exp:.4f}) exceeds limit {self.max_gross_exposure:.4f}")

        # 4. Turnover constraint
        if current_weights:
            turnover = 0.0
            all_assets = set(weights.keys()).union(set(current_weights.keys()))
            for a in all_assets:
                w_t = weights.get(a, 0.0)
                w_c = current_weights.get(a, 0.0)
                turnover += abs(w_t - w_c)
            if turnover > self.max_turnover + 1e-4:
                issues.append(f"Turnover breach: turnover ({turnover:.4f}) exceeds max_turnover {self.max_turnover:.4f}")

        is_valid = len(issues) == 0
        return is_valid, issues

    def apply_projection(self, weights: Dict[str, float]) -> Dict[str, float]:
        """Projects unconstrained weights onto feasible constraint region."""
        if not weights:
            return {}

        assets = list(weights.keys())
        w_arr = np.array([weights[a] for a in assets], dtype=float)

        if self.long_only:
            w_arr = np.clip(w_arr, 0.0, None)

        w_arr = np.clip(w_arr, self.min_weight, self.max_weight)

        total = np.sum(np.abs(w_arr))
        if total > self.max_gross_exposure:
            w_arr = w_arr * (self.max_gross_exposure / total)

        w_arr = np.clip(w_arr, self.min_weight, self.max_weight)

        return {assets[i]: float(round(w_arr[i], 6)) for i in range(len(assets))}
