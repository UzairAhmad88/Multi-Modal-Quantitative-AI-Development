from __future__ import annotations
import pandas as pd
import numpy as np


class PositionSizer:
    """Calculates risk-adjusted position sizes based on alpha score, confidence, volatility, and exposure limits."""

    def __init__(
        self,
        max_position: float = 0.25,
        max_gross_exposure: float = 1.0,
        min_cash: float = 0.0
    ):
        self.max_position = max_position
        self.max_gross_exposure = max_gross_exposure
        self.min_cash = min_cash

    def calculate_weights(
        self,
        alphas: pd.Series,
        confidences: pd.Series | None = None,
        volatilities: pd.Series | None = None
    ) -> pd.Series:
        if alphas.empty:
            return pd.Series(dtype=float)

        raw = alphas.copy()
        # Scale by confidence if provided
        if confidences is not None:
            raw = raw * confidences

        # Scale inversely by volatility if provided
        if volatilities is not None and not volatilities.empty:
            vol_scale = 1.0 / (volatilities + 1e-4)
            raw = raw * vol_scale

        # Filter out negative or zero alphas for long-only portfolio
        longs = raw.clip(lower=0.0)
        total = longs.sum()

        if total > 1e-8:
            weights = longs / total
        else:
            weights = pd.Series(1.0 / len(alphas), index=alphas.index)

        # Cap max position constraint
        capped = cap_weights(weights, maximum=self.max_position)
        return capped


def cap_weights(weights: pd.Series, maximum: float = 0.25) -> pd.Series:
    """Clip individual asset weights to maximum limit and renormalize."""
    if weights.empty or weights.sum() == 0:
        return weights

    out = weights.copy()
    for _ in range(5):  # Iterative capping and redistribution
        over = out > maximum
        if not over.any():
            break
        out[over] = maximum
        under = ~over
        if under.sum() > 0:
            remaining = 1.0 - (over.sum() * maximum)
            under_sum = out[under].sum()
            if under_sum > 0:
                out[under] = out[under] * (remaining / under_sum)

    return out / out.sum()
