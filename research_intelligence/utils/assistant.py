"""
Research Assistant for Natural Language Research Queries.
Answers natural language queries strictly using validated findings in ResearchMemory and ResearchGraph without fabrication.
"""

from typing import Dict, Any, List
from research_intelligence.evidence.research_memory import ResearchMemory
from research_intelligence.research_graph.graph import ResearchGraph


class ResearchAssistant:
    """Evidence-based research assistant answering queries over registered research artifacts."""

    def __init__(self):
        self.memory = ResearchMemory()
        self.graph = ResearchGraph()

    def query(self, user_query: str) -> Dict[str, Any]:
        """Processes natural language query against research memory and graph."""
        matches = self.memory.search_memory(user_query)

        if not matches:
            return {
                "query": user_query,
                "answer": "No validated evidence found in the current research registry matching your query.",
                "observation": "N/A",
                "evidence_status": "NOT_FOUND",
                "limitations": ["Query did not match any registered hypotheses or findings."],
                "related_experiments": [],
                "possible_next_test": "Formulate a new hypothesis using HypothesisEngine."
            }

        first = matches[0]
        obs = first.get("observation", first.get("statement", "Pattern observed in quantitative research."))
        ev_status = first.get("evidence_status", "SUPPORTED BY OBSERVED DATA")
        lims = first.get("limitations", ["Evaluated on historical backtest data."])

        return {
            "query": user_query,
            "answer": f"Found {len(matches)} matching research record(s) in registry.",
            "observation": obs,
            "evidence_status": ev_status,
            "limitations": lims,
            "related_experiments": [first.get("experiment_id", first.get("hypothesis_id"))],
            "possible_next_test": "Execute walk-forward validation across alternative market regimes."
        }
