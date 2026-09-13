# **BTP v2.2 External Challenge Package (FROZEN SPECIFICATION)**
### **Release Tag: `btp-v2.2-frozen` &bull; Date: August 20, 2026**
### **Classification: Open Protocol Specification & Red-Team Challenge**

---

## **1. Package Summary & Invitation to Attack**

This challenge package contains everything necessary for an independent cryptographer, security researcher, or multi-agent engineer to evaluate, implement, or attempt to break the **Bartholomew Trust Protocol (BTP v2.2)**.

> **Objective:** Attempt to falsify any of the 8 formal security invariants listed in the Claim Registry below under the defined threat model.

---

## **2. Formal Security Invariant & Claim Registry**

Researchers may submit proof-of-concept exploits targeting any of the following pre-registered invariant claims:

| Invariant ID | Claim Title | Formal Security Guarantee |
| :--- | :--- | :--- |
| **`BTP-SEC-001`** | **Payload Tamper-Resistance** | A candidate payload cannot be altered by even a single bit without invalidating the RFC 8785 SHA-256 hash and Ed25519 signature. |
| **`BTP-SEC-002`** | **Cross-Recipient Isolation** | An attestation issued for `target_recipient = B` cannot authorize execution by recipient `C` (Context Mismatch). |
| **`BTP-SEC-003`** | **Temporal Validity Enforcement** | An attestation evaluated at `timestamp > expires_at_unix` cannot be accepted (Strict TTL Expiry). |
| **`BTP-SEC-004`** | **Authority Pinning & Origin Authenticity** | An attestation signed by any key outside the recipient's configured `trusted_root_pubkeys` store cannot authorize an action. |
| **`BTP-SEC-005`** | **Capability Scope Containment** | Capability scope cannot be escalated beyond the recipient's allowed policy without invalidating the attestation. |
| **`BTP-SEC-006`** | **Semantic Policy Provenance** | An attestation's `policy_id` or `policy_hash` cannot be substituted or rolled back without invalidating the envelope signature. |
| **`BTP-SEC-007`** | **Nonce & Replay Immunity** | An attestation bearing a previously observed `nonce` within the active TTL window cannot be replayed. |
| **`BTP-SEC-008`** | **Offline Zero-Network Verifiability** | A conforming verifier can reach 100% deterministic authorization decisions without issuing external network calls. |

---

## **3. Included Specifications & Reference Artifacts**

| Component | File Link | Purpose |
| :--- | :--- | :--- |
| **Formal Protocol Spec** | [`BTP_PROTOCOL_SPECIFICATION.md`](file:///c:/Users/User/.gemini/antigravity/scratch/autonomous-circularity-network/BTP_PROTOCOL_SPECIFICATION.md) | Wire format, RFC 8785 canonicalization, and 10-step verification algorithm |
| **Formal Threat Model** | [`THREAT_MODEL.md`](file:///c:/Users/User/.gemini/antigravity/scratch/autonomous-circularity-network/THREAT_MODEL.md) | Adversarial capabilities, explicit guarantees, and non-goals |
| **Conformance Suite** | [`BTP_CONFORMANCE_SUITE.json`](file:///c:/Users/User/.gemini/antigravity/scratch/autonomous-circularity-network/BTP_CONFORMANCE_SUITE.json) | 12 positive and negative deterministic test vectors |
| **Python Clean-Room Verifier** | [`standalone_btp_verifier.py`](file:///c:/Users/User/.gemini/antigravity/scratch/autonomous-circularity-network/standalone_btp_verifier.py) | 35-line zero-SDK reference verifier |
| **Go Reference Verifier** | [`btp_verifier.go`](file:///c:/Users/User/.gemini/antigravity/scratch/autonomous-circularity-network/btp_verifier.go) | Native Go 1.26 independent verifier |
| **Red-Team Evaluation Guide** | [`EXTERNAL_SCRUTINY_AND_REDTEAM_GUIDE.md`](file:///c:/Users/User/.gemini/antigravity/scratch/autonomous-circularity-network/EXTERNAL_SCRUTINY_AND_REDTEAM_GUIDE.md) | Prioritized adversarial attack surfaces |
| **Reproducibility Kit** | [`REPRODUCIBILITY_KIT.md`](file:///c:/Users/User/.gemini/antigravity/scratch/autonomous-circularity-network/REPRODUCIBILITY_KIT.md) | Denominator accounting & 1-command reproduction steps |

---

## **4. Quick Verification (1-Command Conformance)**

```bash
# 1. Clone
git clone https://github.com/ivegotahunnitonit/bartholomew.git
cd bartholomew

# 2. Run Python Conformance Suite
python tests/test_conformance_suite.py

# 3. Run Bidirectional Clean-Room Interoperability Test
python tests/test_bidirectional_interop_challenge.py

# 4. Run Go Independent Verifier
go run btp_verifier.go
```

---

## **5. Vulnerability Disclosure**

Submit findings, proof-of-concept scripts, or protocol ambiguities to **`help@bartholomew.info`** *(routing to `itsub@bartholomew.info`)*. Reference the specific Invariant ID (e.g. `BTP-SEC-005 Broken`) in your submission for rapid triage and attribution.
