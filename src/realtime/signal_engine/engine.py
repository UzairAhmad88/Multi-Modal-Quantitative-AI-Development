"""
Real-Time Signal Engine Module
Evaluates multi-modal features, model predictions, confidence thresholds, signal cooldowns,
and current position states to generate actionable trading signals.
"""

from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
import numpy as np


class RealtimeSignalEngine:
    """Quantitative Real-Time Alpha Signal Engine."""

    def __init__(
        self,
        long_threshold: float = 0.015,
        short_threshold: float = -0.015,
        min_confidence: float = 0.60,
        cooldown_seconds: int = 60,
    ):
        self.long_threshold = long_threshold
        self.short_threshold = short_threshold
        self.min_confidence = min_confidence
        self.cooldown_seconds = cooldown_seconds

        self.last_signal_time: Dict[str, datetime] = {}
        self.current_positions: Dict[str, str] = {}  # symbol -> 'LONG', 'SHORT', 'FLAT'

    def process_features(
        self,
        symbol: str,
        features: Dict[str, float],
        predicted_return: float,
        confidence: float,
        modality_status: Optional[Dict[str, bool]] = None,
    ) -> Dict[str, Any]:
        """
        Evaluate real-time model prediction and output alpha signal decision.
        """
        sym = symbol.upper()
        now = datetime.now(timezone.utc)

        # Check cooldown
        if sym in self.last_signal_time:
            elapsed = (now - self.last_signal_time[sym]).total_seconds()
            if elapsed < self.cooldown_seconds:
                return {
                    "timestamp": now.isoformat(),
                    "symbol": sym,
                    "signal": "COOLDOWN_SKIP",
                    "predicted_return": predicted_return,
                    "confidence": confidence,
                    "reason": f"Signal skipped due to active {self.cooldown_seconds}s cooldown",
                }

        # Default modality status if not provided
        if modality_status is None:
            modality_status = {"market_available": True, "news_available": True, "fundamentals_available": True}

        curr_pos = self.current_positions.get(sym, "FLAT")
        raw_signal = "FLAT"

        if confidence >= self.min_confidence:
            if predicted_return >= self.long_threshold and curr_pos != "LONG":
                raw_signal = "LONG"
            elif predicted_return <= self.short_threshold and curr_pos != "SHORT":
                raw_signal = "SHORT"
            elif abs(predicted_return) < abs(self.short_threshold) and curr_pos != "FLAT":
                raw_signal = "EXIT"

        if raw_signal in ["LONG", "SHORT", "EXIT"]:
            self.last_signal_time[sym] = now
            if raw_signal == "LONG":
                self.current_positions[sym] = "LONG"
            elif raw_signal == "SHORT":
                self.current_positions[sym] = "SHORT"
            elif raw_signal == "EXIT":
                self.current_positions[sym] = "FLAT"

        return {
            "timestamp": now.isoformat(),
            "symbol": sym,
            "signal": raw_signal,
            "predicted_return": round(predicted_return, 6),
            "confidence": round(confidence, 4),
            "current_position_state": self.current_positions.get(sym, "FLAT"),
            "modality_status": modality_status,
        }
