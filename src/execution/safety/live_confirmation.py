"""
Live Trading Interactive Confirmation Token Manager.
Provides secure single-use tokens and confirmation verification workflow.
"""

from datetime import datetime, timezone, timedelta
import secrets
from typing import Dict, Any, Optional, Tuple


class LiveConfirmationManager:
    """Manages single-use secure confirmation tokens for live mode enablement."""

    def __init__(self, token_ttl_seconds: int = 300):
        self.token_ttl_seconds = token_ttl_seconds
        self.active_tokens: Dict[str, Dict[str, Any]] = {}

    def generate_confirmation_token(self, user_id: str = "QUANT_OPERATOR", account_id: str = "LIVE-ACCT") -> Dict[str, Any]:
        """Generate a short-lived token requiring explicit operator verification."""
        token = f"LIVE-CONFIRM-{secrets.token_hex(16).upper()}"
        expires_at = datetime.now(timezone.utc) + timedelta(seconds=self.token_ttl_seconds)

        payload = {
            "token": token,
            "user_id": user_id,
            "account_id": account_id,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "expires_at": expires_at.isoformat(),
            "is_used": False
        }

        self.active_tokens[token] = payload
        return payload

    def validate_and_consume_token(self, token: str) -> Tuple[bool, str]:
        """Validate and consume token for one-time operation."""
        if not token or token not in self.active_tokens:
            return False, "INVALID_TOKEN: Confirmation token is unrecognized or missing."

        rec = self.active_tokens[token]
        if rec["is_used"]:
            return False, "EXPIRED_TOKEN: Confirmation token has already been used."

        exp_dt = datetime.fromisoformat(rec["expires_at"])
        if datetime.now(timezone.utc) > exp_dt:
            return False, "EXPIRED_TOKEN: Confirmation token has expired."

        rec["is_used"] = True
        return True, "TOKEN_VALIDATED: Live trading action confirmed."
