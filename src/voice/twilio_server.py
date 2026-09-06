"""
Bartholomew Trust Protocol (BTP v5.4) — Twilio Voice Server & Interactive Web Bench
Provides FastAPI routes, Twilio bi-directional MediaStream WebSockets,
outbound dialing endpoints, and browser test benches.
"""

import asyncio
import json
import logging
import os
from pathlib import Path
from typing import Dict, Any, Optional

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request, Response, Form, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from .voice_config import config, VoiceConfig
from .audio_codec import AudioCodec
from .sales_persona import OBJECTIONS
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


# ---------------------------------------------------------------------------
# 1. Twilio Inbound & Outbound Voice Webhooks
# ---------------------------------------------------------------------------

@app.post("/voice/twiml")
@app.get("/voice/twiml")
async def twilio_twiml_endpoint(request: Request):
    """
    Returns TwiML that connects Twilio's audio call to our bi-directional MediaStream WebSocket.
    """
    host = request.headers.get("host", f"localhost:{config.server_port}")
    # Use wss for secure or ws for local development
    ws_protocol = "wss" if "https" in str(request.base_url) else "ws"
    stream_url = f"{ws_protocol}://{host}/voice/stream"

    twiml_response = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="Polly.Joey-Neural">Connecting to Bartholomew Engineering Security line.</Say>
    <Connect>
        <Stream url="{stream_url}">
            <Parameter name="customContext" value="bartholomew_cold_call" />
        </Stream>
    </Connect>
</Response>"""
    return Response(content=twiml_response, media_type="application/xml")


@app.websocket("/voice/stream")
async def twilio_stream_websocket(websocket: WebSocket):
    """
    Twilio MediaStream bi-directional WebSocket handler.
    Exchanges 8kHz mu-law audio with Twilio and coordinates with RealtimeVoiceSession.
    """
    await websocket.accept()
    stream_sid: Optional[str] = None
    call_sid: Optional[str] = None
    session: Optional[RealtimeVoiceSession] = None
    lead = lead_mgr.get_next_pending() or Lead(name="Prospect", company="Engineering Team")

    # Callbacks for Realtime AI
    def on_ai_audio_delta(pcm16_24k_b64: str):
        if stream_sid:
            mulaw_8k_b64 = AudioCodec.openai_to_twilio(pcm16_24k_b64)
            media_msg = {
                "event": "media",
                "streamSid": stream_sid,
                "media": {"payload": mulaw_8k_b64}
            }
            asyncio.create_task(websocket.send_json(media_msg))

    def on_ai_interruption():
        if stream_sid:
            clear_msg = {"event": "clear", "streamSid": stream_sid}
            asyncio.create_task(websocket.send_json(clear_msg))

    session = RealtimeVoiceSession(
        lead=lead,
        voice_config=config,
        on_audio_delta=on_ai_audio_delta,
        on_interruption=on_ai_interruption
    )

    try:
        while True:
            raw_msg = await websocket.receive_text()
            data = json.loads(raw_msg)
            event = data.get("event")

            if event == "start":
                stream_sid = data.get("start", {}).get("streamSid")
                call_sid = data.get("start", {}).get("callSid")
                logger.info(f"Twilio MediaStream started: streamSid={stream_sid} callSid={call_sid}")
                active_sessions[stream_sid] = session
                await session.start()

            elif event == "media":
                payload_b64 = data.get("media", {}).get("payload")
                if payload_b64 and session:
                    pcm16_24k_b64 = AudioCodec.twilio_to_openai(payload_b64)
                    await session.send_audio_chunk(pcm16_24k_b64)

            elif event == "stop":
                logger.info(f"Twilio MediaStream ended for {stream_sid}")
                break

    except WebSocketDisconnect:
        logger.info(f"Twilio WebSocket disconnected for {stream_sid}")
    except Exception as e:
        logger.error(f"Error in Twilio MediaStream: {e}")
    finally:
        if session:
            await session.close()
            lead_mgr.update_lead_outcome(
                lead_id=lead.id,
                status=LeadStatus.CONNECTED,
                duration=session.get_duration(),
                transcript=session.transcript
            )
        if stream_sid and stream_sid in active_sessions:
            del active_sessions[stream_sid]


# ---------------------------------------------------------------------------
# 2. Outbound Telephony Dialing Trigger
# ---------------------------------------------------------------------------

@app.post("/api/dial")
async def trigger_outbound_dial(lead_id: Optional[str] = None, phone: Optional[str] = None):
    """
    Trigger a real outbound phone call via Twilio REST API.
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
        twiml_url = f"{config.public_base_url.rstrip('/')}/voice/twiml"
        call_sid = None

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
            import urllib.parse
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
            "mode": "openai" if config.is_openai_ready() else "simulated"
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
