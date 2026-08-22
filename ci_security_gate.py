"""
Bartholomew CI/CD Multi-Runtime Automated Security Gate
======================================================
Executes end-to-end multi-language test suite and policy validation:
  1. Declarative policy validation (YAML/JSON).
  2. Law of Diminishing Marginal Utility (LDMU) Loop Fatigue checks.
  3. Merkle Audit Tree & SOC 2 Inclusion Proof checks.
  4. Claude & Cursor MCP Server handshake.
  5. Hermetic Sandbox & Path Traversal containment.
  6. 1-Line Drop-In Client Wrapper (OpenAI & Anthropic).
"""

import sys
import os
import subprocess
import time

def run_gate():
    print("=" * 80)
    print("RUNNING BARTHOLOMEW CORE CI/CD SECURITY & INVARIANT GATE (BTP v2.2.0)")
    print("=" * 80 + "\n")

    steps = [
        ("1. Validate Declarative Security Policy", ["python", "cli.py", "policy", "validate"]),
        ("2. Test Law of Diminishing Marginal Utility (LDMU) Engine", ["python", "-m", "pytest", "tests/test_marginal_utility_engine.py"]),
        ("3. Test Merkle Audit Tree & SOC 2 Inclusion Proofs", ["python", "tests/test_audit_merkle_tree.py"]),
        ("4. Test Claude Desktop & Cursor MCP Guard Server", ["python", "-m", "pytest", "tests/test_mcp_guard.py"]),
        ("5. Test Hermetic Command & File Containment Sandbox", ["python", "test_hermetic_command_sandbox.py"]),
        ("6. Test 1-Line Drop-In Client Wrapper", ["python", "test_client_wrapper.py"]),
        ("7. Test Enterprise Fleet Telemetry & OpenTelemetry Exporter", ["python", "-m", "pytest", "tests/test_fleet_telemetry.py"]),
        ("8. Test Native Invariant Micro-Engine & Sub-5µs Latency", ["python", "-m", "pytest", "tests/test_native_core.py"]),
        ("9. Test Autonomous Policy Synthesizer", ["python", "-m", "pytest", "tests/test_policy_synthesizer.py"]),
        ("10. Test LangChain Guardrails", ["python", "test_langchain_guard.py"]),
        ("11. Test Information Theory & Epistemic Grounding Engine", ["python", "tests/test_entropy_grounding_engine.py"]),
        ("12. Test Epistemic & Physical Invariant Engine", ["python", "tests/test_epistemic_physics_engine.py"]),
        ("13. Test Advanced Cosmology, PCP & Neuro-Epistemic Engine", ["python", "tests/test_advanced_cosmology_neuro_engine.py"]),
        ("14. Test Unified Classical & Physical Invariant Engine", ["python", "tests/test_unified_physics_invariant_engine.py"]),
        ("15. Test Hawking Information Preservation & Deterministic Gate", ["python", "tests/test_hawking_information_preservation.py"]),
        ("16. Test Compliance & SOC 2 Audit Report Generator", ["python", "tests/test_compliance_report_generator.py"]),
    ]

    all_passed = True

    for item in steps:
        name = item[0]
        cmd = item[1]
        cwd = item[2] if len(item) > 2 else "."

        print(f"[*] Running: {name}...")
        res = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
        if res.returncode == 0:
            print(f"    [PASSED] {name}")
        else:
            print(f"    [FAILED] {name}\n    Error: {res.stderr or res.stdout}")
            all_passed = False

    print("\n" + "=" * 80)
    if all_passed:
        print("CORE CI/CD GATE STATUS: 100% ALL RUNTIMES PASSED CLEAN")
    else:
        print("CORE CI/CD GATE STATUS: FAILURES DETECTED")
    print("=" * 80)

    if not all_passed:
        sys.exit(1)

if __name__ == "__main__":
    run_gate()
