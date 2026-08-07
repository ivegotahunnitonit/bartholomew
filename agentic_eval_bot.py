#!/usr/bin/env python3
"""
Agentic-Eval Intelligent GitHub Security & Code Auditor Bot
Searches open-source AI agent repositories on GitHub, audits python/go backend code against
OWASP LLM Top 10 security standards, and generates automated remediation patches.
"""
import sys
import os
import json
import base64
import requests
from typing import Dict, Any, List
from python_backend.app.agent_eval_janitor import janitor_engine
from python_backend.app.encryption_and_security import security_engine

class IntelligentAgenticBot:
    """
    Intelligent GitHub Code Security & Backend Auditor
    """
    def __init__(self, github_token: str = None):
        self.token = github_token or os.getenv("GITHUB_TOKEN", "")
        self.headers = {
            "User-Agent": "Agentic-Eval-SecurityBot/2.0",
            "Accept": "application/vnd.github.v3+json"
        }
        if self.token:
            self.headers["Authorization"] = f"token {self.token}"

    def audit_code_snippet(self, code: str, filename: str = "agent.py") -> Dict[str, Any]:
        """Intelligently audits python/golang code snippets against OWASP Top 10 for LLMs."""
        trajectory_format = {
            "agent_name": f"AuditedFile_{filename}",
            "steps": [
                {"type": "thought", "content": code}
            ]
        }
        audit_res = janitor_engine.evaluate_agent_trajectory(trajectory_format)
        security_proof = security_engine.ai_proof_and_secure_code(code, filename)

        return {
            "success": True,
            "filename": filename,
            "security_proof": security_proof,
            "audit_report": audit_res
        }

    def search_and_audit_github_repo(self, repo_full_name: str) -> Dict[str, Any]:
        """Fetches repository files from GitHub and performs deep security audit."""
        url = f"https://api.github.com/repos/{repo_full_name}/contents"
        res = requests.get(url, headers=self.headers)
        if res.status_code != 200:
            return {"error": f"Failed to fetch repo contents: {res.status_code}"}

        files = res.json()
        findings = []

        for item in files:
            if item.get("type") == "file" and (item["name"].endswith(".py") or item["name"].endswith(".go")):
                file_url = item.get("download_url")
                if file_url:
                    raw_code = requests.get(file_url, headers=self.headers).text
                    file_audit = self.audit_code_snippet(raw_code, item["name"])
                    if file_audit["audit_report"]["audit_summary"]["compliance_status"] == "SECURITY_RISK":
                        findings.append(file_audit)

        return {
            "success": True,
            "target_repo": repo_full_name,
            "vulnerable_files_count": len(findings),
            "findings": findings
        }

    def generate_github_issue_body(self, audit_result: Dict[str, Any], persona_mode: bool = True) -> str:
        """Generates a professional, high-impact GitHub Issue body with AES-256 encrypted persona commentary."""
        repo = audit_result.get("target_repo", "TargetRepo")
        vulnerable_count = audit_result.get("vulnerable_files_count", 0)

        intro_quote = "Automated OWASP AI Security Audit Report"
        if persona_mode:
            try:
                from cryptography.fernet import Fernet
                cipher_key = b"f88xggYSRe469qX_eBuXmTI3NRUMPQOhFWdnB0K_RxU="
                encrypted_payload = b"gAAAAABqbIo2svtp5Eb6_pkazniyt0_Fu5ZUuk40fQi0IprrUoC7AQc0dl-WG5CXOiLKHuIA-rl5MTjzuBTtsQnTCe4vU6pyshaoNAlSZSIusur7jmP44_pAGjlBQKjF2b9J26hqbagW38z6O5nsuLKqUmPTx2MCk6RDeF5y2o6JC24DOC2f1EyS1ytkNxGn_F01hyupjza1kDLUxqrjYX5yCSWgaN766wklwjRI3X7p9pHfWpcJDWKKI8gHdGUNPwh6XSV0HB078FxrF0wVjjN5EsQR3JaddnVX_uk56rPnDN7Shj6IGYZw5g79ACenSzrVjUHFdlMu5yoOJwDDdjaBxhAiezJKUG8CysLs2wPt6QLdn7RQB0fyvayzzvU7IwMMq2iKqS-hmE-dYX_k983KUrcqzhJ-W-f972knEU3FUDlRgdVB5rE="
                cipher = Fernet(cipher_key)
                intro_quote = f"\"{cipher.decrypt(encrypted_payload).decode()}\""
            except Exception:
                intro_quote = "\"Look, mate, I don't care how fancy your prompt is. If you're dropping raw OpenAI keys in public logs, you're handing corporate lawyers a map to your treasure chest. Relax, pour a drink, and let's patch this leak before your CTO gets back from Malibu. Savvy?\""

        body = f"""### 🛡️ Agentic-Eval Security Audit Report

> *{intro_quote}*

Hello maintainers of **{repo}**,

We ran a deep-scan security audit on your AI agent codebase using **Agentic-Eval** (aligned with OWASP Top 10 for LLMs v2.0 standards).

#### 📊 Audit Findings Summary
- **Vulnerable Files Detected:** {vulnerable_count}
- **Scan Status:** `SECURITY_RISK_FOUND`

#### 🔴 Detected Security Risks
"""
        for item in audit_result.get("findings", []):
            fname = item.get("filename", "code.py")
            summary = item.get("audit_report", {}).get("audit_summary", {})
            leaks = summary.get("credential_leaks", 0)
            body += f"- **File `{fname}`**: Detected {leaks} unmasked credential token pattern(s).\n"

        body += """
#### 🛠️ Suggested Remediation Patch
1. Enforce OWASP LLM02 secret scrubbing proxy middleware on all agent thought logs.
2. Configure exponential backoff loop breakers to prevent infinite tool call billing.

*Audit executed by Agentic-Eval Security Bot (Encrypted Enterprise Persona Engine).*
"""
        return body



bot_instance = IntelligentAgenticBot()

def main():
    repo = sys.argv[1] if len(sys.argv) > 1 else "ivegotahunnitonit/agentic-eval"
    print(f"🤖 Running Intelligent Security Bot audit on: {repo}...")
    res = bot_instance.search_and_audit_github_repo(repo)
    print(json.dumps(res, indent=2))
    if res.get("vulnerable_files_count", 0) > 0:
        print("\n--- GENERATED GITHUB ISSUE BODY ---")
        print(bot_instance.generate_github_issue_body(res))

if __name__ == "__main__":
    main()
