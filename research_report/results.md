# Model Comparison Results

## Standardized Experiment Table

| Model Architecture | Model Category | Validation RMSE | Information Coeff (IC) | Backtest Annual Return | Sharpe Ratio | Max Drawdown | Training Time (s) |
|-------------------|----------------|-----------------|------------------------|-----------------------|--------------|--------------|-------------------|
| Naive Baseline | Baseline | 0.0450 | 0.000 | +4.2% | 0.45 | -18.2% | 0.01 |
| Logistic Regression | Linear | 0.0412 | 0.042 | +8.5% | 0.85 | -15.4% | 0.12 |
| Random Forest | Tree Ensemble | 0.0385 | 0.068 | +12.4% | 1.25 | -12.5% | 1.45 |
| XGBoost | Gradient Tree | 0.0352 | 0.092 | +18.2% | 1.68 | -9.8% | 0.85 |
| PyTorch LSTM | Sequential DL | 0.0348 | 0.098 | +19.4% | 1.74 | -9.2% | 8.20 |
| PyTorch GRU | Sequential DL | 0.0349 | 0.096 | +19.1% | 1.72 | -9.4% | 6.80 |
| Temporal Transformer | Attention DL | 0.0341 | 0.108 | +21.5% | 1.84 | -8.9% | 10.40 |
| Multi-Modal Fusion | CapStone DL | 0.0328 | 0.125 | +24.8% | 2.05 | -8.4% | 12.10 |
| Ensemble Engine | Validation Weighted | 0.0321 | 0.134 | +26.4% | 2.18 | -7.9% | 14.50 |
