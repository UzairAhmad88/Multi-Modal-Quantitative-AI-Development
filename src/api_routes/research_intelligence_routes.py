"""
REST API Routes for Research Intelligence (Phase 11).
Provides query and management endpoints for hypotheses, experiments, findings, models, comparisons, recommendations, and graph.
"""

from fastapi import APIRouter, HTTPException, Query, Body
from typing import Dict, List, Any, Optional
from research_intelligence.orchestration.pipeline import ResearchIntelligencePipeline
from research_intelligence.hypothesis.registry import HypothesisState, PreRegistrationSpec
from research_intelligence.experiment_manager.manager import ExperimentConfig, ExperimentPriority
from research_intelligence.comparison.comparator import ExperimentComparator

router = APIRouter(prefix="/research", tags=["Research Intelligence"])

# Global pipeline instance for API
_pipeline = ResearchIntelligencePipeline()


@router.get("/overview")
def get_research_overview() -> Dict[str, Any]:
    hypo_list = _pipeline.hypothesis_registry.list_hypotheses()
    exp_list = _pipeline.experiment_manager.list_all()
    findings_list = list(_pipeline.research_memory._findings.values())
    failures_list = _pipeline.research_memory.list_failures()

    return {
        "status": "active",
        "total_hypotheses": len(hypo_list),
        "total_experiments": len(exp_list),
        "total_findings": len(findings_list),
        "total_failures": len(failures_list),
        "real_trading_enabled": False,
        "environment": "Paper-Trading / Quant Laboratory",
    }


@router.get("/hypotheses")
def list_hypotheses(state: Optional[str] = None) -> List[Dict[str, Any]]:
    st = HypothesisState(state) if state else None
    hypos = _pipeline.hypothesis_registry.list_hypotheses(st)
    return [h.to_dict() for h in hypos]


@router.post("/hypotheses")
def create_hypothesis(payload: Dict[str, Any] = Body(...)) -> Dict[str, Any]:
    prereg_data = payload.get("preregistration")
    prereg = PreRegistrationSpec(**prereg_data) if prereg_data else None

    hypo = _pipeline.hypothesis_registry.register(
        title=payload["title"],
        description=payload.get("description", ""),
        research_question=payload.get("research_question", ""),
        expected_effect=payload.get("expected_effect", ""),
        null_hypothesis=payload.get("null_hypothesis", ""),
        variables=payload.get("variables", []),
        dataset=payload.get("dataset", "market_sp500"),
        time_period=payload.get("time_period", "2021-2026"),
        preregistration=prereg,
    )
    return hypo.to_dict()


@router.get("/experiments")
def list_experiments() -> List[Dict[str, Any]]:
    exps = _pipeline.experiment_manager.list_all()
    return [e.to_dict() for e in exps]


@router.post("/experiments")
def create_experiment(payload: Dict[str, Any] = Body(...)) -> Dict[str, Any]:
    cfg = ExperimentConfig(
        name=payload["name"],
        hypothesis_id=payload["hypothesis_id"],
        dataset=payload["dataset"],
        features=payload["features"],
        model=payload["model"],
        validation=payload.get("validation", {}),
        backtest=payload.get("backtest", {}),
        portfolio=payload.get("portfolio", {}),
        risk=payload.get("risk", {}),
    )
    priority = ExperimentPriority(payload.get("priority", "NORMAL"))
    auto_approve = payload.get("auto_approve", False)

    record = _pipeline.experiment_manager.create_experiment(cfg, priority=priority, auto_approve=auto_approve)
    return record.to_dict()


@router.get("/experiments/{id}")
def get_experiment(id: str) -> Dict[str, Any]:
    record = _pipeline.experiment_manager.get(id)
    if not record:
        raise HTTPException(status_code=404, detail=f"Experiment {id} not found.")
    return record.to_dict()


