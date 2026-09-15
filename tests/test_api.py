import pytest
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "HEALTHY"
    assert "version" in data

def test_get_market_data_api():
    response = client.get("/market/AAPL")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["ticker"] == "AAPL"

def test_get_news_data_api():
    response = client.get("/news/AAPL")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"

def test_get_fundamentals_api():
    response = client.get("/fundamentals/AAPL")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"

def test_predict_api():
    response = client.post("/predict", json={"ticker": "AAPL", "horizon": "5D"})
    assert response.status_code == 200
    data = response.json()
    assert data["signal"] == "BUY"

def test_multimodal_predict_api():
    response = client.post("/multimodal/predict", json={"ticker": "AAPL", "horizon": "5D"})
    assert response.status_code == 200
    data = response.json()
    assert "modal_breakdown" in data

def test_signals_api():
    response = client.get("/signals")
    assert response.status_code == 200
    data = response.json()
    assert len(data["signals"]) > 0

def test_portfolio_api():
    response = client.get("/portfolio")
    assert response.status_code == 200
    data = response.json()
    assert data["portfolio_value"] > 0

def test_risk_api():
    response = client.get("/risk")
    assert response.status_code == 200
    data = response.json()
    assert "sharpe_ratio" in data

def test_backtest_api():
    response = client.post("/backtest", json={"ticker": "AAPL", "initial_capital": 100000.0})
    assert response.status_code == 200
    data = response.json()
    assert "cagr" in data
