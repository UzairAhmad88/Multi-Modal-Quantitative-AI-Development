import streamlit as st
import pandas as pd
from src.data.news_loader import load_news_data
from src.features.sentiment_features import aggregate_daily_sentiment

st.header("📰 Financial News & Sentiment NLP")

ticker = st.selectbox("Filter News by Ticker", ["AAPL", "MSFT", "NVDA", "ALL"])
tickers_filter = [ticker] if ticker != "ALL" else ["AAPL", "MSFT", "NVDA"]

news_df = load_news_data(tickers=tickers_filter, start="2023-01-01")
daily_sent = aggregate_daily_sentiment(news_df)

c1, c2, c3 = st.columns(3)
c1.metric("Total Articles", len(news_df))
c2.metric("Positive News Ratio", f"{(daily_sent['positive_news_count'].sum() / max(1, daily_sent['news_count'].sum())) * 100:.1f}%")
c3.metric("Avg Sentiment Score", f"{daily_sent['sentiment_mean'].mean():.2f}")

st.subheader("Daily Sentiment Timeline")
st.line_chart(daily_sentiment_df if (daily_sentiment_df := daily_sent.set_index("available_date")["sentiment_mean"]) is not None else None)

st.subheader("Latest Ingested News Articles")
st.dataframe(news_df[["published_at", "ticker", "source", "headline", "sentiment_score"]].tail(20), use_container_width=True)
