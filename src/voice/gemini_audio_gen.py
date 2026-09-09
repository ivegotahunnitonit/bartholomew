"""
Bartholomew Voice AI — Multi-Turn Conversational Gemini Native Voice Engine
===========================================================================
Provides dynamic, multi-turn conversational intelligence using Google Gemini Native Audio.
Maintains session history across turns so the dialogue flows organically based on
what the prospect actually says, while steering back to Bartholomew's core value:
sub-35µs in-process AST & execution dispatch gating for autonomous agents.
"""

import asyncio
import os
import wave
import uuid
import logging
from pathlib import Path
from typing import Dict, List, Optional
from google import genai
from google.genai import types

logger = logging.getLogger("btp.voice.gemini_audio")

SCRATCH_DIR = Path("scratch")
SCRATCH_DIR.mkdir(exist_ok=True)

DEFAULT_GREETING_WAV = SCRATCH_DIR / "gemini_alex_pitch_greeting.wav"
FALLBACK_GREETING_WAV = SCRATCH_DIR / "gemini_alex_greeting.wav"

CONVERSATIONAL_SYSTEM_INSTRUCTION = """
You are Alex, an infrastructure and security engineer calling another developer or tech lead over the phone.
You sound 100% like a real person having a quick phone conversation — casual, natural cadence, relaxed humor, peer-to-peer.

CORE PRODUCT & MISSION:
We built Bartholomew, an open-source in-process AI agent execution gateway (pip install btp-guard).
When autonomous agents run tools in production, prompt injections or hallucinations cause catastrophic actions: rm -rf, DROP TABLE, runaway loops, or secret leaks.
Bartholomew acts as a sub-35 microsecond in-process execution firewall. It parses the AST and intercepts tool dispatch in memory before anything touches the operating system or database. Zero cloud lag.

CRITICAL CONVERSATIONAL RULES:
1. EXTREME BREVITY: 1 to 2 short sentences MAX per response. Never monologue or recite bullet lists.
2. ACTIVE LISTENING: Directly address what the person just said first ("Haha yeah, totally", "Fair point man", "Gotcha, makes sense").
3. PROBLEM-FIRST & SOLUTION: Frame everything around agent execution disasters and how easy it is to fix (single decorator, pip install btp-guard).
4. HANDLE TECHNICAL OBJECTIONS WITH CONFIDENCE:
   - If they ask about "Static AST vs runtime indirection" (getattr, eval, dynamic strings):
     Explain: "Great question! Pre-flight AST catches literal attacks in 30 microseconds, but we also gate the execution dispatch seam in memory, inspecting the resolved arguments before invocation."
   - If they say "We already use LLM guardrails / LlamaGuard / NeMo":
     Explain: "Yeah, dialog rails are great for chat, but they add 300 milliseconds of cloud latency and don't stop an agent once it invokes a bash or SQL tool in memory."
   - If they ask "Is it open source / where can I see it?":
     Say: "Yeah, totally open-source on GitHub and PyPI as btp-guard, docs at bartholomew.info."
5. IF INTERRUPTED OR TOLD TO WAIT:
   Say: "Sure thing man, take your time."
6. CALL-TO-ACTION / CLOSING:
   When they show interest or ask to follow up, offer: "Can I shoot you the 1-page quickstart or check out bartholomew.info?"
""".strip()


class ConversationalSessionManager:
    """Tracks multi-turn conversation context per call session."""
    def __init__(self):
        self.sessions: Dict[str, List[types.Content]] = {}

    def get_or_create_session(self, call_sid: str) -> List[types.Content]:
        if call_sid not in self.sessions:
            # Seed session with the opening dialogue exchange
            self.sessions[call_sid] = [
                types.Content(
                    role="model",
                    parts=[types.Part.from_text(
                        text="Hey! This is Alex. Caught you randomly — saw your team is building with autonomous agents. "
                             "We built Bartholomew, an open-source in-process firewall that blocks rogue shell and database "
                             "commands in 35 microseconds before anything touches your OS. Did I catch you in the middle of a deploy fire, or do you have 30 seconds?"
                    )]
                )
            ]
        return self.sessions[call_sid]

    def add_user_turn(self, call_sid: str, speech_text: str):
        session = self.get_or_create_session(call_sid)
        session.append(types.Content(
            role="user",
            parts=[types.Part.from_text(text=speech_text)]
        ))

    def add_model_turn(self, call_sid: str, response_text: str):
        session = self.get_or_create_session(call_sid)
        session.append(types.Content(
            role="model",
            parts=[types.Part.from_text(text=response_text)]
        ))

    def clear_session(self, call_sid: str):
        self.sessions.pop(call_sid, None)


# Global in-memory session manager
dialog_manager = ConversationalSessionManager()


async def generate_gemini_conversational_reply_wav(user_speech: str, call_sid: str) -> Path:
    """
    Feeds the user's spoken input into the conversational session and generates
    a 24kHz studio-quality WAV reply using Gemini Native Audio (voice: Puck).
    """
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    client = genai.Client(api_key=api_key)

    dialog_manager.add_user_turn(call_sid, user_speech)
    history = dialog_manager.get_or_create_session(call_sid)

    config = types.LiveConnectConfig(
        response_modalities=["AUDIO"],
        speech_config=types.SpeechConfig(
            voice_config=types.VoiceConfig(
                prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name="Puck")
            )
        ),
        system_instruction=types.Content(
            parts=[types.Part.from_text(text=CONVERSATIONAL_SYSTEM_INSTRUCTION)]
        )
    )

    audio_bytes = bytearray()
    model_reply_text = ""
    model = "gemini-2.5-flash-native-audio-latest"

    try:
        async with client.aio.live.connect(model=model, config=config) as session:
            # Send the accumulated dialogue turns
            await session.send_client_content(turns=history, turn_complete=True)

            async for resp in session.receive():
                sc = resp.server_content
                if sc and sc.model_turn:
                    for part in sc.model_turn.parts:
                        if part.inline_data and part.inline_data.data:
                            audio_bytes.extend(part.inline_data.data)
                        if part.text:
                            model_reply_text += part.text
                if sc and sc.turn_complete:
                    break

        # Record model turn in conversation history
        dialog_manager.add_model_turn(call_sid, model_reply_text or "Got it, talk soon.")

        out_path = SCRATCH_DIR / f"reply_{call_sid}_{uuid.uuid4().hex[:6]}.wav"
        with wave.open(str(out_path), "wb") as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(24000)
            wav_file.writeframes(bytes(audio_bytes))

        logger.info(f"Generated conversational reply for [{call_sid}]: {out_path} ({len(audio_bytes)} bytes)")
        return out_path

    except Exception as e:
        logger.error(f"Failed to generate Gemini conversational audio for [{call_sid}]: {e}")
        if DEFAULT_GREETING_WAV.exists():
            return DEFAULT_GREETING_WAV
        return FALLBACK_GREETING_WAV


# Backwards-compatible alias
async def generate_gemini_speech_wav(prompt: str, session_id: str) -> Path:
    return await generate_gemini_conversational_reply_wav(prompt, session_id)
