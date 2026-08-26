# AWS CDK Bartholomew Invariant Guard Construct
==================================================
> Deploy sub-50µs Tier-0 deterministic invariant gates for Amazon Bedrock and autonomous AI agents in 5 lines of AWS CDK.

[![Construct Hub](https://img.shields.io/badge/Construct_Hub-aws--cdk--bartholomew--guard-orange)](https://constructs.dev)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![BTP Protocol](https://img.shields.io/badge/Protocol-BTP_v2.3-emerald)](https://bartholomew.info)

## Overview
`aws-cdk-bartholomew-guard` is an enterprise AWS CDK construct that deploys Bartholomew as a local **Tier-0 Fast Path Invariant Gate** for Amazon Bedrock agents, AWS Lambda extensions, and ECS Fargate security sidecars.

### Key Benefits for AWS Architects:
- **80% Cost Reduction**: Drops invalid, destructive, or high-entropy credential payloads locally on the agent host before hitting cloud guardrail token billing.
- **Sub-50µs Latency**: Evaluates polyglot AST invariants in <0.05 ms, eliminating the 1.5s network round-trip overhead of cloud-only guardrails.
- **FIPS 186-5 & SOC 2 Ready**: Produces RFC 8785 Ed25519 cryptographic execution receipts.

---

## Installation

### Python
```bash
pip install aws-cdk-bartholomew-guard
```

### TypeScript / Node
```bash
npm install @bartholomew/aws-cdk-guard
```

---

## Quickstart (Python CDK)

```python
from aws_cdk import Stack
from constructs import Construct
from aws_cdk_bartholomew import BartholomewGuardConfig

class ProductionBedrockAgentStack(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        # 5-Line Tier-0 Security Gate
        guard_config = BartholomewGuardConfig(
            spend_cap_usd=500.0,
            enable_ast_gate=True,
            enable_secret_masker=True,
            kms_key_arn="arn:aws:kms:us-east-1:123456789012:key/btp-root"
        )
```

---

## Documentation & White Paper
- **Architecture White Paper**: [Reducing AWS Bedrock Guardrail Costs by 80% with Tier-0 Gating](https://github.com/ivegotahunnitonit/bartholomew/blob/main/AWS_BEDROCK_TIER0_WHITE_PAPER.md)
- **Live Interactive Sandbox**: [https://bartholomew.info#sandbox](https://bartholomew.info#sandbox)
- **Core Repository**: [https://github.com/ivegotahunnitonit/bartholomew](https://github.com/ivegotahunnitonit/bartholomew)
