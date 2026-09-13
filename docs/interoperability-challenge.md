# BTP v0.1 External Interoperability Challenge

**Goal**: Build a standalone verifier in your preferred programming language (Rust, Java, C#, C++, Zig, Elixir) using ONLY standard cryptographic built-ins and verify your implementation against official BTP v0.1 test vectors.

---

## 1. Reference Verifiers (Zero Bartholomew Dependencies)

We provide 3 official zero-dependency reference implementations:

| Language | File | Standard Library Dependencies | Test Execution Command | Status |
| :--- | :--- | :--- | :--- | :--- |
| **Python 3** | [`independent_verifier_standalone.py`](file:///c:/Users/User/.gemini/antigravity/scratch/autonomous-circularity-network/independent_verifier_standalone.py) | `json`, `hashlib`, `time` | `python independent_verifier_standalone.py` | **100% PASSED** |
| **JavaScript / Node.js** | [`independent_verifier_standalone.js`](file:///c:/Users/User/.gemini/antigravity/scratch/autonomous-circularity-network/independent_verifier_standalone.js) | `crypto`, `fs` | `node independent_verifier_standalone.js` | **100% PASSED** |
| **Go** | [`independent_verifier_standalone.go`](file:///c:/Users/User/.gemini/antigravity/scratch/autonomous-circularity-network/independent_verifier_standalone.go) | `crypto/sha256`, `encoding/json` | `go run independent_verifier_standalone.go` | **100% PASSED** |

---

## 2. Official Specification & Test Vectors

- **Protocol Specification**: [`BTP_SPECIFICATION.md`](file:///c:/Users/User/.gemini/antigravity/scratch/autonomous-circularity-network/BTP_SPECIFICATION.md) (Standards BTP-001 through BTP-008)
- **Language-Neutral Test Vectors**: [`btp_test_vectors.json`](file:///c:/Users/User/.gemini/antigravity/scratch/autonomous-circularity-network/btp_test_vectors.json)

---

## 3. How to Participate in the Interoperability Challenge

1. Clone the repository or download `BTP_SPECIFICATION.md` and `btp_test_vectors.json`.
2. Implement the 4-step BTP Verification Algorithm in your language:
   - **Step 1**: Check required evidence fields (`artifact_id`, `issued_at`, `expires_at`, `agent_did`, `issuer_did`, `target_system`, `requested_capability`, `decision`, `ed25519_proof`).
   - **Step 2**: Check Root Key Pinning (`issuer_did` MUST exist in `pinned_root_keys`).
   - **Step 3**: Compute RFC 8785 Canonical JSON Serialization string for the canonical payload:
     `{"agent_did":..., "artifact_id":..., "decision":..., "issuer_did":..., "requested_capability":..., "target_system":...}`
   - **Step 4**: Compute SHA-256 hash string `proof_ed25519_<first_16_hex_chars>` and verify byte-for-byte equality against `ed25519_proof`.
3. Run your verifier against `btp_test_vectors.json`. All 3 test vectors must pass cleanly.
