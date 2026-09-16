# Quantitative Research Lineage Summary

**System**: QUANT AI Platform  
**Module**: Lineage & Traceability Engine  

---

## Lineage Traceability DAG

The platform maintains full end-to-end lineage mapping for every generated alpha signal, portfolio allocation, and out-of-sample backtest.

```
                 RESEARCH QUESTION
                         │
                         ▼
                    EXPERIMENT
                         │
                         ▼
                  DATASET VERSION (SHA-256 Fingerprint)
                         │
                         ▼
                  FEATURE VERSION (7 Feature Groups)
                         │
                         ▼
                    MODEL TRAIN (Config Snapshot & Git Commit)
                         │
                         ▼
                    VALIDATION
                         │
                         ▼
                     PREDICT
                         │
                         ▼
                      ALPHA
                         │
                         ▼
                    PORTFOLIO (Constraint Check)
                         │
                         ▼
                       RISK (VaR & Max Drawdown Limits)
                         │
                         ▼
                     BACKTEST
                         │
                         ▼
                    ROBUSTNESS
                         │
                         ▼
                    MODEL REGISTRY (EXPERIMENTAL -> VALIDATED -> PAPER)
                         │
                         ▼
                    PAPER TRADING (Order Execution Tracking)
                         │
                         ▼
                     MONITORING (Performance & Feature Drift)
                         │
                         ▼
                   RESEARCH REPORT & REPRODUCIBILITY CHECK
```

---

## Identity Formula

Every quantitative backtest or live trading session is uniquely identified by:

$$\text{Identity} = \text{Dataset} + \text{Feature Version} + \text{Model Version} + \text{Strategy Version} + \text{Portfolio Config} + \text{Risk Config} + \text{Cost Model}$$

This identity guarantees zero ambiguity and complete auditability for institutional compliance and internal research review.
