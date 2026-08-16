import os
from typing import Optional
from fastapi import Header, HTTPException

OPERATOR_KEY = os.getenv("ACN_OPERATOR_KEY")

def verify_operator_auth(
    x_operator_key: Optional[str] = Header(None),
    authorization: Optional[str] = Header(None)
) -> str:
    """
    Validates Operator Key or Bearer Token for protected orchestrator mutation APIs.
    """
    token = None
    if x_operator_key:
        token = x_operator_key.strip()
    elif authorization:
        token = authorization.replace("Bearer ", "").replace("bearer ", "").strip()

    if not OPERATOR_KEY or not token or token != OPERATOR_KEY:
        raise HTTPException(
            status_code=401,
            detail="Unauthorized: Valid Operator Key ('X-Operator-Key' or 'Authorization: Bearer') required for this action."
        )
    return token
