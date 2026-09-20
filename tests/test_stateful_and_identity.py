"""
Unit tests for Stateful Multi-Turn Session Guard & Non-Human Identity Governance (BTP v2.5.0)
"""

import unittest
from src.stateful_session_guard import StatefulSessionSecurityManager
from src.agent_identity_governance import AgentIdentityGovernanceRegistry

class TestStatefulAndIdentityGovernance(unittest.TestCase):

    def setUp(self):
        self.session_mgr = StatefulSessionSecurityManager()
        self.registry = AgentIdentityGovernanceRegistry()

    def test_single_turn_safe_allowed(self):
        allowed, reason, dt_us = self.session_mgr.evaluate_turn(
            session_id="session-001",
            action_type="DATA_QUERY",
            payload={"sql": "SELECT id, balance FROM accounts LIMIT 10;"},
            raw_code="cursor.execute('SELECT id, balance FROM accounts LIMIT 10;')"
        )
        self.assertTrue(allowed)
        self.assertLess(dt_us, 500.0)

    def test_multi_turn_split_payload_intercepted(self):
        session_id = "session-malicious-split"

        # Turn 1: Define first half of payload
        t1_ok, _, _ = self.session_mgr.evaluate_turn(
            session_id=session_id,
            action_type="VARIABLE_SET",
            payload={},
            raw_code='prefix = "rm -"'
        )
        self.assertTrue(t1_ok)

        # Turn 2: Define second half of payload
        t2_ok, _, _ = self.session_mgr.evaluate_turn(
            session_id=session_id,
            action_type="VARIABLE_SET",
            payload={},
            raw_code='target = "rf /"'
        )
        self.assertTrue(t2_ok)

        # Turn 3: Attempt execution using variables
        t3_ok, reason, _ = self.session_mgr.evaluate_turn(
            session_id=session_id,
            action_type="SHELL_EXEC",
            payload={},
            raw_code='import os; os.system(prefix + target)'
        )
        self.assertFalse(t3_ok, "Must intercept split payload stitched across turns")
        self.assertIn("BTP-STATEFUL-002", reason)

    def test_agent_rbac_and_auto_revocation(self):
        # Register an Analyst agent
        analyst = self.registry.register_identity(
            agent_id="analyst-bot-01",
            role="ANALYST",
            max_spend_hourly_usd=50.0
        )

        # 1. Allowed capability
        auth_ok, msg = self.registry.verify_action_authorization(
            agent_id="analyst-bot-01",
            required_capability="data:read",
            amount_usd=10.0
        )
        self.assertTrue(auth_ok)

        # 2. Denied capability (Analyst cannot mutate code)
        unauth_ok, unauth_msg = self.registry.verify_action_authorization(
            agent_id="analyst-bot-01",
            required_capability="code:mutate"
        )
        self.assertFalse(unauth_ok)
        self.assertIn("BTP-NHI-004", unauth_msg)

        # 3. Record violations and verify automatic revocation
        cert1 = self.registry.record_violation("analyst-bot-01", "Attempted unapproved code mutation")
        self.assertIsNone(cert1)  # 1st violation does not revoke

        cert2 = self.registry.record_violation("analyst-bot-01", "Second unapproved attempt")
        self.assertIsNotNone(cert2)  # 2nd violation revokes
        self.assertTrue(analyst.is_revoked)
        self.assertIn("authority_signature", cert2)

        # 4. Subsequent calls rejected due to revocation
        revoked_ok, revoked_msg = self.registry.verify_action_authorization(
            agent_id="analyst-bot-01",
            required_capability="data:read"
        )
        self.assertFalse(revoked_ok)
        self.assertIn("BTP-NHI-002", revoked_msg)

if __name__ == "__main__":
    unittest.main()
