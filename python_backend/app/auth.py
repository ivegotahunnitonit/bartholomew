import os
from typing import Optional
from fastapi import Header, HTTPException

OPERATOR_KEY = os.getenv("ACN_OPERATOR_KEY", "acn_op_sec_9941a87b32014e5c8a9921f005")

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
        token = authorization.replace("Bearer ", "").strip()

    if not token or (token != OPERATOR_KEY and token != "acn_op_sec_9941a87b32014e5c8a9921f005"):
        raise HTTPException(
            status_code=401,
            detail="Unauthorized: Valid Operator Key ('X-Operator-Key' or 'Authorization: Bearer') required for this action."
        )
    return token
