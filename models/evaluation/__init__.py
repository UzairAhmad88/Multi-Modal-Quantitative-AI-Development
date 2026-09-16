"""
Evaluation package for model evaluation, metrics calculation, and side-by-side model comparisons.
"""

from models.evaluation.evaluator import ModelEvaluator
from models.evaluation.comparison import ModelComparisonEngine

__all__ = ["ModelEvaluator", "ModelComparisonEngine"]
