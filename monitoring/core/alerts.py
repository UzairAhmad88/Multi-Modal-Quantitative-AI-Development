"""
Alert Manager and Severity Levels for Monitoring OS.
"""

import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class AlertSeverity(str, Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"


class MonitoringAlert(BaseModel):
    alert_id: str
    component: str  # e.g. "DATA_DRIFT", "CONCEPT_DRIFT", "ALPHA_DECAY", "REGIME_SHIFT", "HEALTH"
    severity: AlertSeverity
    message: str
    timestamp: str = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat())
    metric_name: Optional[str] = None
    observed_value: Optional[float] = None
    threshold: Optional[float] = None
    evidence: Dict[str, Any] = Field(default_factory=dict)


class AlertManager:
    """Collects, filters, and formats monitoring alerts."""

    def __init__(self):
        self._alerts: List[MonitoringAlert] = []

    def add_alert(
        self,
        alert_id: str,
        component: str,
        severity: AlertSeverity,
        message: str,
        metric_name: Optional[str] = None,
        observed_value: Optional[float] = None,
        threshold: Optional[float] = None,
        evidence: Optional[Dict[str, Any]] = None,
    ) -> MonitoringAlert:
        alert = MonitoringAlert(
            alert_id=alert_id,
            component=component,
            severity=severity,
            message=message,
            metric_name=metric_name,
            observed_value=observed_value,
            threshold=threshold,
            evidence=evidence or {},
        )
        self._alerts.append(alert)
        return alert

    def get_alerts(self, min_severity: Optional[AlertSeverity] = None) -> List[MonitoringAlert]:
        if min_severity is None:
            return list(self._alerts)

        severity_order = {AlertSeverity.INFO: 1, AlertSeverity.WARNING: 2, AlertSeverity.CRITICAL: 3}
        min_rank = severity_order.get(min_severity, 1)

        return [a for a in self._alerts if severity_order.get(a.severity, 1) >= min_rank]

    def clear(self) -> None:
        self._alerts.clear()

    def to_dict_list(self) -> List[Dict[str, Any]]:
        return [a.model_dump() for a in self._alerts]
