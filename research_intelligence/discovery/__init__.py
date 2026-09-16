"""
Discovery package for quantitative market, news, fundamental, and cross-modal pattern discovery.
"""

from research_intelligence.discovery.pattern_discovery import PatternDiscoveryEngine
from research_intelligence.discovery.correlation_analyzer import CorrelationAnalyzer
from research_intelligence.discovery.lag_analyzer import LagAnalyzer
from research_intelligence.discovery.anomaly_detector import AnomalyDetectionEngine

__all__ = [
    "PatternDiscoveryEngine",
    "CorrelationAnalyzer",
    "LagAnalyzer",
    "AnomalyDetectionEngine",
]