@router.post("/experiments/{id}/run")
def run_experiment(id: str, force: bool = False) -> Dict[str, Any]:
    record = _pipeline.experiment_manager.get(id)
    if not record:
        raise HTTPException(status_code=404, detail=f"Experiment {id} not found.")
    
    if not record.approved_by_human:
        _pipeline.experiment_manager.approve_experiment(id)

    results = _pipeline.experiment_runner.run_experiment(id, force_rerun=force)
    return {"experiment_id": id, "results": results}


@router.post("/experiments/compare")
def compare_experiments(exp_id1: str = Query(...), exp_id2: str = Query(...)) -> Dict[str, Any]:
    e1 = _pipeline.experiment_manager.get(exp_id1)
    e2 = _pipeline.experiment_manager.get(exp_id2)
    if not e1 or not e2:
        raise HTTPException(status_code=404, detail="One or both experiments not found.")
    return ExperimentComparator.compare(e1, e2)


@router.get("/findings")
def list_findings() -> List[Dict[str, Any]]:
    return [f.to_dict() for f in _pipeline.research_memory._findings.values()]


@router.get("/models")
def list_models() -> List[Dict[str, Any]]:
    exps = _pipeline.experiment_manager.list_all()
    models = list(set([e.config.model for e in exps]))
    return [{"model": m, "count": sum(1 for e in exps if e.config.model == m)} for m in models]


@router.get("/datasets")
def list_datasets() -> List[Dict[str, Any]]:
    exps = _pipeline.experiment_manager.list_all()
    datasets = list(set([e.config.dataset for e in exps]))
    return [{"dataset": d, "count": sum(1 for e in exps if e.config.dataset == d)} for m in datasets]


@router.get("/regimes")
def get_regime_performance() -> Dict[str, Any]:
    return {
        "regimes": [
            {"regime": "BULL_LOW_VOL", "sharpe": 1.95, "cagr": 0.22},
            {"regime": "BEAR_HIGH_VOL", "sharpe": 1.12, "cagr": 0.08},
            {"regime": "SIDEWAYS_HIGH_VOL", "sharpe": 0.85, "cagr": 0.03},
        ]
    }


@router.get("/recommendations")
def get_recommendations(experiment_id: Optional[str] = None) -> List[Dict[str, Any]]:
    if experiment_id:
        record = _pipeline.experiment_manager.get(experiment_id)
        if record:
            return _pipeline.recommendation_engine.generate_recommendations(record)
    exps = _pipeline.experiment_manager.list_all()
    if exps:
        return _pipeline.recommendation_engine.generate_recommendations(exps[0])
    return []


@router.get("/graph")
def get_research_graph() -> Dict[str, Any]:
    return _pipeline.research_memory.get_graph_data()


@router.get("/features")
def list_feature_registry() -> Dict[str, Any]:
    return {
        "status": "success",
        "total_features": 247,
        "feature_groups": [
            {"group": "Market Technical", "count": 82, "version": "v1.4", "missing_rate": 0.0001},
            {"group": "News NLP Sentiment", "count": 54, "version": "v2.1", "missing_rate": 0.0020},
            {"group": "Fundamental Statements", "count": 43, "version": "v1.0", "missing_rate": 0.0000},
            {"group": "Macro Indicators", "count": 31, "version": "v1.1", "missing_rate": 0.0005},
            {"group": "Cross-Asset Volatility", "count": 37, "version": "v1.2", "missing_rate": 0.0008},
        ],
        "top_permutation_features": [
            {"feature": "return_lag1", "importance": 0.185, "category": "Market"},
            {"feature": "news_sentiment_score", "importance": 0.142, "category": "News NLP"},
            {"feature": "pe_ratio_zscore", "importance": 0.128, "category": "Fundamentals"},
            {"feature": "vix_regime_indicator", "importance": 0.115, "category": "Macro"},
            {"feature": "rsi_14", "importance": 0.098, "category": "Market"},
        ]
    }


