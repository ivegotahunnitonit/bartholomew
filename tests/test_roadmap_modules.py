import unittest
import os
import shutil
from btp_guard.redteam import RedTeamScanner, REFERENCE_ATTACK_VECTORS
from src.kms_provider import KMSKeyDelegationManager, KMSProviderType
from btp_guard.policy_sync import PolicyDistributionManager, COMPLIANCE_PACKS

class TestRoadmapModules(unittest.TestCase):
    def test_redteam_scanner_eval(self):
        scanner = RedTeamScanner(concurrency=4)
        summary = scanner.run_suite(REFERENCE_ATTACK_VECTORS)
        
        self.assertEqual(summary["total_vectors"], len(REFERENCE_ATTACK_VECTORS))
        self.assertEqual(summary["defense_rate_pct"], 100.0)
        self.assertEqual(summary["failed"], 0)
        self.assertIn("LLM02:InsecureOutputHandling", summary["category_breakdown"])
        self.assertLess(summary["p50_latency_us"], 1000)

    def test_kms_key_delegation(self):
        manager = KMSKeyDelegationManager(provider=KMSProviderType.AWS_KMS, key_id="arn:aws:kms:us-east-1:123456789:key/btp-test")
        receipt = manager.get_delegation_receipt()
        
        self.assertIn("token", receipt)
        self.assertEqual(receipt["token"]["fips_compliance"], "FIPS_140_3_LEVEL_3")
        self.assertEqual(receipt["token"]["kms_provider"], "aws_kms")
        
        # Test fast leaf signing (<5us)
        dummy_leaf = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
        sig_data = manager.sign_merkle_leaf_fast(dummy_leaf)
        self.assertIn("signature", sig_data)
        self.assertEqual(sig_data["provider"], "aws_kms")

    def test_policy_sync_and_compliance_packs(self):
        test_dir = "test_policies_tmp"
        try:
            p_mgr = PolicyDistributionManager(policy_dir=test_dir)
            res = p_mgr.install_compliance_pack("soc2")
            self.assertEqual(res["status"], "INSTALLED")
            self.assertEqual(res["pack"], "soc2")
            
            # Verify file created
            self.assertTrue(os.path.exists(res["file"]))
            self.assertIn("urn:btp:compliance:soc2", p_mgr.active_policies)
        finally:
            if os.path.exists(test_dir):
                shutil.rmtree(test_dir, ignore_errors=True)

if __name__ == "__main__":
    unittest.main()
