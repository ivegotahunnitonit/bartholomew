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


def test_cli_mcp_status():
    """Validate btp-guard mcp status reports all 10 registered tools and BTP v3.1 info."""
    cmd = [sys.executable, "cli.py", "mcp", "status"]
    res = subprocess.run(cmd, capture_output=True, text=True)
    assert res.returncode == 0, res.stderr
    assert "BARTHOLOMEW MODEL CONTEXT PROTOCOL (MCP) RUNTIME STATUS" in res.stdout
    assert "BTP v3.1" in res.stdout
    assert "13 ACTIVE" in res.stdout
    assert "btp_execute_command" in res.stdout
    assert "btp_issue_execution_bond" in res.stdout
    assert "btp_slash_execution_bond" in res.stdout
    assert "btp_get_bond_status" in res.stdout
    assert "btp_issue_agent_passport" in res.stdout
    assert "btp_discover_agent_peers" in res.stdout


def test_cli_mcp_install_dry_run():
    """Validate btp-guard mcp install --dry-run across claude, cursor, and astra."""
    for target in ["claude", "cursor", "astra"]:
        cmd = [sys.executable, "cli.py", "mcp", "install", "--target", target, "--dry-run"]
        res = subprocess.run(cmd, capture_output=True, text=True)
        assert res.returncode == 0, res.stderr
        assert f"Target runtime : {target.upper()}" in res.stdout
        assert "[DRY-RUN]" in res.stdout
        assert "bartholomew-guard" in res.stdout
        assert "bartholomew" in res.stdout


def test_cli_bond_lifecycle():
    """Validate full BTP v3.1 Bond Issuance and Invariant Slashing lifecycle via CLI."""
    with tempfile.TemporaryDirectory() as tmpdir:
        bond_file = os.path.join(tmpdir, "test_bond.json")
        
        # 1. Issue warranty bond
        issue_cmd = [
            sys.executable, "cli.py", "bond", "issue",
            "--agent", "gpt6-astra-evaluator",
            "--action", "DATABASE_MIGRATION",
            "--amount", "7500.0",
            "--out", bond_file,
        ]
        res_issue = subprocess.run(issue_cmd, capture_output=True, text=True)
        assert res_issue.returncode == 0, res_issue.stderr
        assert "BTP v3.1 BONDED EXECUTION WARRANTY ISSUANCE" in res_issue.stdout
        assert "$7,500.00 USD" in res_issue.stdout
        assert os.path.exists(bond_file)

        # 2. Arbitrate and slash bond upon verified breach
        slash_cmd = [
            sys.executable, "cli.py", "bond", "slash",
            "--bond-id", bond_file,
            "--reason", "Unverified production schema drop attempt",
        ]
        res_slash = subprocess.run(slash_cmd, capture_output=True, text=True)
        assert res_slash.returncode == 0, res_slash.stderr
        assert "SLASH APPROVED" in res_slash.stdout
        assert "$7,500.00 USD" in res_slash.stdout


def test_cli_audit_certification():
    """Validate btp-guard audit --certify generates verifiable compliance package & HTML."""
    with tempfile.TemporaryDirectory() as tmpdir:
        cert_html = os.path.join(tmpdir, "soc2_cert.html")
        cert_json = os.path.join(tmpdir, "soc2_package.json")

        # 1. HTML export
        cmd_html = [
            sys.executable, "cli.py", "audit", "policies/",
            "--certify",
            "--org", "Acme Frontier AI Systems",
            "--out", cert_html,
        ]
        res_html = subprocess.run(cmd_html, capture_output=True, text=True)
        assert res_html.returncode == 0, res_html.stderr
        assert "BTP v3.2 ENTERPRISE COMPLIANCE & CRYPTOGRAPHIC AUDIT CERTIFICATE" in res_html.stdout
        assert "Acme Frontier AI Systems" in res_html.stdout
        assert os.path.exists(cert_html)
        with open(cert_html, "r", encoding="utf-8") as f:
            html_text = f.read()
            assert "Bartholomew Autonomous AI Compliance Certificate" in html_text
            assert "Acme Frontier AI Systems" in html_text

        # 2. JSON export
        cmd_json = [
            sys.executable, "cli.py", "audit", "policies/",
            "--certify",
            "--org", "Acme Frontier AI Systems",
            "--out", cert_json,
        ]
        res_json = subprocess.run(cmd_json, capture_output=True, text=True)
        assert res_json.returncode == 0, res_json.stderr
        assert os.path.exists(cert_json)
        with open(cert_json, "r", encoding="utf-8") as f:
            data = json.load(f)
            assert "merkle_root_hash" in data
            assert "sovereign_signature" in data
            assert data["signer_public_key"]


