"""
Tests for BTP v2.8.0 FROST Threshold CLI & Swarm Quorum Signing
================================================================
Validates end-to-end execution of:
  - threshold-keygen
  - threshold-sign
  - threshold-verify
  - ByzantineSwarmEngine.attach_frost_signature
"""

import os
import sys
import json
import subprocess
import pytest

from src.frost_threshold_engine import frost_keygen, FrostSigner, FrostCoordinator
from src.byzantine_swarm_consensus import ByzantineSwarmEngine


def test_cli_threshold_roundtrip(tmp_path):
    """Full CLI roundtrip: keygen -> sign -> verify."""
    shares_dir = tmp_path / "shares"
    shares_dir.mkdir()
    sig_file = tmp_path / "action_sig.json"
    payload_file = tmp_path / "action.json"
    payload_file.write_text(json.dumps({"action": "DEPLOY_MODEL", "model": "gemini-pro"}))

    # 1. Keygen (2-of-4)
    cmd_kg = [
        sys.executable, "cli.py", "threshold-keygen",
        "--threshold", "2",
        "--participants", "4",
        "--out", str(shares_dir)
    ]
    res_kg = subprocess.run(cmd_kg, capture_output=True, text=True)
    assert res_kg.returncode == 0
    assert (shares_dir / "group_pubkey.json").exists()
    assert (shares_dir / "share_1.json").exists()
    assert (shares_dir / "share_4.json").exists()

    # 2. Sign with 3 shares (1, 3, 4)
    cmd_sign = [
        sys.executable, "cli.py", "threshold-sign",
        "--shares",
        str(shares_dir / "share_1.json"),
        str(shares_dir / "share_3.json"),
        str(shares_dir / "share_4.json"),
        "--payload", str(payload_file),
        "--out", str(sig_file)
    ]
    res_sign = subprocess.run(cmd_sign, capture_output=True, text=True)
    assert res_sign.returncode == 0
    assert sig_file.exists()

    with open(sig_file, "r") as f:
        sig_data = json.load(f)
    assert sig_data["valid"] is True
    assert sig_data["signing_indices"] == [1, 3, 4]

    # 3. Verify signature
    cmd_verify = [
        sys.executable, "cli.py", "threshold-verify",
        "--sig", str(sig_file),
        "--payload", str(payload_file)
    ]
    res_verify = subprocess.run(cmd_verify, capture_output=True, text=True)
    assert res_verify.returncode == 0
    assert "PASS" in res_verify.stdout


def test_cli_threshold_insufficient_shares_fails(tmp_path):
    """Attempting to sign with fewer than t+1 shares exits with code 2."""
    shares_dir = tmp_path / "shares"
    shares_dir.mkdir()
    payload_file = tmp_path / "action.json"
    payload_file.write_text(json.dumps({"action": "TRANSFER", "amount": 1000}))

    # Keygen (2-of-4 requires 3 signers)
    subprocess.run([
        sys.executable, "cli.py", "threshold-keygen",
        "--threshold", "2",
        "--participants", "4",
        "--out", str(shares_dir)
    ], check=True)

    # Attempt signing with only 2 shares
    cmd_sign = [
        sys.executable, "cli.py", "threshold-sign",
        "--shares",
        str(shares_dir / "share_1.json"),
        str(shares_dir / "share_2.json"),
        "--payload", str(payload_file),
    ]
    res_sign = subprocess.run(cmd_sign, capture_output=True, text=True)
    assert res_sign.returncode == 2
    assert "Insufficient signers" in res_sign.stdout or "Insufficient signers" in res_sign.stderr


def test_cli_threshold_tampered_payload_detected(tmp_path):
    """Verifying with a modified payload detects the discrepancy and fails."""
    shares_dir = tmp_path / "shares"
    shares_dir.mkdir()
    sig_file = tmp_path / "sig.json"
    orig_payload = tmp_path / "orig.json"
    orig_payload.write_text("VALID_DATA")
    tampered_payload = tmp_path / "tampered.json"
    tampered_payload.write_text("TAMPERED_DATA")

    subprocess.run([
        sys.executable, "cli.py", "threshold-keygen",
        "-t", "1",
        "-n", "3",
        "-o", str(shares_dir)
    ], check=True)

    subprocess.run([
        sys.executable, "cli.py", "threshold-sign",
        "-s", str(shares_dir / "share_1.json"), str(shares_dir / "share_2.json"),
        "-p", str(orig_payload),
        "-o", str(sig_file)
    ], check=True)

    # Verify against tampered payload
    res_tamper = subprocess.run([
        sys.executable, "cli.py", "threshold-verify",
        "--sig", str(sig_file),
        "--payload", str(tampered_payload)
    ], capture_output=True, text=True)
    assert res_tamper.returncode == 2
    assert "Payload hash mismatch" in res_tamper.stdout


def test_byzantine_swarm_attach_frost_signature():
    """Swarm PBFT consensus directly coordinates and embeds FROST threshold signature."""
    agents = ["agent-1", "agent-2", "agent-3", "agent-4"]
    swarm = ByzantineSwarmEngine(agents)
    prop_id = "prop-42"
    payload = {"query": "SELECT * FROM secrets", "authorized": True}

    swarm.submit_proposal(prop_id, "agent-1", "SECRET_QUERY", payload)
    for a in ["agent-1", "agent-2", "agent-3"]:
        swarm.cast_vote(prop_id, a, "APPROVE")

    reached, cert, _ = swarm.evaluate_consensus(prop_id)
    assert reached is True

    # FROST setup (3-of-4)
    keygens = frost_keygen(n=4, t=2)
    signers = {agents[i]: FrostSigner(keygens[i]) for i in range(4)}
    coordinator = FrostCoordinator(group_pubkey=keygens[0].group_pubkey, threshold=2)

    ok, sig_dict, msg = swarm.attach_frost_signature(prop_id, signers, coordinator)
    assert ok is True
    assert cert.frost_signature is not None
    assert cert.frost_signature["valid"] is True
    assert "BTP_FROST_ATTACHED" in msg
