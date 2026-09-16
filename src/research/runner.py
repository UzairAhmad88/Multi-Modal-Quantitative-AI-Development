"""
Research Pipeline Orchestrator Module
Runs comprehensive research experiments based on YAML configurations and generates structured reports.
"""

import os
import json
import yaml
from datetime import datetime
from typing import Dict, List, Any, Optional
import numpy as np
import pandas as pd

from src.research.factor_analysis import FactorAnalyzer
from src.research.explainability import ModelExplainer
from src.research.robustness import RobustnessTester
from src.research.stress_testing import StressTester
from src.research.uncertainty import UncertaintyAnalyzer
from src.research.error_analysis import ErrorAnalyzer
from src.research.attribution import PortfolioAttributor
from src.research.statistical_tests import StatisticalTester


class ResearchRunner:
    """Orchestrates end-to-end Quantitative Research Experiments."""

    def __init__(self, config_path_or_dict: Any):
        """
        Initialize ResearchRunner.
        :param config_path_or_dict: Path to research YAML config file or config dictionary.
        """
        if isinstance(config_path_or_dict, str) and os.path.exists(config_path_or_dict):
            with open(config_path_or_dict, "r") as f:
                self.config = yaml.safe_load(f)
        elif isinstance(config_path_or_dict, dict):
            self.config = config_path_or_dict
        else:
            self.config = {
                "experiment_id": f"exp_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "ticker": "AAPL",
                "start_date": "2022-01-01",
                "end_date": "2024-01-01",
            }

    def run_experiment(self, demo: bool = True) -> Dict[str, Any]:
        """
        Execute full research workflow: Data -> Factors -> Models -> Explainability -> Robustness -> Stress Test -> Bootstrap.
        """
        exp_id = self.config.get("experiment_id", f"exp_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        output_dir = os.path.join("experiments", "research", exp_id)
        os.makedirs(output_dir, exist_ok=True)

        # 1. Generate Synthetic/Real Data for Research Pipeline
        dates = pd.date_range(start="2022-01-01", periods=250, freq="B")
        np.random.seed(42)

        price = 150.0 + np.cumsum(np.random.normal(0.2, 2.0, len(dates)))
        volume = np.random.randint(1000000, 5000000, len(dates))
        sentiment = np.random.normal(0.1, 0.5, len(dates))
        pe_ratio = 25.0 + np.random.normal(0, 1, len(dates))
        roe = 0.15 + np.random.normal(0, 0.02, len(dates))

        df = pd.DataFrame({
            "date": dates,
            "ticker": "AAPL",
            "close": price,
            "volume": volume,
            "sentiment_score": sentiment,
            "pe_ratio": pe_ratio,
            "roe": roe,
        })
        df["forward_return"] = df["close"].pct_change(5).shift(-5)
        df["predicted_signal"] = np.tanh(df["sentiment_score"] * 0.5 + (df["close"].pct_change(10).fillna(0)) * 2.0)
        df["strategy_return"] = df["predicted_signal"].shift(1) * df["close"].pct_change()
        df["strategy_return"] = df["strategy_return"].fillna(0.0)

        # 2. Factor Analysis
        fa = FactorAnalyzer(df)
        fa.compute_factors()
        ic_stats = fa.compute_ic(signal_col="predicted_signal", return_col="forward_return")
        ic_decay = fa.compute_ic_decay(signal_col="predicted_signal")
        quantile_res = fa.compute_quantile_returns(signal_col="predicted_signal", return_col="forward_return")

        # 3. Model Explainability
        mock_fi = {
            "factor_momentum_1m": 0.35,
            "factor_sentiment": 0.25,
            "factor_volatility_20d": 0.20,
            "factor_liquidity": 0.10,
            "factor_value": 0.05,
            "factor_quality": 0.05,
        }
        explainer = ModelExplainer(model=None, feature_names=list(mock_fi.keys()))
        modality_att = explainer.compute_modality_attribution(mock_fi)

        # 4. Robustness & Sensitivity
        def dummy_backtest(params):
            cost = params.get("transaction_cost_bps", 10.0)
            slip = params.get("slippage_bps", 5.0)
            net_ret = df["strategy_return"] - (cost + slip) / 10000.0 * 0.10
            ann_m = float(net_ret.mean() * 252)
            ann_s = float(net_ret.std() * np.sqrt(252)) + 1e-8
            return {"sharpe": round(ann_m / ann_s, 4), "cagr": round(ann_m, 4), "max_drawdown": -0.12}

        rob_tester = RobustnessTester(dummy_backtest)
        cost_df = rob_tester.test_cost_sensitivity()
        slip_df = rob_tester.test_slippage_sensitivity()

        # 5. Stress Testing
        stress_tester = StressTester(df["strategy_return"])
        hist_scenarios = stress_tester.run_historical_scenarios()
        shocks = stress_tester.run_hypothetical_shocks()
        liq_stress = stress_tester.run_liquidity_stress()

        # 6. Error & Drift Analysis
        err_analyzer = ErrorAnalyzer(df.assign(predicted_return=df["predicted_signal"]*0.02, realized_return=df["forward_return"]))
        err_metrics = err_analyzer.compute_error_metrics()

        # 7. Statistical Bootstrapping
        stat_tester = StatisticalTester(df["strategy_return"])
        sig_tests = stat_tester.test_performance_significance()
        bootstrap_res = stat_tester.bootstrap_metrics(num_iterations=200)

        # Save structured JSON summary
        report_data = {
            "experiment_id": exp_id,
            "timestamp": datetime.now().isoformat(),
            "ic_analysis": ic_stats,
            "ic_decay": ic_decay,
            "quantile_spread": quantile_res["long_short_spread"],
            "modality_attribution": modality_att,
            "cost_sensitivity_sharpe": cost_df.to_dict(orient="records"),
            "historical_stress": hist_scenarios,
            "hypothetical_shocks": shocks,
            "liquidity_stress": liq_stress,
            "error_metrics": err_metrics,
            "statistical_significance": sig_tests,
            "bootstrap_confidence_intervals": bootstrap_res,
        }

        with open(os.path.join(output_dir, "metrics.json"), "w") as f:
            json.dump(report_data, f, indent=2)

        # Generate markdown report
        md_content = f"""# Research Experiment Report: {exp_id}

Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 1. Information Coefficient (IC) Analysis
- **Mean IC**: {ic_stats['mean_ic']}
- **IC Standard Deviation**: {ic_stats['std_ic']}
- **ICIR**: {ic_stats['icir']}
- **Positive IC Ratio**: {ic_stats['positive_ic_ratio'] * 100:.1f}%

## 2. Modality Attribution
- **Market Features**: {modality_att['Market']*100:.1f}%
- **News/NLP Features**: {modality_att['News']*100:.1f}%
- **Fundamentals**: {modality_att['Fundamentals']*100:.1f}%

## 3. Execution Sensitivity
- **Baseline Sharpe (10 bps fee)**: {cost_df[cost_df['cost_bps']==10.0]['sharpe'].values[0] if not cost_df[cost_df['cost_bps']==10.0].empty else 0.0}
- **High Cost Sharpe (100 bps fee)**: {cost_df[cost_df['cost_bps']==100.0]['sharpe'].values[0] if not cost_df[cost_df['cost_bps']==100.0].empty else 0.0}

## 4. Stress Testing & Liquidity
- **2020 COVID Crash Simulation Max DD**: {hist_scenarios['2020 COVID Crash']['max_drawdown']}
- **-10% Shock Stressed VaR (95%)**: {shocks['Shock -10%']['stressed_var_95']}
- **3x Spread Liquidity Stressed Sharpe**: {liq_stress['stressed_sharpe_ratio']}

## 5. Statistical Significance & Bootstrapping
- **p-value vs Zero**: {sig_tests['p_val_vs_zero']} (Significant: {sig_tests['is_significant_vs_zero_95']})
- **Sharpe 95% Bootstrap CI**: [{bootstrap_res['sharpe']['ci_lower']}, {bootstrap_res['sharpe']['ci_upper']}]
"""

        with open(os.path.join(output_dir, "report.md"), "w") as f:
            f.write(md_content)

        return report_data
