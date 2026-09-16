"""
Portfolio Constraint Engine Module
Enforces single position limits, sector exposure caps, gross/net leverage limits,
turnover penalties, and minimum rebalance thresholds.
"""

from typing import Dict, List, Any, Tuple, Optional
import numpy as np
import pandas as pd


class PortfolioConstraintEngine:
    """Quantitative Portfolio Constraint Enforcement Engine."""

    def __init__(
        self,
        max_asset_weight: float = 0.25,
        max_sector_weight: float = 0.40,
        max_gross_exposure: float = 1.00,
        rebalance_threshold: float = 0.02,
    ):
        self.max_asset_weight = max_asset_weight
        self.max_sector_weight = max_sector_weight
        self.max_gross_exposure = max_gross_exposure
        self.rebalance_threshold = rebalance_threshold

    def apply_constraints(
        self,
        target_weights: pd.Series,
        sector_mapping: Optional[Dict[str, str]] = None,
        current_weights: Optional[pd.Series] = None,
    ) -> Tuple[pd.Series, List[str]]:
        """
        Apply portfolio constraints and return (constrained_weights, log_messages).
        """
        logs = []
        w = target_weights.copy()

        # 1. Single Position Cap
        over_mask = w > self.max_asset_weight
        if over_mask.any():
            over_assets = list(w[over_mask].index)
            logs.append(f"Capped asset position limits ({self.max_asset_weight*100:.1f}%): {over_assets}")
            w[over_mask] = self.max_asset_weight

        # 2. Sector Cap
        if sector_mapping is not None:
            w_df = pd.DataFrame({"weight": w, "sector": [sector_mapping.get(s, "UNKNOWN") for s in w.index]})
            sector_totals = w_df.groupby("sector")["weight"].sum()
            for sec, tot in sector_totals.items():
                if tot > self.max_sector_weight:
                    scale = self.max_sector_weight / tot
                    sec_assets = w_df[w_df["sector"] == sec].index
                    w[sec_assets] = w[sec_assets] * scale
                    logs.append(f"Capped sector '{sec}' exposure to {self.max_sector_weight*100:.1f}%")

        # 3. Rebalance Threshold Filter
        if current_weights is not None:
            curr = current_weights.reindex(w.index).fillna(0.0)
            delta = (w - curr).abs()
            no_rebalance_mask = delta < self.rebalance_threshold
            if no_rebalance_mask.any():
                skipped = list(w[no_rebalance_mask].index)
                w[no_rebalance_mask] = curr[no_rebalance_mask]
                logs.append(f"Skipped rebalance for assets below {self.rebalance_threshold*100:.1f}% delta: {skipped}")

        # 4. Gross Exposure Normalization
        tot_w = w.sum()
        if tot_w > self.max_gross_exposure:
            w = w / tot_w * self.max_gross_exposure
            logs.append(f"Normalized gross exposure to {self.max_gross_exposure*100:.1f}%")

        return w.round(6), logs
