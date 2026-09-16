# Phase 17: Quantitative Data Platform, Point-in-Time Data Store, Feature Store & Dataset Lineage

## 1. System Overview
The Quantitative Data Platform serves as the single source of truth for quantitative financial data, feature engineering, point-in-time temporal alignment, dataset versioning, immutable snapshot management, and lineage tracing across the Multi-Modal Quant AI platform.

It standardizes the full quantitative data flow:
```text
EXTERNAL SOURCES -> INGESTION -> RAW STORAGE -> NORMALIZATION -> DATA QUALITY -> POINT-IN-TIME ALIGNMENT -> FEATURE STORE -> DATASET BUILDER -> VERSIONED DATASET & SNAPSHOT -> MODEL FACTORY
```

---

## 2. Directory Architecture
```text
data_platform/
├── ingestion/        # DataSource interface and connectors for Market, News, and Fundamentals
├── raw/              # RawDataStore managing immutable payload storage
├── normalization/    # DataNormalizer standardizing UTC timestamps, uppercase symbols, and numeric types
├── quality/          # DataQualityEngine validating schemas, range bounds, price sanity, null thresholds, and deduplication
├── point_in_time/    # PointInTimeManager executing point-in-time queries (get_available_data, get_asof) to prevent look-ahead bias
├── features/         # FeatureEngine computing technical, price, volume, volatility, fundamental, and sentiment features
├── feature_store/    # FeatureStoreRegistry cataloging feature definitions, formulas, versions, and feature sets
├── cache/            # FeatureCache disk-backed caching based on hash signatures
├── datasets/         # DatasetBuilder constructing versioned (DATASET-YYYYMMDD-XXXX) datasets with temporal splits
├── versioning/       # SnapshotManager creating immutable snapshots with SHA-256 data hashes
├── lineage/          # DataLineageTracer tracking DAG dependencies from Raw -> Features -> Dataset -> Model
├── metadata/         # SymbolMaster reference database and TradingCalendar market session rules
├── cli/              # CLI scripts (ingest.py, validate.py, features.py, build_dataset.py, inspect.py, features_registry.py)
└── manager.py        # Master DataPlatformManager unifying the platform
```

---

## 3. CLI Tools
```bash
# Ingest Data
python data_platform/cli/ingest.py --source market --symbols AAPL MSFT

# Validate Dataset Quality
python data_platform/cli/validate.py --dataset DATASET-001

# Compute Quantitative Features
python data_platform/cli/features.py --symbols AAPL MSFT --feature-set technical_v1

# Build Versioned Dataset
python data_platform/cli/build_dataset.py --name multimodal_daily --symbols AAPL MSFT NVDA

# Inspect Dataset Metadata
python data_platform/cli/inspect.py --dataset DATASET-001

# Catalog Feature Store Registry
python data_platform/cli/features_registry.py --list
```

---

## 4. REST API Endpoints
- `GET /api/v1/data/sources`
- `GET /api/v1/data/status`
- `POST /api/v1/data/ingest`
- `POST /api/v1/data/validate`
- `GET /api/v1/data/datasets`
- `GET /api/v1/data/datasets/{id}`
- `POST /api/v1/data/datasets/build`
- `GET /api/v1/features`
- `GET /api/v1/features/{id}`
- `POST /api/v1/features/compute`
- `GET /api/v1/features/{id}/lineage`
- `GET /api/v1/data/quality/{id}`
- `GET /api/v1/data/lineage/{id}`

---

## 5. Point-in-Time Integrity & Leakage Protection
- **News Alignment**: Enforces `available_at <= timestamp` restriction to prevent look-ahead bias on news published after prediction cutoff.
- **Fundamental Alignment**: Enforces `public_release_date` / `available_at` cutoff rather than quarter end dates.
- **Data Quality**: Validates high $\ge$ low price bounds, non-negative price/volume rules, and maximum daily price jump thresholds.
