"""
Weight Validation Module for Portfolio Construction OS.
"""

from typing import Dict, Any, List, Tuple, Optional
import math


class WeightValidator:
    """Validates numerical integrity, asset mapping, and baseline constraint bounds of portfolio weights."""

    @staticmethod
    def validate_weights(
        weights: Dict[str, float],
        known_assets: Optional[List[str]] = None,
        long_only: bool = True,
        max_position_weight: float = 1.0,
        min_position_weight: float = -1.0,
        max_leverage: float = 1.0,
    ) -> Tuple[bool, List[str]]:
        """Validate numeric soundness, asset match, and position bounds."""
        errors: List[str] = []

        if not isinstance(weights, dict):
            return False, ["Weights must be a dictionary of asset -> weight float"]

        for asset, w in weights.items():
            if not isinstance(w, (int, float)):
                errors.append(f"Non-numeric weight for asset '{asset}': {w}")
                continue
            if math.isnan(w) or math.isinf(w):
                errors.append(f"Non-finite weight (NaN/Inf) for asset '{asset}': {w}")
                continue

            if known_assets and asset not in known_assets:
                errors.append(f"Asset '{asset}' is not in known_assets list")

            if long_only and w < -1e-7:
                errors.append(f"Long-only violation for asset '{asset}': weight={w:.4f} < 0")

            if w > max_position_weight + 1e-7:
                errors.append(f"Max position weight violation for '{asset}': weight={w:.4f} > {max_position_weight}")

            if not long_only and w < min_position_weight - 1e-7:
                errors.append(f"Min position weight violation for '{asset}': weight={w:.4f} < {min_position_weight}")

        gross_exposure = sum(abs(w) for w in weights.values() if not math.isnan(w) and not math.isinf(w))
        if gross_exposure > max_leverage + 1e-5:
            errors.append(f"Max leverage violation: gross exposure {gross_exposure:.4f} > {max_leverage:.4f}")

        is_valid = len(errors) == 0
        return is_valid, errors

    @staticmethod
    def normalize_weights(weights: Dict[str, float], target_sum: float = 1.0) -> Dict[str, float]:
        """Normalize positive weights to sum to target_sum."""
        total = sum(max(0.0, w) for w in weights.values())
        if total <= 0:
            n = len(weights)
            return {k: target_sum / n for k in weights} if n > 0 else {}
        return {k: (max(0.0, w) / total) * target_sum for k, w in weights.items()}
