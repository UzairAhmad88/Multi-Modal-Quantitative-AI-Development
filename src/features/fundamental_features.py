from __future__ import annotations
import pandas as pd
import numpy as np


def build_fundamental_features(df: pd.DataFrame, price_df: pd.DataFrame | None = None) -> pd.DataFrame:
    """Compute financial ratios, margins, valuation metrics, and growth rates from quarterly fundamentals."""
    out = df.copy()

    # Safety zero division handling
    eps = out.get("eps", pd.Series(1e-5, index=out.index))
    equity = out.get("equity", pd.Series(1e-5, index=out.index))
    assets = out.get("total_assets", pd.Series(1e-5, index=out.index))
    rev = out.get("revenue", pd.Series(1e-5, index=out.index))
    liab = out.get("total_liabilities", pd.Series(1e-5, index=out.index))
    debt = out.get("total_debt", pd.Series(0.0, index=out.index))

    # Profitability Margins
    out["net_margin"] = out["net_income"] / (rev + 1e-10)
    out["ebitda_margin"] = out["ebitda"] / (rev + 1e-10)
    out["fcf_margin"] = out["free_cash_flow"] / (rev + 1e-10)

    # Financial Returns & Ratios
    out["roe"] = out["net_income"] / (equity + 1e-10)
    out["roa"] = out["net_income"] / (assets + 1e-10)
    out["debt_to_equity"] = debt / (equity + 1e-10)
    out["current_ratio"] = out.get("cash", pd.Series(0.0, index=out.index)) / (liab + 1e-10)

    # Growth Rates (YoY 4 quarters difference)
    out = out.sort_values(["ticker", "public_release_date"]).reset_index(drop=True)
    out["revenue_growth_yoy"] = out.groupby("ticker")["revenue"].pct_change(4).fillna(0.0)
    out["earnings_growth_yoy"] = out.groupby("ticker")["net_income"].pct_change(4).fillna(0.0)
    out["fcf_growth_yoy"] = out.groupby("ticker")["free_cash_flow"].pct_change(4).fillna(0.0)

    # Optional Valuation Ratios if market price is available
    if price_df is not None and "close" in price_df.columns:
        merged = pd.merge_asof(
            out.sort_values("public_release_date"),
            price_df[["date", "close"]].sort_values("date"),
            left_on="public_release_date",
            right_on="date",
            direction="backward"
        )
        close_p = merged["close"]
        merged["pe_ratio"] = close_p / (eps + 1e-10)
        merged["pb_ratio"] = (close_p * merged["shares_outstanding"]) / (equity + 1e-10)
        merged["ps_ratio"] = (close_p * merged["shares_outstanding"]) / (rev + 1e-10)
        merged["fcf_yield"] = merged["free_cash_flow"] / (close_p * merged["shares_outstanding"] + 1e-10)
        out = merged

    return out
