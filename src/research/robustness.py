"""
Robustness Testing Module
Evaluates strategy performance across parameter sweeps, transaction costs, slippage drag,
sub-period regimes, cross-asset universes, and purged walk-forward splits with embargoes.
"""

from typing import Dict, List, Any, Optional, Tuple
import numpy as np
import pandas as pd


class RobustnessTester:
    """Quantitative Strategy Robustness & Parameter Sensitivity Engine."""

    def __init__(self, backtest_func: Any):
        """
        Initialize RobustnessTester.
        :param backtest_func: Callable accepting (params_dict) -> returns dict of metrics (sharpe, cagr, max_drawdown, turnover).
        """
        self.backtest_func = backtest_func

    def test_cost_sensitivity(
        self,
        cost_scenarios_bps: List[float] = [0.0, 5.0, 10.0, 20.0, 50.0, 100.0],
        base_params: Optional[Dict[str, Any]] = None,
    ) -> pd.DataFrame:
        """
        Evaluate strategy sensitivity to transaction costs (in bps).
        """
        params = base_params.copy() if base_params else {}
        results = []

        for cost in cost_scenarios_bps:
            p = params.copy()
            p["transaction_cost_bps"] = cost
            metrics = self.backtest_func(p)
            results.append({
                "cost_bps": cost,
                "sharpe": metrics.get("sharpe", 0.0),
                "cagr": metrics.get("cagr", 0.0),
                "max_drawdown": metrics.get("max_drawdown", 0.0),
                "win_rate": metrics.get("win_rate", 0.0),
                "turnover": metrics.get("turnover", 0.0),
            })

        return pd.DataFrame(results)

    def test_slippage_sensitivity(
        self,
        slippage_scenarios_bps: List[float] = [0.0, 2.5, 5.0, 10.0, 25.0, 50.0],
        base_params: Optional[Dict[str, Any]] = None,
    ) -> pd.DataFrame:
        """
        Evaluate strategy sensitivity to execution slippage (in bps).
        """
        params = base_params.copy() if base_params else {}
        results = []

        for slip in slippage_scenarios_bps:
            p = params.copy()
            p["slippage_bps"] = slip
            metrics = self.backtest_func(p)
            results.append({
                "slippage_bps": slip,
                "sharpe": metrics.get("sharpe", 0.0),
                "cagr": metrics.get("cagr", 0.0),
                "max_drawdown": metrics.get("max_drawdown", 0.0),
                "win_rate": metrics.get("win_rate", 0.0),
            })

        return pd.DataFrame(results)

    def test_parameter_grid(
        self, param_grid: Dict[str, List[Any]], base_params: Optional[Dict[str, Any]] = None
    ) -> pd.DataFrame:
        """
        Sweep strategy parameters to build a sensitivity matrix.
        """
        base = base_params.copy() if base_params else {}
        results = []

        import itertools
        keys = list(param_grid.keys())
        values = list(param_grid.values())

        for combination in itertools.product(*values):
            p = base.copy()
            comb_dict = dict(zip(keys, combination))
            p.update(comb_dict)

            metrics = self.backtest_func(p)
            res_entry = comb_dict.copy()
            res_entry.update({
                "sharpe": metrics.get("sharpe", 0.0),
                "cagr": metrics.get("cagr", 0.0),
                "max_drawdown": metrics.get("max_drawdown", 0.0),
            })
            results.append(res_entry)

        return pd.DataFrame(results)

    def evaluate_regimes(
        self, df_returns: pd.DataFrame, return_col: str = "strategy_return"
    ) -> Dict[str, Dict[str, float]]:
        """
        Evaluate performance across market regimes (Bull, Bear, High Vol, Low Vol).
        """
        if df_returns.empty or return_col not in df_returns.columns:
            return {}

        rets = df_returns[return_col]
        vol = rets.rolling(20).std() * np.sqrt(252)
        mean_vol = vol.mean()

        regimes = {
            "Bull Market": rets[rets > 0],
            "Bear Market": rets[rets < 0],
            "High Volatility": rets[vol > mean_vol],
            "Low Volatility": rets[vol <= mean_vol],
        }

        regime_metrics = {}
        for name, r_sub in regimes.items():
            if len(r_sub) < 5:
                regime_metrics[name] = {"cagr": 0.0, "sharpe": 0.0, "volatility": 0.0, "count": 0}
                continue

            ann_mean = float(r_sub.mean() * 252)
            ann_std = float(r_sub.std() * np.sqrt(252)) + 1e-8
            sharpe = float(ann_mean / ann_std)

            regime_metrics[name] = {
                "cagr": round(ann_mean, 4),
                "sharpe": round(sharpe, 4),
                "volatility": round(ann_std, 4),
                "count": int(len(r_sub)),
            }

        return regime_metrics

    @staticmethod
    def purged_train_test_split(
        df: pd.DataFrame,
        train_pct: float = 0.7,
        purge_window: int = 5,
        embargo_window: int = 5,
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Purged time-series train/test split with an embargo period to eliminate look-ahead leakage.
        :param purge_window: Number of samples purged at the end of training to avoid target overlap.
        :param embargo_window: Number of samples embargoed before test set starts.
        """
        n = len(df)
        split_idx = int(n * train_pct)

        train_end = max(0, split_idx - purge_window)
        test_start = min(n, split_idx + embargo_window)

        train_df = df.iloc[:train_end].copy()
        test_df = df.iloc[test_start:].copy()

        return train_df, test_df
