# Changelog

All notable changes to **Bartholomew (BTP)** are documented here.
This project adheres to [Semantic Versioning](https://semver.org) and
[Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [5.4.20] - 2026-09-24

### Added
- **Multi-provider integration recipes** — Google Gemini ADK, Anthropic Claude, xAI Grok, OpenAI Swarms (`examples/multi_provider_agent_guard.py`)
- **Adversarial jailbreak fuzzer** — 150+ attack mutations covering shell injection, SQL DDL, Python AST obfuscation, Unicode homoglyphs, credential leaks, and ANSI escape attacks (`tests/test_adversarial_jailbreak_fuzzer.py`)
- **Provider performance benchmark** — 4,000-cycle latency/containment benchmark across 4 AI ecosystems with zero false negatives at ~7-8ms E2E turn latency (`benchmarks/provider_recipe_benchmarks.json`)
- **SLSA provenance workflow** — `.github/workflows/slsa-provenance.yml` for supply-chain attestations
- **Socket.dev security scan** — `.github/workflows/socket.yml` for dependency vulnerability detection
- **Bartholomew Liaison Fleet** (separate project) — 5 sovereign AI agents (Sales, Support, Onboarding, Growth, HR) with Cloud Run deployment

### Changed
- `src/polyglot_ast_validator.py` — Fixed SQL `TRUNCATE` regex and added hostile-pattern fallback for malformed Python syntax
- `src/trust_protocol.py` — Added `truncate` to forbidden patterns list
- `src/agent_protector.py` — Added support for wrapping raw callable functions (lambdas / plain functions without `invoke`/`run`)

### Fixed
- SQL `TRUNCATE TABLE` false negative — regex now correctly matches all `truncate ...` variants
- `protect_agent()` raised `AttributeError` when wrapping non-agent callables — now falls back to `__call__` interception

---

## [5.4.18] - 2026-09-22

### Added
- `btp-guard export --format otel` — OpenTelemetry ResourceSpans JSON export
- `btp-guard export --format datadog` — Datadog Logs JSON export
- `btp-guard export --format splunk` — Splunk HEC event export
- Interactive **Attack Simulator** in `site/index.html`
- **Frontier 2026 Leaderboard** with benchmark comparison vs Guardrails AI, LlamaGuard, Aegis, and custom prompt-based guards
- HuggingFace Spaces badge + one-line installer (shell, PowerShell, Homebrew)
- Claude Code + GitHub Actions Sentinel docs

### Changed
- `btp-guard bench` now outputs a coloured ASCII summary table with p50/p95/p99 latencies

---

## [5.4.0] - 2026-09-21 — *Initial Public Release*

### Added
- Core BTP engine: `btp_guard.Guard`, `evaluate_intent`, `protect_agent`
- PolyglotASTValidator: Python AST + regex-based SQL/shell guardrails
- Ed25519 cryptographic receipt generation (`TrustProtocol`)
- Python package (`btp-guard` on PyPI) + npm package (`btp-guard` on npm)
- VS Code extension (`bartholomew-btp-guard`)
- Homebrew formula
- GitHub Action (`action.yml`)
- MCP gate (`btp-guard mcp start`)
- Site: `site/index.html`, `site/docs.html`, `site/sitemap.xml`
- Research paper: `BTP_Research_Paper_v5.4.md`
- Security audit: `BTP_Security_Audit_Report_v5.4.18.md`

---

## [Unreleased]

### Planned
- `btp-guard scan --file <path>` — static analysis for Python/TS files
- Rust core hot-path for sub-10µs invariant (targeting p50 < 5µs)
- Native eBPF syscall monitor (Linux kernel 5.8+)
- Kotlin / JVM SDK
- SOC 2 Type II report (Q4 2026)
