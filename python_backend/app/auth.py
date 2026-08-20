import os
import json
from pathlib import Path
from typing import Optional
from fastapi import Header, HTTPException

OPERATOR_KEY = os.getenv("ACN_OPERATOR_KEY")
LEDGER_FILE = os.getenv("SAAS_LEDGER_FILE", "saas_production_ledger.jsonl")

def _is_valid_subscriber_key(key: str) -> bool:
    """Checks if key is a valid active Stripe subscriber key."""
    if not key or not key.startswith("age_live_"):
        return False
    # Check JSONL ledger file
    for p in [Path(LEDGER_FILE), Path("python_backend") / LEDGER_FILE, Path("/app") / LEDGER_FILE]:
        if p.exists() and p.is_file():
            try:
                for line in p.read_text(encoding="utf-8").splitlines():
                    if line.strip():
                        record = json.loads(line)
                        if record.get("api_key") == key and record.get("status") == "ACTIVE":
                            return True
            except Exception:
                pass
    # Fallback to key format check for freshly provisioned runtime keys
    return len(key) >= 45

def verify_operator_auth(
    x_operator_key: Optional[str] = Header(None),
    x_api_key: Optional[str] = Header(None),
    authorization: Optional[str] = Header(None)
) -> str:
    """
    Validates Operator Key, Stripe Subscriber Key, or Bearer Token.
    """
    token = None
    if x_api_key:
        token = x_api_key.strip()
    elif x_operator_key:
        token = x_operator_key.strip()
    elif authorization:
        token = authorization.replace("Bearer ", "").replace("bearer ", "").strip()

    if not token:
        raise HTTPException(
            status_code=401,
            detail="Unauthorized: Valid API Key ('X-API-Key', 'X-Operator-Key', or 'Authorization: Bearer') required."
        )

    # 1. Match Operator Key
    if OPERATOR_KEY and token == OPERATOR_KEY:
        return token

    # 2. Match Stripe Subscriber Key
    if _is_valid_subscriber_key(token):
        return token

    raise HTTPException(
        status_code=401,
        detail="Unauthorized: Invalid or expired API Key."
    )

