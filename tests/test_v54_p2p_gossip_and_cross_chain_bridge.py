import pytest
import os
import json
import time
from src.p2p.reputation_gossip import (
    PeerReputationMesh,
    PeerNode,
    ReputationGossipMessage,
)
from src.settlement.cross_chain_bridge import (
    CrossChainBridgeRelay,
    BridgeVoucher,
)


@pytest.fixture
def clean_mesh(tmp_path):
    store_path = str(tmp_path / "test_gossip_ledger.json")
    mesh = PeerReputationMesh(store_path=store_path)
    return mesh


@pytest.fixture
def clean_bridge(tmp_path):
    store_path = str(tmp_path / "test_bridge_ledger.json")
    bridge = CrossChainBridgeRelay(store_path=store_path)
    return bridge


class TestP2PReputationMesh:
    def test_default_peers_initialization(self, clean_mesh):
        mesh = clean_mesh
        assert len(mesh.peers) >= 4
        assert "agent-code-auditor-99" in mesh.peers
        assert mesh.peers["agent-code-auditor-99"].is_pretrusted is True
        assert mesh.peers["agent-code-auditor-99"].global_trust >= 0.95

    def test_eigentrust_power_iteration_convergence(self, clean_mesh):
        mesh = clean_mesh
        # Run convergence
        scores = mesh.compute_eigentrust(alpha=0.85, max_iterations=30)
        assert len(scores) == len(mesh.peers)
        total_score = sum(scores.values())
        assert pytest.approx(total_score, 0.05) == 1.0 or total_score > 0.9

    def test_broadcast_rating_valid(self, clean_mesh):
        mesh = clean_mesh
        ok, msg, gossip = mesh.broadcast_rating(
            rater_agent_id="agent-code-auditor-99",
            target_agent_id="agent-cloudscale-worker-12",
            score=0.99,
            task_contract_id="SLA-TASK-9921"
        )
        assert ok is True
        assert gossip is not None
        assert gossip.score == 0.99
        assert gossip.signature != ""
        assert mesh.peers["agent-code-auditor-99"].vector_clock > 0

    def test_gossip_signature_tampering_detection(self, clean_mesh):
        mesh = clean_mesh
        ok, _, gossip = mesh.broadcast_rating(
            rater_agent_id="agent-code-auditor-99",
            target_agent_id="agent-cloudscale-worker-12",
            score=0.95,
            task_contract_id="SLA-TASK-1234"
        )
        assert ok is True
        # Tamper with the score
        tampered = ReputationGossipMessage(
            message_id=gossip.message_id,
            rater_agent_id=gossip.rater_agent_id,
            target_agent_id=gossip.target_agent_id,
            score=0.10,  # tampered
            task_contract_id=gossip.task_contract_id,
            epoch=gossip.epoch,
            timestamp=gossip.timestamp,
            signature=gossip.signature
        )
        assert tampered.verify() is False

    def test_sybil_collusion_damping(self, clean_mesh):
        mesh = clean_mesh
        # Add 3 sybil nodes rating each other 1.0
        sybils = ["sybil-node-A", "sybil-node-B", "sybil-node-C"]
        for s in sybils:
            mesh.register_peer(node_id=s, address=f"p2p://{s}:9999", is_pretrusted=False)

        # Sybils vote for each other
        mesh.broadcast_rating("sybil-node-A", "sybil-node-B", 1.0, "FAKE-SLA-1")
        mesh.broadcast_rating("sybil-node-B", "sybil-node-C", 1.0, "FAKE-SLA-2")
        mesh.broadcast_rating("sybil-node-C", "sybil-node-A", 1.0, "FAKE-SLA-3")

        # Re-evaluate global trust
        mesh.compute_eigentrust(alpha=0.85)
        # Pretrusted nodes should have significantly higher trust than sybils
        pretrusted_trust = mesh.peers["agent-code-auditor-99"].global_trust
        sybil_trust = mesh.peers["sybil-node-A"].global_trust
        assert pretrusted_trust > sybil_trust * 2

    def test_fast_path_slashing_propagation(self, clean_mesh):
        mesh = clean_mesh
        target = "agent-cloudscale-worker-12"
        initial_trust = mesh.peers[target].global_trust

        # Fast-path slash broadcast
        mesh.broadcast_slashing_penalty(target_agent_id=target, penalty_ratio=0.80)
        assert mesh.peers[target].global_trust < initial_trust * 0.5


