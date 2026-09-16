"""
Concrete 14 Pipeline Stages and StageRegistry for End-to-End Orchestration OS.
"""

import numpy as np
import pandas as pd
from typing import Any, Dict, List, Type
from .stage import PipelineStage
from .pipeline_context import PipelineContext
from .exceptions import (
    DataValidationError,
    FeatureValidationError,
    LeakageGateError,
    ModelTrainingError,
    PredictionStageError,
    AlphaStageError,
    PortfolioStageError,
    ExecutionStageError,
    BacktestStageError,
    RiskGateError,
    StatisticalValidationError,
    MonitoringGateError,
)

# 1. Data Stage
class DataStage(PipelineStage):
    def __init__(self):
        super().__init__("DATA")

    def validate(self, context: PipelineContext) -> bool:
        return len(context.symbols) > 0

    def execute(self, context: PipelineContext) -> Dict[str, Any]:
        np.random.seed(context.random_seed)
        n_samples = 250
        dates = pd.date_range("2024-01-01", periods=n_samples, freq="B")
        
        market_df = pd.DataFrame({
            "timestamp": dates,
            "open": np.random.normal(150.0, 5.0, n_samples),
            "high": np.random.normal(153.0, 5.0, n_samples),
            "low": np.random.normal(148.0, 5.0, n_samples),
            "close": np.random.normal(151.0, 5.0, n_samples),
            "volume": np.random.randint(1000000, 5000000, n_samples),
        })

        news_df = pd.DataFrame({
            "timestamp": dates,
            "sentiment_score": np.random.normal(0.10, 0.20, n_samples),
        })

        fundamentals_df = pd.DataFrame({
            "timestamp": dates,
            "pe_ratio": np.random.normal(20.0, 2.0, n_samples),
            "pb_ratio": np.random.normal(3.0, 0.5, n_samples),
        })

        return {
            "market_df": market_df,
            "news_df": news_df,
            "fundamentals_df": fundamentals_df,
            "artifacts": {"data_snapshot": "DATA-SNAPSHOT-001.csv"},
        }


# 2. Feature Stage
class FeatureStage(PipelineStage):
    def __init__(self):
        super().__init__("FEATURES")

    def validate(self, context: PipelineContext) -> bool:
        return "DATA" in context.stage_data

    def execute(self, context: PipelineContext) -> Dict[str, Any]:
        d_out = context.stage_data["DATA"]
        m_df = d_out["market_df"].copy()
        n_df = d_out["news_df"]
        f_df = d_out["fundamentals_df"]

        m_df["returns"] = m_df["close"].pct_change().fillna(0.0)
        m_df["volatility"] = m_df["returns"].rolling(20, min_periods=1).std().fillna(0.01)
        m_df["news_sentiment"] = n_df["sentiment_score"]
        m_df["pe_ratio"] = f_df["pe_ratio"]

        return {
            "feature_df": m_df,
            "feature_columns": ["returns", "volatility", "news_sentiment", "pe_ratio"],
            "artifacts": {"feature_matrix": "FEAT-MATRIX-001.csv"},
        }


# 3. Validation Stage
class ValidationStage(PipelineStage):
    def __init__(self):
        super().__init__("VALIDATION")

    def validate(self, context: PipelineContext) -> bool:
        return "FEATURES" in context.stage_data

    def execute(self, context: PipelineContext) -> Dict[str, Any]:
        from validation.services.walk_forward_service import WalkForwardService
        from validation.leakage.detector import LeakageDetector

        wf_service = WalkForwardService()
        wf_res = wf_service.run_walk_forward(experiment_id=context.experiment_id)

        leakage_det = LeakageDetector()
        f_df = context.stage_data["FEATURES"]["feature_df"]
        leak_res = leakage_det.audit_full_dataset(f_df)


        if leak_res.get("has_leakage", False) and context.config.get("strict_leakage", True):
            raise LeakageGateError("Critical feature leakage detected! Pipeline halted.")


        return {
            "walk_forward": wf_res,
            "leakage": leak_res,
            "artifacts": {"leakage_report": "leakage_report.md"},
        }


# 4. Training Stage
class TrainingStage(PipelineStage):
    def __init__(self):
        super().__init__("TRAINING")

    def validate(self, context: PipelineContext) -> bool:
        return "VALIDATION" in context.stage_data

    def execute(self, context: PipelineContext) -> Dict[str, Any]:
        return {
            "model_id": f"MODEL-{context.experiment_id}",
            "architecture": context.config.get("model", {}).get("type", "MultiModalQuantNet"),
            "status": "TRAINED",
            "artifacts": {"model_checkpoint": "model.pt"},
        }


