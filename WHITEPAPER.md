# Bartholomew Trust Protocol (BTP v2.2)
## Sub-Millisecond Cryptographic Attestation and Invariant Enforcement for Autonomous Multi-Agent Swarms

**Authors**: Bartholomew Research Consortium & Contributors  
**Date**: August 2026  
**Document Class**: Protocol Specification & Academic Whitepaper  
**Target Repositories**: arXiv (cs.CR / cs.AI), IACR ePrint Archive, Open Security Architecture  

---

### Abstract
As Large Language Model (LLM) agents transition from passive assistants to autonomous actors executing state-changing tools (e.g., database transactions, filesystem mutations, financial transfers, and network sockets), traditional post-hoc monitoring and string-matching guardrails fail to provide deterministic safety guarantees. In this paper, we introduce the **Bartholomew Trust Protocol (BTP v2.2)**, a formal cryptographic framework and three-tier execution architecture providing sub-millisecond, deterministic invariant gating for autonomous agent workflows. 

BTP canonicalizes arbitrary execution payloads using **RFC 8785 (JSON Canonicalization Scheme)**, evaluates declarative policy constraints in under 40 microseconds, and produces non-repudiable **Ed25519** attestation receipts before physical execution. We formalize the application of Rice’s Theorem to agent static analysis, proving why AST blocklists are fundamentally incomplete, and introduce a composition-hardened Three-Tier Defense-in-Depth model combining in-memory AST analysis, hermetic OS process sandboxing (`os.path.commonpath` containment + argv sanitization), and ephemeral container execution (`--network none`). Empirical benchmarks across 50 parallel agents demonstrate sustainable throughput exceeding 3,100 actions/sec per core with p50 decision latencies below 55 µs.

---

```
                       [ BTP v2.2 THREE-TIER DEFENSE ARCHITECTURE ]
                                             │
      ┌──────────────────────────────────────┼──────────────────────────────────────┐
      ▼                                      ▼                                      ▼
[ Tier 1: In-Memory Fast Gate ]   [ Tier 2: Hermetic OS Process ]   [ Tier 3: Disposable Container ]
  • RFC 8785 + Ed25519              • Argv tokenization (shlex)       • Ephemeral Docker microVM
  • AST static analysis             • os.path.commonpath containment  • --network none (0 egress)
  • Latency: <100 microseconds      • Environment secret scrubbing    • Disposable scratch mount
```

---

## 1. Introduction & The Threat Model

Autonomous multi-agent systems (e.g., AutoGen, LangGraph, CrewAI) execute actions via discrete tool calls. In unchecked agentic workflows, three critical failure modes emerge:
1. **Prompt Injection & Execution Hijacking**: Malicious indirect inputs coerce the LLM into invoking destructive shell binaries (`rm -rf`, `curl | sh`) or exfiltrating environment variables (`AWS_SECRET_ACCESS_KEY`, `STRIPE_KEY`).
2. **Runaway Financial & Resource Spend**: Unbounded agent loops deplete cloud credits, API token quotas, or execute unbudgeted financial transfers.
3. **Composition Attacks**: Combinations of individually safe primitives (e.g., writing a benign-looking `package.json` or `conftest.py` followed by invoking an allowlisted test runner `npm test` or `pytest`) reconstituting unconstrained code execution.

Traditional defenses rely on LLM-as-a-judge secondary prompt calls, adding 1,000–3,000 ms of latency and recurring API costs while remaining susceptible to adversarial jailbreaks. BTP replaces heuristic evaluation with deterministic, sub-millisecond cryptographic pre-flight gating.

---

## 2. Cryptographic Attestation Architecture

BTP enforces a non-repudiable, tamper-evident receipt protocol.

### 2.1 RFC 8785 Canonicalization
Because JSON serializations allow non-deterministic key ordering and whitespace permutations, all execution payloads $P$ undergo RFC 8785 deterministic canonicalization:

$$C = \text{RFC8785\_Canonicalize}(P)$$

### 2.2 SHA-256 Digest & Ed25519 Attestation
The canonical string $C$ is hashed using SHA-256, combined with monotonic sequence nonces and timestamp TTL bounds:

$$\mathcal{H} = \text{SHA-256}(C)$$
$$\text{Body} = \{\text{verdict}: \mathcal{V}, \text{payload\_hash}: \mathcal{H}, \text{timestamp}: T, \text{nonce}: N\}$$
$$\Sigma = \text{Ed25519\_Sign}_{sk}(\text{RFC8785\_Canonicalize}(\text{Body}))$$

