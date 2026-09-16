# Multi-Modal Quant AI — Known Research & System Limitations (Phase 30)

## 1. Quantitative & Financial Research Limitations

1. **Survivorship Bias**:
   - Historical market datasets focus primarily on active, surviving public constituents. Delisted assets and historical bankrupted equity series require external point-in-time universe feeds for full survivorship-bias mitigation.

2. **Execution Microstructure Assumptions**:
   - Market execution is modeled via deterministicTWAP, VWAP, POV algorithms with parametric quadratic market impact models and fixed basis-point slippage/commission rates. Real market order book queue dynamics and latency variations may differ in live high-frequency environments.

3. **News Sentiment NLP Boundaries**:
   - Sentiment scores rely on pre-trained FinBERT embeddings and lexicon models. Satirical news, complex macroeconomic nuances, and novel regulatory phrasing may introduce localized classification noise.

4. **Fundamental Frequency Alignment**:
   - Quarterly SEC filings are aligned using explicit `public_release_date` availability. Where release dates are omitted, conservative 45-day post-fiscal-quarter-end lagging is enforced.

---

## 2. System & Infrastructure Boundaries

1. **No Live Real-Money Broker Trading**:
   - The platform is strictly an institutional quantitative research, simulation, and walk-forward evaluation framework. Direct broker API order routing is **DISABLED BY DESIGN**.

2. **Memory Constraints for Ultra-Large High-Frequency Data**:
   - The laptop-first design optimizes for daily/intraday frequency up to several million rows. Tick-level order book datasets exceeding tens of gigabytes require distributed PySpark or Polars storage backends.

3. **Stochastic Components**:
   - Neural network training (`MultiModalQuantNet`, PyTorch LSTM/Transformer) and Monte Carlo simulations rely on pseudo-random seeds. Exact numerical parity across different hardware platforms (e.g. CUDA vs CPU) may exhibit sub-decimal floating-point variances.
