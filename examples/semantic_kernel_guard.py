"""
Bartholomew Guard Example: Microsoft Semantic Kernel Plugin Gating
==================================================================
Demonstrates how to intercept native Microsoft Semantic Kernel function calls
and kernel filters with sub-50 µs AST invariant checking and Ed25519 seals.
"""

import sys
import os

# Add parent directory to path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from src.trust_protocol import BartholomewTrustAuthority


class SemanticKernelFunctionFilter:
    """
    Simulates a native Semantic Kernel IFunctionInvocationFilter / Plugin Guard.
    """
    def __init__(self):
        self.authority = BartholomewTrustAuthority()

    def on_function_invoking(self, plugin_name: str, function_name: str, arguments: dict) -> dict:
        """
        Invoked immediately before Semantic Kernel executes any native plugin tool.
        """
        action_type = f"{plugin_name}::{function_name}"
        
        # Invariant Pre-Flight Evaluation
        receipt = self.authority.evaluate_intent(
            agent_id="semantic-kernel-orchestrator",
            action_type=action_type,
            payload=arguments
        )

        att_dict = receipt.get("attestation", {})
        verdict = att_dict.get("verdict", "DENY")
        is_allowed = (verdict == "ALLOW")

        return {
            "allowed": is_allowed,
            "verdict": verdict,
            "latency_us": att_dict.get("evaluation_latency_us", 0.0),
            "signature": receipt.get("signature"),
            "receipt": receipt
        }


def run_semantic_kernel_demo():
    print("=" * 70)
    print("DEMO: BARTHOLOMEW GUARD FOR MICROSOFT SEMANTIC KERNEL")
    print("=" * 70)

    sk_guard = SemanticKernelFunctionFilter()

    # Case 1: Safe Math Plugin Invocation
    res1 = sk_guard.on_function_invoking("MathPlugin", "CalculateLoan", {"principal": 10000, "rate": 0.05})
    print(f"[*] Case 1 (Safe MathPlugin)       -> Allowed: {res1['allowed']} | Verdict: {res1['verdict']} | Latency: {res1['latency_us']:.2f} us")

    # Case 2: Destructive FileIO Plugin Invocation
    res2 = sk_guard.on_function_invoking("FileIOPlugin", "DeleteDirectory", {"path": "/var/log/audit", "recursive": True})
    print(f"[*] Case 2 (Unsafe FileIOPlugin)   -> Allowed: {res2['allowed']} | Verdict: {res2['verdict']} | Latency: {res2['latency_us']:.2f} us")

    # Case 3: High Value Stripe Payment Plugin
    res3 = sk_guard.on_function_invoking("BillingPlugin", "TransferFunds", {"amount_usd": 2500.00, "to": "acct_88"})
    print(f"[*] Case 3 (Spend Cap Breach)      -> Allowed: {res3['allowed']} | Verdict: {res3['verdict']} (Requires Co-Sign)")

    print("\n[OK] Microsoft Semantic Kernel Plugin Guard Demo Completed Cleanly.")


if __name__ == "__main__":
    run_semantic_kernel_demo()
