"""
System Health Monitor & Latency Tracker Module
Monitors real-time sub-components, tracks latency metrics, and handles /health, /ready, and /live endpoints.
"""

from datetime import datetime, timezone
import time
from typing import Dict, List, Any, Optional


class SystemHealthMonitor:
    """Quantitative System Health & Latency Monitor."""

    def __init__(self):
        self.subsystems = {
            "data_feed": "HEALTHY",
            "feature_pipeline": "HEALTHY",
            "model_registry": "HEALTHY",
            "signal_engine": "HEALTHY",
            "portfolio_engine": "HEALTHY",
            "risk_engine": "HEALTHY",
            "execution_engine": "HEALTHY",
            "database": "HEALTHY"
        }
        self.latency_ms: Dict[str, float] = {
            "data_latency": 12.5,
            "feature_latency": 8.2,
            "model_latency": 24.1,
            "portfolio_latency": 15.0,
            "risk_latency": 4.8,
            "execution_latency": 18.3
        }

    def record_latency(self, component: str, latency_ms: float):
        """Record runtime component execution latency."""
        self.latency_ms[f"{component}_latency"] = round(latency_ms, 2)

    def set_subsystem_status(self, component: str, status: str):
        """Set subsystem health status."""
        if component in self.subsystems:
            self.subsystems[component] = status

    def get_health_status(self) -> Dict[str, Any]:
        """Return overall health status payload for /health."""
        is_all_healthy = all(s == "HEALTHY" for s in self.subsystems.values())
        return {
            "status": "HEALTHY" if is_all_healthy else "DEGRADED",
            "system": "QUANT AI - Real-Time Paper Engine",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "subsystems": self.subsystems,
            "latency_ms": self.latency_ms,
            "active_errors": [comp for comp, stat in self.subsystems.items() if stat != "HEALTHY"]
        }

    def is_ready(self) -> bool:
        """Return True if system is ready to process signals (/ready)."""
        critical_systems = ["data_feed", "feature_pipeline", "model_registry", "risk_engine", "execution_engine"]
        return all(self.subsystems.get(sys) == "HEALTHY" for sys in critical_systems)

    def is_live(self) -> bool:
        """Return True if process is alive (/live)."""
        return True
