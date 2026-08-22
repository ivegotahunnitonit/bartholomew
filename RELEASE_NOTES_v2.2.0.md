# Bartholomew Trust Protocol (BTP v2.2.0) - Official Release Notes

**Release**: `v2.2.0`  
**Date**: August 2026  
**License**: Apache-2.0 (SDKs) / Business Source License (BSL 1.1) (Core Engine)  
**Repository**: [github.com/ivegotahunnitonit/bartholomew](https://github.com/ivegotahunnitonit/bartholomew)

---

## Highlights & New Features

### 1. Three-Tier Defense-in-Depth Architecture
* **Tier 1 (In-Memory Microsecond Gate)**:
  - RFC 8785 (JCS) deterministic canonicalization + Ed25519 cryptographic receipts.
  - Compiler-grade AST static analysis (`src/ast_validator.py`) with symbol resolution, alias tracking (`s = os`, `a, s = 1, os`), constant-folding string evaluation, and dunder reflection blocking.
* **Tier 2 (Hermetic Process & Path Sandbox)**:
  - `src/hermetic_sandbox.py` using `shlex.split` argv parsing with `shell=False`.
  - Directory boundary containment via `os.path.commonpath`.
  - Composition attack defenses locking execution-triggering configs (`package.json`, `conftest.py`, `build.rs`).
* **Tier 3 (Disposable Docker Container Runner)**:
  - `src/docker_runner.py` executing untrusted scripts inside disposable containers with `--network none` and unprivileged execution.

### 2. Multi-Runtime SDKs (100% Offline Local-First)
* **Python**: `pip install bartholomew-eval` & `btp_guard`
* **TypeScript / Node.js**: `@bartholomew/btp-guard` (npm)
* **Go**: `github.com/ivegotahunnitonit/bartholomew/pkg/btp`
* **MCP Server**: Official Model Context Protocol server for Claude Desktop and Cursor.

### 3. Developer Tools & Observability
* **CLI Quickstart**: `bartholomew init` and `bartholomew keygen` for 1-command project setup.
* **Real-Time Terminal Monitor (TUI)**: `python src/tui_monitor.py` for live terminal inspection.
* **Prometheus Metrics Exporter**: HTTP `/metrics` endpoint on port 9100 for Grafana and Datadog.
* **GitHub Action**: Drop-in `.github/workflows/` step for automated CI/CD security gating.
* **Web Dashboard**: Interactive Visual Policy Editor and real-time Attestation Inspector.

### 4. 10,000-Action Invariant Fuzzing Verification
* Evaluated 10,000 randomized attack permutations in **0.347 seconds**.
* **28,799 actions/sec** sustained single-core throughput.
* **35.5 µs P50 latency** (<0.1 ms P99).
* **100.0% exploit interception** with 0 false positives.

---

## Quickstart

```bash
# 1. Initialize BTP in your repository
python -m src.cli init

# 2. Run the live agent pilot demonstrator
python launch_live_agent_guard.py

# 3. Start real-time terminal monitoring
python src/tui_monitor.py
```
