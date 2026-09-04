"""
Unit Tests for BTP v2.9 & v3.0 CLI Toolchain Commands
=====================================================
Validates CLI operations:
  - btp-guard hybrid-sign (FROST RFC 9591 + Post-Quantum WOTS+)
  - btp-guard hybrid-verify
  - btp-guard zk-prove (Pedersen + Fiat-Shamir Zero-Knowledge Proofs)
  - btp-guard zk-verify
"""

import json
import os
import subprocess
import sys
import tempfile
import pytest


@pytest.fixture
def cli_test_env():
    """Create temp directory and 2-of-3 threshold keys for CLI testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        keygen_cmd = [
            sys.executable, "cli.py", "threshold-keygen",
            "--threshold", "1",
            "--participants", "3",
            "--out", tmpdir,
        ]
        res = subprocess.run(keygen_cmd, capture_output=True, text=True, check=True)
        assert res.returncode == 0
        yield tmpdir


def test_cli_hybrid_sign_and_verify(cli_test_env):
    """Test full BTP v2.9 Hybrid Threshold CLI workflow."""
    tmpdir = cli_test_env
    share1 = os.path.join(tmpdir, "share_1.json")
    share2 = os.path.join(tmpdir, "share_2.json")
    payload_file = os.path.join(tmpdir, "mission_action.json")
    envelope_file = os.path.join(tmpdir, "hybrid_envelope.json")

    with open(payload_file, "w", encoding="utf-8") as f:
        json.dump({"action": "deploy_smart_contract", "target": "production_cluster"}, f)

    # 1. hybrid-sign
    sign_cmd = [
        sys.executable, "cli.py", "hybrid-sign",
        "--shares", share1, share2,
        "--payload", payload_file,
        "--out", envelope_file,
    ]
    res_sign = subprocess.run(sign_cmd, capture_output=True, text=True)
    assert res_sign.returncode == 0, res_sign.stderr
    assert "BTP v2.9 HYBRID POST-QUANTUM THRESHOLD SIGNING CEREMONY" in res_sign.stdout
    assert os.path.exists(envelope_file)

    # 2. hybrid-verify (valid)
    verify_cmd = [
        sys.executable, "cli.py", "hybrid-verify",
        "--envelope", envelope_file,
        "--payload", payload_file,
    ]
    res_ver = subprocess.run(verify_cmd, capture_output=True, text=True)
    assert res_ver.returncode == 0, res_ver.stderr
    assert "PASS (100% VALID)" in res_ver.stdout

    # 3. hybrid-verify (tampered payload must fail)
    tampered_payload = os.path.join(tmpdir, "tampered.json")
    with open(tampered_payload, "w", encoding="utf-8") as f:
        json.dump({"action": "exfiltrate_secrets"}, f)

    res_fail = subprocess.run(
        [sys.executable, "cli.py", "hybrid-verify", "--envelope", envelope_file, "--payload", tampered_payload],
        capture_output=True,
        text=True,
    )
    assert res_fail.returncode != 0
    assert "FAIL" in res_fail.stdout or "TAMPERED" in res_fail.stdout


def test_cli_zk_prove_and_verify(cli_test_env):
    """Test full BTP v3.0 Zero-Knowledge Compliance CLI workflow."""
    tmpdir = cli_test_env
    receipt_file = os.path.join(tmpdir, "zk_receipt.json")

    # 1. zk-prove
    prove_cmd = [
        sys.executable, "cli.py", "zk-prove",
        "--session-id", "test-session-astra-001",
        "--actions", "read_file('/etc/hosts')", "http_get('https://api.example.com')",
        "--out", receipt_file,
    ]
    res_prove = subprocess.run(prove_cmd, capture_output=True, text=True)
    assert res_prove.returncode == 0, res_prove.stderr
    assert "BTP v3.0 ZERO-KNOWLEDGE INVARIANT COMPLIANCE PROVER" in res_prove.stdout
    assert os.path.exists(receipt_file)

    with open(receipt_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    receipt = data["btp_proof_receipt"]
    assert receipt["proof_valid"] is True
    # Zero-knowledge: make sure raw action plaintext is not present in receipt
    assert "read_file" not in json.dumps(receipt)

    # 2. zk-verify (valid)
    verify_cmd = [
        sys.executable, "cli.py", "zk-verify",
        "--receipt", receipt_file,
    ]
    res_ver = subprocess.run(verify_cmd, capture_output=True, text=True)
    assert res_ver.returncode == 0, res_ver.stderr
    assert "PASS (COMPLIANCE VERIFIED)" in res_ver.stdout

    # 3. zk-verify (tampered receipt must fail)
    tampered_receipt_file = os.path.join(tmpdir, "tampered_receipt.json")
    receipt["aggregate_response_hex"] = hex(int(receipt["aggregate_response_hex"], 16) + 1)
    with open(tampered_receipt_file, "w", encoding="utf-8") as f:
        json.dump({"btp_proof_receipt": receipt}, f)

    res_tamper = subprocess.run(
        [sys.executable, "cli.py", "zk-verify", "--receipt", tampered_receipt_file],
        capture_output=True,
        text=True,
    )
    assert res_tamper.returncode != 0
    assert "FAIL" in res_tamper.stdout
