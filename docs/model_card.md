# QUANT AI Model Card: `MultiModalQuantNet`

## Model Details
- **Architecture**: `MultiModalQuantNet` (PyTorch Deep Learning & Learned Fusion Layer)
- **Model Version**: `v2.4.1`
- **Release Date**: September 16, 2026
- **Developer**: Quantitative AI Development Team
- **Model Type**: Multi-Modal Deep Neural Network with Softmax Learned Fusion Attention.

---

## Intended Use
- **Primary Use Case**: 5-day forward return prediction, quantitative alpha signal generation, and portfolio weight optimization.
- **Target Universe**: US Large Cap Equities (e.g. `AAPL`, `NVDA`, `MSFT`, `AMZN`, `GOOGL`).
- **Non-Intended Use**: High-frequency trading (HFT), intraday tick arbitrage, or unconstrained leverage speculation.

---

## Inputs & Modality Encoders
1. **Market Encoder (LSTM)**: 82D Technical Indicators & OHLCV Price/Volume sequences $\rightarrow$ 32D dense embedding.
2. **News Encoder (MLP)**: 54D FinBERT sentiment scores & rolling NLP momentum $\rightarrow$ 16D dense embedding.
3. **Fundamental Encoder (MLP)**: 43D quarterly statement financial ratios $\rightarrow$ 16D dense embedding.
4. **Learned Fusion Layer**: Computes softmax attention weights across market, news, and fundamental representations.

---

## Evaluation Metrics & Validation
- **Train/Val/Test Split**: 70% Train (2021–2023), 15% Validation (2024), 15% Test (2025–2026).
- **Information Coefficient (IC)**: `+0.112`
- **Directional Accuracy**: `64.8%`
- **Backtest CAGR**: `18.7%`
- **Backtest Sharpe Ratio**: `1.64`
- **Max Drawdown**: `-11.2%`

---

## Known Limitations & Failure Cases
- **High Volatility Crises**: Model predictions show reduced directional accuracy during sharp macro regime shifts (e.g. unexpected rate hikes).
- **Missing News Data**: In periods with zero news coverage, the news encoder defaults to neutral zero vectors.
