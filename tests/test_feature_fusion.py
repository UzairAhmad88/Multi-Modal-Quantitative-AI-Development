import pandas as pd
from src.data.market_loader import generate_demo_market_data
from src.data.news_loader import generate_demo_news
from src.data.fundamental_loader import generate_demo_fundamentals
from src.data.data_synchronizer import align_modalities
from src.features.feature_fusion import FeatureBuilder, FeatureValidator, FeatureManifest

def test_data_synchronizer():
    market = generate_demo_market_data("AAPL", "2023-01-01", "2023-06-01")
    news = generate_demo_news(["AAPL"], "2023-01-01", "2023-06-01")
    fund = generate_demo_fundamentals(["AAPL"], 2023, 2023)

    aligned = align_modalities(market, news, fund)
    assert not aligned.empty
    assert len(aligned) == len(market)
    assert "ticker" in aligned.columns

def test_feature_builder():
    market = generate_demo_market_data("AAPL", "2023-01-01", "2023-12-31")
    news = generate_demo_news(["AAPL"], "2023-01-01", "2023-12-31")
    fund = generate_demo_fundamentals(["AAPL"], 2022, 2023)

    builder = FeatureBuilder()
    df, manifest = builder.build_dataset(market, news, fund)

    assert not df.empty
    assert "target_return" in df.columns
    assert "target_class" in df.columns
    assert manifest["num_rows"] == len(df)
    assert len(manifest["feature_names"]) > 10
