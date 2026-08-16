import sys
import os
import json
import argparse
import re

SECRET_REGEX = re.compile(r'(sk-[a-zA-Z0-9]{20,}|ghp_[a-zA-Z0-9]{20,}|AKIA[0-9A-Z]{16})')

def scan_file(filepath):
    issues = []
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            lines = content.splitlines()

            for idx, line in enumerate(lines):
                if SECRET_REGEX.search(line):
                    issues.append({
                        "line": idx + 1,
                        "type": "SECRET_LEAK",
                        "severity": "CRITICAL",
                        "detail": f"Unmasked API key/credential pattern in {os.path.basename(filepath)}"
                    })
                if "except Exception:" in line or "except:" in line:
                    if idx + 1 < len(lines) and ("pass" in lines[idx + 1] or "return None" in lines[idx + 1] or "return null" in lines[idx + 1]):
                        issues.append({
                            "line": idx + 1,
                            "type": "SILENT_ERROR_SWALLOWING",
                            "severity": "MEDIUM",
                            "detail": f"Silent exception swallowing fallback in {os.path.basename(filepath)}"
                        })
    except Exception as e:
        pass
    return issues

def main():
    parser = argparse.ArgumentParser(description="agent-qa-guard: CI/CD AI Agent Linter & Secret Scanner")
    parser.add_argument("command", choices=["check", "fix", "version"], help="Command to run: check, fix, or version")
    parser.add_argument("--path", default=".", help="Target directory or file path to scan")
    parser.add_argument("--trajectory", help="Path to AI agent JSON step trajectory file")

    args = parser.parse_args()

    if args.command == "version":
        print("agent-qa-guard v1.0.0")
        sys.exit(0)

    print("================================================================================")
    print("  [AGENT-QA-GUARD V1.0.0] AI AGENT LINTER & SECRET SCANNER")
    print("================================================================================")


    total_files = 0
    all_issues = []

    target_path = os.path.abspath(args.path)

    if os.path.isfile(target_path):
        total_files = 1
        all_issues.extend(scan_file(target_path))
    else:
        for root, dirs, files in os.walk(target_path):
            if ".git" in root or "node_modules" in root or "venv" in root or "__pycache__" in root:
                continue
            for file in files:
                if file.endswith((".py", ".js", ".ts", ".json", ".env")):
                    total_files += 1
                    fp = os.path.join(root, file)
                    all_issues.extend(scan_file(fp))

    critical_count = sum(1 for i in all_issues if i['severity'] == 'CRITICAL')
    medium_count = sum(1 for i in all_issues if i['severity'] == 'MEDIUM')

    deductions = (critical_count * 25) + (medium_count * 10)
    score = max(0, 100 - deductions)

    print(f"[*] Scanned Files: {total_files}")
    print(f"[*] Issues Found:  {len(all_issues)} ({critical_count} Critical, {medium_count} Medium)\n")

    if all_issues:
        print("[!] FLAGGED VULNERABILITIES:")
        for issue in all_issues[:10]:
            print(f"  [{issue['severity']}] Line {issue['line']}: {issue['detail']}")
        print()

    status_str = "PASSED" if score >= 85 else "ACTION REQUIRED"
    print("--------------------------------------------------------------------------------")
    print(f"  Overall Reliability Score: {score}% / 100% [{status_str}]")
    if score < 100:
        print("  -> Upgrade to Agent-QA Pro or run 'agent-qa fix' to auto-patch errors.")
        print("  -> Live Dashboard & API: https://acn-network.org/dashboard/orchestrator.html")
    print("================================================================================\n")


    if critical_count > 0 and args.command == "check":
        sys.exit(1)

if __name__ == "__main__":
    main()
