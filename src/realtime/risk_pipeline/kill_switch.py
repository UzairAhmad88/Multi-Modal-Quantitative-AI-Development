"""
Trading Kill Switch Module
Provides circuit breaker protection. Default state is PAPER TRADING ONLY.
Safely halts order generation and rebalancing upon risk or system breach.
"""

from datetime import datetime, timezone
import os
from typing import Dict, Any, Optional


class TradingKillSwitch:
    """Quantitative Trading Kill Switch & Safety Circuit Breaker."""

    def __init__(self, mode_env_var: str = "TRADING_MODE"):
        self.mode_env_var = mode_env_var
        self.is_active: bool = False
        self.reason: Optional[str] = None
        self.activated_at: Optional[str] = None

        # Verify Environment Safety
        trading_mode = os.getenv(self.mode_env_var, "paper").lower()
        if trading_mode != "paper":
            self.activate(f"CRITICAL SAFETY BREACH: {self.mode_env_var} is '{trading_mode}'. REAL-MONEY TRADING IS STRICTLY FORBIDDEN.")

    def activate(self, reason: str = "Manual kill switch triggered"):
        """Activate Kill Switch to halt signal and order execution."""
        self.is_active = True
        self.reason = reason
        self.activated_at = datetime.now(timezone.utc).isoformat()

    def deactivate(self):
        """Reset Kill Switch (Operator Override)."""
        trading_mode = os.getenv(self.mode_env_var, "paper").lower()
        if trading_mode != "paper":
            raise PermissionError("Cannot deactivate Kill Switch when real-money trading is configured!")
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
            "trading_mode": os.getenv(self.mode_env_var, "paper")
        }
