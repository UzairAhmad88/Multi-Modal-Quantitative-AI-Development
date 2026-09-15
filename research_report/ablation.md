# Modality Ablation Study

## Multi-Modal Feature Contribution Analysis
We conducted controlled experiments across identical time periods, cost assumptions (10 bps fee, 5 bps slippage), and risk constraints:

| Experiment | Modalities Included | Features | IC | RMSE | Annualized Return | Sharpe Ratio | Max Drawdown |
|------------|---------------------|----------|----|------|-------------------|--------------|--------------|
| **Exp A** | Market Technical Only | 24 | 0.068 | 0.0385 | +12.4% | 1.25 | -12.5% |
| **Exp B** | Market + News NLP | 34 | 0.092 | 0.0352 | +18.2% | 1.62 | -9.8% |
| **Exp C** | Market + Fundamentals | 36 | 0.095 | 0.0348 | +16.8% | 1.55 | -10.2% |
| **Exp D** | Multi-Modal Fusion | 46 | 0.125 | 0.0328 | +24.8% | 2.05 | -8.4% |

## Key Findings
1. **News NLP Sentiment** materially improves signal timing during earnings announcement periods, reducing drawdowns.
2. **Fundamental Financial Ratios** provide robust medium-term trend stability.
3. **Multi-Modal Fusion** yields the highest Information Coefficient (IC 0.125) and Sharpe ratio (2.05).
