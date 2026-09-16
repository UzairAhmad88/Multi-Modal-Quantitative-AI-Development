"""
Alert Engine Module
Generates, filters, deduplicates, and logs system, risk, and data alerts with cooldown windows.
"""

from datetime import datetime, timezone
import uuid
from typing import Dict, List, Any, Optional


class AlertEngine:
    """Quantitative Alert Engine with Deduplication & Cooldown Control."""

    def __init__(self, cooldown_sec: float = 60.0):
        self.cooldown_sec = cooldown_sec
        self.alerts: List[Dict[str, Any]] = []
        self.last_alert_time: Dict[str, float] = {}

    def emit_alert(
        self,
        event_type: str,
        message: str,
        severity: str = "WARNING",
        component: str = "SYSTEM"
    ) -> Optional[Dict[str, Any]]:
        """
        Emit a structured system or risk alert if not suppressed by cooldown window.
        """
        now = datetime.now(timezone.utc)
        now_ts = now.timestamp()

        alert_key = f"{event_type}_{component}_{severity}"
        if alert_key in self.last_alert_time:
            if (now_ts - self.last_alert_time[alert_key]) < self.cooldown_sec:
                # Deduplicated / Suppressed
                return None

        self.last_alert_time[alert_key] = now_ts

        alert_record = {
            "alert_id": f"ALT-{uuid.uuid4().hex[:6].upper()}",
            "timestamp": now.isoformat(),
            "severity": severity,
            "event_type": event_type,
            "component": component,
            "message": message,
            "is_acknowledged": False
        }
        self.alerts.append(alert_record)
        return alert_record

    def get_alerts(self, severity_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """Retrieve recent alerts."""
        if severity_filter:
            return [a for a in self.alerts if a["severity"].upper() == severity_filter.upper()]
        return self.alerts
