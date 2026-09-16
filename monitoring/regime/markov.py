"""
Markov Regime Transition State Probability Estimator.
"""

import numpy as np
from typing import Dict, Any, List, Tuple


class MarkovRegimeTransition:
    """Estimates state transition probabilities across macro regimes (e.g. BULL, BEAR, HIGH_VOLATILITY, STAGNANT)."""

    def __init__(self, states: List[str] = None):
        self.states = states or ["BULL", "BEAR", "HIGH_VOLATILITY", "STAGNANT"]
        self.state_to_idx = {s: i for i, s in enumerate(self.states)}

    def estimate_transition_matrix(self, regime_sequence: List[str]) -> np.ndarray:
        n = len(self.states)
        trans_counts = np.zeros((n, n), dtype=float)

        for i in range(len(regime_sequence) - 1):
            s_curr = regime_sequence[i]
            s_next = regime_sequence[i + 1]
            if s_curr in self.state_to_idx and s_next in self.state_to_idx:
                idx_curr = self.state_to_idx[s_curr]
                idx_next = self.state_to_idx[s_next]
                trans_counts[idx_curr, idx_next] += 1.0

        row_sums = trans_counts.sum(axis=1, keepdims=True)
        row_sums[row_sums == 0] = 1.0
        trans_matrix = trans_counts / row_sums
        return trans_matrix

    def predict_regime(self, return_series: np.ndarray) -> Tuple[str, float]:
        """Classifies current return series into regime state and transition probability."""
        if len(return_series) == 0:
            return "STAGNANT", 0.5

        cum_ret = float(np.sum(return_series))
        vol = float(np.std(return_series) * np.sqrt(252))

        if vol > 0.30:
            regime = "HIGH_VOLATILITY"
            prob = min(vol / 0.50, 0.99)
        elif cum_ret > 0.05:
            regime = "BULL"
            prob = 0.85
        elif cum_ret < -0.05:
            regime = "BEAR"
            prob = 0.85
        else:
            regime = "STAGNANT"
            prob = 0.70

        return regime, prob
