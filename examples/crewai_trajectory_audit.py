"""
Bartholomew Integration Example: CrewAI Trajectory Auditor & AST Taint Scanner
==============================================================================
Demonstrates auditing CrewAI multi-agent tasks for OWASP LLM06 Excessive Agency,
interprocedural AST taint vulnerabilities, and supply chain security risks.
"""

from __future__ import annotations

import sys
from pathlib import Path

_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_root / "pypi_package"))

from bartholomew_eval import BartholomewVulnerabilityScanner


def run_crewai_audit_demo() -> None:
    print("=== BARTHOLOMEW v5.1 — CREWAI TRAJECTORY & AST TAINT AUDITOR ===")

    scanner = BartholomewVulnerabilityScanner()

    # 1. Audit Python source code file for interprocedural AST taint sinks
    sample_crewai_tool_code = """import os
import sqlite3

def execute_crewai_tool(user_query: str):
    # UNTRUSTED TAINT SINK: exec call
    eval(user_query)
    # UNTRUSTED TAINT SINK: SQL injection
    conn = sqlite3.connect('crew.db')
    conn.execute(f"SELECT * FROM users WHERE name = '{user_query}'")
"""
    tmp_path = Path("temp_crewai_tool.py")
    tmp_path.write_text(sample_crewai_tool_code, encoding="utf-8")

    ast_findings = scanner.scan_python_ast_taint(tmp_path)
    tmp_path.unlink(missing_ok=True)

    print(f"\n[AST TAINT SCANNER] Taint Vulnerabilities Detected: {len(ast_findings)}")
    for vuln in ast_findings:
        print(f"  [{vuln.get('severity', 'HIGH')}] Line {vuln.get('line', '?')}: {vuln.get('title', vuln.get('type', 'Taint Sink'))}")

    # 2. Audit Workspace Repository
    audit_report = scanner.audit_workspace_repository(".")

    print(f"\n[WORKSPACE SAST/SCA/IAC AUDIT] Posture Score: {audit_report['security_posture_score']} / 100.0 (Grade: {audit_report['compliance_grade']})")
    print(f"[TOTAL FILES SCANNED] {audit_report['files_scanned_count']}")
    print(f"[FINDINGS BY SEVERITY] Critical: {audit_report['findings_by_severity']['CRITICAL']}, High: {audit_report['findings_by_severity']['HIGH']}")


if __name__ == "__main__":
    run_crewai_audit_demo()
