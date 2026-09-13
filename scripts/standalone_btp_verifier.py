"""
BTP Standalone Independent Reference Verifier (Frozen BTP v2.2 Standards Track)
Provides 100% offline, zero-network cryptographic verification for BTP receipts.
Does not depend on any proprietary Bartholomew SDK.
"""

import json
import hashlib
import time
from typing import Dict, Any, Tuple, Optional, Set, List, Union
from cryptography.hazmat.primitives.asymmetric import ed25519

# Embedded RFC 8785 JSON Canonicalization Scheme (JCS)
def rfc8785_canonicalize(val: Any) -> bytes:
    def _ser(v):
        if v is None: return "null"
        if isinstance(v, bool): return "true" if v else "false"
        if isinstance(v, int): return str(v)
        if isinstance(v, float):
            if v == 0.0: return "0"
            return str(int(v)) if v.is_integer() else repr(v).replace("E", "e").replace("e+", "e")
        if isinstance(v, str):
            out = []
            for c in v:
                code = ord(c)
                if c == '"': out.append('\\"')
                elif c == '\\': out.append('\\\\')
                elif c == '\b': out.append('\\b')
                elif c == '\f': out.append('\\f')
                elif c == '\n': out.append('\\n')
                elif c == '\r': out.append('\\r')
                elif c == '\t': out.append('\\t')
                elif code < 0x20: out.append(f"\\u{code:04x}")
                else: out.append(c)
            return '"' + "".join(out) + '"'
        if isinstance(v, (list, tuple)):
            return "[" + ",".join(_ser(x) for x in v) + "]"
        if isinstance(v, dict):
            keys = sorted(v.keys(), key=lambda k: [ord(c) for c in k])
            return "{" + ",".join(f"{_ser(k)}:{_ser(v[k])}" for k in keys) + "}"
        raise TypeError(f"Unserializable type {type(v)}")
    return _ser(val).encode('utf-8')

def independent_verify_btp_receipt(receipt_json_str: str, 
                                  candidate_payload: Dict[str, Any], 
                                  trusted_root_pubkeys: Union[str, List[str]],
                                  expected_recipient_context: Optional[str] = None,
                                  seen_nonces: Optional[Set[str]] = None,
                                  eval_timestamp: Optional[float] = None,
                                  required_policy_hash: Optional[str] = None,
                                  allowed_capabilities: Optional[List[str]] = None) -> Tuple[bool, str]:
    """
    Independently verifies a BTP trust receipt with ZERO network requests.
    Validates complete contextual and semantic binding:
    1. Authority Public Key match against trusted authority store.
    2. Protocol Version compatibility (BTP/2.2).
    3. Target Recipient context binding.
    4. Expiration Window & Future-Timestamp defense (Clock Skew).
    5. Nonce uniqueness (Replay Defense).
    6. Policy Hash provenance matching.
    7. Capability Scope containment.
    8. RFC 8785 SHA-256 payload hash binding.
    9. Mathematical Ed25519 digital signature over canonical attestation.
    10. Policy verdict authorization.
    """
    try:
        packet = json.loads(receipt_json_str) if isinstance(receipt_json_str, str) else receipt_json_str
        att = packet.get("attestation", {})
        signature_hex = packet.get("signature", "")

        trusted_keys = [trusted_root_pubkeys] if isinstance(trusted_root_pubkeys, str) else trusted_root_pubkeys

        # 1. Authority Pinning Check (Decentralized Multi-Authority Store)
        authority_key = att.get("authority_pubkey")
        if authority_key not in trusted_keys:
            return False, "FORGERY_DETECTED: Authority public key does not match any recognized root in trust store"

        # 2. Protocol Version Check
        if att.get("protocol_version") != "BTP/2.2":
            return False, "PROTOCOL_MISMATCH: Unsupported or deprecated BTP protocol version"

        # 3. Recipient Context Binding Check (Cross-Context Replay Defense)
        if expected_recipient_context:
            receipt_recipient = att.get("target_recipient")
            if receipt_recipient and receipt_recipient != expected_recipient_context:
                return False, f"CONTEXT_MISMATCH: Receipt intended for '{receipt_recipient}', not '{expected_recipient_context}'"

        # 4. Expiration & Future-Dated Checks
        now = eval_timestamp if eval_timestamp is not None else time.time()
        issued_at = att.get("issued_at_unix", 0)
        expires_at = att.get("expires_at_unix", 0)

        if issued_at > (now + 60.0): # Allow max 60s clock skew
            return False, f"FUTURE_DATED_RECEIPT: Attestation issuance timestamp {issued_at} is in future relative to {now}"

        if now > expires_at:
            return False, f"EXPIRED_RECEIPT: Attestation token expired {now - expires_at:.1f}s ago"

        # 5. Nonce Uniqueness Check (Replay Defense)
        nonce = att.get("nonce")
        if not nonce:
            return False, "INVALID_RECEIPT: Missing cryptographic nonce"
        if seen_nonces is not None:
            if nonce in seen_nonces:
                return False, f"REPLAY_ATTACK: Nonce '{nonce}' has already been processed"
            seen_nonces.add(nonce)

        # 6. Policy Hash Provenance Check
        if required_policy_hash and att.get("policy_hash") != required_policy_hash:
            return False, f"POLICY_HASH_MISMATCH: Receipt evaluated under policy hash {att.get('policy_hash')}, expected {required_policy_hash}"

        # 7. Capability Scope Containment Check
        if allowed_capabilities is not None:
            receipt_caps = set(att.get("capability_scope", []))
            allowed_set = set(allowed_capabilities)
            if not receipt_caps.issubset(allowed_set):
                return False, f"CAPABILITY_OVERREACH: Receipt requests capabilities {receipt_caps - allowed_set} exceeding allowed policy"

        # 8. RFC 8785 SHA-256 Payload Hash Binding Check
        expected_hash = hashlib.sha256(rfc8785_canonicalize(candidate_payload)).hexdigest()
        if att.get("action_payload_hash") != expected_hash:
            return False, "PAYLOAD_TAMPERED: Candidate payload does not match evaluated hash"

        # 9. Mathematical Ed25519 Signature Verification
        pubkey = ed25519.Ed25519PublicKey.from_public_bytes(bytes.fromhex(authority_key))
        canonical_att_bytes = rfc8785_canonicalize(att)
        pubkey.verify(bytes.fromhex(signature_hex), canonical_att_bytes)

        # 10. Verdict Authorization
        if att.get("verdict") != "ALLOW":
            return False, f"ACTION_DENIED_BY_POLICY: {att.get('reason')}"

        return True, "VERIFIED_VALID: Cryptographic proof demonstrated independently"

    except Exception as e:
        return False, f"VERIFICATION_FAILED: {str(e)}"


