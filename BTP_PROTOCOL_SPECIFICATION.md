# **Bartholomew Trust Protocol (BTP/2.2) — Formal Protocol Specification**
### **Status: Proposed Standard &bull; Category: Standards Track &bull; Version: 2.2**

---

## **1. Abstract**

The Bartholomew Trust Protocol (BTP) defines a vendor-neutral, cryptographically verifiable trust exchange format for autonomous agent systems, container runtimes, and CI/CD deployment gates. BTP enables autonomous agents and execution environments to establish authenticity, payload integrity, and policy compliance across trust boundaries with **zero network dependencies and 100% offline mathematical verifiability**.

---

## **2. Cryptographic Core Primitives**

1. **Serialization Standard:** Strict **IETF RFC 8785** JSON Canonicalization Scheme (JCS).
   * UTF-8 byte stream without BOM.
   * Object keys sorted lexicographically by UTF-16 code units.
   * IEEE 754 float/integer formatting matching ECMAScript standard.
   * Minimal string escaping (only `"` and `\` and control characters U+0000..U+001F).
2. **Digest Algorithm:** **SHA-256** (FIPS 180-4).
3. **Digital Signature Algorithm:** **Ed25519 / PureEdDSA** (RFC 8032 / FIPS 186-5).

---

## **3. Attestation Receipt Data Structure**

An authentic BTP Attestation Receipt consists of an `attestation` envelope and a hex-encoded `signature`:

```json
{
  "attestation": {
    "protocol_version": "BTP/2.2",
    "authority": "Bartholomew-Trust-Engine-v2.2",
    "authority_pubkey": "<64-hex-char-ed25519-public-key>",
    "nonce": "<32-hex-char-csprng-nonce>",
    "issued_at_unix": 1755648000,
    "expires_at_unix": 1755648300,
    "originating_agent": "Agent-A-Coordinator",
    "target_recipient": "Agent-B-Worker",
    "action_type": "DEPLOY_PATCH",
    "action_payload_hash": "<64-hex-char-sha256-hash-of-canonical-payload>",
    "verdict": "ALLOW",
    "reason": "All pre-flight checks and trajectory policies verified successfully."
  },
  "signature": "<128-hex-char-ed25519-signature>"
}
```

---

## **4. Mandatory Verification Algorithm (8-Step Gauntlet)**

Any independent verifier (in Go, Python, Rust, or C) MUST execute the following sequence:

```
┌────────────────────────────────────────────────────────────────────────┐
│                   8-STEP BTP VERIFICATION ALGORITHM                    │
├────────────────────────────────────────────────────────────────────────┤
│ 1. AUTHORITY MATCH: Assert attestation.authority_pubkey == pinned_key  │
│ 2. VERSION CHECK:   Assert attestation.protocol_version == "BTP/2.2"   │
│ 3. CONTEXT MATCH:   Assert attestation.target_recipient == self.id     │
│ 4. EXPIRY CHECK:    Assert time.now() <= attestation.expires_at_unix   │
│ 5. REPLAY CHECK:    Assert attestation.nonce not in seen_nonces        │
│ 6. PAYLOAD BINDING: Assert SHA256(JCS(candidate_payload)) == hash      │
│ 7. ED25519 VERIFY:  Assert Ed25519Verify(pubkey, JCS(att), signature)  │
│ 8. VERDICT GATE:    Assert attestation.verdict == "ALLOW"              │
└────────────────────────────────────────────────────────────────────────┘
```

---

## **5. Cross-Language Test Vectors**

Test vectors ensuring identical canonicalization and verification across runtimes are maintained in [`BTP_TEST_VECTORS.json`](file:///c:/Users/User/.gemini/antigravity/scratch/autonomous-circularity-network/BTP_TEST_VECTORS.json).

* **Go Reference Verifier:** [`btp_verifier.go`](file:///c:/Users/User/.gemini/antigravity/scratch/autonomous-circularity-network/btp_verifier.go)
* **Python Reference Verifier:** [`standalone_btp_verifier.py`](file:///c:/Users/User/.gemini/antigravity/scratch/autonomous-circularity-network/standalone_btp_verifier.py)

---
© 2026 Bartholomew AI & Contributors. Standards Track.
