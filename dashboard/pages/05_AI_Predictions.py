import streamlit as st
import pandas as pd

st.header("🤖 AI Returns & Probability Predictions")

preds = pd.DataFrame([
    {"Ticker": "AAPL", "Horizon": "5 Days", "Expected Return": "+2.45%", "Direction Prob": "68%", "Confidence": "HIGH", "Model": "Multi-Modal Fusion v1.0"},
    {"Ticker": "MSFT", "Horizon": "5 Days", "Expected Return": "+1.82%", "Direction Prob": "61%", "Confidence": "MEDIUM", "Model": "Ensemble v1.0"},
    {"Ticker": "NVDA", "Horizon": "5 Days", "Expected Return": "+4.12%", "Direction Prob": "74%", "Confidence": "HIGH", "Model": "XGBoost v1.0"},
    {"Ticker": "AMZN", "Horizon": "5 Days", "Expected Return": "-0.95%", "Direction Prob": "42%", "Confidence": "MEDIUM", "Model": "Transformer v1.0"},
    {"Ticker": "TSLA", "Horizon": "5 Days", "Expected Return": "-2.10%", "Direction Prob": "35%", "Confidence": "HIGH", "Model": "LSTM v1.0"}
])

st.dataframe(preds, use_container_width=True)
