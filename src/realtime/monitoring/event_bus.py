"""
Real-Time Event Bus & System Health Monitor
In-memory pub/sub event dispatcher and real-time system status reporter.
"""

from datetime import datetime, timezone
from typing import Dict, List, Any, Callable


class RealtimeEventBus:
    """In-Memory Quantitative Event Bus & Status Monitor."""

    def __init__(self):
        self.subscribers: Dict[str, List[Callable[[Dict[str, Any]], None]]] = {}
        self.event_log: List[Dict[str, Any]] = []
        self.system_status = {
            "market_data_status": "ONLINE",
            "nlp_status": "ONLINE",
            "model_inference_status": "ONLINE",
            "risk_engine_status": "PASSING",
            "execution_status": "PAPER_ACTIVE",
            "trading_enabled": False,
        }

    def subscribe(self, event_type: str, callback: Callable[[Dict[str, Any]], None]):
        """Subscribe callback to specific event type."""
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(callback)

    def publish(self, event_type: str, payload: Dict[str, Any]):
        """Publish event to all registered subscribers."""
        event_record = {
            "event_type": event_type,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "payload": payload,
        }
        self.event_log.append(event_record)

        if event_type in self.subscribers:
            for cb in self.subscribers[event_type]:
                try:
                    cb(payload)
                except Exception:
                    pass

    def get_health_status(self) -> Dict[str, Any]:
        """Return system health summary payload for GET /health/realtime."""
        return {
            "status": "HEALTHY",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "system_components": self.system_status,
            "total_events_logged": len(self.event_log),
            "trading_mode": "PAPER_TRADING_ONLY" if not self.system_status["trading_enabled"] else "LIVE_TRADING",
        }
