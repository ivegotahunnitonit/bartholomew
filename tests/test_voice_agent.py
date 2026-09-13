"""
Unit tests for Bartholomew Voice AI Engine (BTP v5.4).
Tests audio codecs, Goertzel 1000Hz voicemail beep detection,
recipient intent classification (human vs. voicemail/IVR), AI-proofing,
phonetic email extraction, and global 24/7 timezone resolution.
"""

import pytest
import struct
import math
from datetime import datetime, timezone
from fastapi.testclient import TestClient

from src.voice.audio_codec import AudioCodec
from src.voice.audio_codecs import detect_tone_goertzel, detect_voicemail_beep
from src.voice.lead_manager import LeadManager, Lead, LeadStatus
from src.voice.sales_persona import (
    OBJECTIONS,
    CallRecipientType,
    ConversationStage,
    LiveCallState,
    classify_recipient_intent,
    extract_email_from_speech,
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


def test_goertzel_voicemail_beep_detector():
    """Verify Goertzel algorithm detects 1000Hz voicemail beep tone."""
    sample_rate = 8000.0
    num_samples = 800  # 100ms chunk

    # 1. Synthesize 1000 Hz pure sine wave (standard voicemail beep)
    beep_samples = [int(14000 * math.sin(2 * math.pi * 1000.0 * t / sample_rate)) for t in range(num_samples)]
    beep_bytes = struct.pack(f"<{len(beep_samples)}h", *beep_samples)

    is_beep, score = detect_voicemail_beep(beep_bytes, target_freq=1000.0, sample_rate=sample_rate)
    assert is_beep is True
    assert score >= 0.40

    # 2. Synthesize 300 Hz low pitch tone (non-beep voice fundamental)
    voice_samples = [int(14000 * math.sin(2 * math.pi * 300.0 * t / sample_rate)) for t in range(num_samples)]
    voice_bytes = struct.pack(f"<{len(voice_samples)}h", *voice_samples)

    is_beep_voice, score_voice = detect_voicemail_beep(voice_bytes, target_freq=1000.0, sample_rate=sample_rate)
    assert is_beep_voice is False
    assert score_voice < 0.15


def test_classify_recipient_intent():
    """Verify distinction between live humans, voicemails, and IVR systems."""
    # Voicemail phrases
    vm_samples = [
        "Hi you have reached the voicemail of Marcus Vance, please leave a message after the tone",
        "I am not available to take your call right now, please record your message at the beep",
        "The mailbox is full, cannot take your call",
    ]
    for s in vm_samples:
        rec_type, reason = classify_recipient_intent(s)
        assert rec_type == CallRecipientType.VOICEMAIL, f"Failed on: {s}"

    # Human greeting phrases
    human_samples = [
        "Hello?",
        "Hey, this is Marcus",
        "Marcus speaking, how can I help you?",
        "Yeah, who is this calling?",
    ]
    for s in human_samples:
        rec_type, reason = classify_recipient_intent(s)
        assert rec_type == CallRecipientType.HUMAN, f"Failed on: {s}"

    # IVR phrase
    ivr_sample = "Thank you for calling. Press 1 for engineering, press 2 for sales."
    rec_type_ivr, _ = classify_recipient_intent(ivr_sample)
    assert rec_type_ivr == CallRecipientType.IVR


def test_ai_proofing_and_professional_elevation():
    """Verify AI-proofing objections, anti-jailbreak grounding, and professional language."""
    categories = {o.category: o.suggested_reply for o in OBJECTIONS}

    # AI identity transparency
    assert "ai_identity" in categories
    assert "Bartholomew's real-time voice infrastructure assistant" in categories["ai_identity"]

    # Jailbreak defense
    assert "jailbreak_defense" in categories
    assert "deterministic execution boundaries" in categories["jailbreak_defense"]

    # Professional voicemail text
    vm = generate_voicemail_text("Marcus", "Synthetix AI")
    assert "Marcus" in vm
    assert "Synthetix AI" in vm
    assert "automated spend controls" in vm
    assert "dispatched a brief technical overview" in vm
    assert "haha" not in vm.lower()
    assert "bro" not in vm.lower()


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
        transcript=[{"role": "assistant", "content": "Hello Marcus"}]
    )
    
    updated = mgr.get_by_id(next_lead.id)
    assert updated.status == LeadStatus.QUALIFIED
    assert updated.call_duration_seconds == 45
    assert len(updated.transcript) == 1


