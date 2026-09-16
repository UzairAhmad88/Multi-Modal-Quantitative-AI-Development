"""
Research Summary Engine & Factual Evidence Summarizer.
"""

import numpy as np
from typing import Dict, Any, List, Optional
from knowledge.schemas.knowledge_record import ResearchKnowledgeRecord
from knowledge.repository.knowledge_repository import KnowledgeRepository


class ResearchSummaryEngine:
    """
    Computes factual evidence summaries and metric group statistics.
    Strictly avoids subjective investment recommendations.
    """

    def __init__(self, repo: KnowledgeRepository = None):
        self.repo = repo or KnowledgeRepository()

    def generate_summary(self) -> Dict[str, Any]:
        records = self.repo.list_records()

        total = len(records)
        completed = sum(1 for r in records if r.status.upper() == "COMPLETED")
        failed = sum(1 for r in records if r.status.upper() == "FAILED")

        sharpes = [r.metrics.get("sharpe_ratio") for r in records if r.metrics.get("sharpe_ratio") is not None]

        sharpe_stats = {}
        if sharpes:
            sharpe_stats = {
                "count": len(sharpes),
                "mean": round(float(np.mean(sharpes)), 4),
                "median": round(float(np.median(sharpes)), 4),
                "std": round(float(np.std(sharpes)), 4),
                "min": round(float(np.min(sharpes)), 4),
                "max": round(float(np.max(sharpes)), 4),
            }

        # Model breakdown
        model_counts = {}
        for r in records:
            model_counts[r.model_id] = model_counts.get(r.model_id, 0) + 1

        return {
            "total_experiments": total,
            "completed_experiments": completed,
            "failed_experiments": failed,
            "sharpe_ratio_statistics": sharpe_stats,
            "model_breakdown": model_counts,
            "claims_count": len(self.repo.list_claims()),
            "journal_entries_count": len(self.repo.list_journal_entries()),
        }
