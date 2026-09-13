"""
bartholomew_eval.linux_master
=============================
BTP Linux Resource Target Adapter — POSIX Command Interceptor & Execution Adapter.
"""

from typing import Dict, Any, Optional, List
from .linux_adapter import LinuxExecutionAdapter, LinuxExecutionViolation

LinuxSecurityViolation = LinuxExecutionViolation


class LinuxMasterEngine(LinuxExecutionAdapter):
    """
    Adapter subclass providing backward-compatible interface wrapping LinuxExecutionAdapter.
    """

    def evaluate_command(self, cmd: str, strict: bool = True) -> Dict[str, Any]:
        adapter_res = self.evaluate_execution(command=cmd)
        is_safe = adapter_res["is_authorized"]
        
        threats = []
        if not is_safe:
            threats.append({
                "category": "AUTHORITY_BOUNDARY_VIOLATION",
                "rule": "BTP_RESOURCE_BOUNDARY",
                "severity": "CRITICAL",
                "matched_text": adapter_res["denial_reason"]
            })

        return {
            "command": cmd,
            "status": "ALLOWED" if is_safe else "BLOCKED",
            "is_safe": is_safe,
            "max_severity": "NONE" if is_safe else "CRITICAL",
            "threats_count": len(threats),
            "threats": threats,
            "parsed_tokens_count": adapter_res["shell_semantics"]["parsed_tokens_count"],
            "parse_error": None,
            "evaluator": "BTP Linux Target Execution Adapter v1.0",
            "recommended_action": "Execute within BTP authority envelope." if is_safe else "Halt execution: " + str(adapter_res["denial_reason"])
        }

    def evaluate_linux_script(self, script_text: str) -> Dict[str, Any]:
        cis = self.evaluate_cis_benchmark()
        lines = script_text.splitlines()
        flagged = []
        for idx, line in enumerate(lines, 1):
            if line.strip() and not line.strip().startswith("#"):
                res = self.evaluate_command(line.strip())
                if not res["is_safe"]:
                    flagged.append({"line_number": idx, "line_content": line.strip(), "max_severity": "CRITICAL", "threats": res["threats"]})
        
        return {
            "total_lines_analyzed": len(lines),
            "flagged_lines_count": len(flagged),
            "total_threats": len(flagged),
            "critical_threats": len(flagged),
            "status": "PASSED" if len(flagged) == 0 else "FAILED_HARDENING_AUDIT",
            "flagged_lines": flagged,
            "cis_benchmark_evidence": cis
        }

    def get_hardening_profile(self) -> Dict[str, Any]:
        return self.evaluate_cis_benchmark()
