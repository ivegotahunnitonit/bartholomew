import os
import sys
import pytest

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from src.compliance_report_generator import ComplianceReportGenerator


def test_compliance_report_generation(tmp_path):
    generator = ComplianceReportGenerator(organization_name="FinTech Bot Swarm Inc", policy_id="urn:btp:policy:banking-v1")

    sample_receipts = [
        {"agent": "bot-1", "action": "CHECK_BALANCE", "verdict": "ALLOW", "nonce": "n1"},
        {"agent": "bot-2", "action": "TRANSFER_FUNDS", "verdict": "ALLOW", "nonce": "n2"},
        {"agent": "bot-3", "action": "DROP_TABLE", "verdict": "DENY", "nonce": "n3"},
        {"agent": "bot-4", "action": "HIGH_VALUE_WIRE", "verdict": "CO_SIGN_REQUIRED", "nonce": "n4"},
    ]
    generator.ingest_receipts(sample_receipts)

    pkg = generator.generate_audit_package()
    assert pkg["organization"] == "FinTech Bot Swarm Inc"
    assert pkg["total_evaluated_intents"] == 4
    assert pkg["summary_metrics"]["total_allowed"] == 2
    assert pkg["summary_metrics"]["total_blocked_threats"] == 1
    assert pkg["summary_metrics"]["total_human_co_signed"] == 1
    assert len(pkg["merkle_root_hash"]) == 64

    # Test HTML report export
    out_file = str(tmp_path / "compliance_report.html")
    exported_path = generator.export_html_report(out_file)
    assert os.path.exists(exported_path)
    with open(exported_path, "r", encoding="utf-8") as f:
        content = f.read()
    assert "FinTech Bot Swarm Inc" in content
    assert pkg["merkle_root_hash"] in content


if __name__ == "__main__":
    import tempfile
    import pathlib
    with tempfile.TemporaryDirectory() as td:
        test_compliance_report_generation(pathlib.Path(td))
    print("[OK] ALL COMPLIANCE REPORT GENERATOR TESTS PASSED!")
