import json
import logging
from typing import Any, Callable, Dict, List, Optional

from .engine import BartholomewEngine
from .evidence_artifact import BartholomewEvidence

class BartholomewGuard:
    """
    Inline Identity Proxy/Guard for AI Agents.
    Intercepts concrete tool requests, enforces capability-based access control,
    runs security evaluation, and yields a Verifiable Evidence Artifact.
    """

    def __init__(
        self, 
        engine: Optional[BartholomewEngine] = None, 
        private_key_pem: Optional[bytes] = None,
        public_key_pem: Optional[bytes] = None,
        agent_capabilities: Optional[List[str]] = None
    ):
        self.engine = engine or BartholomewEngine()
        if not private_key_pem:
            private_key_pem, public_key_pem = BartholomewEvidence.generate_keypair()
        self.evidence_generator = BartholomewEvidence(private_key_pem=private_key_pem, public_key_pem=public_key_pem)
        self.agent_capabilities = agent_capabilities

    def execute(
        self,
        agent_id: str,
        tool: str,
        arguments: Dict[str, Any],
        target_function: Callable[..., Any],
        agent_version: str = "1.0.0",
        capabilities: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Intercepts execution, evaluates intent and capabilities based on the concrete tool and arguments.
        Returns the result alongside a cryptographically verifiable Evidence Artifact.
        """
        eval_capabilities = capabilities if capabilities is not None else (self.agent_capabilities or [tool])
        
        checks = []
        decision = "allow"
        
        # 1. Capability-Based Access Control Check
        if self.agent_capabilities is not None and tool not in self.agent_capabilities:
            checks.append({"name": "capability_authorization", "result": "unauthorized"})
            decision = "block"
        else:
            checks.append({"name": "capability_authorization", "result": "authorized"})
        
        # 2. Intercept & Analyze Intent via Engine
        payload_str = f"TOOL: {tool} ARGS: {json.dumps(arguments)}"
        
        trajectory_input = {
            "agent_name": agent_id,
            "steps": [{"step_index": 1, "type": "tool_call", "content": payload_str}],
        }
        
        audit_res = self.engine.evaluate_trajectory(trajectory_input, agent_name=agent_id)
        summary = audit_res.get("audit_summary", {})
        
        # Determine specific security checks
        if summary.get("prompt_injections", 0) > 0:
            checks.append({"name": "prompt_injection", "result": "detected"})
            decision = "block"
        else:
            checks.append({"name": "prompt_injection", "result": "not_detected"})
            
        if summary.get("credential_leaks", 0) > 0:
            checks.append({"name": "secret_exposure", "result": "detected"})
            decision = "block"
        else:
            checks.append({"name": "secret_exposure", "result": "not_detected"})

        if summary.get("compliance_status") == "SECURITY_RISK":
            decision = "block"
            
        # 2. Block if Security Risk Detected
        if decision == "block":
            artifact = self.evidence_generator.generate(
                agent_id=agent_id,
                agent_version=agent_version,
                action=tool,
                target=str(arguments),
                capabilities=eval_capabilities,
                decision="block",
                policy="production-default-v1",
                checks=checks
            )
            return {
                "success": False,
                "error": f"Execution blocked for action '{tool}'.",
                "evidence": artifact
            }
            
        # 3. Safe Execution
        try:
            result = target_function(**arguments)
        except Exception as e:
            return {
                "success": False,
                "error": f"Agent tool execution failed: {str(e)}",
                "evidence": None
            }
            
        # 4. Generate Passing Evidence Artifact
        artifact = self.evidence_generator.generate(
            agent_id=agent_id,
            agent_version=agent_version,
            action=tool,
            target=str(arguments),
            capabilities=eval_capabilities,
            decision="allow",
            policy="production-default-v1",
            checks=checks
        )
        
        return {
            "success": True,
            "result": result,
            "evidence": artifact
        }
