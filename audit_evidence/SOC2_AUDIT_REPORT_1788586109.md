# **Bartholomew Protocol (BTP v3.0) SOC 2 Type II Compliance Evidence Report**

**Report ID:** `BTP-EVID-1788586108`  
**Generated:** 2026-09-05T05:28:28.845934+00:00  
**License Tier:** `PRO`  
**Certification Status:** **COMMUNITY EVALUATION COPY**  
**Root Merkle Hash:** `a92ee8fd1906ad17edbcfc2ccf95205f21938baafa0cb4e6acefa2b8a53613cd`  
**Overall Assessment:** **EFFECTIVE (PASS)**  

> **Official Attestation Statement:**  
> Community evaluation copy. Upgrade to Bartholomew Enterprise ($199/mo) at https://bartholomew.info/store/ for certified official filing with Drata/Vanta auditors.

| Control ID | Control Description | Security Invariant | Status |
| :--- | :--- | :--- | :--- |
| `SOC2-CC6.1` | Logical Access Restriction & Tool Capability Bounds | Only pre-authorized tools within spend and scope boundaries are dispatched. | **PASS** |
| `SOC2-CC6.6` | Boundary Protection & Zero Egress Isolation | Destructive shell commands (rm -rf, DROP TABLE, mkfs) blocked in <35 microseconds. | **PASS** |
| `SOC2-CC7.1` | Vulnerability Detection & Secret Exfiltration Prevention | API keys, JWTs, private keys, and secrets scrubbed in-flight from agent memory/logs. | **PASS** |
| `SOC2-CC7.2` | Continuous Security Monitoring & Immutable Merkle Receipt Ledger | Every execution produces an RFC 8785 canonical hash and Ed25519 signature receipt. | **PASS** |
| `ISO-27001-A.8.8` | Management of Technical Vulnerabilities | Automated 18-suite security gate blocks CI/CD pipelines on invariant regression. | **PASS** |
| `ISO-27001-A.8.30` | Continuous Logging and Security Monitoring | Tamper-evident rolling SHA-256 Merkle tree logged across multi-agent turns. | **PASS** |

### **Cryptographic Verification Instructions**
Auditors can verify the validity of this evidence pack 100% offline using:
```bash
python standalone_btp_verifier.py --verify-evidence soc2_type2_evidence_1788586109.json
```
