"""
Replication Engine: Executes exact replication runs of previous experiments.
"""

from typing import Dict, Any
from research_lab.reproducibility.reproducibility_checker import ReproducibilityChecker


class ReplicationExperiment:
    """Executes replication experiments to verify reproducibility."""

    def __init__(self):
        self.checker = ReproducibilityChecker()

    def replicate_experiment(
        self,
        original_exp: Dict[str, Any],
        replication_runner
    ) -> Dict[str, Any]:
        """Runs replication run and returns comparison results."""
        rep_exp = replication_runner(original_exp)
        status, details = self.checker.verify_reproducibility(original_exp, rep_exp)

        return {
            "original_experiment_id": original_exp.get("experiment_id"),
            "replication_experiment_id": rep_exp.get("experiment_id"),
            "replication_status": status,
            "verification_details": details
        }
