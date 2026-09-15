import streamlit as st
import pandas as pd
from src.data.market_loader import load_market_data
from src.features.technical import add_technical_features
from dashboard.components.charts import plot_price_and_indicators

st.header("📈 Market Data & Technical Analysis")

col1, col2 = st.columns(2)
ticker = col1.selectbox("Select Asset Ticker", ["AAPL", "MSFT", "NVDA", "AMZN", "GOOGL", "META", "TSLA", "JPM", "XOM"])
start_date = col2.date_input("Start Date", pd.Timestamp("2023-01-01"))

df = load_market_data(ticker, start=str(start_date))
feats = add_technical_features(df)

st.plotly_chart(plot_price_and_indicators(feats, ticker), use_container_width=True)

st.subheader("Latest Technical Metrics")
m1, m2, m3, m4 = st.columns(4)
latest = feats.iloc[-1]
m1.metric("Close Price", f"${latest['close']:.2f}", f"{latest['return_1d']*100:.2f}%")
m2.metric("RSI (14)", f"{latest['rsi_14']:.1f}")
m3.metric("ATR (14)", f"${latest['atr_14']:.2f}")
m4.metric("Volatility (20d)", f"{latest['volatility_20d']*100:.1f}%")

st.subheader("Raw Data Table")
st.dataframe(feats.tail(50), use_container_width=True)
