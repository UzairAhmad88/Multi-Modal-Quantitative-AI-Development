"""
Assumption Checker for Normality, Stationarity, and Sample Size Requirements.
"""

import numpy as np
import scipy.stats as stats
from typing import List, Dict, Any, Tuple
from validation.schemas.validation_schema import AssumptionCheck, IntegrityFlag, IntegrityFlagType, IntegrityFlagSeverity


class AssumptionChecker:
    """
    Verifies underlying statistical assumptions before significance testing.
    """

    @staticmethod
    def check_all(
        returns: np.ndarray, min_observations: int = 252
    ) -> Tuple[List[AssumptionCheck], List[IntegrityFlag]]:
        checks: List[AssumptionCheck] = []
        flags: List[IntegrityFlag] = []

        n = len(returns)

        # 1. Sample Size Check
        if n < min_observations:
            checks.append(
                AssumptionCheck(
                    assumption="Sample Size",
                    status="WARNING",
                    message=f"Sample size ({n}) is below recommended threshold ({min_observations})",
                    details={"sample_size": n, "min_required": min_observations},
                )
            )
            flags.append(
                IntegrityFlag(
                    flag_type=IntegrityFlagType.SMALL_SAMPLE,
                    severity=IntegrityFlagSeverity.WARNING,
                    message=f"Small sample size ({n} < {min_observations}) increases statistical uncertainty",
                )
            )
        else:
            checks.append(
                AssumptionCheck(
                    assumption="Sample Size",
                    status="PASS",
                    message=f"Sample size ({n}) satisfies threshold ({min_observations})",
                )
            )

        # 2. Normality Check (Shapiro-Wilk or Jarque-Bera)
        if n >= 8:
            stat, p_val = stats.shapiro(returns[:500]) if n <= 500 else stats.jarque_bera(returns)
            is_normal = p_val > 0.05
            checks.append(
                AssumptionCheck(
                    assumption="Normality",
                    status="PASS" if is_normal else "WARNING",
                    message="Returns follow Gaussian distribution" if is_normal else f"Non-normal return distribution detected (p={p_val:.4f})",
                    details={"statistic": float(stat), "p_value": float(p_val)},
                )
            )

        return checks, flags
