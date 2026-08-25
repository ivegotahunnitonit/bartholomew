# Y Combinator (YC) Application Dossier — Bartholomew
======================================================
Ready-to-use responses formatted specifically for the official Y Combinator application.

---

### 1. Company Name & Online Presence
* **Company Name**: Bartholomew (Autonomous Circularity Network)
* **Website**: https://bartholomew.info
* **GitHub Repository**: https://github.com/ivegotahunnitonit/bartholomew
* **Permanent Research DOI**: https://doi.org/10.5281/zenodo.22076536

---

### 2. What is your company going to make? (50 characters or less)
```text
Deterministic cryptographic execution gate for AI agents.
```

---

### 3. Describe what your company does in 50 words or less.
```text
Bartholomew is the open-source trust and execution gate for autonomous AI agents. Instead of probabilistic LLM guardrails that take 2 seconds and can be jailbroken, Bartholomew uses in-memory AST compilation and FIPS 186-5 Ed25519 cryptography to verify and gate agent tool calls in sub-50 microseconds with zero cloud dependencies.
```

---

### 4. What is new about what you make? Why will it succeed?
```text
Existing agent guardrails (NeMo, Bedrock Guardrails, Guardrails AI) use another LLM or regex strings. They add 2,000ms latency, cost money per token, and fail against basic code obfuscation.

Bartholomew treats AI security as compiler theory and hardware cryptography:
1. In-Memory AST Compilation: Statically parses proposed code across Python, TypeScript, Go, and Rust in <40 µs.
2. Deterministic Invariants: Intercepts 'rm -rf', 'DROP TABLE', unauthorized financial transfers, and runaway infinite retry loops (LDMU decay) before any OS syscall happens.
3. Cryptographic Attestations: Every approved action is stamped with an RFC 8785 Ed25519 digital signature in an immutable Merkle tree for enterprise SOC 2 compliance.
```

---

### 5. How far along are you? (Demo & Code)
```text
We have built a fully functional in-process engine passing 18/18 CI security test gates.

Anyone can run our 3-second live terminal test:
  git clone https://github.com/ivegotahunnitonit/bartholomew.git
  cd bartholomew
  python cli.py demo

We also support 1-click Claude Desktop/Cursor IDE integration ('python cli.py mcp install') and a 1-line Python SDK ('from btp_guard import Guard').
```

---

### 6. How will you make money?
```text
Open-core SaaS & Enterprise Infrastructure:
1. Free Developer Tier: Open-source core SDK and local MCP server for developers.
2. Bartholomew Enterprise Gate ($499 – $2,500/mo): Multi-agent fleet telemetry, decentralized multi-sig approval quorums, and automated SOC 2 audit evidence export for FinTech and Healthcare enterprises.
3. Cloud Marketplace (AWS / GCP): 1-click containerized deployment add-ons billed directly through customer cloud bills.
```

---

### 7. Why did you choose this idea? What is your domain expertise?
```text
Autonomous AI agents are currently trapped in chatboxes because enterprises are terrified of giving them root execution access to databases and terminal shells. We recognized that probabilistic LLMs need a deterministic, zero-latency cryptographic leash before they can achieve true economic autonomy.
```
