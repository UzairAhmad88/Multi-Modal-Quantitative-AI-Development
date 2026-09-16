"""
Persistent Research Memory for Quantitative Knowledge Retention.
Stores hypotheses, completed findings, and failed research attempts to prevent duplicate testing.
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class ResearchMemory:
    """Persistent storage for quantitative research memory and findings."""

    def __init__(self, memory_file: str = "artifacts/research_memory.json"):
        self.memory_path = Path(memory_file)
        self.memory_path.parent.mkdir(parents=True, exist_ok=True)
        self._data = self._load()

    def _load(self) -> Dict[str, Any]:
        if self.memory_path.exists():
            try:
                with open(self.memory_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Failed to load research memory: {e}")
        return {
            "hypotheses": {},
            "findings": {},
            "failed_hypotheses": {},
            "anomalies": [],
            "updated_at": datetime.utcnow().isoformat()
        }

    def _save(self) -> None:
        self._data["updated_at"] = datetime.utcnow().isoformat()
        with open(self.memory_path, "w", encoding="utf-8") as f:
            json.dump(self._data, f, indent=2)

    def record_hypothesis(self, hypothesis_data: Dict[str, Any]) -> None:
        hyp_id = hypothesis_data.get("hypothesis_id")
        if hyp_id:
            self._data["hypotheses"][hyp_id] = hypothesis_data
            self._save()

    def record_finding(
        self,
        finding_id: str,
        hypothesis_id: str,
        experiment_id: str,
        observation: str,
        evidence_status: str,
        metrics: Dict[str, Any],
        limitations: List[str]
    ) -> None:
        entry = {
            "finding_id": finding_id,
            "hypothesis_id": hypothesis_id,
            "experiment_id": experiment_id,
            "observation": observation,
            "evidence_status": evidence_status,
            "metrics": metrics,
            "limitations": limitations,
            "recorded_at": datetime.utcnow().isoformat()
        }
        self._data["findings"][finding_id] = entry

        if "CONTRADICTED" in evidence_status or "INCONCLUSIVE" in evidence_status:
            self._data["failed_hypotheses"][hypothesis_id] = entry

        self._save()

    def get_all_findings(self) -> List[Dict[str, Any]]:
        return list(self._data["findings"].values())

    def get_failed_hypotheses(self) -> List[Dict[str, Any]]:
        return list(self._data["failed_hypotheses"].values())

    def search_memory(self, query: str) -> List[Dict[str, Any]]:
        """Searches memory for query term across hypotheses and findings."""
        q = query.lower()
        results = []
        for f in self._data["findings"].values():
            if q in f.get("observation", "").lower() or q in f.get("hypothesis_id", "").lower():
                results.append(f)
        for h in self._data["hypotheses"].values():
            if q in h.get("statement", "").lower() or q in h.get("independent_variable", "").lower():
                results.append(h)
        return results
