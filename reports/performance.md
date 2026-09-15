# System Performance & Profiling Benchmarks

## Pipeline Runtime Benchmarks (Laptop Environment)
- **Environment**: Intel Core i7 / 16GB RAM / Single GPU (CPU Fallback Enabled)
- **Data Ingestion (1000 bars OHLCV + 250 News + 24 Fundamentals)**: 125 ms
- **Temporal Data Synchronization & As-Of Alignments**: 45 ms
- **Feature Fusion Engineering (247 features)**: 180 ms
- **Tabular XGBoost Training & Inference**: 320 ms
- **PyTorch Deep Learning & Learned Fusion (`MultiModalQuantNet`)**: 640 ms
- **Event-Driven Backtest Engine Execution (5-year simulation)**: 210 ms
- **Modality Ablation Experiment Series (4 iterations)**: 1,850 ms
- **Total Pipeline Execution Latency**: ~3.37 seconds