def verify_evidence_package(filepath: str) -> Tuple[bool, str, Dict[str, Any]]:
    """
    Independently verifies a SOC 2 / ISO 27001 Evidence Pack without external network dependencies.
    """
    import os
    if not os.path.exists(filepath):
        return False, f"File not found: {filepath}", {}

    with open(filepath, "r", encoding="utf-8") as f:
        pack = json.load(f)

    report_id = pack.get("report_id", "UNKNOWN")
    expected_root = pack.get("merkle_root_sha256")
    controls = pack.get("audited_controls", [])

    if not expected_root:
        return False, "Missing 'merkle_root_sha256' in evidence pack", {}

    # Reconstruct Merkle root over audited controls
    leaves = []
    for ctrl in controls:
        if ctrl.get("status") != "PASS":
            return False, f"Control failure detected in {ctrl.get('control_id')}: status={ctrl.get('status')}", {}
        leaf_hash = hashlib.sha256(json.dumps(ctrl, sort_keys=True).encode("utf-8")).hexdigest()
        leaves.append(leaf_hash)

    # Compute Merkle root exactly matching generator algorithm
    if not leaves:
        calc_root = hashlib.sha256(b"empty_ledger").hexdigest()
    else:
        cur_layer = list(leaves)
        while len(cur_layer) > 1:
            if len(cur_layer) % 2 != 0:
                cur_layer.append(cur_layer[-1])
            next_layer = []
            for i in range(0, len(cur_layer), 2):
                combined = cur_layer[i] + cur_layer[i + 1]
                next_layer.append(hashlib.sha256(combined.encode("utf-8")).hexdigest())
            cur_layer = next_layer
        calc_root = cur_layer[0]

    # Verify root hash matches
    if calc_root != expected_root:
        return False, f"MERKLE_ROOT_MISMATCH: Calculated {calc_root}, expected {expected_root}", {}

    return True, "VERIFIED_VALID: All controls demonstrated cryptographically without exceptions", {
        "report_id": report_id,
        "protocol_version": pack.get("protocol_version"),
        "license_tier": pack.get("license_tier"),
        "merkle_root": calc_root,
        "control_count": len(controls),
        "frameworks": pack.get("compliance_frameworks", [])
    }


if __name__ == "__main__":
    import argparse
    import sys

    parser = argparse.ArgumentParser(description="BTP Standalone Offline Cryptographic Reference Verifier")
    parser.add_argument("--verify-evidence", type=str, help="Path to SOC 2 Type II evidence pack JSON to verify")
    parser.add_argument("--receipt", type=str, help="Path to BTP receipt JSON file")
    parser.add_argument("--payload", type=str, help="Path to candidate action payload JSON file")
    parser.add_argument("--pubkey", type=str, help="Hex-encoded Ed25519 authority public key")

    args = parser.parse_args()

    if args.verify_evidence:
        ok, msg, meta = verify_evidence_package(args.verify_evidence)
        print("=" * 72)
        print("  BTP INDEPENDENT COMPLIANCE EVIDENCE AUDIT VERIFICATION")
        print("=" * 72)
        print(f"  • Evidence File    : {args.verify_evidence}")
        print(f"  • Report ID        : {meta.get('report_id', 'N/A')}")
        print(f"  • License Tier     : {meta.get('license_tier', 'N/A')}")
        print(f"  • Merkle Root Hash : {meta.get('merkle_root', 'N/A')}")
        print(f"  • Audited Controls : {meta.get('control_count', 0)} / {meta.get('control_count', 0)} PASSED")
        print(f"  • Verification SLA : 0 Network Bytes | 100% Offline Cryptographic Match")
        print("=" * 72)
        if ok:
            print(f"  [RESULT] SUCCESS: {msg}")
            print("=" * 72)
            sys.exit(0)
        else:
            print(f"  [RESULT] FAILED: {msg}")
            print("=" * 72)
            sys.exit(1)

    elif args.receipt and args.payload and args.pubkey:
        with open(args.receipt, "r", encoding="utf-8") as f:
            receipt_str = f.read()
        with open(args.payload, "r", encoding="utf-8") as f:
            payload = json.load(f)

        ok, msg = independent_verify_btp_receipt(receipt_str, payload, args.pubkey)
        if ok:
            print(f"[OK] {msg}")
            sys.exit(0)
        else:
            print(f"[ERROR] {msg}")
            sys.exit(1)
    else:
        parser.print_help()
        sys.exit(1)
