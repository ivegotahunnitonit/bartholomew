"""
Sanitize Synthetic Test Secrets
================================
Replaces dummy test tokens with sanitized mock strings to prevent GitGuardian
false positive alerts on test suites.
"""

import os
import glob
import re

REPLACEMENTS = [
    (r"ghp_[0-9a-zA-Z]{20,}", "ghp_MOCK_TEST_TOKEN_FOR_AUDIT_VERIFICATION_ONLY_0000"),
    (r"sk-(?!ant-)(?:proj-)?[0-9a-zA-Z]{20,}", "sk-proj-MOCK_OPENAI_KEY_FOR_TESTING_PURPOSES_ONLY_0000"),
    (r"sk-ant-[0-9a-zA-Z]{20,}", "sk-ant-MOCK_ANTHROPIC_KEY_TEST_ONLY_0000"),
    (r"AKIAIOSFODNN7EXAMPLE", "AKIA_MOCK_AWS_KEY_FOR_TESTS_0000"),
    (r"AIza[0-9a-zA-Z_\-]{30,40}", "AIzaSy_MOCK_GOOGLE_API_KEY_TEST_000000000"),
]

TARGET_FILES = [
    "examples/migrations/autogen_to_okf/test_migrate_autogen.py",
    "examples/migrations/chatgpt_export_to_okf/test_migrate_chatgpt.py",
    "examples/migrations/crewai_to_okf/test_migrate_crewai.py",
    "examples/migrations/langmem_to_okf/test_migrate_langmem.py",
    "examples/sovereign_memory_dreaming.py",
    "pypi_package/bartholomew_eval/fuzzer.py",
    "pypi_package/test_trust_artifact.py",
    "python_backend/bartholomew_eval/bartholomew_eval/fuzzer.py",
    "python_backend/bartholomew_eval/fuzzer.py",
    "scripts/demo_live_bedrock_suite.py",
    "scripts/secret_guard.py",
    "scripts/test_live_aws_bedrock.py",
    "test_1m_million_invariant_fuzzer.py",
    "test_agentic_eval_security.py",
    "test_bartholomew_eval.py",
    "test_secret_masker.py",
    "tests/test_massive_fuzzing_suite.py",
    "web/src/components/CommandCenter.tsx",
    "web/src/components/InteractiveAgentSandbox.tsx",
]

def sanitize():
    for fpath in TARGET_FILES:
        if not os.path.exists(fpath):
            continue
        with open(fpath, "r", encoding="utf-8") as f:
            content = f.read()
        
        orig = content
        for pattern, repl in REPLACEMENTS:
            content = re.sub(pattern, repl, content)
        
        if content != orig:
            with open(fpath, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"[OK] Sanitized mock tokens in: {fpath}")

if __name__ == "__main__":
    sanitize()
