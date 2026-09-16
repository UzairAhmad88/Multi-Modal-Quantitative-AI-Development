# Portfolio Optimization Specifications Report

**System**: Multi-Modal Quantitative Intelligence Platform  
**Package**: `src/portfolio/`  
**Version**: v2.7.0 Portfolio Release  

---

## 1. Supported Portfolio Optimizers

1. **Equal Weight**: Baseline $w_i = \frac{1}{N}$.
2. **Signal Weight**: Proportional to positive expected return score.
3. **Inverse Volatility**: Inverse to historical asset standard deviation $w_i \propto \frac{1}{\sigma_i}$.
4. **Minimum Variance**: Quadratic program minimizing portfolio variance $w^T \Sigma w$.
5. **Mean-Variance Markowitz**: Maximizes $\mu^T w - \frac{\lambda}{2} w^T \Sigma w$.
6. **Risk Parity**: Solves equal component risk contribution $w_i (\Sigma w)_i = \text{const}$.
7. **Hierarchical Risk Parity (HRP)**: Single-linkage clustering on correlation distance matrices.
