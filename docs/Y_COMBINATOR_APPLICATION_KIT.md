# Y COMBINATOR (YC) APPLICATION MASTER KIT
### Bartholomew AI — Autonomous Agent Execution Gateway

**Founder**: Itsub Alemayehu (Solo Technical Founder & Chief Architect)  
**URL**: `https://bartholomew.info` | **GitHub**: `https://github.com/ivegotahunnitonit/bartholomew`  
**Demo Video / Repo Link**: `https://github.com/ivegotahunnitonit/bartholomew`  

---

## 1. Company Information

* **Company Name:** Bartholomew AI (Autonomous Circularity Labs)
* **Describe what your company does in 50 characters or less:**  
  *Sub-35µs in-process runtime guard for AI agents.*
* **Company URL:** `https://bartholomew.info`
* **Where will you be located?** San Francisco, CA / Remote

---

## 2. Founders & Equity

* **Founder Name:** Itsub Alemayehu
* **Role:** Founder & Chief Architect
* **Equity:** 100%
* **Background:** Systems architect and researcher in low-latency runtime security, formal verification, and cryptographic trust systems. Engineered the Bartholomew sub-35µs in-process AST gating engine, authored the formal Zenodo research specification, and scaled developer adoption to 4,500+ active users.

---

## 3. Product & Progress

### What is your company going to make?
> We make Bartholomew: the in-process execution gateway for autonomous AI agent swarms. 
>
> When developers deploy autonomous agents (CrewAI, LangGraph, AutoGen, OpenAI Agents SDK), they grant models access to tools: bash terminal, relational databases, cloud APIs, and payment rails. If an agent encounters untrusted data (like an email or web page), an indirect prompt injection can coerce the agent into running destructive shell commands (`rm -rf /`), dropping SQL tables, or leaking AWS credentials.
>
> Existing defenses use secondary "LLM-as-a-judge" models, which add 2,000ms of latency and double inference costs. Bartholomew runs directly inside the agent's process memory, evaluating policy invariants in under 35 microseconds (<0.035 ms)—making it 50,000× faster than LLM judges with zero external network dependencies. It also emits tamper-evident Ed25519 Merkle receipts and supports native L402 Lightning micropayments.

### How far along are you?
> We have a production-ready, benchmarked product with active developer traction:
> * **4,500+ Active Developers:**
>   * npm package (`btp-guard`): 1,673 weekly downloads.
>   * PyPI package (`btp-guard`): 1,836 monthly downloads across 16 published releases.
>   * Open VSX / Cursor Extension: 1,026 active installs (v5.4.15 published with official logo).
>   * GitHub: 834 unique developer cloners; 2,147 total git clones.
> * **2,879 automated tests passing** across CrewAI, LangChain, AutoGen, and OpenAI SDK.
> * **2,563 metered actions evaluated** in our production ledger.
> * 5-page formal research paper ready on Zenodo/arXiv proving our Three-Tier Composition Model via Rice's Theorem.
> * Live production endpoint running at `https://bartholomew.info`.

### How do you understand your users and how do they find you?
> AI engineers building multi-agent systems are terrified of agents running wild in production. They find us through GitHub, PyPI (`pip install btp-guard`), npm (`npm install btp-guard`), and the Cursor/VS Code marketplace. Our 1-line Python decorator (`@guard.protect`) and standard Model Context Protocol (MCP) server mean developers can secure their entire agent pipeline in less than 60 seconds without refactoring their architecture.

### Who are your competitors and why are you better?
> 1. **LLM Judges (LlamaGuard, NeMo Guardrails):** They take 1,500–3,000 ms per call and cost $0.01 per check. We run in-process in 24.8 microseconds (50,000× faster) with $0.00 marginal cost.
> 2. **Perimeter WAFs (Cloudflare):** They only see HTTP traffic at the network edge. They are completely blind to an agent executing local terminal bash commands or writing to local databases. We run inside the process.
> 3. **Legacy EDR (CrowdStrike, Datadog):** They look for binary malware signatures and HTTP 500s. They have zero understanding of JSON-RPC Model Context Protocol frames, spend loop recursion, or multi-agent delegation chains.

### How do you make money?
> We use a Developer-Led Product-Led Growth (PLG) model:
> * Free Open Source Core for individual developers to drive viral adoption.
> * Pro Workspaces at $49 to $499/month for cloud telemetry, Slack alerts, and team spend caps.
> * Enterprise Swarm Control Plane at $50,000 to $250,000 / year ACV for air-gapped on-premises / VPC Kubernetes deployments, continuous SOC 2 Type II compliance dossiers, multi-tenant governance, and 99.99% SLAs. Gross margins exceed 88%.

---

## 4. Why YC?

### Why do you want to join Y Combinator?
> YC is the epicenter of the autonomous agent revolution. Nearly every top-tier AI company in the upcoming batches (and in the YC alumni network) is building autonomous agents that need runtime execution guardrails. YC provides the ideal platform to make Bartholomew the default, industry-standard execution constitution for every autonomous AI company on Earth.
