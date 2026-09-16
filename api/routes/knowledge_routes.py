"""
REST API Routes for Phase 23 Quant Research Knowledge Base.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
import uuid

from knowledge.repository.knowledge_repository import KnowledgeRepository
from knowledge.search.search_engine import KnowledgeSearchEngine
from knowledge.comparison.comparison_engine import ExperimentComparisonEngine
from knowledge.lineage.lineage_service import ResearchLineageService
from knowledge.graph.knowledge_graph import ResearchKnowledgeGraph
from knowledge.summaries.summary_engine import ResearchSummaryEngine
from knowledge.schemas.knowledge_record import ResearchClaim, ResearchJournalEntry, ClaimStatus, JournalType
from knowledge.reports.report_generator import KnowledgeReportGenerator

router = APIRouter(prefix="/knowledge", tags=["Knowledge Base"])

repo = KnowledgeRepository()
search_engine = KnowledgeSearchEngine(repo=repo)
comp_engine = ExperimentComparisonEngine(repo=repo)
summary_engine = ResearchSummaryEngine(repo=repo)


class CreateClaimRequest(BaseModel):
    statement: str = "Adding news sentiment changed test-period Sharpe ratio"
    evidence_experiment_ids: List[str] = Field(default_factory=list)
    status: ClaimStatus = ClaimStatus.OBSERVED
    notes: Optional[str] = None


class CreateJournalRequest(BaseModel):
    experiment_id: Optional[str] = None
    entry_type: JournalType = JournalType.OBSERVATION
    content: str = "Observed increased turnover during high volatility periods."
    linked_artifacts: List[str] = Field(default_factory=list)


class CompareExperimentsRequest(BaseModel):
    experiment_a: str
    experiment_b: str


@router.get("/search")
def search_knowledge(
    query: Optional[str] = None,
    model: Optional[str] = None,
    modality: Optional[str] = None,
    dataset: Optional[str] = None,
    status: Optional[str] = None,
    min_sharpe: Optional[float] = None,
):
    return search_engine.search(
        query=query,
        model=model,
        modality=modality,
        dataset=dataset,
        status=status,
        min_sharpe=min_sharpe,
    )


@router.get("/experiments/{experiment_id}")
def get_experiment_record(experiment_id: str):
    rec = repo.get_record(experiment_id)
    if not rec:
        raise HTTPException(status_code=404, detail="Knowledge record not found")
    card = repo.get_reproducibility_card(experiment_id)
    return {
        "record": rec.model_dump(),
        "reproducibility_card": card.model_dump() if card else None,
    }


@router.get("/experiments/{experiment_id}/lineage")
def get_experiment_lineage(experiment_id: str):
    rec = repo.get_record(experiment_id)
    if not rec:
        raise HTTPException(status_code=404, detail="Knowledge record not found")
    return ResearchLineageService.get_experiment_lineage(rec)


@router.post("/compare")
def compare_experiments(req: CompareExperimentsRequest):
    try:
        res = comp_engine.compare_experiments(req.experiment_a, req.experiment_b)
        report_md = KnowledgeReportGenerator.generate_comparison_report_md(res)
        res["report_markdown"] = report_md
        return res
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/models")
def list_models():
    records = repo.list_records()
    models = sorted(list(set(r.model_id for r in records)))
    return {"models_count": len(models), "models": models}


@router.get("/features")
def list_features():
    records = repo.list_records()
    features = sorted(list(set(r.feature_set_id for r in records)))
    return {"features_count": len(features), "features": features}


@router.get("/datasets")
def list_datasets():
    records = repo.list_records()
    datasets = sorted(list(set(r.dataset_id for r in records)))
    return {"datasets_count": len(datasets), "datasets": datasets}


@router.get("/failures")
def list_failures():
    return search_engine.search(status="FAILED")


@router.get("/claims")
def list_claims():
    return [c.model_dump() for c in repo.list_claims()]


@router.post("/claims")
def create_claim(req: CreateClaimRequest):
    claim = ResearchClaim(
        claim_id=f"CLAIM-{uuid.uuid4().hex[:8].upper()}",
        statement=req.statement,
        evidence_experiment_ids=req.evidence_experiment_ids,
        status=req.status,
        notes=req.notes,
    )
    repo.save_claim(claim)
    return claim.model_dump()


@router.get("/journal")
def list_journal():
    return [j.model_dump() for j in repo.list_journal_entries()]


@router.post("/journal")
def create_journal_entry(req: CreateJournalRequest):
    entry = ResearchJournalEntry(
        journal_id=f"JRN-{uuid.uuid4().hex[:8].upper()}",
        experiment_id=req.experiment_id,
        entry_type=req.entry_type,
        content=req.content,
        linked_artifacts=req.linked_artifacts,
    )
    repo.save_journal_entry(entry)
    return entry.model_dump()


@router.get("/graph")
def get_knowledge_graph():
    records = repo.list_records()
    kg = ResearchKnowledgeGraph()
    kg.build_from_records(records)
    return kg.to_dict()


@router.get("/summary")
def get_summary():
    return summary_engine.generate_summary()


@router.get("/reproducibility/{experiment_id}")
def get_reproducibility_card(experiment_id: str):
    card = repo.get_reproducibility_card(experiment_id)
    if not card:
        raise HTTPException(status_code=404, detail="Reproducibility card not found")
    md = KnowledgeReportGenerator.generate_reproducibility_card_md(card)
    return {"card": card.model_dump(), "card_markdown": md}


@router.get("/health")
def knowledge_health():
    return {
        "status": "HEALTHY",
        "records_count": len(repo.list_records()),
        "claims_count": len(repo.list_claims()),
        "journal_count": len(repo.list_journal_entries()),
    }
