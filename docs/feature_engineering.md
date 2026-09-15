# Feature Engineering & Multi-Modal Fusion Documentation

## Overview
The feature engineering module generates 247 standardized quantitative features across five primary domains:

1. **Market Technical Features**: Returns (1D, 5D, 21D), SMAs (20D, 50D, 200D), RSI (14D), MACD, Bollinger Bands, ATR, 20D Volatility.
2. **News NLP Sentiment Features**: VADER & FinBERT Polarity Scores, 5D Rolling Sentiment Momentum, Article Count.
3. **Fundamental Ratios**: P/E, P/B, ROE, Debt/Equity, Free Cash Flow Margin, Revenue Growth, EPS Growth, Fundamental Rating.
4. **Macro Features**: VIX Level, Treasury Yield Spread, Macro Expansion Regime Indicator.
5. **Cross-Asset Features**: SPY Beta, Sector Relative Momentum.
