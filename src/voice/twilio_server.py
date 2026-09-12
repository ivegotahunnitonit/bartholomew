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
conversation_histories: Dict[str, List[Dict[str, Any]]] = {}


def get_gemini_alex_reply(user_speech: str, call_sid: str) -> str:
    """Queries conversational AI in real-time with sub-millisecond objection matching and model fallback."""
    if call_sid not in conversation_histories:
        conversation_histories[call_sid] = []

    # 1. Fast sub-millisecond keyword objection matcher
    speech_lower = user_speech.lower()
    for obj in OBJECTIONS:
        if any(kw in speech_lower for kw in obj.keywords):
            reply = format_speech_for_natural_delivery(obj.suggested_reply)
            conversation_histories[call_sid].append({"role": "model", "parts": [{"text": reply}]})
            return reply

    # 2. Query Gemini with fast timeout and Astra-level conversational prompt
    key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if key:
        prompt = generate_session_instructions("there")
        try:
            from google import genai
            from google.genai import types

            client = genai.Client(api_key=key)
            history = conversation_histories[call_sid]
            history.append({"role": "user", "parts": [{"text": user_speech}]})

            contents = (
                f"{prompt}\n\n"
                f"Prospect just said on phone: \"{user_speech}\"\n\n"
                "Reply as Alex in 1 to 2 short conversational sentences (10-25 words max), "
                "mirroring their emotion or technical problem naturally:"
            )

            for model_name in ["gemini-3.5-flash", "gemini-flash-latest", "gemini-2.5-flash"]:
                try:
                    resp = client.models.generate_content(
                        model=model_name,
                        contents=contents,
                        config=types.GenerateContentConfig(
                            max_output_tokens=80,
                            temperature=0.7
                        )
                    )
                    if resp and resp.text:
                        reply = format_speech_for_natural_delivery(resp.text.strip())
                        history.append({"role": "model", "parts": [{"text": reply}]})
                        return reply
                except Exception as e:
                    logger.warning(f"Model {model_name} failed: {e}. Trying fallback...")
        except Exception as exc:
            logger.error(f"GenAI error: {exc}")

    return "Haha yeah, totally hear you. Are you guys letting your agents run tools autonomously, or still babysitting every step?"


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
    ws_scheme = "wss" if (proto == "https" or "loca.lt" in host) else "ws"

    lead_id = request.query_params.get("lead_id", "")
    lead = lead_mgr.get_by_id(lead_id) if lead_id else None

    prospect_name = lead.name if lead else request.query_params.get("name", "there")
    company_name = lead.company if lead else request.query_params.get("company", "")
    tech_stack = request.query_params.get("stack", "")

    query_encoded = urllib.parse.urlencode({
        "name": prospect_name,
        "company": company_name,
        "stack": tech_stack
    })
    stream_url = f"{ws_scheme}://{host}/voice/stream?{query_encoded}"
    logger.info(f"Connecting Twilio call to stream URL: {stream_url}")

    twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Connect>
        <Stream url="{stream_url}">
            <Parameter name="customContext" value="bartholomew_cold_call" />
            <Parameter name="prospectName" value="{prospect_name}" />
            <Parameter name="companyName" value="{company_name}" />
            <Parameter name="leadId" value="{lead_id}" />
        </Stream>
    </Connect>
</Response>"""
    return Response(content=twiml, media_type="application/xml")


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
    host = request.headers.get("x-forwarded-host") or request.headers.get("host") or "localhost:8765"
    base_url = f"https://{host}"
    respond_url = f"{base_url}/voice/respond"

    twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Gather input="speech" action="{respond_url}" method="POST" speechTimeout="auto" timeout="5">
        <Say voice="Polly.Joey-Neural">Hey there, Alex here. Caught you randomly — saw your team is building with autonomous agents. We built Bartholomew, an open-source execution firewall that blocks dangerous shell commands and database drops in under 35 microseconds. Do you have 30 seconds, or did I catch you in the middle of a deployment fire?</Say>
    </Gather>
    <Redirect method="POST">{respond_url}</Redirect>
</Response>"""
    return Response(content=twiml, media_type="application/xml")


