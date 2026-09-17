"""
Trading Kill Switch Module.
Provides circuit breaker protection across all execution environments (PAPER, SHADOW, SANDBOX, LIVE).
Safely halts order generation and rebalancing upon risk or system breach.
"""

from datetime import datetime, timezone
import os
from typing import Dict, Any, Optional

from src.execution.safety.environment import SafetyGuard, ExecutionEnvironment


class TradingKillSwitch:
    """Quantitative Trading Kill Switch & Safety Circuit Breaker."""

    def __init__(self, mode_env_var: str = "TRADING_MODE"):
        self.mode_env_var = mode_env_var
        self.is_active: bool = False
        self.reason: Optional[str] = None
        self.activated_at: Optional[str] = None

        # Verify Environment Safety on Initialization
        permitted, reason = SafetyGuard.verify_live_execution_permitted()
        curr_env = SafetyGuard.get_current_environment()

        # If environment is configured as LIVE but SafetyGuard blocks it (e.g. LIVE_TRADING_ENABLED=false), activate circuit breaker
        if curr_env == ExecutionEnvironment.LIVE and not permitted:
            self.activate(f"SAFETY CIRCUIT BREAKER: {reason}")

    def activate(self, reason: str = "Manual kill switch triggered"):
        """Activate Kill Switch to halt signal and order execution."""
        self.is_active = True
        self.reason = reason
        self.activated_at = datetime.now(timezone.utc).isoformat()

    def deactivate(self, operator_override: bool = False):
        """Reset Kill Switch (Operator Override)."""
        permitted, reason = SafetyGuard.verify_live_execution_permitted()
        curr_env = SafetyGuard.get_current_environment()

        if curr_env == ExecutionEnvironment.LIVE and not permitted and not operator_override:
            raise PermissionError("Cannot deactivate Kill Switch while real-money trading is not fully authorized!")

        self.is_active = False
        self.reason = None
        self.activated_at = None

    def get_status(self) -> Dict[str, Any]:
        """Return Kill Switch state."""
        return {
            "kill_switch_active": self.is_active,
            "status": "HALTED" if self.is_active else "OPERATIONAL",
            "reason": self.reason,
            "activated_at": self.activated_at,
            "trading_env": SafetyGuard.get_current_environment().value,
            "live_trading_enabled": SafetyGuard.is_live_flag_set()
        }
