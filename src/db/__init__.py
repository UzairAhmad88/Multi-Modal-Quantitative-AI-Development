"""
QUANT AI: Supabase Database Integration Package
Organization: szlgsmaolpgwjrvdgvut
"""

from .supabase_client import SupabaseQuantClient
from .sync_to_supabase import SupabaseDataSyncer

__all__ = ["SupabaseQuantClient", "SupabaseDataSyncer"]
