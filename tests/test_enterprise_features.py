"""
Unit tests for Bartholomew Enterprise Features (BTP v2.5.0):
  - Dynamic Policy Sync (`src/dynamic_policy_sync.py`)
  - Asynchronous SIEM Exporter (`src/siem_exporter.py`)
  - Framework Integrations (`src/framework_integrations.py`)
"""

import unittest
import os
import shutil
import tempfile
from src.dynamic_policy_sync import compute_policy_hash, verify_policy_integrity, load_and_validate_policy
from src.siem_exporter import SIEMExporter
from src.framework_integrations import BartholomewLangChainTool, btp_crewai_tool, BartholomewAutoGenHook
from src.client_wrapper import BTPViolationError

class TestEnterpriseFeatures(unittest.TestCase):

    def test_canonical_hash_determinism(self):
        policy_a = {"version": "2.5.0", "spend_cap": 500.0, "rules": [{"id": "R1"}]}
        policy_b = {"rules": [{"id": "R1"}], "spend_cap": 500.0, "version": "2.5.0"}
        hash_a = compute_policy_hash(policy_a)
        hash_b = compute_policy_hash(policy_b)
        self.assertEqual(hash_a, hash_b, "Canonical hashes must be identical regardless of key order")

    def test_policy_integrity_check(self):
        valid_policy = {
            "version": "2.5.0",
            "rules": [
                {"id": "SPEND", "field": "amount_usd", "value": 250.0},
                {"id": "SQL", "field": "query", "operator": "not_contains", "values": ["drop table"]}
            ]
        }
        is_valid, issues = verify_policy_integrity(valid_policy)
        self.assertTrue(is_valid)

        invalid_policy = {
            "version": "2.5.0",
            "rules": [
                {"id": "SPEND", "field": "amount_usd", "value": -50.0},
                {"field": "missing_id"}
            ]
        }
        is_valid, issues = verify_policy_integrity(invalid_policy)
        self.assertFalse(is_valid)

    def test_siem_exporter_spooling(self):
        test_spool_dir = tempfile.mkdtemp(prefix="btp_siem_test_")
        try:
            exporter = SIEMExporter(spool_dir=test_spool_dir, batch_size=2, flush_interval_seconds=0.1)
            mock_receipt = {
                "attestation": {"verdict": "ALLOW", "reason": "Passed"},
                "signature": "ed25519:test_sig_123"
            }
            exporter.emit_receipt(mock_receipt)
            exporter.shutdown(timeout=1.0)
            
            spool_file = os.path.join(test_spool_dir, "siem_spool.jsonl")
            self.assertTrue(os.path.exists(spool_file))
            with open(spool_file, "r") as f:
                lines = f.readlines()
            self.assertEqual(len(lines), 1)
        finally:
            shutil.rmtree(test_spool_dir, ignore_errors=True)

    def test_langchain_tool_protection(self):
        def safe_tool(query: str):
            return f"Queried: {query}"

        guarded = BartholomewLangChainTool(safe_tool, name="safe_search", max_spend_usd=100.0)
        result = guarded.run(query="Python best practices")
        self.assertEqual(result, "Queried: Python best practices")

        # Test spend limit violation
        with self.assertRaises(BTPViolationError):
            guarded.run(query="Expensive operation", amount_usd=500.0)

    def test_crewai_tool_decorator(self):
        @btp_crewai_tool(max_spend_usd=200.0)
        def mock_crew_action(task: str, amount_usd: float = 0.0):
            return f"Completed: {task}"

        res = mock_crew_action("safe data processing", amount_usd=10.0)
        self.assertEqual(res, "Completed: safe data processing")

        with self.assertRaises(BTPViolationError):
            mock_crew_action("malicious spend", amount_usd=999.0)

    def test_autogen_hook(self):
        hook = BartholomewAutoGenHook()
        messages = [{"content": "Hello user, safe response."}]
        handled, reply = hook.filter_message(None, messages, None, None)
        self.assertFalse(handled)

if __name__ == "__main__":
    unittest.main()
