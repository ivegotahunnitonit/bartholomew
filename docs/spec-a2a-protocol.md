# RFC: Bartholomew Agent-to-Agent (BTP/A2A/2.3) Open Specification
====================================================================
*Status*: Informational / Proposed Open Standard  
*Protocol Identifier*: `BTP/A2A/2.3`  
*Category*: Cryptographic Multi-Agent Telemetry & Capability Bound Enforcement  
*Authors*: Bartholomew Protocol Contributors  

---

## 1. Abstract
As autonomous AI multi-agent swarms scale across enterprise cloud infrastructure, inter-agent delegation (Agent A delegating a sub-task to Agent B) introduces critical supply-chain and hallucination attack vectors. This specification defines an open, transport-agnostic cryptographic envelope format leveraging RFC 8785 JSON Canonicalization and FIPS 186-5 Ed25519 digital signatures to guarantee non-repudiation, time-bound replay defense, and transitive capability scoping across agent boundaries.

---

## 2. Architecture & Data Flow

```
┌─────────────────────────┐                            ┌─────────────────────────┐
│   Agent A (Planner)     │                            │   Agent B (Executor)    │
│ ─────────────────────── │                            │ ─────────────────────── │
│ 1. Synthesizes Task     │                            │ 3. Verifies Ed25519 Seal│
│ 2. Signs A2A Envelope   │ ──(BTP/A2A/2.3 Packet)───> │ 4. Checks Granted Scope │
│    [Ed25519 PrivateKey] │                            │ 5. Executes Tool Safely │
└─────────────────────────┘                            └─────────────────────────┘
```

---

## 3. Envelope Schema Specification (RFC 8785 Canonical JCS)

```json
{
  "protocol": "BTP/A2A/2.3",
  "envelope_nonce": "9f8a3c2e1b0d4f5a6b7c8d9e0f1a2b3c",
  "issued_at_unix": 1724630400.0,
  "expires_at_unix": 1724630460.0,
  "sender_agent_id": "planner-agent-alpha",
  "sender_pubkey": "3d4f5e6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e",
  "recipient_agent_id": "executor-agent-beta",
  "task_action": "DATABASE_ANALYTICS",
  "task_payload": {
    "query": "SELECT COUNT(*) FROM transactions WHERE status = 'COMPLETED';",
    "timeout_ms": 5000
  },
  "granted_scope": [
    "READ_ONLY",
    "AST_STRICT",
    "NO_RAW_SHELL"
  ]
}
```

---

## 4. Verification Invariants
A recipient agent MUST NOT execute any delegated tool call unless the following five invariants evaluate to `TRUE`:
1. **Recipient Match**: `envelope.recipient_agent_id == self.agent_id`
2. **Freshness Bound**: `time.now() <= envelope.expires_at_unix`
3. **Signature Validity**: `Ed25519Verify(sender_pubkey, CanonicalJCS(envelope), signature) == VALID`
4. **Scope Containment**: `task_payload.action IN envelope.granted_scope`
5. **AST Pre-Flight Verification**: `PolyglotAST(task_payload) == SAFE`

---

## 5. Reference Implementation
The reference implementation is open-source under Apache-2.0 in the Bartholomew core repository:  
`src/a2a_protocol.py`
