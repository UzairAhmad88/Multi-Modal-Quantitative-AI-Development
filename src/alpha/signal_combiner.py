import numpy as np

def weighted_average(scores, weights=None):
    values = np.asarray(scores, dtype=float)
    weights = np.ones(len(values)) if weights is None else np.asarray(weights, dtype=float)
    return float(np.average(values, weights=weights))
