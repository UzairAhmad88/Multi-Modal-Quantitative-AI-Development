import streamlit as st
import pandas as pd
from src.data.fundamental_loader import load_fundamentals
from src.features.fundamental_features import build_fundamental_features

st.header("🏢 Fundamental Analysis & Financial Ratios")

ticker = st.selectbox("Select Ticker", ["AAPL", "MSFT", "NVDA"])
df = load_fundamentals(ticker)
feats = build_fundamental_features(df)

st.subheader("Quarterly Financial Statements")
st.dataframe(df[["quarter_end_date", "public_release_date", "revenue", "net_income", "eps", "free_cash_flow", "equity", "total_debt"]], use_container_width=True)

st.subheader("Derived Valuation & Financial Health Ratios")
st.dataframe(feats[["public_release_date", "net_margin", "roe", "roa", "debt_to_equity", "revenue_growth_yoy", "earnings_growth_yoy"]], use_container_width=True)
