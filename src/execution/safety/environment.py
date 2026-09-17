"""
Execution Environment & Two-Key Live Enablement Safety Guard.
Enforces multi-stage environment isolation and explicit authorization checks.
"""

from enum import Enum
import os
from typing import Dict, Any, Tuple


class ExecutionEnvironment(str, Enum):
    BACKTEST = "BACKTEST"
    PAPER = "PAPER"
    SHADOW = "SHADOW"
    SANDBOX = "SANDBOX"
    LIVE = "LIVE"


class SafetyGuard:
    """
    Master Trading Safety Guard.
    Ensures REAL TRADING is NEVER enabled by default and requires two independent keys.
    """

    ENV_VAR_TRADING_ENV = "TRADING_ENV"
    ENV_VAR_LIVE_ENABLED = "LIVE_TRADING_ENABLED"

    @classmethod
    def get_current_environment(cls) -> ExecutionEnvironment:
        env_str = os.getenv(cls.ENV_VAR_TRADING_ENV, "PAPER").upper()
        try:
            return ExecutionEnvironment(env_str)
        except ValueError:
            return ExecutionEnvironment.PAPER

    @classmethod
    def is_live_flag_set(cls) -> bool:
        flag = os.getenv(cls.ENV_VAR_LIVE_ENABLED, "false").lower()
        return flag in ("true", "1", "yes")

    @classmethod
    def verify_live_execution_permitted(cls, confirmation_token: str = "") -> Tuple[bool, str]:
        """
        Evaluate Two-Key Condition:
        Key 1: TRADING_ENV == LIVE
        Key 2: LIVE_TRADING_ENABLED == true
        Optional: Valid confirmation token
        """
        current_env = cls.get_current_environment()
        live_flag = cls.is_live_flag_set()

        # Key 1 Check
        if current_env != ExecutionEnvironment.LIVE:
            return False, f"REAL BROKER EXECUTION BLOCKED: TRADING_ENV is '{current_env.value}' (Must be 'LIVE')."

        # Key 2 Check
        if not live_flag:
            return False, "REAL BROKER EXECUTION BLOCKED: LIVE_TRADING_ENABLED is false."

        return True, "LIVE TRADING AUTHORIZED: Both TRADING_ENV=LIVE and LIVE_TRADING_ENABLED=true are verified."

    @classmethod
    def get_safety_status(cls) -> Dict[str, Any]:
        curr_env = cls.get_current_environment()
        live_flag = cls.is_live_flag_set()
        permitted, reason = cls.verify_live_execution_permitted()

        return {
            "trading_env": curr_env.value,
            "live_trading_enabled": live_flag,
            "real_money_active": permitted,
            "safety_status": "LIVE_ACTIVE" if permitted else "REAL_MONEY_DISABLED",
            "reason": reason
        }
