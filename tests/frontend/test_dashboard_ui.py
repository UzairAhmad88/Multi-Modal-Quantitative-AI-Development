"""
Integration Test Suite for Quant Research Workstation Backend & UI Integration (Phase 12).
"""

import pytest
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "HEALTHY"


def test_market_data_endpoint():
    response = client.get("/market/AAPL")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["ticker"] == "AAPL"


def test_signals_and_lineage_endpoint():
    response = client.get("/signals")
    assert response.status_code == 200
    signals = response.json()
    assert "signals" in signals

    lineage_res = client.get("/research/signals/SIG-001/lineage")
    assert lineage_res.status_code == 200
    lineage_data = lineage_res.json()
    assert "lineage_chain" in lineage_data
    assert len(lineage_data["lineage_chain"]) >= 5


def test_feature_registry_endpoint():
    response = client.get("/research/features")
    assert response.status_code == 200
    data = response.json()
    assert data["total_features"] == 247
    assert len(data["feature_groups"]) >= 4


def test_paper_trading_session_endpoint():
    response = client.get("/research/paper-trading/session")
    assert response.status_code == 200
    data = response.json()
    assert data["paper_trading_only"] is True
    assert data["real_money_trading_enabled"] is False


def test_data_health_endpoint():
    response = client.get("/research/data/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "HEALTHY"
    assert len(data["providers"]) >= 3


def test_reports_endpoints():
    response = client.get("/research/reports")
    assert response.status_code == 200
    reports = response.json()
    assert isinstance(reports, list)

    if reports:
        filename = reports[0]["filename"]
        content_res = client.get(f"/research/reports/{filename}")
        assert content_res.status_code == 200
        assert "content" in content_res.json()
