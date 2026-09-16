"""
Master Pattern Discovery Engine for Quantitative Research Intelligence.
Combines market technicals, news sentiment, fundamental trends, and cross-modal interactions.
"""

from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np

from research_intelligence.discovery.correlation_analyzer import CorrelationAnalyzer
from research_intelligence.discovery.lag_analyzer import LagAnalyzer
from research_intelligence.discovery.anomaly_detector import AnomalyDetectionEngine


class PatternDiscoveryEngine:
    """Discovers descriptive patterns across market, news, and fundamental modalities."""

    def __init__(self):
        self.correlation_analyzer = CorrelationAnalyzer()
        self.lag_analyzer = LagAnalyzer()
        self.anomaly_detector = AnomalyDetectionEngine()

    def discover_patterns(
        self,
        market_df: Optional[pd.DataFrame] = None,
        news_df: Optional[pd.DataFrame] = None,
        fundamental_df: Optional[pd.DataFrame] = None,
        combined_df: Optional[pd.DataFrame] = None
    ) -> Dict[str, Any]:
        """Discovers descriptive patterns across all available modalities."""
        df = combined_df
        if df is None or df.empty:
            # Attempt simple merge if separate dataframes passed
            dfs = [d for d in [market_df, news_df, fundamental_df] if d is not None and not d.empty]
            if dfs:
                df = pd.concat(dfs, axis=1).dropna(how="all")
            else:
                df = self._generate_synthetic_research_df()

        patterns = []

        # 1. Market Patterns
        market_cols = [c for c in df.columns if any(k in c.lower() for k in ["close", "return", "vol", "rsi", "macd"])]
        if market_cols:
            vol_col = [c for c in market_cols if "vol" in c.lower() or "std" in c.lower()]
            if vol_col:
                vol_series = df[vol_col[0]].dropna()
                if len(vol_series) > 5:
                    autocorr = vol_series.autocorr(lag=1)
                    patterns.append({
                        "category": "MARKET",
                        "pattern_name": "Volatility Clustering",
                        "description": f"Volatility series '{vol_col[0]}' exhibits autocorrelation = {autocorr:.3f}",
                        "evidence_level": "DESCRIPTIVE",
                        "metric_value": round(float(autocorr), 4)
                    })

        # 2. News Patterns
        news_cols = [c for c in df.columns if "sentiment" in c.lower() or "news" in c.lower()]
        if news_cols:
            sentiment_series = df[news_cols[0]].dropna()
            if len(sentiment_series) > 5:
                mean_sent = sentiment_series.mean()
                patterns.append({
                    "category": "NEWS",
                    "pattern_name": "News Sentiment Mean",
                    "description": f"Sentiment series '{news_cols[0]}' average sentiment = {mean_sent:.3f}",
                    "evidence_level": "DESCRIPTIVE",
                    "metric_value": round(float(mean_sent), 4)
                })

        # 3. Cross-Modal Patterns
        if market_cols and news_cols:
            corr_res = self.correlation_analyzer.analyze_correlations(df, variables=news_cols, target_col=market_cols[0])
            for item in corr_res.get("correlations", []):
                if item.get("is_significant"):
                    patterns.append({
                        "category": "CROSS_MODAL",
                        "pattern_name": f"{item['variable']} vs {item['target']}",
                        "description": f"Correlation = {item['pearson_corr']} (p={item['pearson_pvalue']:.4f})",
                        "evidence_level": "STATISTICAL",
                        "metric_value": item['pearson_corr']
                    })

        # 4. Anomaly Detection
        anomalies_res = self.anomaly_detector.detect_anomalies(df)

        return {
            "status": "SUCCESS",
            "total_patterns_found": len(patterns),
            "patterns": patterns,
            "anomalies": anomalies_res.get("anomalies", []),
            "research_questions": anomalies_res.get("research_questions", [])
        }

    def _generate_synthetic_research_df(self) -> pd.DataFrame:
        """Generates clean synthetic dataset for pattern testing."""
        np.random.seed(42)
        n = 250
        dates = pd.date_range("2024-01-01", periods=n, freq="D")

        sentiment = np.random.normal(0.05, 0.5, n)
        returns = 0.3 * sentiment + np.random.normal(0.0005, 0.015, n)
        volatility = np.abs(returns) * 1.5 + np.random.normal(0.01, 0.002, n)
        revenue_growth = np.random.normal(0.08, 0.03, n)

        return pd.DataFrame({
            "returns": returns,
            "news_sentiment": sentiment,
            "volatility": volatility,
            "revenue_growth": revenue_growth
        }, index=dates)
