import streamlit as st

st.header("🛡️ Risk Engine & Risk Gate Checklist")

c1, c2, c3, c4 = st.columns(4)
c1.metric("Annualized Volatility", "14.2%")
c2.metric("Historical VaR (95%)", "1.85%")
c3.metric("Max Drawdown", "-8.42%")
c4.metric("Gross Exposure", "1.00x")

st.subheader("Risk Limit Status Checklist")
r1, r2, r3, r4 = st.columns(4)
r1.success("Max Position (25.0% <= 25%): PASS")
r2.success("Max Sector (35.0% <= 40%): PASS")
r3.success("Max Leverage (1.0x <= 1.0x): PASS")
r4.success("Max Drawdown (-8.4% <= 20%): PASS")
