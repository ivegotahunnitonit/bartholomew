# Bartholomew DevOps Gate — Autonomous AI Security & Attestation

[![Verified Bartholomew Seal](https://img.shields.io/badge/Verified_Bartholomew_Seal-Active-10b981.svg)](https://bartholomew.info)
[![Security Standard](https://img.shields.io/badge/Standard-BTP_v5.4.21-purple.svg)](https://bartholomew.info)

Autonomous AI agents (Cursor, Copilot, Claude, Devin, Cline) generate and modify code at scale. **Bartholomew DevOps Gate** is an automated pipeline task for Azure Pipelines that evaluates codebases for safety, scrubs unredacted credentials, prevents destructive execution invariants, and issues cryptographic **Verified Bartholomew Seals** on every build.

---

## Key Features

1. **Deterministic AST Invariant Firewall:** Blocks catastrophic execution patterns (destructive shell scripts, drop database without limits, raw fork bombs) before merging.
2. **Zero-Leak Secret Redaction:** Scrubs OpenAI, GitHub, AWS, and private keys in `<100µs`.
3. **Verified Bartholomew Seal Attestation:** Connects to the Bartholomew Authority Fleet to mint an immutable cryptographic record (`BTP-SEAL-v54-...`), publicly verifiable at `https://bartholomew.info/verify`.
4. **Zero External Runtime Dependencies:** Runs immediately on any Linux, Windows, or macOS Azure DevOps hosted agent.

---

## Azure Pipelines YAML Usage

Add this step to your `azure-pipelines.yml`:

```yaml
steps:
- task: BartholomewGateV1@1
  displayName: 'Run Bartholomew Agent Security Gate'
  inputs:
    scanPath: '$(Build.SourcesDirectory)'
    failOnViolation: true
    mintSeal: true
```

---

## Pipeline Output

When the gate passes, it issues a cryptographic seal and sets a pipeline output variable:
- `$(BartholomewSealId)`: E.g., `BTP-SEAL-v54-A780B84D290F`
- Verification URL: `https://bartholomew.info/verify?id=$(BartholomewSealId)`

---

## Institutional Inquiries & Enterprise Retainers

For dedicated authority nodes, defense compliance (ITB / PrairiesCan), or SOC 2 evidence packs:
- Website: [https://bartholomew.info](https://bartholomew.info)
- Verification Registry: [https://bartholomew.info/verify.html](https://bartholomew.info/verify.html)
