import pandas as pd
import numpy as np
from src.alpha.prediction import normalize_alpha
from src.alpha.signal_generator import generate_signal, AlphaEngine
from src.portfolio.allocator import equal_weight, alpha_weighted, volatility_adjusted, risk_parity
from src.portfolio.position_sizing import PositionSizer
from src.risk.risk_manager import RiskEngine

def test_alpha_engine():
    alpha = normalize_alpha(0.04, scale=0.05)
    assert 0.0 < alpha < 1.0

    eng = AlphaEngine(buy_threshold=0.50, sell_threshold=-0.50)
    res = eng.process_predictions({"xgb": 0.04, "lstm": 0.03})
    assert res["signal"] == "BUY"
    assert res["confidence_level"] in ["HIGH", "MEDIUM", "LOW"]

def test_portfolio_allocator():
    alphas = pd.Series([0.8, 0.4, 0.0], index=["AAPL", "MSFT", "NVDA"])
    w_alpha = alpha_weighted(alphas, max_position=0.50)
    assert abs(w_alpha.sum() - 1.0) < 1e-5

    w_eq = equal_weight(["AAPL", "MSFT", "NVDA"])
    assert (w_eq == 1.0 / 3.0).all()

def test_risk_gate():
    proposed = pd.Series([0.50, 0.50], index=["AAPL", "MSFT"])  # Exceeds max position 0.25
    engine = RiskEngine(max_position=0.25, max_sector_exposure=0.40)

    sector_map = {"AAPL": "Tech", "MSFT": "Tech"}
    gated, report = engine.validate_and_gate_portfolio(proposed, sector_map=sector_map)

    assert report["status"] == "MODIFIED_BY_RISK_GATE"
    assert (gated.abs() <= 0.25 + 1e-5).all()
    assert report["max_position_actual"] <= 0.25
