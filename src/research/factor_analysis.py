"""
Factor Analysis Module
Calculates quantitative factor scores, cross-sectional rankings, Information Coefficients (IC),
IC decay, quantile spread returns, and factor neutralization.
"""

from typing import Dict, List, Optional, Tuple, Union
import numpy as np
import pandas as pd
from scipy import stats


class FactorAnalyzer:
    """Quantitative Factor Analysis & Signal Diagnostics Engine."""

    def __init__(self, df: pd.DataFrame):
        """
        Initialize FactorAnalyzer.
        :param df: Multi-asset or single-asset dataframe containing price, volume, sentiment, fundamental cols.
        """
        self.df = df.copy()

    def compute_factors(self) -> pd.DataFrame:
        """Calculate standardized quantitative factors."""
        df = self.df.copy()

        # Momentum Factor (20D / 1M return)
        if "close" in df.columns:
            df["factor_momentum_1m"] = df.groupby("ticker")["close"].pct_change(20) if "ticker" in df.columns else df["close"].pct_change(20)
            df["factor_volatility_20d"] = df.groupby("ticker")["close"].pct_change().rolling(20).std() if "ticker" in df.columns else df["close"].pct_change().rolling(20).std()

        # Sentiment Factor
        if "sentiment_score" in df.columns:
            df["factor_sentiment"] = df["sentiment_score"]

        # Liquidity Factor (20D log volume)
        if "volume" in df.columns:
            df["factor_liquidity"] = np.log1p(df["volume"])

        # Fundamentals (Value & Quality)
        if "pe_ratio" in df.columns:
            df["factor_value"] = -df["pe_ratio"]  # Lower PE = higher value score
        if "roe" in df.columns:
            df["factor_quality"] = df["roe"]

        # Fill NAs and standardize (z-score across time/ticker)
        factor_cols = [c for c in df.columns if c.startswith("factor_")]
        for col in factor_cols:
            df[col] = df[col].replace([np.inf, -np.inf], np.nan).fillna(0)
            mean = df[col].mean()
            std = df[col].std() + 1e-8
            df[col] = (df[col] - mean) / std

        self.df = df
        return df

    def compute_ic(
        self, signal_col: str, return_col: str = "forward_return", method: str = "spearman"
    ) -> Dict[str, float]:
        """
        Compute Information Coefficient (IC) time series and aggregate statistics.
        :param signal_col: Name of prediction signal column.
        :param return_col: Name of realized target return column.
        :param method: 'spearman' or 'pearson'.
        :return: Dict containing mean IC, std IC, ICIR, positive IC ratio.
        """
        df = self.df.dropna(subset=[signal_col, return_col])
        if len(df) < 5:
            return {"mean_ic": 0.0, "std_ic": 0.0, "icir": 0.0, "positive_ic_ratio": 0.0, "count": 0}

        if "date" in df.columns and len(df["date"].unique()) > 2:
            # Group by date for cross-sectional IC
            ic_series = []
            for date, group in df.groupby("date"):
                if len(group) >= 2 and group[signal_col].nunique() > 1 and group[return_col].nunique() > 1:
                    if method == "spearman":
                        ic, _ = stats.spearmanr(group[signal_col], group[return_col])
                    else:
                        ic, _ = stats.pearsonr(group[signal_col], group[return_col])
                    if not np.isnan(ic):
                        ic_series.append(ic)
            ic_series = pd.Series(ic_series)
        else:
            # Time-series IC overall
            if method == "spearman":
                ic, _ = stats.spearmanr(df[signal_col], df[return_col])
            else:
                ic, _ = stats.pearsonr(df[signal_col], df[return_col])
            ic_series = pd.Series([ic if not np.isnan(ic) else 0.0])

        if ic_series.empty:
            return {"mean_ic": 0.0, "std_ic": 0.0, "icir": 0.0, "positive_ic_ratio": 0.0, "count": 0}

        mean_ic = float(ic_series.mean())
        std_ic = float(ic_series.std()) if len(ic_series) > 1 else 1e-6
        std_ic = std_ic if std_ic > 1e-6 else 1e-6
        icir = float(mean_ic / std_ic)
        pos_ratio = float((ic_series > 0).mean())

        return {
            "mean_ic": round(mean_ic, 4),
            "std_ic": round(std_ic, 4),
            "icir": round(icir, 4),
            "positive_ic_ratio": round(pos_ratio, 4),
            "count": int(len(ic_series)),
        }

    def compute_ic_decay(
        self, signal_col: str, horizons: List[int] = [1, 2, 3, 5, 10]
    ) -> Dict[int, float]:
        """Compute IC across multiple forward return horizons to measure signal decay."""
        decay = {}
        df = self.df.copy()
        for h in horizons:
            ret_col = f"forward_ret_{h}d"
            if "close" in df.columns:
                df[ret_col] = df.groupby("ticker")["close"].pct_change(h).shift(-h) if "ticker" in df.columns else df["close"].pct_change(h).shift(-h)
                analyzer = FactorAnalyzer(df)
                res = analyzer.compute_ic(signal_col=signal_col, return_col=ret_col)
                decay[h] = res["mean_ic"]
            else:
                decay[h] = 0.0
        return decay

    def compute_quantile_returns(
        self, signal_col: str, return_col: str = "forward_return", quantiles: int = 5
    ) -> Dict[str, Union[Dict[int, float], float]]:
        """
        Group assets/timestamps into N quantiles and compute average return per quantile.
        Returns top-minus-bottom quantile spread.
        """
        df = self.df.dropna(subset=[signal_col, return_col]).copy()
        if len(df) < quantiles * 2:
            return {"quantile_returns": {i: 0.0 for i in range(1, quantiles + 1)}, "long_short_spread": 0.0}

        try:
            df["quantile"] = pd.qcut(df[signal_col], q=quantiles, labels=False, duplicates="drop") + 1
        except Exception:
            df["quantile"] = pd.Series(1, index=df.index)

        q_returns = df.groupby("quantile")[return_col].mean().to_dict()
        q_returns = {int(k): float(v) for k, v in q_returns.items()}

        top_q = q_returns.get(quantiles, 0.0)
        bot_q = q_returns.get(1, 0.0)
        spread = top_q - bot_q

        return {
            "quantile_returns": q_returns,
            "long_short_spread": round(float(spread), 6),
        }

    def neutralize_factor(self, factor_col: str, risk_factor_cols: List[str]) -> pd.Series:
        """
        Neutralize factor_col against risk_factor_cols via OLS regression residualization.
        """
        df = self.df.dropna(subset=[factor_col] + risk_factor_cols).copy()
        if df.empty:
            return self.df[factor_col]

        y = df[factor_col].values
        X = df[risk_factor_cols].values
        X = np.hstack([np.ones((len(X), 1)), X])  # add constant

        try:
            beta = np.linalg.lstsq(X, y, rcond=None)[0]
            residuals = y - X.dot(beta)
            res_series = pd.Series(residuals, index=df.index)
            return res_series.reindex(self.df.index).fillna(0.0)
        except Exception:
            return self.df[factor_col]
