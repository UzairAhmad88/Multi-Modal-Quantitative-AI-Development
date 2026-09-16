"""
Hypothesis Types Definition for Quantitative Research Intelligence.
"""

from enum import Enum


class HypothesisType(str, Enum):
    DESCRIPTIVE = "DESCRIPTIVE"
    CORRELATIONAL = "CORRELATIONAL"
    PREDICTIVE = "PREDICTIVE"
    COMPARATIVE = "COMPARATIVE"
    EVENT_BASED = "EVENT_BASED"
    REGIME_BASED = "REGIME_BASED"
    MULTIMODAL = "MULTIMODAL"
