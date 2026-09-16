"""
Performance Metrics Engine: Computes Sharpe, Sortino, Calmar, Win Rate, Profit Factor, Turnover.
"""

import numpy as np
from typing import Union, List, Dict, Any
from research_evaluation.metrics.return_calculator import ReturnCalculator
from research_evaluation.metrics.drawdown_analyzer import DrawdownAnalyzer


class PerformanceMetricsEngine:
    """Calculates comprehensive performance ratios and trading statistics."""

    def __init__(self, risk_free_rate: float = 0.02, annualization_factor: int = 252):
        self.risk_free_rate = risk_free_rate
        self.annualization_factor = annualization_factor
        self.return_calc = ReturnCalculator(annualization_factor=annualization_factor)
        self.dd_analyzer = DrawdownAnalyzer()

    def evaluate_performance(self, equity_curve: Union[List[float], np.ndarray]) -> Dict[str, Any]:
        """Evaluates full performance ratio matrix given an equity curve."""
        eq = np.array(equity_curve, dtype=float)
        ret_info = self.return_calc.compute_returns(eq)
        dd_info = self.dd_analyzer.analyze_drawdowns(eq)

        returns = np.array(ret_info["simple_returns"])
        if len(returns) == 0:
            return {"sharpe_ratio": 0.0, "sortino_ratio": 0.0, "calmar_ratio": 0.0}

        ann_return = ret_info["cagr"]
        ann_vol = float(np.std(returns) * np.sqrt(self.annualization_factor)) if len(returns) > 1 else 0.0

        # Sharpe Ratio
        rf_daily = self.risk_free_rate / self.annualization_factor
        excess_returns = returns - rf_daily
        sharpe = float((np.mean(excess_returns) / np.std(returns)) * np.sqrt(self.annualization_factor)) if np.std(returns) > 1e-6 else 0.0

        # Sortino Ratio
        downside_returns = returns[returns < 0]
        downside_std = float(np.std(downside_returns) * np.sqrt(self.annualization_factor)) if len(downside_returns) > 0 and np.std(downside_returns) > 1e-6 else 1e-6
        sortino = float((ann_return - self.risk_free_rate) / downside_std)

        # Calmar Ratio
        max_dd = dd_info["max_drawdown"]
        calmar = float(ann_return / max_dd) if max_dd > 1e-6 else float(ann_return / 0.01)

        # Win rate & Profit factor
        wins = returns[returns > 0]
        losses = returns[returns < 0]
        win_rate = float(len(wins) / len(returns)) if len(returns) > 0 else 0.0
        gross_profit = float(np.sum(wins)) if len(wins) > 0 else 0.0
        gross_loss = float(abs(np.sum(losses))) if len(losses) > 0 else 0.0
        profit_factor = float(gross_profit / gross_loss) if gross_loss > 1e-6 else float(gross_profit / 0.01)

        return {
            "total_return": round(ret_info["total_return"], 4),
            "cagr": round(ann_return, 4),
            "annualized_volatility": round(ann_vol, 4),
            "sharpe_ratio": round(sharpe, 4),
            "sortino_ratio": round(sortino, 4),
            "calmar_ratio": round(calmar, 4),
            "max_drawdown": round(max_dd, 4),
            "avg_drawdown": round(dd_info["avg_drawdown"], 4),
            "win_rate": round(win_rate, 4),
            "profit_factor": round(profit_factor, 4),
            "average_win": round(float(np.mean(wins)), 6) if len(wins) > 0 else 0.0,
            "average_loss": round(float(np.mean(losses)), 6) if len(losses) > 0 else 0.0,
            "annualization_factor": self.annualization_factor,
            "risk_free_rate": self.risk_free_rate
        }
