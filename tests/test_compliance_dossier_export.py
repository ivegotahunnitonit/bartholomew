"""
Tests for BTP Multi-Tenant Compliance Dossier Exporter.
Verifies SOC 2 Type II, EU AI Act, and ISO 27001 evidence assembly,
Merkle root integrity, HMAC signatures, and CLI export commands.
"""

import os
import json
import tempfile
import argparse
import pytest

from src.compliance_dossier_exporter import ComplianceDossierExporter
from cli import cmd_audit


def test_compliance_dossier_assembly_and_merkle():
    exporter = ComplianceDossierExporter(
        tenant_id="ten_clinical_mesh_prod",
        org_id="Novartis Health Mesh",
        project_id="clinical-data-lake"
    )
    dossier = exporter.build_dossier()

    assert dossier["report_id"].startswith("DOSSIER-")
    assert dossier["tenant_id"] == "ten_clinical_mesh_prod"
    assert dossier["organization"] == "Novartis Health Mesh"
    assert len(dossier["compliance_frameworks"]) >= 4
    
    # Merkle verification
    merkle = dossier["merkle_verification"]
    assert len(merkle["merkle_root_hash"]) == 64
    assert merkle["cryptographic_signature"].startswith("btp_audit_")

    # Metrics
    metrics = dossier["telemetry_metrics"]
    assert metrics["total_intents_audited"] >= 4
    assert metrics["threats_intercepted"] >= 1
    assert metrics["clean_intents_verified"] >= 1


def test_markdown_and_file_export():
    with tempfile.TemporaryDirectory() as temp_dir:
        out_path = os.path.join(temp_dir, "SOC2_EVIDENCE_DOSSIER.md")
        exporter = ComplianceDossierExporter(
            tenant_id="ten_acme_corp_dev",
            org_id="Acme Corp",
            project_id="finance-agent"
        )
        md_text = exporter.export_markdown_dossier(output_path=out_path)

        assert os.path.exists(out_path)
        assert "# Bartholomew Trust Protocol (BTP)" in md_text
        assert "SOC 2 Type II" in md_text
        assert "EU AI Act Art. 14" in md_text
        assert "Merkle Root Hash" in md_text
        assert "btp_audit_" in md_text


def test_cli_audit_dossier_command(capsys):
    with tempfile.TemporaryDirectory() as temp_dir:
        out_json = os.path.join(temp_dir, "evidence.json")
        args_json = argparse.Namespace(
            path=".",
            dossier=True,
            tenant="ten_test_org_prod",
            org="Test AI Labs",
            format="json",
            out=out_json
        )
        cmd_audit(args_json)
        captured = capsys.readouterr()
        assert "Cryptographic evidence pack saved to" in captured.out
        assert os.path.exists(out_json)

        with open(out_json, "r", encoding="utf-8") as f:
            pack = json.load(f)
            assert pack["tenant_id"] == "ten_test_org_prod"
            assert pack["organization"] == "Test AI Labs"
            assert "merkle_root_hash" in pack["merkle_verification"]

        # Test markdown direct stdout
        args_md = argparse.Namespace(
            path=".",
            dossier=True,
            tenant="ten_test_org_prod",
            org="Test AI Labs",
            format="md",
            out=None
        )
        cmd_audit(args_md)
        captured_md = capsys.readouterr()
        assert "Autonomous Agent Cryptographic Compliance Dossier" in captured_md.out
