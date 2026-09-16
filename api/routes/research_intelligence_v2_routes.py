"""
API Router for Phase 15 Quant Research Intelligence & Pattern Discovery.
Exposes endpoints for pattern discovery, hypothesis creation, research graph queries, evidence, and natural language assistant.
"""

from __future__ import annotations
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from research_intelligence.engine import ResearchIntelligenceEngine
from research_intelligence.hypotheses.hypothesis_types import HypothesisType

router = APIRouter(prefix="/research-intelligence", tags=["Research Intelligence OS"])
engine = ResearchIntelligenceEngine()


class CreateHypothesisRequest(BaseModel):
    statement: str = Field(..., example="News sentiment is associated with next-period returns.")
    hypothesis_type: str = Field("MULTIMODAL", example="MULTIMODAL")
    independent_variable: str = Field(..., example="news_sentiment")
    dependent_variable: str = Field(..., example="returns")
    null_hypothesis: Optional[str] = Field(default=None, example="No measurable relationship exists.")
    alternative_hypothesis: Optional[str] = Field(default=None, example="A statistically significant relationship exists.")


class NaturalLanguageQueryRequest(BaseModel):
    query: str = Field(..., example="Show experiments involving news sentiment.")


@router.post("/discover", response_model=Dict[str, Any])
def run_pattern_discovery():
    res = engine.discover_and_hypothesize()
    return {"status": "success", "discovery": res}


@router.get("/patterns", response_model=Dict[str, Any])
def list_patterns():
    res = engine.discover_and_hypothesize()
    return {"status": "success", "patterns": res.get("patterns", [])}


@router.get("/hypotheses", response_model=Dict[str, Any])
def list_hypotheses():
    hyps = engine.hypothesis_engine.list_hypotheses()
    return {
        "status": "success",
        "count": len(hyps),
        "hypotheses": [h.to_dict() for h in hyps]
    }


@router.post("/hypotheses", response_model=Dict[str, Any])
def create_hypothesis(req: CreateHypothesisRequest):
    try:
        htype = HypothesisType(req.hypothesis_type)
    except ValueError:
        htype = HypothesisType.MULTIMODAL

    hyp = engine.hypothesis_engine.create_hypothesis(
        statement=req.statement,
        hypothesis_type=htype,
        independent_variable=req.independent_variable,
        dependent_variable=req.dependent_variable,
        null_hypothesis=req.null_hypothesis or "",
        alternative_hypothesis=req.alternative_hypothesis or ""
    )
    return {"status": "success", "hypothesis": hyp.to_dict()}


@router.get("/hypotheses/{id}", response_model=Dict[str, Any])
def get_hypothesis_details(id: str):
    hyp = engine.hypothesis_engine.get_hypothesis(id)
    if not hyp:
        raise HTTPException(status_code=404, detail=f"Hypothesis '{id}' not found.")
    return {"status": "success", "hypothesis": hyp.to_dict()}


@router.post("/hypotheses/{id}/experiment", response_model=Dict[str, Any])
def generate_experiment_from_hypothesis(id: str, model_type: str = "multimodal"):
    try:
        res = engine.generate_experiment_for_hypothesis(hypothesis_id=id, model_type=model_type)
        return {"status": "success", "experiment_generation": res}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/findings", response_model=Dict[str, Any])
def list_findings():
    findings = engine.memory.get_all_findings()
    return {"status": "success", "count": len(findings), "findings": findings}


@router.get("/findings/{id}", response_model=Dict[str, Any])
def get_finding_details(id: str):
    findings = engine.memory.get_all_findings()
    matching = [f for f in findings if f.get("finding_id") == id or f.get("experiment_id") == id]
    if not matching:
        raise HTTPException(status_code=404, detail=f"Finding '{id}' not found.")
    return {"status": "success", "finding": matching[0]}


@router.get("/questions", response_model=Dict[str, Any])
def list_research_questions():
    res = engine.discover_and_hypothesize()
    return {"status": "success", "questions": res.get("anomalies", [])}


@router.get("/similar/{id}", response_model=Dict[str, Any])
def find_similar_experiments_endpoint(id: str):
    dummy_config = {"model": {"type": "multimodal"}, "data": {"symbols": ["AAPL", "MSFT"]}}
    similar = engine.similarity_engine.find_similar_experiments(dummy_config)
    return {"status": "success", "target_id": id, "similar_experiments": similar}


@router.get("/graph", response_model=Dict[str, Any])
def get_research_graph():
    return {"status": "success", "graph": engine.graph.to_dict()}


@router.post("/query", response_model=Dict[str, Any])
def natural_language_query(req: NaturalLanguageQueryRequest):
    res = engine.assistant.query(req.query)
    return {"status": "success", "result": res}
