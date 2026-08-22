import os
import sys
import pytest

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from src import Guard, wrap_client


def test_guard_direct_check():
    guard = Guard(spend_cap=100.0)

    # Safe SQL passes
    res = guard.check("SELECT * FROM customers WHERE id = 10")
    assert res["allowed"] is True
    assert res["verdict"] == "ALLOW"

    # Destructive command blocked instantly
    res = guard.check("rm -rf /var/data")
    assert res["allowed"] is False
    assert res["verdict"] == "DENY"
    assert "forbidden" in res["reason"].lower() or "violation" in res["reason"].lower()

    # Over budget blocked
    res = guard.check("PAYMENT", amount_usd=150.0)
    assert res["allowed"] is False
    assert "Spend limit exceeded" in res["reason"]


def test_guard_decorator():
    guard = Guard()

    @guard.protect
    def run_query(sql: str):
        return f"Executed: {sql}"

    # Safe call works
    assert run_query("SELECT id FROM users") == "Executed: SELECT id FROM users"

    # Malicious call raises PermissionError
    with pytest.raises(PermissionError) as exc_info:
        run_query("DROP TABLE users CASCADE;")
    assert "Bartholomew Blocked Action" in str(exc_info.value)


def test_wrap_client_integration():
    class DummyClient:
        def execute(self, cmd: str):
            return f"Ran: {cmd}"

    client = DummyClient()
    protected_client = wrap_client(client, spend_cap=50.0)

    # Safe call executes
    assert protected_client.execute("ls -la") == "Ran: ls -la"

    # Destructive call blocked
    with pytest.raises(PermissionError):
        protected_client.execute("rm -rf /")


if __name__ == "__main__":
    test_guard_direct_check()
    test_guard_decorator()
    test_wrap_client_integration()
    print("[OK] ALL SIMPLE GUARD TESTS PASSED!")
