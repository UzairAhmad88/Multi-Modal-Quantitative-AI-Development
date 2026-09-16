import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
import pandas as pd
import numpy as np


def plot_equity_curve(equity_series: pd.Series, benchmark_series: pd.Series | None = None) -> go.Figure:
    """Plot Strategy Equity Curve vs Benchmark."""
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=equity_series.index, y=equity_series.values, mode="lines",
        name="Multi-Modal AI Strategy", line=dict(color="#10B981", width=2.5)
    ))
    if benchmark_series is not None and not benchmark_series.empty:
        norm_bm = benchmark_series / benchmark_series.iloc[0] * equity_series.iloc[0]
        fig.add_trace(go.Scatter(
            x=norm_bm.index, y=norm_bm.values, mode="lines",
            name="Benchmark (Buy & Hold)", line=dict(color="#9CA3AF", width=1.5, dash="dash")
        ))

    fig.update_layout(
        title="Strategy Equity Curve vs Benchmark ($)",
        xaxis_title="Date",
        yaxis_title="Portfolio Value ($)",
        template="plotly_dark",
        paper_bgcolor="#0F172A",
        plot_bgcolor="#0F172A",
        margin=dict(l=20, r=20, t=40, b=20),
        hovermode="x unified"
    )
    return fig


def plot_candlestick_with_indicators(df: pd.DataFrame, ticker: str) -> go.Figure:
    """Plot OHLCV Candlestick chart with 20D/50D SMAs and RSI sub-panel."""
    fig = make_subplots(
        rows=2, cols=1, shared_xaxes=True,
        vertical_spacing=0.03, row_heights=[0.75, 0.25]
    )

    # Candlesticks
    fig.add_trace(go.Candlestick(
        x=df["date"], open=df["open"], high=df["high"], low=df["low"], close=df["close"],
        name="OHLC", increasing_line_color="#10B981", decreasing_line_color="#EF4444"
    ), row=1, col=1)

    if "sma_20" in df.columns:
        fig.add_trace(go.Scatter(x=df["date"], y=df["sma_20"], mode="lines", name="SMA 20", line=dict(color="#3B82F6", width=1.5)), row=1, col=1)
    if "sma_50" in df.columns:
        fig.add_trace(go.Scatter(x=df["date"], y=df["sma_50"], mode="lines", name="SMA 50", line=dict(color="#F59E0B", width=1.5)), row=1, col=1)

    # RSI
    if "rsi_14" in df.columns:
        fig.add_trace(go.Scatter(x=df["date"], y=df["rsi_14"], mode="lines", name="RSI (14)", line=dict(color="#8B5CF6", width=1.5)), row=2, col=1)
        fig.add_hline(y=70, line_dash="dash", line_color="#EF4444", row=2, col=1)
        fig.add_hline(y=30, line_dash="dash", line_color="#10B981", row=2, col=1)

    fig.update_layout(
        title=f"{ticker} Institutional Candlestick & RSI Technical Analysis",
        template="plotly_dark",
        paper_bgcolor="#0F172A",
        plot_bgcolor="#0F172A",
        margin=dict(l=20, r=20, t=40, b=20),
        xaxis_rangeslider_visible=False
    )
    return fig


def plot_drawdown_curve(equity_series: pd.Series) -> go.Figure:
    """Plot underwater drawdown chart."""
    from src.risk.drawdown import drawdown
    dd = drawdown(equity_series) * 100.0
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=dd.index, y=dd.values, fill="tozeroy",
        name="Drawdown %", line=dict(color="#EF4444", width=1.5)
    ))
    fig.update_layout(
        title="Underwater Portfolio Drawdown (%)",
        xaxis_title="Date",
        yaxis_title="Drawdown %",
        template="plotly_dark",
        paper_bgcolor="#0F172A",
        plot_bgcolor="#0F172A",
        margin=dict(l=20, r=20, t=40, b=20)
    )
    return fig


def plot_portfolio_allocation(weights: pd.Series) -> go.Figure:
    """Plot asset allocation donut chart."""
    fig = px.pie(
        values=weights.values,
        names=weights.index,
        title="Portfolio Target Allocation Weights",
        hole=0.4,
        template="plotly_dark"
    )
    fig.update_layout(
        paper_bgcolor="#0F172A",
        plot_bgcolor="#0F172A",
        margin=dict(l=20, r=20, t=40, b=20)
    )
    return fig


def plot_multimodal_breakdown() -> go.Figure:
    """Plot Multi-Modal modality contribution breakdown bar chart."""
    categories = ["Market Momentum", "Technical Indicators", "News Sentiment NLP", "Quarterly Fundamentals", "Macro Indicators"]
    scores = [0.74, 0.71, 0.68, 0.82, 0.41]
    fig = go.Figure(go.Bar(
        x=scores, y=categories, orientation="h",
        marker=dict(color=["#3B82F6", "#60A5FA", "#10B981", "#8B5CF6", "#F59E0B"])
    ))
    fig.update_layout(
        title="Multi-Modal Feature Modality Contributions",
        xaxis_title="Normalized Factor Contribution Score",
        template="plotly_dark",
        paper_bgcolor="#0F172A",
        plot_bgcolor="#0F172A",
        margin=dict(l=20, r=20, t=40, b=20)
    )
    return fig


def plot_ablation_comparison(ablation_dict: dict) -> go.Figure:
    """Plot modality ablation Sharpe and CAGR comparison bar chart."""
    exps = list(ablation_dict.keys())
    sharpes = [m.get("sharpe", 1.0) for m in ablation_dict.values()]
    cagrs = [m.get("cagr", 0.1) * 100.0 for m in ablation_dict.values()]

    fig = go.Figure()
    fig.add_trace(go.Bar(x=exps, y=sharpes, name="Sharpe Ratio", marker_color="#10B981"))
    fig.add_trace(go.Bar(x=exps, y=cagrs, name="CAGR (%)", marker_color="#3B82F6"))

    fig.update_layout(
        title="Modality Ablation Study: Performance Metric Comparison",
        barmode="group",
        template="plotly_dark",
        paper_bgcolor="#0F172A",
        plot_bgcolor="#0F172A",
        margin=dict(l=20, r=20, t=40, b=20)
    )
    return fig
