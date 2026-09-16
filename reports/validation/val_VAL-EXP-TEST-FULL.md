# Statistical Validation & Research Integrity Report

## Metadata
- **Validation ID**: `VAL-EXP-TEST-FULL`
- **Experiment ID**: `EXP-TEST-FULL`
- **Status**: `VALID`
- **Configuration Hash**: `9a89210b00228dc3d2d5493085ef049fd7bb350e3011c956fc74c3b21ce5b5f7`
- **Sample Size**: `300` observations
- **Created At**: `2026-09-16T19:57:23.691219`

## Basic Statistics & Parametric Confidence Interval
- **Mean Return**: `0.000945`
- **Standard Deviation**: `0.009842`
- **Skewness**: `0.1743`
- **Kurtosis**: `0.5669`
- **Parametric 95% CI**: `[-0.000174, 0.002063]`

## Stationary Block Bootstrap Analysis
- **Metric**: `mean_return` | **Estimate**: `0.000945` | **95% Bootstrap CI**: `[-0.000147, 0.001842]` (Iterations: `500`, Block Size: `20`)

## Hypothesis Testing & Significance
- **Test**: `1-Sample t-Test` | **p-value**: `0.097517` | **t-stat**: `1.6622` | **Cohen's d**: `0.096` | **Significant (<0.05)**: `NO`

## Multiple Testing Correction (`Benjamini-Hochberg (FDR)`)
- **Number of Tests**: `3`
- **Adjusted p-values**: `[0.12, 0.12, 0.12]`

## Temporal Stability Analysis
- **Stability Score**: `58.7 / 100` | **Sharpe Std**: `1.3672` | **Drawdown Std**: `0.0303`

## Research Integrity Flags
- [IntegrityFlagSeverity.WARNING] **IntegrityFlagType.TRAIN_TEST_GAP**: High train/test performance gap detected (Train Sharpe: 2.00, Test Sharpe: 0.01, Gap: 1.99)

## Assumptions & Limitations
- Results are based on historical return series under explicit statistical assumptions.
- Statistical significance does not constitute a recommendation or guarantee of future performance.
