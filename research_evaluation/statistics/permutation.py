"""
Permutation Test Engine: Permutes return ordering to test null hypothesis of zero temporal predictability.
"""

import numpy as np
from typing import List, Dict, Any


class PermutationTester:
    """Permutation test assessing null hypothesis of zero predictive structure."""

    def __init__(self, num_permutations: int = 500, random_seed: int = 42):
        self.num_permutations = num_permutations
        self.random_seed = random_seed

    def test_permutation(self, returns: List[float]) -> Dict[str, Any]:
        """Calculates permutation p-value for cumulative strategy return."""
        rets = np.array(returns, dtype=float)
        if len(rets) < 10:
            return {"p_value": 1.0, "observed_return": 0.0}

        np.random.seed(self.random_seed)
        obs_total = float(np.sum(rets))

        perm_totals = []
        for _ in range(self.num_permutations):
            shuffled = np.random.permutation(rets)
            perm_totals.append(np.sum(shuffled))

        perm_totals = np.array(perm_totals)
        p_val = float(np.mean(perm_totals >= obs_total))

        return {
            "observed_total_return": round(obs_total, 4),
            "permuted_mean_return": round(float(np.mean(perm_totals)), 4),
            "permutation_p_value": round(p_val, 6),
            "is_significant": bool(p_val < 0.05),
            "num_permutations": self.num_permutations
        }
