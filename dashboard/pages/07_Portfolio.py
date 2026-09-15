import streamlit as st
import pandas as pd
from dashboard.components.charts import plot_portfolio_allocation

st.header("💼 Portfolio Construction & Allocation")

weights = pd.Series({"AAPL": 0.25, "MSFT": 0.25, "NVDA": 0.20, "AMZN": 0.15, "GOOGL": 0.15})

st.plotly_chart(plot_portfolio_allocation(weights), use_container_width=True)

st.subheader("Holdings Summary")
holdings = pd.DataFrame([
    {"Asset": "AAPL", "Weight": "25.0%", "Notional": "$31,212", "P&L": "+$4,120"},
    {"Asset": "MSFT", "Weight": "25.0%", "Notional": "$31,212", "P&L": "+$2,850"},
    {"Asset": "NVDA", "Weight": "20.0%", "Notional": "$24,970", "P&L": "+$5,910"},
    {"Asset": "AMZN", "Weight": "15.0%", "Notional": "$18,727", "P&L": "-$420"},
    {"Asset": "GOOGL", "Weight": "15.0%", "Notional": "$18,727", "P&L": "+$1,140"}
])

st.dataframe(holdings, use_container_width=True)
