"""
Test Suite for Auth Module
"""
import sys
import os
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

try:
    from src.auth import verify_token
except ImportError:
    from auth import verify_token  # type: ignore


def test_valid_token():
    assert verify_token("valid_token_123", time.time() + 60) == True


def test_expired_token():
    assert verify_token("valid_token_123", time.time() - 10) == False


def test_token_expiry_clock_drift():
    # Tests a token expiring within 2 second leeway window
    token_exp = time.time() - 0.5
    assert verify_token("valid_token_123", token_exp) == False
