"""
Return Calculator: Simple returns, log returns, cumulative returns, CAGR, and frequency handling.
"""

import numpy as np
import pandas as pd
from typing import Union, List, Dict, Any, Optional


class ReturnCalculator:
    """Calculates simple, log, cumulative returns and CAGR."""

    def __init__(self, annualization_factor: int = 252):
        self.annualization_factor = annualization_factor

    def compute_returns(self, equity_curve: Union[List[float], pd.Series, np.ndarray]) -> Dict[str, Any]:
        """Calculates return series and total / CAGR metrics."""
        eq = np.array(equity_curve, dtype=float)
        if len(eq) < 2 or eq[0] <= 0:
            return {"simple_returns": [], "total_return": 0.0, "cagr": 0.0}

        simple_returns = np.diff(eq) / eq[:-1]
        log_returns = np.log(eq[1:] / eq[:-1])
        total_return = (eq[-1] / eq[0]) - 1.0

        n_periods = len(eq) - 1
        years = n_periods / self.annualization_factor
        cagr = ((eq[-1] / eq[0]) ** (1.0 / years) - 1.0) if years > 0 else total_return

        return {
            "simple_returns": simple_returns.tolist(),
            "log_returns": log_returns.tolist(),
            "total_return": float(total_return),
            "cagr": float(cagr),
            "n_periods": n_periods,
            "years": round(float(years), 2)
        }
