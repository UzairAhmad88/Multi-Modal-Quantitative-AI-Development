"""
Unified Ensemble Engine for Quantitative AI Models.
Coordinates voting, weighted averaging, stacking, and blending.
"""

from typing import Dict, Any, List, Optional
import numpy as np

from models.ensemble.voting import VotingEnsemble
from models.ensemble.averaging import AveragingEnsemble
from models.ensemble.stacking import StackingEnsemble
from models.ensemble.blending import BlendingEnsemble


class EnsembleEngine:
    """Master Ensemble Engine coordinating multi-model aggregation methods."""

    def __init__(self):
        self.voting = VotingEnsemble()
        self.averaging = AveragingEnsemble()
        self.stacking = StackingEnsemble()
        self.blending = BlendingEnsemble()

    def combine_predictions(
        self,
        predictions_list: List[np.ndarray],
        ensemble_type: str = "weighted_average",
        weights: Optional[List[float]] = None,
        y_true: Optional[np.ndarray] = None
    ) -> np.ndarray:
        """Combines list of prediction arrays according to selected ensemble method."""
        if not predictions_list:
            return np.array([])

        if ensemble_type == "voting":
            return self.voting.predict(predictions_list)
        elif ensemble_type == "stacking" and y_true is not None:
            self.stacking.fit(predictions_list, y_true)
            return self.stacking.predict(predictions_list)
        elif ensemble_type == "blending":
            return self.blending.predict(predictions_list, weights=weights)
        else:
            return self.averaging.predict(predictions_list, weights=weights)
