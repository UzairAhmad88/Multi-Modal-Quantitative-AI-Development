"""
Research Question Generator for Next-Horizon Investigation.
Formulates structured research follow-up prompts after experiment completion.
"""

from typing import Dict, Any, List


class PromptGenerator:
    """Generates follow-up research questions based on completed experiment evidence."""

    @staticmethod
    def generate_follow_up_questions(
        hypothesis_statement: str,
        evidence_status: str,
        metrics: Dict[str, Any]
    ) -> List[str]:
        """Generates standard follow-up research prompts."""
        questions = [
            "Does the observed relationship hold in another market regime (e.g. high volatility / market stress)?",
            "Does performance survive higher transaction costs (e.g., 20 bps commission + 10 bps slippage)?",
            "Does removing the news sentiment modality materially change the signal directional accuracy?",
            "Does the model generalize to unseen asset classes (e.g., small-cap equities, commodities)?"
        ]
        if "CONTRADICTED" in evidence_status or "INCONCLUSIVE" in evidence_status:
            questions.append("Would adjusting the lookback window or lag horizon resolve the statistical insignificance?")

        return questions
