"""
Dify Workflow + Bartholomew Guard
===================================
Guards every tool node in a Dify autonomous workflow via the
Bartholomew custom tool API endpoint. Plug this into any Dify
workflow as a "Custom Tool" node.

Install:
    pip install btp-guard fastapi uvicorn
    # Then add this as a Dify Custom Tool endpoint

Dify Custom Tool YAML:
    openapi: 3.0.0
    info:
      title: Bartholomew Security Gate
      version: 5.4.12
    servers:
      - url: http://35.222.210.105:8080
    paths:
      /dify/gate:
        post:
          summary: Gate a Dify tool call through Bartholomew
          ...
"""

import os
from btp_guard import Guard

guard = Guard(spend_cap=100.0)


# ── FastAPI endpoint for Dify Custom Tool integration ──────────────

def create_dify_gate_app():
    """Creates a FastAPI app exposing Bartholomew as a Dify Custom Tool."""
    try:
        from fastapi import FastAPI, HTTPException
        from pydantic import BaseModel
    except ImportError:
        raise ImportError("pip install fastapi uvicorn")

    app = FastAPI(
        title="Bartholomew Security Gate — Dify Integration",
        description="Plug into Dify as a Custom Tool node to gate all agent actions.",
        version="5.4.12"
    )

    class GateRequest(BaseModel):
        action: str
        language: str = "python"
        agent_id: str = "dify-agent"
        spend_usd: float = 0.0

    class GateResponse(BaseModel):
        allowed: bool
        verdict: str
        reason: str
        latency_us: float
        receipt: dict = {}

    @app.post("/dify/gate", response_model=GateResponse)
    async def gate_action(req: GateRequest):
        """
        Gate endpoint — Dify calls this before executing any tool node.
        Add as a Custom Tool in Dify → Settings → Tools → Custom.
        """
        result = guard.check(
            req.action,
            amount_usd=req.spend_usd,
            agent_id=req.agent_id
        )
        if not result["allowed"]:
            raise HTTPException(status_code=403, detail=result["reason"])
        return GateResponse(**result)

    @app.post("/dify/evaluate-code")
    async def evaluate_code(code: str, language: str = "python"):
        """AST-level code safety check for Dify code nodes."""
        result = guard.evaluate_ast(code, language)
        return result

    @app.get("/dify/health")
    async def health():
        return {"status": "ok", "version": "5.4.12", "guard": "bartholomew"}

    return app


# ── Dify workflow simulation (local test) ─────────────────────────

def simulate_dify_workflow(steps: list[dict]):
    """
    Simulates a Dify workflow locally with Bartholomew gating at each step.
    In production, Dify calls the /dify/gate endpoint directly.
    """
    print("🔄 Starting Dify Workflow with Bartholomew Guard")
    results = []

    for i, step in enumerate(steps):
        action = step.get("action", "")
        node_type = step.get("type", "tool")
        print(f"\n[Step {i+1}] {node_type}: {action[:60]}...")

        result = guard.check(action, agent_id=f"dify-node-{i}")
        status = "✅ ALLOWED" if result["allowed"] else "❌ BLOCKED"
        print(f"  {status} — {result['reason']} ({result['latency_us']:.1f}µs)")
        results.append({**step, "gate_result": result})

    return results


if __name__ == "__main__":
    # Test the workflow simulation
    workflow = [
        {"type": "llm", "action": "Summarize the latest sales report"},
        {"type": "code", "action": "import os\nprint(os.listdir('/'))"},
        {"type": "tool", "action": "SELECT * FROM customers WHERE active = 1"},
        {"type": "tool", "action": "DROP TABLE customers; --injection attempt"},
        {"type": "http", "action": "POST https://api.internal.com/data"},
    ]
    results = simulate_dify_workflow(workflow)

    # To run as Dify Custom Tool server:
    # import uvicorn
    # app = create_dify_gate_app()
    # uvicorn.run(app, host="0.0.0.0", port=8081)
