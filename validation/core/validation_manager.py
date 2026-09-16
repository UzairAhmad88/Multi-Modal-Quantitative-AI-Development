"""
Central Statistical Validation Manager for Phase 24.
"""

import os
import json
import hashlib
import numpy as np
from typing import Dict, Any, List, Optional
from datetime import datetime

from validation.schemas.validation_schema import (
    StatisticalValidation,
    BootstrapResult,
    SignificanceResult,
    MultipleTestingResult,
    StabilityResult,
)
from validation.statistics.basic_stats import BasicStatisticsCalculator
from validation.bootstrap.bootstrap_analyzer import BootstrapAnalyzer
from validation.significance.hypothesis_tester import HypothesisTester
from validation.multiple_testing.multiple_testing import MultipleTestingCorrector
from validation.stability.stability_analyzer import StabilityAnalyzer
from validation.diagnostics.overfitting_diagnostics import OverfittingDiagnostics
from validation.diagnostics.assumption_checker import AssumptionChecker


class StatisticalValidationManager:
    """
    Central manager executing full statistical validation pipelines over return series.
    """

    def __init__(self, storage_dir: str = "artifacts/validation"):
        self.storage_dir = storage_dir
        os.makedirs(self.storage_dir, exist_ok=True)
        os.makedirs(os.path.join(self.storage_dir, "statistical"), exist_ok=True)

    def compute_config_hash(self, experiment_id: str, config: Dict[str, Any], seed: int) -> str:
        norm_json = json.dumps({"exp": experiment_id, "cfg": config, "seed": seed}, sort_keys=True)
        return hashlib.sha256(norm_json.encode("utf-8")).hexdigest()

    def run_validation(
        self,
        experiment_id: str,
        returns: np.ndarray,
        benchmark_returns: Optional[np.ndarray] = None,
        train_sharpe: float = 2.0,
        random_seed: int = 42,
        config: Optional[Dict[str, Any]] = None,
    ) -> StatisticalValidation:
        val_id = f"VAL-{experiment_id}"
        cfg = config or {}
        config_hash = self.compute_config_hash(experiment_id, cfg, random_seed)

        n = len(returns)
        if n < 10:
            val = StatisticalValidation(
                validation_id=val_id,
                experiment_id=experiment_id,
                dataset_id=cfg.get("dataset_id", "DS-SP500"),
                validation_status="INSUFFICIENT_SAMPLE",
                configuration_hash=config_hash,
                sample_size=n,
            )
            self.save_validation(val)
            return val

        # 1. Basic Statistics & Parametric CI
        basic_stats = BasicStatisticsCalculator.calculate_moments(returns)
        param_ci = BasicStatisticsCalculator.parametric_confidence_interval(returns, confidence_level=0.95)

        # 2. Bootstrap
        analyzer = BootstrapAnalyzer(iterations=500, block_size=20, random_seed=random_seed)
        boot_res = analyzer.stationary_block_bootstrap(returns, np.mean, metric_name="mean_return")

        # 3. Significance Testing
        sig_res = HypothesisTester.one_sample_t_test(returns, null_value=0.0)

        # 4. Multiple Testing
        mt_res = MultipleTestingCorrector.benjamini_hochberg([sig_res.p_value, 0.04, 0.12])

        # 5. Stability Analysis
        stab_res = StabilityAnalyzer.analyze_subperiods(returns, num_windows=5)

        # 6. Diagnostics & Assumption Checks
        checks, flags = AssumptionChecker.check_all(returns, min_observations=126)
        gap_res = OverfittingDiagnostics.evaluate_generalization_gap(
            train_sharpe=train_sharpe,
            test_sharpe=basic_stats.get("mean", 0.0) * 15.8,  # Approximate annual Sharpe
        )
        flags.extend(gap_res["integrity_flags"])

        val = StatisticalValidation(
            validation_id=val_id,
            experiment_id=experiment_id,
            backtest_id=f"BT-{experiment_id}",
            evaluation_id=f"EVAL-{experiment_id}",
            dataset_id=cfg.get("dataset_id", "DS-SP500"),
            validation_status="VALID",
            configuration_hash=config_hash,
            sample_size=n,
            basic_statistics=basic_stats,
            confidence_intervals=param_ci,
            bootstrap_results=[boot_res],
            significance_results=[sig_res],
            multiple_testing_result=mt_res,
            stability_result=stab_res,
            assumption_checks=checks,
            integrity_flags=flags,
        )

        self.save_validation(val)
        return val

    def save_validation(self, val: StatisticalValidation) -> str:
        filepath = os.path.join(self.storage_dir, "statistical", f"{val.validation_id}.json")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(val.model_dump_json(indent=2))
        return filepath

    def get_validation(self, validation_id_or_exp_id: str) -> Optional[StatisticalValidation]:
        filepath = os.path.join(self.storage_dir, "statistical", f"{validation_id_or_exp_id}.json")
        if not os.path.exists(filepath):
            filepath = os.path.join(self.storage_dir, "statistical", f"VAL-{validation_id_or_exp_id}.json")
        if not os.path.exists(filepath):
            return None
        with open(filepath, "r", encoding="utf-8") as f:
            return StatisticalValidation(**json.load(f))
