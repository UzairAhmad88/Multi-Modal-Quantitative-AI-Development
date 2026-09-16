"""
Master Advanced Quantitative Risk & Stress Testing Engine for Advanced Risk Engine OS.
"""

from typing import Dict, Any, List, Optional
import numpy as np
from datetime import datetime

from risk.core.risk_snapshot import RiskSnapshot
from risk.core.risk_result import RiskResult
from risk.market.volatility import VolatilityAnalyzer
from risk.market.beta import BetaCalculator
from risk.market.correlation import CorrelationAnalyzer
from risk.market.covariance import CovarianceAudit
from risk.market.factor import FactorRiskEngine
from risk.portfolio.contribution import RiskContributionEngine
from risk.portfolio.concentration import ConcentrationRiskAnalyzer
from risk.portfolio.exposure import ExposureRiskEngine
from risk.tail.var import VaREngine
from risk.tail.cvar import CVaREngine
from risk.tail.tail_distribution import DrawdownAnalyzer
from risk.stress.engine import StressTestingEngine
from risk.monte_carlo.engine import MonteCarloRiskEngine
from risk.diagnostics.limits import RiskLimitEngine


class AdvancedRiskEngine:
    """Master Quantitative Risk & Stress Engine integrating market risk, tail risk, stress tests, and Monte Carlo."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.stress_engine = StressTestingEngine()
        self.mc_engine = MonteCarloRiskEngine()
        self.limit_engine = RiskLimitEngine(self.config.get("risk_limits"))

    def evaluate_portfolio_risk(
        self,
        portfolio_id: str,
        weights: Dict[str, float],
        returns_history: np.ndarray,
        cov_matrix: np.ndarray,
        benchmark_returns: Optional[np.ndarray] = None,
        portfolio_value: float = 100000.0,
        asset_metadata: Optional[Dict[str, Dict[str, Any]]] = None,
        run_monte_carlo: bool = True,
        run_stress_testing: bool = True,
    ) -> RiskResult:
        assets = list(weights.keys())
        w_vec = np.array([weights[a] for a in assets], dtype=float)

        # 1. Market Risk
        rets_vec = returns_history @ w_vec if returns_history.ndim == 2 else returns_history
        vol = VolatilityAnalyzer.calculate_historical_volatility(rets_vec)
        ewma_vol = VolatilityAnalyzer.calculate_ewma_volatility(rets_vec)

        beta = 1.0
        if benchmark_returns is not None and len(benchmark_returns) == len(rets_vec):
            beta = BetaCalculator.calculate_beta(rets_vec, benchmark_returns)

        corr_diag = CorrelationAnalyzer.compute_correlation_matrix(
            returns_history if returns_history.ndim == 2 else np.column_stack([rets_vec, rets_vec]),
            asset_names=assets if returns_history.ndim == 2 else ["Port", "Bench"],
        )
        cov_valid, cov_diag = CovarianceAudit.audit_covariance(cov_matrix)

        market_risk = {
            "historical_volatility": vol,
            "ewma_volatility": ewma_vol,
            "beta": beta,
            "correlation": corr_diag,
            "covariance_audit": cov_diag,
        }

        # 2. Portfolio Risk & Attribution
        contrib = RiskContributionEngine.compute_contributions(weights, cov_matrix)
        conc = ConcentrationRiskAnalyzer.analyze(weights, asset_metadata)
        exp = ExposureRiskEngine.calculate_exposures(weights)

        portfolio_risk = {
            "contributions": contrib,
            "concentration": conc,
            "exposures": exp,
        }

        # 3. Tail Risk & Drawdown
        var95_hist = VaREngine.historical_var(rets_vec, confidence_level=0.95)
        var95_param = VaREngine.parametric_var(rets_vec, confidence_level=0.95)
        cvar95 = CVaREngine.calculate_cvar(rets_vec, confidence_level=0.95)
        dd_res = DrawdownAnalyzer.analyze_drawdown(rets_vec, initial_value=portfolio_value)

        tail_risk = {
            "var_95_historical": var95_hist,
            "var_95_parametric": var95_param,
            "cvar_95": cvar95,
        }

        # 4. Stress Testing
        stress_res = {}
        if run_stress_testing:
            stress_res = self.stress_engine.run_stress_matrix(
                portfolio_id=portfolio_id,
                weights=weights,
                base_value=portfolio_value,
                asset_metadata=asset_metadata,
            )

        # 5. Monte Carlo Simulation
        mc_res = {}
        if run_monte_carlo:
            mc_res = self.mc_engine.run_simulation(
                portfolio_id=portfolio_id,
                weights=weights,
                cov_matrix=cov_matrix,
                num_simulations=10000,
                base_value=portfolio_value,
            )

        # 6. Risk Limit Evaluation
        snapshot_dict = {
            "volatility": vol,
            "var_95": var95_hist,
            "cvar_95": cvar95,
            "maximum_drawdown": dd_res["max_drawdown"],
            "leverage": exp["leverage"],
        }
        limits_res = self.limit_engine.evaluate_limits(snapshot_dict)

        risk_id = f"RISK-{portfolio_id}-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"

        return RiskResult(
            risk_id=risk_id,
            portfolio_id=portfolio_id,
            market_risk=market_risk,
            portfolio_risk=portfolio_risk,
            tail_risk=tail_risk,
            drawdown_analysis=dd_res,
            stress_results=stress_res,
            monte_carlo_results=mc_res,
            risk_limits_status=limits_res,
            timestamp=datetime.utcnow().isoformat() + "Z",
        )
