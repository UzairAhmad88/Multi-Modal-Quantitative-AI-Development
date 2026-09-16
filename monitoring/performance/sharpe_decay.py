"""
Rolling Sharpe Ratio & Return Degradation Monitor.
"""

import numpy as np
from typing import Dict, Any


def calculate_sharpe_decay(
    baseline_returns: np.ndarray,
    target_returns: np.ndarray,
    annualization_factor: float = 252.0,
) -> Dict[str, Any]:
    """Calculates Sharpe ratio degradation between baseline and evaluation target periods."""
    b_rets = np.asarray(baseline_returns, dtype=float)
    t_rets = np.asarray(target_returns, dtype=float)

    b_rets = b_rets[~np.isnan(b_rets)]
    t_rets = t_rets[~np.isnan(t_rets)]

    b_sharpe = float(np.mean(b_rets) / (np.std(b_rets) + 1e-8) * np.sqrt(annualization_factor)) if len(b_rets) > 1 else 0.0
    t_sharpe = float(np.mean(t_rets) / (np.std(t_rets) + 1e-8) * np.sqrt(annualization_factor)) if len(t_rets) > 1 else 0.0

    sharpe_drop = b_sharpe - t_sharpe
    sharpe_decay_pct = sharpe_drop / max(abs(b_sharpe), 1e-6)

    return {
        "baseline_sharpe": b_sharpe,
        "target_sharpe": t_sharpe,
        "sharpe_drop": sharpe_drop,
        "sharpe_decay_pct": sharpe_decay_pct,
        "is_sharpe_decayed": sharpe_decay_pct > 0.30 or t_sharpe < 0.0,
    }