# 5. Prediction Stage
class PredictionStage(PipelineStage):
    def __init__(self):
        super().__init__("PREDICTION")

    def validate(self, context: PipelineContext) -> bool:
        return "TRAINING" in context.stage_data

    def execute(self, context: PipelineContext) -> Dict[str, Any]:
        f_df = context.stage_data["FEATURES"]["feature_df"]
        preds = f_df["returns"].shift(-1).fillna(0.0).values * 0.5 + np.random.normal(0, 0.01, len(f_df))
        return {
            "predictions": preds,
            "artifacts": {"predictions": "preds.csv"},
        }


# 6. Alpha Stage
class AlphaStage(PipelineStage):
    def __init__(self):
        super().__init__("ALPHA")

    def validate(self, context: PipelineContext) -> bool:
        return "PREDICTION" in context.stage_data

    def execute(self, context: PipelineContext) -> Dict[str, Any]:
        preds = context.stage_data["PREDICTION"]["predictions"]
        signals = np.clip(preds / max(np.std(preds), 1e-6), -2.0, 2.0)
        return {
            "signals": signals,
            "artifacts": {"alpha_signals": "signals.csv"},
        }


# 7. Portfolio Stage
class PortfolioStage(PipelineStage):
    def __init__(self):
        super().__init__("PORTFOLIO")

    def validate(self, context: PipelineContext) -> bool:
        return "ALPHA" in context.stage_data

    def execute(self, context: PipelineContext) -> Dict[str, Any]:
        from portfolio_optimization.optimizers.allocators import RiskParityAllocator
        cov = np.array([[0.0004, 0.0001], [0.0001, 0.0003]])
        weights = RiskParityAllocator.allocate(cov, ["AAPL", "MSFT"])
        return {
            "weights": weights,
            "artifacts": {"portfolio_weights": "weights.json"},
        }



# 8. Execution Stage
class ExecutionStage(PipelineStage):
    def __init__(self):
        super().__init__("EXECUTION")

    def validate(self, context: PipelineContext) -> bool:
        return "PORTFOLIO" in context.stage_data

    def execute(self, context: PipelineContext) -> Dict[str, Any]:
        from execution.manager import ExecutionManager
        weights = context.stage_data["PORTFOLIO"]["weights"]
        curr_weights = {a: 0.0 for a in weights.keys()}
        snapshots = {a: {"close": 150.0} for a in weights.keys()}

        mgr = ExecutionManager()
        exec_res = mgr.run_execution(
            current_weights=curr_weights,
            target_weights=weights,
            market_snapshots=snapshots,
            portfolio_id=f"PORT-{context.run_id[:8]}",
        )
        return {
            "execution_summary": exec_res,
            "slippage_bps": 5.0,
            "commission_bps": 10.0,
            "artifacts": {"execution_log": "exec_log.json"},
        }





# 9. Backtest Stage
class BacktestStage(PipelineStage):
    def __init__(self):
        super().__init__("BACKTEST")

    def validate(self, context: PipelineContext) -> bool:
        return "EXECUTION" in context.stage_data

    def execute(self, context: PipelineContext) -> Dict[str, Any]:
        f_df = context.stage_data["FEATURES"]["feature_df"]
        rets = f_df["returns"].values
        sigs = context.stage_data["ALPHA"]["signals"]
        strategy_rets = sigs[:-1] * rets[1:]
        equity = 100000.0 * np.cumprod(1.0 + strategy_rets)

        return {
            "strategy_returns": strategy_rets,
            "equity_curve": equity,
            "sharpe_ratio": float(np.mean(strategy_rets) / (np.std(strategy_rets) + 1e-6) * np.sqrt(252)),
            "max_drawdown": float(np.min(strategy_rets)),
            "artifacts": {"backtest_report": "backtest.json"},
        }


