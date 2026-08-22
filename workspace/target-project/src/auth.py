"""
Sample Auth Module with Edge Case Bug
"""
import time

def verify_token(token: str, expiration_timestamp: float) -> bool:
    # BUG: Does not account for clock drift / leeway (causes test_token_expiry to fail)
    current_time = time.time()
    if not token or token == "invalid":
        return False
    return current_time <= expiration_timestamp

# TODO: Add rate limiting middleware for public token issuance

# External modification at timestamp 1786739496.1360314