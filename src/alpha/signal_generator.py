from __future__ import annotations
from typing import Dict, Any, List, Tuple
import numpy as np
import pandas as pd


def compute_signal_confidence(
    alpha: float,
    model_signals: List[str] | None = None,
    data_quality_score: float = 1.0
) -> Dict[str, Any]:
    """Calculate signal confidence combining signal magnitude, model agreement, and data quality."""
    signal_magnitude = abs(alpha)

    if model_signals and len(model_signals) > 0:
        dominant_signal = max(set(model_signals), key=model_signals.count)
        agreement = model_signals.count(dominant_signal) / len(model_signals)
    else:
        agreement = 1.0

    raw_confidence = (0.5 * signal_magnitude) + (0.3 * agreement) + (0.2 * data_quality_score)

    if raw_confidence >= 0.70:
        level = "HIGH"
    elif raw_confidence >= 0.40:
        level = "MEDIUM"
    else:
        level = "LOW"

    return {
        "confidence_score": round(raw_confidence, 4),
        "confidence_level": level,
        "agreement": round(agreement, 2),
        "data_quality": round(data_quality_score, 2)
    }


def generate_signal(
    alpha: float,
    buy_threshold: float = 0.50,
    sell_threshold: float = -0.50,
    model_signals: List[str] | None = None,
    return_details: bool = False
) -> str | Tuple[str, Dict[str, Any]]:
    """Convert continuous alpha score into discrete BUY / HOLD / SELL signal."""
    if alpha >= buy_threshold:
        signal = "BUY"
    elif alpha <= sell_threshold:
        signal = "SELL"
    else:
        signal = "HOLD"

    conf = compute_signal_confidence(alpha, model_signals)

    if return_details:
        return signal, conf
    return signal


class AlphaEngine:
    """Combines multi-modal predictions, normalizes alpha scores, generates signals, and evaluates confidence."""

    def __init__(self, buy_threshold: float = 0.50, sell_threshold: float = -0.50):
        self.buy_threshold = buy_threshold
        self.sell_threshold = sell_threshold

    def process_predictions(self, raw_predictions: Dict[str, float]) -> Dict[str, Any]:
        """Process dictionary of model predictions {model_name: expected_return}."""
        alphas = {m: float(np.tanh(ret / 0.05)) for m, ret in raw_predictions.items()}
        composite_alpha = float(np.mean(list(alphas.values()))) if alphas else 0.0

        model_signals = [
            generate_signal(a, self.buy_threshold, self.sell_threshold)
            for a in alphas.values()
        ]

        signal, conf = generate_signal(
            composite_alpha, self.buy_threshold, self.sell_threshold, model_signals, return_details=True
        )

        return {
            "composite_alpha": round(composite_alpha, 4),
            "signal": signal,
            "confidence_level": conf["confidence_level"],
            "confidence_score": conf["confidence_score"],
            "model_alphas": alphas,
            "model_signals": model_signals
        }
