"""
Bartholomew Trust Protocol (BTP v5.4) — Twilio Voice Server & Interactive Web Bench
Provides FastAPI routes, Twilio bi-directional MediaStream WebSockets,
outbound dialing endpoints, Answering Machine Detection (AMD), and browser test benches.
"""

import asyncio
import json
import logging
import os
import urllib.parse
from pathlib import Path
from typing import Dict, Any, Optional, List

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request, Response, Form, HTTPException
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from .voice_config import config, VoiceConfig
from .audio_codec import AudioCodec
from .sales_persona import (
    OBJECTIONS,
    generate_session_instructions,
    generate_voicemail_text,
    format_speech_for_natural_delivery
)
from .lead_manager import LeadManager, Lead, LeadStatus
from .realtime_session import RealtimeVoiceSession

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("btp.voice.server")

app = FastAPI(title="Bartholomew Voice AI Server", version="5.4.0")

# Enable CORS for local testing
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

lead_mgr = LeadManager()
active_sessions: Dict[str, RealtimeVoiceSession] = {}
conversation_histories: Dict[str, List[Any]] = {}
active_call_states: Dict[str, Any] = {}


def get_gemini_alex_reply(user_speech: str, call_sid: str) -> str:
    """Queries conversational AI in real-time with full multi-turn memory, entity tracking, and model fallback."""
    from src.voice.sales_persona import (
        classify_recipient_intent,
        CallRecipientType,
        generate_voicemail_text,
        LiveCallState
    )

    if call_sid not in active_call_states:
        active_call_states[call_sid] = LiveCallState()
    call_state = active_call_states[call_sid]

    # 1. Update FSM, extract frameworks, operational pains, and prospect name
    stage = call_state.advance_turn(user_speech)

    # 2. Check if answering party is voicemail/IVR
    rec_type, reason = classify_recipient_intent(user_speech)
    if rec_type in (CallRecipientType.VOICEMAIL, CallRecipientType.IVR):
        logger.info(f"Voicemail detected during speech analysis [{call_sid}]: {reason}")
        reply = format_speech_for_natural_delivery(generate_voicemail_text(call_state.prospect_name, call_state.company_name))
        return reply

    if call_sid not in conversation_histories:
        conversation_histories[call_sid] = []

    # 3. Query Gemini with full multi-turn history and personalized system instruction
    key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if key:
        stack_str = ", ".join(call_state.detected_frameworks) if call_state.detected_frameworks else None
        system_prompt = generate_session_instructions(
            prospect_name=call_state.prospect_name,
            company_name=call_state.company_name,
            tech_stack=stack_str,
            current_stage=stage
        )
        try:
            from google import genai
            from google.genai import types

            client = genai.Client(api_key=key)
            history = conversation_histories[call_sid]
            history.append(types.Content(role="user", parts=[types.Part.from_text(text=user_speech)]))

            for model_name in ["gemini-3.5-flash-lite", "gemini-3.5-flash", "gemini-flash-latest"]:
                try:
                    resp = client.models.generate_content(
                        model=model_name,
                        contents=history,
                        config=types.GenerateContentConfig(
                            system_instruction=system_prompt,
                            thinking_config=types.ThinkingConfig(thinking_level=types.ThinkingLevel.MINIMAL),
                            max_output_tokens=300,
                            temperature=0.7
                        )
                    )
                    if resp and resp.text:
                        reply = format_speech_for_natural_delivery(resp.text.strip())
                        history.append(types.Content(role="model", parts=[types.Part.from_text(text=reply)]))
                        return reply
                except Exception as e:
                    logger.warning(f"Model {model_name} failed: {e}. Trying fallback...")
        except Exception as exc:
            logger.error(f"GenAI error: {exc}")

    return "Fair enough! Are you guys currently letting agents run tools hands-free, or still having engineers manually approve every action?"


# ---------------------------------------------------------------------------
# 1. Twilio Inbound & Outbound Voice Webhooks & Media Streams
# ---------------------------------------------------------------------------

