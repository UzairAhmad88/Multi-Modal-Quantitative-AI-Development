from src.data.news_loader import (
    load_news_data, generate_demo_news, NewsCleaner, NewsValidator, REQUIRED_NEWS_COLUMNS
)

def test_generate_demo_news():
    df = generate_demo_news(["AAPL", "MSFT"], "2023-01-01", "2023-06-01", count_per_ticker=20)
    assert not df.empty
    assert set(REQUIRED_NEWS_COLUMNS).issubset(df.columns)
    assert set(df["ticker"].unique()) == {"AAPL", "MSFT"}
    assert NewsValidator.validate_schema(df)

def test_news_cleaner():
    raw = generate_demo_news(["AAPL"], "2023-01-01", "2023-01-10", count_per_ticker=5)
    cleaned = NewsCleaner.clean(raw)
    assert "published_at" in cleaned.columns
    assert cleaned["published_at"].dt.tz is not None

def test_load_news_data():
    df = load_news_data(tickers=["AAPL"], start="2023-01-01", end="2023-03-01")
    assert not df.empty
