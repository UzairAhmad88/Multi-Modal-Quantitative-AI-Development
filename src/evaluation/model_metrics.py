from __future__ import annotations
from typing import Dict, Any
import numpy as np
import pandas as pd
from sklearn.metrics import (
    mean_absolute_error, mean_squared_error, r2_score,
    accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
)


def compute_regression_metrics(y_true: np.ndarray | pd.Series, y_pred: np.ndarray | pd.Series) -> Dict[str, float]:
    """Compute regression evaluation metrics: MAE, RMSE, R2, Information Coefficient (Pearson Correlation)."""
    y_t = np.asarray(y_true, dtype=float)
    y_p = np.asarray(y_pred, dtype=float)

    mae = float(mean_absolute_error(y_t, y_p))
    rmse = float(np.sqrt(mean_squared_error(y_t, y_p)))
    r2 = float(r2_score(y_t, y_p))

    # Information Coefficient (Pearson correlation between prediction and actual)
    if np.std(y_t) > 1e-8 and np.std(y_p) > 1e-8:
        ic = float(np.corrcoef(y_t, y_p)[0, 1])
    else:
        ic = 0.0

    return {
        "mae": round(mae, 6),
        "rmse": round(rmse, 6),
        "r2": round(r2, 6),
        "ic": round(ic, 6)
    }


def compute_classification_metrics(y_true: np.ndarray | pd.Series, y_pred: np.ndarray | pd.Series, y_prob: np.ndarray | None = None) -> Dict[str, float]:
    """Compute classification metrics: Accuracy, Precision, Recall, F1, ROC-AUC."""
    y_t = np.asarray(y_true)
    y_p = np.asarray(y_pred)

    acc = float(accuracy_score(y_t, y_p))
    prec = float(precision_score(y_t, y_p, average="weighted", zero_division=0))
    rec = float(recall_score(y_t, y_p, average="weighted", zero_division=0))
    f1 = float(f1_score(y_t, y_p, average="weighted", zero_division=0))

    metrics = {
        "accuracy": round(acc, 4),
        "precision": round(prec, 4),
        "recall": round(rec, 4),
        "f1": round(f1, 4)
    }

    if y_prob is not None:
        try:
            if len(np.unique(y_t)) == 2:
                metrics["roc_auc"] = round(float(roc_auc_score(y_t, y_prob[:, 1])), 4)
            else:
                metrics["roc_auc"] = round(float(roc_auc_score(y_t, y_prob, multi_class="ovr")), 4)
        except Exception:
            metrics["roc_auc"] = 0.5

    return metrics


# Alias for backward compatibility
def regression_metrics(y_true, y_pred):
    return compute_regression_metrics(y_true, y_pred)
