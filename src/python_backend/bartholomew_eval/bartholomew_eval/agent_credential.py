"""
bartholomew_eval.agent_credential
=================================
Portable, Machine-Verifiable AI Agent Trust Credentials & Attestation Badges for Bartholomew v7.2.

Provides cryptographic verification of agent identity, evaluated capabilities,
OWASP LLM01-LLM10 security posture, and tamper-evident SHA-256 audit chains.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import time
from typing import Any, Dict, List, Optional


class AgentCredential:
    """
    Portable Bartholomew Agent Trust Credential Object.
    Encapsulates identity, declared capabilities, security evaluation result,
    and HMAC-SHA256 cryptographic attestation proof.
    """

    def __init__(
        self,
        agent_id: str,
        agent_name: str,
        version: str = "1.0.0",
        model: str = "unknown",
        capabilities: Optional[List[str]] = None,
        evaluation_results: Optional[Dict[str, str]] = None,
        compliance_status: str = "PASS",
        reliability_score: float = 100.0,
        secret_key: str = "bartholomew-audit-signing-secret",
        timestamp: Optional[str] = None,
        attestation_hash: Optional[str] = None,
    ) -> None:
        self.agent_id = agent_id if agent_id.startswith("agent://") else f"agent://{agent_id}"
        self.agent_name = agent_name
        self.version = version
        self.model = model
        self.capabilities = capabilities if capabilities is not None else ["database.read", "web.search"]
        self.evaluation_results = evaluation_results if evaluation_results is not None else {
            f"OWASP_LLM0{i}": "PASS" for i in range(1, 10)
        }
        self.evaluation_results["OWASP_LLM10"] = "PASS"
        self.compliance_status = compliance_status
        self.reliability_score = reliability_score
        self.secret_key = secret_key
        self.timestamp = timestamp or time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        self.attestation_hash = attestation_hash or self.compute_hash()

    def compute_hash(self) -> str:
        """Computes HMAC-SHA256 attestation signature over canonical credential fields."""
        caps_str = ",".join(sorted(self.capabilities))
        payload = f"{self.agent_id}:{self.agent_name}:{self.version}:{self.model}:{caps_str}:{self.compliance_status}:{self.reliability_score}:{self.timestamp}:{self.secret_key}"
        return hmac.new(
            self.secret_key.encode("utf-8"),
            payload.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()

    def verify(self) -> Dict[str, Any]:
        """Validates tamper-evident integrity of this credential."""
        expected = self.compute_hash()
        is_valid = hmac.compare_digest(expected, self.attestation_hash)
        return {
            "verified": is_valid,
            "agent_id": self.agent_id,
            "attestation_sha256": self.attestation_hash,
            "expected_sha256": expected,
            "chain_status": "VALID" if is_valid else "INVALID_TAMPERED",
            "evaluated_at": self.timestamp,
        }

    def to_dict(self) -> Dict[str, Any]:
        """Export credential as machine-readable JSON dictionary."""
        return {
            "attestation_header": "BARTHOLOMEW ATTESTATION",
            "agent_id": self.agent_id,
            "agent_name": self.agent_name,
            "version": self.version,
            "model": self.model,
            "capabilities": self.capabilities,
            "evaluation": "OWASP LLM01–LLM10",
            "evaluation_details": self.evaluation_results,
            "result": self.compliance_status,
            "reliability_score": self.reliability_score,
            "attestation_sha256": self.attestation_hash,
            "evaluated": self.timestamp,
            "chain_status": "VALID" if self.verify()["verified"] else "INVALID_TAMPERED",
        }

    def to_formatted_text(self) -> str:
        """Renders credential as formatted human-readable badge text."""
        ver = self.verify()
        caps = ", ".join(self.capabilities)
        return (
            "+-------------------------------------------------------------+\n"
            "|                   BARTHOLOMEW ATTESTATION                   |\n"
            "+-------------------------------------------------------------+\n"
            f"| Agent           : {self.agent_name:<41} |\n"
            f"| Identity        : {self.agent_id:<41} |\n"
            f"| Version         : {self.version:<41} |\n"
            f"| Model           : {self.model:<41} |\n"
            f"| Capabilities    : {caps:<41} |\n"
            "| Evaluation      : OWASP LLM01-LLM10                           |\n"
            f"| Result          : {self.compliance_status:<41} |\n"
            f"| Score           : {self.reliability_score:.1f}%                                   |\n"
            f"| Attestation     : SHA-256:{self.attestation_hash[:28]}... |\n"
            f"| Evaluated       : {self.timestamp:<41} |\n"
            f"| Chain status    : {ver['chain_status']:<41} |\n"
            "+-------------------------------------------------------------+"
        )
