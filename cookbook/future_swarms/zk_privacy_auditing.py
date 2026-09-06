"""
Cookbook Recipe: Zero-Knowledge Privacy-Preserving Compliance Auditing
======================================================================
Demonstrates generating cryptographic ZK proofs that an agent session
obeyed BTP policy constraints without revealing proprietary tool calls or prompts.

Algorithm:
    Pedersen Commitment + Fiat-Shamir Heuristic (RFC 3526 MODP Group 14)

Run:
    python cookbook/future_swarms/zk_privacy_auditing.py
"""

import sys
import os

# Add repository root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from src.zk_compliance_proof_engine import ZKComplianceEngine, ZKComplianceProof


def main():
    print("=" * 75)
    print("  BTP Global Cookbook: Zero-Knowledge Compliance Auditing Demo")
    print("=" * 75)

    engine = ZKComplianceEngine(policy_id="BTP-STANDARD-FINANCIAL-3.0")

    # 1. Simulate sensitive session containing proprietary customer data
    session_id = "agent-session-enterprise-998"
    sensitive_tool_calls = [
        "query_customer_ssn_encrypted --id 4981",
        "calculate_credit_score --mode strict",
        "export_sanitized_summary --dest /tmp/report.pdf"
    ]

    print(f"\n--- [1] Generating ZK Proof for Session: {session_id} ---")
    proof = engine.prove_session(session_id=session_id, tool_calls=sensitive_tool_calls)
    receipt = proof.to_receipt()["btp_proof_receipt"]

    print(f"[+] Proof ID: {receipt['proof_id']}")
    print(f"[+] Aggregate Commitment: {receipt['aggregate_commitment_hex'][:24]}...")
    print(f"[+] Aggregate Response: {receipt['aggregate_response_hex'][:24]}...")
    print(f"[+] Privacy Notice: {receipt['privacy_notice']}")

    # Confirm zero plaintext leakage
    receipt_str = str(receipt)
    assert "4981" not in receipt_str
    assert "query_customer_ssn" not in receipt_str

    # 2. Independent auditor verification (without knowing the original tool calls)
    print("\n--- [2] Independent Auditor Verification ---")
    is_valid = engine.verify_proof(proof)
    print(f"Auditor Verification Result: {is_valid} (Discrete Log Equation Satisfied)")
    assert is_valid is True

    print("\n" + "=" * 75)
    print("  ZK Compliance Auditing Complete: Zero Plaintext Leaked")
    print("=" * 75)
    return True


if __name__ == "__main__":
    main()
