"""
Unit tests for Bartholomew Voice AI Engine (BTP v5.4).
Tests audio codecs, lead workflows, sales persona prosody, AMD callbacks,
and global 24/7 timezone resolution.
"""

import pytest
import struct
import math
from datetime import datetime, timezone
from fastapi.testclient import TestClient

from src.voice.audio_codec import AudioCodec
from src.voice.lead_manager import LeadManager, Lead, LeadStatus
from src.voice.sales_persona import (
    OBJECTIONS,
    generate_session_instructions,
    generate_voicemail_text,
    format_speech_for_natural_delivery
)
from src.voice.global_campaign_runner import (
    resolve_prospect_timezone,
    is_in_business_hours,
    GlobalCampaignRunner
)
from src.voice.twilio_server import app


def test_audio_codec_mulaw_roundtrip():
    """Verify mu-law encode and decode preserves signals."""
    samples = [int(12000 * math.sin(2 * math.pi * 440 * t / 8000)) for t in range(400)]
    pcm_bytes = struct.pack(f"<{len(samples)}h", *samples)
    
    mulaw = AudioCodec.pcm16_to_mulaw(pcm_bytes)
    assert len(mulaw) == len(samples)
    
    recovered = AudioCodec.mulaw_to_pcm16(mulaw)
    assert len(recovered) == len(pcm_bytes)
    
    orig_rms = AudioCodec.calculate_rms(pcm_bytes)
    rec_rms = AudioCodec.calculate_rms(recovered)
    assert abs(orig_rms - rec_rms) / orig_rms < 0.05


def test_audio_codec_resampling():
    """Verify 3:1 sample rate conversion."""
    samples = [1000] * 100
    pcm_8k = struct.pack(f"<{len(samples)}h", *samples)
    
    pcm_24k = AudioCodec.resample_8k_to_24k(pcm_8k)
    assert len(pcm_24k) == len(pcm_8k) * 3
    
    pcm_back = AudioCodec.resample_24k_to_8k(pcm_24k)
    assert len(pcm_back) == len(pcm_8k)


def test_lead_manager_lifecycle(tmp_path):
    """Test lead manager queue operations."""
    test_file = tmp_path / "test_leads.json"
    mgr = LeadManager(storage_file=test_file)
    
    leads = mgr.get_all()
    assert len(leads) >= 4
    
    next_lead = mgr.get_next_pending()
    assert next_lead is not None
    assert next_lead.status == LeadStatus.PENDING
    
    mgr.update_lead_outcome(
        lead_id=next_lead.id,
        status=LeadStatus.QUALIFIED,
        duration=45,
        transcript=[{"role": "assistant", "content": "Hey Marcus"}]
    )
    
    updated = mgr.get_by_id(next_lead.id)
    assert updated.status == LeadStatus.QUALIFIED
    assert updated.call_duration_seconds == 45
    assert len(updated.transcript) == 1


def test_sales_persona_prompt_and_objections():
    """Test prompt customization, prosody formatting, and objection keywords."""
    prompt = generate_session_instructions(prospect_name="Elena Rostova", company_name="VectorFlow", tech_stack="LangGraph")
    assert "Elena" in prompt
    assert "VectorFlow" in prompt
    assert "LangGraph" in prompt
    assert "Bartholomew" in prompt
    assert "pip install btp-guard" in prompt

    # Verify voicemail generation
    vm = generate_voicemail_text("Elena Rostova", "VectorFlow")
    assert "Elena" in vm
    assert "VectorFlow" in vm
    assert "35-microsecond" in vm

    # Verify natural prosody formatting
    formatted = format_speech_for_natural_delivery("Hello - this is Alex - testing pacing")
    assert "..." in formatted

    # Verify all objection categories exist
    categories = [o.category for o in OBJECTIONS]
    assert "existing_guardrails" in categories
    assert "pricing" in categories
    assert "busy" in categories
    assert "send_email" in categories
    assert "mcp_tools" in categories
    assert "in_house" in categories


def test_global_timezone_resolution():
    """Verify international prefix and area code timezone resolution."""
    # US & Canada
    offset, desc = resolve_prospect_timezone("+14155551234")
    assert offset == -7.0
    assert "Pacific" in desc

    offset, desc = resolve_prospect_timezone("+14165559876")
    assert offset == -4.0
    assert "Eastern" in desc

    # EMEA
    offset, desc = resolve_prospect_timezone("+442079460912")
    assert offset == 1.0
    assert "London" in desc

    offset, desc = resolve_prospect_timezone("+35315554321")
    assert offset == 1.0
    assert "Dublin" in desc

    offset, desc = resolve_prospect_timezone("+97145558901")
    assert offset == 4.0
    assert "Dubai" in desc

    # APAC
    offset, desc = resolve_prospect_timezone("+81355556789")
    assert offset == 9.0
    assert "Tokyo" in desc

    offset, desc = resolve_prospect_timezone("+6565554321")
    assert offset == 8.0
    assert "Singapore" in desc

    offset, desc = resolve_prospect_timezone("+91805552345")
    assert offset == 5.5
    assert "Kolkata" in desc


