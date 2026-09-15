import streamlit as st
import pandas as pd
from src.data.market_loader import generate_demo_market_data
from src.backtesting.engine import BacktestEngine, BacktestConfig
from dashboard.components.charts import plot_equity_curve, plot_drawdown_curve

st.header("🧪 Backtest Engine & Walk-Forward Simulation")

col1, col2, col3 = st.columns(3)
initial_capital = col1.number_input("Initial Capital ($)", 10000, 1000000, 100000)
tx_bps = col2.slider("Transaction Cost (bps)", 0, 50, 10)
slip_bps = col3.slider("Slippage (bps)", 0, 50, 5)

if st.button("🚀 RUN BACKTEST"):
    with st.spinner("Executing realistic backtest simulation with slippage and fees..."):
        market = generate_demo_market_data("AAPL", "2020-01-01", "2023-12-31")
        weights = pd.DataFrame({"AAPL": [0.25] * len(market)}, index=pd.to_datetime(market["date"], utc=True))
        cfg = BacktestConfig(initial_capital=initial_capital, transaction_cost_bps=tx_bps, slippage_bps=slip_bps)
        engine = BacktestEngine(cfg)
        res = engine.run(market, weights)

        st.success("Backtest Execution Completed!")

        m = res["metrics"]
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Total Return", f"{m['total_return']*100:.2f}%")
        k2.metric("CAGR", f"{m['cagr']*100:.2f}%")
        k3.metric("Sharpe Ratio", f"{m['sharpe_ratio']:.2f}")
        k4.metric("Max Drawdown", f"{m['max_drawdown']*100:.2f}%")

        st.plotly_chart(plot_equity_curve(res["equity_curve"]), use_container_width=True)
