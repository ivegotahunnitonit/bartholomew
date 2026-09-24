---
title: Bartholomew AI Agent Attack Simulator
emoji: 🛡️
colorFrom: blue
colorTo: indigo
sdk: gradio
sdk_version: 4.44.0
app_file: app.py
pinned: false
license: mit
short_description: Zero-VRAM (<35us) deterministic firewall for AI agents
---

# 🛡️ Bartholomew: AI Agent Attack Simulator & Runtime Protection

Bartholomew is an open-source, deterministic firewall for AI agents, tool calls, and LLM code execution. 

Unlike heavy model-based guards (e.g. Llama Guard 3) that consume 16 GB of GPU VRAM and take 650ms per check, Bartholomew runs at the compiler AST level on CPU in under **35 microseconds** with **0 MB GPU memory**.

### 🔗 Links
- **GitHub:** [ivegotahunnitonit/bartholomew](https://github.com/ivegotahunnitonit/bartholomew)
- **PyPI:** [`pip install btp-guard`](https://pypi.org/project/btp-guard/)
- **Documentation & Web Lab:** [bartholomew.info](https://bartholomew.info)
