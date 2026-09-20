"""
Tests for Milestones 3.3 (Cookbooks), 3.4 (Production Container Daemon & Prometheus),
and 4.0 Prep (Autonomous Micro-Escrow & Slashing Settlements).
"""

import json
import time
import urllib.request
import pytest
from cryptography.hazmat.primitives.asymmetric import ed25519

from src.daemon.btp_daemon import BTPDaemon, GLOBAL_METRICS
from src.settlement.autonomous_escrow import AutonomousEscrowPool
from src.agent_passport import SovereignAgentPassport

# Import cookbook main functions
from examples.crewai_secure_coding_swarm.run_swarm import main as crewai_main
from examples.langgraph_financial_analyst.run_workflow import main as langgraph_main
from examples.autogen_multiagent_defense.run_groupchat import main as autogen_main
from examples.llamaindex_rag_guard.run_rag import main as llamaindex_main


def test_milestone_33_framework_cookbooks():
    """Verify all 4 developer cookbook recipes run cleanly without errors."""
    assert crewai_main() is True
    assert langgraph_main() is True
    assert autogen_main() is True
    assert llamaindex_main() is True


def test_milestone_34_production_daemon_and_prometheus():
    """Verify BTP Container Daemon HTTP endpoints, Prometheus formatting, and ZK rollup anchoring."""
    test_port = 19091
    daemon = BTPDaemon(host="127.0.0.1", port=test_port)
    daemon.start()
    time.sleep(0.1)

    base_url = f"http://127.0.0.1:{test_port}"
    try:
        # 1. Test /healthz
        req = urllib.request.Request(f"{base_url}/healthz")
        with urllib.request.urlopen(req) as response:
            assert response.status == 200
            data = json.loads(response.read().decode())
            assert data["status"] == "healthy"
            assert data["service"] == "btp-daemon"
            assert data["version"] == "3.5.0"

        # 2. Test /metrics Prometheus exposition
        GLOBAL_METRICS.update_threat_entropy(0.125, 3, 5)
        GLOBAL_METRICS.record_blocked_syscall()
        req_metrics = urllib.request.Request(f"{base_url}/metrics")
        with urllib.request.urlopen(req_metrics) as response:
            assert response.status == 200
            metrics_text = response.read().decode()
            assert "# HELP btp_threat_entropy_ratio" in metrics_text
            assert "btp_threat_entropy_ratio 0.125" in metrics_text
            assert "btp_active_quorum_k 3" in metrics_text
            assert "btp_active_quorum_n 5" in metrics_text
            assert "btp_blocked_syscalls_total" in metrics_text

        # 3. Test /api/v1/anchor POST endpoint
        anchor_payload = {
            "sessions": [
                {"session_id": "sess-alpha-01", "tool_calls": ["ls -la", "cat /app/data.json"]},
                {"session_id": "sess-beta-02", "tool_calls": ["python script.py"]}
            ]
        }
        req_anchor = urllib.request.Request(
            f"{base_url}/api/v1/anchor",
            data=json.dumps(anchor_payload).encode(),
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req_anchor) as response:
            assert response.status == 200
            anchor_res = json.loads(response.read().decode())
            assert anchor_res["status"] == "HARDWARE_ANCHORED_AND_ATTESTED"
            assert anchor_res["session_count"] == 2
            assert "merkle_root" in anchor_res
            assert "hardware_enclave_attestation" in anchor_res

        # Confirm Prometheus counters incremented
        assert GLOBAL_METRICS.zk_rollups_sealed_total >= 1
        assert GLOBAL_METRICS.enclave_attestations_total >= 1

    finally:
        daemon.stop()


def test_milestone_40_autonomous_escrow_and_slashing():
    """Verify autonomous micro-escrow locking, release, and automated slashing with passport tripping."""
    pool = AutonomousEscrowPool(reserve_pool_usd=50_000.0, max_escrow_per_action_usd=5_000.0)

    owner_key = ed25519.Ed25519PrivateKey.generate()
    owner_pubkey_hex = owner_key.public_key().public_bytes_raw().hex()

    passport = SovereignAgentPassport(
        agent_id="Agent-Escrow-Target-01",
        worker_model="Claude-3.5-Sonnet",
        owner_pubkey=owner_pubkey_hex,
        granted_capabilities=["db:query", "fs:write"]
    )
    passport.sign(owner_key)

    # 1. Lock Escrow Deposit
    deposit = pool.lock_escrow(
        agent_id="Agent-Escrow-Target-01",
        action_type="DATABASE_MIGRATION",
        amount_usd=1_500.0,
        passport=passport,
        settlement_rail="L402_LIGHTNING"
    )
    assert deposit.status == "LOCKED"
    assert deposit.amount_usd == 1500.0
    assert deposit.escrow_id.startswith("ESCROW-")

    # 2. Test Clean Escrow Release
    deposit_clean = pool.lock_escrow(
        agent_id="Agent-Escrow-Target-01",
        action_type="READ_ONLY_AUDIT",
        amount_usd=500.0,
        passport=passport
    )
    ok_rel, msg_rel = pool.release_escrow(deposit_clean.escrow_id)
    assert ok_rel is True
    assert pool.active_escrows[deposit_clean.escrow_id].status == "RELEASED"

    # 3. Fraudulent Claim Rejection (Missing Invariant or Action Mismatch)
    fraudulent_proof = {
        "type": "BTP_REGRESSION_PROOF",
        "proof_signature": "sig_abc",
        "target_action": "DIFFERENT_ACTION",
        "violated_invariant": "CATASTROPHIC_DROP"
    }
    ok_fraud, msg_fraud, _ = pool.claim_and_slash(
        escrow_id=deposit.escrow_id,
        regression_proof=fraudulent_proof,
        payee_destination="lnbc1500u..."
    )
    assert ok_fraud is False
    assert "does not match escrow action" in msg_fraud

    # 4. Verified Claim & Automated Slashing
    valid_regression_proof = {
        "type": "BTP_REGRESSION_PROOF",
        "proof_signature": "ed25519_valid_signature_evidence_9981",
        "target_action": "DATABASE_MIGRATION",
        "violated_invariant": "INVARIANT_VIOLATION: DROP_TABLE_WITHOUT_SNAPSHOT"
    }
    ok_slash, msg_slash, receipt = pool.claim_and_slash(
        escrow_id=deposit.escrow_id,
        regression_proof=valid_regression_proof,
        payee_destination="lnbc150000000satoshis_invoice_hash",
        agent_passport=passport
    )

    assert ok_slash is True
    assert "slashed and liquidated indemnity disbursed" in msg_slash
    assert receipt["status"] == "DISBURSED_AND_SETTLED"
    assert receipt["passport_tripped"] is True
    assert pool.active_escrows[deposit.escrow_id].status == "SLASHED"

    # Verify passport circuit breaker was tripped
    assert passport.circuit_breaker_tripped is True

    # 5. Tripped Passport cannot lock new escrows
    with pytest.raises(PermissionError, match="circuit-breaker TRIPPED"):
        pool.lock_escrow(
            agent_id="Agent-Escrow-Target-01",
            action_type="ANOTHER_TASK",
            amount_usd=500.0,
            passport=passport
        )
