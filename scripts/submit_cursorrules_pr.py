import subprocess
import re
import urllib.request
import json
import base64
import time

remote_url = subprocess.check_output(['git', 'config', '--get', 'remote.origin.url'], encoding='utf-8').strip()
token = re.search(r'https://([^@]+)@github\.com', remote_url).group(1)
headers = {
    'Authorization': f'Bearer {token}',
    'Accept': 'application/vnd.github+json',
    'User-Agent': 'Bartholomew-Bot'
}

fork_owner = "ivegotahunnitonit"
upstream_owner = "PatrickJS"
repo_name = "awesome-cursorrules"
branch_name = "add-btp-guard-rules"

print("[+] Waiting for fork to synchronize...")
time.sleep(3)

# 1. Get default branch sha
req = urllib.request.Request(f"https://api.github.com/repos/{fork_owner}/{repo_name}/git/ref/heads/main", headers=headers)
with urllib.request.urlopen(req) as resp:
    main_ref = json.loads(resp.read().decode('utf-8'))
    main_sha = main_ref['object']['sha']
    print(f"[+] Main branch SHA: {main_sha}")

# 2. Create new branch
branch_payload = json.dumps({
    "ref": f"refs/heads/{branch_name}",
    "sha": main_sha
}).encode('utf-8')

req = urllib.request.Request(
    f"https://api.github.com/repos/{fork_owner}/{repo_name}/git/refs",
    data=branch_payload,
    headers=headers,
    method="POST"
)

try:
    with urllib.request.urlopen(req) as resp:
        print(f"[+] Created branch {branch_name}")
except Exception as e:
    print(f"[*] Branch might already exist: {e}")

# 3. Read content of local .cursor/rules/btp-guard.mdc
with open(".cursor/rules/btp-guard.mdc", "r", encoding="utf-8") as f:
    rule_content = f.read()

content_b64 = base64.b64encode(rule_content.encode('utf-8')).decode('utf-8')

# 4. Check if file exists on branch to get sha if updating
file_sha = None
try:
    check_req = urllib.request.Request(
        f"https://api.github.com/repos/{fork_owner}/{repo_name}/contents/rules/btp-guard.mdc?ref={branch_name}",
        headers=headers
    )
    with urllib.request.urlopen(check_req) as resp:
        existing_file = json.loads(resp.read().decode('utf-8'))
        file_sha = existing_file.get("sha")
except Exception:
    pass

put_payload = {
    "message": "feat(rules): add BTP Guard autonomous agent security rules",
    "content": content_b64,
    "branch": branch_name
}
if file_sha:
    put_payload["sha"] = file_sha

put_req = urllib.request.Request(
    f"https://api.github.com/repos/{fork_owner}/{repo_name}/contents/rules/btp-guard.mdc",
    data=json.dumps(put_payload).encode('utf-8'),
    headers=headers,
    method="PUT"
)

with urllib.request.urlopen(put_req) as resp:
    print("[+] Successfully committed rules/btp-guard.mdc to branch!")

# 5. Check if PR already exists
prs_req = urllib.request.Request(
    f"https://api.github.com/repos/{upstream_owner}/{repo_name}/pulls?head={fork_owner}:{branch_name}&state=all",
    headers=headers
)
with urllib.request.urlopen(prs_req) as resp:
    existing_prs = json.loads(resp.read().decode('utf-8'))

if existing_prs:
    print(f"[+] PR already exists: {existing_prs[0].get('html_url')}")
else:
    pr_body = """### Overview
Adds Cursor rules (`.cursor/rules/btp-guard.mdc`) for the Bartholomew Trust Protocol (BTP Guard v5.4.4).

### Invariants Enforced
- **Zero Destructive Shell Commands**: Hard-blocks `rm -rf /`, `rmdir /s`, disk partition wipes, and fork-bombs.
- **Zero Credential Exfiltration**: Prevents reading, printing, or transmitting `.env`, private SSH keys (`id_rsa`, `id_ed25519`), AWS/GCP service keys, or tokens.
- **Surgical Code Mutations**: Enforces surgical diffs and non-destructive workspace refactoring.
- **Agent Framework Compatibility**: Validated across Cursor, VS Code (750+ downloads), CrewAI, LangGraph, AutoGen, and Claude Desktop.

Reference: https://github.com/ivegotahunnitonit/bartholomew
"""
    pr_payload = json.dumps({
        "title": "feat(rules): add BTP Guard autonomous agent safety & anti-exfiltration rules",
        "head": f"{fork_owner}:{branch_name}",
        "base": "main",
        "body": pr_body
    }).encode('utf-8')

    create_pr_req = urllib.request.Request(
        f"https://api.github.com/repos/{upstream_owner}/{repo_name}/pulls",
        data=pr_payload,
        headers=headers,
        method="POST"
    )

    with urllib.request.urlopen(create_pr_req) as resp:
        pr_data = json.loads(resp.read().decode('utf-8'))
        print(f"[+] Successfully opened Pull Request: {pr_data.get('html_url')}")