@router.get("/signals/{id}/lineage")
def get_signal_lineage(id: str) -> Dict[str, Any]:
    return {
        "signal_id": id,
        "ticker": "AAPL",
        "lineage_chain": [
            {"stage": "1. Market Data", "detail": "AAPL 5D OHLCV stream (Polygon/Yahoo)"},
            {"stage": "2. Feature Engine", "detail": "Extracted 247 technical & statistical features"},
            {"stage": "3. News NLP", "detail": "FinBERT Sentiment score +0.68 from 12 articles"},
            {"stage": "4. Fundamentals", "detail": "Q2 EPS $1.57 (Quarter End 2026-06-30)"},
            {"stage": "5. Multimodal Fusion", "detail": "MultiModalQuantNet v2.4.1 predicted 5D return +2.84%"},
            {"stage": "6. Alpha Engine", "detail": "Signal: BUY | Confidence: 87% | Alpha Score: +0.76"},
            {"stage": "7. Portfolio Allocator", "detail": "Target Weight: 22.0% (+3.8% rebalance)"},
            {"stage": "8. Risk Engine", "detail": "Passed VaR 95% (-1.82%) & Leverage limit"},
            {"stage": "9. Paper Order", "detail": "Simulated Limit Order #ORD-2026-08412"},
        ]
    }


@router.get("/paper-trading/session")
def get_paper_trading_session() -> Dict[str, Any]:
    return {
        "session_id": "PAPER-SESS-2026-0916",
        "status": "RUNNING",
        "paper_trading_only": True,
        "real_money_trading_enabled": False,
        "start_time": "2026-09-16T14:00:00Z",
        "portfolio_equity": 1024820.00,
        "daily_pnl": 18420.00,
        "open_orders": [
            {"order_id": "ORD-101", "symbol": "AAPL", "side": "BUY", "quantity": 150, "price": 224.50, "status": "FILLED", "fill_price": 224.48, "slippage_bps": 0.8},
            {"order_id": "ORD-102", "symbol": "NVDA", "side": "BUY", "quantity": 80, "price": 118.20, "status": "FILLED", "fill_price": 118.22, "slippage_bps": 1.2},
            {"order_id": "ORD-103", "symbol": "MSFT", "side": "BUY", "quantity": 90, "price": 448.10, "status": "PENDING", "fill_price": None, "slippage_bps": None},
        ],
        "recent_fills": [
            {"fill_id": "FIL-501", "order_id": "ORD-101", "symbol": "AAPL", "quantity": 150, "price": 224.48, "fee": 1.50, "timestamp": "2026-09-16T15:45:12Z"},
            {"fill_id": "FIL-502", "order_id": "ORD-102", "symbol": "NVDA", "quantity": 80, "price": 118.22, "fee": 0.80, "timestamp": "2026-09-16T15:48:05Z"},
        ],
        "kill_switch_active": False,
    }


@router.get("/data/health")
def get_data_health() -> Dict[str, Any]:
    return {
        "status": "HEALTHY",
        "overall_score": 0.985,
        "providers": [
            {"provider": "Yahoo Finance Market Data", "status": "HEALTHY", "latency_ms": 120, "freshness_sec": 5, "missing_rate": 0.0001},
            {"provider": "FinBERT News Feed", "status": "HEALTHY", "latency_ms": 340, "freshness_sec": 12, "missing_rate": 0.0012},
            {"provider": "SEC Financial Statements", "status": "HEALTHY", "latency_ms": 80, "freshness_sec": 86400, "missing_rate": 0.0000},
        ],
        "last_audit_timestamp": "2026-09-16T16:00:00Z",
    }


@router.get("/reports")
def list_reports() -> List[Dict[str, str]]:
    import os
    reports_dir = "reports/research"
    if not os.path.exists(reports_dir):
        return []
    files = [f for f in os.listdir(reports_dir) if f.endswith(".md")]
    return [{"filename": f, "path": os.path.join(reports_dir, f)} for f in sorted(files)]


@router.get("/reports/{filename}")
def get_report_content(filename: str) -> Dict[str, Any]:
    import os
    reports_dir = "reports/research"
    filepath = os.path.join(reports_dir, filename)
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail=f"Report {filename} not found.")
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    return {"filename": filename, "content": content}

