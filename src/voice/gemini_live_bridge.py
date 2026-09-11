"""
Bartholomew Voice AI — Gemini Live Realtime Audio Bridge
Connects Twilio Media Streams (WebSockets) directly to Google Gemini Live API
for full-duplex native human voice conversations with live interruption (barge-in).
"""

import asyncio
import json
import base64
import logging
import os
from starlette.websockets import WebSocket, WebSocketDisconnect
from google import genai
from google.genai import types

from src.voice.audio_codecs import mulaw8k_to_pcm16k, pcm24k_to_mulaw8k

logger = logging.getLogger("btp.voice.gemini_live")

SYSTEM_INSTRUCTION = """
You are Alex, an authentic, chill software engineer calling another developer.
You sound 100% like a real person having a quick phone conversation — casual, natural cadence, subtle humor, relaxed.

CRITICAL CONVERSATIONAL RULES:
1. KEEP IT ULTRA BRIEF: Maximum 1 to 2 short sentences per turn. Never monologue or give a sales pitch.
2. IF USER SAYS "HOLD ON", "WAIT", OR "ONE SEC": Say "Sure thing, take your time man" and stop talking completely until they say they're back.
3. AUTHENTIC VOCAL TONE: Use casual developer phrasing ("haha yeah", "totally get that", "fair enough", "man, that sucks"). Sound like you are speaking, not reading text.
4. PROBLEM CONTEXT: You're calling engineers about runaway AI agents in production (CrewAI, LangGraph, AutoGen). If agents have shell/DB access, bad hallucinations or injections can run destructive commands. You're sharing an open-source guard called btp-guard that blocks bad bash/SQL in under 35 microseconds.
5. LISTEN FIRST: Let the other person talk. If they speak, stop talking immediately. Ask questions, don't lecture.
""".strip()


async def handle_twilio_gemini_stream(websocket: WebSocket):
    await websocket.accept()
    logger.info("Twilio Media Stream WebSocket accepted.")

    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not api_key:
        logger.error("No Gemini API key configured.")
        await websocket.close()
        return

    client = genai.Client(api_key=api_key)
    config = types.LiveConnectConfig(
        response_modalities=["AUDIO"],
        speech_config=types.SpeechConfig(
            voice_config=types.VoiceConfig(
                prebuilt_voice_config=types.PrebuiltVoiceConfig(
                    voice_name="Puck"  # Youthful, natural, friendly conversational male voice
                )
            )
        ),
        system_instruction=types.Content(
            parts=[types.Part.from_text(text=SYSTEM_INSTRUCTION)]
        )
    )

    model = os.getenv("GEMINI_LIVE_MODEL", "gemini-2.0-flash-exp")
    stream_sid = None

    try:
        async with client.aio.live.connect(model=model, config=config) as session:
            logger.info("Connected to Gemini Live session.")

            # Queue for audio from Gemini to Twilio
            send_queue = asyncio.Queue()

            # Task 1: Receive from Twilio -> Send to Gemini
            async def twilio_to_gemini():
                nonlocal stream_sid
                first_media_seen = False
                greeting_sent = False

                while True:
                    try:
                        message = await websocket.receive_text()
                        data = json.loads(message)
                        event = data.get("event")

                        if event == "connected":
                            logger.info("Twilio stream connected event received.")

                        elif event == "start":
                            stream_sid = data.get("start", {}).get("streamSid")
                            logger.info(f"Twilio stream started. StreamSid: {stream_sid}")

                            # Trigger casual opening line from Alex
                            if not greeting_sent:
                                greeting_sent = True
                                opener = types.Content(
                                    role="user",
                                    parts=[types.Part.from_text(text="[Call answered. Say hello casually: 'Hey! Alex here. Did I catch you in the middle of something or do you have 30 seconds?']")]
                                )
                                await session.send_client_content(turns=[opener], turn_complete=True)

                        elif event == "media":
                            payload = data.get("media", {}).get("payload")
                            if payload:
                                raw_mulaw = base64.b64decode(payload)
                                pcm16k = mulaw8k_to_pcm16k(raw_mulaw)
                                if pcm16k:
                                    blob = types.Blob(mime_type="audio/pcm;rate=16000", data=pcm16k)
                                    await session.send_realtime_input(audio=blob)

                        elif event == "stop":
                            logger.info("Twilio stream stopped.")
                            break

                    except WebSocketDisconnect:
                        logger.info("Twilio WebSocket disconnected.")
                        break
                    except Exception as e:
                        logger.error(f"Error in twilio_to_gemini: {e}")
                        break

            # Task 2: Receive from Gemini -> Send to Twilio
            async def gemini_to_twilio():
                nonlocal stream_sid
                while True:
                    try:
                        async for response in session.receive():
                            sc = response.server_content
                            if sc:
                                # Live Barge-In detection: if user speaks over Gemini, clear Twilio buffer
                                if sc.interrupted:
                                    logger.info("Gemini detected interruption! Sending clear to Twilio.")
                                    if stream_sid:
                                        clear_msg = json.dumps({"event": "clear", "streamSid": stream_sid})
                                        await websocket.send_text(clear_msg)

                                # Forward synthesized audio to Twilio
                                if sc.model_turn:
                                    for part in sc.model_turn.parts:
                                        if part.inline_data and part.inline_data.data:
                                            pcm24k = part.inline_data.data
                                            mulaw8k = pcm24k_to_mulaw8k(pcm24k)
                                            if mulaw8k and stream_sid:
                                                b64_payload = base64.b64encode(mulaw8k).decode("ascii")
                                                msg = json.dumps({
                                                    "event": "media",
                                                    "streamSid": stream_sid,
                                                    "media": {"payload": b64_payload}
                                                })
                                                await websocket.send_text(msg)
                    except (WebSocketDisconnect, RuntimeError):
                        logger.info("Twilio WebSocket closed during audio output.")
                        break
                    except Exception as e:
                        logger.error(f"Error in gemini_to_twilio: {e}")
                        break

            # Run both bidirectional loops concurrently
            producer = asyncio.create_task(twilio_to_gemini())
            consumer = asyncio.create_task(gemini_to_twilio())

            done, pending = await asyncio.wait(
                [producer, consumer],
                return_when=asyncio.FIRST_COMPLETED
            )

            for task in pending:
                task.cancel()

    except Exception as e:
        logger.error(f"Gemini Live bridge exception: {e}")
    finally:
        try:
            await websocket.close()
        except Exception:
            pass
        logger.info("Twilio-Gemini Live session finished.")
