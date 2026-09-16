"""
Base Constraint Interface for Portfolio Construction OS.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Tuple, Optional
import numpy as np


class BaseConstraint(ABC):
    """Abstract Base Class for Portfolio Optimization Constraints."""

    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def validate(
        self,
        weights: Dict[str, float],
        current_weights: Optional[Dict[str, float]] = None,
        asset_metadata: Optional[Dict[str, Dict[str, Any]]] = None,
    ) -> Tuple[bool, str]:
        """Validate if target weights satisfy this constraint."""
        pass
