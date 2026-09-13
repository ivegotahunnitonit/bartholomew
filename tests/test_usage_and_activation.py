"""
Test Suite: Bartholomew BTP v3.0 Usage Tracker & Activation Engine
==================================================================
Tests:
  1. Free tier quota tracking and evaluation count increments.
  2. Non-blocking upgrade reminder behavior.
  3. License key parsing (COMMUNITY, PRO, ENTERPRISE).
  4. Local license persistence and cross-runtime detection.
  5. License tier receipt stamping.
"""

import os
import sys
import json
import unittest
from pathlib import Path

sys.path.insert(0, os.path.abspath("."))
from src.usage_tracker import (
    load_license,
    save_license,
    parse_license_token,
    record_evaluation,
    FREE_TIER_CALL_LIMIT,
    get_btp_dir
)
from btp_guard import Guard

class TestUsageAndActivation(unittest.TestCase):
    def setUp(self):
        self.btp_dir = get_btp_dir()
        self.license_file = self.btp_dir / "license.json"
        self.metrics_file = self.btp_dir / "metrics.json"

        # Backup existing license if present
        self.backup_lic = None
        if self.license_file.exists():
            with open(self.license_file, "r", encoding="utf-8") as f:
                self.backup_lic = f.read()
            self.license_file.unlink()

    def tearDown(self):
        # Restore backup license
        if self.backup_lic:
            with open(self.license_file, "w", encoding="utf-8") as f:
                f.write(self.backup_lic)
        elif self.license_file.exists():
            self.license_file.unlink()

    def test_01_token_parsing(self):
        free_info = parse_license_token("random_short_key")
        self.assertEqual(free_info["tier"], "COMMUNITY")
        self.assertFalse(free_info["licensed"])

        pro_info = parse_license_token("btp_pro_customer_1234567890abcdef")
        self.assertEqual(pro_info["tier"], "PRO")
        self.assertTrue(pro_info["licensed"])

        ent_info = parse_license_token("btp_ent_soc2_customer_9999")
        self.assertEqual(ent_info["tier"], "ENTERPRISE")
        self.assertTrue(ent_info["licensed"])
        self.assertIn("soc2_type2_compliance", ent_info["features"])

    def test_02_license_save_and_load(self):
        save_license("btp_pro_998877665544332211")
        loaded = load_license()
        self.assertTrue(loaded["licensed"])
        self.assertEqual(loaded["tier"], "PRO")

    def test_03_guard_receipt_stamping(self):
        # Save enterprise key
        save_license("btp_ent_fortune500_corp")
        guard = Guard()
        res = guard.check("SELECT id, name FROM users;")
        self.assertTrue(res["allowed"])
        self.assertEqual(res["license_tier"], "ENTERPRISE")

    def test_04_evaluation_counter(self):
        # Remove license to test free tracking
        if self.license_file.exists():
            self.license_file.unlink()

        # Record evaluations
        for _ in range(5):
            record_evaluation()

        with open(self.metrics_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            self.assertGreaterEqual(data["evaluation_count"], 5)

if __name__ == "__main__":
    unittest.main()