def test_phonetic_email_extraction():
    """Verify speech-to-text phonetic email address extraction."""
    cases = [
        ("send it to alex at synthetix dot com please", "alex@synthetix.com"),
        ("my email is devin dot chen at hyperscale dot io", "devin.chen@hyperscale.io"),
        ("drop it to beat at alpineautonomy dot ch", "beat@alpineautonomy.ch"),
        ("email is zayd at oasisfrontier dot ae thanks", "zayd@oasisfrontier.ae"),
        ("no email here just testing", None),
    ]
    for spoken, expected in cases:
        result = extract_email_from_speech(spoken)
        assert result == expected, f"Failed for '{spoken}': got '{result}', expected '{expected}'"


def test_live_call_state_transitions():
    """Verify conversational stage progression and recipient classification."""
    state = LiveCallState(prospect_name="Kenji", company_name="Nexus Frontier Labs")
    assert state.stage == ConversationStage.OPENER

    # Turn 1: Prospect responds with short human greeting
    st1 = state.advance_turn("Speaking, what is this regarding?")
    assert state.recipient_type == CallRecipientType.HUMAN
    assert st1 == ConversationStage.PAIN_EXPLORATION

    # Turn 2: Prospect mentions LangGraph and manual approval
    st2 = state.advance_turn("We use LangGraph and approve every tool call manually to stop database drops.")
    assert "langgraph" in state.detected_frameworks
    assert "babysitting_fatigue" in state.detected_pains
    assert "destructive_action" in state.detected_pains
    assert st2 == ConversationStage.SOLUTION_BRIDGE

    # Turn 3: Prospect provides email
    st3 = state.advance_turn("Sure, send docs to kenji at nexusfrontier dot jp")
    assert st3 == ConversationStage.EMAIL_CAPTURED
    assert state.captured_email == "kenji@nexusfrontier.jp"


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

    offset, desc = resolve_prospect_timezone("+97235559876")
    assert offset == 3.0
    assert "Jerusalem" in desc

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
    test_dt = datetime(2026, 9, 9, 14, 0, tzinfo=timezone.utc)  # Wednesday
    in_hours, status = is_in_business_hours(-4.0, target_time_utc=test_dt)
    assert in_hours is True

    test_dt_night = datetime(2026, 9, 9, 3, 0, tzinfo=timezone.utc)
    in_hours, status = is_in_business_hours(-4.0, target_time_utc=test_dt_night)
    assert in_hours is False

    test_weekend = datetime(2026, 9, 12, 15, 0, tzinfo=timezone.utc)  # Saturday
    in_hours_sat, status_sat = is_in_business_hours(-4.0, target_time_utc=test_weekend, allow_weekends=False)
    assert in_hours_sat is False

    test_weekend_day = datetime(2026, 9, 12, 6, 0, tzinfo=timezone.utc)
    in_hours_apac, status_apac = is_in_business_hours(8.0, target_time_utc=test_weekend_day, allow_weekends=True)
    assert in_hours_apac is True


def test_fastapi_endpoints():
    """Test Twilio TwiML, AMD callbacks, voicemail drop, SMS dispatch, and API routes."""
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
        assert ("Nexus Frontier" in live_resp.text or "Nexus+Frontier" in live_resp.text)

        # Voicemail drop endpoint
        vm_resp = client.post("/voice/voicemail?name=Marcus&company=Synthetix")
        assert vm_resp.status_code == 200
        assert "Marcus" in vm_resp.text
        assert "<Hangup/>" in vm_resp.text

        # AMD callback test
        amd_resp = client.post("/voice/amd_callback?lead_id=dummy_id", data={"AnsweredBy": "machine_start", "CallSid": "CA12345"})
        assert amd_resp.status_code == 200
        assert amd_resp.json()["answered_by"] == "machine_start"

        # Campaign status API
        camp_resp = client.get("/api/campaign/status")
        assert camp_resp.status_code == 200
        assert "active_business_regions" in camp_resp.json()
        assert "total_pipeline_value_usd" in camp_resp.json()

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

        # Create dynamic test lead
        create_resp = client.post("/api/leads", json={
            "name": "Alex Test",
            "company": "Test Enterprise Corp",
            "phone": "+15559990000",
            "email": "test@enterprise.ai",
            "role": "CTO"
        })
        assert create_resp.status_code == 200
        test_lead_id = create_resp.json()["lead"]["id"]

        # SMS follow-up endpoint test
        sms_resp = client.post(f"/api/leads/{test_lead_id}/send_sms", json={})
        assert sms_resp.status_code == 200
        assert sms_resp.json()["status"] == "sms_dispatched"

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


