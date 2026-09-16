"""
Master Regime Change Detector.
"""

import numpy as np
from typing import Dict, Any, List
from .volatility_shift import detect_volatility_jump
from .markov import MarkovRegimeTransition
from ..core.monitor_result import RegimeShiftResult


class RegimeChangeDetector:
    """Master regime shift detector."""

    def __init__(self, jump_threshold: float = 2.0):
        self.jump_threshold = jump_threshold
        self.markov = MarkovRegimeTransition()

    def detect_regime_shift(
        self,
        baseline_returns: np.ndarray,
        target_returns: np.ndarray,
    ) -> RegimeShiftResult:
        vol_info = detect_volatility_jump(baseline_returns, target_returns, self.jump_threshold)
        curr_regime, prob = self.markov.predict_regime(target_returns)

        b_regime, _ = self.markov.predict_regime(baseline_returns)
        is_shift = (curr_regime != b_regime) or vol_info["is_volatility_jump"]

        return RegimeShiftResult(
            current_regime=curr_regime,
            regime_transition_prob=prob,
            volatility_jump_ratio=vol_info["volatility_ratio"],
            is_regime_shift_detected=is_shift,
        )
