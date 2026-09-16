"""
Bootstrap Analyzer for Empirical & Stationary Block Bootstrap Confidence Intervals.
"""

import numpy as np
from typing import Dict, Any, List, Callable
from validation.schemas.validation_schema import BootstrapResult


class BootstrapAnalyzer:
    """
    Performs empirical & stationary block bootstrap to generate confidence intervals.
    Preserves time-series dependence structure via block sampling.
    """

    def __init__(
        self,
        iterations: int = 1000,
        confidence_level: float = 0.95,
        block_size: int = 20,
        random_seed: int = 42,
    ):
        self.iterations = iterations
        self.confidence_level = confidence_level
        self.block_size = block_size
        self.random_seed = random_seed

    def stationary_block_bootstrap(
        self,
        series: np.ndarray,
        metric_func: Callable[[np.ndarray], float],
        metric_name: str = "mean_return",
    ) -> BootstrapResult:
        np.random.seed(self.random_seed)
        n = len(series)
        if n == 0:
            return BootstrapResult(
                metric=metric_name,
                estimate=0.0,
                lower_bound=0.0,
                upper_bound=0.0,
            )

        point_estimate = float(metric_func(series))
        boot_estimates = []

        num_blocks = int(np.ceil(n / self.block_size))

        for _ in range(self.iterations):
            sampled_indices = []
            for _ in range(num_blocks):
                start_idx = np.random.randint(0, max(1, n - self.block_size + 1))
                sampled_indices.extend(range(start_idx, min(n, start_idx + self.block_size)))

            boot_sample = series[sampled_indices[:n]]
            boot_estimates.append(float(metric_func(boot_sample)))

        alpha = 1.0 - self.confidence_level
        lower_bound = float(np.percentile(boot_estimates, (alpha / 2.0) * 100))
        upper_bound = float(np.percentile(boot_estimates, (1.0 - alpha / 2.0) * 100))

        return BootstrapResult(
            metric=metric_name,
            estimate=round(point_estimate, 6),
            lower_bound=round(lower_bound, 6),
            upper_bound=round(upper_bound, 6),
            confidence_level=self.confidence_level,
            iterations=self.iterations,
            block_size=self.block_size,
            random_seed=self.random_seed,
            method="stationary_block",
        )
