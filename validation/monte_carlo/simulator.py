"""
Monte Carlo Path Simulator for Quantitative Strategy Trades.
Simulates trade sequence permutations to estimate drawdown distributions and path variability.
"""

from typing import Dict, List, Any
import numpy as np


class MonteCarloSimulator:
    """Simulates trade sequence resamplings for risk and drawdown distribution estimation."""

    @staticmethod
    def simulate_trade_paths(
        trade_returns: List[float],
        num_simulations: int = 500,
        initial_capital: float = 100000.0,
        seed: int = 42,
    ) -> Dict[str, Any]:
        np.random.seed(seed)
        trades = np.array(trade_returns)
        if len(trades) < 5:
            return {"status": "INCONCLUSIVE", "reason": "Insufficient trade history"}

        num_trades = len(trades)
        final_equity_list = []
        max_drawdown_list = []

        for _ in range(num_simulations):
            path_trades = np.random.choice(trades, size=num_trades, replace=True)
            cum_returns = np.cumprod(1.0 + path_trades)
            equity_curve = initial_capital * cum_returns

            peak = np.maximum.accumulate(equity_curve)
            drawdowns = (peak - equity_curve) / peak
            max_dd = float(np.max(drawdowns))

            final_equity_list.append(float(equity_curve[-1]))
            max_drawdown_list.append(max_dd)

        return {
            "num_simulations": num_simulations,
            "seed": seed,
            "disclaimer": "SIMULATED MONTE CARLO OUTCOMES ONLY. NOT ACTUAL HISTORICAL RESULTS.",
            "final_equity": {
                "mean": round(float(np.mean(final_equity_list)), 2),
                "5th_percentile": round(float(np.percentile(final_equity_list, 5)), 2),
                "95th_percentile": round(float(np.percentile(final_equity_list, 95)), 2),
            },
            "max_drawdown_distribution": {
                "mean_drawdown": round(float(np.mean(max_drawdown_list)), 4),
                "worst_5pct_drawdown": round(float(np.percentile(max_drawdown_list, 95)), 4),
                "max_observed_drawdown": round(float(np.max(max_drawdown_list)), 4),
            },
        }
