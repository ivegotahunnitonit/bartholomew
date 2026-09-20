# btp-guard

Deterministic In-Process Invariant Gate & Cryptographic Attestation Protocol for Autonomous AI Agents

[![npm version](https://img.shields.io/npm/v/btp-guard?style=flat-square&color=38bdf8)](https://www.npmjs.com/package/btp-guard)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg?style=flat-square)](https://github.com/bartholomew-ai/bartholomew/blob/main/LICENSE)
[![Security Policy](https://img.shields.io/badge/Security-Policy-green.svg?style=flat-square)](https://github.com/bartholomew-ai/bartholomew/blob/main/SECURITY.md)
[![Zero Dependencies](https://img.shields.io/badge/Dependencies-0-brightgreen.svg?style=flat-square)](https://www.npmjs.com/package/btp-guard)

---

## Overview

`btp-guard` is a sub-35 microsecond in-process deterministic invariant gate and cryptographic attestation engine implementing the Bartholomew Trust Protocol (BTP v5.4.12).

- **Smithery MCP Registry:** [https://smithery.ai/servers/itsubsolomon/calls_10k](https://smithery.ai/servers/itsubsolomon/calls_10k) (100/100 Verified)
- **Hosted MCP Endpoint:** `http://35.222.210.105:8080` (L402 Lightning Enabled)

It evaluates proposed AI agent tool actions (Bash executions, SQL queries, HTTP calls, MCP tool calls) in caller memory before execution, blocking catastrophic operations (`rm -rf`, `DROP TABLE`, destructive disk overwrites) and redacting high-entropy secrets (OpenAI, Anthropic, AWS, GitHub) while generating FIPS 186-5 Ed25519 verifiable receipts.

---

## Installation

```bash
npm install btp-guard
```

Zero external dependencies. Operates natively using Node.js built-in cryptography and standard primitives.

---

## Quickstart

### In-Process Intent Gate

```javascript
import { evaluateIntent, verifyReceipt } from 'btp-guard';

// 1. Evaluate tool call in caller memory (<35 us)
const result = evaluateIntent({
  agentId: 'worker-node-01',
  actionType: 'EXECUTE_QUERY',
  payload: { sql: 'SELECT * FROM users WHERE active = true;' }
});

console.log('Allowed:', result.allowed);
console.log('Latency:', result.latencyUs.toFixed(2), 'us');
console.log('Attestation Verdict:', result.verdict);
console.log('Signature:', result.signature);

// 2. Cryptographic receipt validation
const isValid = verifyReceipt(result);
console.log('Cryptographically Valid:', isValid);
```

### In-Flight Secret Redaction

```javascript
import { scrubSensitiveCredentials } from 'btp-guard';

const payload = {
  task: 'sync_data',
  auth: 'Bearer sk-proj-00000000000000000000000000000000',
  aws_key: 'AKIAIOSFODNN7EXAMPLE'
};

const { data, redactionCount } = scrubSensitiveCredentials(payload);
console.log('Redacted count:', redactionCount);
console.log('Sanitized payload:', data);
```

### RFC 8785 Canonicalization & Offline Verification

```javascript
import { verifyBtpReceipt, rfc8785Canonicalize } from 'btp-guard';

const canonBytes = rfc8785Canonicalize({ action: 'query', id: 42 });
console.log('Canonical UTF-8 Hex:', canonBytes.toString('hex'));
```

---

## CLI Usage

The package exposes `btp-guard` and `btp-mcp-proxy` binaries for terminal and pipeline inspection:

```bash
# Run local self-test and latency benchmark
npx btp-guard demo

# Initialize Model Context Protocol (MCP) desktop proxy
npx btp-guard init

# Scrub sensitive credentials from JSON input
npx btp-guard scrub payload.json
```

---

## Editions & Commercial Licensing

`btp-guard` is free and open-source for local execution. For engineering teams deploying multi-agent swarms in staging or production:

| Edition | Price | Ideal For | Core Capabilities |
|---|---|---|---|
| **Community (OSS)** | **Free Forever** | Solo Devs & Local Scripts | In-process sub-35µs AST gate, offline Ed25519 receipts, secret scrubber, MIT license |
| **Pro / Team** | **$49 / month** | Startups & Engineering Teams | [Cloud Telemetry Dashboard](https://bartholomew.info/cloud), instant Slack/Discord threat alerts, fleet API keys, policy sync |
| **Enterprise** | **$199 / month** | Scale-ups, FinTech & Healthcare | Continuous 1-click SOC 2 Type II evidence bundles, multi-tenant workspace isolation, dedicated CISO ledger, priority SLA |

👉 **Checkout & Upgrades:**
- **Pro Tier ($49/mo):** [Direct Stripe Checkout](https://buy.stripe.com/fZu28rbNz5TYcmAddK9R600)
- **Enterprise Tier ($199/mo):** [Direct Stripe Checkout](https://buy.stripe.com/fZu14ng3PgyC9ao2z69R601)
- **CLI Activation:** Run `npx btp-guard activate <key>` or `npx btp-guard pricing`
- **Pricing & Storefront:** [https://bartholomew.info/pricing](https://bartholomew.info/pricing)

---

## Enterprise Quality & Compliance

- **Zero External Dependencies**: Pure Node.js standard library. No supply chain exposure.
- **RFC 8785 Compliance**: Canonical JSON formatting ensures deterministic cryptographic hashing across polyglot implementations (TypeScript, Python, Go, Rust).
- **FIPS 186-5 Ed25519 Signatures**: Receipts are signed and verifiable offline without network round-trips.
- **Sub-35 Microsecond Latency**: In-memory inspection executes orders of magnitude faster than cloud-hosted proxy services.
- **Fail-Closed Architecture**: Any syntax corruption or policy mismatch rejects the candidate execution by default.

---

## Security & Verification

- **Security Policy**: [SECURITY.md](https://github.com/bartholomew-ai/bartholomew/blob/main/SECURITY.md)
- **Vulnerability Reporting**: security@bartholomew.info
- **Official Portal**: [https://bartholomew.info](https://bartholomew.info)
- **GitHub Repository**: [https://github.com/bartholomew-ai/bartholomew](https://github.com/bartholomew-ai/bartholomew)

---

## License

MIT License. Copyright (c) 2026 Bartholomew AI Contributors.
