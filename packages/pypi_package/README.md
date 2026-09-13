# **`btp-guard` &bull; BTP v2.2 Universal Agent Trust Guard**
### **Cryptographic Governance for LangGraph, AutoGen, CrewAI &amp; LlamaIndex**

`btp-guard` is the official Python SDK for the **Bartholomew Trust Protocol (BTP v2.2)**. It provides 100% offline, zero-network mathematical verification of autonomous agent trajectories, tool executions, and cross-framework delegations using RFC 8785 JSON Canonicalization (JCS) and FIPS 186-5 Ed25519 signatures.

---

## **Installation**

```bash
pip install btp-guard
```

---

## **Quickstart: 1-Line Tool Guard (LangGraph / LangChain)**

```python
from btp_guard import BTPGuard

# 1. Initialize guard with your organization's recognized root authorities
guard = BTPGuard(
    trusted_authorities=["<64-hex-char-ed25519-public-key>"],
    agent_id="Agent-Production-Cluster"
)

# 2. Decorate critical tools
@guard.wrap_tool
def execute_sql_patch(sql_query: str):
    # Automatically blocked if unauthenticated or payload tampered
    return db.execute(sql_query)
```

---

## **Quickstart: Microsoft AutoGen Interceptor**

```python
from btp_guard import BTPGuard

guard = BTPGuard(trusted_authorities=[ROOT_KEY])

# Drops or alerts on unattested high-privilege tool requests in transit
safe_message = guard.intercept_autogen_message(inbound_packet)
```

---

## **Quickstart: Standalone Offline Verification (Zero-SDK)**

```python
from btp_guard import verify_btp_receipt

ok, msg = verify_btp_receipt(
    receipt_json_str=inbound_packet,
    candidate_payload={"file": "worker.py", "patch": "fix()"},
    trusted_root_pubkeys=[ROOT_KEY],
    expected_recipient_context="Agent-Production-Cluster"
)

if not ok:
    raise PermissionError(f"Attestation rejected: {msg}")
```

---

## **Specification & Challenge Package**
* **Frozen Protocol Spec:** [BTP_PROTOCOL_SPECIFICATION.md](https://github.com/ivegotahunnitonit/bartholomew/blob/main/BTP_PROTOCOL_SPECIFICATION.md)
* **8-Invariant Red-Team Challenge:** [CHALLENGE_PACKAGE.md](https://github.com/ivegotahunnitonit/bartholomew/blob/main/CHALLENGE_PACKAGE.md)
* **Live Interactive Simulator:** [https://app.bartholomew.info/simulator](https://app.bartholomew.info/simulator)
