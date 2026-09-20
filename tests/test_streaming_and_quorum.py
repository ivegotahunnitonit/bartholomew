"""
Unit tests for Streaming Output Guard, Quorum Approval Gate, and Token Budget Governor (BTP v2.5.0)
"""

import unittest
from src.streaming_tool_guard import StreamingSecretFilter, guard_sync_stream
from src.quorum_approval_gate import QuorumApprovalGate
from src.token_budget_governor import TokenBudgetGovernor

class TestStreamingAndQuorum(unittest.TestCase):

    def test_streaming_boundary_secret_scrubbing(self):
        """Tests that credentials split across consecutive stream chunks are cleanly redacted."""
        filter_engine = StreamingSecretFilter(window_overlap=20)
        
        # Split a GitHub PAT across chunk boundaries
        chunk_1 = "Incoming header: Authorization: Bearer ghp_"
        chunk_2 = "9384910283910293840192830192 and next steps"

        res_1 = filter_engine.filter_chunk(chunk_1)
        res_2 = filter_engine.filter_chunk(chunk_2)
        res_3 = filter_engine.flush()
        total_out = res_1 + res_2 + res_3

        self.assertNotIn("ghp_9384910283910293840192830192", total_out)
        self.assertIn("[REDACTED_SECRET: GITHUB_PAT]", total_out)
        self.assertGreater(filter_engine.total_redactions, 0)

    def test_sync_stream_generator_wrapper(self):
        def sample_generator():
            yield "Starting task... "
            yield "Connecting with AKIAIOSFODNN7EXAMPLE "
            yield "Task completed."

        stream = guard_sync_stream(sample_generator())
        accumulated = "".join(list(stream))
        self.assertNotIn("AKIAIOSFODNN7EXAMPLE", accumulated)
        self.assertIn("[REDACTED_SECRET: AWS_KEY]", accumulated)

    def test_quorum_approval_flow(self):
        gate = QuorumApprovalGate(high_risk_spend_threshold_usd=500.0)

        # 1. Standard low-risk action
        risk_low = gate.assess_risk("HTTP_GET", {"url": "https://api.example.com"})
        self.assertEqual(risk_low, "ALLOW")

        # 2. Elevated-risk action (high spend)
        risk_high = gate.assess_risk("PAYMENT_DISPATCH", {"amount_usd": 2500.0})
        self.assertEqual(risk_high, "REQUIRE_APPROVAL")

        # 3. Create pending approval request
        approvers = {"ed25519:pubkey_alice_123", "ed25519:pubkey_bob_456"}
        req = gate.create_approval_request(
            agent_id="finance_bot",
            action_type="PAYMENT_DISPATCH",
            payload={"amount_usd": 2500.0},
            required_signatures=2,
            authorized_approver_pubkeys=approvers
        )

        # 4. Submit first signature
        approved_1, msg_1, attestation_1 = gate.submit_approval_signature(
            req.request_id,
            "ed25519:pubkey_alice_123",
            "sig_alice_mock_991823"
        )
        self.assertFalse(approved_1)
        self.assertIsNone(attestation_1)
        self.assertEqual(req.status, "PENDING")

        # 5. Submit second signature (Quorum satisfied)
        approved_2, msg_2, attestation_2 = gate.submit_approval_signature(
            req.request_id,
            "ed25519:pubkey_bob_456",
            "sig_bob_mock_441290"
        )
        self.assertTrue(approved_2)
        self.assertIsNotNone(attestation_2)
        self.assertEqual(req.status, "APPROVED")
        self.assertIn("quorum_attestation", attestation_2)

    def test_token_budget_and_rpm_governor(self):
        governor = TokenBudgetGovernor(max_rpm=3, max_tokens_per_hour=1000)
        session_id = "test-session-governor"

        # First 3 requests succeed
        ok1, _ = governor.check_request(session_id, estimated_tokens=100)
        ok2, _ = governor.check_request(session_id, estimated_tokens=100)
        ok3, _ = governor.check_request(session_id, estimated_tokens=100)
        self.assertTrue(ok1 and ok2 and ok3)

        # 4th request exceeds RPM
        ok4, msg4 = governor.check_request(session_id, estimated_tokens=100)
        self.assertFalse(ok4)
        self.assertIn("BTP-RATE-001", msg4)

        # Test token budget cap
        dow_session = "dow-session"
        ok_init, _ = governor.check_request(dow_session, estimated_tokens=500)
        self.assertTrue(ok_init)

        # Exceed budget
        ok_over, msg_over = governor.check_request(dow_session, estimated_tokens=600)
        self.assertFalse(ok_over)
        self.assertIn("BTP-DOW-002", msg_over)

if __name__ == "__main__":
    unittest.main()