def test_intent_driven_curiosity_and_objection_holding():
    """Verify that technical inquiries hold the stage without prematurely rushing to close."""
    state = LiveCallState(prospect_name="Elena", company_name="Sovereign AI Systems")
    assert state.stage == ConversationStage.GREETING_AND_HOOK

    # Turn 1: Acknowledge hook
    s1 = state.advance_turn("Hey Alex, yeah I have 30 seconds. What's this about?")
    assert s1 == ConversationStage.TECHNICAL_DISCOVERY

    # Turn 2: Mention stack
    s2 = state.advance_turn("We run LangGraph agents with custom tools on AWS.")
    assert "langgraph" in state.detected_frameworks
    assert s2 in (ConversationStage.PAIN_AMPLIFICATION, ConversationStage.SOLUTION_FRAMING)

    # Turn 3: Technical inquiry - MUST hold in SOLUTION_FRAMING, not rush to close!
    s3 = state.advance_turn("How does Bartholomew achieve sub-35us latency without calling an LLM guardrail?")
    assert s3 == ConversationStage.SOLUTION_FRAMING

    # Turn 4: Objection raised - transitions to OBJECTION_RESOLUTION
    s4 = state.advance_turn("Wait, are you an AI or a real engineer?")
    assert s4 == ConversationStage.OBJECTION_RESOLUTION

    # Turn 5: Receptive consent given -> ACTION_DISPATCH
    s5 = state.advance_turn("That's impressive. Sure, shoot me the quickstart repo link.")
    assert s5 == ConversationStage.ACTION_DISPATCH


def test_role_and_sentiment_adaptation():
    """Verify entity role extraction, sentiment classification, and adaptive prompt injection."""
    state = LiveCallState(prospect_name="Elena", company_name="Sovereign AI Systems")
    
    # Caller introduces role and frustration
    state.advance_turn("I am the VP of Engineering here. We had a terrible outage when an agent dropped a staging table.")
    assert state.detected_role == "Vp Of Engineering"
    assert state.detected_sentiment == "FRUSTRATED"
    assert "destructive_action" in state.detected_pains

    prompt = generate_session_instructions(
        prospect_name=state.prospect_name,
        company_name=state.company_name,
        current_stage=state.stage,
        detected_pains=state.detected_pains,
        caller_role=state.detected_role,
        caller_sentiment=state.detected_sentiment
    )
    assert "Caller Role: Vp Of Engineering" in prompt
    assert "CALLER SENTIMENT: FRUSTRATED" in prompt
    assert "destructive_action" in prompt


def test_gemini_voice_tool_declarations():
    """Verify function calling schemas registered for Gemini Live full-duplex session."""
    from src.voice.sales_persona import VOICE_TOOL_DECLARATIONS
    tool_names = [t["name"] for t in VOICE_TOOL_DECLARATIONS]
    assert "check_framework_compatibility" in tool_names
    assert "dispatch_quickstart_email" in tool_names
    assert "log_detected_stack" in tool_names
    assert "schedule_followup" in tool_names
    assert "drop_voicemail_and_hangup" in tool_names

    email_tool = next(t for t in VOICE_TOOL_DECLARATIONS if t["name"] == "dispatch_quickstart_email")
    assert "email" in email_tool["parameters"]["required"]
    assert "recipient_name" in email_tool["parameters"]["properties"]


def test_modular_prompt_engine_stages():
    """Verify that dynamic stage instructions inject stage-specific technical objectives."""
    p_discovery = generate_session_instructions(
        prospect_name="Marcus",
        company_name="Astra Labs",
        current_stage=ConversationStage.TECHNICAL_DISCOVERY
    )
    assert "CURRENT OBJECTIVE: TECHNICAL DISCOVERY" in p_discovery
    assert "Marcus" in p_discovery

    p_solution = generate_session_instructions(
        prospect_name="Marcus",
        company_name="Astra Labs",
        current_stage=ConversationStage.SOLUTION_FRAMING
    )
    assert "CURRENT OBJECTIVE: HIGH-SIGNAL ARCHITECTURAL INSIGHT" in p_solution
    assert "35 microseconds" in p_solution

    p_dispatch = generate_session_instructions(
        prospect_name="Marcus",
        company_name="Astra Labs",
        current_stage=ConversationStage.ACTION_DISPATCH
    )
    assert "CURRENT OBJECTIVE: OFFER LOW-FRICTION TECHNICAL ASSET" in p_dispatch


def test_framework_compatibility_lookup():
    """Verify sub-35 microsecond lookup and integration facts for AI frameworks."""
    from src.voice.sales_persona import get_framework_compatibility_info

    lg = get_framework_compatibility_info("LangGraph")
    assert lg["supported"] is True
    assert lg["latency_microseconds"] <= 35
    assert "LangGraph" in lg["framework"]

    cc = get_framework_compatibility_info("claude_code")
    assert cc["supported"] is True
    assert "AnthropicComputerUseGuard" in cc["integration"]

    generic = get_framework_compatibility_info("custom_inhouse_agent")
    assert generic["supported"] is True
    assert generic["latency_microseconds"] == 35


