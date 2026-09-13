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
    ConversationStage,
    LiveCallState,
    VOICE_TOOL_DECLARATIONS,
    get_framework_compatibility_info
)

logger = logging.getLogger("btp.voice.gemini_live")


async def handle_twilio_gemini_stream(websocket: WebSocket):
    """
    Handles bidirectional Twilio WebSocket MediaStream to Gemini Live.
    Extracts caller context, discriminates between live humans and voicemails,
    enforces AI-proofed professional conversation standards, and handles
    autonomous in-call tool calling.
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
    call_state = LiveCallState(prospect_name=prospect_name, company_name=company_name)
    instruction_text = generate_session_instructions(
        prospect_name=prospect_name,
        company_name=company_name,
        tech_stack=tech_stack,
        current_stage=call_state.stage,
        detected_pains=call_state.detected_pains,
        caller_role=call_state.detected_role,
        caller_sentiment=call_state.detected_sentiment
    )

    gemini_tools = [types.Tool(function_declarations=VOICE_TOOL_DECLARATIONS)]

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
        ),
        tools=gemini_tools
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
                            if custom_params.get("techStack"):
                                tech_stack = custom_params["techStack"]
                            if custom_params.get("leadId"):
                                lead_id = custom_params["leadId"]

                            first_name = prospect_name.strip().split()[0] if prospect_name != "there" else "there"
                            logger.info(f"Twilio stream started. StreamSid: {stream_sid} for {first_name} at {company_name}")

                            # Trigger professional executive opening line from Alex
                            if not greeting_sent:
                                greeting_sent = True
                                company_ref = f" at {company_name}" if company_name else ""
                                if first_name == "there":
                                    opener_prompt = (
                                        "[Call answered. Say casually and naturally in 1-2 short sentences as Alex: "
                                        "'Hey, Alex here from Bartholomew. Saw your team is building with AI agents — "
                                        "quick question: are you letting them run shell tools freely, or still stuck babysitting every command with manual approvals?']"
                                    )
                                else:
                                    opener_prompt = (
                                        f"[Call answered by {first_name}. Say casually and naturally in 1-2 short sentences as Alex: "
                                        f"'Hey {first_name}, Alex here from Bartholomew. Saw your team{company_ref} is building with AI agents — "
                                        f"quick question: are you letting them run shell tools freely, or still stuck babysitting every command with manual approvals?']"
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
                                    try:
                                        from src.voice.twilio_server import broadcast_event
                                        asyncio.create_task(broadcast_event("stream_interrupted", {"stream_sid": stream_sid}))
                                    except Exception:
                                        pass

                                # Forward synthesized native audio chunks to Twilio
                                if sc.model_turn:
                                    for part in sc.model_turn.parts:
                                        if getattr(part, "text", None):
                                            try:
                                                from src.voice.twilio_server import broadcast_event
                                                asyncio.create_task(broadcast_event("live_transcript", {
                                                    "speaker": "alex",
                                                    "text": part.text,
                                                    "stream_sid": stream_sid
                                                }))
                                            except Exception:
                                                pass

                                        if part.inline_data and part.inline_data.data:
                                            pcm24k = part.inline_data.data
                                            mulaw8k = pcm24k_to_mulaw8k(pcm24k)
                                            if mulaw8k and stream_sid:
                                                # Send in smooth 320-byte (40ms) packets to prevent Twilio buffer jitter
                                                chunk_size = 320
                                                for i in range(0, len(mulaw8k), chunk_size):
                                                    chunk = mulaw8k[i:i + chunk_size]
                                                    b64_payload = base64.b64encode(chunk).decode("ascii")
                                                    msg = json.dumps({
                                                        "event": "media",
                                                        "streamSid": stream_sid,
                                                        "media": {"payload": b64_payload}
                                                    })
                                                    await websocket.send_text(msg)
                                                    if len(mulaw8k) > chunk_size * 2:
                                                        await asyncio.sleep(0.015)

                            # Handle autonomous function/tool calls from Gemini Live
                            if response.tool_call:
                                for fc in response.tool_call.function_calls:
                                    logger.info(f"[TOOL_CALL] Gemini invoked '{fc.name}' with args: {fc.args}")
                                    call_state.dispatched_tools.append(fc.name)
                                    result_data = {"status": "success"}

                                    try:
                                        from src.voice.twilio_server import broadcast_event
                                        asyncio.create_task(broadcast_event("tool_invoked", {
                                            "tool_name": fc.name,
                                            "args": fc.args,
                                            "stream_sid": stream_sid
                                        }))
                                    except Exception:
                                        pass

                                    if fc.name == "dispatch_quickstart_email":
                                        email = fc.args.get("email") if fc.args else None
                                        if email:
                                            call_state.captured_email = email
                                            call_state.stage = ConversationStage.WRAP_UP
                                            phone = query_params.get("phone")
                                            if phone:
                                                try:
                                                    from src.voice.twilio_server import send_outbound_sms
                                                    asyncio.create_task(send_outbound_sms(phone, email=email, lead_name=prospect_name))
                                                except Exception as ex:
                                                    logger.warning(f"SMS dispatch note: {ex}")
                                        result_data = {
                                            "status": "dispatched",
                                            "message": f"Quickstart repository and architecture overview dispatched to {email}."
                                        }

                                    elif fc.name == "log_detected_stack":
                                        frameworks = fc.args.get("frameworks", []) if fc.args else []
                                        pains = fc.args.get("pain_points", []) if fc.args else []
                                        call_state.detected_frameworks.update(frameworks)
                                        call_state.detected_pains.update(pains)
                                        result_data = {"status": "logged", "frameworks": list(frameworks)}

                                    elif fc.name == "schedule_followup":
                                        time_pref = fc.args.get("preferred_time", "this week") if fc.args else "this week"
                                        email = fc.args.get("email", call_state.captured_email or "") if fc.args else ""
                                        result_data = {"status": "scheduled", "time_window": time_pref, "email": email}

                                    elif fc.name == "check_framework_compatibility":
                                        fw_name = fc.args.get("framework_name", "").lower().strip() if fc.args else ""
                                        compat_info = get_framework_compatibility_info(fw_name)
                                        call_state.detected_frameworks.add(compat_info.get("framework", fw_name))
                                        result_data = compat_info

                                    elif fc.name == "drop_voicemail_and_hangup":
                                        call_state.recipient_type = CallRecipientType.VOICEMAIL
                                        call_state.stage = ConversationStage.VOICEMAIL_DROP
                                        result_data = {"status": "voicemail_ready"}

                                    fn_response = types.FunctionResponse(
                                        name=fc.name,
                                        id=fc.id,
                                        response=result_data
                                    )
                                    await session.send_tool_response(function_responses=[fn_response])
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
