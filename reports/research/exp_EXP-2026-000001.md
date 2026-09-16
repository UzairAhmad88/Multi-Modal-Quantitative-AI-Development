# Quantitative Research Experiment Report: EXP-2026-000001

## 1. Objective & Hypothesis
* **Experiment ID:** `EXP-2026-000001`
* **Experiment Name:** Exp_Integration_Test_Workflow
* **Hypothesis ID:** `HYP-2026-EDE815`
* **Created Timestamp:** 2026-09-16T16:50:50.602649

## 2. Dataset & Features
* **Dataset:** `market_sp500`
* **Feature Set:** `market_return`, `news_sentiment`
* **Random Seed:** `42`

## 3. Model & Configuration
* **Model Architecture:** `Transformer`
* **Code Version:** `1.0.0`
* **Model Version:** `v1`

## 4. Empirical Performance Results
* **Directional Accuracy (Observed):** 58.00%
* **CAGR (Simulated):** 18.50%
* **Sharpe Ratio:** 1.72
* **Sortino Ratio:** 2.10
* **Max Drawdown:** 11.50%
* **Turnover:** 35.00%

## 5. Risk & Transaction Cost Metrics
* **VaR 95%:** 2.10%
* **CVaR 95%:** 3.40%
* **Simulated Transaction Cost:** 0.100%
* **Real-Money Trading:** DISABLED (Paper-Trading / Backtest Only)

## 6. Research Summary & Evidence-Based Statement
The empirical results measured during backtesting were consistent with the expected directional behavior.
No guaranteed return or risk-free performance is implied. Performance remains subject to regime changes.

## 7. Reproducibility
Reproduce this experiment locally via:
```bash
python scripts/research_intel.py experiment reproduce --id EXP-2026-000001
```
