"""
Reports sub-module initialization.
"""

from research_evaluation.reports.research_report import ResearchReportGenerator
from research_evaluation.reports.html_report import HTMLReportGenerator

__all__ = ["ResearchReportGenerator", "HTMLReportGenerator"]
