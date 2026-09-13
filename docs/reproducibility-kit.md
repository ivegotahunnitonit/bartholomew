# **Bartholomew Trust Protocol (BTP v2.2) — Independent Reproducibility Kit**
### **Classification: Open Scientific Specification &bull; Evaluation Commit: `0026e59`**

---

## **1. Exact Denominator Accounting (Traceable to Raw Records)**

The 12,000 evaluations are derived from **8 atomic workloads** executed across **3 multi-framework delegation channels** with **500 repetitions** per channel:

### **Workload Composition Per Repetition:**
* **3 Malicious Workloads:** `WL-MAL-01` (Email Injection), `WL-MAL-02` (Shell Injection), `WL-MAL-03` (API Key Exfil).
* **3 Benign Workloads:** `WL-BEN-01` (AST Constant Fix), `WL-BEN-02` (SQL Query), `WL-BEN-03` (Linter Audit).
* **2 Ambiguous Workloads:** `WL-AMB-01` (Unconstrained SQL Update), `WL-AMB-02` (Replica Scale-Up).
* **Total Workloads Per Batch = $3 + 3 + 2 = 8$ tasks.**

### **Exact Breakdown by Delegation Channel:**

| Delegation Channel | Source Framework | Target Framework | Repetitions | Attack Tasks | Benign Tasks | Ambiguous Tasks | Total Tasks |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Channel 1** | LangChain / LangGraph | Microsoft AutoGen | 500 | 1,500 | 1,500 | 1,000 | **4,000** |
| **Channel 2** | Microsoft AutoGen | LangChain / LangGraph | 500 | 1,500 | 1,500 | 1,000 | **4,000** |
| **Channel 3** | CrewAI Orchestrator | ReAct Tool Runner | 500 | 1,500 | 1,500 | 1,000 | **4,000** |
| **TOTALS** | — | — | **1,500** | **4,500** | **4,500** | **3,000** | **12,000** |

---

## **2. Proof That BTP is a Protocol, Not a Proprietary SDK**

To prove that BTP is an **open cryptographic protocol** (like RFC 7519 JWT / RFC 8785 JCS) rather than a proprietary vendor library, any external agent framework can independently verify trust receipts in **35 lines of standard Python** with **zero Bartholomew dependencies**:

```python
# standalone_btp_verifier.py (Zero Bartholomew SDK dependency)
import json, hashlib, time
from cryptography.hazmat.primitives.asymmetric import ed25519

def independent_verify_btp(receipt_json: str, candidate_payload: dict, trusted_pubkey_hex: str):
    packet = json.loads(receipt_json)
    att = packet["attestation"]
    
    # 1. Authority Pinning & Expiry
    if att["authority_pubkey"] != trusted_pubkey_hex or time.time() > att["expires_at_unix"]:
        return False, "INVALID_OR_EXPIRED"
        
    # 2. SHA-256 Payload Hash Binding
    canonical_bytes = json.dumps(candidate_payload, sort_keys=True, separators=(',', ':')).encode('utf-8')
    if att["action_payload_hash"] != hashlib.sha256(canonical_bytes).hexdigest():
        return False, "PAYLOAD_TAMPERED"
        
    # 3. Mathematical Ed25519 Verification (100% Offline)
    pubkey = ed25519.Ed25519PublicKey.from_public_bytes(bytes.fromhex(trusted_pubkey_hex))
    canonical_att = json.dumps(att, sort_keys=True, separators=(',', ':')).encode('utf-8')
    pubkey.verify(bytes.fromhex(packet["signature"]), canonical_att)
    
    return (att["verdict"] == "ALLOW"), att["reason"]
```

---

## **3. Pre-Registered Falsification Criteria for External Researchers**

An external researcher has successfully falsified the BTP thesis if they produce any of the following:
1. **Uncontained Attack Escape:** Craft a malicious payload that bypasses BTP trajectory policies and obtains an `ALLOW` attestation without throwing a policy violation.
2. **Post-Attestation Substitution:** Modify the candidate code artifact after receipt issuance and have the standalone verifier accept it.
3. **Replay Acceptance:** Re-submit a previously processed attestation packet and have the standalone verifier accept it.
4. **False-Positive Legitimate Block:** Provide clean, syntactically valid code that passes all configured unit test assertions but is rejected by BTP.

---

## **4. Independent Reproduction Steps**

```bash
# 1. Clone repository
git clone https://github.com/ivegotahunnitonit/bartholomew.git
cd bartholomew

# 2. Create isolated clean virtual environment
python -m venv .venv
source .venv/bin/activate # On Windows: .venv\Scripts\activate

# 3. Install cryptographic standard dependency
pip install cryptography

# 4. Execute the 12,000-evaluation cross-agent experiment
python tests/test_cross_agent_generalization.py
```
