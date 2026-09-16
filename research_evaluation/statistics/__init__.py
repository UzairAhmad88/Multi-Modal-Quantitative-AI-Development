"""
Statistics sub-module initialization.
"""

from research_evaluation.statistics.significance import SignificanceTester
from research_evaluation.statistics.bootstrap import BootstrapEngine
from research_evaluation.statistics.permutation import PermutationTester
from research_evaluation.statistics.stationarity import StationarityTester
from research_evaluation.statistics.autocorrelation import AutocorrelationAnalyzer
from research_evaluation.statistics.distribution import DistributionAnalyzer

__all__ = [
    "SignificanceTester",
    "BootstrapEngine",
    "PermutationTester",
    "StationarityTester",
    "AutocorrelationAnalyzer",
    "DistributionAnalyzer"
]
