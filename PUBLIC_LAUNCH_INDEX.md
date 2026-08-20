# **Bartholomew &bull; Public Launch &amp; Distribution Master Index**
### **Consolidated Entry Point for Developers, Framework Maintainers &amp; Red Teams**

---

## **1. Core Protocol Specifications & Proofs**
* **Frozen Protocol RFC:** [`BTP_PROTOCOL_SPECIFICATION.md`](BTP_PROTOCOL_SPECIFICATION.md) *(Release Tag: `btp-v2.2-frozen`)*
* **12-Vector Formal Conformance Suite:** [`BTP_CONFORMANCE_SUITE.json`](BTP_CONFORMANCE_SUITE.json)
* **Adversarial Invariant Challenge:** [`CHALLENGE_PACKAGE.md`](CHALLENGE_PACKAGE.md) *(Claims `BTP-SEC-001` through `008`)*
* **Clean-Room Interoperability Suite:** [`tests/test_bidirectional_interop_challenge.py`](tests/test_bidirectional_interop_challenge.py)

---

## **2. Cross-Language Zero-Dependency Reference Verifiers**
* **Python Verifier (35 Lines):** [`standalone_btp_verifier.py`](standalone_btp_verifier.py)
* **Go Verifier (Compiled Daemon):** [`btp_verifier.go`](btp_verifier.go)
* **Node.js / TypeScript Verifier:** [`btp_verifier.js`](btp_verifier.js)

---

## **3. 1-Line Drop-in Framework Adapters**
* **LangChain / LangGraph Guard:** [`framework_adapters/langgraph/`](framework_adapters/langgraph/)
* **Microsoft AutoGen Interceptor:** [`framework_adapters/autogen/`](framework_adapters/autogen/)
* **CrewAI Task Guard:** [`framework_adapters/crewai/`](framework_adapters/crewai/)
* **Anthropic Model Context Protocol (MCP) Server:** [`mcp_server/`](mcp_server/)

---

## **4. Live Cloud & Machine Discovery Endpoints**
* **Production Web Hub:** [https://www.bartholomew.info/](https://www.bartholomew.info/)
* **Interactive Side-by-Side Simulator:** [https://app.bartholomew.info/simulator](https://app.bartholomew.info/simulator)
* **Machine Discovery RFC Profile:** [https://www.bartholomew.info/.well-known/btp-configuration.json](https://www.bartholomew.info/.well-known/btp-configuration.json)
* **Live Google Cloud Run REST Gateway:** `https://acn-backend-444129982305.us-central1.run.app`

---

## **5. Public Launch & Red-Team Kits**
* **Show HN & Reddit Launch Kit:** [`SHOW_HN_AND_COMMUNITY_DISTRIBUTION.md`](SHOW_HN_AND_COMMUNITY_DISTRIBUTION.md)
* **Adversarial Red-Team Target Dossier:** [`RED_TEAM_TARGET_DOSSIER.md`](RED_TEAM_TARGET_DOSSIER.md)
* **Staged Framework PR Envelopes:** [`generated_evidence_artifacts/framework_prs/`](generated_evidence_artifacts/framework_prs/)
