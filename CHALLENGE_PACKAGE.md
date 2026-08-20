# **BTP v2.2 External Challenge Package (FROZEN SPECIFICATION)**
### **Release Tag: `btp-v2.2-frozen` &bull; Date: August 20, 2026**
### **Classification: Open Protocol Specification & Red-Team Challenge**

---

## **1. Package Summary & Invitation to Attack**

This challenge package contains everything necessary for an independent cryptographer, security researcher, or multi-agent engineer to evaluate, implement, or attempt to break the **Bartholomew Trust Protocol (BTP v2.2)**.

> **Objective:** Attempt to falsify the BTP v2.2 security invariants or demonstrate an uncontained exploit under the threat model.

---

## **2. Included Specifications & Reference Artifacts**

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

## **3. Top Priority Attack Surfaces for Adversarial Review**

1. **Confused Deputy:** Can Agent A obtain an authorization for one action and trick Agent B into applying it to a different resource?
2. **Authority Compromise & Revocation:** Can a recipient safely revoke a compromised root key without breaking unrelated authorities?
3. **Capability Substitution:** Can an attacker transform `FS_WRITE_RESTRICTED` into unrestricted filesystem access?
4. **Policy Rollback:** Can an attestation referencing an older, weaker policy be replayed after a recipient moves to a newer policy?
5. **Version Downgrade:** Can an attacker force the verifier into accepting legacy protocol formats?
6. **Canonicalization Disagreement:** Can two independent implementations produce different interpretations of the same JSON while accepting the signature?

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

Submit findings, proof-of-concept scripts, or protocol ambiguities to **`help@bartholomew.info`** *(routing to `itsub@bartholomew.info`)*.