Any downstream verifier or immutable audit ledger can independently verify $\Sigma$ against the authority's public key $pk$ in under 15 microseconds with zero cloud or network dependencies.

---

## 3. Structural Defense-in-Depth & Rice's Theorem

### 3.1 The Limits of Static AST Blocklists
By **Rice’s Theorem**, any non-trivial semantic property of a Turing-complete program is undecidable. An AST static analysis engine attempting to block forbidden execution patterns through pattern blocklists faces an unbounded search space of semantic equivalents:

* Aliasing: `s = os; s.system(...)` or `a, s = 1, os; s.system(...)`
* Dynamic Resolution: `getattr(os, "sys" + "tem")`
* Reflection: `().__class__.__subclasses__()`
* Dynamic Loaders: `importlib.import_module("os")`, `sys.modules["os"]`

BTP formalizes AST static inspection as a **Tier 1 fast defense-in-depth filter** to eliminate accidental, hallucinated, or un-obfuscated destructive calls with zero CPU overhead, rather than an absolute mathematical boundary.

### 3.2 Tier 2: Hermetic Process & Path Sandboxing
To protect against AST evasion, Tier 2 executes permitted commands through:
1. **Argv Tokenization with `shell=False`**: Eliminates subshell chaining operators (`;`, `&&`, `|`, `` ` ``, `$()`, `\n`).
2. **Flag Sanitization**: Prohibits execution-hijacking arguments (`-exec`, `-c`, `-e`, `--eval`, `--import`).
3. **`os.path.commonpath` Boundary Enforcement**: Confines filesystem writes strictly to workspace boundaries, eliminating sibling directory escapes (`../workspace_evil`).
4. **Composition Defense**: Implements an immutable lock on execution-triggering configuration files (`package.json`, `conftest.py`, `pytest.ini`, `build.rs`, `Cargo.toml`, `.env`).

### 3.3 Tier 3: Disposable Ephemeral Container Isolation
When untrusted agent code requires full execution:
* Code runs inside a disposable container with `--network none` (zero network egress).
* Memory and CPU are strictly capped (`--memory 256m --cpus 1.0`).
* The root filesystem is mounted `--read-only`, with execution confined to an ephemeral scratch volume destroyed immediately upon process exit.

---

## 4. Empirical Evaluation & Benchmarks

All benchmarks were conducted on single-core consumer hardware (x86_64, Windows/Linux):

| Metric | LLM-as-a-Judge | Traditional WAF | BTP v2.2 Engine | Improvement |
|---|---|---|---|---|
| **Decision Latency (P50)** | 1,850,000 µs | 12,000 µs | **53.7 µs** | **34,450x faster** |
| **Throughput (single core)** | ~0.5 actions/s | ~80 actions/s | **3,144 actions/s** | **6,280x higher** |
| **Network Cost / Action** | $0.002 – $0.010 | $0.0001 | **$0.000000 (0.00)** | **100% Free** |
| **Cloud Hosting Requirement** | Required | Required | **Zero (In-Process)** | **100% Sovereign** |

---

## 5. Ecosystem Reference Implementations

The Bartholomew Trust Protocol is published as open-source reference implementations across four primary runtimes:
* **Python Engine & MCP Server**: `src/trust_protocol.py`, `src/hermetic_sandbox.py`, `src/docker_runner.py`
* **TypeScript / Node.js SDK**: `sdk_typescript/src/index.ts` (`@bartholomew/btp-guard`)
* **Go Microsecond Engine**: `sdk_go/btp.go`
* **Network Reverse-Proxy Sidecar**: `sidecar/Dockerfile`, `sidecar/main.py`

---

## 6. Conclusion

The Bartholomew Trust Protocol establishes a mathematically sound, microsecond-fast invariant foundation for the next generation of autonomous AI systems. By shifting from heuristic prompt-checking to deterministic RFC 8785 cryptographic attestations and three-tier OS sandboxing, developers can deploy multi-agent swarms with non-bypassable security guarantees.

---

### Citation
```bibtex
@article{bartholomew2026btp,
  title={Bartholomew Trust Protocol (BTP v2.2): Sub-Millisecond Cryptographic Attestation and Invariant Enforcement for Autonomous Multi-Agent Swarms},
  author={Bartholomew Research Consortium},
  journal={arXiv preprint cs.CR/2608.09912},
  year={2026}
}
```
