"""
Unit Test Suite for Bartholomew Bayesian Engine, Adaptive Text Handler, & Latency Solvers
================================================================---------------------------
Tests mathematical correctness, Bayesian posterior updating, small/large text handling,
Shannon entropy computation, DFA pattern matching, and Little's Law queueing metrics.
"""

import sys
import unittest
from pathlib import Path

# Ensure repo root is on sys.path
root_dir = Path(__file__).resolve().parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from pypi_package.bartholomew_eval.bayesian_engine import BayesianRiskEngine
from pypi_package.bartholomew_eval.text_handler import AdaptiveTextHandler, SmallTextScanner, LargeTextScanner
from pypi_package.bartholomew_eval.latency_solver import LatencySolver, DFAPatternMatcher, LocklessRingBuffer, ThroughputGovernor
from pypi_package.bartholomew_eval.internal_engine_calculator import InternalEngineCalculator
from pypi_package.bartholomew_eval.engine import BartholomewEngine

class TestBayesianAndTextEngine(unittest.TestCase):

    def test_bayesian_prior_and_posterior(self):
        engine = BayesianRiskEngine()
        prior_prod = engine.compute_prior("prod", 0.0)
        self.assertEqual(prior_prod, 0.02)

        prior_dev = engine.compute_prior("dev", 0.10)
        self.assertAlmostEqual(prior_dev, 0.10, places=2)

        # Test posterior calculation with high-risk features
        features = {
            "has_credential_pattern": True,
            "has_prompt_injection": True,
            "high_shannon_entropy": True,
        }
        res = engine.evaluate_trajectory_risk(features, environment="prod")
        self.assertGreaterEqual(res["posterior_threat_prob"], 0.90)
        self.assertEqual(res["security_action"], "CIRCUIT_BREAK")
        self.assertEqual(res["severity"], "CRITICAL")

    def test_epistemic_node_confidence_updating(self):
        engine = BayesianRiskEngine()
        conf_verified = engine.update_epistemic_node_confidence("VERIFIED", prior_confidence=0.80)
        self.assertAlmostEqual(conf_verified, 0.89, places=2)

        conf_disproven = engine.update_epistemic_node_confidence("DISPROVEN", prior_confidence=0.80, evidence_disproven=True)
        self.assertEqual(conf_disproven, 0.0)

    def test_shannon_entropy_calculation(self):
        entropy_low = AdaptiveTextHandler.calculate_shannon_entropy("aaaaaaaaaaaa")
        self.assertEqual(entropy_low, 0.0)

        entropy_high = AdaptiveTextHandler.calculate_shannon_entropy("sk-proj-xK9mN2pQ7rT4vY8wA3bC6dE9fG2hJ5")
        self.assertGreater(entropy_high, 4.0)

    def test_adaptive_text_routing(self):
        handler = AdaptiveTextHandler()
        
        # Small text payload (< 2 KB)
        small_text = "Authenticating agent with sk-proj-99887766554433221100"
        res_small = handler.analyze(small_text)
        self.assertEqual(res_small["scanner_mode"], "SmallTextScanner (Trie)")
        self.assertTrue(res_small["has_threat"])
        self.assertLess(res_small["latency_us"], 100.0) # Sub-microsecond / Fast

        # Large text payload (> 2 KB)
        large_text = ("System prompt context document. " * 150) + "sk-proj-99887766554433221100"
        res_large = handler.analyze(large_text)
        self.assertEqual(res_large["scanner_mode"], "LargeTextScanner (Sliding-Window)")
        self.assertTrue(res_large["has_threat"])

    def test_latency_solver_and_ring_buffer(self):
        solver = LatencySolver()
        res = solver.solve_scan("Executing SELECT * FROM users")
        self.assertIn("matched_patterns", res)
        self.assertTrue(res["sla_compliant"])

        # Test LocklessRingBuffer
        rb = LocklessRingBuffer(capacity=3)
        rb.push("item1")
        rb.push("item2")
        rb.push("item3")
        rb.push("item4") # overwrites oldest
        self.assertEqual(rb.pop(), "item2")

    def test_internal_engine_calculator(self):
        calc = InternalEngineCalculator()
        assessment = calc.evaluate_system_assessment(
            predictions=[0.9, 0.8, 0.95],
            outcomes=[1, 1, 1],
            sample_payload_text="sk-proj-99887766554433221100"
        )
        self.assertIn("bayesian_posterior_risk", assessment)
        self.assertIn("shannon_entropy_bits", assessment)
        self.assertEqual(assessment["ownership_status"], "OWNED_OUTRIGHT_PROPRIETARY_IP")

    def test_bartholomew_engine_full_trajectory_scan(self):
        engine = BartholomewEngine()
        trajectory = {
            "agent_name": "TestBot",
            "steps": [
                {"step_index": 1, "type": "thought", "content": "Using key sk-proj-99887766554433221100"},
                {"step_index": 2, "type": "tool_call", "tool_name": "search_db", "content": "SELECT * FROM users"}
            ]
        }
        res = engine.evaluate_trajectory(trajectory)
        self.assertTrue(res["success"])
        self.assertIn("bayesian_risk_evaluation", res)
        self.assertIn("adaptive_text_analysis", res)
        self.assertIn("latency_solver_metrics", res)
        self.assertGreater(res["audit_summary"]["credential_leaks"], 0)

if __name__ == "__main__":
    unittest.main()
