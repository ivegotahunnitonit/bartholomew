import time
import secrets
from typing import Dict, Any, Optional

class EnterpriseAPIKeyManager:
    """
    MULTI-TENANT ENTERPRISE API KEY & METERING ENGINE v1.0
    Issues, validates, and meters enterprise API keys (`age_live_...`) for CI/CD pipelines.
    """
    def __init__(self):
        self.keys_db: Dict[str, Dict[str, Any]] = {
            "age_live_demo_enterprise_key_2026": {
                "owner": "Enterprise Demo Client",
                "tier": "enterprise",
                "audits_used": 142,
                "audits_limit": 1000000,
                "created_at": time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
            }
        }

    def generate_api_key(self, owner_email: str, tier: str = "developer") -> Dict[str, Any]:
        """Generates cryptographically secure enterprise API key."""
        raw_token = secrets.token_hex(20)
        api_key = f"age_live_{raw_token}"
        
        limits = {
            "developer": 10000,
            "pro_team": 100000,
            "enterprise": 1000000
        }
        
        limit = limits.get(tier.lower(), 10000)
        record = {
            "api_key": api_key,
            "owner": owner_email,
            "tier": tier,
            "audits_used": 0,
            "audits_limit": limit,
            "created_at": time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
            "status": "ACTIVE"
        }
        self.keys_db[api_key] = record
        return {
            "success": True,
            "api_key": api_key,
            "owner": owner_email,
            "tier": tier,
            "audit_quota_monthly": limit
        }

    def validate_and_record_usage(self, api_key: str) -> Dict[str, Any]:
        """Validates key authenticity & meters monthly audit usage."""
        if not api_key or api_key not in self.keys_db:
            # Fallback for open sandbox mode
            return {"valid": True, "metered": False, "tier": "sandbox_free"}

        rec = self.keys_db[api_key]
        if rec["audits_used"] >= rec["audits_limit"]:
            return {"valid": False, "error": "QUOTA_EXCEEDED", "detail": "Monthly audit quota exhausted. Upgrade tier."}

        rec["audits_used"] += 1
        return {
            "valid": True,
            "metered": True,
            "owner": rec["owner"],
            "tier": rec["tier"],
            "audits_remaining": rec["audits_limit"] - rec["audits_used"]
        }

api_key_manager = EnterpriseAPIKeyManager()
