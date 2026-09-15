# Data Leakage Prevention Architecture & Rules

## 1. Core Principles
Quantitative AI models must strictly adhere to historical point-in-time data availability. The QUANT AI platform explicitly prevents data leakage across six critical dimensions:

---

## 2. Leakage Protection Mechanisms

### A. Temporal Order & Time-Series Splitting
- **Forbidden**: Random train/test split or K-Fold cross-validation.
- **Enforced**: Chronological train (70%), validation (15%), and test (15%) splitting without shuffling.
- **Rule**: `train_dates < val_dates < test_dates`.

### B. Feature Scaler Scoping
- **Forbidden**: Fitting `StandardScaler` or `MinMaxScaler` on the entire dataset prior to splitting.
- **Enforced**: Scalers are fit strictly on `train_df`, then applied via `transform()` to `val_df` and `test_df`.

### C. News & NLP Point-In-Time Policy
- **Rule**: News published at or after 21:00 UTC on day $T$ cannot affect trading decisions on day $T$.
- **Enforcement**: Shifted to effective date $T+1$ prior to daily sentiment aggregation.

### D. Quarterly Fundamentals Point-In-Time Policy
- **Rule**: Earnings statements are only available after SEC filing release (`public_release_date`), typically 30–45 days post quarter-end.
- **Enforcement**: Merged via `pd.merge_asof(direction='backward')` using `public_release_date`.

### E. Rolling Technical Indicators
- **Rule**: Rolling windows (e.g. 20D SMA, RSI, Volatility) use only backward-looking windows ($t \le T$).

### F. Execution Accounting & Signal Timing
- **Rule**: Signals are generated at market Close on day $T$. Execution occurs at market Open on day $T+1$ with 10 bps transaction fees and 5 bps slippage.
