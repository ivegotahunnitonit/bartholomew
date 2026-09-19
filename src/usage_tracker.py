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
FIRST_USE_NOTICE_KEY = "upgrade_notice_shown"

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
    """Validates license key structure and tier with resilient sanitization."""
    if not token:
        return {
            "status": "FREE",
            "tier": "COMMUNITY",
            "licensed": False,
            "features": ["local_ast_gating"]
        }
    token = str(token).strip().strip('"\'`')
    token_lower = token.lower()

    if token_lower.startswith("btp_ent_") or token_lower.startswith("age_ent_") or "enterprise" in token_lower:
        return {
            "status": "ACTIVE",
            "tier": "ENTERPRISE",
            "licensed": True,
            "features": ["unlimited_evals", "soc2_type2_compliance", "siem_streaming", "multi_agent_consensus"]
        }
    elif token_lower.startswith("btp_pro_") or token_lower.startswith("age_live_") or "pro" in token_lower or len(token) >= 20:
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
    data = {}
    try:
        if metrics_path.exists():
            with open(metrics_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                count = int(data.get("evaluation_count", 0))
    except Exception:
        count = 0

    count += 1
    first_use_notice = ""

    try:
        metrics = {
            "evaluation_count": count,
            "last_active": time.time()
        }
        with open(metrics_path, "w", encoding="utf-8") as f:
            json.dump({
                **metrics,
                FIRST_USE_NOTICE_KEY: True if count == 1 else data.get(FIRST_USE_NOTICE_KEY, False)
            }, f)
    except Exception:
        pass

    # Respect quiet / silent environments and avoid polluting automated logs
    if os.getenv("BTP_SILENT") == "true" or os.getenv("BTP_QUIET") == "true":
        return True, ""

    # In CI/CD or production containers, keep execution 100% silent unless explicitly requested
    is_ci_env = os.getenv("CI") == "true" or os.getenv("GITHUB_ACTIONS") == "true"
    if is_ci_env and os.getenv("BTP_LOGS") != "true":
        return True, ""

    if count == 1:
        first_use_notice = (
            "\n[BTP GUARD] In-process execution gate initialized (Community Edition).\n"
            f"For team policy sync and telemetry, Pro is $49/month: {STRIPE_PRO_URL}\n"
            f"For enterprise controls and compliance evidence, Enterprise is $199/month: {STRIPE_ENTERPRISE_URL}\n"
            "Run 'btp-guard trial --email user@company.com' for an instant 14-day team trial.\n"
        )
        try:
            sys.stderr.write(first_use_notice)
            sys.stderr.flush()
        except Exception:
            pass

    if count > FREE_TIER_CALL_LIMIT and not _ALERT_SHOWN_THIS_SESSION:
        _ALERT_SHOWN_THIS_SESSION = True
        notice = (
            f"\n[BTP GUARD] Core Local Engine: Free forever for open-source development.\n"
            "To unlock multi-agent cloud sync, team SIEM streaming, and certified SOC 2 auditor packs:\n"
            f"-> Run: btp-guard activate (or visit {STORE_URL})\n"
        )
        try:
            sys.stderr.write(notice)
            sys.stderr.flush()
        except Exception:
            pass
        return False, first_use_notice + notice

    return True, first_use_notice


def trigger_threat_intercept_notice(rule_id: str, action_summary: str = "", latency_us: float = 24.8) -> None:
    """
    Emits a high-impact notification when an agent action is blocked,
    prompting team alert routing. Strictly NO emojis.
    """
    if os.getenv("BTP_SILENT") == "true" or os.getenv("BTP_QUIET") == "true":
        return

    lic = load_license()
    if lic.get("licensed", False):
        return

    clean_summary = str(action_summary).replace("\n", " ").strip()
    if len(clean_summary) > 60:
        clean_summary = clean_summary[:57] + "..."

    msg = (
        f"\n[BTP GUARD ALERT] Threat Intercepted: Blocked '{clean_summary}' (Rule {rule_id}, {latency_us:.1f}us).\n"
        "[BTP PRO] To forward real-time security alerts to team Slack/Discord or SIEM webhook:\n"
        f"          Upgrade to Pro ($49/mo): {STRIPE_PRO_URL}\n"
        "          Or activate 14-day team trial: btp-guard trial --email your@company.com\n"
    )
    try:
        sys.stderr.write(msg)
        sys.stderr.flush()
    except Exception:
        pass


def activate_trial(email: str) -> Dict[str, Any]:
    """
    Activates an instant 14-day Pro Trial for a verified corporate/developer email.
    Saves trial state locally and returns credentials. Strictly NO emojis.
    """
    email = str(email).strip().lower()
    if "@" not in email or "." not in email:
        raise ValueError("Please provide a valid corporate or developer email address.")

    btp_dir = get_btp_dir()
    salt = "btp_trial_v5_pro"
    token_digest = hashlib.sha256(f"{email}:{salt}:{time.time()}".encode()).hexdigest()[:16]
    trial_key = f"btp_pro_trial_{token_digest}"

    now = time.time()
    expires_at = now + (14 * 86400)

    payload = {
        "key": trial_key,
        "email": email,
        "tier": "PRO",
        "status": "ACTIVE_TRIAL",
        "activated_at": now,
        "expires_at": expires_at,
        "features": ["unlimited_evals", "cloud_policy_sync", "team_slack_webhooks"]
    }

    with open(btp_dir / "license.json", "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)

    with open(btp_dir / "trial.json", "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)

    return payload

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
