# Bartholomew BTP v2.2.0 Official Release Notes
**Release Tag**: `v2.2.0`  
**Release Date**: August 22, 2026  
**License**: Apache-2.0  
**Specification**: Bartholomew Trust Protocol (BTP) v2.2 Standards Track  

---

## Executive Summary
Bartholomew v2.2.0 provides dual-layer deterministic safety, sub-5 microsecond in-process semantic pre-flight invariant gating, ephemeral Docker container hardware isolation, and Merkle audit trail logging for autonomous AI agents (OpenAI, Anthropic, LangChain, Claude Desktop, and Cursor).

---

## Key Features & Enhancements

### 1. Dual-Layer Execution Defense
* **Layer 1 (Semantic Invariant Gate)**: In-process sub-5 microsecond AST parsing, spend limit enforcement, and Law of Diminishing Marginal Utility (LDMU) loop damping.
* **Layer 2 (Kernel Isolation Sandbox)**: Ephemeral Docker container runtime with hardware cgroup limits (512MB RAM cap, 1.0 CPU core throttle, read-only root filesystems, `--network none` isolation, and hermetic tokenized fallback).

### 2. Standardized Ecosystem Integrations
* **Model Context Protocol (MCP)**: Full stdio and SSE server implementation with official `smithery.yaml` specification for 1-click installation in Claude Desktop and Cursor.
* **Drop-in Client Wrappers**: 1-line Python decorator (`@guard.protect`) and Node.js middleware for zero-overhead runtime protection.

### 3. Master CI/CD Security Gate (18/18 Multi-Runtime Suites)
* 100% clean test execution across policy validation, LDMU engine, Merkle trees, MCP handshakes, cosmological/epistemic groundings, and container sandboxes.

### 4. Compliance & Audit Documentation
* **AICPA SOC 2 Type I/II**: Complete mapping across Trust Services Criteria (CC6.1-CC6.8, CC7.1-CC7.3, CC8.1, PI1.1-PI1.2).
* **ISO/IEC 27001:2022**: Comprehensive ISMS Annex A control alignment matrix.
* **OpenSSF Best Practices**: Passing, Silver, Gold, and Baseline 1-3 criteria registered.

---

## Verification & Integrity
* Audit Evidence Package: `dist/BARTHOLOMEW_SOC2_ISO27001_AUDIT_PACKAGE.zip`
* SHA-256 Checksums and Ed25519 signatures embedded in audit receipts.
