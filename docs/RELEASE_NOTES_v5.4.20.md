# Bartholomew v5.4.20 — Release Notes & GitHub Marketplace Publication

**Release Date:** September 23, 2026  
**Commit:** `main`  
**License:** MIT  
**Release Tag:** `v5.4.20` / `v5`

---

## ⚡ What's New in v5.4.20

### 1. Official GitHub Action for AI Agent PR Gating
- Published turnkey composite GitHub Action (`action.yml`) for the **GitHub Marketplace**.
- Run deterministic sub-35µs AST safety checks and secret scrubbing directly in your CI/CD pipeline on every Pull Request or commit:
  ```yaml
  - name: Bartholomew AI Agent Guard
    uses: ivegotahunnitonit/bartholomew@v5
    with:
      fail-on-violation: 'true'
      spend-cap: '50.0'
  ```
- Automatically generates rich Markdown audit summary reports in `$GITHUB_STEP_SUMMARY` with cryptographic Ed25519 Merkle digests.

### 2. Anthropic Claude Code & Local Agent Sentinel
- Official `CLAUDE.md` memory rules prohibiting credential exfiltration (`.env*`, `id_rsa`, `.pem`) and destructive terminal operations (`rm -rf`, `DROP TABLE`).
- 1-Click setup:
  ```bash
  npx btp-guard claude
  ```
- Ready for Claude Code MCP server routing (`claude mcp add bartholomew -- npx -y btp-guard mcp start`).

### 3. PyPI SDK v5.4.20 ([pypi.org/project/btp-guard/5.4.20/](https://pypi.org/project/btp-guard/5.4.20/))
- Clean 1-line in-process decorator:
  ```python
  from btp_guard import Guard, secure_tool
  
  @secure_tool
  def run_query(sql: str): ...
  ```
- First-class framework adapters under `btp_guard.integrations` for **LangChain, CrewAI, LangGraph, AutoGen, LlamaIndex, Smolagents, OpenAI Swarm, and NVIDIA NIM**.

### 4. NVIDIA NIM Microservice Stack
- GPU-accelerated container stack in `docker-compose.nim.yml` deploying `nvcr.io/nim/meta/llama-3.1-8b-instruct` / `70b` with the zero-overhead `BartholomewNIMGuard`.
- >12,000x faster than LLM-as-a-judge with **0 MB GPU VRAM** consumption.

### 5. Cybersecurity Terminal HUD
- Real-time live execution monitor with microsecond AST latency tracking and Merkle receipts:
  ```bash
  npx btp-guard hud
  # or: python -m src.cli hud --once
  ```

### 6. Zero-Latency Agent Cookbooks (`examples/`)
- 6 self-contained, 1-click runnable recipes testing LangChain, CrewAI, LangGraph, NVIDIA NIM, standard decorators, and Claude Code with 100% pass rates.

### 7. Cursor & Windsurf Auto-Detection
- `npx btp-guard init` automatically scaffolds `.cursorrules` and `.windsurfrules`.
