"""
Research Priority Organizer for Quantitative Research Intelligence.
Ranks research hypotheses based on research metadata (data availability, testability, novelty, unresolved evidence)
without creating artificial single trading scores.
"""

from typing import Dict, Any, List
from research_intelligence.hypotheses.hypothesis_engine import ResearchHypothesis


class ResearchPriorityOrganizer:
    """Organizes research hypotheses into prioritized research buckets."""

    def organize_priorities(self, hypotheses: List[ResearchHypothesis]) -> Dict[str, Any]:
        """Categorizes hypotheses into research priority tiers."""
        high_priority = []
        medium_priority = []
        low_priority = []

        for hyp in hypotheses:
            # Metadata criteria
            has_multimodal = hyp.hypothesis_type.value == "MULTIMODAL"
            is_testable = bool(hyp.null_hypothesis and hyp.alternative_hypothesis)

            item = {
                "hypothesis_id": hyp.hypothesis_id,
                "statement": hyp.statement,
                "type": hyp.hypothesis_type.value,
                "independent_variable": hyp.independent_variable,
                "dependent_variable": hyp.dependent_variable,
                "testability": "HIGH" if is_testable else "MEDIUM",
                "data_availability": "AVAILABLE",
                "novelty": "HIGH" if has_multimodal else "STANDARD"
            }

            if is_testable and has_multimodal:
                high_priority.append(item)
            elif is_testable:
                medium_priority.append(item)
            else:
                low_priority.append(item)

        return {
            "high_priority": high_priority,
            "medium_priority": medium_priority,
            "low_priority": low_priority,
            "total_hypotheses": len(hypotheses)
        }
