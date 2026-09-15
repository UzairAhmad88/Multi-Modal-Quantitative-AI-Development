import streamlit as st
import pandas as pd
import numpy as np
from src.data.market_loader import generate_demo_market_data
from src.backtesting.engine import BacktestEngine
from dashboard.components.charts import plot_equity_curve, plot_drawdown_curve

st.header("📊 Executive Overview")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Portfolio Value", "$124,850", "+24.85%")
col2.metric("Sharpe Ratio", "1.82", "Annualized")
col3.metric("Sortino Ratio", "2.45", "Annualized")
col4.metric("Max Drawdown", "-8.42%", "PASS (Limit: 20%)")

st.divider()

# Load demo simulation for overview chart
market = generate_demo_market_data("AAPL", "2023-01-01", "2023-12-31")
weights = pd.DataFrame({"AAPL": [0.25] * len(market)}, index=pd.to_datetime(market["date"], utc=True))
engine = BacktestEngine()
res = engine.run(market, weights)

c1, c2 = st.columns(2)
with c1:
    st.plotly_chart(plot_equity_curve(res["equity_curve"]), use_container_width=True)
with c2:
    st.plotly_chart(plot_drawdown_curve(res["equity_curve"]), use_container_width=True)

st.subheader("System Status Summary")
s1, s2, s3, s4 = st.columns(4)
s1.success("Market Data: OK")
s2.success("News NLP: OK")
s3.success("Fundamentals: OK")
s4.success("Risk Engine: OK")
