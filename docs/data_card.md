# QUANT AI Data Card

## Data Modalities & Schema Specification

### 1. Market Data (OHLCV)
- **Source**: Polygon / YFinance / Stooq Data Loader.
- **Frequency**: Daily Bars.
- **Columns**: `date`, `ticker`, `open`, `high`, `low`, `close`, `adj_close`, `volume`.
- **Validation**: Enforces $High \ge Low$, $Volume \ge 0$, and timestamp monotonicity.

### 2. Financial News Data (NLP)
- **Source**: Financial News API / Demo Pipeline Generator.
- **Columns**: `article_id`, `ticker`, `published_at`, `source`, `headline`, `article_text`, `url`.
- **Point-in-Time Policy**: News articles published at or after 21:00 UTC are assigned effective availability date $T+1$.

### 3. Fundamental Data
- **Source**: SEC EDGAR Filings / Demo Statement Generator.
- **Columns**: `quarter_end_date`, `public_release_date`, `ticker`, `revenue`, `net_income`, `eps`, `ebitda`, `free_cash_flow`, `total_assets`, `total_liabilities`, `total_debt`, `cash`, `equity`, `shares_outstanding`.
- **Point-in-Time Policy**: Quarterly statements are merged via `pd.merge_asof(direction='backward')` using `public_release_date` (typically 30–45 days post quarter-end).
