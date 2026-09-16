"""
Multi-Faceted Structured & Semantic Knowledge Search Engine.
"""

from typing import List, Dict, Any, Optional
from knowledge.schemas.knowledge_record import ResearchKnowledgeRecord
from knowledge.repository.knowledge_repository import KnowledgeRepository
from knowledge.embeddings.embedding_provider import EmbeddingProvider


class KnowledgeSearchEngine:
    """
    Search Engine supporting structured filters and semantic similarity queries over experiment memory.
    """

    def __init__(self, repo: KnowledgeRepository = None):
        self.repo = repo or KnowledgeRepository()
        self.embedding_provider = EmbeddingProvider()

    def search(
        self,
        query: Optional[str] = None,
        model: Optional[str] = None,
        modality: Optional[str] = None,
        dataset: Optional[str] = None,
        status: Optional[str] = None,
        min_sharpe: Optional[float] = None,
        max_drawdown: Optional[float] = None,
    ) -> List[Dict[str, Any]]:
        records = self.repo.list_records()
        filtered: List[ResearchKnowledgeRecord] = []

        for r in records:
            if model and model.lower() not in r.model_id.lower():
                continue
            if modality and not any(modality.lower() in m.lower() for m in r.modalities):
                continue
            if dataset and dataset.lower() not in r.dataset_id.lower():
                continue
            if status and status.upper() != r.status.upper():
                continue
            if min_sharpe is not None and r.metrics.get("sharpe_ratio", 0.0) < min_sharpe:
                continue
            if max_drawdown is not None and r.risk_metrics.get("max_drawdown", 0.0) > max_drawdown:
                continue

            filtered.append(r)

        if not filtered:
            return []

        results = []
        if query and query.strip():
            doc_texts = [
                f"{r.experiment_id} {r.research_question} {r.hypothesis} {r.model_id} {' '.join(r.modalities)}"
                for r in filtered
            ]
            similarities = self.embedding_provider.compute_similarity(query, doc_texts)
            for r, sim in zip(filtered, similarities):
                rec_dict = r.model_dump()
                rec_dict["relevance_score"] = sim
                results.append(rec_dict)
            results.sort(key=lambda x: x["relevance_score"], reverse=True)
        else:
            for r in filtered:
                rec_dict = r.model_dump()
                rec_dict["relevance_score"] = 1.0
                results.append(rec_dict)

        return results
