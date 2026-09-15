import streamlit as st
from src.alpha.signal_generator import AlphaEngine

st.header("⚡ Alpha Engine & Signal Generator")

engine = AlphaEngine(buy_threshold=0.50, sell_threshold=-0.50)

st.subheader("Interactive Signal Simulation")
xgb_pred = st.slider("XGBoost Expected Return", -0.10, 0.10, 0.04, step=0.01)
lstm_pred = st.slider("LSTM Expected Return", -0.10, 0.10, 0.03, step=0.01)
trans_pred = st.slider("Transformer Expected Return", -0.10, 0.10, 0.05, step=0.01)

raw_preds = {"XGBoost": xgb_pred, "LSTM": lstm_pred, "Transformer": trans_pred}
res = engine.process_predictions(raw_preds)

c1, c2, c3 = st.columns(3)
c1.metric("Composite Alpha", f"{res['composite_alpha']:.2f}")
c2.metric("Generated Signal", res['signal'])
c3.metric("Signal Confidence", res['confidence_level'])

st.json(res)
