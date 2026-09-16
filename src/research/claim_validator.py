"""
Research Claim Validator Module
Audits text in research reports and code comments for prohibited promotional financial claims.
"""

from typing import Dict, List, Any


class ResearchClaimValidator:
    """Quantitative Academic Research Claim Auditor."""

    PROHIBITED_TERMS = [
        "guaranteed return",
        "guaranteed profit",
        "risk-free",
        "risk free",
        "certain prediction",
        "100% win rate",
        "foolproof strategy",
        "optimal prediction",
        "always profitable"
    ]

    def audit_text(self, text: str) -> Dict[str, Any]:
        """
        Scan text for forbidden financial claims.
        """
        violations = []
        text_lower = text.lower()

        for term in self.PROHIBITED_TERMS:
            if term in text_lower:
                violations.append(f"Prohibited promotional claim found: '{term}'")

        is_valid = len(violations) == 0
        return {
            "is_compliant": is_valid,
            "status": "COMPLIANT" if is_valid else "NON_COMPLIANT",
            "violations": violations
        }