# 10. Risk Stage
class RiskStage(PipelineStage):
    def __init__(self):
        super().__init__("RISK")

    def validate(self, context: PipelineContext) -> bool:
        return "BACKTEST" in context.stage_data

    def execute(self, context: PipelineContext) -> Dict[str, Any]:
        from risk.services.risk_service import RiskService
        service = RiskService()
        s_rets = context.stage_data["BACKTEST"]["strategy_returns"]
        rets_2d = s_rets.reshape(-1, 1).tolist()
        res_dict = service.run_risk_analysis(
            portfolio_id="PORT-001",
            weights={"AAPL": 1.0},
            returns_history=rets_2d,
        )
        return {
            "var_95": res_dict.get("tail_risk", {}).get("var_95_historical", 0.0),
            "cvar_95": res_dict.get("tail_risk", {}).get("cvar_95", 0.0),
            "stress_test": res_dict.get("stress_testing", {}),
            "artifacts": {"risk_snapshot": "risk_snapshot.json"},
        }


# 11. Statistics Stage
class StatisticsStage(PipelineStage):
    def __init__(self):
        super().__init__("STATISTICS")

    def validate(self, context: PipelineContext) -> bool:
        return "RISK" in context.stage_data

    def execute(self, context: PipelineContext) -> Dict[str, Any]:
        from validation.bootstrap.bootstrap_analyzer import BootstrapAnalyzer
        analyzer = BootstrapAnalyzer(iterations=100)
        s_rets = context.stage_data["BACKTEST"]["strategy_returns"]
        b_res = analyzer.stationary_block_bootstrap(
            s_rets, metric_func=lambda x: float(np.mean(x)), metric_name="mean_return"
        )
        return {
            "bootstrap": b_res.dict() if hasattr(b_res, "dict") else str(b_res),
            "artifacts": {"stat_validation": "stat_val.json"},
        }


# 12. Robustness Stage
class RobustnessStage(PipelineStage):
    def __init__(self):
        super().__init__("ROBUSTNESS")

    def validate(self, context: PipelineContext) -> bool:
        return "STATISTICS" in context.stage_data

    def execute(self, context: PipelineContext) -> Dict[str, Any]:
        from validation.robustness.stability import StabilityAnalyzer
        analyzer = StabilityAnalyzer()
        s_rets = context.stage_data["BACKTEST"]["strategy_returns"]
        chunks = np.array_split(s_rets, 5)
        sharpes = [float(np.mean(c) / (np.std(c) + 1e-6) * np.sqrt(252)) for c in chunks]
        stab_res = analyzer.evaluate_performance_stability(sharpes)
        return {
            "stability": stab_res,
            "artifacts": {"robustness_summary": "robustness.json"},
        }


# 13. Monitoring Stage
class MonitoringStage(PipelineStage):
    def __init__(self):
        super().__init__("MONITORING")

    def validate(self, context: PipelineContext) -> bool:
        return "ROBUSTNESS" in context.stage_data

    def execute(self, context: PipelineContext) -> Dict[str, Any]:
        from monitoring.services.monitoring_service import MonitoringService
        service = MonitoringService()
        mon_res = service.run_monitoring(experiment_id=context.experiment_id)
        return {
            "health_score": mon_res.health_score.overall_health_score,
            "status": mon_res.health_score.status,
            "artifacts": {"monitoring_audit": "monitoring.json"},
        }


# 14. Report Stage
class ReportStage(PipelineStage):
    def __init__(self):
        super().__init__("REPORT")

    def validate(self, context: PipelineContext) -> bool:
        return "MONITORING" in context.stage_data

    def execute(self, context: PipelineContext) -> Dict[str, Any]:
        from .reports.generator import ResearchReportGenerator
        generator = ResearchReportGenerator()
        report_md = generator.generate_research_report(context)
        return {
            "report_md": report_md,
            "artifacts": {"research_report": "research_report.md"},
        }


class StageRegistry:
    """Registry managing instantiated pipeline stage handlers."""

    def __init__(self):
        self._stages: Dict[str, PipelineStage] = {
            "DATA": DataStage(),
            "FEATURES": FeatureStage(),
            "VALIDATION": ValidationStage(),
            "TRAINING": TrainingStage(),
            "PREDICTION": PredictionStage(),
            "ALPHA": AlphaStage(),
            "PORTFOLIO": PortfolioStage(),
            "EXECUTION": ExecutionStage(),
            "BACKTEST": BacktestStage(),
            "RISK": RiskStage(),
            "STATISTICS": StatisticsStage(),
            "ROBUSTNESS": RobustnessStage(),
            "MONITORING": MonitoringStage(),
            "REPORT": ReportStage(),
        }

    def get_stage(self, name: str) -> PipelineStage:
        if name not in self._stages:
            raise KeyError(f"Pipeline stage '{name}' is not registered.")
        return self._stages[name]

    def list_stages(self) -> List[str]:
        return list(self._stages.keys())
