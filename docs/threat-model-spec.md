# **Bartholomew Trust Protocol (BTP) — Formal Threat Model & Security Boundaries**
### **Document Version: v2.1-PROD &bull; Classification: Public Security Specification**

---

## **1. Executive Summary & Core Philosophy**

> **"Trust isn't granted. Trust is demonstrated."**

The Bartholomew Trust Protocol (BTP) provides an **independent, neutral cryptographic verification and trust exchange mechanism** for autonomous agent interactions, CI/CD execution gates, and tool invocation boundaries.

BTP is explicitly designed to operate under zero-trust assumptions:
1. Agents are assumed to be potentially compromised, hallucinating, prompt-injected, or overprivileged.
2. Downstream execution environments (tools, databases, production clusters) do not rely on probabilistic LLM promises.
3. Every authorization decision is bound to an immutable **RFC 8785 Canonical JSON** representation and signed with **FIPS 186-5 Ed25519** digital signatures verifiable **100% offline with zero server dependencies**.

---

## **2. Threat Actors & Adversarial Capabilities**

| Threat Actor | Assumed Capabilities | Adversarial Objective |
| :--- | :--- | :--- |
| **Compromised / Prompt-Injected Agent** | Can emit arbitrary tool requests, hallucinate dependencies, or execute injected shell payloads (`$AWS_SECRET_KEY`, `rm -rf`). | Data exfiltration, privilege escalation, or production sabotage. |
| **Impersonator / Rogue Node** | Can generate ephemeral Ed25519 keypairs, mimic registered service IDs, and submit crafted attestations. | Bypass access controls and execute unauthorized actions. |
| **Man-in-the-Middle (MITM) / Proxy** | Can intercept and modify JSON payloads in transit between evaluation and execution (TOCTOU). | Substitute a malicious code payload for an already-approved attestation. |
| **Replay Attacker** | Can observe network traffic and re-submit expired or previously valid attestations. | Re-execute destructive actions or exhaust computing resources. |
| **Malicious / Compromised Authority Node** | Private signing key exposed or authority compromised. | Issue forged `ALLOW` attestations. |

---

## **3. Exact Protocol Guarantees vs. Non-Guarantees**

### **What BTP Cryptographically Guarantees:**
1. **Payload & Code Integrity (No Bait-and-Switch):** The executed payload exactly matches the byte-for-byte SHA-256 hash of the artifact evaluated in the hermetic sandbox.
2. **Replay & Expiration Impossibility:** Attestations cannot be replayed (cryptographic nonces) or used past their Time-To-Live expiration window (`expires_at_unix`).
3. **Authenticity & Non-Repudiation:** The attestation was signed by a pinned, authorized root key authority and cannot be forged without the Ed25519 private key.
4. **Sub-Microsecond Policy Interception (1.14 &mu;s):** Ring-0 and POSIX dangerous commands are blocked before process execution.
5. **Zero-Network Offline Independence:** Downstream tools can verify receipts with zero network calls to Bartholomew cloud servers.

### **What BTP Does NOT Guarantee (Explicit Non-Goals):**
1. **Does NOT Guarantee "Zero Vulnerabilities":** BTP proves that an action passed the configured test suite, trajectory policies, and AST boundaries. It cannot guarantee mathematical perfection against tests that were never written.
2. **Does NOT Replace Formal Certification:** BTP generates verifiable audit evidence mapped to SOC 2, NIST AI RMF, and ISO 42001 controls; it does not confer legal certification.

---

## **4. Key Lifecycle, Revocation & Disaster Recovery**

```

                        KEY LIFECYCLE & REVOCATION                      

 1. ROOT KEY PINNING: Public keys are pinned in downstream verifiers.   
 2. KEY ROTATION: Authority rolls keys via signed root transition cert. 
 3. CRL / REVOCATION: Compromised keys are published to the CRL table.  
 4. FAIL-CLOSED DEFAULT: If a key is revoked, all subsequent            
    attestations signed by that key are strictly REFUSED.               

```

---

## **5. Vulnerability Disclosure & Security Reporting**

We welcome independent security research and blind red-teaming against the BTP protocol interface:
* **Scope:** `src/trust_protocol.py`, `src/deploy_gate.py`, and public API endpoints.
* **Reporting:** Send proof-of-concept exploits to **`help@bartholomew.info`** *(routing to `itsub@bartholomew.info`)*.
* **Commitment:** We acknowledge within 24 hours, provide remediation within 72 hours, and publish transparent postmortems.

---
© 2026 Bartholomew AI & Contributors. All Rights Reserved.
