import unittest
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.byzantine_swarm_consensus import ByzantineSwarmEngine, SwarmProposal, SwarmQuorumCertificate

class TestByzantineSwarmConsensus(unittest.TestCase):
    def setUp(self):
        # 4 validators -> n=4, f=1, required_quorum = 2f + 1 = 3
        self.validators = ["agent-alpha", "agent-beta", "agent-gamma", "agent-delta"]
        self.swarm = ByzantineSwarmEngine(self.validators)
        self.proposal_id = "prop-db-schema-migration-001"

    def test_bft_threshold_calculation(self):
        self.assertEqual(self.swarm.n, 4)
        self.assertEqual(self.swarm.f, 1)
        self.assertEqual(self.swarm.required_quorum, 3)

    def test_successful_quorum_consensus(self):
        # 1. Propose action
        ok, err = self.swarm.submit_proposal(
            proposal_id=self.proposal_id,
            proposer_agent_id="agent-alpha",
            action_type="DB_SCHEMA_MIGRATION",
            action_payload={"table": "users", "operation": "ADD_COLUMN", "col": "status"}
        )
        self.assertTrue(ok)
        self.assertIsNone(err)

        # 2. 3 agents vote APPROVE (meets quorum 3)
        self.swarm.cast_vote(self.proposal_id, "agent-alpha", "APPROVE")
        self.swarm.cast_vote(self.proposal_id, "agent-beta", "APPROVE")

        # 2 votes: not yet quorum
        reached, cert, msg = self.swarm.evaluate_consensus(self.proposal_id)
        self.assertFalse(reached)
        self.assertIsNone(cert)
        self.assertIn("PENDING_QUORUM", msg)

        # 3rd vote arrives
        self.swarm.cast_vote(self.proposal_id, "agent-gamma", "APPROVE")

        reached, cert, msg = self.swarm.evaluate_consensus(self.proposal_id)
        self.assertTrue(reached)
        self.assertIsNotNone(cert)
        self.assertIn("BFT_QUORUM_REACHED", msg)
        self.assertEqual(cert.votes_received, 3)
        self.assertEqual(len(cert.certificate_sha256), 64)

    def test_byzantine_fault_tolerance(self):
        # Even with 1 malicious/Byzantine node rejecting, 3 honest nodes reach consensus
        self.swarm.submit_proposal(
            proposal_id="prop-002",
            proposer_agent_id="agent-alpha",
            action_type="HIGH_VALUE_TRANSFER",
            action_payload={"amount_usd": 50000}
        )

        # 1 Byzantine vote (rejecting or corrupted)
        self.swarm.cast_vote("prop-002", "agent-delta", "REJECT", reason="byzantine corruption")

        # 3 Honest votes
        self.swarm.cast_vote("prop-002", "agent-alpha", "APPROVE")
        self.swarm.cast_vote("prop-002", "agent-beta", "APPROVE")
        self.swarm.cast_vote("prop-002", "agent-gamma", "APPROVE")

        reached, cert, msg = self.swarm.evaluate_consensus("prop-002")
        self.assertTrue(reached)
        self.assertIsNotNone(cert)
        self.assertEqual(cert.votes_received, 3)

    def test_unauthorized_proposer_rejected(self):
        ok, err = self.swarm.submit_proposal(
            proposal_id="prop-unauthorized",
            proposer_agent_id="unknown-rogue-agent",
            action_type="IAM_ELEVATION",
            action_payload={}
        )
        self.assertFalse(ok)
        self.assertIn("BTP-SWARM-001", err)

    def test_duplicate_vote_rejected(self):
        self.swarm.submit_proposal(
            proposal_id="prop-003",
            proposer_agent_id="agent-alpha",
            action_type="CONFIG_RELOAD",
            action_payload={}
        )
        ok1, err1 = self.swarm.cast_vote("prop-003", "agent-alpha", "APPROVE")
        self.assertTrue(ok1)

        ok2, err2 = self.swarm.cast_vote("prop-003", "agent-alpha", "APPROVE")
        self.assertFalse(ok2)
        self.assertIn("BTP-SWARM-005", err2)

    def test_swarm_veto(self):
        self.swarm.submit_proposal(
            proposal_id="prop-veto",
            proposer_agent_id="agent-alpha",
            action_type="DROP_DATABASE",
            action_payload={}
        )
        # 2 rejections (> f=1): consensus is mathematically impossible
        self.swarm.cast_vote("prop-veto", "agent-beta", "REJECT", reason="Destructive query detected")
        self.swarm.cast_vote("prop-veto", "agent-gamma", "REJECT", reason="Protected schema invariant")

        reached, cert, msg = self.swarm.evaluate_consensus("prop-veto")
        self.assertFalse(reached)
        self.assertIsNone(cert)
        self.assertIn("BFT_QUORUM_VETOED", msg)

if __name__ == "__main__":
    unittest.main()
