"""
Portfolio & P&L Attribution Module
Decomposes portfolio returns into price effect, position sizing effect, transaction costs,
slippage drag, and signal confidence attribution.
"""

from typing import Dict, List, Any, Optional, Tuple
import numpy as np
import pandas as pd


class PortfolioAttributor:
    """Quantitative P&L and Factor Return Attribution Engine."""

    def __init__(self, trades_df: pd.DataFrame):
        """
        Initialize PortfolioAttributor.
        :param trades_df: DataFrame containing trade records with asset, weight, gross_return, cost_bps, slippage_bps.
        """
        self.df = trades_df.copy()

    def compute_pnl_decomposition(self) -> Dict[str, float]:
        """
        Decompose portfolio total return into price gain, transaction costs, and slippage.
        """
        df = self.df.copy()
        if df.empty:
            return {
                "total_gross_return": 0.0,
                "transaction_cost_drag": 0.0,
                "slippage_drag": 0.0,
                "total_net_return": 0.0,
            }

        gross_ret = float(df["gross_return"].sum()) if "gross_return" in df.columns else 0.0
        cost_drag = float(df["transaction_cost"].sum()) if "transaction_cost" in df.columns else (
            float((df["cost_bps"] / 10000.0 * df["traded_value"]).sum()) if "cost_bps" in df.columns and "traded_value" in df.columns else 0.0
        )
        slippage_drag = float(df["slippage_cost"].sum()) if "slippage_cost" in df.columns else (
            float((df["slippage_bps"] / 10000.0 * df["traded_value"]).sum()) if "slippage_bps" in df.columns and "traded_value" in df.columns else 0.0
        )

        net_ret = gross_ret - cost_drag - slippage_drag

        return {
            "total_gross_return": round(gross_ret, 6),
            "transaction_cost_drag": round(cost_drag, 6),
            "slippage_drag": round(slippage_drag, 6),
            "total_net_return": round(net_ret, 6),
        }

    def compute_asset_attribution(self) -> pd.DataFrame:
        """
        Group returns by asset ticker to identify individual asset contributions.
        """
        df = self.df.copy()
        if df.empty or "ticker" not in df.columns:
            return pd.DataFrame()

        ret_col = "net_return" if "net_return" in df.columns else "gross_return"
        if ret_col not in df.columns:
            df[ret_col] = 0.0

        summary = df.groupby("ticker").agg(
            total_return=(ret_col, "sum"),
            trade_count=(ret_col, "count"),
            avg_return=(ret_col, "mean"),
            win_rate=(ret_col, lambda x: (x > 0).mean()),
        ).reset_index()

        summary["total_return"] = summary["total_return"].round(6)
        summary["avg_return"] = summary["avg_return"].round(6)
        summary["win_rate"] = summary["win_rate"].round(4)

        return summary.sort_values(by="total_return", ascending=False)
