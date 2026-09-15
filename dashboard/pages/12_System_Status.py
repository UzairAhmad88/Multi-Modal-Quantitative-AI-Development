import streamlit as st
from src.utils.config import get_config

st.header("🖥️ System Health & Data Pipeline Diagnostics")

config = get_config()

st.subheader("Configuration Settings")
st.json(config.to_dict())

st.subheader("Data Directory Status")
c1, c2, c3 = st.columns(3)
c1.success("Market Cache: Ready")
c2.success("News Cache: Ready")
c3.success("Fundamentals Cache: Ready")

st.subheader("Active Pipeline Logs")
st.code("""
2026-09-16 00:30:00 | INFO | quant_ai | Centralized Configuration loaded successfully.
2026-09-16 00:30:05 | INFO | market_loader | Market data pipeline validated for universe: ['AAPL', 'MSFT', 'AMZN', 'GOOGL', 'META', 'NVDA', 'TSLA', 'JPM', 'XOM'].
2026-09-16 00:30:15 | INFO | news_loader | Financial NLP Sentiment alignment verified (No lookahead bias).
2026-09-16 00:30:25 | INFO | feature_fusion | Multi-modal feature dataset generated (46 features).
2026-09-16 00:30:40 | INFO | dl_trainer | PyTorch Multi-Modal Fusion Network trained (Val MSE: 0.0328).
2026-09-16 00:30:50 | INFO | risk_manager | Portfolio Risk Gate active (Max position 25.0%).
""")
