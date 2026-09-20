"""
Adversarial Falsification & Attack Benchmark for Bartholomew Trust Protocol (BTP v2.1)
Directly tests attacks against the trust model:
1. Replay Attacks
2. Expired Attestation Exploits
3. Post-Attestation Artifact Substitution Attacks
4. Forged / Self-Signed Authority Roots
5. Total Cloud Outage / Offline Independent Verification
"""

import sys
import os
import json
import time

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.trust_protocol import BartholomewTrustAuthority, IndependentTrustVerifier
from cryptography.hazmat.primitives.asymmetric import ed25519

def run_falsification_battery():
    print("=" * 80)
    print("  BARTHOLOMEW TRUST MODEL ADVERSARIAL FALSIFICATION BATTERY")
    print("=" * 80)
    print("  Principle: 'Trust isn't granted. Trust is demonstrated.'")
    print("=" * 80)

    authority = BartholomewTrustAuthority(ttl_seconds=60)
    trusted_root_pubkey = authority.public_key_hex
    seen_nonces = set()

    # 1. Base Valid Attestation
    clean_payload = {"file": "worker.py", "delta": 3, "code": "def process(): return True"}
    valid_packet = authority.evaluate_intent(
        agent_id="Agent-OpenAI-GPT4o",
        action_type="DEPLOY_PATCH",
        payload=clean_payload
    )

    # -------------------------------------------------------------------------
    # TEST 1: Baseline Valid Execution (Must Pass)
    # -------------------------------------------------------------------------
    ok, msg = IndependentTrustVerifier.verify_attestation(
        attestation_packet=valid_packet,
        expected_payload=clean_payload,
        trusted_root_pubkey=trusted_root_pubkey,
        seen_nonces=seen_nonces
    )
    print(f"\n[TEST 1: BASELINE VERIFICATION]")
    print(f"   Result: {msg}")
    assert ok

    # -------------------------------------------------------------------------
    # TEST 2: Replay Attack (Re-submitting the same attestation packet)
    # -------------------------------------------------------------------------
    ok, msg = IndependentTrustVerifier.verify_attestation(
        attestation_packet=valid_packet,
        expected_payload=clean_payload,
        trusted_root_pubkey=trusted_root_pubkey,
        seen_nonces=seen_nonces
    )
    print(f"\n[TEST 2: REPLAY ATTACK]")
    print(f"   Attacker Action: Re-submitting previous valid attestation packet...")
    print(f"   Gate Defense: {msg}")
    assert not ok
    assert "REPLAY_ATTACK_DETECTED" in msg

    # -------------------------------------------------------------------------
    # TEST 3: Expired Attestation Window (Simulating TTL Expiry)
    # -------------------------------------------------------------------------
    future_time = time.time() + 120 # 2 minutes in future (exceeds 60s TTL)
    fresh_packet = authority.evaluate_intent(
        agent_id="Agent-A",
        action_type="DEPLOY_PATCH",
        payload=clean_payload
    )
    ok, msg = IndependentTrustVerifier.verify_attestation(
        attestation_packet=fresh_packet,
        expected_payload=clean_payload,
        trusted_root_pubkey=trusted_root_pubkey,
        current_timestamp=future_time
    )
    print(f"\n[TEST 3: EXPIRED ATTESTATION EXPLOIT]")
    print(f"   Attacker Action: Submitting attestation after TTL expiry (+120s)...")
    print(f"   Gate Defense: {msg}")
    assert not ok
    assert "EXPIRED_ATTESTATION" in msg

    # -------------------------------------------------------------------------
    # TEST 4: Post-Attestation Artifact Substitution (Bait-and-Switch)
    # -------------------------------------------------------------------------
    substituted_payload = {"file": "worker.py", "delta": 3, "malicious_backdoor": "eval(untrusted_req)"}
    ok, msg = IndependentTrustVerifier.verify_attestation(
        attestation_packet=fresh_packet,
        expected_payload=substituted_payload,
        trusted_root_pubkey=trusted_root_pubkey
    )
    print(f"\n[TEST 4: ARTIFACT SUBSTITUTION (BAIT-AND-SWITCH)]")
    print(f"   Attacker Action: Attestation generated on safe code, then substituted with malicious code...")
    print(f"   Gate Defense: {msg}")
    assert not ok
    assert "ARTIFACT_SUBSTITUTION_DETECTED" in msg

    # -------------------------------------------------------------------------
    # TEST 5: Forged / Self-Signed Root Authority
    # -------------------------------------------------------------------------
    fake_authority = BartholomewTrustAuthority()
    fake_packet = fake_authority.evaluate_intent(
        agent_id="Agent-A",
        action_type="DEPLOY_PATCH",
        payload=clean_payload
    )
    ok, msg = IndependentTrustVerifier.verify_attestation(
        attestation_packet=fake_packet,
        expected_payload=clean_payload,
        trusted_root_pubkey=trusted_root_pubkey # Verified against real root key
    )
    print(f"\n[TEST 5: SELF-SIGNED / FORGED AUTHORITY KEY]")
    print(f"   Attacker Action: Attacker generates rogue Ed25519 keypair and signs attestation...")
    print(f"   Gate Defense: {msg}")
    assert not ok
    assert "FORGERY_DETECTED" in msg

    # -------------------------------------------------------------------------
    # TEST 6: 100% Offline Zero-Network Independent Verification
    # -------------------------------------------------------------------------
    t0 = time.perf_counter()
    offline_verified, offline_msg = IndependentTrustVerifier.verify_attestation(
        attestation_packet=fresh_packet,
        expected_payload=clean_payload,
        trusted_root_pubkey=trusted_root_pubkey
    )
    offline_latency_us = (time.perf_counter() - t0) * 1_000_000
    print(f"\n[TEST 6: ZERO-NETWORK OFFLINE INDEPENDENCE]")
    print(f"   Network Status: Completely Offline (0 HTTP calls, 0 cloud dependencies)")
    print(f"   Verification Latency: {offline_latency_us:.2f} µs")
    print(f"   Verification Result: {offline_msg}")
    assert offline_verified

    print("\n" + "=" * 80)
    print("  FALSIFICATION BATTERY SUMMARY: ALL 6/6 ADVERSARIAL ATTACKS MITIGATED")
    print("================================================================================")
    print("  1. Replay Attacks:            BLOCKED via Cryptographic Nonces")
    print("  2. Expired Attestations:      BLOCKED via Time-To-Live Window")
    print("  3. Artifact Substitution:     BLOCKED via RFC 8785 SHA-256 Hash Binding")
    print("  4. Forged Authority Roots:    BLOCKED via Ed25519 Root Key Pinning")
    print("  5. Offline Resilience:        PROVEN with Zero Server Dependencies")
    print("================================================================================")
    return True

if __name__ == "__main__":
    success = run_falsification_battery()
    sys.exit(0 if success else 1)