@app.post("/voice/live_stream")
@app.get("/voice/live_stream")
async def voice_live_stream_entrypoint(request: Request):
    """
    TwiML entrypoint that connects Twilio call directly to Gemini Live full-duplex WebSocket stream.
    Passes prospect context parameters into the WebSocket stream.
    """
    host = request.headers.get("x-forwarded-host") or request.headers.get("host") or "localhost:8765"
    proto = request.headers.get("x-forwarded-proto", "http")
    ws_scheme = "wss" if (proto == "https" or "lhr.life" in host or "loca.lt" in host or "ngrok" in host or not (host.startswith("localhost") or host.startswith("127.0.0.1"))) else "ws"

    lead_id = request.query_params.get("lead_id", "")
    lead = lead_mgr.get_by_id(lead_id) if lead_id else None

    prospect_name = lead.name if lead else request.query_params.get("name", "there")
    company_name = lead.company if lead else request.query_params.get("company", "")
    tech_stack = request.query_params.get("stack", "")

    stream_url = f"{ws_scheme}://{host}/voice/stream"
    logger.info(f"Connecting Twilio call to stream URL: {stream_url}")

    params_xml = ['            <Parameter name="customContext" value="bartholomew_cold_call" />']
    if prospect_name and prospect_name != "there":
        params_xml.append(f'            <Parameter name="prospectName" value="{prospect_name}" />')
    if company_name:
        params_xml.append(f'            <Parameter name="companyName" value="{company_name}" />')
    if tech_stack:
        params_xml.append(f'            <Parameter name="techStack" value="{tech_stack}" />')
    if lead_id:
        params_xml.append(f'            <Parameter name="leadId" value="{lead_id}" />')

    stream_xml = f"""        <Stream name="alex_voice_stream" url="{stream_url}">
{chr(10).join(params_xml)}
        </Stream>"""

    twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Connect>
{stream_xml}
    </Connect>
</Response>""".strip()

    return Response(content=twiml, media_type="text/xml")


@app.websocket("/voice/stream")
async def websocket_voice_stream(websocket: WebSocket):
    from src.voice.gemini_live_bridge import handle_twilio_gemini_stream
    await handle_twilio_gemini_stream(websocket)


@app.post("/voice/voicemail")
@app.get("/voice/voicemail")
async def voice_voicemail_drop(request: Request):
    """
    TwiML endpoint for leaving an authentic 8-second human voicemail drop.
    """
    lead_id = request.query_params.get("lead_id", "")
    lead = lead_mgr.get_by_id(lead_id) if lead_id else None

    name = lead.name if lead else request.query_params.get("name", "there")
    company = lead.company if lead else request.query_params.get("company", "")

    voicemail_msg = generate_voicemail_text(prospect_name=name, company_name=company)
    logger.info(f"Leaving automated voicemail drop for {name} ({company})...")

    if lead:
        lead.status = LeadStatus.VOICEMAIL
        lead.notes = f"{lead.notes} | Voicemail dropped".strip(" |")
        lead_mgr.save()
        lead_mgr.send_proposal(lead.id, tier="pro", notes="Automated follow-up after voicemail drop")

    twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Pause length="1"/>
    <Say voice="Polly.Joey-Neural">{voicemail_msg}</Say>
    <Hangup/>
</Response>"""
    return Response(content=twiml, media_type="application/xml")


@app.post("/voice/amd_callback")
async def twilio_amd_callback(request: Request):
    """
    Twilio Answering Machine Detection (AMD) status callback.
    Transitions machine-answered calls to voicemail drop or follow-up status.
    Zero external dependencies using standard library urllib.parse.
    """
    raw_body = await request.body()
    params = urllib.parse.parse_qs(raw_body.decode("utf-8", errors="replace"))
    answered_by = params.get("AnsweredBy", ["unknown"])[0]
    call_sid = params.get("CallSid", [""])[0]
    lead_id = request.query_params.get("lead_id", "")

    logger.info(f"AMD Callback for CallSid {call_sid} (Lead {lead_id}): AnsweredBy={answered_by}")

    lead = lead_mgr.get_by_id(lead_id) if lead_id else None
    if lead:
        if answered_by.startswith("machine"):
            lead.status = LeadStatus.VOICEMAIL
            lead.notes = f"{lead.notes} | AMD: {answered_by}".strip(" |")
            lead_mgr.save()
            lead_mgr.send_proposal(lead.id, tier="pro", notes="Auto proposal dispatched after AMD voicemail")
        elif answered_by == "human":
            lead.status = LeadStatus.CONNECTED
            lead_mgr.save()

    return {"status": "ok", "answered_by": answered_by, "lead_id": lead_id}


