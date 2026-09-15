# Data Pipeline & Synchronization

## Temporal Alignment Policy
To eliminate lookahead data leakage:
- Market OHLCV prices are aligned on trading date $T$.
- News articles published after 21:00 UTC are shifted to effective availability date $T+1$.
- Quarterly fundamentals are merged using `public_release_date` (SEC filing release timestamp, typically 30–45 days post quarter-end) via `pd.merge_asof(direction='backward')`.
