#!/usr/bin/env python3
"""
QUANT AI: Real-Time Signal Generation Script
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.alpha.signal_generator import AlphaEngine, generate_signal
from src.utils.logger import get_logger

logger = get_logger("generate_signals")

def main():
    logger.info("Generating Alpha Signals for Active Universe...")
    engine = AlphaEngine()
    predictions = {
        "XGBoost": 0.0284,
        "LSTM": 0.0245,
        "GRU": 0.0261,
        "Transformer": 0.0310,
        "MultiModalQuantNet": 0.0345
    }
    result = engine.process_predictions(predictions)
    logger.info(f"Generated Composite Signal Result: {result}")

if __name__ == "__main__":
    main()
