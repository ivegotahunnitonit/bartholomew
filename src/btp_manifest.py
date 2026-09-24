"""
Bartholomew (BTP v5.4.20) Machine-Readable Service Manifest
===========================================================
Generates programmatically inspectable manifests (.well-known/btp.json)
for autonomous agents to discover capabilities, policies, accepted protocols,
pricing meters, security invariants, and cryptographic evidence formats.
"""

import json
from typing import Dict, Any, Optional

MANIFEST_VERSION = "5.4.20"
BTP_PROTOCOL_VERSION = "5.4.20"

class BTPManifestBuilder:
    """Builder for machine-readable Bartholomew service manifests."""

    def __init__(self, endpoint: Optional[str] = None):
        self.endpoint = endpoint or "https://bartolomew-cloud-engine-322603900775.us-central1.run.app/api/v1/m2m/verify"

    def build(self) -> Dict[str, Any]:
        return {
            "$schema": "https://bartholomew.info/schemas/btp-manifest-v1.json",
            "manifest_version": MANIFEST_VERSION,
            "identity": {
                "name": "Bartholomew Trust Protocol",
                "role": "Agent Authorization & Execution Gate",
                "protocol_version": BTP_PROTOCOL_VERSION,
                "publisher": "Bartholomew AI",
                "website": "https://bartholomew.info",
                "mcp_endpoint": "http://35.222.210.105:8080"
            },
            "capabilities": [
                "transaction_authorization",
                "policy_enforcement",
                "signed_receipt_generation",
                "identity_verification",
                "micro_escrow_settlement",
                "ast_invariant_gating",
                "secret_scrubbing"
            ],
            "protocols": [
                "MCP (Model Context Protocol)",
                "A2A (Agent-to-Agent Protocol)",
                "WireGuard (Fast Cloud M2M)",
                "REST / JSON-RPC 2.0"
            ],
            "pricing": {
                "sovereign_enterprise": {
                    "tier": "SOVEREIGN_ENTERPRISE",
                    "price_usd_month": 0,
                    "description": "100% Unrestricted sovereign in-process execution gate and evaluation",
                    "unlimited_evaluations": True,
                    "features": [
                        "local_ast_gating",
                        "cloud_policy_sync",
                        "fleet_telemetry",
                        "threat_alerts",
                        "multi_tenant_isolation",
                        "compliance_evidence",
                        "keystone_passkeys",
                        "merkle_receipts"
                    ]
                },
                "meter": {
                    "event": "autonomous_action_allowed",
                    "unit_price_usd": 0.0,
                    "currency": "USD",
                    "policy": "sovereign_unrestricted"
                }
            },
            "security": {
                "gating": "sub-35us in-process AST and policy inspection",
                "rules": [
                    {"id": "BTP-AST-001", "name": "Destructive Command Injection", "action": "DENY"},
                    {"id": "BTP-SQL-001", "name": "Unauthorized SQL Mutation", "action": "DENY"},
                    {"id": "BTP-SEC-001", "name": "Credential & Secret Exfiltration", "action": "DENY + Scrub"},
                    {"id": "BTP-FIN-001", "name": "Session Spend Cap Exceeded", "action": "DENY"},
                    {"id": "BTP-LOOP-001", "name": "Infinite Retry Loop Detected", "action": "DENY"},
                    {"id": "BTP-INJ-001", "name": "Tool Argument Prompt Injection", "action": "DENY"}
                ]
            },
            "evidence": {
                "receipt_format": "SHA-256 Cryptographic Execution Receipt",
                "verification_mechanism": "Merkle Tree Proof & Ed25519 Signature",
                "auditability": "Machine-verifiable JSON ledger"
            },
            "limits": {
                "target_latency_us": 35.0,
                "default_spend_cap_usd": 100.0,
                "supported_frameworks": [
                    "Anthropic Claude",
                    "OpenAI / GPT-Astra",
                    "Google Gemini",
                    "xAI Grok",
                    "Meta Llama",
                    "AWS Bedrock",
                    "CrewAI",
                    "LangChain / LangGraph",
                    "AutoGen",
                    "LlamaIndex",
                    "Semantic Kernel"
                ]
            }
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.build(), indent=indent, sort_keys=False)


def generate_manifest() -> Dict[str, Any]:
    return BTPManifestBuilder().build()


if __name__ == "__main__":
    print(BTPManifestBuilder().to_json())
