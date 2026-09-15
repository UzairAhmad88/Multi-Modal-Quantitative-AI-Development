from __future__ import annotations
from typing import Tuple, List, Dict, Any
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
import torch
from torch.utils.data import Dataset, DataLoader
from src.utils.logger import get_logger

logger = get_logger("sequence_builder")


class QuantScaler:
    """Scales feature arrays using StandardScaler, ensuring fitting ONLY on training data."""

    def __init__(self):
        self.scaler = StandardScaler()
        self.is_fitted = False

    def fit_transform(self, X: np.ndarray) -> np.ndarray:
        scaled = self.scaler.fit_transform(X)
        self.is_fitted = True
        return scaled

    def transform(self, X: np.ndarray) -> np.ndarray:
        if not self.is_fitted:
            raise ValueError("Scaler must be fit on training data before calling transform.")
        return self.scaler.transform(X)


class SequenceDataset(Dataset):
    """PyTorch Dataset yielding 30-day temporal sequence tensors (sequence_length, num_features) and target."""

    def __init__(self, sequences: np.ndarray, targets: np.ndarray):
        self.sequences = torch.tensor(sequences, dtype=torch.float32)
        self.targets = torch.tensor(targets, dtype=torch.float32)

    def __len__(self) -> int:
        return len(self.sequences)

    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, torch.Tensor]:
        return self.sequences[idx], self.targets[idx]


class SequenceBuilder:
    """Constructs 30-day sliding window sequence datasets for PyTorch DL models without data leakage."""

    def __init__(self, sequence_length: int = 30):
        self.sequence_length = sequence_length
        self.scaler = QuantScaler()

    def build_sequences(
        self,
        df: pd.DataFrame,
        feature_cols: List[str],
        target_col: str = "target_return"
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Convert a single asset time series into (num_samples, sequence_length, num_features) and targets."""
        df_sorted = df.sort_values("date").reset_index(drop=True)
        feats = df_sorted[feature_cols].values
        targets = df_sorted[target_col].values

        X_seq, y_seq = [], []
        for i in range(len(df_sorted) - self.sequence_length):
            X_seq.append(feats[i : i + self.sequence_length])
            y_seq.append(targets[i + self.sequence_length - 1])

        if not X_seq:
            return np.zeros((0, self.sequence_length, len(feature_cols))), np.zeros((0,))

        return np.array(X_seq), np.array(y_seq)

    def prepare_datasets(
        self,
        train_df: pd.DataFrame,
        val_df: pd.DataFrame,
        test_df: pd.DataFrame,
        feature_cols: List[str],
        target_col: str = "target_return",
        batch_size: int = 32
    ) -> Tuple[DataLoader, DataLoader, DataLoader, QuantScaler]:
        """Fit scaler ONLY on train, apply to val and test, and construct PyTorch DataLoaders."""
        train_df_clean = train_df.dropna(subset=[target_col]).copy()
        val_df_clean = val_df.dropna(subset=[target_col]).copy()
        test_df_clean = test_df.dropna(subset=[target_col]).copy()

        # 1. Fit scaler ONLY on training features
        train_feats_scaled = train_df_clean.copy()
        train_feats_scaled[feature_cols] = self.scaler.fit_transform(train_df_clean[feature_cols].values)

        val_feats_scaled = val_df_clean.copy()
        val_feats_scaled[feature_cols] = self.scaler.transform(val_df_clean[feature_cols].values)

        test_feats_scaled = test_df_clean.copy()
        test_feats_scaled[feature_cols] = self.scaler.transform(test_df_clean[feature_cols].values)

        # 2. Build sliding window sequence arrays per ticker
        X_tr_list, y_tr_list = [], []
        for ticker, grp in train_feats_scaled.groupby("ticker"):
            X_s, y_s = self.build_sequences(grp, feature_cols, target_col)
            if len(X_s) > 0:
                X_tr_list.append(X_s)
                y_tr_list.append(y_s)

        X_val_list, y_val_list = [], []
        for ticker, grp in val_feats_scaled.groupby("ticker"):
            X_s, y_s = self.build_sequences(grp, feature_cols, target_col)
            if len(X_s) > 0:
                X_val_list.append(X_s)
                y_val_list.append(y_s)

        X_te_list, y_te_list = [], []
        for ticker, grp in test_feats_scaled.groupby("ticker"):
            X_s, y_s = self.build_sequences(grp, feature_cols, target_col)
            if len(X_s) > 0:
                X_te_list.append(X_s)
                y_te_list.append(y_s)

        X_tr = np.concatenate(X_tr_list, axis=0) if X_tr_list else np.zeros((0, self.sequence_length, len(feature_cols)))
        y_tr = np.concatenate(y_tr_list, axis=0) if y_tr_list else np.zeros((0,))

        X_val = np.concatenate(X_val_list, axis=0) if X_val_list else np.zeros((0, self.sequence_length, len(feature_cols)))
        y_val = np.concatenate(y_val_list, axis=0) if y_val_list else np.zeros((0,))

        X_te = np.concatenate(X_te_list, axis=0) if X_te_list else np.zeros((0, self.sequence_length, len(feature_cols)))
        y_te = np.concatenate(y_te_list, axis=0) if y_te_list else np.zeros((0,))

        # DataLoaders (shuffle=False for time-series evaluation)
        train_loader = DataLoader(SequenceDataset(X_tr, y_tr), batch_size=batch_size, shuffle=True)
        val_loader = DataLoader(SequenceDataset(X_val, y_val), batch_size=batch_size, shuffle=False)
        test_loader = DataLoader(SequenceDataset(X_te, y_te), batch_size=batch_size, shuffle=False)

        return train_loader, val_loader, test_loader, self.scaler
