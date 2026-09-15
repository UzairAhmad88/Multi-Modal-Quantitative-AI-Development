from __future__ import annotations
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.data.market_loader import load_market_data
from src.features.feature_fusion import FeatureBuilder
from src.data.sequence_builder import SequenceBuilder
from src.models.dl.lstm import LSTMModel
from src.models.dl.trainer import train_dl_model
from src.models.ml.split import chronological_split
from src.utils.paths import MODELS_DIR
from src.utils.logger import get_logger

logger = get_logger("script_train_dl")


def main():
    logger.info("Training Deep Learning Models (PyTorch LSTM)...")
    market_df = load_market_data("AAPL", start="2018-01-01")

    builder = FeatureBuilder()
    raw_df, manifest = builder.build_dataset(market_df)
    df = raw_df.dropna(subset=["target_return"]).reset_index(drop=True)

    feature_cols = manifest["feature_names"]
    train_df, val_df, test_df = chronological_split(df)

    seq_builder = SequenceBuilder(sequence_length=30)
    tr_l, val_l, te_l, scaler = seq_builder.prepare_datasets(train_df, val_df, test_df, feature_cols)

    model = LSTMModel(input_size=len(feature_cols), hidden_size=32)
    ckpt = MODELS_DIR / "checkpoints" / "lstm_v1.pt"

    res = train_dl_model(model, tr_l, val_l, epochs=5, checkpoint_path=ckpt)
    logger.info(f"LSTM Training Complete: {res}")


if __name__ == "__main__":
    main()
