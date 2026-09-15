import numpy as np
import pandas as pd
import pytest
from src.data.sequence_builder import SequenceBuilder, QuantScaler, SequenceDataset

def test_quant_scaler():
    scaler = QuantScaler()
    X_train = np.array([[1.0, 2.0], [3.0, 4.0], [5.0, 6.0]])
    X_test = np.array([[2.0, 3.0]])

    scaled_tr = scaler.fit_transform(X_train)
    scaled_te = scaler.transform(X_test)
    assert scaled_tr.shape == (3, 2)
    assert scaled_te.shape == (1, 2)

def test_sequence_builder():
    df = pd.DataFrame({
        "date": pd.date_range("2023-01-01", periods=50),
        "ticker": ["AAPL"] * 50,
        "f1": np.random.randn(50),
        "f2": np.random.randn(50),
        "target_return": np.random.randn(50)
    })
    builder = SequenceBuilder(sequence_length=10)
    X_seq, y_seq = builder.build_sequences(df, ["f1", "f2"], "target_return")
    assert X_seq.shape == (40, 10, 2)
    assert y_seq.shape == (40,)

def test_prepare_dataloaders():
    df = pd.DataFrame({
        "date": pd.date_range("2023-01-01", periods=100),
        "ticker": ["AAPL"] * 100,
        "f1": np.random.randn(100),
        "target_return": np.random.randn(100)
    })
    train_df = df.iloc[:60]
    val_df = df.iloc[60:80]
    test_df = df.iloc[80:]

    builder = SequenceBuilder(sequence_length=10)
    tr_l, val_l, te_l, scaler = builder.prepare_datasets(
        train_df, val_df, test_df, ["f1"], "target_return", batch_size=8
    )

    for X, y in tr_l:
        assert X.shape[1] == 10
        assert X.shape[2] == 1
        break
