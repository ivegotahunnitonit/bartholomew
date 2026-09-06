"""
BTP Enterprise Developer Experience: Project Init Wizard.
Automatically detects AI agent frameworks (CrewAI, LangGraph, AutoGen, OpenAI/Claude),
scaffolds hardened .btp/ policies, configures scoped tenant keys,
and outputs a ready-to-run drop-in integration snippet.
"""

import os
import json
import yaml
import secrets
import hashlib
from typing import Dict, Any, Optional, Tuple


SUPPORTED_FRAMEWORKS = ["crewai", "langgraph", "autogen", "openai", "anthropic", "generic"]

FRAMEWORK_SNIPPETS = {
    "crewai": """# --- Bartholomew BTP Guard for CrewAI ---
from framework_adapters.crewai import BTPCrewAITaskGuard
guard = BTPCrewAITaskGuard(tenant_id="{tenant_id}")
# Attach to crew or task:
# crew = Crew(agents=[...], tasks=[...], task_callback=guard.intercept_task_execution)
""",
    "langgraph": """# --- Bartholomew BTP Guard for LangGraph ---
from framework_adapters.langgraph import BTPLangGraphGuard
guard = BTPLangGraphGuard(tenant_id="{tenant_id}")
# Wrap graph invocation:
# app = guard.wrap_graph(workflow.compile())
""",
    "autogen": """# --- Bartholomew BTP Guard for AutoGen ---
from framework_adapters.autogen import BTPAutoGenInterceptor
interceptor = BTPAutoGenInterceptor(tenant_id="{tenant_id}")
# Register hook:
# assistant.register_hook(hookable_method="process_message", hook=interceptor.verify_message)
""",
    "openai": """# --- Bartholomew BTP Guard for OpenAI Tools ---
from src.mcp_gateway import MCPProxyGateway
gateway = MCPProxyGateway()
# Wire into tool execution loop to block destructive calls in <35µs
""",
    "anthropic": """# --- Bartholomew BTP Guard for Anthropic Claude ---
from src.mcp_gateway import MCPProxyGateway
gateway = MCPProxyGateway()
# Intercept tool_use blocks with zero prompt leakage
""",
    "generic": """# --- Bartholomew BTP Guard Generic Setup ---
from src.agent_passport import SovereignAgentPassport
passport = SovereignAgentPassport.load(".btp/passport.json")
# Enforce invariant checks before executing agent tool calls
"""
}


def detect_framework(directory: str) -> str:
    """Scans project directory files and requirements to auto-detect the agent framework."""
    search_files = [
        "requirements.txt",
        "pyproject.toml",
        "Pipfile",
        "package.json",
        "environment.yml",
    ]
    detected = "generic"

    for fname in search_files:
        fpath = os.path.join(directory, fname)
        if os.path.exists(fpath):
            try:
                with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read().lower()
                    if "crewai" in content:
                        return "crewai"
                    elif "langgraph" in content:
                        return "langgraph"
                    elif "langchain" in content:
                        return "langgraph"
                    elif "autogen" in content or "pyautogen" in content:
                        return "autogen"
                    elif "anthropic" in content:
                        return "anthropic"
                    elif "openai" in content:
                        return "openai"
            except Exception:
                continue

    # Also inspect .py files in root
    try:
        for root_f in os.listdir(directory):
            if root_f.endswith(".py"):
                with open(os.path.join(directory, root_f), "r", encoding="utf-8", errors="ignore") as pf:
                    code = pf.read().lower()
                    if "from crewai" in code or "import crewai" in code:
                        return "crewai"
                    elif "from langgraph" in code or "import langgraph" in code:
                        return "langgraph"
                    elif "from autogen" in code or "import autogen" in code:
                        return "autogen"
    except Exception:
        pass

    return detected


