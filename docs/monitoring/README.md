# Phase 28: Model Monitoring, Data Drift, Concept Drift & Research Health OS

The **Model Monitoring & Research Health OS** provides real-time, institutional-grade evaluation of feature distributions, prediction drift, concept drift, alpha signal decay, macro regime shifts, and overall research integrity across the Multi-Modal Quant AI platform.

---

## Key Features & Architecture

1. **Multi-Feature Data Drift Detection (`monitoring/data_drift/`)**:
   - `DataDriftDetector`: Population Stability Index (PSI), 2-sample Kolmogorov-Smirnov (KS) statistical tests, and Wasserstein (Earth Mover) distance metrics across daily market bars, FinBERT news sentiment, and SEC fundamental features.

2. **Feature & Correlation Matrix Shift (`monitoring/feature_drift/`)**:
   - `FeatureDriftMonitor`: Tracks cosine similarity and Spearman rank correlation of feature importance vectors across folds.
   - `calculate_correlation_matrix_shift`: Measures Frobenius norm shifts ($\|\Delta R\|_F$) in pairwise feature correlation matrices.

3. **Prediction Output & Confidence Decay (`monitoring/prediction_drift/`)**:
   - `OutputPredictionMonitor`: Evaluates model output distribution shifts (mean, std, skewness, kurtosis) and signal confidence decay.

4. **Streaming Concept Drift Detectors (`monitoring/concept_drift/`)**:
   - `DDM`: Drift Detection Method tracking error rate standard deviation bounds ($\mu + 2\sigma$ warning, $\mu + 3\sigma$ drift).
   - `EDDM`: Early Drift Detection Method tracking distances between consecutive prediction errors.
   - `PageHinkley`: Cumulative sum test for sequential change-point detection.

5. **Performance & Alpha Signal Decay (`monitoring/performance/`)**:
   - `calculate_accuracy_decay`: Tracks rolling OOS MAE, RMSE, F1, and directional accuracy degradation.
   - `AlphaDecayTracker`: Computes rolling Information Coefficient (IC), Rank IC, IC half-life decay, and IC degradation percentages.
   - `calculate_sharpe_decay`: Monitors rolling Sharpe ratio degradation and drawdown accumulation.

6. **Macro Regime Transition Detector (`monitoring/regime/`)**:
   - `RegimeChangeDetector`: EWMA/GARCH volatility jump ratio detector and Markov 2-state/4-state transition probability estimator (Bull, Bear, High Volatility, Stagnant).

7. **Composite Research Health Score (`monitoring/health/`)**:
   - `calculate_research_health_score`: Calculates a normalized **Research Health Score ($0 - 100$)** aggregating Data Quality ($20\%$), Feature Stability ($20\%$), Concept Stability ($20\%$), Alpha Retention ($20\%$), and Risk Compliance ($20\%$).

8. **CLI Tools (`monitoring/cli/`)**:
   - `run.py`, `drift.py`, `health.py`, `report.py`.

9. **REST API & Interactive Dashboard Page**:
   - Endpoints at `/monitoring/run`, `/monitoring/runs`, `/monitoring/{id}`, `/monitoring/drift-check`, `/monitoring/health`.
   - **35th Streamlit Workspace Page**: `dashboard/pages/35_Model_Monitoring_OS.py`.

---

## Quick Start CLI Usage

```bash
# Run complete model monitoring audit
python monitoring/cli/run.py --experiment EXP-001 --save-report

# Run standalone data drift audit between CSV files
python monitoring/cli/drift.py --baseline data/base.csv --target data/curr.csv
```
