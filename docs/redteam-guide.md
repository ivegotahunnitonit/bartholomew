# **BTP v2.2 External Scrutiny & Red-Team Evaluation Guide**
### **Status: Open Research Call &bull; Protocol Version: BTP/2.2 (Frozen)**
### **License: Public Specification (Open Standard) / BSL 1.1 Implementation Protection**

---

## **1. Invitation to Independent Cryptographers & Red Teams**

We officially transition the Bartholomew Trust Protocol (BTP v2.2) from **Internal Engineering Mode** into **External Scrutiny Mode**.

We invite external security researchers, cryptographers, and multi-agent architects to attack the protocol interface and attempt to break its security invariants.

---

## **2. Core Attack Surfaces for Red-Teaming**

| Target Attack Surface | Adversarial Goal | Evaluation Criterion |
| :--- | :--- | :--- |
| **1. Confused-Deputy & Cross-Recipient Replay** | Replay a valid attestation issued for Worker Agent A against Critical Node B. | The recipient context MUST be rejected via `target_recipient` mismatch. |
| **2. Semantic Policy Substitution** | Swap the evaluated policy ruleset without changing the candidate code. | The attestation MUST be rejected via `policy_hash` mismatch. |
| **3. Capability Scope Overreach** | Elevate capability permissions (e.g. from `FS_READ` to `ROOT_ADMIN`). | The verifier MUST catch that requested capabilities exceed allowed policy. |
| **4. Clock Skew & Pre-Issuance Exploits** | Submit future-dated tokens to bypass active revocation windows. | Verifier MUST reject tokens with `issued_at_unix > now + 60s`. |
| **5. Canonicalization Ambiguities (RFC 8785)** | Exploit floating point `-0.0`, exponential formatting, or Unicode surrogate pairs to generate hash collisions. | Python and Go verifiers MUST generate identical byte hashes. |
| **6. Multi-Authority Trust Store Manipulation** | Attempt to substitute an unpinned root authority key into the verification pipeline. | Verifier MUST enforce strict membership against `trusted_root_pubkeys`. |

---

## **3. Clean-Room Interoperability Verification**

To prove BTP is a genuine protocol rather than a vendor SDK, you can execute the clean-room bidirectional interoperability test:

```bash
# Run Bidirectional Clean-Room Interoperability Challenge
python tests/test_bidirectional_interop_challenge.py
```

* **Reference Implementation:** [`standalone_btp_verifier.py`](file:///c:/Users/User/.gemini/antigravity/scratch/autonomous-circularity-network/standalone_btp_verifier.py)
* **Go Reference Implementation:** [`btp_verifier.go`](file:///c:/Users/User/.gemini/antigravity/scratch/autonomous-circularity-network/btp_verifier.go)
* **Frozen Conformance Suite:** [`BTP_CONFORMANCE_SUITE.json`](file:///c:/Users/User/.gemini/antigravity/scratch/autonomous-circularity-network/BTP_CONFORMANCE_SUITE.json)

---

## **4. Vulnerability Disclosure & Coordination**

Report findings and proof-of-concept exploits directly to:
* **Contact:** `help@bartholomew.info` *(routes to `itsub@bartholomew.info`)*
* **PGP / Key Coordinates:** Pinned in [`THREAT_MODEL.md`](file:///c:/Users/User/.gemini/antigravity/scratch/autonomous-circularity-network/THREAT_MODEL.md).
* **Response Commitment:** Initial triage within 24 hours, remediation within 72 hours, public attribution upon request.

---
© 2026 Bartholomew AI & Contributors. Public Specification.
