"""
Multi-Modal Quant AI - Research Engine
Modular research package for factor analysis, explainability, robustness, stress testing,
uncertainty estimation, error analysis, attribution, and statistical testing.
"""

from src.research.factor_analysis import FactorAnalyzer
from src.research.explainability import ModelExplainer
from src.research.robustness import RobustnessTester
from src.research.stress_testing import StressTester
from src.research.uncertainty import UncertaintyAnalyzer
from src.research.error_analysis import ErrorAnalyzer
from src.research.attribution import PortfolioAttributor
from src.research.statistical_tests import StatisticalTester
from src.research.runner import ResearchRunner

__all__ = [
    "FactorAnalyzer",
    "ModelExplainer",
    "RobustnessTester",
    "StressTester",
    "UncertaintyAnalyzer",
    "ErrorAnalyzer",
    "PortfolioAttributor",
    "StatisticalTester",
    "ResearchRunner",
]
