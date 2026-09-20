# BTP Universal Model & Execution Guards

BTP v5.4.10 operates natively at the execution boundary between frontier models, autonomous tools, and host operating systems:

- **Universal Model Guard**: [`src/universal_model_guard.py`](../src/universal_model_guard.py)
- **Model Context Protocol (MCP)**: [`npm_package/cli.js`](../npm_package/cli.js)
- **In-Process Python Guard**: `from btp_guard import secure_tool`
- **In-Process Node.js Guard**: `import { evaluateIntent } from 'btp-guard'`

Legacy framework-specific adapters (CrewAI, LangGraph, AutoGen, LlamaIndex) have been archived under `.archive/legacy_framework_adapters/`.
