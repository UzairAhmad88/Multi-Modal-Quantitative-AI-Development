"""
Model comparison sub-module initialization.
"""

from research_evaluation.model_comparison.ic_analyzer import ICAnalyzer
from research_evaluation.model_comparison.ablation_engine import AblationEngine
from research_evaluation.model_comparison.strategy_comparison import StrategyComparisonEngine

__all__ = ["ICAnalyzer", "AblationEngine", "StrategyComparisonEngine"]
