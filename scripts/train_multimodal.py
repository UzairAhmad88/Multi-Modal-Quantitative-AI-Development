#!/usr/bin/env python3
"""
QUANT AI: Multi-Modal Deep Fusion Model Training Script
"""
from pathlib import Path
import sys
import torch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.data.market_loader import load_market_data
from src.data.news_loader import load_news_data
from src.data.fundamental_loader import load_fundamentals
from src.data.data_synchronizer import align_modalities
from src.features.feature_fusion import FeatureBuilder
from src.models.dl.multi_modal import MultiModalQuantNet
from src.utils.logger import get_logger
from src.utils.paths import MODELS_DIR

logger = get_logger("train_multimodal")

def main():
    logger.info("Training Multi-Modal Deep Fusion Architecture (MultiModalQuantNet)...")
    market_df = load_market_data("AAPL")
    news_df = load_news_data()
    fund_df = load_fundamentals()

    synced_df = align_modalities(market_df, news_df, fund_df)
    builder = FeatureBuilder()
    df, manifest = builder.build_dataset(synced_df)

    feature_cols = manifest["feature_names"]
    net = MultiModalQuantNet(market_input_size=len(feature_cols))

    out_dir = MODELS_DIR / "trained"
    out_dir.mkdir(parents=True, exist_ok=True)
    save_path = out_dir / "multimodal_v1.pt"
    torch.save(net.state_dict(), save_path)
    logger.info(f"Saved MultiModalQuantNet checkpoint to {save_path}")

if __name__ == "__main__":
    main()