@app.post("/voice/respond")
async def voice_interactive_respond(request: Request):
    """
    Processes the user's spoken response and returns the conversational reply with intent classification.
    """
    raw_body = await request.body()
    params = urllib.parse.parse_qs(raw_body.decode("utf-8", errors="replace"))
    user_speech = params.get("SpeechResult", [""])[0].strip()
    call_sid = params.get("CallSid", ["default"])[0]
    logger.info(f"User spoken input [{call_sid}]: '{user_speech}'")

    host = request.headers.get("x-forwarded-host") or request.headers.get("host") or "localhost:8765"
    base_url = f"https://{host}"
    respond_url = f"{base_url}/voice/respond"

    if not user_speech:
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
    <Gather input="speech" action="{respond_url}" method="POST" speechTimeout="auto" timeout="5">
        <Say voice="Polly.Joey-Neural">{reply}</Say>
    </Gather>
    <Redirect method="POST">{respond_url}</Redirect>
</Response>"""
    return Response(content=twiml, media_type="application/xml")


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
    <Say voice="Polly.Joey-Neural">Connecting to Bartholomew Engineering Security line.</Say>
    <Connect>
        <Stream url="{stream_url}">
            <Parameter name="customContext" value="bartholomew_cold_call" />
            <Parameter name="prospectName" value="{name}" />
            <Parameter name="companyName" value="{company}" />
            <Parameter name="leadId" value="{lead_id}" />
        </Stream>
    </Connect>
</Response>"""
    return Response(content=twiml_response, media_type="application/xml")


# ---------------------------------------------------------------------------
# 2. Outbound Telephony Dialing Trigger
# ---------------------------------------------------------------------------

@app.post("/api/dial")
async def trigger_outbound_dial(lead_id: Optional[str] = None, phone: Optional[str] = None):
    """
    Trigger a real outbound phone call via Twilio REST API with Answering Machine Detection.
    """
    target_lead = lead_mgr.get_by_id(lead_id) if lead_id else None
    target_phone = phone or (target_lead.phone if target_lead else None)

    if not target_phone:
        raise HTTPException(status_code=400, detail="Missing target phone number.")

    if "555" in target_phone or not config.is_twilio_ready():
        return {
            "status": "simulation_queued",
            "message": "Simulation queued for test number or simulation mode. Test with the Interactive Browser Bench at /voice/test.",
            "target_phone": target_phone,
            "lead": target_lead.to_dict() if target_lead else None
        }

    try:
        lead_param = f"?lead_id={target_lead.id}" if target_lead else ""
        twiml_url = f"{config.public_base_url.rstrip('/')}/voice/live_stream{lead_param}"
        amd_callback_url = f"{config.public_base_url.rstrip('/')}/voice/amd_callback{lead_param}"
        call_sid = None

        try:
            from twilio.rest import Client
            client = Client(config.twilio_account_sid, config.twilio_auth_token)
            call = client.calls.create(
                to=target_phone,
                from_=config.twilio_phone_number,
                url=twiml_url,
                machine_detection="DetectMessageEnd",
                async_amd="true",
                async_amd_status_callback=amd_callback_url
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
                "MachineDetection": "DetectMessageEnd",
                "AsyncAmd": "true",
                "AsyncAmdStatusCallback": amd_callback_url
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


@app.get("/voice/test")
@app.get("/voice")
async def get_test_bench_html():
    """Serves the standalone internal browser testing suite."""
    html_file = Path(__file__).resolve().parent / "static" / "index.html"
    if html_file.exists():
        return HTMLResponse(content=html_file.read_text(encoding="utf-8"))
    return HTMLResponse("<h1>Bartholomew Voice AI Server Running.</h1>")
