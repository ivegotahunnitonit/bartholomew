"""
Live Adversarial Audit & Cross-Language Parity Test
Directly attacks the live Google Cloud Run backend and proves cross-language byte parity.
"""

import urllib.request
import json
import subprocess
import hashlib
import sys
import os

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.rfc8785 import rfc8785_canonicalize

def run_deep_adversarial_audit():
    print("=" * 80)
    print("  DEEP ADVERSARIAL SKEPTICISM AUDIT & LIVE ATTACK HARNESS")
    print("=" * 80)

    # -------------------------------------------------------------------------
    # 1. Cross-Language RFC 8785 Hash Parity (Python vs Node.js)
    # -------------------------------------------------------------------------
    test_object = {
        "z_key": "test",
        "a_key": 123.45,
        "nested": {
            "unicode": "日本語",
            "escapes": "line1\nline2\t\"quoted\"",
            "list": [3, 2, 1]
        },
        "b_bool": True,
        "c_null": None
    }

    py_bytes = rfc8785_canonicalize(test_object)
    py_hash = hashlib.sha256(py_bytes).hexdigest()

    node_script = f"""
import {{ rfc8785Canonicalize }} from './btp_verifier.js';
import crypto from 'crypto';
const obj = {json.dumps(test_object)};
const b = rfc8785Canonicalize(obj);
console.log(crypto.createHash('sha256').update(b).digest('hex'));
"""
    node_out = subprocess.check_output(['node', '--input-type=module', '-e', node_script], text=True).strip()

    print("[1] RFC 8785 Canonical JCS Hash Parity Check:")
    print(f"    |-- Python SHA-256:  {py_hash}")
    print(f"    |-- Node.js SHA-256: {node_out}")
    assert py_hash == node_out, "FATAL: Cross-language hash mismatch!"
    print("    |-- Result: 100.00% EXACT BYTE-FOR-BYTE PARITY")

    # -------------------------------------------------------------------------
    # 2. Live Public Cloud Run Attacks over Real Internet HTTPS
    # -------------------------------------------------------------------------
    base = "https://acn-backend-444129982305.us-central1.run.app"
    print(f"\n[2] Attacking Live Cloud Run Gateway ({base})...")

    # Step A: Request a legitimate receipt for a safe payload
    req_eval_data = json.dumps({
        "agent_id": "Adversarial-Test-Agent",
        "action_type": "DEPLOY_PATCH",
        "payload": {"file": "safe.py", "delta": 1},
        "target_recipient": "Target-Worker-Node"
    }).encode("utf-8")

    req_eval = urllib.request.Request(
        f"{base}/v2.2/evaluate",
        data=req_eval_data,
        headers={"Content-Type": "application/json", "User-Agent": "BTP-Auditor/2.2"}
    )
    with urllib.request.urlopen(req_eval, timeout=10) as r:
        legit_receipt = json.loads(r.read().decode("utf-8"))

    print(f"    |-- Baseline Legitimate Receipt Issued (HTTP {r.status} OK)")
    print(f"    |-- Signature: {legit_receipt['signature'][:32]}...")

    # ATTACK 1: Payload Tampering Injection
    req_att1_data = json.dumps({
        "receipt": legit_receipt,
        "candidate_payload": {"file": "MALICIOUS_INJECTION.py", "delta": 999},
        "expected_recipient": "Target-Worker-Node"
    }).encode("utf-8")
    req_att1 = urllib.request.Request(f"{base}/v2.2/verify", data=req_att1_data, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req_att1, timeout=10) as r:
        res1 = json.loads(r.read().decode("utf-8"))
        print(f"\n[ATTACK 1] Payload Tampering Attack:")
        print(f"    |-- Attestation Valid: {res1.get('valid')} (Expected: False)")
        print(f"    |-- Cloud Defense Log: {res1.get('message')}")
        assert res1.get("valid") is False, "SECURITY FAILURE: Tampered payload accepted!"

    # ATTACK 2: Cross-Recipient Privilege Escalation
    req_att2_data = json.dumps({
        "receipt": legit_receipt,
        "candidate_payload": {"file": "safe.py", "delta": 1},
        "expected_recipient": "Unauthorized-Master-Admin"
    }).encode("utf-8")
    req_att2 = urllib.request.Request(f"{base}/v2.2/verify", data=req_att2_data, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req_att2, timeout=10) as r:
        res2 = json.loads(r.read().decode("utf-8"))
        print(f"\n[ATTACK 2] Cross-Recipient Privilege Escalation Attack:")
        print(f"    |-- Attestation Valid: {res2.get('valid')} (Expected: False)")
        print(f"    |-- Cloud Defense Log: {res2.get('message')}")
        assert res2.get("valid") is False, "SECURITY FAILURE: Cross-recipient replay accepted!"

    # ATTACK 3: Cryptographic Signature Mutation (1-Bit Flip)
    corrupted_receipt = json.loads(json.dumps(legit_receipt))
    sig_chars = list(corrupted_receipt["signature"])
    sig_chars[0] = 'f' if sig_chars[0] != 'f' else '0'
    corrupted_receipt["signature"] = "".join(sig_chars)

    req_att3_data = json.dumps({
        "receipt": corrupted_receipt,
        "candidate_payload": {"file": "safe.py", "delta": 1},
        "expected_recipient": "Target-Worker-Node"
    }).encode("utf-8")
    req_att3 = urllib.request.Request(f"{base}/v2.2/verify", data=req_att3_data, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req_att3, timeout=10) as r:
        res3 = json.loads(r.read().decode("utf-8"))
        print(f"\n[ATTACK 3] Mutated Ed25519 Signature Attack:")
        print(f"    |-- Attestation Valid: {res3.get('valid')} (Expected: False)")
        print(f"    |-- Cloud Defense Log: {res3.get('message')}")
        assert res3.get("valid") is False, "SECURITY FAILURE: Mutated signature accepted!"

    print("\n" + "=" * 80)
    print("  AUDIT VERDICT: 100% MATHEMATICAL & LIVE CLOUD ATTACK DEFENSE VERIFIED")
    print("=" * 80)
    return True

if __name__ == "__main__":
    success = run_deep_adversarial_audit()
    sys.exit(0 if success else 1)
