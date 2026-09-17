"""
Trading Safety & Environment Security Package.
Provides multi-environment safety guards, dual-key live enablement checks, and confirmation tokens.
"""

from src.execution.safety.environment import ExecutionEnvironment, SafetyGuard
from src.execution.safety.live_confirmation import LiveConfirmationManager

__all__ = ["ExecutionEnvironment", "SafetyGuard", "LiveConfirmationManager"]
