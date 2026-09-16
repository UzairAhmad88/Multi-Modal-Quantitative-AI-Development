"""
Hypothesis Manager: Handles research question, null hypothesis, and expected behavior.
"""

from dataclasses import dataclass, asdict
from typing import Dict, Any, Optional


@dataclass
class Hypothesis:
    research_question: str
    hypothesis: str
    expected_behavior: str
    null_hypothesis: str
    success_criteria: str
    limitations: str = "Subject to market regime changes and finite backtest history."

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class HypothesisManager:
    """Manages hypothesis creation and validation criteria."""

    def create_hypothesis(
        self,
        question: str,
        hypothesis: str,
        expected_behavior: str,
        null_hypothesis: str,
        success_criteria: str,
        limitations: Optional[str] = None
    ) -> Hypothesis:
        return Hypothesis(
            research_question=question,
            hypothesis=hypothesis,
            expected_behavior=expected_behavior,
            null_hypothesis=null_hypothesis,
            success_criteria=success_criteria,
            limitations=limitations or "Subject to finite sample boundaries."
        )
