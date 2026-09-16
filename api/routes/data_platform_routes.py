"""
REST API Routes for Quantitative Data Platform, Point-In-Time Queries, Feature Store & Lineage.
"""

from fastapi import APIRouter, HTTPException, Query, Body
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

from data_platform.manager import DataPlatformManager

router = APIRouter(prefix="/data", tags=["Quantitative Data Platform"])
mgr = DataPlatformManager()


class IngestionRequest(BaseModel):
    source: str = Field("market", description="Data source: market, news, or fundamentals")
    symbols: List[str] = Field(["AAPL", "MSFT"], description="Symbols to ingest")


class BuildDatasetRequest(BaseModel):
    name: str = Field("multimodal_daily", description="Dataset name")
    symbols: List[str] = Field(["AAPL", "MSFT", "NVDA"], description="Symbols")


class ComputeFeaturesRequest(BaseModel):
    symbols: List[str] = Field(["AAPL", "MSFT"], description="Symbols")
    feature_set: str = Field("technical_v1", description="Feature set name")


@router.get("/sources")
def get_data_sources() -> Dict[str, Any]:
    """Returns catalog of supported quantitative data sources."""
    return {
        "sources": [
            {"id": "market", "name": "Market OHLCV Prices", "frequency": "daily"},
            {"id": "news", "name": "FinBERT News Sentiment", "frequency": "intraday"},
            {"id": "fundamentals", "name": "SEC Statement Fundamentals", "frequency": "quarterly"}
        ]
    }


@router.get("/status")
def get_platform_status() -> Dict[str, Any]:
    """Returns operational status of Data Platform & Feature Store."""
    return {
        "status": "OPERATIONAL",
        "symbol_count": len(mgr.symbol_master.list_symbols()),
        "feature_count": len(mgr.feature_registry.list_features())
    }


@router.post("/ingest")
def ingest_data(req: IngestionRequest) -> Dict[str, Any]:
    """Executes data ingestion pipeline."""
    if req.source == "market":
        return mgr.ingest_market_data(req.symbols)
    elif req.source == "news":
        return mgr.ingest_news_data(req.symbols)
    elif req.source == "fundamentals":
        return mgr.ingest_fundamental_data(req.symbols)
    else:
        raise HTTPException(status_code=400, detail=f"Invalid data source: {req.source}")


@router.post("/validate")
def validate_dataset(dataset_id: str = Query(..., description="Dataset ID")) -> Dict[str, Any]:
    """Runs data quality validation on dataset."""
    import pandas as pd
    from pathlib import Path
    filepath = Path("data/datasets") / f"{dataset_id}.parquet"
    if not filepath.exists():
        raise HTTPException(status_code=404, detail="Dataset not found")
    df = pd.read_parquet(filepath)
    return mgr.quality_engine.validate_dataset(df, dataset_id=dataset_id)


@router.get("/datasets")
def list_datasets() -> Dict[str, Any]:
    """Lists constructed versioned datasets."""
    from pathlib import Path
    import json
    datasets_dir = Path("data/datasets")
    res = []
    if datasets_dir.exists():
        for meta_path in datasets_dir.glob("*_meta.json"):
            try:
                with open(meta_path, "r", encoding="utf-8") as f:
                    res.append(json.load(f))
            except Exception:
                pass
    return {"datasets": res, "total": len(res)}


@router.get("/datasets/{dataset_id}")
def get_dataset_metadata(dataset_id: str) -> Dict[str, Any]:
    """Gets metadata for specific dataset ID."""
    from pathlib import Path
    import json
    meta_path = Path("data/datasets") / f"{dataset_id}_meta.json"
    if not meta_path.exists():
        raise HTTPException(status_code=404, detail="Dataset ID not found")
    with open(meta_path, "r", encoding="utf-8") as f:
        return json.load(f)


@router.post("/datasets/build")
def build_dataset(req: BuildDatasetRequest) -> Dict[str, Any]:
    """Builds a new versioned, point-in-time aligned dataset."""
    res = mgr.build_versioned_dataset(req.symbols, dataset_name=req.name)
    if res.get("status") == "FAILED":
        raise HTTPException(status_code=500, detail=res.get("reason", "Dataset build failed"))
    return res


@router.get("/features")
def list_features() -> Dict[str, Any]:
    """Lists feature store registry catalog."""
    return {"features": mgr.feature_registry.list_features()}


@router.get("/features/{feature_id}")
def get_feature(feature_id: str) -> Dict[str, Any]:
    """Gets feature definition by ID."""
    feat = mgr.feature_registry.get_feature(feature_id)
    if not feat:
        raise HTTPException(status_code=404, detail="Feature not found")
    return feat


@router.post("/features/compute")
def compute_features(req: ComputeFeaturesRequest) -> Dict[str, Any]:
    """Computes features for given symbols."""
    mkt = mgr.normalizer.normalize_market(mgr.market_source.fetch(req.symbols, "2024-01-01", "2026-09-01"))
    feats = mgr.feature_engine.compute_features(mkt)
    return {
        "status": "SUCCESS",
        "symbols": req.symbols,
        "rows": len(feats),
        "columns": list(feats.columns)
    }


@router.get("/features/{feature_id}/lineage")
def get_feature_lineage(feature_id: str) -> Dict[str, Any]:
    """Gets feature lineage graph."""
    return mgr.lineage_tracer.get_lineage(feature_id)


@router.get("/quality/{dataset_id}")
def get_quality_report(dataset_id: str) -> Dict[str, Any]:
    """Gets quality report for dataset."""
    from pathlib import Path
    import json
    rep_path = Path("reports/data_quality") / f"quality_{dataset_id}.json"
    if not rep_path.exists():
        rep_path = Path("reports/data_quality/market_quality.json")
    if not rep_path.exists():
        raise HTTPException(status_code=404, detail="Quality report not found")
    with open(rep_path, "r", encoding="utf-8") as f:
        return json.load(f)


@router.get("/lineage/{id}")
def get_data_lineage(id: str) -> Dict[str, Any]:
    """Gets dataset or model data lineage DAG."""
    return mgr.lineage_tracer.get_lineage(id)
