"""
Reproducibility Checker: Compares configuration hashes, random seeds, and dependency checksums.
"""

from typing import Dict, Any, Tuple


class ReproducibilityChecker:
    """Verifies experiment configuration and output hash match."""

    def verify_reproducibility(
        self,
        exp_a: Dict[str, Any],
        exp_b: Dict[str, Any]
    ) -> Tuple[str, Dict[str, Any]]:
        """Compares config hashes, seeds, and resulting Sharpe ratio."""
        hash_a = exp_a.get("configuration_hash", "")
        hash_b = exp_b.get("configuration_hash", "")
        seed_a = exp_a.get("random_seed")
        seed_b = exp_b.get("random_seed")

        sh_a = exp_a.get("metrics", {}).get("sharpe_ratio", 0.0)
        sh_b = exp_b.get("metrics", {}).get("sharpe_ratio", 0.0)

        hash_match = (hash_a == hash_b) and (hash_a != "")
        seed_match = (seed_a == seed_b)
        metric_diff = abs(sh_a - sh_b)

        if hash_match and seed_match and metric_diff < 1e-4:
            status = "MATCH"
        elif metric_diff < 0.05:
            status = "PARTIAL_MATCH"
        else:
            status = "MISMATCH"

        return status, {
            "hash_match": hash_match,
            "seed_match": seed_match,
            "metric_difference": round(metric_diff, 6),
            "status": status
        }
