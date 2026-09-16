"""
Risk Limit Monitor & Alert Engine for Advanced Risk Engine OS.
"""

from typing import Dict, Any, List, Tuple, Optional


class RiskLimitEngine:
    """Evaluates portfolio risk metrics against configured limits and issues RISK_LIMIT_BREACH alerts."""

    def __init__(self, limits_config: Optional[Dict[str, Any]] = None):
        self.config = limits_config or {}
        self.max_volatility = self.config.get("max_volatility", 0.25)
        self.max_var_95 = self.config.get("max_var_95", 0.05)
        self.max_cvar_95 = self.config.get("max_cvar_95", 0.08)
        self.max_drawdown = self.config.get("max_drawdown", 0.20)
        self.max_leverage = self.config.get("max_leverage", 1.50)
        self.max_hhi = self.config.get("max_hhi", 0.35)

    def evaluate_limits(self, risk_snapshot: Dict[str, Any]) -> Dict[str, Any]:
        breaches: List[str] = []
        limit_statuses: Dict[str, Dict[str, Any]] = {}

        # 1. Volatility check
        vol = risk_snapshot.get("volatility", 0.0)
        vol_passed = vol <= self.max_volatility + 1e-6
        limit_statuses["volatility"] = {"value": vol, "limit": self.max_volatility, "passed": vol_passed}
        if not vol_passed:
            breaches.append(f"RISK_LIMIT_BREACH: Volatility {vol*100:.2f}% exceeds limit {self.max_volatility*100:.2f}%")

        # 2. VaR check
        var95 = risk_snapshot.get("var_95", 0.0)
        var_passed = var95 <= self.max_var_95 + 1e-6
        limit_statuses["var_95"] = {"value": var95, "limit": self.max_var_95, "passed": var_passed}
        if not var_passed:
            breaches.append(f"RISK_LIMIT_BREACH: VaR (95%) {var95*100:.2f}% exceeds limit {self.max_var_95*100:.2f}%")

        # 3. CVaR check
        cvar95 = risk_snapshot.get("cvar_95", 0.0)
        cvar_passed = cvar95 <= self.max_cvar_95 + 1e-6
        limit_statuses["cvar_95"] = {"value": cvar95, "limit": self.max_cvar_95, "passed": cvar_passed}
        if not cvar_passed:
            breaches.append(f"RISK_LIMIT_BREACH: CVaR (95%) {cvar95*100:.2f}% exceeds limit {self.max_cvar_95*100:.2f}%")

        # 4. Maximum Drawdown check
        max_dd = risk_snapshot.get("maximum_drawdown", 0.0)
        dd_passed = max_dd <= self.max_drawdown + 1e-6
        limit_statuses["maximum_drawdown"] = {"value": max_dd, "limit": self.max_drawdown, "passed": dd_passed}
        if not dd_passed:
            breaches.append(f"RISK_LIMIT_BREACH: Drawdown {max_dd*100:.2f}% exceeds limit {self.max_drawdown*100:.2f}%")

        # 5. Leverage check
        lev = risk_snapshot.get("leverage", 1.0)
        lev_passed = lev <= self.max_leverage + 1e-6
        limit_statuses["leverage"] = {"value": lev, "limit": self.max_leverage, "passed": lev_passed}
        if not lev_passed:
            breaches.append(f"RISK_LIMIT_BREACH: Leverage {lev:.2f}x exceeds limit {self.max_leverage:.2f}x")

        has_breach = len(breaches) > 0

        return {
            "status": "BREACH_DETECTED" if has_breach else "NORMAL",
            "has_breach": has_breach,
            "breaches": breaches,
            "limits_eval": limit_statuses,
        }
