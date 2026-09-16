# QUANT AI Research Methodology

## Multi-Modal Alpha Hypothesis
Financial markets are driven by heterogeneous information sources. Technical price momentum captures market microstructure dynamics, financial news sentiment captures immediate catalyst shifts, and quarterly fundamentals capture intrinsic asset value.

`MultiModalQuantNet` dynamically weights these three modalities using a learned attention mechanism:

$$\text{Fused Representation} = w_1 \cdot E_{\text{market}} + w_2 \cdot E_{\text{news}} + w_3 \cdot E_{\text{fundamentals}}$$

where $\sum w_i = 1$ is computed via softmax.

---

## Modality Ablation Framework
To rigorously prove that multi-modal fusion adds value, four controlled experiments are evaluated:
1. **Experiment A (Market Only)**: Baseline technical features.
2. **Experiment B (Market + News)**: Technicals + FinBERT sentiment scores.
3. **Experiment C (Market + Fundamentals)**: Technicals + Quarterly ratios.
4. **Experiment D (Full Multi-Modal Fusion)**: Technicals + News + Fundamentals.
