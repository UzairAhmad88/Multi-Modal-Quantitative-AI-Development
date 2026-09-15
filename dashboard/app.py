import streamlit as st
from pathlib import Path
import sys

# Add root directory to python path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.utils.config import get_config

st.set_page_config(
    page_title="Multi-Modal Quant AI Platform",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply sleek, professional technical CSS styling
st.markdown("""
<style>
    .main { background-color: #F8FAFC; }
    .stMetric { background: #FFFFFF; border: 1px solid #E2E8F0; padding: 12px; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }
    .stAlert { border-radius: 8px; }
    h1, h2, h3 { color: #0F172A; font-family: 'Inter', sans-serif; }
</style>
""", unsafe_allow_html=True)

config = get_config()

st.sidebar.title("🤖 Quant AI Hub")
st.sidebar.caption(f"Environment: {config.get('env', 'development').upper()} | Data Mode: {config.get('data_mode', 'demo').upper()}")
st.sidebar.divider()

st.title("Multi-Modal Quant AI Research Platform")
st.markdown("""
Welcome to the **Multi-Modal Quant AI Platform**. This research workspace integrates **Market Data**, **Financial News & Sentiment NLP**, **Fundamental Ratios**, **Multi-Modal Neural Fusion**, **Risk-Gated Portfolio Optimization**, and **Realistic Backtesting**.
""")

st.info("💡 Select a page from the sidebar navigation to inspect research analytics, AI signals, risk gates, model comparisons, or execute backtests.")
