"""
Test Suite for Bartholomew Production Deploy Gate & SOC-2 Compliance Exporter
Verifies the mandatory gating mechanism and regulatory evidence generation.
"""

import sys
import os
import json
import tempfile

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.trust_protocol import BartholomewTrustAuthority
from src.deploy_gate import ProductionDeployGate
from src.compliance_exporter import ComplianceEvidenceExporter

def test_production_deployment_gate():
    print("=" * 80)
    print("  TESTING BARTHOLOMEW MANDATORY PRODUCTION DEPLOYMENT GATE")
    print("=" * 80)
    
    authority = BartholomewTrustAuthority()
    gate = ProductionDeployGate(trusted_authority_pubkey=authority.public_key_hex)
    
    # 1. Test Missing Receipt (Must be Refused)
    ok, msg = gate.verify_pipeline_deployment("non_existent_receipt.json", {"code": "print(1)"})
    print(f"[TEST 1: MISSING RECEIPT] Result: {msg}")
    assert not ok
    assert "REFUSED" in msg

    # 2. Test Legitimate Bartholomew Signed Receipt
    valid_payload = {"target_file": "billing.py", "delta_lines": 3, "patch": "def fix(): pass"}
    packet = authority.evaluate_intent(
        agent_id="Agent-OpenAI-GPT4o",
        action_type="DEPLOY_PATCH",
        payload=valid_payload
    )
    
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
        json.dump(packet, f)
        receipt_path = f.name
        
    try:
        ok, msg = gate.verify_pipeline_deployment(receipt_path, valid_payload)
        print(f"[TEST 2: VALID SIGNED RECEIPT] Result: {msg}")
        assert ok
        assert "AUTHORIZED" in msg

        # 3. Test Payload Tampering Attack (Modified code after receipt issuance)
        tampered_payload = {"target_file": "billing.py", "delta_lines": 3, "malicious_backdoor": "eval(req)"}
        ok, msg = gate.verify_pipeline_deployment(receipt_path, tampered_payload)
        print(f"[TEST 3: TAMPERED CODE] Result: {msg}")
        assert not ok
        assert "Payload Tampering Detected" in msg
    finally:
        if os.path.exists(receipt_path):
            os.remove(receipt_path)
            
    print("[PASS] Production Deployment Gate verified 100%!")

def test_soc2_compliance_exporter():
    print("\n" + "=" * 80)
    print("  TESTING SOC-2 / NIST AI RMF COMPLIANCE EVIDENCE EXPORTER")
    print("=" * 80)
    
    exporter = ComplianceEvidenceExporter(organization_name="Fintech Global Enterprise")
    
    mock_records = [
        {"action_id": "ACT-001", "agent": "Agent-A", "action": "DEPLOY_PATCH", "verdict": "ALLOW", "latency_us": 129.5},
        {"action_id": "ACT-002", "agent": "Agent-B", "action": "EXEC_SHELL", "verdict": "DENY", "reason": "Secret exfiltration attempt blocked", "latency_us": 2.6},
        {"action_id": "ACT-003", "agent": "Agent-C", "action": "DB_MIGRATION", "verdict": "ALLOW", "latency_us": 140.2}
    ]
    
    bundle = exporter.generate_compliance_bundle(mock_records)
    out_file = exporter.export_to_file(bundle, "SOC2_COMPLIANCE_EVIDENCE_PACK.json")
    
    print(f"[COMPLIANCE BUNDLE GENERATED] File: {out_file} | Report ID: {bundle['report_id']}")
    print(f"  ├─ Monitored Actions: {bundle['telemetry_summary']['total_autonomous_actions_monitored']}")
    print(f"  ├─ Threats Blocked:   {bundle['telemetry_summary']['security_threats_blocked']}")
    print(f"  └─ Frameworks:        {len(bundle['frameworks_covered'])} Standard Certifications Mapped")
    
    assert bundle["telemetry_summary"]["cryptographic_integrity_rate"] == "100.00%"
    assert os.path.exists(out_file)
    print("[PASS] SOC-2 Compliance Evidence Exporter verified 100%!")

if __name__ == "__main__":
    test_production_deployment_gate()
    test_soc2_compliance_exporter()
    print("\n[OK] All Deployment Gate & Compliance tests passed successfully.")
