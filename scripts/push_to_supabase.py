#!/usr/bin/env python3
"""
QUANT AI: Push Backend to Supabase Script
Organization: szlgsmaolpgwjrvdgvut
"""

import sys
import os
import logging
import pandas as pd

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.db.supabase_client import SupabaseQuantClient
from src.db.sync_to_supabase import SupabaseDataSyncer

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

def main():
    logger.info("==================================================")
    logger.info("   QUANT AI: SUPABASE BACKEND DEPLOYMENT & SYNC   ")
    logger.info("   Organization: szlgsmaolpgwjrvdgvut             ")
    logger.info("==================================================")

    client = SupabaseQuantClient()
    logger.info("Supabase Project URL: %s", client.url)
    logger.info("Configured Status: %s", client.is_configured())

    sample_signals = pd.DataFrame([
        {
            "ticker": "AAPL",
            "signal": "BUY",
            "forecast_return_5d": 0.0284,
            "confidence_score": 0.87,
            "composite_alpha_score": 0.76,
            "market_factor_score": 0.74,
            "news_factor_score": 0.68,
            "fundamental_factor_score": 0.82,
            "technical_factor_score": 0.71,
            "macro_factor_score": 0.41,
            "model_agreement_count": 5,
            "total_models": 5,
            "regime": "BULLISH",
        },
        {
            "ticker": "NVDA",
            "signal": "STRONG BUY",
            "forecast_return_5d": 0.0412,
            "confidence_score": 0.91,
            "composite_alpha_score": 0.89,
            "market_factor_score": 0.92,
            "news_factor_score": 0.73,
            "fundamental_factor_score": 0.91,
            "technical_factor_score": 0.88,
            "macro_factor_score": 0.52,
            "model_agreement_count": 5,
            "total_models": 5,
            "regime": "BULLISH",
        }
    ])

    sample_risk = {
        "portfolio_value": 1024820.00,
        "volatility_ann": 0.1480,
        "sharpe_ratio": 1.7200,
        "var_95": -0.0182,
        "max_drawdown": -0.0841,
        "beta": 0.9400,
        "gross_exposure": 0.8300,
        "cash_weight": 0.1700,
        "risk_status": "NORMAL"
    }

    syncer = SupabaseDataSyncer(client)
    res = syncer.sync_all(sample_signals, {}, sample_risk)

    logger.info("Sync Execution Result: %s", res)
    logger.info("Supabase backend files successfully built & ready for deployment!")
    logger.info("==================================================")

if __name__ == "__main__":
    main()
