"""
Order State Machine Module.
Defines valid order states and enforces strict state transition policies.
"""

from enum import Enum
from typing import Dict, Set, Tuple


class OrderState(str, Enum):
    CREATED = "CREATED"
    VALIDATING = "VALIDATING"
    APPROVED = "APPROVED"
    SUBMITTED = "SUBMITTED"
    ACKNOWLEDGED = "ACKNOWLEDGED"
    PARTIALLY_FILLED = "PARTIALLY_FILLED"
    FILLED = "FILLED"
    REJECTED = "REJECTED"
    CANCELLED = "CANCELLED"
    EXPIRED = "EXPIRED"
    FAILED = "FAILED"


class OrderStateMachine:
    """Enforces valid lifecycle state transitions for trading orders."""

    VALID_TRANSITIONS: Dict[OrderState, Set[OrderState]] = {
        OrderState.CREATED: {OrderState.VALIDATING, OrderState.REJECTED, OrderState.FAILED},
        OrderState.VALIDATING: {OrderState.APPROVED, OrderState.REJECTED, OrderState.FAILED},
        OrderState.APPROVED: {OrderState.SUBMITTED, OrderState.CANCELLED, OrderState.FAILED},
        OrderState.SUBMITTED: {OrderState.ACKNOWLEDGED, OrderState.REJECTED, OrderState.FAILED, OrderState.FILLED},
        OrderState.ACKNOWLEDGED: {OrderState.PARTIALLY_FILLED, OrderState.FILLED, OrderState.CANCELLED, OrderState.FAILED},
        OrderState.PARTIALLY_FILLED: {OrderState.PARTIALLY_FILLED, OrderState.FILLED, OrderState.CANCELLED, OrderState.FAILED},
        OrderState.FILLED: set(),
        OrderState.REJECTED: set(),
        OrderState.CANCELLED: set(),
        OrderState.EXPIRED: set(),
        OrderState.FAILED: set(),
    }

    @classmethod
    def can_transition(cls, current_state: OrderState, new_state: OrderState) -> bool:
        """Check if transition from current_state to new_state is authorized."""
        allowed = cls.VALID_TRANSITIONS.get(current_state, set())
        return new_state in allowed

    @classmethod
    def validate_transition(cls, current_state: OrderState, new_state: OrderState):
        """Raise ValueError if state transition is invalid."""
        if not cls.can_transition(current_state, new_state):
            raise ValueError(f"Invalid Order State Transition: '{current_state.value}' ➔ '{new_state.value}' is forbidden.")
