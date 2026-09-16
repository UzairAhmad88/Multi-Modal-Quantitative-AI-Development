"""
Unit & Integration Test Suite for Quantitative Data Platform, Point-in-Time Store, Feature Store & Dataset Lineage.
"""

import pytest
import pandas as pd
import numpy as np
import tempfile
from pathlib import Path

from data_platform.ingestion.data_source import MarketDataSource, NewsDataSource, FundamentalDataSource
from data_platform.raw.raw_store import RawDataStore
from data_platform.normalization.normalizer import DataNormalizer
from data_platform.quality.quality_engine import DataQualityEngine
from data_platform.point_in_time.pit_manager import PointInTimeManager
from data_platform.features.feature_engine import FeatureEngine
from data_platform.feature_store.registry import FeatureStoreRegistry
from data_platform.cache.feature_cache import FeatureCache
from data_platform.datasets.dataset_builder import DatasetBuilder
from data_platform.versioning.snapshot_manager import SnapshotManager
from data_platform.lineage.lineage_tracer import DataLineageTracer
from data_platform.manager import DataPlatformManager


@pytest.fixture
def sample_symbols():
    return ["AAPL", "MSFT"]


def test_data_sources_ingestion(sample_symbols):
    m_src = MarketDataSource()
    df_m = m_src.fetch(sample_symbols, "2024-01-01", "2024-03-01")
    assert not df_m.empty
    assert m_src.validate(df_m)
    df_m_norm = m_src.normalize(df_m)
    assert "date" in df_m_norm.columns

    n_src = NewsDataSource()
    df_n = n_src.fetch(sample_symbols, "2024-01-01", "2024-03-01")
    assert not df_n.empty
    assert n_src.validate(df_n)

    f_src = FundamentalDataSource()
    df_f = f_src.fetch(sample_symbols, "2024-01-01", "2024-03-01")
    assert not df_f.empty
    assert f_src.validate(df_f)


def test_raw_store_and_normalizer(sample_symbols):
    m_src = MarketDataSource()
    raw = m_src.fetch(sample_symbols, "2024-01-01", "2024-02-01")

    with tempfile.TemporaryDirectory() as tmp_dir:
        store = RawDataStore(raw_dir=tmp_dir)
        path = store.save_raw(raw, "market")
        assert Path(path).exists()
        loaded = store.load_latest_raw("market")
        assert len(loaded) == len(raw)

    norm = DataNormalizer.normalize_market(raw)
    assert norm["symbol"].iloc[0] in sample_symbols


def test_data_quality_engine():
    q_eng = DataQualityEngine(reports_dir="reports/data_quality")
    good_mkt = pd.DataFrame([
        {"date": "2024-01-01", "symbol": "AAPL", "open": 100, "high": 105, "low": 99, "close": 102, "volume": 1000},
        {"date": "2024-01-02", "symbol": "AAPL", "open": 102, "high": 106, "low": 101, "close": 105, "volume": 1200}
    ])
    res_good = q_eng.validate_market(good_mkt)
    assert res_good["status"] == "PASS"

    bad_mkt = pd.DataFrame([
        {"date": "2024-01-01", "symbol": "AAPL", "open": 100, "high": 90, "low": 99, "close": 102, "volume": 1000}  # high < low breach
    ])
    res_bad = q_eng.validate_market(bad_mkt)
    assert res_bad["status"] in ["WARNING", "FAIL"]


