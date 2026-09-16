"""
Portfolio Risk Attribution Engine for Portfolio Construction OS.
"""

from typing import Dict, Any, List, Optional
import numpy as np
from portfolio.risk.contribution import RiskContributionCalculator
from portfolio.risk.concentration import ConcentrationAnalyzer
from portfolio.risk.diversification import DiversificationAnalyzer


class PortfolioRiskAttribution:
    """Unified Portfolio Risk Attribution system incorporating MCR/PCR, HHI, and Diversification metrics."""

    @staticmethod
    def compute_full_attribution(
        weights: Dict[str, float],
        cov_matrix: np.ndarray,
        asset_metadata: Optional[Dict[str, Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        assets = list(weights.keys())
        w_vec = np.array([weights[a] for a in assets], dtype=float)

        contrib = RiskContributionCalculator.calculate_risk_contributions(
            weights=w_vec,
            cov_matrix=cov_matrix,
            asset_names=assets,
        )

        conc = ConcentrationAnalyzer.analyze_concentration(weights)
        div_ratio = DiversificationAnalyzer.calculate_diversification_ratio(w_vec, cov_matrix)
        corr_diag = DiversificationAnalyzer.analyze_correlation(cov_matrix)

        # Sector risk attribution
        sector_pcr: Dict[str, float] = {}
        if asset_metadata:
            for i, a in enumerate(assets):
                sec = asset_metadata.get(a, {}).get("sector", "Unassigned")
                sector_pcr[sec] = sector_pcr.get(sec, 0.0) + contrib["pcr"][a]

        return {
            "portfolio_volatility": contrib["portfolio_volatility"],
            "portfolio_variance": contrib["portfolio_variance"],
            "diversification_ratio": div_ratio,
            "asset_risk_contributions": contrib["pcr"],
            "sector_risk_contributions": sector_pcr,
            "concentration_metrics": conc,
            "correlation_summary": {
                "avg_correlation": corr_diag["avg_correlation"],
                "max_correlation": corr_diag["max_correlation"],
                "min_correlation": corr_diag["min_correlation"],
            },
        }
