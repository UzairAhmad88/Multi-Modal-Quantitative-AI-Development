# Phase 20: Research Evaluation & Statistical Validation OS

## Overview

Phase 20 provides a research-grade evaluation and validation layer for analyzing backtest strategies, portfolio allocations, and execution simulation performance out-of-sample. It computes performance ratios (Sharpe, Sortino, Calmar, CAGR, Max Drawdown), runs statistical hypothesis testing (t-tests, bootstrap 95% CIs, permutation tests, stationarity, ACF), detects data leakage, performs walk-forward cross-validation, benchmarks against market baselines, assesses market regime performance, runs parameter sensitivity & robustness analysis, computes overfitting diagnostics, performs multimodal ablation studies, and generates interactive Markdown and HTML research reports.

## Key Modules

### 1. Performance & Drawdown Engine (`research_evaluation/metrics/`)
- `ReturnCalculator`: Simple, log, and cumulative returns, CAGR calculation.
- `DrawdownAnalyzer`: Peak-to-trough drawdowns, max drawdown, average drawdown, duration, and recovery tracking.
- `PerformanceMetricsEngine`: Sharpe Ratio, Sortino Ratio, Calmar Ratio, Win Rate, Profit Factor, and risk-adjusted metrics.

### 2. Statistical Validation (`research_evaluation/statistics/`)
- `SignificanceTester`: 1-sample t-test significance testing.
- `BootstrapEngine`: Empirical circular block bootstrap confidence intervals for Sharpe ratio.
- `PermutationTester`: Permutation test against null hypothesis of zero temporal predictability.
- `StationarityTester`: ADF stationarity testing on return series.
- `AutocorrelationAnalyzer`: ACF and PACF serial correlation analysis.
- `DistributionAnalyzer`: Moments (mean, std, skewness, kurtosis), VaR, CVaR, and left-tail loss frequency.

### 3. Out-Of-Sample Validation (`research_evaluation/validation/`, `research_evaluation/walk_forward/`)
- `LeakageDetector`: Checks for look-ahead timestamps and availability violations.
- `WalkForwardEngine`: Rolling and expanding window walk-forward validation with purged CV and embargo gaps.

### 4. Benchmarking & Market Regimes (`research_evaluation/benchmarks/`, `research_evaluation/regime_analysis/`)
- `BenchmarkEngine`: Alpha, Beta, R-squared, Tracking Error, and Information Ratio.
- `RegimeAnalyzer`: Conditioned performance breakdown across Bull, Bear, High Volatility, and Low Volatility market regimes.

### 5. Sensitivity, Robustness & Overfitting (`research_evaluation/sensitivity/`, `research_evaluation/robustness/`, `research_evaluation/overfitting/`)
- `SensitivityEngine`: Cost grid sensitivity testing ($0$ to $20$ bps).
- `RobustnessEngine`: Multi-dimensional strategy stability scoring ($0$ to $100$).
- `OverfittingDetector`: Train-test degradation gap, parameter instability, and Deflated Sharpe ratio penalty.

### 6. Model Comparison & Ablation (`research_evaluation/model_comparison/`)
- `ICAnalyzer`: Pearson IC, Spearman Rank IC, ICIR, and signal decay profile.
- `AblationEngine`: Multimodal ablation study (Market, News, Fundamentals, Full Fusion).
- `StrategyComparisonEngine`: Side-by-side strategy metrics comparison.

### 7. Reports Generation (`research_evaluation/reports/`)
- `ResearchReportGenerator`: Compiles Markdown research report.
- `HTMLReportGenerator`: Builds standalone interactive HTML research report.

## Usage

### CLI Tools
```bash
# Run strategy evaluation
python research_evaluation/cli/evaluate.py --strategy STRATEGY-001 --config configs/evaluation/default.yaml

# Run walk-forward validation
python research_evaluation/cli/walk_forward.py --strategy STRATEGY-001 --config configs/evaluation/walk_forward.yaml

# Inspect strategy robustness
python research_evaluation/cli/robustness.py --evaluation EVAL-001

# Export research report
python research_evaluation/cli/report.py --evaluation EVAL-001 --format html
```

### REST API
- `POST /research/evaluate`
- `GET /research/evaluations`
- `GET /research/evaluations/{id}`
- `POST /research/walk-forward`
- `POST /research/robustness`
- `POST /research/sensitivity`
- `POST /research/compare`
- `GET /research/evaluations/{id}/report`

### Streamlit Workspace Page
- **Page 27**: `dashboard/pages/27_Research_Evaluation_OS.py`