def test_point_in_time_leakage_protection():
    news_df = pd.DataFrame([
        {"symbol": "AAPL", "headline": "Early News", "published_at": "2024-01-01 09:00:00", "available_at": "2024-01-01 09:05:00"},
        {"symbol": "AAPL", "headline": "Late News", "published_at": "2024-01-01 10:00:00", "available_at": "2024-01-01 10:05:00"}
    ])

    avail_at_0930 = PointInTimeManager.get_available_news(news_df, "2024-01-01 09:30:00")
    assert len(avail_at_0930) == 1
    assert avail_at_0930.iloc[0]["headline"] == "Early News"

    fund_df = pd.DataFrame([
        {"symbol": "AAPL", "period_end": "2024-03-31", "announcement_date": "2024-04-15", "available_at": "2024-04-15 00:00:00", "eps": 2.5}
    ])
    avail_fund_march = PointInTimeManager.get_available_fundamentals(fund_df, "2024-04-01 00:00:00")
    assert len(avail_fund_march) == 0

    avail_fund_april = PointInTimeManager.get_available_fundamentals(fund_df, "2024-04-20 00:00:00")
    assert len(avail_fund_april) == 1


def test_feature_engine_and_registry(sample_symbols):
    m_src = MarketDataSource()
    mkt = m_src.fetch(sample_symbols, "2024-01-01", "2024-03-01")

    f_eng = FeatureEngine()
    feats = f_eng.compute_features(mkt)

    assert "RSI_14" in feats.columns or "rsi" in feats.columns
    assert "Volatility_20" in feats.columns

    with tempfile.TemporaryDirectory() as tmp_dir:
        reg_file = str(Path(tmp_dir) / "registry.json")
        reg = FeatureStoreRegistry(registry_file=reg_file)
        reg.register_feature("VOL_10", "Volatility 10D", "volatility", "std(returns, 10)", ["close"])
        assert reg.get_feature("VOL_10")["name"] == "Volatility 10D"


def test_feature_cache(sample_symbols):
    df = pd.DataFrame([{"symbol": "AAPL", "date": "2024-01-01", "RSI_14": 55.4}])
    with tempfile.TemporaryDirectory() as tmp_dir:
        cache = FeatureCache(cache_dir=tmp_dir)
        path = cache.put(df, "RSI_14", "AAPL", "2024-01-01", "2024-01-10")
        assert Path(path).exists()
        cached = cache.get("RSI_14", "AAPL", "2024-01-01", "2024-01-10")
        assert cached is not None
        assert cached.iloc[0]["RSI_14"] == 55.4


def test_dataset_builder_and_snapshots(sample_symbols):
    m_src = MarketDataSource()
    mkt = m_src.fetch(sample_symbols, "2024-01-01", "2024-04-01")

    with tempfile.TemporaryDirectory() as tmp_dir:
        builder = DatasetBuilder(datasets_dir=tmp_dir)
        res = builder.build_dataset(mkt, config={"name": "test_ds"})
        assert res["status"] == "SUCCESS"
        assert "dataset_id" in res
        assert Path(res["file_path"]).exists()

        df_loaded = pd.read_parquet(res["file_path"])
        train_df, val_df, test_df = builder.split_dataset(df_loaded)
        assert len(train_df) + len(val_df) + len(test_df) == len(df_loaded)


def test_data_lineage_tracer():
    with tempfile.TemporaryDirectory() as tmp_dir:
        lineage_file = str(Path(tmp_dir) / "lineage.json")
        tracer = DataLineageTracer(lineage_file=lineage_file)
        tracer.record_node("RAW_AAPL", "RAW_MARKET", {"symbol": "AAPL"})
        tracer.record_node("DS_001", "DATASET", {"name": "test"})
        tracer.record_edge("RAW_AAPL", "DS_001", "CONSTRUCTED_FROM")

        lin = tracer.get_lineage("DS_001")
        assert len(lin["parents"]) == 1
        assert lin["parents"][0]["id"] == "RAW_AAPL"


def test_data_platform_manager(sample_symbols):
    mgr = DataPlatformManager()
    ing_res = mgr.ingest_market_data(sample_symbols, "2024-01-01", "2024-02-01")
    assert ing_res["status"] == "SUCCESS"

    pit_res = mgr.get_point_in_time_data("AAPL", "2024-01-15 10:00:00")
    assert pit_res["symbol"] == "AAPL"

    ds_res = mgr.build_versioned_dataset(sample_symbols, dataset_name="e2e_test")
    assert ds_res["status"] == "SUCCESS"
