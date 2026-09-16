"""
Alpha Signal IC & Half-Life Decay Engine.
"""

import numpy as np
from scipy import stats
from typing import Dict, Any, List, Tuple
from ..core.monitor_result import AlphaDecayResult


def calculate_alpha_ic_decay(
    signals: np.ndarray,
    future_returns: np.ndarray,
    lags: List[int] = None,
) -> Dict[str, Any]:
    """Calculates Information Coefficient (Pearson & Spearman Rank IC) across lag horizons."""
    if lags is None:
        lags = [1, 2, 3, 5, 10, 20]

    signals = np.asarray(signals, dtype=float)
    future_returns = np.asarray(future_returns, dtype=float)

    ic_map = {}
    rank_ic_map = {}

    for lag in lags:
        if len(signals) <= lag:
            ic_map[lag] = 0.0
            rank_ic_map[lag] = 0.0
            continue

        s = signals[:-lag]
        r = future_returns[lag:]

        valid_mask = ~np.isnan(s) & ~np.isnan(r)
        if np.sum(valid_mask) < 5:
            ic_map[lag] = 0.0
            rank_ic_map[lag] = 0.0
            continue

        pearson_ic, _ = stats.pearsonr(s[valid_mask], r[valid_mask])
        spearman_ic, _ = stats.spearmanr(s[valid_mask], r[valid_mask])

        ic_map[lag] = float(pearson_ic) if not np.isnan(pearson_ic) else 0.0
        rank_ic_map[lag] = float(spearman_ic) if not np.isnan(spearman_ic) else 0.0

    # Estimate IC half-life (days until IC drops to 50% of lag-1 IC)
    ic_1 = abs(rank_ic_map.get(1, 0.0))
    half_life_days = 1.0
    if ic_1 > 1e-4:
        for lag in sorted(lags):
            if abs(rank_ic_map.get(lag, 0.0)) <= 0.5 * ic_1:
                half_life_days = float(lag)
                break
        else:
            half_life_days = float(max(lags))

    return {
        "ic_by_lag": ic_map,
        "rank_ic_by_lag": rank_ic_map,
        "ic_lag_1": rank_ic_map.get(1, 0.0),
        "ic_half_life_days": half_life_days,
    }


class AlphaDecayTracker:
    """Tracks historical rolling alpha IC and flags decay."""

    def __init__(self, ic_decay_threshold_pct: float = 0.30):
        self.ic_decay_threshold_pct = ic_decay_threshold_pct

    def evaluate_alpha_decay(
        self,
        baseline_signals: np.ndarray,
        baseline_returns: np.ndarray,
        target_signals: np.ndarray,
        target_returns: np.ndarray,
    ) -> AlphaDecayResult:
        b_res = calculate_alpha_ic_decay(baseline_signals, baseline_returns)
        t_res = calculate_alpha_ic_decay(target_signals, target_returns)

        b_ic = b_res["ic_lag_1"]
        t_ic = t_res["ic_lag_1"]

        ic_decay_pct = (b_ic - t_ic) / max(abs(b_ic), 1e-6)

        # Estimate rolling Sharpe and max drawdown
        b_sharpe = float(np.mean(baseline_returns) / (np.std(baseline_returns) + 1e-6) * np.sqrt(252)) if len(baseline_returns) > 0 else 0.0
        t_sharpe = float(np.mean(target_returns) / (np.std(target_returns) + 1e-6) * np.sqrt(252)) if len(target_returns) > 0 else 0.0

        sharpe_decay_pct = (b_sharpe - t_sharpe) / max(abs(b_sharpe), 1e-6)

        cum_rets = np.cumsum(target_returns) if len(target_returns) > 0 else np.array([0.0])
        peak = np.maximum.accumulate(cum_rets)
        drawdowns = (cum_rets - peak)
        max_dd = float(abs(np.min(drawdowns))) if len(drawdowns) > 0 else 0.0

        is_flagged = ic_decay_pct >= self.ic_decay_threshold_pct or sharpe_decay_pct >= 0.30

        return AlphaDecayResult(
            rolling_ic=t_ic,
            rank_ic=t_res["rank_ic_by_lag"].get(1, 0.0),
            ic_half_life_days=t_res["ic_half_life_days"],
            ic_decay_pct=ic_decay_pct,
            rolling_sharpe=t_sharpe,
            sharpe_decay_pct=sharpe_decay_pct,
            max_drawdown_pct=max_dd,
            is_decay_flagged=is_flagged,
        )
