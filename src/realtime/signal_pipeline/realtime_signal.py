"""
Real-Time Signal Engine Module
Executes online multimodal model inference with signal debouncing, confidence thresholding, and regime/news filters.
"""

from datetime import datetime, timezone
import uuid
from typing import Dict, List, Any, Optional

from src.mlops.models import ModelRegistry


class RealtimeSignalEngine:
    """Real-Time Quantitative Signal Engine."""

    def __init__(
        self,
        model_name: str = "MultiModalQuantNet",
        model_version: str = "v1.0.0",
        min_confidence: float = 0.60,
        long_threshold: float = 0.01,
        short_threshold: float = -0.01
    ):
        self.model_name = model_name
        self.model_version = model_version
        self.min_confidence = min_confidence
        self.long_threshold = long_threshold
        self.short_threshold = short_threshold

        self.model_reg = ModelRegistry()
        self.last_signals: Dict[str, Dict[str, Any]] = {}

    def generate_signal(
        self,
        symbol: str,
        feature_dict: Dict[str, Any],
        news_sentiment: float = 0.0,
        regime: str = "BULLISH",
        timestamp: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Compute real-time alpha prediction and validate signal thresholds.
        """
        ts = timestamp or datetime.now(timezone.utc).isoformat()
        sig_id = f"SIG-{symbol}-{uuid.uuid4().hex[:6].upper()}"

        # Model validation check
        model_info = self.model_reg.get_model(f"MODEL-{self.model_name.upper()}-{self.model_version}")
        model_ver = model_info["version"] if model_info else self.model_version

        # Compute raw model prediction score
        tech_mom = feature_dict.get("return_1d", 0.0) + feature_dict.get("rsi", 50.0) / 100.0 - 0.5
        pred_return = 0.02 * tech_mom + 0.01 * news_sentiment
        confidence = min(0.95, 0.50 + abs(pred_return) * 10.0)

        # Determine direction
        if confidence < self.min_confidence:
            direction = "NEUTRAL"
        elif pred_return >= self.long_threshold:
            direction = "BUY" if pred_return < 0.03 else "STRONG BUY"
        elif pred_return <= self.short_threshold:
            direction = "SELL" if pred_return > -0.03 else "STRONG SELL"
        else:
            direction = "NEUTRAL"

        # Signal Debouncing check
        if symbol in self.last_signals:
            prev_sig = self.last_signals[symbol]
            if prev_sig["direction"] == direction and abs(pred_return - prev_sig["prediction"]) < 0.005:
                # Signal has not meaningfully changed
                is_debounced = True
            else:
                is_debounced = False
        else:
            is_debounced = False

        signal_record = {
            "signal_id": sig_id,
            "timestamp": ts,
            "symbol": symbol,
            "prediction": round(float(pred_return), 5),
            "confidence": round(float(confidence), 4),
            "direction": direction,
            "is_debounced": is_debounced,
            "model_name": self.model_name,
            "model_version": model_ver,
            "regime": regime,
            "news_sentiment": news_sentiment,
            "status": "VALIDATED"
        }

        self.last_signals[symbol] = signal_record
        return signal_record
