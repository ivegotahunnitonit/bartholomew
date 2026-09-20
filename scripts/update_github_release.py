import subprocess
import re
import json
import urllib.request
from pathlib import Path

# 1. Extract token safely
remote_url = subprocess.check_output(['git', 'config', '--get', 'remote.origin.url'], encoding='utf-8').strip()
match = re.search(r'https://([^@]+)@github\.com/([^/]+)/([^/\.]+)', remote_url)
if not match:
    print("[!] Could not parse GitHub token from remote URL.")
    exit(1)

token = match.group(1)
owner = match.group(2)
repo = match.group(3)

print(f"[+] Authenticated as owner: {owner}, repo: {repo}")

headers = {
    "Authorization": f"Bearer {token}",
    "Accept": "application/vnd.github+json",
    "User-Agent": "Bartholomew-Release-Bot"
}

# 2. Fetch existing release
req = urllib.request.Request(f"https://api.github.com/repos/{owner}/{repo}/releases/tags/v5.4.4", headers=headers)
try:
    with urllib.request.urlopen(req) as resp:
        rel = json.loads(resp.read().decode('utf-8'))
        release_id = rel["id"]
        print(f"[+] Found existing release ID: {release_id}")
except Exception as e:
    print(f"[!] Error fetching release: {e}")
    exit(1)

body_content = """## Bartholomew AI (BTP v5.4.4 Standards Track)

The in-process AI agent execution gateway providing sub-35µs tool gating, zero prompt leakage, Ed25519 audit receipts, and multi-tenant cloud fleet management.

### [NEW] What's in v5.4.4:
* **Interactive In-Browser AST Invariant Playground**: Try live in your browser at [https://bartholomew.info/cookbook](https://bartholomew.info/cookbook) with zero setup.
* **Cursor & Windsurf IDE Rules**: Added `.cursor/rules/btp-guard.mdc` and `.windsurfrules` for direct AI IDE enforcement.
* **Production Kubernetes & Helm Chart**: Enterprise private VPC Helm deployment with dedicated sidecar container (`ghcr.io/bartholomew-ai/bartholomew-sidecar:5.4.4`).
* **Framework Adapters Hardening**: Production middleware for CrewAI, LangGraph, AutoGen, and LlamaIndex with 100% test coverage.
* **Direct Stripe Commercial Licensing**: Pro Tier ($49/mo) & Enterprise Fleet ($199/mo) direct checkout integration.
* **750+ Open VSX Downloads**: Available on [Open VSX Registry](https://open-vsx.org/extension/Bartholomew/bartholomew-guard-vscode) and VS Code marketplace.

### Download & Install (.vsix):
1. Download `bartholomew-guard-vscode-5.4.4.vsix` below.
2. In VS Code or Cursor: Press `Ctrl+Shift+P` -> **Extensions: Install from VSIX...** -> Select this file.
3. The shield icon in your status bar confirms real-time AST protection is active.

### Commercial Plans & Cloud Fleet:
* **Bartholomew Pro ($49/mo)**: Real-time Cloud Telemetry Dashboard & Slack alerts -> [Upgrade to Pro](https://buy.stripe.com/fZu28rbNz5TYcmAddK9R600)
* **Enterprise Fleet ($199/mo)**: Multi-tenant workspace isolation & SOC 2 Type II audit packs -> [Upgrade to Enterprise](https://buy.stripe.com/fZu14ng3PgyC9ao2z69R601)
* **Portal**: https://bartholomew.info/pricing
"""

payload = {
    "name": "Bartholomew Guard v5.4.4 — Autonomous Agent Execution Gateway",
    "body": body_content,
    "draft": False,
    "prerelease": False
}

patch_req = urllib.request.Request(
    f"https://api.github.com/repos/{owner}/{repo}/releases/{release_id}",
    data=json.dumps(payload).encode('utf-8'),
    headers=headers,
    method="PATCH"
)

with urllib.request.urlopen(patch_req) as resp:
    res = json.loads(resp.read().decode('utf-8'))
    print(f"[+] Release v5.4.4 updated successfully: {res.get('html_url')}")
