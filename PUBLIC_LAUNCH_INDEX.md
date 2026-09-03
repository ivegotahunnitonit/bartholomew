# **Bartholomew &bull; Public Launch &amp; Distribution Master Index**
### **Consolidated Entry Point for Developers, Framework Maintainers &amp; Red Teams**

---

## **1. Core Protocol Specifications, Papers & Proofs**
* **Technical Research Paper (v2.4):** [`paper_v2_4.md`](paper_v2_4.md) *(Transactional Micro-Rollbacks & Chained Merkle Graphs)*
* **Release Notes (v2.4.0):** [`RELEASE_NOTES_v2.4.0.md`](RELEASE_NOTES_v2.4.0.md)
* **Frozen Protocol RFC:** [`BTP_PROTOCOL_SPECIFICATION.md`](BTP_PROTOCOL_SPECIFICATION.md) *(Release Tag: `v2.4.0`)*
* **12-Vector Formal Conformance Suite:** [`BTP_CONFORMANCE_SUITE.json`](BTP_CONFORMANCE_SUITE.json)
* **Adversarial Invariant Challenge:** [`CHALLENGE_PACKAGE.md`](CHALLENGE_PACKAGE.md) *(Claims `BTP-SEC-001` through `008`)*
* **Clean-Room Interoperability Suite:** [`tests/test_bidirectional_interop_challenge.py`](tests/test_bidirectional_interop_challenge.py)

---

## **2. Transactional Runtime & MCP Proxy Engine (v2.4)**
* **Transparent MCP Security Proxy:** [`src/mcp_gateway.py`](src/mcp_gateway.py) *(Bi-directional secret scrubbing & turn receipt chaining)*
* **In-Memory Copy-on-Write Rollback Engine:** [`src/workspace_transaction.py`](src/workspace_transaction.py) *(<5µs instant state restoration)*
* **Scoped AST Invariant Visitor:** [`src/ast_validator.py`](src/ast_validator.py) *(Symbol-table based AST analysis)*
* **Interactive Terminal Showcase:** `python cli.py demo-v24` ([`src/demo_v24.py`](src/demo_v24.py))

---

## **3. Cross-Language Zero-Dependency Reference Verifiers**
* **Python Verifier (35 Lines):** [`standalone_btp_verifier.py`](standalone_btp_verifier.py)
* **Go Verifier (Compiled Daemon):** [`btp_verifier.go`](btp_verifier.go)
* **Node.js / TypeScript Verifier:** [`btp_verifier.js`](btp_verifier.js)

---

## **4. 1-Line Drop-in Framework Adapters & Desktop Integrations**
* **Claude Desktop & Cursor MCP Config:** [`setup_claude_desktop_mcp.py`](setup_claude_desktop_mcp.py)
* **LangChain / LangGraph Guard:** [`framework_adapters/langgraph/`](framework_adapters/langgraph/)
* **Microsoft AutoGen Interceptor:** [`framework_adapters/autogen/`](framework_adapters/autogen/)
* **CrewAI Task Guard:** [`framework_adapters/crewai/`](framework_adapters/crewai/)
* **Anthropic Model Context Protocol (MCP) Server:** [`mcp_server/`](mcp_server/)

---

## **5. Live Cloud & Machine Discovery Endpoints**
* **Live Google Cloud Run REST Gateway:** [`https://acn-fastapi-backend-322603900775.us-central1.run.app`](https://acn-fastapi-backend-322603900775.us-central1.run.app)
* **Live Interactive Command Center:** [`https://acn-fastapi-backend-322603900775.us-central1.run.app/dashboard`](https://acn-fastapi-backend-322603900775.us-central1.run.app/dashboard)
* **Production Web Hub:** [https://www.bartholomew.info/](https://www.bartholomew.info/)
* **Machine Discovery RFC Profile:** [https://www.bartholomew.info/.well-known/btp-configuration.json](https://www.bartholomew.info/.well-known/btp-configuration.json)

---

## **6. Public Distribution Packages**
* **Python Wheel (PyPI):** [`dist/btp_guard-2.4.0-py3-none-any.whl`](dist/btp_guard-2.4.0-py3-none-any.whl)
* **npm Tarball:** [`npm_package/btp-guard-2.4.0.tgz`](npm_package/btp-guard-2.4.0.tgz)
* **Red-Team Dossier:** [`RED_TEAM_TARGET_DOSSIER.md`](RED_TEAM_TARGET_DOSSIER.md)
