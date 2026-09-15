import pandas as pd
import pytest
from src.features.technical import add_basic_technical_features
from src.features.price_features import forward_return

def test_basic_features():
    out = add_basic_technical_features(pd.DataFrame({"close": range(1, 101)}))
    assert "return_1d" in out
    assert "sma_20" in out

def test_forward_return():
    df = pd.DataFrame({"close": [100, 110, 120, 130, 140, 150]})
    assert forward_return(df, 2).iloc[0] == pytest.approx(0.2)
