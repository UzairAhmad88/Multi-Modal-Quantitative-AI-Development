import pandas as pd
from src.risk.drawdown import max_drawdown
from src.risk.var import historical_var

def test_drawdown():
    assert round(max_drawdown(pd.Series([100, 110, 99])), 2) == -0.10

def test_var():
    assert historical_var(pd.Series([-0.10, -0.05, 0.01, 0.02, 0.03]), 0.95) >= 0
