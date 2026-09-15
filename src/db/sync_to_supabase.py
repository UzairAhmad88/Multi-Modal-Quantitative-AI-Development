import logging
from typing import Dict, Any, Optional
import pandas as pd
from .supabase_client import SupabaseQuantClient

logger = logging.getLogger(__name__)

class SupabaseDataSyncer:
    """
    Automated Sync Manager for Multi-Modal Quant AI to Supabase
    """

    def __init__(self, client: Optional[SupabaseQuantClient] = None):
        self.client = client or SupabaseQuantClient()

    def sync_all(self, signals_df: pd.DataFrame, portfolio_dict: Dict[str, Any], risk_dict: Dict[str, Any]) -> Dict[str, Any]:
        """
        Synchronize signals, portfolio, and risk metrics to Supabase.
        """
        logger.info("Starting complete sync to Supabase backend...")
        
        signals_res = self.client.insert_signals(signals_df)
        risk_res = self.client.insert_risk_metrics(risk_dict)
        
        return {
            "status": "completed",
            "signals_sync": signals_res.get("status"),
            "risk_sync": risk_res.get("status"),
            "ticker_count": len(signals_df) if not signals_df.empty else 0,
        }
