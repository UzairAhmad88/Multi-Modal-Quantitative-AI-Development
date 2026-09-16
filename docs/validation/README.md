# Phase 24: Statistical Validation & Research Integrity OS

The **Statistical Validation & Research Integrity Engine** evaluates whether quantitative research results are statistically meaningful, stable, and reproducible. It consumes return series and evaluation metrics from existing engines (`backtests/`, `research_evaluation/`) without duplicating logic.

## Key Features

1. **Basic Moments & Parametric Confidence Intervals (`validation/statistics/`)**:
   - Higher-order moments (mean, std, skewness, kurtosis) and parametric confidence intervals.

2. **Stationary Block Bootstrap (`validation/bootstrap/`)**:
   - `BootstrapAnalyzer`: Stationary block bootstrap preserving time-series temporal dependence structure with configurable `block_size` and `iterations`.

3. **Significance Testing & Effect Sizes (`validation/significance/`)**:
   - `HypothesisTester`: 1-sample, 2-sample paired t-tests, p-values, and Cohen's d effect sizes.

4. **Multiple Testing Adjustments (`validation/multiple_testing/`)**:
   - `MultipleTestingCorrector`: Bonferroni, Holm-Bonferroni, and Benjamini-Hochberg (FDR) adjustments for multiple hypothesis testing.

5. **Temporal Stability Analysis (`validation/stability/`)**:
   - `StabilityAnalyzer`: Subperiod window breakdown, rolling metric dispersion, and stability scoring ($0$ to $100$).

6. **Overfitting Diagnostics & Assumption Checker (`validation/diagnostics/`)**:
   - `OverfittingDiagnostics`: Train/test Sharpe gap degradation and generalization gap analysis.
   - `AssumptionChecker`: Normality and minimum sample size verification.

7. **Research Integrity Flags (`validation/schemas/`)**:
   - Structured technical flags (`LOOK_AHEAD_RISK`, `DATA_LEAKAGE`, `MULTIPLE_TESTING`, `SMALL_SAMPLE`, `PARAMETER_INSTABILITY`, `REGIME_INSTABILITY`, `HIGH_COST_SENSITIVITY`, `TRAIN_TEST_GAP`) with `INFO`, `WARNING`, or `CRITICAL` severity.

8. **CLI Tools (`validation/cli/`)**:
   - `run.py`, `inspect.py`, `compare.py`, `bootstrap.py`, `significance.py`, `stability.py`, `multiple_testing.py`, `report.py`.

9. **REST API & Dashboard Page**:
   - Endpoints at `/validation/run`, `/validation/{id}`, `/validation/{id}/bootstrap`, `/validation/{id}/significance`, `/validation/{id}/stability`, `/validation/{id}/multiple-testing`, `/validation/{id}/report`, `/validation/compare`, `/validation/health`.
   - **31st Streamlit Workspace Page**: `dashboard/pages/31_Statistical_Validation_OS.py`.

## Quick Start CLI Usage

```bash
# Execute statistical validation for experiment
python validation/cli/run.py --experiment EXP-001 --seed 42

# Inspect validation results
python validation/cli/inspect.py --validation VAL-EXP-001

# Inspect stationary block bootstrap confidence intervals
python validation/cli/bootstrap.py --validation VAL-EXP-001

# Generate Markdown validation report
python validation/cli/report.py --validation VAL-EXP-001
```
