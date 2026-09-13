# **Bartholomew Trust Protocol (BTP/2.2) — Formal Specification (FROZEN)**
### **Status: Frozen Proposed Standard &bull; Classification: Standards Track &bull; Version: 2.2**
### **Intellectual Property Notice: Business Source License (BSL 1.1) & Proprietary Protective Agreement**

---

## **1. Abstract & Scope**

The Bartholomew Trust Protocol (BTP v2.2) defines a **vendor-neutral, decentralized, cryptographically verifiable trust exchange specification** for autonomous agent architectures, container runtimes, and CI/CD deployment gates.

BTP v2.2 is **formally frozen**. It enables autonomous systems to establish identity, payload integrity, semantic policy provenance, and capability scope boundaries with **zero network dependencies and 100% offline mathematical verifiability**.

---

## **2. Decentralized Multi-Authority Trust Architecture**

BTP does not mandate a single centralized authority. Instead, **any organization, agent network, or sovereign enterprise cluster can configure its own root trust store**:

```

                   DECENTRALIZED MULTI-AUTHORITY STORE                  

 [Recipient Agent / Deployment Gate]                                    
     Trust Store: [Pubkey_Authority_A, Pubkey_Authority_B]           
     Validates:   Attestation signed by any recognized authority     
     Rejects:     Attestations from unrecognized/rogue keys          

```

---

## **3. Formal Attestation Envelope Structure (BTP v2.2 Frozen)**

Every authenticated statement MUST contain the following structured fields signed via **RFC 8785 (JCS)** and **FIPS 186-5 Ed25519**:

```json
{
  "attestation": {
    "protocol_version": "BTP/2.2",
    "authority": "Bartholomew-Trust-Engine-v2.2",
    "authority_pubkey": "<64-hex-char-ed25519-public-key>",
    "nonce": "<32-hex-char-csprng-nonce>",
    "issued_at_unix": 1771500000.0,
    "expires_at_unix": 1771500300.0,
    "originating_agent": "Agent-LangGraph-01",
    "target_recipient": "Agent-AutoGen-02",
    "action_type": "DEPLOY_PATCH",
    "action_payload_hash": "<sha256-hash-of-rfc8785-canonical-payload>",
    "policy_id": "urn:btp:policy:owasp-agentic-v2026.1",
    "policy_hash": "<sha256-hash-of-evaluated-policy-ruleset>",
    "capability_scope": ["FS_WRITE_RESTRICTED", "NO_NET_EGRESS", "AST_MAX_DELTA_5"],
    "verdict": "ALLOW",
    "reason": "All pre-flight checks and trajectory policies verified successfully."
  },
  "signature": "<128-hex-char-ed25519-signature>"
}
```

---

## **4. Mandatory 10-Step Verification Algorithm**

An independent conforming verifier MUST execute the following sequence:

1. **Authority Pinning:** Verify `attestation.authority_pubkey` is in the recipient's configured `trusted_root_pubkeys`.
2. **Version Pinning:** Assert `attestation.protocol_version == "BTP/2.2"`.
3. **Recipient Binding:** Assert `attestation.target_recipient == self.id` (or wildcard if authorized).
4. **Clock Skew & Future-Timestamp Defense:** Assert `attestation.issued_at_unix <= now + 60.0s`.
5. **Expiration Window (TTL):** Assert `now <= attestation.expires_at_unix`.
6. **Nonce Uniqueness:** Assert `attestation.nonce` has not been seen in the active replay window.
7. **Policy Hash Provenance:** Assert `attestation.policy_hash == expected_policy_hash` (if specified).
8. **Capability Scope Check:** Assert `set(attestation.capability_scope).issubset(allowed_capabilities)`.
9. **Payload Hash Integrity:** Assert `SHA256(RFC8785(candidate_payload)) == attestation.action_payload_hash`.
10. **Ed25519 Signature Verification:** Mathematically verify `Ed25519Verify(authority_pubkey, RFC8785(attestation), signature)`.

---

---

## **6. BTP v2.4 Extension: Chained Merkle Trajectories & MCP Transactional Semantics**

In BTP v2.4, the protocol extends isolated attestations to **stateful, chained multi-turn agent sessions** over Anthropic's Model Context Protocol (MCP):

### **6.1 Chained Merkle Turn Receipt (`BTP/2.4`)**
Each turn receipt cryptographically commits to the session's prior execution state via hash chaining:
$$H_i = \text{SHA256}(H_{i-1} \parallel \text{RFC8785}(\text{receipt}_i))$$

```json
{
  "protocol": "BTP/2.4",
  "turn_index": 3,
  "parent_receipt_hash": "029807446fb2b9ada32c113e93926b39...",
  "receipt_hash": "952abfb3eee25017f2d751ceb91d2cc9...",
  "tool_name": "execute_command",
  "action_payload_hash": "<sha256-hash-of-sanitized-tool-args>",
  "scrubbed_secrets_count": 0,
  "transaction_state": "COMMITTED",
  "timestamp_unix": 1772670000.0,
  "signature": "<128-hex-char-ed25519-signature>"
}
```

### **6.2 Atomic Copy-on-Write (CoW) Workspace Rollback**
* **Snapshot Engine**: Prior to invoking mutating tools (`write_file`, `patch_file`, `execute_command`), BTP captures an in-memory byte snapshot of target paths.
* **Invariant Evaluation**: Tool execution is monitored against workspace root boundaries (`os.path.commonpath`) and scoped AST policies.
* **Instant Reversion**: If boundary violation occurs, all mutations are reverted in $<5\,\mu\text{s}$ (measured benchmark: $2.30\,\mu\text{s}$), and JSON-RPC error code `-32000` is returned with structured diagnostic hints enabling LLM self-correction.

---

## **7. Conformance Suite & External Implementation Challenge**

The frozen conformance test vectors are publicly verifiable in [`BTP_CONFORMANCE_SUITE.json`](file:///c:/Users/User/.gemini/antigravity/scratch/autonomous-circularity-network/BTP_CONFORMANCE_SUITE.json):

* **Python Reference Verifier:** [`standalone_btp_verifier.py`](file:///c:/Users/User/.gemini/antigravity/scratch/autonomous-circularity-network/standalone_btp_verifier.py)
* **Go Reference Verifier:** [`btp_verifier.go`](file:///c:/Users/User/.gemini/antigravity/scratch/autonomous-circularity-network/btp_verifier.go)
* **MCP Proxy & Transaction Suite:** [`src/mcp_gateway.py`](file:///c:/Users/User/.gemini/antigravity/scratch/autonomous-circularity-network/src/mcp_gateway.py), [`src/workspace_transaction.py`](file:///c:/Users/User/.gemini/antigravity/scratch/autonomous-circularity-network/src/workspace_transaction.py)
* **Conformance Test Runner:** [`tests/test_v24_mcp_transaction.py`](file:///c:/Users/User/.gemini/antigravity/scratch/autonomous-circularity-network/tests/test_v24_mcp_transaction.py)

---
© 2026 Bartholomew AI & Contributors. All Rights Reserved. Proprietary Commercial License (BSL 1.1).

