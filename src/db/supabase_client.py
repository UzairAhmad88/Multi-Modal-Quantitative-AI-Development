import os
import json
import logging
from typing import Dict, Any, List, Optional
import pandas as pd
import requests

logger = logging.getLogger(__name__)

class SupabaseQuantClient:
    """
    Python Client Interface for Supabase Backend
    Organization: szlgsmaolpgwjrvdgvut
    """

    def __init__(self, url: Optional[str] = None, key: Optional[str] = None):
        self.url = url or os.getenv("SUPABASE_URL", "https://szlgsmaolpgwjrvdgvut.supabase.co")
        self.key = key or os.getenv("SUPABASE_KEY", os.getenv("SUPABASE_SERVICE_ROLE_KEY", "sb_anon_mock_key"))
        self.headers = {
            "apikey": self.key,
            "Authorization": f"Bearer {self.key}",
            "Content-Type": "application/json",
            "Prefer": "return=representation",
        }
        self.rest_url = f"{self.url.rstrip('/')}/rest/v1"

    def is_configured(self) -> bool:
        """Check if Supabase credentials are path valid."""
        return bool(self.url and "supabase.co" in self.url and self.key and self.key != "sb_anon_mock_key")

    def insert_signals(self, signals_df: pd.DataFrame) -> Dict[str, Any]:
        """Insert or upsert AI signals into Supabase `ai_signals` table."""
        records = []
        for idx, row in signals_df.iterrows():
            rec = {
                "ticker": str(row.get("ticker", "AAPL")),
                "signal": str(row.get("signal", "BUY")),
                "forecast_return_5d": float(row.get("forecast_return_5d", 0.0)),
                "confidence_score": float(row.get("confidence_score", 0.85)),
                "composite_alpha_score": float(row.get("composite_alpha_score", 0.75)),
                "market_factor_score": float(row.get("market_factor_score", 0.70)),
                "news_factor_score": float(row.get("news_factor_score", 0.65)),
                "fundamental_factor_score": float(row.get("fundamental_factor_score", 0.80)),
                "technical_factor_score": float(row.get("technical_factor_score", 0.70)),
                "macro_factor_score": float(row.get("macro_factor_score", 0.40)),
                "model_agreement_count": int(row.get("model_agreement_count", 5)),
                "total_models": int(row.get("total_models", 5)),
                "regime": str(row.get("regime", "BULLISH")),
            }
            records.append(rec)

        if not self.is_configured():
            logger.info("Supabase client running in local mock mode. Signals serialized (%d rows).", len(records))
            return {"status": "mock", "count": len(records), "records": records}

        try:
            resp = requests.post(f"{self.rest_url}/ai_signals", headers=self.headers, json=records, timeout=10)
            resp.raise_for_status()
            return {"status": "success", "count": len(records), "response": resp.json()}
        except Exception as e:
            logger.error("Failed to insert signals to Supabase: %s", str(e))
            return {"status": "error", "message": str(e), "records": records}

    def fetch_latest_signals(self) -> pd.DataFrame:
        """Fetch latest AI signals from Supabase view `v_latest_signals`."""
        if not self.is_configured():
            logger.info("Supabase client in mock mode: returning standard default signals.")
            return pd.DataFrame([
                {"ticker": "AAPL", "signal": "BUY", "forecast_return_5d": 0.0284, "confidence_score": 0.87, "composite_alpha_score": 0.76},
                {"ticker": "NVDA", "signal": "STRONG BUY", "forecast_return_5d": 0.0412, "confidence_score": 0.91, "composite_alpha_score": 0.89},
                {"ticker": "MSFT", "signal": "BUY", "forecast_return_5d": 0.0215, "confidence_score": 0.84, "composite_alpha_score": 0.71},
            ])

        try:
            resp = requests.get(f"{self.rest_url}/v_latest_signals", headers=self.headers, timeout=10)
            resp.raise_for_status()
            return pd.DataFrame(resp.json())
        except Exception as e:
            logger.error("Failed to fetch signals from Supabase: %s", str(e))
            return pd.DataFrame()

    def insert_risk_metrics(self, risk_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Insert portfolio risk metrics into Supabase `risk_metrics` table."""
        if not self.is_configured():
            logger.info("Supabase client in mock mode: Risk metrics serialized.")
            return {"status": "mock", "metrics": risk_dict}

        try:
            resp = requests.post(f"{self.rest_url}/risk_metrics", headers=self.headers, json=[risk_dict], timeout=10)
            resp.raise_for_status()
            return {"status": "success", "response": resp.json()}
        except Exception as e:
            logger.error("Failed to insert risk metrics to Supabase: %s", str(e))
            return {"status": "error", "message": str(e)}
