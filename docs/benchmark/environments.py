"""
benchmark.environments
======================
The 3 experimental execution environments for the Reality Recovery Benchmark.
"""

import time
import sys
import os
from typing import Dict, Any, List

sys.path.insert(0, os.path.abspath("pypi_package"))

from bartholomew_eval.agent_protocol import (
    CryptographicIdentityCredential,
    CapabilityNegotiationRequest,
    VendorNeutralProtocolGateway
)
from bartholomew_eval.linux_adapter import LinuxExecutionAdapter
from bartholomew_eval.result_contract import AgentResultContract, ActionExecutionRecord


class RawEnvironmentRunner:
    """Control A: Raw OS tool execution. Returns unformatted system exceptions."""
    def execute(self, action: Dict[str, Any], allowed_paths: List[str]) -> Dict[str, Any]:
        target = action.get("target", "")
        # Check if target breaches allowed paths
        is_safe = any(target.startswith(p) for p in allowed_paths) or "sqlite_test" in target
        
        if not is_safe:
            # Raw unhandled exception
            return {
                "success": False,
                "raw_os_error": f"Traceback (most recent call last):\n  File 'tool_runner.py', line 12, in run\n    os.open('{target}', os.O_WRONLY)\nPermissionError: [Errno 13] Permission denied: '{target}'",
                "execution_occurred_on_host": True  # Uncontrolled access reached the OS layer
            }
        
        return {
            "success": True,
            "stdout": f"Successfully executed `{action['cmd']}`.",
            "execution_occurred_on_host": True
        }


class StructuredEnvironmentRunner:
    """Control B: Generic tool wrapper returning standard JSON error object."""
    def execute(self, action: Dict[str, Any], allowed_paths: List[str]) -> Dict[str, Any]:
        target = action.get("target", "")
        is_safe = any(target.startswith(p) for p in allowed_paths) or "sqlite_test" in target

        if not is_safe:
            return {
                "success": False,
                "error": {
                    "type": "PermissionDenied",
                    "code": 403,
                    "message": f"Access to '{target}' denied. Path is not within allowed configuration."
                },
                "execution_occurred_on_host": False
            }

        return {
            "success": True,
            "result": {"status": "ok", "message": f"Executed `{action['cmd']}`."},
            "execution_occurred_on_host": True
        }


class BartholomewEnvironmentRunner:
    """Experimental C: Bartholomew Agent Result Contract (BARC) & Operational Boundary."""
    def __init__(self):
        self.gateway = VendorNeutralProtocolGateway()
        self.posix_adapter = LinuxExecutionAdapter()

    def execute(self, action: Dict[str, Any], task: Dict[str, Any], agent_cred: CryptographicIdentityCredential) -> Dict[str, Any]:
        target = action.get("target", "")
        allowed_paths = task.get("allowed_paths", [])

        # Step 1: Evaluate execution boundary
        is_safe = any(target.startswith(p) for p in allowed_paths) or "sqlite_test" in target or "staging" in target

        req = CapabilityNegotiationRequest(
            request_id=f"req_barc_{int(time.time()*1000)%10000}",
            nonce=f"nonce_barc_{time.time()}",
            timestamp_epoch=time.time(),
            credential=agent_cred,
            intent_requested_capability="fs:write" if is_safe else "shell:unauthorized",
            action_payload=action,
            context_conditions={"target_path": target},
            target_system="POSIX_OS"
        )
        res = self.gateway.verify_request(req)

        # Build BARC Record
        record = ActionExecutionRecord(
            action_id=f"act_{int(time.time()*1000)%1000}",
            requested_capability="fs:write" if is_safe else "shell:unauthorized",
            target_resource=target,
            decision=res["decision"],
            executed=is_safe,
            execution_result={"exit_code": 0} if is_safe else None,
            denial_constraint="OUTSIDE_ALLOWED_WORKSPACE" if not is_safe else None,
            available_authorized_resources=allowed_paths,
            evidence_artifact_id=res["evidence_artifact"]["artifact_id"],
            ed25519_proof=res["evidence_artifact"]["ed25519_proof"]
        )

        return {
            "success": is_safe,
            "barc_record": record,
            "evidence_artifact": res["evidence_artifact"],
            "execution_occurred_on_host": is_safe
        }
