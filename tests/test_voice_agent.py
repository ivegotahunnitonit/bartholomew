"""
Unit tests for Bartholomew Voice AI Engine (BTP v5.4).
"""

import pytest
import struct
import math
from fastapi.testclient import TestClient

from src.voice.audio_codec import AudioCodec
from src.voice.lead_manager import LeadManager, Lead, LeadStatus
from src.voice.sales_persona import OBJECTIONS, generate_session_instructions
from src.voice.twilio_server import app


def test_audio_codec_mulaw_roundtrip():
    """Verify mu-law encode and decode preserves signals."""
    # Generate 16-bit PCM sine wave
    samples = [int(12000 * math.sin(2 * math.pi * 440 * t / 8000)) for t in range(400)]
    pcm_bytes = struct.pack(f"<{len(samples)}h", *samples)
    
    # Encode to mu-law
    mulaw = AudioCodec.pcm16_to_mulaw(pcm_bytes)
    assert len(mulaw) == len(samples)
    
    # Decode back
    recovered = AudioCodec.mulaw_to_pcm16(mulaw)
    assert len(recovered) == len(pcm_bytes)
    
    # Check RMS difference is within mu-law quantization error bounds
    orig_rms = AudioCodec.calculate_rms(pcm_bytes)
    rec_rms = AudioCodec.calculate_rms(recovered)
    assert abs(orig_rms - rec_rms) / orig_rms < 0.05


def test_audio_codec_resampling():
    """Verify 3:1 sample rate conversion."""
    samples = [1000] * 100
    pcm_8k = struct.pack(f"<{len(samples)}h", *samples)
    
    # Upsample 8k -> 24k
    pcm_24k = AudioCodec.resample_8k_to_24k(pcm_8k)
    assert len(pcm_24k) == len(pcm_8k) * 3
    
    # Downsample 24k -> 8k
    pcm_back = AudioCodec.resample_24k_to_8k(pcm_24k)
    assert len(pcm_back) == len(pcm_8k)


def test_lead_manager_lifecycle(tmp_path):
    """Test lead manager queue operations."""
    test_file = tmp_path / "test_leads.json"
    mgr = LeadManager(storage_file=test_file)
    
    # Check seeded leads
    leads = mgr.get_all()
    assert len(leads) >= 4
    
    # Fetch next pending
    next_lead = mgr.get_next_pending()
    assert next_lead is not None
    assert next_lead.status == LeadStatus.PENDING
    
    # Update outcome
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
    """Test prompt customization and objection keywords."""
    prompt = generate_session_instructions(prospect_name="Elena", company_name="VectorFlow")
    assert "Elena" in prompt
    assert "VectorFlow" in prompt
    assert "Bartholomew" in prompt
    assert "pip install btp-guard" in prompt

    # Verify all objection categories exist
    categories = [o.category for o in OBJECTIONS]
    assert "existing_guardrails" in categories
    assert "pricing" in categories
    assert "busy" in categories
    assert "send_email" in categories


def test_fastapi_endpoints():
    """Test Twilio TwiML and API routes."""
    client = TestClient(app)
    
    # TwiML endpoint
    resp = client.post("/voice/twiml")
    assert resp.status_code == 200
    assert "<Stream" in resp.text
    assert "voice/stream" in resp.text

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