def test_cli_enclave_lifecycle():
    """Validate BTP v3.2 Confidential Enclave status, attest, and verify lifecycle."""
    with tempfile.TemporaryDirectory() as tmpdir:
        doc_file = os.path.join(tmpdir, "enclave_attestation.json")

        # 1. Status
        res_stat = subprocess.run([sys.executable, "cli.py", "enclave", "status"], capture_output=True, text=True)
        assert res_stat.returncode == 0, res_stat.stderr
        assert "BTP v3.2 CONFIDENTIAL COMPUTING & HARDWARE ENCLAVE RUNTIME" in res_stat.stdout
        assert "AWS Nitro Enclaves / AMD SEV-SNP" in res_stat.stdout

        # 2. Attest
        attest_cmd = [
            sys.executable, "cli.py", "enclave", "attest",
            "--module-id", "enclave-worker-node-01",
            "--nonce", "beefc001cafe002233445566778899aa",
            "--out", doc_file,
        ]
        res_att = subprocess.run(attest_cmd, capture_output=True, text=True)
        assert res_att.returncode == 0, res_att.stderr
        assert "BTP v3.2 CONFIDENTIAL HARDWARE ENCLAVE ATTESTATION" in res_att.stdout
        assert os.path.exists(doc_file)

        # 3. Verify (valid)
        ver_cmd = [
            sys.executable, "cli.py", "enclave", "verify",
            "--document", doc_file,
            "--nonce", "beefc001cafe002233445566778899aa",
        ]
        res_ver = subprocess.run(ver_cmd, capture_output=True, text=True)
        assert res_ver.returncode == 0, res_ver.stderr
        assert "PASS (HARDWARE PROOF CERTIFIED)" in res_ver.stdout

        # 4. Verify with tampered nonce (must fail)
        bad_ver_cmd = [
            sys.executable, "cli.py", "enclave", "verify",
            "--document", doc_file,
            "--nonce", "tampered_nonce_12345",
        ]
        res_bad = subprocess.run(bad_ver_cmd, capture_output=True, text=True)
        assert res_bad.returncode != 0
        assert "FAIL" in res_bad.stdout


def test_cli_passport_lifecycle():
    """Validate BTP v3.1 Sovereign Digital Passport issuance and verification via CLI."""
    with tempfile.TemporaryDirectory() as tmpdir:
        pass_file = os.path.join(tmpdir, "agent_passport.json")

        # 1. Issue passport
        issue_cmd = [
            sys.executable, "cli.py", "passport", "issue",
            "--agent", "agent-worker-42",
            "--model", "claude-3-5-sonnet",
            "--capabilities", "data:read,code:mutate",
            "--bond", "3500.0",
            "--out", pass_file
        ]
        res_issue = subprocess.run(issue_cmd, capture_output=True, text=True)
        assert res_issue.returncode == 0, res_issue.stderr
        assert "BTP v3.1 SOVEREIGN AGENT DIGITAL PASSPORT ISSUANCE" in res_issue.stdout
        assert "agent-worker-42" in res_issue.stdout
        assert os.path.exists(pass_file)

        # 2. Verify valid passport
        ver_cmd = [
            sys.executable, "cli.py", "passport", "verify",
            "--file", pass_file,
            "--capability", "code:mutate"
        ]
        res_ver = subprocess.run(ver_cmd, capture_output=True, text=True)
        assert res_ver.returncode == 0, res_ver.stderr
        assert "PASS (AUTHORIZED)" in res_ver.stdout

        # 3. Verify unauthorized capability (must fail with exit code 1)
        unauth_cmd = [
            sys.executable, "cli.py", "passport", "verify",
            "--file", pass_file,
            "--capability", "root:admin"
        ]
        res_unauth = subprocess.run(unauth_cmd, capture_output=True, text=True)
        assert res_unauth.returncode != 0
        assert "FAIL (REJECTED)" in res_unauth.stdout


def test_cli_peers_discover():
    """Validate BTP v3.1 Autonomous Agent Peer Discovery via CLI."""
    disc_cmd = [
        sys.executable, "cli.py", "peers", "discover",
        "--capability", "data:read"
    ]
    res_disc = subprocess.run(disc_cmd, capture_output=True, text=True)
    assert res_disc.returncode == 0, res_disc.stderr
    assert "BTP v3.1 AUTONOMOUS PEER DISCOVERY MESH" in res_disc.stdout


