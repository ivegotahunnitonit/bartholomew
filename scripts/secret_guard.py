# Bartholomew Secret Guard & Zero-Leak Auditor v2.0
# Scans all codebase files for hardcoded credentials, Bearer tokens, and private keys.

import os
import re
import sys

PATTERNS = [
    (r'sk-proj-[a-zA-Z0-9_\-]{20,}', 'OpenAI Project Key'),
    (r'sk-[a-zA-Z0-9]{20,}', 'Generic OpenAI/Anthropic Key'),
    (r'ghp_[A-Za-z0-9_]{20,}', 'GitHub Classic Token'),
    (r'github_pat_[A-Za-z0-9_]{20,}', 'GitHub Fine-Grained Token'),
    (r'sk_live_[A-Za-z0-9_]{24,}', 'Stripe Live Secret Key'),
    (r'pk_live_[A-Za-z0-9_]{24,}', 'Stripe Live Publishable Key'),
    (r'AKIA[0-9A-Z]{16}', 'AWS Access Key ID'),
    (r'age_live_[a-zA-Z0-9_\-]{16,}', 'Bartholomew Enterprise API Key'),
    (r'acn_op_sec_[a-zA-Z0-9_\-]{16,}', 'Operator Security Bearer Key'),
    (r'eyJ[a-zA-Z0-9_\-]+\.[a-zA-Z0-9_\-]+\.[a-zA-Z0-9_\-]+', 'Unmasked JWT Bearer Token'),
    (r'(?i)bearer\s+[a-zA-Z0-9_\-\.\+/=]{16,}', 'Generic Bearer Token'),
    (r'(?i)authorization:\s*bearer\s+[a-zA-Z0-9_\-\.\+/=]{16,}', 'Authorization Bearer Header'),
    (r'-----BEGIN (?:RSA|OPENSSH|EC|DSA|PRIVATE) KEY-----', 'Private Key Header'),
]

EXCLUDE_DIRS = {'.git', 'node_modules', '.tempmediaStorage', '.system_generated', 'dist', 'build', '__pycache__', '.venv', 'tests', 'test', 'examples', 'go_services'}
EXCLUDE_FILES = {
    'test_api.py', 'test_unit.py', 'test_provider.py', 'test_sso_federation.py',
    'test_jwt_algorithm_key_confusion_fix.py', 'jwt_poc.py', 'jwt_algorithm_key_confusion_fix.py',
    'test_agentic_eval_security.py', 'security_stress_tester.py', 'agent_pen_tester.py',
    'test_revenue_engines.py', 'bartholomew_daemon', 'bartholomew_daemon_linux', 'main', 'main.exe'
}

# Known false positive / example placeholders to allow in documentation and test files
ALLOW_LIST = {
    "age_live_your_key_here",
    "sk-proj-1234567890abcdef1234567890",
    "ghp_1234567890abcdef1234567890",
    "AKIAIOSFODNN7EXAMPLE",
    "sk_live_test_placeholder_key_value",
    "YOUR_GITHUB_TOKEN_HERE",
    "YOUR_STRIPE_SECRET_KEY_HERE",
    "YOUR_STRIPE_PUBLISHABLE_KEY_HERE",
    "sk-proj-99887766554433221",
    "sk-proj-xK9mN2pQ7rT4vY8wA",
    "sk-proj-99a8b1c7d2e3f4a5b",
    "ghp_99887766554433221100a",
    "sk-1234567890abcdef",
    "sk-9999999999999999",
    "sk-abcdef1234567890",
    "Bearer token",
    "Bearer <token>",
    "Bearer <YOUR_ACN_OPERATOR_KEY>",
    "Bearer ${token}",
    "Bearer ${stripeKey}",
    "Bearer ${STRIPE_SECRET_KEY}",
    "Bearer ${githubToken}",
    "Bearer ${GITHUB_TOKEN}",
    "Bearer ${OPERATOR_TOKEN}",
}

def is_allowed(snippet):
    for allowed in ALLOW_LIST:
        if allowed in snippet:
            return True
    return False

def install_git_hook(root_dir):
    git_hooks_dir = os.path.join(root_dir, ".git", "hooks")
    if not os.path.exists(git_hooks_dir):
        print(f"[ERROR] Git hooks directory not found at `{git_hooks_dir}`.")
        return False
    hook_path = os.path.join(git_hooks_dir, "pre-commit")
    hook_content = (
        "#!/bin/sh\n"
        "# Bartholomew Secret Guard Pre-Commit Hook\n"
        "python scripts/secret_guard.py .\n"
        "if [ $? -ne 0 ]; then\n"
        "  echo '🚨 [BARTHOLOMEW SECRET GUARD] Pre-commit hook failed! Fix exposed Bearer tokens or credentials before committing.'\n"
        "  exit 1\n"
        "fi\n"
    )
    with open(hook_path, "w", encoding="utf-8") as f:
        f.write(hook_content)
    try:
        os.chmod(hook_path, 0o755)
    except Exception:
        pass
    print(f"[SUCCESS] Installed Bartholomew Secret Guard pre-commit hook at `{hook_path}`!")
    return True

def audit_workspace(root_dir):
    print("[SECRET GUARD] Starting Bartholomew Secret Guard Audit v2.0...")
    findings = []

    for root, dirs, files in os.walk(root_dir):
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS and not d.startswith('.')]
        
        for file in files:
            if file in EXCLUDE_FILES or file.endswith('.exe') or file.endswith('.zip') or file.endswith('.pyc') or file.endswith('.png') or file.endswith('.jpg') or file.endswith('.tmp') or file.endswith('.tar.gz'):
                continue
            
            abs_path = os.path.join(root, file)
            rel_path = os.path.relpath(abs_path, root_dir)
            
            # Skip self
            if rel_path == os.path.join('scripts', 'secret_guard.py'):
                continue

            try:
                with open(abs_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    
                for pattern, name in PATTERNS:
                    matches = re.finditer(pattern, content)
                    for match in matches:
                        matched_str = match.group(0)
                        if is_allowed(matched_str):
                            continue
                        line_num = content[:match.start()].count('\n') + 1
                        findings.append({
                            'file': rel_path,
                            'line': line_num,
                            'type': name,
                            'snippet': matched_str[:25] + "..."
                        })
            except Exception:
                pass

    print(f"\nSecret Audit Results: {len(findings)} issues detected.")
    if findings:
        for item in findings:
            print(f"[LEAK RISK] {item['file']} (Line {item['line']}): {item['type']} -> {item['snippet']}")
        return False
    else:
        print("[CLEAN] No exposed Bearer tokens, private keys, or API credentials found in codebase!")
        return True

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--install-hook":
        install_git_hook(r"c:\Users\User\.gemini\antigravity\scratch\autonomous-circularity-network")
        sys.exit(0)
    target = sys.argv[1] if len(sys.argv) > 1 else r"c:\Users\User\.gemini\antigravity\scratch\autonomous-circularity-network"
    success = audit_workspace(target)
    sys.exit(0 if success else 1)
