import unittest
import os
import sys
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.dynamic_memory_governor import DynamicMemoryGovernor

class TestDynamicMemoryGovernor(unittest.TestCase):
    def setUp(self):
        # 100 MB soft limit, 200 MB hard limit, 50 MB/s max velocity
        self.governor = DynamicMemoryGovernor(
            soft_limit_mb=100.0,
            hard_limit_mb=200.0,
            max_velocity_mb_s=50.0
        )
        self.session_id = "agent-session-memory-test-01"
        self.governor.register_session(self.session_id, baseline_bytes=10 * 1024 * 1024)

    def test_normal_allocation(self):
        allowed, status, reason = self.governor.record_allocation(
            self.session_id,
            new_rss_bytes=50 * 1024 * 1024
        )
        self.assertTrue(allowed)
        self.assertEqual(status, "NORMAL")
        self.assertIsNone(reason)

    def test_soft_limit_throttling(self):
        allowed, status, reason = self.governor.record_allocation(
            self.session_id,
            new_rss_bytes=120 * 1024 * 1024  # > 100 MB soft limit
        )
        self.assertTrue(allowed)
        self.assertEqual(status, "THROTTLED")
        self.assertIn("BTP-DOM-003", reason)

    def test_hard_limit_termination(self):
        allowed, status, reason = self.governor.record_allocation(
            self.session_id,
            new_rss_bytes=250 * 1024 * 1024  # > 200 MB hard limit
        )
        self.assertFalse(allowed)
        self.assertEqual(status, "TERMINATED")
        self.assertIn("BTP-DOM-001", reason)

    def test_velocity_explosion_detection(self):
        # Simulate explosive growth: 0MB to 60MB in 0.01 seconds (> 50 MB/s)
        session = self.governor.sessions[self.session_id]
        session.current_rss_bytes = 10 * 1024 * 1024
        session.last_check_timestamp = time.time() - 0.05  # 50ms ago
        new_bytes = 80 * 1024 * 1024  # +70MB in 50ms = 1400 MB/s velocity

        allowed, status, reason = self.governor.record_allocation(
            self.session_id,
            new_rss_bytes=new_bytes
        )
        self.assertFalse(allowed)
        self.assertEqual(status, "TERMINATED")
        self.assertIn("BTP-DOM-002", reason)

    def test_audit_summary(self):
        self.governor.record_allocation(self.session_id, 50 * 1024 * 1024)
        self.governor.record_allocation(self.session_id, 250 * 1024 * 1024)

        summary = self.governor.get_audit_summary()
        self.assertEqual(summary["active_sessions"], 1)
        self.assertEqual(summary["total_violations"], 1)
        self.assertEqual(summary["status"], "HEALTHY")
        self.assertEqual(len(summary["audit_digest_sha256"]), 64)

if __name__ == "__main__":
    unittest.main()