class TestCrossChainBridgeRelay:
    def test_lock_source_escrow_success(self, clean_bridge):
        bridge = clean_bridge
        ok, msg, voucher = bridge.lock_source_escrow(
            source_chain="EVM_BASE",
            target_chain="L402_LIGHTNING",
            depositor="0xAliceBaseWallet",
            recipient="bob@btp.lightning.node",
            amount_usd=150.0
        )
        assert ok is True
        assert voucher.status == "LOCKED"
        assert voucher.amount_usd == 150.0
        assert voucher.source_chain == "EVM_BASE"
        assert voucher.target_chain == "L402_LIGHTNING"
        assert voucher.lock_hash != ""
        assert voucher.preimage is not None

    def test_claim_target_escrow_correct_preimage(self, clean_bridge):
        bridge = clean_bridge
        ok, _, voucher = bridge.lock_source_escrow(
            source_chain="EVM_ARBITRUM",
            target_chain="EVM_BASE",
            depositor="0xSenderArb",
            recipient="0xRecipientBase",
            amount_usd=500.0
        )
        assert ok is True

        # Claim using correct preimage
        claim_ok, claim_msg, claimed_voucher = bridge.claim_target_escrow(
            voucher_id=voucher.voucher_id,
            secret_preimage=voucher.preimage
        )
        assert claim_ok is True
        assert claimed_voucher.status == "CLAIMED"
        assert claimed_voucher.claimed_at is not None

    def test_claim_target_escrow_invalid_preimage(self, clean_bridge):
        bridge = clean_bridge
        ok, _, voucher = bridge.lock_source_escrow(
            source_chain="EVM_BASE",
            target_chain="EVM_ARBITRUM",
            depositor="0xAlice",
            recipient="0xBob",
            amount_usd=75.0
        )
        assert ok is True

        claim_ok, claim_msg, _ = bridge.claim_target_escrow(
            voucher_id=voucher.voucher_id,
            secret_preimage="wrong_secret_preimage_xyz"
        )
        assert claim_ok is False
        assert "Invalid secret preimage" in claim_msg

    def test_double_claim_prevention(self, clean_bridge):
        bridge = clean_bridge
        ok, _, voucher = bridge.lock_source_escrow(
            source_chain="L402_LIGHTNING",
            target_chain="EVM_BASE",
            depositor="alice@ln",
            recipient="0xBobBase",
            amount_usd=200.0
        )
        assert ok is True

        # First claim succeeds
        ok1, _, _ = bridge.claim_target_escrow(voucher.voucher_id, voucher.preimage)
        assert ok1 is True

        # Second claim fails
        ok2, msg2, _ = bridge.claim_target_escrow(voucher.voucher_id, voucher.preimage)
        assert ok2 is False
        assert "already" in msg2.lower()

    def test_refund_expired_voucher(self, clean_bridge):
        bridge = clean_bridge
        ok, _, voucher = bridge.lock_source_escrow(
            source_chain="EVM_BASE",
            target_chain="L402_LIGHTNING",
            depositor="0xRefundUser",
            recipient="charlie@ln",
            amount_usd=100.0,
            ttl_seconds=-10  # simulate pre-expired timelock
        )
        assert ok is True

        refund_ok, refund_msg, refunded_voucher = bridge.refund_expired_voucher(voucher.voucher_id)
        assert refund_ok is True
        assert refunded_voucher.status == "REFUNDED"


class TestV54CLIIntegration:
    def test_cli_gossip_peer_list(self, capsys):
        from cli import cmd_gossip_peer_list
        from unittest.mock import MagicMock

        args = MagicMock()
        cmd_gossip_peer_list(args)
        out = capsys.readouterr().out
        assert "DECENTRALIZED P2P PEER REPUTATION MESH" in out
        assert "agent-code-auditor-99" in out

    def test_cli_gossip_rate(self, capsys):
        from cli import cmd_gossip_rate
        from unittest.mock import MagicMock

        args = MagicMock()
        args.rater = "agent-code-auditor-99"
        args.target = "agent-liquidity-arbiter-07"
        args.score = 0.96
        args.contract_id = "SLA-CLI-TEST-1"
        cmd_gossip_rate(args)
        out = capsys.readouterr().out
        assert "P2P REPUTATION GOSSIP BROADCAST" in out
        assert "Gossip ID" in out
        assert "96.0%" in out

    def test_cli_bridge_transfer_and_claim(self, capsys):
        from cli import cmd_bridge_transfer, cmd_bridge_claim
        from unittest.mock import MagicMock

        # 1. Transfer Lock
        lock_args = MagicMock()
        lock_args.source = "EVM_BASE"
        lock_args.target = "L402_LIGHTNING"
        lock_args.depositor = "0xAliceCLITest"
        lock_args.recipient = "bob@lightning.local"
        lock_args.amount = 42.50

        cmd_bridge_transfer(lock_args)
        out1 = capsys.readouterr().out
        assert "ATOMIC CROSS-CHAIN ESCROW BRIDGE: LOCK" in out1
        assert "VOUCHER-" in out1

        # Extract voucher ID and preimage from stdout
        voucher_id = None
        preimage = None
        for line in out1.splitlines():
            if "Voucher ID" in line:
                voucher_id = line.split(":")[-1].strip()
            if "Preimage Key" in line:
                preimage = line.split(":")[-1].strip()

        assert voucher_id is not None
        assert preimage is not None

        # 2. Claim
        claim_args = MagicMock()
        claim_args.voucher = voucher_id
        claim_args.preimage = preimage

        cmd_bridge_claim(claim_args)
        out2 = capsys.readouterr().out
        assert "ATOMIC CROSS-CHAIN ESCROW BRIDGE: CLAIM" in out2
        assert "CLAIMED" in out2

