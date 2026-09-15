import torch
import numpy as np
from src.models.dl.lstm import LSTMModel
from src.models.dl.gru import GRUModel
from src.models.dl.transformer import TransformerModel
from src.models.dl.multi_modal import MultiModalQuantNet
from src.models.dl.trainer import train_dl_model, save_checkpoint, load_checkpoint
from src.models.ml.ensemble import EnsembleEngine
from torch.utils.data import DataLoader, TensorDataset

def test_dl_forward_passes():
    x = torch.randn(8, 30, 10)  # batch=8, seq=30, features=10

    lstm = LSTMModel(input_size=10, hidden_size=16)
    out_l = lstm(x)
    assert out_l.shape == (8,)

    gru = GRUModel(input_size=10, hidden_size=16)
    out_g = gru(x)
    assert out_g.shape == (8,)

    trans = TransformerModel(input_size=10, d_model=16, nhead=2)
    out_t = trans(x)
    assert out_t.shape == (8,)

def test_multi_modal_network():
    m_seq = torch.randn(8, 30, 10)
    n_vec = torch.randn(8, 10)
    f_vec = torch.randn(8, 12)

    net = MultiModalQuantNet(market_input_size=10, news_input_dim=10, fund_input_dim=12, fusion_method="learned")
    out = net(m_seq, n_vec, f_vec)
    assert out.shape == (8,)

def test_train_dl_model(tmp_path):
    x = torch.randn(32, 10, 5)
    y = torch.randn(32)
    loader = DataLoader(TensorDataset(x, y), batch_size=16)

    model = LSTMModel(input_size=5, hidden_size=8)
    ckpt = tmp_path / "lstm.pt"
    res = train_dl_model(model, loader, loader, epochs=2, checkpoint_path=ckpt)

    assert res["epochs_trained"] == 2
    assert ckpt.exists()

def test_ensemble_engine():
    preds = {
        "xgb": np.array([0.01, 0.02, -0.01]),
        "lstm": np.array([0.02, 0.01, -0.02])
    }
    y_val = np.array([0.015, 0.015, -0.015])

    ens = EnsembleEngine(method="validation_weighted")
    w = ens.fit_weights(preds, y_val)
    out = ens.predict(preds)

    assert len(out) == 3
    assert abs(sum(w.values()) - 1.0) < 1e-5
