import unittest
import os
import sys

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.ebpf_kernel_guard import EBPFKernelGuard, KernelSecurityPolicy, KernelSyscallEvent

class TestEBPFKernelGuard(unittest.TestCase):
    def setUp(self):
        self.policy = KernelSecurityPolicy()
        self.guard = EBPFKernelGuard(self.policy)
        self.test_pid = 4096
        self.guard.register_pid(self.test_pid)

    def test_pid_registration(self):
        self.assertIn(self.test_pid, self.guard.monitored_pids)
        self.guard.unregister_pid(self.test_pid)
        self.assertNotIn(self.test_pid, self.guard.monitored_pids)

    def test_execve_interception_blocked(self):
        event = self.guard.intercept_execve(self.test_pid, "/bin/rm")
        self.assertEqual(event.action, "BLOCK")
        self.assertEqual(event.syscall_nr, 59)
        self.assertIn("BTP-KERNEL-001", event.reason)

        event2 = self.guard.intercept_execve(self.test_pid, "sudo")
        self.assertEqual(event2.action, "BLOCK")

    def test_execve_interception_allowed(self):
        event = self.guard.intercept_execve(self.test_pid, "/usr/bin/python3")
        self.assertEqual(event.action, "ALLOW")
        self.assertIsNone(event.reason)

    def test_unlinkat_interception_blocked(self):
        event = self.guard.intercept_unlinkat(self.test_pid, "/etc/passwd")
        self.assertEqual(event.action, "BLOCK")
        self.assertEqual(event.syscall_nr, 263)
        self.assertIn("BTP-KERNEL-002", event.reason)

        event2 = self.guard.intercept_unlinkat(self.test_pid, "/home/user/.git/config")
        self.assertEqual(event2.action, "BLOCK")

    def test_unlinkat_interception_allowed(self):
        event = self.guard.intercept_unlinkat(self.test_pid, "/tmp/scratch_cache.json")
        self.assertEqual(event.action, "ALLOW")
        self.assertIsNone(event.reason)

    def test_kernel_audit_manifest(self):
        self.guard.intercept_execve(self.test_pid, "/bin/rm")
        self.guard.intercept_execve(self.test_pid, "python")
        self.guard.intercept_unlinkat(self.test_pid, "/etc/hosts")

        manifest = self.guard.generate_kernel_audit_manifest()
        self.assertEqual(manifest["events_intercepted"], 3)
        self.assertEqual(manifest["blocked_count"], 2)
        self.assertEqual(manifest["status"], "HEALTHY")
        self.assertEqual(len(manifest["manifest_sha256"]), 64)

if __name__ == "__main__":
    unittest.main()
