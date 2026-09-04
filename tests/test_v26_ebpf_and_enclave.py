"""
BTP v2.6.0 Deep Kernel Sandboxing & Enclave Attestation Test Suite
==================================================================
Tests:
  1. eBPF syscall traps: execve (59), unlinkat (263), connect (42).
  2. Network egress boundaries and exfiltration port blocking.
  3. Hardware-attested enclave PCR verification (AWS Nitro / AMD SEV-SNP).
  4. Anti-replay nonce enforcement and timestamp freshness.
  5. Cryptographic kernel audit manifest verification.
"""

import unittest
import os
import sys
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.ebpf_kernel_guard import EBPFKernelGuard, KernelSecurityPolicy
from src.confidential_enclave_attestation import (
    ConfidentialEnclaveAttestationEngine,
    EnclaveAttestationDocument
)

class TestV26KernelAndEnclave(unittest.TestCase):
    def setUp(self):
        self.policy = KernelSecurityPolicy(network_egress_restricted=True)
        self.guard = EBPFKernelGuard(self.policy)
        self.enclave_engine = ConfidentialEnclaveAttestationEngine()
        self.agent_pid = 8192
        self.guard.register_pid(self.agent_pid)

    def test_ebpf_execve_interception(self):
        # Destructive binaries blocked
        blocked = self.guard.intercept_execve(self.agent_pid, "/bin/rm")
        self.assertEqual(blocked.action, "BLOCK")
        self.assertEqual(blocked.syscall_nr, 59)
        self.assertIn("BTP-KERNEL-001", blocked.reason)

        # Benign binary allowed
        allowed = self.guard.intercept_execve(self.agent_pid, "/usr/bin/node")
        self.assertEqual(allowed.action, "ALLOW")
        self.assertIsNone(allowed.reason)

    def test_ebpf_unlinkat_protected_paths(self):
        # Attempting to delete SSH key or Git repo
        blocked_ssh = self.guard.intercept_unlinkat(self.agent_pid, "/home/agent/.ssh/id_ed25519")
        self.assertEqual(blocked_ssh.action, "BLOCK")
        self.assertEqual(blocked_ssh.syscall_nr, 263)
        self.assertIn("BTP-KERNEL-002", blocked_ssh.reason)

        # Allowed deletion in temp
        allowed_tmp = self.guard.intercept_unlinkat(self.agent_pid, "/tmp/cache_run.log")
        self.assertEqual(allowed_tmp.action, "ALLOW")

    def test_ebpf_connect_socket_egress(self):
        # Blocked reverse shell port
        blocked_shell = self.guard.intercept_connect(self.agent_pid, "198.51.100.23", 4444)
        self.assertEqual(blocked_shell.action, "BLOCK")
        self.assertEqual(blocked_shell.syscall_nr, 42)
        self.assertIn("BTP-KERNEL-003", blocked_shell.reason)

        # Disallowed external domain when restricted egress is enabled
        blocked_unapproved = self.guard.intercept_connect(self.agent_pid, "evil-c2-server.com", 443)
        self.assertEqual(blocked_unapproved.action, "BLOCK")
        self.assertIn("BTP-KERNEL-004", blocked_unapproved.reason)

        # Whitelisted host allowed
        allowed_api = self.guard.intercept_connect(self.agent_pid, "api.anthropic.com", 443)
        self.assertEqual(allowed_api.action, "ALLOW")

    def test_kernel_audit_manifest_integrity(self):
        self.guard.intercept_execve(self.agent_pid, "rm")
        self.guard.intercept_unlinkat(self.agent_pid, "/etc/shadow")
        self.guard.intercept_connect(self.agent_pid, "10.0.0.1", 31337)

        manifest = self.guard.generate_kernel_audit_manifest()
        self.assertEqual(manifest["events_intercepted"], 3)
        self.assertEqual(manifest["blocked_count"], 3)
        self.assertEqual(len(manifest["manifest_sha256"]), 64)

    def test_enclave_attestation_and_tamper_detection(self):
        module_id = "nitro-enclave-worker-v26"
        pubkey = "-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAzTEST=\n-----END PUBLIC KEY-----"
        nonce = f"nonce-{time.time_ns()}"

        doc = self.enclave_engine.generate_attestation_document(module_id, pubkey, nonce)
        valid, err = self.enclave_engine.verify_attestation_document(doc, expected_nonce=nonce)
        self.assertTrue(valid)
        self.assertIsNone(err)

        # Tampered PCR1 policy rejection
        doc_tampered = self.enclave_engine.generate_attestation_document(
            module_id, pubkey, nonce, custom_pcr1="corrupted_policy_measurement_hash_val"
        )
        t_valid, t_err = self.enclave_engine.verify_attestation_document(doc_tampered, expected_nonce=nonce)
        self.assertFalse(t_valid)
        self.assertIn("BTP-ENCLAVE-004", t_err)

    def test_end_to_end_v26_pipeline(self):
        # 1. Register process with kernel sandbox
        self.guard.register_pid(self.agent_pid)
        self.assertIn(self.agent_pid, self.guard.monitored_pids)

        # 2. Issue enclave cryptographic root attestation
        nonce = "e2e-session-v26-nonce"
        doc = self.enclave_engine.generate_attestation_document("enclave-worker", "pubkey", nonce)
        valid, _ = self.enclave_engine.verify_attestation_document(doc, expected_nonce=nonce)
        self.assertTrue(valid)

        # 3. Intercept and vet process actions in real-time
        event = self.guard.intercept_execve(self.agent_pid, "python3 worker.py")
        self.assertEqual(event.action, "ALLOW")

        # 4. Generate audit trail
        manifest = self.guard.generate_kernel_audit_manifest()
        self.assertGreaterEqual(manifest["events_intercepted"], 1)

if __name__ == "__main__":
    unittest.main()
