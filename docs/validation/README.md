# Phase 13: Research-Grade Validation, Leakage Detection & Robustness System

## Architecture Overview

Phase 13 establishes a institutional-grade **Validation Architecture** (`validation/`) for the Multi-Modal Quant AI platform. The system audits empirical model performance to ensure observed results are statistically supported, free from future look-ahead bias, stable across temporal walk-forward splits, resilient under transaction cost stress, and fully reproducible.

```
DATA → QUALITY CHECK → LEAKAGE AUDIT → TEMPORAL CV → WALK-FORWARD → BOOTSTRAP CIs → STRESS TEST → REPRODUCIBILITY HASH → REPORT
```

---

## Core Validation Modules

### 1. Data Quality Validator (`validation/data_validation/quality.py`)
- Audits OHLC price sanity (`High >= max(Open, Close, Low)`, `Low <= min(Open, Close, High)`).
- Verifies non-negative volumes, missing value rates, and timestamp continuity.

### 2. Leakage Detector (`validation/leakage_detection/detector.py`)
- Checks for future publication timestamps (`publication_time <= prediction_time`).
- Detects scaler leakage (fitting normalization scalers on full dataset prior to train/test split).
- Identifies target label leakage and documents survivorship bias boundaries.
- **Critical Policy**: If look-ahead leakage is detected, `validation_status` sets to `FAILED` and displays `POTENTIAL DATA LEAKAGE`.

### 3. Temporal Validation & Walk-Forward (`validation/temporal_validation/`, `validation/walk_forward/`)
- Sequential chronological splits with purging and embargo periods.
- Walk-forward temporal cross-validation supporting expanding and rolling windows.

### 4. Statistical Testing & Bootstrap Engine (`validation/statistical_tests/`, `validation/bootstrap/`)
- One-tailed T-tests for positive return significance.
- 1,000-iteration non-parametric bootstrap resampling for 95% confidence intervals on Sharpe ratio and CAGR.
- Multiple-testing data-snooping warnings.

### 5. Monte Carlo & Stress Testing (`validation/monte_carlo/`, `validation/stress_testing/`)
- Trade path resampling for drawdown probability distributions.
- Transaction cost sweeps (0 to 20 bps) and market regime performance breakdowns (Bull, Bear, Sideways, High Volatility).

### 6. Overfitting Diagnostics & Attribution (`validation/overfitting/`, `validation/performance_attribution/`)
- Generalization gap calculation (`validation_metric - test_metric`).
- Confidence bucket calibration (Brier Score) and modality attribution.

### 7. Reproducibility Engine (`validation/robustness/reproducibility.py`)
- Generates SHA-256 validation hashes (`validation_id`, `experiment_id`, `config_hash`, `result_hash`, `code_version`, `seed`).

---

## CLI Reference

```bash
# Full 12-axis validation suite
python scripts/validate.py --experiment-id EXP-2026-000001

# Leakage audit only
python scripts/validate.py --leakage --experiment-id EXP-2026-000001

# Walk-forward CV only
python scripts/validate.py --walk-forward --experiment-id EXP-2026-000001

# Stress testing suite only
python scripts/validate.py --stress --experiment-id EXP-2026-000001

# Reproduce validation hash
python scripts/reproduce_validation.py --experiment-id EXP-2026-000001
```

---

## REST API Reference

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/validation/overview` | Validation engine status overview |
| `GET` | `/validation/experiments/{id}` | Audit summary for experiment |
| `POST` | `/validation/run` | Execute full 12-axis validation suite |
| `GET` | `/validation/leakage/{id}` | Leakage audit details |
| `GET` | `/validation/walk-forward/{id}` | Walk-forward OOS folds |
| `GET` | `/validation/stress/{id}` | Transaction cost and regime stress |
| `GET` | `/validation/statistics/{id}` | T-tests, CIs, and Monte Carlo |
| `GET` | `/validation/reproducibility/{id}` | Validation hash and seed log |
