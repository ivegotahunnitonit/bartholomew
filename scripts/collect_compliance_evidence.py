"""
Bartholomew Continuous SOC 2 & ISO 27001 Evidence Collection Script
====================================================================
Runs the 18-suite master CI security gate, generates a timestamped
Merkle audit receipt with SHA-256 root hash, and appends the evidence
record to the rolling daily audit log archive.

AICPA Trust Services Criteria Satisfied:
  CC7.1 - System monitoring of control operating effectiveness
  CC7.2 - Continuous system log collection and evaluation
  CC9.1 - Risk assessment and control verification via automated testing

ISO 27001:2022 Annex A Controls Satisfied:
  A.8.8  - Management of technical vulnerabilities (automated gate)
  A.8.30 - Monitoring activities (daily cron evidence stamping)
  A.9.1  - Performance evaluation - monitoring, measurement, analysis
"""

import os
import sys
import json
import time
import hashlib
import subprocess
import platform
from datetime import datetime, timezone
from pathlib import Path

EVIDENCE_DIR = Path("audit_evidence")
ARCHIVE_FILE = EVIDENCE_DIR / "soc2_continuous_evidence.jsonl"
RECEIPT_DIR = EVIDENCE_DIR / "daily_receipts"


def sha256_of_file(path: str) -> str:
    """Returns SHA-256 hex digest of file contents."""
    h = hashlib.sha256()
    try:
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                h.update(chunk)
    except FileNotFoundError:
        return "FILE_NOT_FOUND"
    return h.hexdigest()


def build_merkle_root(leaves: list) -> str:
    """Computes a SHA-256 Merkle root from a list of hex digest strings."""
    layer = list(leaves)
    if not layer:
        return hashlib.sha256(b"").hexdigest()
    while len(layer) > 1:
        if len(layer) % 2 == 1:
            layer.append(layer[-1])
        next_layer = []
        for i in range(0, len(layer), 2):
            combined = layer[i] + layer[i + 1]
            next_layer.append(hashlib.sha256(combined.encode()).hexdigest())
        layer = next_layer
    return layer[0]


def run_ci_gate() -> dict:
    """Runs the 18-suite CI security gate and returns results."""
    print("[BARTHOLOMEW] Running 18-suite CI Security Gate...")
    start_t = time.time()
    env = os.environ.copy()
    env["PYTHONPATH"] = "."
    proc = subprocess.run(
        [sys.executable, "ci_security_gate.py"],
        env=env,
        capture_output=True,
        text=True
    )
    elapsed = time.time() - start_t

    all_passed = proc.returncode == 0
    output_lines = (proc.stdout + proc.stderr).splitlines()

    suite_results = []
    for line in output_lines:
        if "[PASSED]" in line:
            suite_results.append({"suite": line.strip(), "status": "PASSED"})
        elif "[FAILED]" in line:
            suite_results.append({"suite": line.strip(), "status": "FAILED"})

    return {
        "all_passed": all_passed,
        "suite_results": suite_results,
        "total_suites": len(suite_results),
        "passed_suites": sum(1 for r in suite_results if r["status"] == "PASSED"),
        "elapsed_seconds": round(elapsed, 2)
    }


def collect_source_integrity_hashes() -> dict:
    """SHA-256 fingerprints of all core source modules for tamper evidence."""
    files_to_hash = [
        "src/trust_protocol.py",
        "src/ast_validator.py",
        "src/audit_merkle_tree.py",
        "src/hermetic_sandbox.py",
        "src/container_sandbox.py",
        "src/declarative_policy_engine.py",
        "ci_security_gate.py",
        "policies/default_security_policy.yaml",
        "SECURITY.md"
    ]
    return {f: sha256_of_file(f) for f in files_to_hash}


def generate_evidence_record(ci_results: dict, source_hashes: dict) -> dict:
    """Generates a timestamped, Merkle-rooted evidence record."""
    timestamp = datetime.now(timezone.utc).isoformat()

    # Compute Merkle root over all source hash values
    leaves = list(source_hashes.values())
    merkle_root = build_merkle_root(leaves)

    record = {
        "schema_version": "1.0",
        "timestamp_utc": timestamp,
        "framework": {
            "soc2_tsc": ["CC7.1", "CC7.2", "CC9.1"],
            "iso27001_annex_a": ["A.8.8", "A.8.30", "A.9.1"]
        },
        "repository": "https://github.com/ivegotahunnitonit/bartholomew",
        "release_tag": "v2.2.0",
        "platform": platform.system(),
        "python_version": platform.python_version(),
        "ci_gate": ci_results,
        "source_integrity": source_hashes,
        "merkle_root_sha256": merkle_root,
        "control_conclusion": "PASS" if ci_results["all_passed"] else "FAIL"
    }

    return record


def archive_evidence(record: dict):
    """Appends the evidence record to the JSONL rolling archive and daily receipt."""
    EVIDENCE_DIR.mkdir(exist_ok=True)
    RECEIPT_DIR.mkdir(exist_ok=True)

    # Append to rolling archive
    with open(ARCHIVE_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")

    # Write daily receipt
    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    receipt_path = RECEIPT_DIR / f"receipt_{date_str}.json"
    with open(receipt_path, "w", encoding="utf-8") as f:
        json.dump(record, f, indent=2)

    print(f"[EVIDENCE] Archived to {ARCHIVE_FILE}")
    print(f"[EVIDENCE] Daily receipt written to {receipt_path}")
    return str(receipt_path)


def main():
    print("=" * 72)
    print("BARTHOLOMEW CONTINUOUS SOC 2 & ISO 27001 EVIDENCE COLLECTOR")
    print("=" * 72)

    ci_results = run_ci_gate()
    source_hashes = collect_source_integrity_hashes()
    record = generate_evidence_record(ci_results, source_hashes)
    receipt_path = archive_evidence(record)

    print("\n" + "=" * 72)
    print(f"Control Conclusion:   {record['control_conclusion']}")
    print(f"Merkle Root (SHA256): {record['merkle_root_sha256']}")
    print(f"CI Suites Passed:     {ci_results['passed_suites']}/{ci_results['total_suites']}")
    print(f"Timestamp (UTC):      {record['timestamp_utc']}")
    print(f"TSC Controls:         {', '.join(record['framework']['soc2_tsc'])}")
    print(f"ISO 27001 Controls:   {', '.join(record['framework']['iso27001_annex_a'])}")
    print("=" * 72)

    if not ci_results["all_passed"]:
        sys.exit(1)


if __name__ == "__main__":
    main()
