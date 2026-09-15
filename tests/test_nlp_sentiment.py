import pandas as pd
import numpy as np
from src.nlp.sentiment import score_text_sentiment, score_sentiment_full
from src.nlp.embeddings import encode_texts
from src.features.sentiment_features import align_news_timestamps, aggregate_daily_sentiment, add_rolling_sentiment_features

def test_sentiment_scoring():
    score, pos, neg, neu = score_text_sentiment("AAPL reports record revenue beat and strong profit growth")
    assert score > 0.0
    assert pos > neg

    score_neg, pos_n, neg_n, neu_n = score_text_sentiment("MSFT misses earnings expectations, fell sharply on lawsuit risk")
    assert score_neg < 0.0
    assert neg_n > pos_n

def test_encode_texts():
    texts = ["AAPL earnings report", "Market volatility increases"]
    emb = encode_texts(texts, dimension=32)
    assert emb.shape == (2, 32)

def test_time_alignment_policy():
    df = pd.DataFrame({
        "published_at": ["2023-01-01 10:00:00+00:00", "2023-01-01 22:00:00+00:00"],
        "ticker": ["AAPL", "AAPL"],
        "headline": ["Before close news", "After close news"]
    })
    aligned = align_news_timestamps(df)
    assert aligned.iloc[0]["available_date"] == pd.Timestamp("2023-01-01", tz="UTC")
    assert aligned.iloc[1]["available_date"] == pd.Timestamp("2023-01-02", tz="UTC")

def test_aggregate_daily_sentiment():
    df = pd.DataFrame({
        "published_at": ["2023-01-01 10:00:00+00:00", "2023-01-01 14:00:00+00:00"],
        "ticker": ["AAPL", "AAPL"],
        "headline": ["Beat growth revenue", "Upgrade strong dividend"]
    })
    daily = aggregate_daily_sentiment(df)
    assert len(daily) == 1
    assert "sentiment_mean" in daily.columns
    assert "positive_news_count" in daily.columns

    rolling = add_rolling_sentiment_features(daily)
    assert "sentiment_rolling_mean_3d" in rolling.columns
