# Bartholomew Trust Protocol (BTP v0.1) Specification
**A vendor-neutral protocol for machine identity, delegated authority, verifiable intent, and independently verifiable execution evidence.**

---

## 1. Overview & Core Philosophy

The Bartholomew Trust Protocol (BTP v0.1) defines a vendor-neutral wire format and cryptographic verification procedure for cross-organizational machine interactions.

BTP operates on a single architectural principle:
**Bartholomew is not the authority; it is the verification mechanism.**

Counterparty systems (Resource Owners) do not call Bartholomew APIs or query Bartholomew databases. Instead, they independently verify signed BTP Evidence Artifacts using pinned root public keys and standard cryptographic hashing.

---

## 2. Protocol Standards (BTP-001 through BTP-008)

### BTP-001: Machine Identity Credential
A machine identity credential represents an agent's cryptographically established identity.

```json
{
  "agent_did": "did:bth:org_a_agent_alpha",
  "issuer_did": "did:bth:org_a_root",
  "issuer_pub_key": "pubkey_org_a_ed25519_key_101",
  "audience": "urn:btp:resource:org_c",
  "resource": "urn:btp:resource:compute_node_4",
  "possessed_capabilities": ["compute.execute", "resource_c.access"],
  "constraint_manifest": ["max_cost_500", "region_ca_only"],
  "issued_at": "2026-08-12T12:00:00Z",
  "expires_at": "2026-12-31T23:59:59Z",
  "signature": "sig_issuer_ed25519_..."
}
```

### BTP-002: Authority Delegation Chain
A delegation chain links a Root Authority to a Sub-Agent.

```json
{
  "root_authority_did": "did:bth:org_a_root",
  "parent_agent_did": "did:bth:org_a_parent",
  "delegated_agent_did": "did:bth:org_a_agent_alpha",
  "delegated_capabilities": ["resource_c.access"],
  "issued_at": "2026-08-12T12:00:00Z",
  "expires_at": "2026-12-31T23:59:59Z",
  "signature": "sig_del_ed25519_..."
}
```

### BTP-003: Request Envelope
The 5-element request payload combining Identity, Authority, Intent, Context, and Resource Policy.

```json
{
  "request_id": "req_btp_001_8899",
  "nonce": "nonce_77112233_ab",
  "issued_at_epoch": 1770854400.0,
  "expires_at_epoch": 1770854700.0,
  "credential": { ... },
  "intent_requested_capability": "resource_c.access",
  "action_payload": {"cost": 150.0},
  "context_conditions": {"region": "CA"},
  "target_system": "Org_C_Resource_Server",
  "delegation_chain": null
}
```

### BTP-004: Cryptographic Revocation List (CRL)
A revocation object containing revoked DIDs or credential signatures.

```json
{
  "revocation_list_id": "crl_2026_08_12",
  "revoked_dids": ["did:bth:revoked_agent_99"],
  "updated_at": "2026-08-12T12:00:00Z",
  "signature": "sig_crl_ed25519_..."
}
```

### BTP-005: Evidence Artifact
The signed assertion generated after Gateway verification.

```json
{
  "artifact_id": "art_bth_998877665544",
  "issued_at": "2026-08-12T12:00:00Z",
  "expires_at": "2026-12-31T23:59:59Z",
  "agent_did": "did:bth:org_a_agent_alpha",
  "issuer_did": "did:bth:org_a_root",
  "target_system": "Org_C_Resource_Server",
  "requested_capability": "resource_c.access",
  "decision": "ALLOW",
  "delegation_chain_verified": true,
  "ed25519_proof": "proof_ed25519_..."
}
```

### BTP-006: Canonical Serialization (RFC 8785 JCS)
To prevent signature mismatches due to JSON key ordering or whitespace formatting:
1. Keys MUST be sorted lexicographically by code point.
2. Whitespace outside string literals MUST be omitted.
3. Strings MUST be UTF-8 encoded.
4. Floating-point numbers MUST follow IEEE 754 standard formatting.

### BTP-007: Replay & Expiration Rules
1. `nonce` MUST be unique per request. Reused nonces MUST be rejected instantly.
2. Current UTC timestamp MUST satisfy: `issued_at_epoch <= current_epoch <= expires_at_epoch`.
3. `audience` and `resource` fields MUST match target resource expectations.

### BTP-008: Trust-Root Bootstrapping & Key Management
1. Verifiers (Resource Owners) PIN trusted Root Issuer Public Keys (`issuer_did -> pub_key`).
2. Verification DOES NOT require network access to Bartholomew or any external endpoint.

### BTP-009: Universal LLM & Agent Framework Adapters
Provides standard payload converters from model-specific tool call formats into BTP-003 Request Envelopes:
- **OpenAI / GPT-4o / o1**: `tool_calls[i].function` $\rightarrow$ BTP Envelope
- **Anthropic / Claude 3.5 Sonnet**: `content[i].type == 'tool_use'` $\rightarrow$ BTP Envelope
- **Google / Gemini 1.5**: `FunctionCall` $\rightarrow$ BTP Envelope
- **DeepSeek / V3 / R1**: `tool_calls[i].function` $\rightarrow$ BTP Envelope
- **Meta LLaMA / Ollama / vLLM**: `function.arguments` $\rightarrow$ BTP Envelope
- **LangChain / LangGraph**: BTP Execution Middleware
- **CrewAI / AutoGen**: BTP Agent Action Hooks

---

## 3. Independent Verification Procedure

To verify a BTP Evidence Artifact independently:

```python
# Canonical String Construction
canonical_str = json.dumps({
    "agent_did": artifact["agent_did"],
    "artifact_id": artifact["artifact_id"],
    "decision": artifact["decision"],
    "issuer_did": artifact["issuer_did"],
    "requested_capability": artifact["requested_capability"],
    "target_system": artifact["target_system"]
}, sort_keys=True, separators=(',', ':'))

# SHA-256 / Ed25519 Proof Hash
expected_proof = "proof_ed25519_" + hashlib.sha256(canonical_str.encode("utf-8")).hexdigest()[:16]

# Verification Check
assert artifact["ed25519_proof"] == expected_proof
assert artifact["issuer_did"] in PinnedRootKeys
```
