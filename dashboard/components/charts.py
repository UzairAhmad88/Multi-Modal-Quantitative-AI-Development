import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np


def plot_equity_curve(equity_series: pd.Series, benchmark_series: pd.Series | None = None) -> go.Figure:
    """Plot Strategy Equity Curve vs Benchmark."""
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=equity_series.index, y=equity_series.values, mode="lines", name="Strategy AI Portfolio", line=dict(color="#2563EB", width=2)))
    if benchmark_series is not None and not benchmark_series.empty:
        norm_bm = benchmark_series / benchmark_series.iloc[0] * equity_series.iloc[0]
        fig.add_trace(go.Scatter(x=norm_bm.index, y=norm_bm.values, mode="lines", name="Benchmark (Buy & Hold)", line=dict(color="#9CA3AF", width=1.5, dash="dash")))

    fig.update_layout(
        title="Equity Curve Performance ($)",
        xaxis_title="Date",
        yaxis_title="Portfolio Value ($)",
        template="plotly_white",
        margin=dict(l=20, r=20, t=40, b=20),
        hovermode="x unified"
    )
    return fig


def plot_price_and_indicators(df: pd.DataFrame, ticker: str) -> go.Figure:
    """Plot OHLCV Price chart with SMA 20/50 and Volume."""
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df["date"], y=df["close"], mode="lines", name="Close Price", line=dict(color="#1E293B", width=2)))

    if "sma_20" in df.columns:
        fig.add_trace(go.Scatter(x=df["date"], y=df["sma_20"], mode="lines", name="SMA 20", line=dict(color="#3B82F6", width=1)))
    if "sma_50" in df.columns:
        fig.add_trace(go.Scatter(x=df["date"], y=df["sma_50"], mode="lines", name="SMA 50", line=dict(color="#F59E0B", width=1)))

    fig.update_layout(
        title=f"{ticker} Historical Market Price & Moving Averages",
        xaxis_title="Date",
        yaxis_title="Price ($)",
        template="plotly_white",
        margin=dict(l=20, r=20, t=40, b=20)
    )
    return fig


def plot_drawdown_curve(equity_series: pd.Series) -> go.Figure:
    """Plot underwater drawdown chart."""
    from src.risk.drawdown import drawdown
    dd = drawdown(equity_series) * 100.0
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=dd.index, y=dd.values, fill="tozeroy", name="Drawdown %", line=dict(color="#EF4444", width=1)))
    fig.update_layout(
        title="Underwater Portfolio Drawdown (%)",
        xaxis_title="Date",
        yaxis_title="Drawdown %",
        template="plotly_white",
        margin=dict(l=20, r=20, t=40, b=20)
    )
    return fig


def plot_portfolio_allocation(weights: pd.Series) -> go.Figure:
    """Plot asset allocation pie/donut chart."""
    fig = px.pie(
        values=weights.values,
        names=weights.index,
        title="Portfolio Target Allocation Weights",
        hole=0.4,
        color_discrete_sequence=px.colors.qualitative.Prism
    )
    fig.update_layout(margin=dict(l=20, r=20, t=40, b=20))
    return fig


def plot_feature_importance(importance: pd.Series, top_n: int = 15) -> go.Figure:
    """Plot horizontal bar chart of top N feature importances."""
    top_feats = importance.head(top_n).iloc[::-1]
    fig = go.Figure(go.Bar(
        x=top_feats.values,
        y=top_feats.index,
        orientation="h",
        marker=dict(color="#3B82F6")
    ))
    fig.update_layout(
        title=f"Top {top_n} Feature Importances",
        xaxis_title="Importance Score",
        template="plotly_white",
        margin=dict(l=20, r=20, t=40, b=20)
    )
    return fig
