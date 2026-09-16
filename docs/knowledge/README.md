# Phase 23: Quant Research Knowledge Base, Experiment Intelligence & Knowledge Graph OS

The **Quant Research Knowledge & Experiment Intelligence Layer** sits on top of all existing research modules (`data_platform/`, `model_factory/`, `portfolio_optimization/`, `execution/`, `backtests/`, `research_evaluation/`, `research_lab/`, `orchestrator/`). It indexes completed and failed experiments, preserves research lineage, builds evidence-driven research claims and journal entries, performs multi-faceted structured and semantic search, constructs interactive research knowledge graphs, generates reproducibility cards, and performs controlled side-by-side experiment comparisons.

## Core Components

1. **Schemas & Models (`knowledge/schemas/`)**:
   - `ResearchKnowledgeRecord`: Central immutable snapshot linking Experiment, Dataset, Features, Model, Strategy, Backtest, Evaluation, and Reports.
   - `ResearchClaim`: Structured claims (`OBSERVED`, `STATISTICAL`, `HYPOTHESIS`, `UNSUPPORTED`, `REJECTED`) linked directly to empirical experiment evidence.
   - `ResearchJournalEntry`: Qualitative research logs (`OBSERVATION`, `HYPOTHESIS`, `DECISION`, `RESULT`, `FAILURE`, `LIMITATION`, `FOLLOW_UP`).
   - `ReproducibilityCard`: Verifiable snapshot storing code version, random seed, dataset version, feature version, model version, environment info, and SHA256 configuration hash.
   - `ExperimentFamily`: Groups parent and child ablation experiments across modalities (`Market`, `Market + News`, `Market + Fundamentals`, `All`).

2. **Knowledge Repository (`knowledge/repository/`)**:
   - Manages record persistence, configuration hash deduplication, and lookup by experiment ID.

3. **Lineage Service & Knowledge Graph (`knowledge/lineage/`, `knowledge/graph/`)**:
   - `ResearchLineageService`: Resolves complete pipeline DAG lineage (`Dataset` $\rightarrow$ `Feature` $\rightarrow$ `Model` $\rightarrow$ `Signal` $\rightarrow$ `Portfolio` $\rightarrow$ `Execution` $\rightarrow$ `Backtest` $\rightarrow$ `Evaluation` $\rightarrow$ `Report`).
   - `ResearchKnowledgeGraph`: Dynamic Node/Edge relationship graph (`USES`, `GENERATES`, `DERIVED_FROM`, `EVALUATED_BY`, `SUPPORTS`, `FAILED_AT`).

4. **Multi-Faceted & Semantic Vector Search (`knowledge/search/`, `knowledge/embeddings/`)**:
   - `EmbeddingProvider`: Self-contained TF-IDF vectorizer and cosine similarity engine requiring zero external cloud dependencies.
   - `KnowledgeSearchEngine`: Filters by model, modality, dataset, status, date range, metric threshold, and free-text semantic relevance.

5. **Side-by-Side Experiment Comparison Engine (`knowledge/comparison/`)**:
   - `ExperimentComparisonEngine`: Calculates metric deltas, parameter diffs, and checks for fair comparison (raising warnings if datasets or evaluation setups differ).

6. **Metadata Extractor & Factual Evidence Summarizer (`knowledge/indexing/`, `knowledge/summaries/`)**:
   - `MetadataExtractor`: Automatically indexes completed and failed experiment runs.
   - `ResearchSummaryEngine`: Computes factual group statistics (mean, median, std, min, max) strictly avoiding subjective investment advice.

7. **CLI Tools (`knowledge/cli/`)**:
   - `search.py`, `inspect.py`, `compare.py`, `lineage.py`, `failures.py`, `summary.py`, `graph.py`, `index.py`.

8. **REST API & Dashboard Page**:
   - Endpoints at `/knowledge/search`, `/knowledge/experiments/{id}`, `/knowledge/experiments/{id}/lineage`, `/knowledge/models`, `/knowledge/features`, `/knowledge/datasets`, `/knowledge/failures`, `/knowledge/claims`, `/knowledge/journal`, `/knowledge/compare`, `/knowledge/graph`, `/knowledge/summary`, `/knowledge/health`.
   - **30th Streamlit Workspace Page**: `dashboard/pages/30_Quant_Research_Knowledge_OS.py`.

## Quick Start CLI Usage

```bash
# Index completed experiments into Knowledge Base
python knowledge/cli/index.py

# Search knowledge base semantically
python knowledge/cli/search.py --query "news sentiment volatile period"

# Inspect specific experiment record
python knowledge/cli/inspect.py --experiment EXP-001

# Compare two experiments side-by-side
python knowledge/cli/compare.py EXP-001 EXP-002

# Trace experiment lineage DAG
python knowledge/cli/lineage.py --experiment EXP-001

# List failed experiment logs
python knowledge/cli/failures.py

# Generate knowledge base summary & statistics
python knowledge/cli/summary.py
```