def scaffold_project(
    target_dir: str,
    framework: Optional[str] = None,
    org: str = "my-org",
    project: str = "my-agent-swarm",
    env: str = "dev",
    non_interactive: bool = False,
) -> Dict[str, Any]:
    """
    Initializes a new or existing project with Bartholomew Trust Protocol configuration.
    Creates:
      - .btp/policy.yaml (AST rules, threat thresholds, circuit-breaker parameters)
      - .btp/tenant.json (scoped API key, tenant ID, org & project identity)
      - .btp/passport.json (sovereign Ed25519 identity)
    Returns setup metadata and code snippet.
    """
    btp_dir = os.path.join(target_dir, ".btp")
    os.makedirs(btp_dir, exist_ok=True)

    detected = framework or detect_framework(target_dir)
    if detected not in SUPPORTED_FRAMEWORKS:
        detected = "generic"

    # Generate tenant identity and scoped key
    tenant_entropy = f"{org}:{project}:{env}:{secrets.token_hex(8)}"
    tenant_id = f"ten_{hashlib.sha256(tenant_entropy.encode()).hexdigest()[:16]}"
    api_key = f"btp_{env}_{secrets.token_hex(24)}"

    # 1. Write .btp/tenant.json
    tenant_data = {
        "version": "5.3.0",
        "tenant_id": tenant_id,
        "org_id": org,
        "project_id": project,
        "environment": env,
        "api_key": api_key,
        "framework": detected,
        "created_at_utc": os.path.getmtime(btp_dir),
    }
    with open(os.path.join(btp_dir, "tenant.json"), "w", encoding="utf-8") as f:
        json.dump(tenant_data, f, indent=2)

    # 2. Write .btp/policy.yaml
    policy_data = {
        "version": "1.0",
        "tenant_id": tenant_id,
        "ast_gating": {
            "enabled": True,
            "latency_target_us": 35.0,
            "block_destructive_shell": True,
            "block_sql_mutations": True,
            "scrub_credentials": True,
        },
        "escrow_collateral": {
            "enabled": True,
            "min_bond_usd": 25.0,
            "settlement_rail": "L402_LIGHTNING",
        },
        "circuit_breaker": {
            "max_consecutive_breaches": 3,
            "cooldown_seconds": 300,
        },
        "invariants": [
            {
                "id": "RULE-AST-001",
                "description": "Block destructive file system erasure",
                "pattern": r"(?i)\brm\s+(-[rfRF]+\s+|-[rR]\s+-[fF]\s+)",
                "action": "BLOCK_AND_LOG",
            },
            {
                "id": "RULE-SQL-002",
                "description": "Block production DROP TABLE queries",
                "pattern": r"(?i)\bdrop\s+(table|schema|database)\b",
                "action": "BLOCK_AND_LOG",
            },
            {
                "id": "RULE-SEC-003",
                "description": "Scrub live cloud secret keys and tokens",
                "pattern": r"(sk-[a-zA-Z0-9]{24,}|ghp_[a-zA-Z0-9]{36}|AIza[0-9A-Za-z-_]{35})",
                "action": "SCRUB_IN_MEMORY",
            },
        ],
    }
    with open(os.path.join(btp_dir, "policy.yaml"), "w", encoding="utf-8") as f:
        yaml.dump(policy_data, f, default_flow_style=False, sort_keys=False)

    # 3. Write .btp/passport.json (Ed25519 identity simulation)
    passport_data = {
        "agent_id": f"agent-{project}-{secrets.token_hex(4)}",
        "tenant_id": tenant_id,
        "public_key": f"ed25519_pub_{secrets.token_hex(32)}",
        "reputation_score": 1.0,
        "status": "ACTIVE",
    }
    with open(os.path.join(btp_dir, "passport.json"), "w", encoding="utf-8") as f:
        json.dump(passport_data, f, indent=2)

    snippet = FRAMEWORK_SNIPPETS.get(detected, FRAMEWORK_SNIPPETS["generic"]).format(
        tenant_id=tenant_id
    )

    return {
        "status": "SUCCESS",
        "btp_dir": btp_dir,
        "tenant_id": tenant_id,
        "api_key": api_key,
        "framework": detected,
        "snippet": snippet,
    }
