import streamlit as st
import pandas as pd
from dashboard.components.charts import plot_multimodal_breakdown

st.header("🤖 Multi-Modal AI Predictions & Feature Fusion")

c1, c2 = st.columns([1.2, 1])

with c1:
    st.subheader("Asset Prediction Matrix")
    preds = pd.DataFrame([
        {"Ticker": "AAPL", "Horizon": "5 Days", "Expected Return": "+2.84%", "Direction Prob": "68%", "Confidence": "87%", "Model": "MultiModalQuantNet v2.4"},
        {"Ticker": "NVDA", "Horizon": "5 Days", "Expected Return": "+4.12%", "Direction Prob": "74%", "Confidence": "91%", "Model": "MultiModalQuantNet v2.4"},
        {"Ticker": "MSFT", "Horizon": "5 Days", "Expected Return": "+2.15%", "Direction Prob": "64%", "Confidence": "84%", "Model": "Ensemble v2.4"},
        {"Ticker": "AMZN", "Horizon": "5 Days", "Expected Return": "+2.65%", "Direction Prob": "62%", "Confidence": "82%", "Model": "Transformer v2.4"},
        {"Ticker": "GOOGL", "Horizon": "5 Days", "Expected Return": "+0.42%", "Direction Prob": "51%", "Confidence": "65%", "Model": "XGBoost v2.4"}
    ])
    st.dataframe(preds, use_container_width=True)

with c2:
    st.plotly_chart(plot_multimodal_breakdown(), use_container_width=True)
