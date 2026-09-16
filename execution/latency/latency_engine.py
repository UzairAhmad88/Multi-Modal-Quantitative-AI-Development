"""
Latency Engine for modeling signal, decision, order submission, and execution delays.
"""

from typing import Dict, Any, Optional
from datetime import datetime, timedelta


class LatencyEngine:
    """Calculates granular execution timing delays."""

    def __init__(
        self,
        signal_ms: float = 50.0,
        decision_ms: float = 20.0,
        order_submission_ms: float = 30.0,
        execution_ms: float = 100.0
    ):
        self.signal_ms = signal_ms
        self.decision_ms = decision_ms
        self.order_submission_ms = order_submission_ms
        self.execution_ms = execution_ms

    @property
    def total_latency_ms(self) -> float:
        return self.signal_ms + self.decision_ms + self.order_submission_ms + self.execution_ms

    def compute_timestamps(self, base_timestamp: Optional[str] = None) -> Dict[str, Any]:
        """Calculates precise timestamp sequence from signal generation to fill completion."""
        if base_timestamp:
            try:
                base_dt = datetime.fromisoformat(base_timestamp.replace("Z", "+00:00"))
            except Exception:
                base_dt = datetime.utcnow()
        else:
            base_dt = datetime.utcnow()

        t_signal = base_dt
        t_decision = t_signal + timedelta(milliseconds=self.signal_ms)
        t_order = t_decision + timedelta(milliseconds=self.decision_ms)
        t_submit = t_order + timedelta(milliseconds=self.order_submission_ms)
        t_fill = t_submit + timedelta(milliseconds=self.execution_ms)

        return {
            "signal_timestamp": t_signal.isoformat() + "Z",
            "decision_timestamp": t_decision.isoformat() + "Z",
            "order_timestamp": t_order.isoformat() + "Z",
            "submission_timestamp": t_submit.isoformat() + "Z",
            "fill_timestamp": t_fill.isoformat() + "Z",
            "total_latency_ms": round(self.total_latency_ms, 2)
        }
