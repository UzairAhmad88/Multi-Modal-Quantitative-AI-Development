"""
Base Position Sizer Interface for Portfolio Construction OS.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import numpy as np


class BasePositionSizer(ABC):
    """Abstract Base Class for Position Sizing Algorithms."""

    @abstractmethod
    def calculate_weights(
        self,
        alpha_scores: Dict[str, float],
        volatilities: Optional[Dict[str, float]] = None,
        confidence_scores: Optional[Dict[str, float]] = None,
        target_volatility: Optional[float] = None,
    ) -> Dict[str, float]:
        """Calculate unconstrained raw position weights."""
        pass
