"""
Bartholomew Live Public Agent Gateway (M2M Node)
================================================
Production-ready FastAPI gateway for autonomous agent-to-agent (M2M) communication:
  - `POST /v1/evaluate`: Sub-50 µs pre-flight invariant evaluation & Ed25519 attestation.
  - `POST /v1/verify`: 100% offline-compatible independent attestation verification.
  - `GET /v1/trust-root`: Public key distribution and active policy hash.
  - `GET /healthz`: Health and node vital status.
  - `GET /metrics`: Prometheus metrics for swarm observability.
"""

import os
import sys
import time
import json
from typing import Dict, Any, Optional

from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn

sys.path.insert(0, os.path.abspath("."))
from src.trust_protocol import BartholomewTrustAuthority, IndependentTrustVerifier
from src.declarative_policy_engine import DeclarativePolicyEngine

app = FastAPI(
    title="Bartholomew Public Agent Gateway",
    version="2.2.0",
    description="Sub-millisecond cryptographic invariant and attestation gateway for autonomous AI agents."
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global Trust Authority & Policy Engine
authority = BartholomewTrustAuthority(ttl_seconds=300)
policy_engine = DeclarativePolicyEngine("policies/default_security_policy.yaml")
node_start_time = time.time()
metrics_counters = {"total_evals": 0, "total_allows": 0, "total_denies": 0}

class EvaluateRequest(BaseModel):
    agent_id: str = Field(..., example="agent-swarm-worker-01")
    action_type: str = Field(..., example="EXECUTE_COMMAND")
    payload: Dict[str, Any] = Field(..., example={"command": "git status"})
    target_recipient: Optional[str] = "Agent-Universal-Recipient"

class VerifyRequest(BaseModel):
    attestation_receipt: Dict[str, Any]
    candidate_payload: Dict[str, Any]
    trusted_root_pubkey: Optional[str] = None

@app.get("/")
@app.get("/healthz")
def get_health():
    uptime = time.time() - node_start_time
    return {
        "status": "HEALTHY",
        "protocol": "BTP/2.2",
        "authority_public_key": authority.public_key_hex,
        "policy_id": policy_engine.policy_id,
        "rules_active": len(policy_engine.rules),
        "uptime_seconds": round(uptime, 2),
        "metrics": metrics_counters
    }

@app.get("/v1/trust-root")
def get_trust_root():
    return {
        "protocol_version": "BTP/2.2",
        "authority_pubkey": authority.public_key_hex,
        "ttl_seconds": authority.ttl_seconds,
        "policy_id": policy_engine.policy_id,
        "active_rules_count": len(policy_engine.rules)
    }

@app.post("/v1/evaluate")
def evaluate_agent_action(req: EvaluateRequest):
    metrics_counters["total_evals"] += 1
    t0 = time.perf_counter()

    # 1. Declarative Policy Evaluation
    allowed, reason, policy_latency_us = policy_engine.evaluate_payload(req.payload)
    
    # 2. Cryptographic Attestation Generation
    receipt = authority.evaluate_intent(
        agent_id=req.agent_id,
        action_type=req.action_type,
        payload=req.payload,
        target_recipient=req.target_recipient or "Agent-Universal-Recipient"
    )
    dt_us = (time.perf_counter() - t0) * 1_000_000

    # Override verdict if declarative policy blocked
    if not allowed:
        receipt["attestation"]["verdict"] = "DENY"
        receipt["attestation"]["reason"] = reason

    if receipt["attestation"]["verdict"] == "ALLOW":
        metrics_counters["total_allows"] += 1
    else:
        metrics_counters["total_denies"] += 1

    return {
        "verdict": receipt["attestation"]["verdict"],
        "reason": receipt["attestation"]["reason"],
        "total_latency_us": round(dt_us, 2),
        "receipt": receipt
    }

@app.post("/v1/verify")
def verify_receipt(req: VerifyRequest):
    pubkey = req.trusted_root_pubkey or authority.public_key_hex
    is_valid, reason = IndependentTrustVerifier.verify_attestation(
        attestation_packet=req.attestation_receipt,
        expected_payload=req.candidate_payload,
        trusted_root_pubkey=pubkey
    )
    return {
        "is_valid": is_valid,
        "verification_message": reason,
        "trusted_root_pubkey": pubkey
    }

@app.get("/metrics")
def get_prometheus_metrics():
    uptime = time.time() - node_start_time
    body = (
        f"# HELP btp_evaluations_total Total number of BTP evaluations\n"
        f"# TYPE btp_evaluations_total counter\n"
        f"btp_evaluations_total {metrics_counters['total_evals']}\n"
        f"btp_allows_total {metrics_counters['total_allows']}\n"
        f"btp_denies_total {metrics_counters['total_denies']}\n"
        f"btp_uptime_seconds {uptime:.2f}\n"
    )
    return Response(content=body, media_type="text/plain")

if __name__ == "__main__":
    port = int(os.getenv("PORT", "8080"))
    uvicorn.run(app, host="0.0.0.0", port=port)
