"""
Cookbook Recipe: Confidential Hardware Enclave Anchoring (Nitro / SEV-SNP)
==========================================================================
Demonstrates locking recursive ZK-Rollup batches into hardware PCR registers
to guarantee untampered cloud enclave execution.

Run:
    python cookbook/future_swarms/confidential_enclave_anchor.py
"""

import sys
import os

# Add repository root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from src.zk_compliance_proof_engine import ZKComplianceEngine
from src.zk_rollup_batcher import ZKRollupBatcher, EnclaveZKRollupAnchor
from src.confidential_enclave_attestation import ConfidentialEnclaveAttestationEngine


def main():
    print("=" * 75)
    print("  BTP Global Cookbook: Confidential Enclave Anchoring Demo")
    print("=" * 75)

    zk_engine = ZKComplianceEngine()
    batcher = ZKRollupBatcher()

    # 1. Produce proofs from 2 sessions
    print("\n--- [1] Aggregating Agent Sessions into ZK-Rollup ---")
    p1 = zk_engine.prove_session("session-01", ["ls -la", "grep pattern file.txt"])
    p2 = zk_engine.prove_session("session-02", ["cat /app/data.json"])
    batcher.add_proof(p1)
    batcher.add_proof(p2)

    rollup = batcher.seal()
    print(f"[+] Sealed Rollup: {rollup.batch_id}")
    print(f"[+] Merkle Root: {rollup.merkle_root}")
    print(f"[+] Aggregate Commitment: {rollup.aggregate_commitment[:24]}...")

    # 2. Hardware Enclave Attestation Anchor
    print("\n--- [2] Generating Hardware Attestation Anchor ---")
    enclave_engine = ConfidentialEnclaveAttestationEngine()
    anchor = EnclaveZKRollupAnchor.create_hardware_anchor(
        rollup=rollup,
        enclave_engine=enclave_engine,
        module_id="aws-nitro-enclave-worker-01"
    )

    print(f"[+] Hardware Status: {anchor['status']}")
    print(f"[+] Nonce: {anchor['hardware_enclave_attestation']['measurements']['nonce']}")
    print(f"[+] PCR0 Golden Hash: {anchor['hardware_enclave_attestation']['measurements']['pcr0'][:24]}...")

    # 3. Verify Hardware Root of Trust
    print("\n--- [3] Verifying Hardware Enclave Attestation Document ---")
    is_valid, msg = EnclaveZKRollupAnchor.verify_hardware_anchor(anchor, enclave_engine=enclave_engine)
    print(f"Hardware Verification Result: {is_valid} ({msg})")
    assert is_valid is True

    print("\n" + "=" * 75)
    print("  Hardware Enclave Anchor Complete: Root-of-Trust Attested")
    print("=" * 75)
    return True


if __name__ == "__main__":
    main()