@app.get("/voice/audio/{filename}")
async def get_voice_audio(filename: str):
    """
    Serves generated 24kHz Gemini native audio WAV files to Twilio.
    """
    file_path = Path("scratch") / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Audio file not found")
    return FileResponse(file_path, media_type="audio/wav")


@app.post("/voice/interactive")
@app.get("/voice/interactive")
async def voice_interactive_start(request: Request):
    """
    Initial entrypoint for conversational outbound phone calls.
    Plays developer pitch greeting and gathers user speech.
    """
    public_base = os.getenv("VOICE_PUBLIC_BASE_URL", "").rstrip("/")
    if not public_base or "localhost" in public_base or "127.0.0.1" in public_base:
        host = request.headers.get("x-forwarded-host") or request.headers.get("host") or ""
        if host and not (host.startswith("localhost") or host.startswith("127.0.0.1")):
            public_base = f"https://{host}"
        else:
            public_base = config.public_base_url.rstrip("/")

    respond_url = f"{public_base}/voice/respond"

    twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Gather input="speech dtmf" action="{respond_url}" method="POST" speechTimeout="auto" timeout="6">
        <Say voice="Google.en-US-Journey-D">Hey, Alex here from Bartholomew. Saw you guys are building with AI agents — quick question: are you letting them run shell tools freely, or still stuck babysitting every command with manual approvals?</Say>
    </Gather>
    <Redirect method="POST">{respond_url}</Redirect>
</Response>""".strip()
    return Response(content=twiml, media_type="text/xml")


@app.post("/voice/respond")
async def voice_interactive_respond(request: Request):
    """
    Processes the user's spoken response and returns the conversational reply with intent classification.
    """
    raw_body = await request.body()
    params = urllib.parse.parse_qs(raw_body.decode("utf-8", errors="replace"))
    user_speech = params.get("SpeechResult", [""])[0].strip()
    digits = params.get("Digits", [""])[0].strip()
    call_sid = params.get("CallSid", ["default"])[0]
    logger.info(f"User input [{call_sid}]: speech='{user_speech}', digits='{digits}'")

    public_base = os.getenv("VOICE_PUBLIC_BASE_URL", "").rstrip("/")
    if not public_base or "localhost" in public_base or "127.0.0.1" in public_base:
        host = request.headers.get("x-forwarded-host") or request.headers.get("host") or ""
        if host and not (host.startswith("localhost") or host.startswith("127.0.0.1")):
            public_base = f"https://{host}"
        else:
            public_base = config.public_base_url.rstrip("/")

    respond_url = f"{public_base}/voice/respond"

    if digits and not user_speech:
        reply = "Hey, Alex here from Bartholomew. Saw you guys are building with AI agents — quick question: are you letting them run shell tools freely, or still stuck babysitting every command with manual approvals?"
    elif not user_speech:
        reply = "Hey, you still there? No worries if you're swamped, I can let you get back to it."
    else:
        reply = get_gemini_alex_reply(user_speech, call_sid)

        # Automatic Lead Qualification in Real-Time
        speech_lower = user_speech.lower()
        if any(w in speech_lower for w in ["yes", "sure", "email", "send", "pricing", "cost", "sign up", "deck", "doc"]):
            lead = lead_mgr.get_next_pending()
            if lead:
                lead_mgr.qualify_lead(lead.id, notes=f"Spoke on phone [{call_sid}]: {user_speech}")

    twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Gather input="speech dtmf" action="{respond_url}" method="POST" speechTimeout="auto" timeout="6">
        <Say voice="Google.en-US-Journey-D">{reply}</Say>
    </Gather>
    <Redirect method="POST">{respond_url}</Redirect>
</Response>"""
    return Response(content=twiml, media_type="text/xml")


