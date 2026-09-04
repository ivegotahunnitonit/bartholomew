import unittest
import os
import sys
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.confidential_enclave_attestation import (
    ConfidentialEnclaveAttestationEngine,
    EnclaveAttestationDocument,
    EnclaveMeasurements
)

class TestConfidentialEnclave(unittest.TestCase):
    def setUp(self):
        self.engine = ConfidentialEnclaveAttestationEngine()
        self.module_id = "enclave-worker-node-01"
        self.public_key_pem = "-----BEGIN PUBLIC KEY-----\nMCowBQYDK2VwAyEAXmockEd25519EnclaveKey000000000000000000000=\n-----END PUBLIC KEY-----"
        self.nonce = "fresh-session-anti-replay-nonce-99124"

    def test_valid_attestation_document(self):
        doc = self.engine.generate_attestation_document(
            module_id=self.module_id,
            public_key_pem=self.public_key_pem,
            nonce=self.nonce
        )
        self.assertTrue(doc.is_hardware_certified)
        self.assertEqual(doc.module_id, self.module_id)

        valid, error = self.engine.verify_attestation_document(doc, expected_nonce=self.nonce)
        self.assertTrue(valid)
        self.assertIsNone(error)

    def test_replay_attack_rejected(self):
        doc = self.engine.generate_attestation_document(
            module_id=self.module_id,
            public_key_pem=self.public_key_pem,
            nonce=self.nonce
        )
        stale_nonce = "replayed-stale-nonce-0000"
        valid, error = self.engine.verify_attestation_document(doc, expected_nonce=stale_nonce)
        self.assertFalse(valid)
        self.assertIn("BTP-ENCLAVE-001", error)

    def test_tampered_pcr0_kernel_rejected(self):
        doc = self.engine.generate_attestation_document(
            module_id=self.module_id,
            public_key_pem=self.public_key_pem,
            nonce=self.nonce,
            custom_pcr0="tampered_unverified_kernel_hash_00000000000000000000000000000000"
        )
        valid, error = self.engine.verify_attestation_document(doc, expected_nonce=self.nonce)
        self.assertFalse(valid)
        self.assertIn("BTP-ENCLAVE-003", error)

    def test_tampered_pcr1_policy_rejected(self):
        doc = self.engine.generate_attestation_document(
            module_id=self.module_id,
            public_key_pem=self.public_key_pem,
            nonce=self.nonce,
            custom_pcr1="tampered_unauthorized_policy_hash_00000000000000000000000000000000"
        )
        valid, error = self.engine.verify_attestation_document(doc, expected_nonce=self.nonce)
        self.assertFalse(valid)
        self.assertIn("BTP-ENCLAVE-004", error)

    def test_expired_attestation_rejected(self):
        doc = self.engine.generate_attestation_document(
            module_id=self.module_id,
            public_key_pem=self.public_key_pem,
            nonce=self.nonce
        )
        # Mock timestamp to 400 seconds ago
        doc.measurements.timestamp = time.time() - 400.0
        valid, error = self.engine.verify_attestation_document(doc, expected_nonce=self.nonce, max_age_seconds=60.0)
        self.assertFalse(valid)
        self.assertIn("BTP-ENCLAVE-002", error)

    def test_isolated_secret_storage_and_fingerprint(self):
        doc = self.engine.generate_attestation_document(
            module_id=self.module_id,
            public_key_pem=self.public_key_pem,
            nonce=self.nonce
        )
        raw_key = b"ENCLAVE_ISOLATED_PRIVATE_ED25519_KEY_BYTES_SECRET"
        stored = self.engine.store_isolated_secret(self.module_id, raw_key)
        self.assertTrue(stored)

        fp = self.engine.get_isolated_secret_fingerprint(self.module_id)
        self.assertIsNotNone(fp)
        self.assertEqual(len(fp), 64)

if __name__ == "__main__":
    unittest.main()
