"""
Central Risk Service for Advanced Risk OS.
"""

from typing import Dict, Any, List, Optional
import os
import json
import numpy as np
from datetime import datetime

from risk.core.risk_engine import AdvancedRiskEngine
from risk.core.risk_snapshot import RiskSnapshot
from risk.core.risk_result import RiskResult


class RiskService:
    """Unified service for Quantitative Risk & Stress Engine OS operations."""

    def __init__(self, storage_dir: str = "artifacts/risk"):
        self.storage_dir = storage_dir
        os.makedirs(self.storage_dir, exist_ok=True)
        os.makedirs(os.path.join(self.storage_dir, "snapshots"), exist_ok=True)
        os.makedirs(os.path.join(self.storage_dir, "reports"), exist_ok=True)
        self.engine = AdvancedRiskEngine()

    def run_risk_analysis(
        self,
        portfolio_id: str,
        weights: Optional[Dict[str, float]] = None,
        returns_history: Optional[List[List[float]]] = None,
        cov_matrix: Optional[List[List[float]]] = None,
        portfolio_value: float = 100000.0,
        asset_metadata: Optional[Dict[str, Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        w = weights or {"AAPL": 0.35, "MSFT": 0.35, "GOOGL": 0.30}
        n = len(w)

        if returns_history is not None:
            rets = np.array(returns_history, dtype=float)
        else:
            np.random.seed(42)
            rets = np.random.normal(loc=0.0005, scale=0.015, size=(250, n))

        if cov_matrix is not None:
            cov = np.array(cov_matrix, dtype=float)
        else:
            cov = np.cov(rets, rowvar=False)

        np.random.seed(42)
        bench = np.random.normal(loc=0.0004, scale=0.012, size=len(rets))

        res = self.engine.evaluate_portfolio_risk(
            portfolio_id=portfolio_id,
            weights=w,
            returns_history=rets,
            cov_matrix=cov,
            benchmark_returns=bench,
            portfolio_value=portfolio_value,
            asset_metadata=asset_metadata,
        )

        res_dict = res.to_dict()

        # Create RiskSnapshot
        snapshot = RiskSnapshot(
            risk_id=res.risk_id,
            portfolio_id=portfolio_id,
            timestamp=res.timestamp,
            portfolio_value=portfolio_value,
            volatility=res.market_risk["historical_volatility"],
            beta=res.market_risk["beta"],
            var_95=res.tail_risk["var_95_historical"],
            cvar_95=res.tail_risk["cvar_95"],
            maximum_drawdown=res.drawdown_analysis["max_drawdown"],
            gross_exposure=res.portfolio_risk["exposures"]["gross_exposure"],
            net_exposure=res.portfolio_risk["exposures"]["net_exposure"],
            leverage=res.portfolio_risk["exposures"]["leverage"],
            concentration=res.portfolio_risk["concentration"],
            risk_contributions=res.portfolio_risk["contributions"]["percentage_contributions"],
            limit_breaches=res.risk_limits_status.get("breaches", []),
        )

        self._save_snapshot(snapshot)
        self._save_result(res_dict)

        return res_dict

    @staticmethod
    def _make_json_serializable(obj: Any) -> Any:
        if isinstance(obj, dict):
            return {k: RiskService._make_json_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [RiskService._make_json_serializable(v) for v in obj]
        elif isinstance(obj, tuple):
            return [RiskService._make_json_serializable(v) for v in obj]
        elif isinstance(obj, (np.bool_, bool)):
            return bool(obj)
        elif isinstance(obj, (np.integer, int)):
            return int(obj)
        elif isinstance(obj, (np.floating, float)):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        return obj

    def _save_snapshot(self, snapshot: RiskSnapshot) -> None:
        filepath = os.path.join(self.storage_dir, "snapshots", f"{snapshot.risk_id}.json")
        data = self._make_json_serializable(snapshot.to_dict())
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)

    def _save_result(self, res_dict: Dict[str, Any]) -> None:
        filepath = os.path.join(self.storage_dir, f"{res_dict['risk_id']}.json")
        data = self._make_json_serializable(res_dict)
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)
