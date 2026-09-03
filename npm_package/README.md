<p align="center">
  <img src="https://bartholomew.info/bartholomew_logo_4k.png" width="140" alt="Bartholomew Logo" />
</p>

<h1 align="center">btp-guard</h1>

<p align="center">
  <strong>Sub-50 µs In-Memory Deterministic Invariant Guard & Cryptographic Attestation Protocol for Autonomous AI Agents</strong>
</p>

<p align="center">
  <a href="https://bartholomew.info"><img src="https://img.shields.io/badge/Protocol-BTP%20v2.3-10b981?style=flat-square" alt="BTP Version" /></a>
  <a href="https://www.npmjs.com/package/btp-guard"><img src="https://img.shields.io/npm/v/btp-guard?style=flat-square&color=38bdf8" alt="npm version" /></a>
  <a href="https://github.com/ivegotahunnitonit/bartholomew/blob/main/LICENSE.md"><img src="https://img.shields.io/badge/License-MIT-blue.svg?style=flat-square" alt="License" /></a>
</p>

---

##  What is Bartholomew?

**Bartholomew** is a sub-50 microsecond in-memory deterministic invariant gate and cryptographic attestation protocol (BTP v2.3). It evaluates proposed AI agent tool actions (Bash commands, SQL queries, HTTP calls) in caller memory before execution, preventing catastrophic commands (`rm -rf`, `DROP TABLE`) and high-entropy secret leaks with FIPS 186-5 Ed25519 verifiable receipts.

---

##  Installation

```bash
npm install btp-guard
```

---

##  Quickstart

```typescript
import { evaluateIntent, verifyReceipt } from '@bartholomew/guard';

// 1. Evaluate tool call in caller memory (<50 µs)
const result = evaluateIntent({
  agentId: 'worker-node-01',
  actionType: 'EXECUTE_QUERY',
  payload: { sql: 'SELECT * FROM users WHERE active = true;' }
});

console.log(`Allowed: ${result.allowed} | Latency: ${result.latencyUs} µs`);
console.log(`Ed25519 Signature: ${result.signature}`);

// 2. Verify receipt offline with zero dependencies
const isValid = verifyReceipt(result);
console.log(`Cryptographically Valid: ${isValid}`);
```

---

##  Enterprise Security Invariants
* **Zero-Escape Polyglot AST Engine**: Mathematical pre-flight inspection for Python, TypeScript, SQL, and POSIX shell.
* **Secret Vault Masking**: In-flight redaction of OpenAI, Anthropic, GitHub, and AWS credentials.
* **RFC 8785 Canonical JCS**: Deterministic JSON hashing paired with Ed25519 nonced receipts.

---

##  Resources
* **Website & Interactive Sandbox**: [https://bartholomew.info](https://bartholomew.info)
* **GitHub Repository**: [https://github.com/ivegotahunnitonit/bartholomew](https://github.com/ivegotahunnitonit/bartholomew)
* **AWS Bedrock White Paper**: [AWS_BEDROCK_TIER0_WHITE_PAPER.md](https://github.com/ivegotahunnitonit/bartholomew/blob/main/AWS_BEDROCK_TIER0_WHITE_PAPER.md)
