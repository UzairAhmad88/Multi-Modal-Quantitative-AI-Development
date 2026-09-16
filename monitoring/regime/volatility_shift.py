"""
Volatility Jump & Regime Shift Detector.
"""

import numpy as np
from typing import Tuple, Dict, Any


def detect_volatility_jump(
    baseline_returns: np.ndarray,
    target_returns: np.ndarray,
    jump_threshold_ratio: float = 2.0,
) -> Dict[str, Any]:
    """Detects volatility jumps between baseline and target return series."""
    b_rets = np.asarray(baseline_returns, dtype=float)
    t_rets = np.asarray(target_returns, dtype=float)

    b_vol = float(np.std(b_rets)) if len(b_rets) > 0 else 0.01
    t_vol = float(np.std(t_rets)) if len(t_rets) > 0 else 0.01

    vol_ratio = t_vol / max(b_vol, 1e-6)
    is_jump = vol_ratio >= jump_threshold_ratio

    return {
        "baseline_volatility": b_vol,
        "target_volatility": t_vol,
        "volatility_ratio": vol_ratio,
        "is_volatility_jump": is_jump,
    }
