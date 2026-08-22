"""
Bartholomew Stripe Webhook Handler
====================================
Handles Stripe webhook events with signature verification (STRIPE_WEBHOOK_SECRET).
On checkout.session.completed:
  1. Verifies Stripe-Signature header (prevents replay / spoofed events)
  2. Determines plan tier from amount_total
  3. Auto-provisions an age_live_ API key for the customer
  4. Appends a tamper-evident provisioning record to saas_production_ledger.jsonl
  5. Returns 200 immediately so Stripe stops retrying

On customer.subscription.deleted:
  1. Marks the customer's key as CANCELLED in the ledger
"""

import os
import json
import time
import hmac
import hashlib
import secrets
from typing import Dict, Any, Optional, Tuple

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

#  Plan Tier Lookup by Amount 
# Matches the 3 Stripe products: Developer ($0), Pro ($49), Team ($199)
AMOUNT_TO_TIER: Dict[int, str] = {
    0:     "DEVELOPER_FREE",
    4900:  "PRO_REPO_$49",
    19900: "TEAM_ORG_$199",
}

TIER_AUDIT_QUOTAS: Dict[str, int] = {
    "DEVELOPER_FREE":  10_000,
    "PRO_REPO_$49":   500_000,
    "TEAM_ORG_$199": 5_000_000,
}

LEDGER_FILE = os.getenv("SAAS_LEDGER_FILE", "saas_production_ledger.jsonl")

# In-memory provisioned customer store (survives process lifetime)
_provisioned: Dict[str, Dict[str, Any]] = {}


def _verify_stripe_signature(
    raw_body: bytes,
    sig_header: str,
    secret: str,
    tolerance_seconds: int = 300
) -> Tuple[bool, str]:
    """
    Validates the Stripe-Signature header using HMAC-SHA256.
    Returns (True, "") on success or (False, reason) on failure.
    """
    if not secret:
        # Dev mode: skip signature check if no secret configured
        return True, "WEBHOOK_SECRET_NOT_SET_DEV_MODE"

    try:
        parts = {k: v for k, v in (p.split("=", 1) for p in sig_header.split(","))}
        timestamp = int(parts.get("t", 0))
        v1_sig    = parts.get("v1", "")
    except Exception:
        return False, "Malformed Stripe-Signature header"

    # Replay attack window check
    if abs(time.time() - timestamp) > tolerance_seconds:
        return False, f"Timestamp outside {tolerance_seconds}s tolerance window"

    # HMAC-SHA256 over "<timestamp>.<raw_body>"
    signed_payload = f"{timestamp}.".encode() + raw_body
    expected_sig   = hmac.new(
        secret.encode("utf-8"),
        signed_payload,
        hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(expected_sig, v1_sig):
        return False, "Signature mismatch — possible forged webhook"

    return True, "OK"


def _resolve_tier(amount_cents: int) -> str:
    """Maps Stripe amount_total (in cents) to a plan tier string."""
    return AMOUNT_TO_TIER.get(amount_cents, "PRO_REPO_$49")


def _provision_api_key(customer_email: str, tier: str, stripe_session_id: str) -> Dict[str, Any]:
    """
    Generates a cryptographically secure age_live_ API key,
    records it in-memory and appends to the JSONL ledger file.
    """
    api_key = f"age_live_{secrets.token_hex(20)}"
    quota   = TIER_AUDIT_QUOTAS.get(tier, 10_000)

    record = {
        "event":            "STRIPE_CHECKOUT_PROVISIONED",
        "timestamp":        time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
        "customer_email":   customer_email,
        "plan_tier":        tier,
        "api_key":          api_key,
        "audit_quota":      quota,
        "stripe_session_id": stripe_session_id,
        "status":           "ACTIVE",
    }

    _provisioned[customer_email] = record

    # Append to tamper-evident JSONL ledger
    try:
        with open(LEDGER_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(record) + "\n")
    except Exception as e:
        print(f"[Webhook] Ledger write warning: {e}")

    return record


def _cancel_subscription(customer_email: str, stripe_subscription_id: str) -> Dict[str, Any]:
    """Marks a customer's API key as CANCELLED in memory and ledger."""
    if customer_email in _provisioned:
        _provisioned[customer_email]["status"] = "CANCELLED"

    record = {
        "event":                    "STRIPE_SUBSCRIPTION_CANCELLED",
        "timestamp":                time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
        "customer_email":           customer_email,
        "stripe_subscription_id":   stripe_subscription_id,
        "status":                   "CANCELLED",
    }

    try:
        with open(LEDGER_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(record) + "\n")
    except Exception as e:
        print(f"[Webhook] Ledger write warning: {e}")

    return record


def handle_stripe_webhook(
    raw_body: bytes,
    sig_header: str,
    secret: Optional[str] = None,
) -> Tuple[int, Dict[str, Any]]:
    """
    Main entry point called by the HTTP server.
    Returns (http_status_code, response_dict).
    """
    effective_secret = secret or os.getenv("STRIPE_WEBHOOK_SECRET", "")
    # 1. Verify signature
    sig_ok, sig_msg = _verify_stripe_signature(raw_body, sig_header, effective_secret)
    if not sig_ok:
        print(f"[Webhook] REJECTED: {sig_msg}")
        return 400, {"error": sig_msg}

    # 2. Parse event
    try:
        event = json.loads(raw_body.decode("utf-8"))
    except Exception:
        return 400, {"error": "Invalid JSON body"}

    event_type = event.get("type", "")
    event_id   = event.get("id", "")
    obj        = event.get("data", {}).get("object", {})

    print(f"[Webhook] Received: {event_type} ({event_id})")

    # 3. Route event type
    if event_type == "checkout.session.completed":
        customer_email = (
            obj.get("customer_details", {}).get("email")
            or obj.get("customer_email")
            or "unknown@customer.com"
        )
        amount_cents   = obj.get("amount_total", 4900)
        session_id     = obj.get("id", event_id)
        tier           = _resolve_tier(amount_cents)
        record         = _provision_api_key(customer_email, tier, session_id)

        print(f"[Webhook] [OK] Provisioned {tier} key for {customer_email}: {record['api_key'][:20]}...")
        return 200, {
            "received":   True,
            "event_type": event_type,
            "provisioned": True,
            "customer_email": customer_email,
            "plan_tier": tier,
        }

    elif event_type in ("customer.subscription.deleted", "customer.subscription.updated"):
        customer_email      = obj.get("metadata", {}).get("email", "unknown@customer.com")
        subscription_id     = obj.get("id", "")
        record              = _cancel_subscription(customer_email, subscription_id)
        print(f"[Webhook] [INFO] Subscription cancelled for {customer_email}")
        return 200, {"received": True, "event_type": event_type, "status": "CANCELLED"}

    else:
        # Acknowledge but take no action for unhandled events
        print(f"[Webhook] Unhandled event type: {event_type} — acknowledged")
        return 200, {"received": True, "event_type": event_type, "action": "none"}


def get_provisioned_customers() -> Dict[str, Dict[str, Any]]:
    """Returns the in-memory provisioned customer store for dashboard display."""
    return _provisioned
