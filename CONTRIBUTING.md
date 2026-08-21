# Contributing to Bartholomew & BTP

Thank you for your interest in contributing to the **Bartholomew Trust Protocol (BTP)**!

---

## 🛠️ Development Setup

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/ivegotahunnitonit/bartholomew.git
   cd bartholomew
   ```

2. **Install Python Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the Master CI/CD Test Suite**:
   ```bash
   python ci_security_gate.py
   ```

---

## 📐 Architecture Overview

* `src/trust_protocol.py`: Core RFC 8785 canonicalization & Ed25519 cryptographic attestation engine.
* `src/declarative_policy_engine.py`: Fast YAML/JSON policy-as-code parser.
* `src/ast_validator.py`: Deep Abstract Syntax Tree (AST) static analysis for Python code.
* `src/hermetic_sandbox.py`: Shlex-based command allowlists and `os.path.commonpath` filesystem containment.
* `src/docker_runner.py`: Ephemeral Docker container isolation runner.
* `mcp_server/`: Official Model Context Protocol (MCP) server for Claude Desktop and Cursor.
* `sidecar/`: Docker/Kubernetes network reverse-proxy gateway.

---

## 🧪 Testing Guidelines

Before submitting a pull request, ensure all tests pass:
```bash
python ci_security_gate.py
```

### Adding New Declarative Rules
1. Add your rule to `policies/default_security_policy.yaml`.
2. Validate with `python -m src.cli policy validate --file policies/default_security_policy.yaml`.
3. Add a test case in `test_declarative_policy_engine.py`.

---

## 📜 License
* Client SDKs: **Apache-2.0**
* Core Engine: **Business Source License (BSL 1.1)**
