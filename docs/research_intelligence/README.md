# Quant Research Intelligence, Pattern Discovery & Hypothesis Engine (Phase 15)

## Overview

The Research Intelligence layer transforms the Multi-Modal Quant AI platform into an **evidence-based quantitative research operating system**. It automates pattern discovery across market technicals, FinBERT news sentiment, and SEC quarterly fundamentals, executes lag analysis and event studies, formats testable hypotheses with explicit null and alternative bounds, builds an end-to-end research lineage graph, classifies evidence, retains persistent research memory, and supports natural-language research queries without fabricating unvalidated claims.

```text
                    QUANT DATA
                        │
                        ▼
                PATTERN DISCOVERY
                        │
          ┌─────────────┼─────────────┐
          ▼             ▼             ▼
       MARKET          NEWS       FUNDAMENTALS
          │             │             │
          └─────────────┼─────────────┘
                        ▼
                CROSS-MODAL ANALYSIS
                        │
                        ▼
                    ANOMALIES
                        │
                        ▼
                HYPOTHESIS ENGINE
                        │
                        ▼
              EXPERIMENT GENERATOR
                        │
                        ▼
              RESEARCH ORCHESTRATOR
                        │
                        ▼
                   VALIDATION
                        │
          ┌─────────────┼─────────────┐
          ▼             ▼             ▼
      STATISTICS     ROBUSTNESS     STRESS
          │             │             │
          └─────────────┼─────────────┘
                        ▼
                  EVIDENCE ENGINE
                        │
                        ▼
                 RESEARCH FINDING
                        │
                        ▼
               FOLLOW-UP QUESTIONS
                        │
                        ▼
                RESEARCH KNOWLEDGE
```

---

## Key Submodules (`research_intelligence/`)

1. **`discovery/`**:
   - `pattern_discovery.py`: Discovers market technical, news sentiment, fundamental, and cross-modal interactions.
   - `correlation_analyzer.py`: Calculates Pearson and Spearman correlations across variables.
   - `lag_analyzer.py`: Evaluates cross-correlations across temporal lags ($t, t+1, t+5, t+10, t+20$).
   - `anomaly_detector.py`: Identifies statistical outliers ($z > 3.0$) and formulates research questions.

2. **`patterns/`**:
   - `event_study.py`: Evaluates pre/post event window returns across `[-1,+1]`, `[-3,+3]`, `[-5,+5]`, `[-10,+10]`.
   - `regime_discovery.py`: Segments relationship stability across market regime clusters (high/low volatility).

3. **`hypotheses/`**:
   - `hypothesis_engine.py`: Creates structured hypotheses (`HYP-xxxx`) with explicit null ($H_0$) and alternative ($H_1$) hypotheses.

4. **`experiment_generation/`**:
   - `generator.py`: Converts hypotheses into executable experiment YAML configs in `configs/experiments/`.

5. **`evidence/`**:
   - `evidence_engine.py`: Classifies findings into standard research statuses (`SUPPORTED BY OBSERVED DATA`, `MIXED EVIDENCE`, `INCONCLUSIVE`, `CONTRADICTED BY TEST`, `NOT TESTED`).
   - `research_memory.py`: Persistent storage (`artifacts/research_memory.json`) retaining hypotheses, findings, and failed hypotheses.

6. **`attribution/`**:
   - `error_analyzer.py`: Analyzes false positives, false negatives, directional failures, and multimodal disagreement.

7. **`similarity/`**:
   - `similarity.py`: Detects duplicate or overlapping research experiments.

8. **`research_graph/`**:
   - `graph.py`: Network graph representing Hypotheses, Experiments, Datasets, Features, Models, Validations, and Findings.

9. **`reports/`**:
   - `report_generator.py`: Compiles Markdown research reports under `reports/research_intelligence/`.

10. **`utils/`**:
    - `assistant.py`: Natural Language Research Assistant answering queries over registered research artifacts without fabrication.

---

## CLI Reference

### 1. Execute Pattern Discovery
```bash
python research_intelligence/discover.py
```

### 2. Generate Hypotheses
```bash
python research_intelligence/generate_hypotheses.py
```

### 3. Display Hypothesis
```bash
python research_intelligence/show_hypothesis.py --id HYP-20260916-0001
```

### 4. Create Experiment Config from Hypothesis
```bash
python research_intelligence/create_experiment.py --hypothesis HYP-20260916-0001
```

### 5. Search Similar Experiments
```bash
python research_intelligence/find_similar.py --experiment EXP-001
```

### 6. Compile Research Intelligence Report
```bash
python research_intelligence/report.py --experiment EXP-001
```

---

## REST API Endpoints

- `POST /research-intelligence/discover`
- `GET /research-intelligence/patterns`
- `GET /research-intelligence/hypotheses`
- `POST /research-intelligence/hypotheses`
- `GET /research-intelligence/hypotheses/{id}`
- `POST /research-intelligence/hypotheses/{id}/experiment`
- `GET /research-intelligence/findings`
- `GET /research-intelligence/findings/{id}`
- `GET /research-intelligence/questions`
- `GET /research-intelligence/similar/{id}`
- `GET /research-intelligence/graph`
- `POST /research-intelligence/query`
