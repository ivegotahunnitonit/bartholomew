"""
Bartholomew Voice AI — Gemini Live Realtime Audio Bridge
Connects Twilio Media Streams (WebSockets) directly to Google Gemini Live API
for full-duplex native human voice conversations with live interruption (barge-in).
Equipped with Goertzel 1000Hz voicemail beep detection, human vs. answering machine
classification, and AI-proofed professional executive communication.
"""

import asyncio
import json
import base64
import logging
import os
import time
from starlette.websockets import WebSocket, WebSocketDisconnect
from google import genai
from google.genai import types

from src.voice.audio_codecs import mulaw8k_to_pcm16k, pcm24k_to_mulaw8k, detect_voicemail_beep
from src.voice.sales_persona import (
    generate_session_instructions,
    generate_voicemail_text,
    classify_recipient_intent,
    CallRecipientType,
    LiveCallState
)

logger = logging.getLogger("btp.voice.gemini_live")


async def handle_twilio_gemini_stream(websocket: WebSocket):
    """
    Handles bidirectional Twilio WebSocket MediaStream to Gemini Live.
    Extracts caller context, discriminates between live humans and voicemails,
    and enforces AI-proofed professional conversation standards.
    """
    await websocket.accept()
    logger.info("Twilio Media Stream WebSocket accepted.")

    # Extract initial query parameters if provided
    query_params = dict(websocket.query_params)
    prospect_name = query_params.get("name", "there")
    company_name = query_params.get("company", "")
    tech_stack = query_params.get("stack", "")
    lead_id = query_params.get("lead_id", "")
    voice_name = os.getenv("GEMINI_VOICE_NAME", "Puck")

    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not api_key:
        logger.error("No Gemini API key configured.")
        await websocket.close()
        return

    client = genai.Client(api_key=api_key)

    # Compile dynamic prompt with prospect context and AI-proofing
    instruction_text = generate_session_instructions(
        prospect_name=prospect_name,
        company_name=company_name,
        tech_stack=tech_stack
    )

    config = types.LiveConnectConfig(
        response_modalities=["AUDIO"],
        speech_config=types.SpeechConfig(
            voice_config=types.VoiceConfig(
                prebuilt_voice_config=types.PrebuiltVoiceConfig(
                    voice_name=voice_name
                )
            )
        ),
        system_instruction=types.Content(
            parts=[types.Part.from_text(text=instruction_text)]
        )
    )

    model = os.getenv("GEMINI_LIVE_MODEL", "gemini-2.5-flash-native-audio-latest")
    stream_sid = None
    call_state = LiveCallState(prospect_name=prospect_name, company_name=company_name)

    try:
        async with client.aio.live.connect(model=model, config=config) as session:
            logger.info(f"Connected to Gemini Live session with voice '{voice_name}' for {prospect_name}.")

            # Task 1: Receive from Twilio -> Send to Gemini
            async def twilio_to_gemini():
                nonlocal stream_sid, prospect_name, company_name
                greeting_sent = False
                speech_start_time = None
                voicemail_beep_handled = False

                while True:
                    try:
                        message = await websocket.receive_text()
                        data = json.loads(message)
                        event = data.get("event")

                        if event == "connected":
                            logger.info("Twilio stream connected event received.")

                        elif event == "start":
                            stream_sid = data.get("start", {}).get("streamSid")
                            custom_params = data.get("start", {}).get("customParameters", {})
                            
                            # Update context if custom parameters were passed via TwiML
                            if custom_params.get("prospectName"):
                                prospect_name = custom_params["prospectName"]
                            if custom_params.get("companyName"):
                                company_name = custom_params["companyName"]

                            first_name = prospect_name.strip().split()[0] if prospect_name != "there" else "there"
                            logger.info(f"Twilio stream started. StreamSid: {stream_sid} for {first_name} at {company_name}")

                            # Trigger professional executive opening line from Alex
                            if not greeting_sent:
                                greeting_sent = True
                                company_ref = f" at {company_name}" if company_name else ""
                                opener_prompt = (
                                    f"[Call answered by {first_name}. Speak articulately and professionally: "
                                    f"'Hello {first_name}, Alex here from Bartholomew Trust. Caught you briefly -- "
                                    f"do you have 30 seconds, or did I catch you in the middle of a deployment release{company_ref}?']"
                                )
                                opener = types.Content(
                                    role="user",
                                    parts=[types.Part.from_text(text=opener_prompt)]
                                )
                                await session.send_client_content(turns=[opener], turn_complete=True)

                        elif event == "media":
                            payload = data.get("media", {}).get("payload")
                            if payload:
                                raw_mulaw = base64.b64decode(payload)
                                pcm16k = mulaw8k_to_pcm16k(raw_mulaw)
                                if pcm16k:
                                    # 1. Beep tone detection: Goertzel 1000 Hz algorithm
                                    if not voicemail_beep_handled:
                                        is_beep, score = detect_voicemail_beep(
                                            pcm16k, target_freq=1000.0, sample_rate=16000.0, confidence_threshold=0.32
                                        )
                                        if is_beep:
                                            voicemail_beep_handled = True
                                            call_state.recipient_type = CallRecipientType.VOICEMAIL
                                            logger.info(f"[DETECTOR] Voicemail 1000Hz beep tone detected (confidence={score:.2f})!")
                                            first_name = prospect_name.strip().split()[0] if prospect_name != "there" else "there"
                                            vm_text = generate_voicemail_text(first_name, company_name)
                                            vm_turn = types.Content(
                                                role="user",
                                                parts=[types.Part.from_text(
                                                    text=f"[Voicemail beep tone detected. Deliver this articulate 10-second message then stop: '{vm_text}']"
                                                )]
                                            )
                                            await session.send_client_content(turns=[vm_turn], turn_complete=True)

                                    # 2. Forward audio to Gemini Live
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
                                # Sub-millisecond barge-in: If caller interrupts, clear Twilio playback buffer
                                if sc.interrupted:
                                    logger.info("Interruption detected: clearing Twilio playback buffer.")
                                    if stream_sid:
                                        clear_msg = json.dumps({"event": "clear", "streamSid": stream_sid})
                                        await websocket.send_text(clear_msg)

                                # Forward synthesized native audio chunks to Twilio
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