def test_build_natural_ssml():
    """Verify SSML synthesis adds prosodic tags and escapes characters."""
    from src.voice.sales_persona import build_natural_ssml

    raw = "Hey, Alex here. We do AST filtering in under 35µs for your CLI tools..."
    ssml = build_natural_ssml(raw)
    assert "<prosody rate=\"103%\">" in ssml
    assert "</prosody>" in ssml
    assert '<say-as interpret-as="characters">AST</say-as>' in ssml
    assert '<say-as interpret-as="characters">CLI</say-as>' in ssml
    assert '<break time="150ms"/>' in ssml
    assert "35 microseconds" in ssml


def test_find_matching_objection_reply():
    """Verify rapid detection and authoritative answers to developer curveballs."""
    from src.voice.sales_persona import find_matching_objection_reply

    r_ai = find_matching_objection_reply("Wait, are you an AI or a human?")
    assert r_ai is not None
    assert "Gemini Live" in r_ai

    r_obs = find_matching_objection_reply("We already use LangSmith for tracing")
    assert r_obs is not None
    assert "tracing" in r_obs

    r_ebpf = find_matching_objection_reply("Is this based on eBPF?")
    assert r_ebpf is not None
    assert "kernel" in r_ebpf

    r_proof = find_matching_objection_reply("Who else uses this in production?")
    assert r_proof is not None
    assert "Synthetix" in r_proof

    r_time = find_matching_objection_reply("How long does it take to integrate?")
    assert r_time is not None
    assert "five minutes" in r_time

    r_air = find_matching_objection_reply("Can we run this offline in an air gapped VPC?")
    assert r_air is not None
    assert "offline" in r_air

    r_spend = find_matching_objection_reply("Can it stop runaway spend from infinite loops?")
    assert r_spend is not None
    assert "recursive" in r_spend

    r_latency = find_matching_objection_reply("What is the latency overhead on tool calls?")
    assert r_latency is not None
    assert "35 microseconds" in r_latency

    r_code = find_matching_objection_reply("Does this work with Claude Code or Cursor?")
    assert r_code is not None
    assert "Claude Code" in r_code

    r_soc2 = find_matching_objection_reply("We need an audit log for SOC2 compliance")
    assert r_soc2 is not None
    assert "SOC2" in r_soc2

    r_false = find_matching_objection_reply("What about false positives blocking developers?")
    assert r_false is not None
    assert "false positives" in r_false

    r_none = find_matching_objection_reply("The weather in Calgary is nice today")
    assert r_none is None


def test_twilio_status_callback_lifecycle():
    """Verify call completion webhook updates duration, transcript, and lead status."""
    from src.voice.twilio_server import app, lead_mgr, active_call_states
    from src.voice.sales_persona import LiveCallState

    client = TestClient(app)
    lead = lead_mgr.get_next_pending()
    assert lead is not None

    test_sid = "CA_TEST_LIFECYCLE_99"
    active_call_states[test_sid] = LiveCallState(prospect_name=lead.name, captured_email="test@company.ai")

    resp = client.post(
        f"/voice/status_callback?lead_id={lead.id}",
        data={
            "CallSid": test_sid,
            "CallStatus": "completed",
            "CallDuration": "42"
        }
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "recorded"
    assert resp.json()["duration"] == 42

    updated_lead = lead_mgr.get_by_id(lead.id)
    assert updated_lead.call_duration_seconds == 42
    assert updated_lead.status == LeadStatus.QUALIFIED
    assert updated_lead.email == "test@company.ai"


def test_voice_metrics_endpoint():
    """Verify real-time engine telemetry endpoint."""
    from src.voice.twilio_server import app
    client = TestClient(app)

    resp = client.get("/api/voice/metrics")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "online"
    assert data["sub_35us_deterministic_gate"] is True
    assert data["default_voice"] == "Google.en-US-Journey-D"


@pytest.mark.anyio
async def test_sse_voice_events():
    """Verify Server-Sent Events broadcasting to subscriber queues."""
    import asyncio
    from src.voice.twilio_server import broadcast_event, event_subscribers

    q = asyncio.Queue()
    event_subscribers.append(q)
    try:
        await broadcast_event("transcript", {"user_speech": "hello", "alex_reply": "hey"})
        msg = await asyncio.wait_for(q.get(), timeout=1.0)
        assert "event: transcript" in msg
        assert "alex_reply" in msg
    finally:
        if q in event_subscribers:
            event_subscribers.remove(q)


def test_webhook_dispatch_endpoint():
    """Verify CRM webhook test dispatch endpoint."""
    from src.voice.twilio_server import app
    client = TestClient(app)

    resp = client.post("/api/webhook/test")
    assert resp.status_code == 200
    data = resp.json()
    assert "status" in data
    assert "configured_url" in data
    assert data["test_payload"]["name"] == "Marcus Vance"




