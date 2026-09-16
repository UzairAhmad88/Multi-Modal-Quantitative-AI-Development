"""
Research Knowledge Base: Indexes findings, research notes, lessons from failed experiments, and search queries.
"""

from typing import Dict, Any, List, Optional
from research_lab.knowledge_base.findings import Finding


class ResearchKnowledgeBase:
    """Knowledge Base for indexing research discoveries and notes."""

    def __init__(self):
        self.findings: Dict[str, Finding] = {}
        self.notes: List[Dict[str, Any]] = []

    def add_finding(self, finding: Finding) -> Finding:
        self.findings[finding.finding_id] = finding
        return finding

    def add_note(self, experiment_id: str, note_text: str, author: str = "Quant Researcher"):
        entry = {"experiment_id": experiment_id, "note": note_text, "author": author}
        self.notes.append(entry)
        return entry

    def search_knowledge(self, query: str) -> List[Dict[str, Any]]:
        """Searches findings and notes for matching keywords."""
        q = query.lower()
        results = []
        for f in self.findings.values():
            if q in f.statement.lower() or q in f.experiment_id.lower():
                results.append({"type": "FINDING", "data": f.to_dict()})
        for n in self.notes:
            if q in n["note"].lower() or q in n["experiment_id"].lower():
                results.append({"type": "NOTE", "data": n})
        return results
