"""
Test Suite for BTP Tamper-Evident Merkle Compliance Ledger
"""

import sys
import os
import json

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.audit_ledger import TamperEvidentAuditLedger
from src.trust_protocol import BartholomewTrustAuthority

def test_audit_ledger_integrity():
    print("=" * 80)
    print("  TESTING BTP TAMPER-EVIDENT MERKLE COMPLIANCE LEDGER")
    print("=" * 80)

    auth = BartholomewTrustAuthority(ttl_seconds=300)
    ledger = TamperEvidentAuditLedger()

    # 1. Append 50 valid agent action attestations
    print("[1] Appending 50 chained agent attestations...")
    for i in range(1, 51):
        payload = {"action": "AST_SLA_HEAL", "iteration": i, "target": f"service_{i}.py"}
        receipt = auth.evaluate_intent(
            agent_id=f"Agent-Cluster-{i%5}",
            action_type="DEPLOY_PATCH",
            payload=payload,
            target_recipient=f"Worker-Node-{i%3}"
        )
        entry = ledger.append_attestation(receipt)

    print(f"    |-- Total Entries: {len(ledger.entries)}")
    print(f"    |-- Tip Merkle Root: {ledger.get_merkle_root()[:32]}...")

    # 2. Verify chain integrity on clean ledger
    ok, msg = ledger.verify_chain_integrity()
    assert ok, f"Clean ledger failed verification: {msg}"
    print(f"[2] Clean Ledger Chain Verification: [SUCCESS] ({msg})")

    # 3. Adversarial Test: Mutate entry #23 payload
    print("\n[3] Testing Adversarial Retroactive Tampering Detection...")
    tampered_ledger = TamperEvidentAuditLedger()
    tampered_ledger.entries = json.loads(json.dumps(ledger.entries))
    tampered_ledger.current_tip_hash = ledger.current_tip_hash

    # Alter historical record at index 23
    tampered_ledger.entries[23]["attestation_packet"]["attestation"]["action_type"] = "MALICIOUS_ADMIN_ESCALATION"

    bad_ok, bad_msg = tampered_ledger.verify_chain_integrity()
    assert not bad_ok, "Security failure: Tampered historical ledger passed verification!"
    print(f"    |-- Tampering at Index 23 Caught: [YES]")
    print(f"    |-- Ledger Error Diagnosis: [{bad_msg}]")

    print("\n" + "=" * 80)
    print("  MERKLE COMPLIANCE LEDGER TEST SUITE: 100% PASSED")
    print("=" * 80)

if __name__ == "__main__":
    test_audit_ledger_integrity()
    sys.exit(0)