def test_business_hours_checker():
    """Test business hours calculation across weekday and weekend windows."""
    # Weekday 14:00 UTC (10:00 AM Eastern at UTC-4) -> in hours
    test_dt = datetime(2026, 9, 9, 14, 0, tzinfo=timezone.utc)  # Wednesday
    in_hours, status = is_in_business_hours(-4.0, target_time_utc=test_dt)
    assert in_hours is True

    # Weekday 03:00 UTC (23:00 PM Eastern at UTC-4) -> off hours
    test_dt_night = datetime(2026, 9, 9, 3, 0, tzinfo=timezone.utc)
    in_hours, status = is_in_business_hours(-4.0, target_time_utc=test_dt_night)
    assert in_hours is False

    # Weekend without allow_weekends -> False
    test_weekend = datetime(2026, 9, 12, 15, 0, tzinfo=timezone.utc)  # Saturday
    in_hours_sat, status_sat = is_in_business_hours(-4.0, target_time_utc=test_weekend, allow_weekends=False)
    assert in_hours_sat is False

    # Weekend with allow_weekends at 12:00 local time -> True
    # At UTC+8 (Singapore/Tokyo), 06:00 UTC is 14:00 (2:00 PM) local
    test_weekend_day = datetime(2026, 9, 12, 6, 0, tzinfo=timezone.utc)
    in_hours_apac, status_apac = is_in_business_hours(8.0, target_time_utc=test_weekend_day, allow_weekends=True)
    assert in_hours_apac is True


def test_fastapi_endpoints():
    """Test Twilio TwiML, AMD callbacks, voicemail drop, and API routes."""
    from src.voice.twilio_server import lead_mgr
    original_leads_content = None
    if lead_mgr.storage_file.exists():
        original_leads_content = lead_mgr.storage_file.read_bytes()

    try:
        client = TestClient(app)
        
        # TwiML endpoint
        resp = client.post("/voice/twiml")
        assert resp.status_code == 200
        assert "<Stream" in resp.text
        assert "voice/stream" in resp.text

        # Live stream entrypoint with context
        live_resp = client.post("/voice/live_stream?name=Kenji&company=Nexus+Frontier")
        assert live_resp.status_code == 200
        assert "Kenji" in live_resp.text
        assert "Nexus+Frontier" in live_resp.text

        # Voicemail drop endpoint
        vm_resp = client.post("/voice/voicemail?name=Marcus&company=Synthetix")
        assert vm_resp.status_code == 200
        assert "Marcus" in vm_resp.text
        assert "<Hangup/>" in vm_resp.text

        # AMD callback test
        amd_resp = client.post("/voice/amd_callback?lead_id=dummy_id", data={"AnsweredBy": "machine_start", "CallSid": "CA12345"})
        assert amd_resp.status_code == 200
        assert amd_resp.json()["answered_by"] == "machine_start"

        # Leads API
        leads_resp = client.get("/api/leads")
        assert leads_resp.status_code == 200
        data = leads_resp.json()
        assert "leads" in data
        assert len(data["leads"]) > 0

        # Dial simulation response
        dial_resp = client.post("/api/dial?phone=%2B15550001111")
        assert dial_resp.status_code == 200
        assert "status" in dial_resp.json()

        # Leads summary endpoint
        summary_resp = client.get("/api/leads/summary")
        assert summary_resp.status_code == 200
        sum_data = summary_resp.json()
        assert "total_leads" in sum_data
        assert "total_pipeline_value_usd" in sum_data

        # Create a dynamic test lead to keep production queue clean
        create_resp = client.post("/api/leads", json={
            "name": "Alex Test",
            "company": "Test Enterprise Corp",
            "phone": "+15559990000",
            "email": "test@enterprise.ai",
            "role": "CTO"
        })
        assert create_resp.status_code == 200
        test_lead_id = create_resp.json()["lead"]["id"]

        # Qualify and send proposal on the test lead
        qual_resp = client.post(f"/api/leads/{test_lead_id}/qualify", json={"notes": "Agreed to trial", "email": "test@enterprise.ai"})
        assert qual_resp.status_code == 200
        assert qual_resp.json()["lead"]["status"] == "QUALIFIED"

        prop_resp = client.post(f"/api/leads/{test_lead_id}/send_proposal", json={"tier": "pro"})
        assert prop_resp.status_code == 200
        assert prop_resp.json()["proposal"]["tier"] == "Pro Startup ($49/mo)"

        close_resp = client.post(f"/api/leads/{test_lead_id}/close", json={"tier": "enterprise", "deal_value_usd": 199.0})
        assert close_resp.status_code == 200
        assert close_resp.json()["lead"]["status"] == "CLOSED_WON"
        assert close_resp.json()["lead"]["deal_value_usd"] == 199.0

    finally:
        if original_leads_content is not None:
            lead_mgr.storage_file.write_bytes(original_leads_content)
            lead_mgr._load_or_seed()