@app.post("/voice/twiml")
@app.get("/voice/twiml")
async def twilio_twiml_endpoint(request: Request):
    """
    Returns TwiML that connects Twilio's audio call to our bi-directional MediaStream WebSocket.
    """
    host = request.headers.get("host", f"localhost:{config.server_port}")
    ws_protocol = "wss" if "https" in str(request.base_url) else "ws"

    lead_id = request.query_params.get("lead_id", "")
    lead = lead_mgr.get_by_id(lead_id) if lead_id else None
    name = lead.name if lead else request.query_params.get("name", "there")
    company = lead.company if lead else request.query_params.get("company", "")

    stream_url = f"{ws_protocol}://{host}/voice/stream"

    twiml_response = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="Google.en-US-Journey-D">Connecting to Bartholomew live stream.</Say>
    <Connect>
        <Stream url="{stream_url}">
            <Parameter name="customContext" value="bartholomew_cold_call" />
            <Parameter name="prospectName" value="{name}" />
            <Parameter name="companyName" value="{company}" />
            <Parameter name="leadId" value="{lead_id}" />
        </Stream>
    </Connect>
</Response>"""
    return Response(content=twiml_response, media_type="text/xml")


# ---------------------------------------------------------------------------
# 2. Outbound Telephony Dialing Trigger
# ---------------------------------------------------------------------------

@app.post("/api/dial")
async def trigger_outbound_dial(request: Request, lead_id: Optional[str] = None, phone: Optional[str] = None, stream: bool = True):
    """
    Trigger a real outbound phone call via Twilio REST API directly into Gemini Live voice engine.
    """
    target_lead = lead_mgr.get_by_id(lead_id) if lead_id else None
    target_phone = phone or (target_lead.phone if target_lead else None)

    if not target_phone:
        raise HTTPException(status_code=400, detail="Missing target phone number.")

    import re
    clean_digits = re.sub(r"[^\d+]", "", target_phone)
    if not clean_digits.startswith("+"):
        if len(clean_digits) == 10:
            clean_digits = f"+1{clean_digits}"
        elif len(clean_digits) == 11 and clean_digits.startswith("1"):
            clean_digits = f"+{clean_digits}"
        else:
            clean_digits = f"+{clean_digits}"
    target_phone = clean_digits

    if "555000" in target_phone or not config.is_twilio_ready():
        return {
            "status": "simulation_queued",
            "message": "Simulation queued for test number or simulation mode. Test with the Interactive Browser Bench at /voice/test.",
            "target_phone": target_phone,
            "lead": target_lead.to_dict() if target_lead else None
        }

    try:
        # Determine public base URL (from env, tunnel header, or config)
        public_base = os.getenv("VOICE_PUBLIC_BASE_URL", "").rstrip("/")
        if not public_base or "localhost" in public_base or "127.0.0.1" in public_base:
            req_host = request.headers.get("x-forwarded-host") or request.headers.get("host") or ""
            if req_host and not (req_host.startswith("localhost") or req_host.startswith("127.0.0.1")):
                public_base = f"https://{req_host}"
            else:
                public_base = config.public_base_url.rstrip("/")

        lead_param = f"?lead_id={target_lead.id}" if target_lead else ""
        twiml_path = "/voice/live_stream" if stream else "/voice/interactive"
        twiml_url = f"{public_base}{twiml_path}{lead_param}"
        call_sid = None

        logger.info(f"Initiating outbound call to {target_phone} with TwiML URL: {twiml_url}")

        try:
            from twilio.rest import Client
            client = Client(config.twilio_account_sid, config.twilio_auth_token)
            call = client.calls.create(
                to=target_phone,
                from_=config.twilio_phone_number,
                url=twiml_url
            )
            call_sid = call.sid
        except ImportError:
            # Zero-dependency fallback via Twilio REST API
            import base64
            import urllib.request

            api_url = f"https://api.twilio.com/2010-04-01/Accounts/{config.twilio_account_sid}/Calls.json"
            post_data = urllib.parse.urlencode({
                "To": target_phone,
                "From": config.twilio_phone_number,
                "Url": twiml_url,
            }).encode("utf-8")
            auth_str = f"{config.twilio_account_sid}:{config.twilio_auth_token}"
            auth_b64 = base64.b64encode(auth_str.encode("utf-8")).decode("utf-8")

            req = urllib.request.Request(
                api_url,
                data=post_data,
                headers={"Authorization": f"Basic {auth_b64}"}
            )
            with urllib.request.urlopen(req) as response:
                res_data = json.loads(response.read().decode("utf-8"))
                call_sid = res_data.get("sid")

        if target_lead:
            target_lead.status = LeadStatus.CALLING
            lead_mgr.save()

        return {
            "status": "dialing",
            "call_sid": call_sid,
            "target_phone": target_phone
        }
    except Exception as e:
        logger.error(f"Failed to place Twilio call: {e}")
        raise HTTPException(status_code=500, detail=f"Twilio dialing error: {str(e)}")


# ---------------------------------------------------------------------------
# 3. Interactive Web Audio Bench (Mic & Speaker Browser Test)
# ---------------------------------------------------------------------------

@app.websocket("/voice/browser-stream")
async def browser_audio_websocket(websocket: WebSocket):
    """
    Bi-directional WebSocket for browser testing (testing AI voice using laptop mic & speaker).
    Exchanges JSON envelopes containing text and audio samples.
    """
    await websocket.accept()
    lead = lead_mgr.get_next_pending() or Lead(name="Test Prospect", company="Sample AI Corp")

    def on_audio_delta(pcm16_24k_b64: str):
        msg = {"type": "audio", "payload": pcm16_24k_b64}
        asyncio.create_task(websocket.send_json(msg))

    def on_transcript_delta(role: str, text: str):
        msg = {"type": "transcript", "role": role, "text": text}
        asyncio.create_task(websocket.send_json(msg))

    def on_interruption():
        msg = {"type": "interruption"}
        asyncio.create_task(websocket.send_json(msg))

    session = RealtimeVoiceSession(
        lead=lead,
        voice_config=config,
        on_audio_delta=on_audio_delta,
        on_transcript_delta=on_transcript_delta,
        on_interruption=on_interruption
    )

    try:
        await session.start()
        # Notify browser of active session
        await websocket.send_json({
            "type": "ready",
            "lead": lead.to_dict(),
            "mode": "gemini" if (os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")) else "simulated"
        })

        while True:
            raw_msg = await websocket.receive_text()
            data = json.loads(raw_msg)
            m_type = data.get("type")

            if m_type == "audio":
                audio_b64 = data.get("payload", "")
                await session.send_audio_chunk(audio_b64)

            elif m_type == "text":
                text = data.get("text", "")
                await session.handle_user_text_input(text)

            elif m_type == "interrupt":
                await session.close()
                break

    except WebSocketDisconnect:
        logger.info("Browser audio test client disconnected.")
    except Exception as e:
        logger.error(f"Browser websocket error: {e}")
    finally:
        await session.close()
        lead_mgr.update_lead_outcome(
            lead_id=lead.id,
            status=LeadStatus.QUALIFIED,
            duration=session.get_duration(),
            transcript=session.transcript
        )


# ---------------------------------------------------------------------------
# 4. Lead Queue & Management APIs
# ---------------------------------------------------------------------------

@app.get("/api/leads")
async def list_leads():
    return {"leads": [l.to_dict() for l in lead_mgr.get_all()]}


@app.get("/api/leads/summary")
async def leads_summary():
    """Returns real-time sales pipeline metrics."""
    leads = lead_mgr.get_all()
    total = len(leads)
    by_status = {}
    total_val = 0.0
    closed_won_val = 0.0

    for l in leads:
        st = l.status.value if hasattr(l.status, "value") else str(l.status)
        by_status[st] = by_status.get(st, 0) + 1
        val = getattr(l, "deal_value_usd", 0.0) or 0.0
        total_val += val
        if st == "CLOSED_WON":
            closed_won_val += val

    return {
        "total_leads": total,
        "by_status": by_status,
        "total_pipeline_value_usd": total_val,
        "closed_won_revenue_usd": closed_won_val,
        "qualified_count": by_status.get("QUALIFIED", 0),
        "proposals_sent": by_status.get("PROPOSAL_SENT", 0),
        "voicemails_dropped": by_status.get("VOICEMAIL", 0),
        "closed_won_count": by_status.get("CLOSED_WON", 0)
    }


@app.post("/api/leads/{lead_id}/qualify")
async def qualify_lead_endpoint(lead_id: str, request: Request):
    """Mark a prospect as qualified."""
    body = {}
    try:
        body = await request.json()
    except Exception:
        pass
    notes = body.get("notes", "Qualified via phone consultation")
    email = body.get("email")
    lead = lead_mgr.qualify_lead(lead_id, notes=notes, email=email)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    return {"status": "qualified", "lead": lead.to_dict()}


@app.post("/api/leads/{lead_id}/send_proposal")
async def send_proposal_endpoint(lead_id: str, request: Request):
    """Dispatch proposal and Stripe checkout link to prospect."""
    body = {}
    try:
        body = await request.json()
    except Exception:
        pass
    tier = body.get("tier", "pro")
    notes = body.get("notes", "")
    result = lead_mgr.send_proposal(lead_id, tier=tier, notes=notes)
    if not result:
        raise HTTPException(status_code=404, detail="Lead not found")
    return {"status": "proposal_sent", "proposal": result}


@app.post("/api/leads/{lead_id}/close")
async def close_deal_endpoint(lead_id: str, request: Request):
    """Close deal as CLOSED_WON with recorded contract value."""
    body = {}
    try:
        body = await request.json()
    except Exception:
        pass
    tier = body.get("tier", "pro")
    deal_val = body.get("deal_value_usd")
    notes = body.get("notes", "Closed via direct consultation")
    lead = lead_mgr.close_deal(lead_id, tier=tier, deal_value_usd=deal_val, notes=notes)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    return {"status": "closed_won", "lead": lead.to_dict()}


@app.post("/api/leads")
async def add_lead(request: Request):
    data = await request.json()
    new_lead = lead_mgr.add_lead(
        name=data.get("name", "New Lead"),
        company=data.get("company", "Tech Co"),
        phone=data.get("phone", ""),
        email=data.get("email"),
        role=data.get("role", "AI Engineer")
    )
    return {"status": "created", "lead": new_lead.to_dict()}


@app.post("/api/leads/{lead_id}/send_sms")
async def send_lead_sms_endpoint(lead_id: str, request: Request):
    """Dispatch instant SMS follow-up with sandbox link and Stripe checkout portal."""
    body = {}
    try:
        body = await request.json()
    except Exception:
        pass
    lead = lead_mgr.get_by_id(lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    checkout = body.get("checkout_url", lead.checkout_url)
    res = send_followup_sms(lead.phone, lead.name, checkout_url=checkout)
    lead.notes = f"{lead.notes} | SMS follow-up sent ({res.get('status')})".strip(" |")
    lead_mgr.save()
    return {"status": "sms_dispatched", "result": res, "lead_id": lead.id}


@app.get("/api/campaign/status")
async def campaign_status_endpoint():
    """Returns global timezone readiness and active callable leads."""
    from src.voice.global_campaign_runner import GlobalCampaignRunner
    runner = GlobalCampaignRunner(lead_mgr)
    return runner.get_global_schedule_status(allow_weekends=True)


def send_followup_sms(to_phone: str, prospect_name: str, checkout_url: Optional[str] = None) -> Dict[str, Any]:
    """Sends an authentic, zero-pressure SMS follow-up via Twilio REST API."""
    if not config.is_twilio_ready() or "555" in to_phone:
        logger.info(f"[SIMULATION] Outbound SMS to {to_phone} simulated successfully.")
        return {"status": "simulated_sms_sent", "to": to_phone}

    try:
        from twilio.rest import Client
        client = Client(config.twilio_account_sid, config.twilio_auth_token)
        first_name = prospect_name.split()[0] if prospect_name else "there"
        checkout = checkout_url or "https://buy.stripe.com/fZu28rbNz5TYcmAddK9R600"
        body = (
            f"Hey {first_name}, Alex here from Bartholomew -- "
            f"here is our 1-page sandbox guide: https://bartholomew.info "
            f"or start Pro anytime: {checkout}. Text me back if you have any questions!"
        )
        msg = client.messages.create(
            to=to_phone,
            from_=config.twilio_phone_number,
            body=body
        )
        logger.info(f"Twilio SMS sent to {to_phone} (Sid: {msg.sid})")
        return {"status": "sms_sent", "sid": msg.sid, "to": to_phone}
    except Exception as e:
        logger.error(f"Failed to send Twilio SMS to {to_phone}: {e}")
        return {"status": "error", "error": str(e)}


@app.get("/voice/test")
@app.get("/voice")
async def get_test_bench_html():
    """Serves the standalone internal browser testing suite."""
    html_file = Path(__file__).resolve().parent / "static" / "index.html"
    if html_file.exists():
        return HTMLResponse(content=html_file.read_text(encoding="utf-8"))
    return HTMLResponse("<h1>Bartholomew Voice AI Server Running.</h1>")
