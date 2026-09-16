# Phase 24 & Phase 27: Statistical Validation, Walk-Forward & Out-of-Sample Research OS

The **Statistical & Walk-Forward Validation OS** evaluates whether quantitative research results are statistically meaningful, stable, reproducible, and robust against out-of-sample temporal degradation. It consumes return series, feature matrices, and evaluation metrics from existing engines (`backtests/`, `research_evaluation/`, `portfolio/`, `risk/`) without duplicating logic.

---

## Phase 27: Walk-Forward Validation & Anti-Overfitting OS Features

1. **Temporal Timeline & Date-Based Splitting (`validation/temporal/`)**:
   - `TimelineValidator`: Validates non-overlapping decision boundaries, timestamp sorting, point-in-time availability timestamps, and horizon compatibility.
   - Date-based explicit date ranges take precedence over percentage split ratios.

2. **Walk-Forward Generators (`validation/walk_forward/`)**:
   - `ExpandingWindowGenerator`: Anchored start date with expanding train periods.
   - `RollingWindowGenerator`: Fixed rolling train window moved sequentially across the timeline.
   - `AnchoredWindowGenerator`: Fixed training window start with sliding validation/test horizons.
   - `WalkForwardEngine`: Automated execution across repeated train/validation/test cycles.

3. **Purged & Embargoed Cross-Validation (`validation/purged/`)**:
   - `LabelHorizonPurger`: Marcos López de Prado style label overlap purger removing training samples overlapping evaluation label horizons (`t` to `t+k`).
   - `EmbargoExcluder`: Excludes post-evaluation observations to eliminate autocorrelation contamination.
   - `PurgedTimeSeriesSplitter`: Integrates purging and embargo into sklearn-compatible CV splitters.

4. **6-Stage Data Leakage Detection (`validation/leakage/`)**:
   - `FeatureLeakageAuditor`: Detects future-derived indicators, look-ahead features, and correlation anomalies ($r > 0.99$).
   - `LabelLeakageAuditor`: Detects direct/indirect label target contamination in feature matrices.
   - `TemporalLeakageAuditor`: Verifies strict chronological ordering (`train_end <= val_start`).
   - `AvailabilityAuditor`: Audits point-in-time availability timestamps (`availability <= decision`).
   - `PreprocessingLeakageAuditor`: Enforces feature scalers, imputers, PCA, and encoders are fit *only* on training folds.
   - `LeakageDetector`: Master 6-stage leakage orchestrator generating markdown leakage reports.

5. **Out-of-Sample (OOS) Prediction Storage & Metrics (`validation/oos/`)**:
   - `OOSPredictionStore`: Structured storage for OOS predictions, actuals, windows, and symbols.
   - `OOSMetricsCalculator`: Computes regression (MAE, MSE, RMSE, MAPE) and classification (Accuracy, Precision, Recall, F1) metrics across concatenated OOS windows.
   - `OOSEvaluator`: Links OOS predictions to signal generation, portfolio optimization, execution simulation, and backtesting.

6. **Robustness & Stability Analysis (`validation/robustness/`)**:
   - `StabilityAnalyzer`: Analyzes cross-window performance dispersion, drawdown stability, and worst/best window spread.
   - `ParameterSensitivityEngine`: Grid evaluations across lookbacks, thresholds, rebalance frequencies, and model sizes.
   - `RegimeOOSAnalyzer`: Maps OOS metrics to macro market regimes without look-ahead bias.

7. **Test-Set Lock Mechanism (`validation/core/test_lock.py`)**:
   - `TestSetLockEngine`: Enables `TEST_SET_LOCKED` protection to prevent post-hoc hyperparameter tuning or silent reuse of final out-of-sample test evaluation data. Maintains audit trail access logs.

8. **REST API & Dashboard Page**:
   - Endpoints at `/validation/walk-forward/run`, `/validation/walk-forward/{id}`, `/validation/walk-forward/{id}/windows`, `/validation/walk-forward/{id}/predictions`, `/validation/walk-forward/{id}/metrics`, `/validation/walk-forward/{id}/leakage`, `/validation/walk-forward/{id}/robustness`, `/validation/walk-forward/{id}/report`, `/validation/walk-forward/leakage-check`, `/validation/walk-forward/health`.
   - **34th Streamlit Workspace Page**: `dashboard/pages/34_Walk_Forward_Validation_OS.py`.

---

## Quick Start CLI Usage

```bash
# Execute statistical validation for experiment
python validation/cli/run.py --experiment EXP-001 --seed 42

# Execute Walk-Forward Validation Engine
python validation/cli/run.py --experiment EXP-001 --method expanding --train 504 --test 63

# Perform 6-Stage Data Leakage Audit
python validation/cli/leakage.py --experiment EXP-001

# Inspect stationary block bootstrap confidence intervals
python validation/cli/bootstrap.py --validation VAL-EXP-001

# Generate Markdown validation report
python validation/cli/report.py --validation VAL-EXP-001
```

