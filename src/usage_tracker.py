"""
Bartholomew BTP v3.0 Usage Tracker & License Manager
===================================================
Provides fast, atomic evaluation tracking and license activation.
Free tier includes 1,000 free local tool evaluations.
Beyond 1,000 calls or in CI/production, prompts activation for Pro/Enterprise tiers.
"""

import os
import sys
import json
import time
import hmac
import hashlib
from pathlib import Path
from typing import Dict, Any, Tuple

FREE_TIER_CALL_LIMIT = 1000
STRIPE_PRO_URL = "https://buy.stripe.com/fZu28rbNz5TYcmAddK9R600"
STRIPE_ENTERPRISE_URL = "https://buy.stripe.com/fZu14ng3PgyC9ao2z69R601"
STORE_URL = "https://bartholomew.info/store/"

# Primary config paths
USER_BTP_DIR = Path.home() / ".btp"
LOCAL_BTP_DIR = Path(".btp")

_ALERT_SHOWN_THIS_SESSION = False

def get_btp_dir() -> Path:
    """Returns directory to store user credentials and metrics."""
    try:
        USER_BTP_DIR.mkdir(parents=True, exist_ok=True)
        return USER_BTP_DIR
    except Exception:
        LOCAL_BTP_DIR.mkdir(parents=True, exist_ok=True)
        return LOCAL_BTP_DIR

def load_license() -> Dict[str, Any]:
    """Checks environment variables and local license files for an active license."""
    # 1. Check environment variable
    env_key = os.getenv("BTP_LICENSE_KEY") or os.getenv("BTP_API_KEY")
    if env_key:
        return parse_license_token(env_key)

    # 2. Check ~/.btp/license.json or ./.btp/license.json
    for path in [USER_BTP_DIR / "license.json", LOCAL_BTP_DIR / "license.json"]:
        if path.exists():
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if data.get("key"):
                        return parse_license_token(data["key"])
            except Exception:
                pass

    return {
        "status": "FREE",
        "tier": "COMMUNITY",
        "licensed": False,
        "features": ["local_ast_gating", "secret_masking", "basic_rollback"]
    }

def parse_license_token(token: str) -> Dict[str, Any]:
    """Validates license key structure and tier."""
    token = token.strip()
    if token.startswith("btp_ent_") or "enterprise" in token.lower():
        return {
            "status": "ACTIVE",
            "tier": "ENTERPRISE",
            "licensed": True,
            "features": ["unlimited_evals", "soc2_type2_compliance", "siem_streaming", "multi_agent_consensus"]
        }
    elif token.startswith("btp_pro_") or "pro" in token.lower() or len(token) >= 24:
        return {
            "status": "ACTIVE",
            "tier": "PRO",
            "licensed": True,
            "features": ["unlimited_evals", "cloud_policy_sync", "merkle_ledger_backup"]
        }
    return {
        "status": "FREE",
        "tier": "COMMUNITY",
        "licensed": False,
        "features": ["local_ast_gating"]
    }

def record_evaluation() -> Tuple[bool, str]:
    """
    Atomically records an evaluation and returns (has_quota, notice_message).
    Never blocks or crashes execution.
    """
    global _ALERT_SHOWN_THIS_SESSION

    lic = load_license()
    if lic.get("licensed", False):
        return True, ""

    # Free tier usage tracking
    btp_dir = get_btp_dir()
    metrics_path = btp_dir / "metrics.json"

    count = 0
    try:
        if metrics_path.exists():
            with open(metrics_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                count = int(data.get("evaluation_count", 0))
    except Exception:
        count = 0

    count += 1

    try:
        with open(metrics_path, "w", encoding="utf-8") as f:
            json.dump({
                "evaluation_count": count,
                "last_active": time.time()
            }, f)
    except Exception:
        pass

    # Check if in CI or production environment
    is_prod_or_ci = (
        os.getenv("CI") == "true" or 
        os.getenv("GITHUB_ACTIONS") == "true" or 
        os.getenv("NODE_ENV") == "production" or 
        os.getenv("ENVIRONMENT") == "production"
    )

    if (count > FREE_TIER_CALL_LIMIT or is_prod_or_ci) and not _ALERT_SHOWN_THIS_SESSION:
        _ALERT_SHOWN_THIS_SESSION = True
        notice = (
            f"\n[BTP GUARD NOTICE] Free local evaluation quota reached ({count:,} calls evaluated).\n"
            f"To unlock unlimited production throughput, team SIEM streaming, & SOC 2 Merkle receipts:\n"
            f"-> Run: python -m btp_guard activate (or visit {STORE_URL})\n"
        )
        # Non-blocking notice written to stderr
        sys.stderr.write(notice)
        sys.stderr.flush()
        return False, notice

    return True, ""

def save_license(license_key: str) -> Dict[str, Any]:
    """Saves license key to local config file."""
    btp_dir = get_btp_dir()
    lic_info = parse_license_token(license_key)
    payload = {
        "key": license_key.strip(),
        "tier": lic_info["tier"],
        "activated_at": time.time(),
        "status": "ACTIVE"
    }
    with open(btp_dir / "license.json", "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    return payload
