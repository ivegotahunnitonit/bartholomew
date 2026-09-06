"""
Bartholomew Trust Protocol (BTP v5.4) — Realtime Bi-directional Voice Session
Manages WebSocket streaming to OpenAI Realtime API (or intelligent fallback simulator)
with instantaneous interruption (barge-in) and transcript telemetry.
"""

import asyncio
import json
import logging
import math
import struct
import time
from typing import AsyncGenerator, Callable, Dict, Any, List, Optional
import websockets

from .voice_config import config, VoiceConfig
from .sales_persona import generate_session_instructions, OBJECTIONS
from .lead_manager import Lead

logger = logging.getLogger("btp.voice.realtime")


class RealtimeVoiceSession:
    """
    Manages a single real-time voice call session.
    Streams bi-directional 24kHz PCM16 audio and handles real-time conversational events.
    """

    def __init__(
        self,
        lead: Optional[Lead] = None,
        voice_config: Optional[VoiceConfig] = None,
        on_audio_delta: Optional[Callable[[str], Any]] = None,
        on_transcript_delta: Optional[Callable[[str, str], Any]] = None,
        on_interruption: Optional[Callable[[], Any]] = None,
    ):
        self.lead = lead or Lead(name="Engineer", company="AI Team")
        self.cfg = voice_config or config
        self.on_audio_delta = on_audio_delta
        self.on_transcript_delta = on_transcript_delta
        self.on_interruption = on_interruption
        
        self.ws: Optional[websockets.WebSocketClientProtocol] = None
        self.is_active = False
        self.transcript: List[Dict[str, str]] = []
        self.current_ai_buffer: List[str] = []
        self.current_user_buffer: List[str] = []
        self.conversation_turn = 0
        self.start_time = 0.0

    async def start(self) -> None:
        """Initialize the real-time session."""
        self.is_active = True
        self.start_time = time.time()
        
        if self.cfg.is_openai_ready():
            await self._connect_openai_realtime()
        else:
            logger.info("OpenAI API key not set — initializing intelligent simulated voice engine.")
            await self._start_simulated_session()

    async def _connect_openai_realtime(self) -> None:
        """Connect to official OpenAI Realtime WebSocket API."""
        url = f"wss://api.openai.com/v1/realtime?model={self.cfg.openai_realtime_model}"
        headers = {
            "Authorization": f"Bearer {self.cfg.openai_api_key}",
            "OpenAI-Beta": "realtime=v1"
        }
        
        try:
            self.ws = await websockets.connect(url, extra_headers=headers)
            
            # Configure Realtime Session
            session_update = {
                "type": "session.update",
                "session": {
                    "modalities": ["audio", "text"],
                    "instructions": generate_session_instructions(
                        prospect_name=self.lead.name,
                        company_name=self.lead.company
                    ),
                    "voice": self.cfg.openai_voice,
                    "input_audio_format": "pcm16",
                    "output_audio_format": "pcm16",
                    "input_audio_transcription": {
                        "model": "whisper-1"
                    },
                    "turn_detection": {
                        "type": "server_vad",
                        "threshold": 0.5,
                        "prefix_padding_ms": 300,
                        "silence_duration_ms": 500
                    }
                }
            }
            await self.ws.send(json.dumps(session_update))
            
            # Trigger immediate opening greeting
            await self.trigger_greeting()
            
            # Run background receiver loop
            asyncio.create_task(self._openai_receive_loop())
            
        except Exception as e:
            logger.error(f"Failed to connect to OpenAI Realtime: {e}. Falling back to simulation mode.")
            await self._start_simulated_session()

    async def _openai_receive_loop(self) -> None:
        """Process incoming WebSocket frames from OpenAI."""
        try:
            while self.is_active and self.ws:
                msg_str = await self.ws.recv()
                event = json.loads(msg_str)
                event_type = event.get("type", "")

                # 1. User interruption / Barge-in
                if event_type == "input_audio_buffer.speech_started":
                    if self.on_interruption:
                        self.on_interruption()

                # 2. Audio Delta Output from AI
                elif event_type == "response.audio.delta":
                    delta_b64 = event.get("delta", "")
                    if delta_b64 and self.on_audio_delta:
                        self.on_audio_delta(delta_b64)

                # 3. AI Transcript Delta
                elif event_type == "response.audio_transcript.delta":
                    delta_text = event.get("delta", "")
                    if delta_text:
                        self.current_ai_buffer.append(delta_text)
                        if self.on_transcript_delta:
                            self.on_transcript_delta("assistant", delta_text)

                # 4. AI Finished Turn
                elif event_type == "response.audio_transcript.done":
                    full_ai_turn = "".join(self.current_ai_buffer).strip()
                    if full_ai_turn:
                        self.transcript.append({"role": "assistant", "content": full_ai_turn})
                    self.current_ai_buffer = []

                # 5. User Speech Transcription Completed
                elif event_type == "conversation.item.input_audio_transcription.completed":
                    user_text = event.get("transcript", "").strip()
                    if user_text:
                        self.transcript.append({"role": "user", "content": user_text})
                        if self.on_transcript_delta:
                            self.on_transcript_delta("user", user_text)

        except Exception as e:
            logger.warning(f"OpenAI receive loop closed: {e}")
        finally:
            self.is_active = False

    async def send_audio_chunk(self, pcm16_24k_b64: str) -> None:
        """Stream an inbound audio chunk from the prospect to the AI."""
        if not self.is_active:
            return

        if self.ws and self.cfg.is_openai_ready():
            append_event = {
                "type": "input_audio_buffer.append",
                "audio": pcm16_24k_b64
            }
            await self.ws.send(json.dumps(append_event))
        else:
            # Simulated engine receives chunk
            await self._simulate_audio_processing(pcm16_24k_b64)

    async def trigger_greeting(self) -> None:
        """Trigger the AI to speak the cold call opening hook."""
        if self.ws and self.cfg.is_openai_ready():
            prompt_greeting = {
                "type": "response.create",
                "response": {
                    "instructions": f"Introduce yourself to {self.lead.name} at {self.lead.company} using the opening hook. Keep it to one short sentence."
                }
            }
            await self.ws.send(json.dumps(prompt_greeting))
        else:
            # Simulation greeting
            greeting = f"Hey {self.lead.name}, this is Alex from Bartholomew. Saw your team is building with autonomous agents at {self.lead.company} — did I catch you in the middle of something?"
            await self._dispatch_simulated_ai_response(greeting)

    async def handle_user_text_input(self, text: str) -> None:
        """Handle direct text input (e.g. from web test bench or transcription)."""
        self.transcript.append({"role": "user", "content": text})
        if self.on_transcript_delta:
            self.on_transcript_delta("user", text)

        # Match against objection matrix
        text_lower = text.lower()
        matched_reply = None
        for obj in OBJECTIONS:
            if any(kw in text_lower for kw in obj.keywords):
                matched_reply = obj.suggested_reply
                break

        if matched_reply:
            reply = matched_reply
        elif self.conversation_turn == 0:
            reply = (
                "Thanks! We built Bartholomew — an open-source in-process AST firewall for AI agents. "
                "When agents execute terminal or SQL tools, prompt injections or hallucinations can run destructive commands like rm -rf. "
                "Have you guys run into tool-safety or spend runaway issues yet?"
            )
        elif self.conversation_turn == 1:
            reply = (
                "Bartholomew is a deterministic Python AST gate that blocks dangerous commands in under 35 microseconds before anything hits the OS. "
                "It installs with pip install btp-guard. I'd love to send you our 2-page developer quickstart and repo. What's the best email for you?"
            )
        else:
            reply = "You got it. You can check out bartholomew.info or test it locally with pip install btp-guard. Really appreciate your time today!"

        self.conversation_turn += 1
        await self._dispatch_simulated_ai_response(reply)

    async def _start_simulated_session(self) -> None:
        """Run intelligent mock session with realistic pacing."""
        await asyncio.sleep(0.5)
        await self.trigger_greeting()

    async def _simulate_audio_processing(self, pcm16_24k_b64: str) -> None:
        """Analyze audio energy in simulated mode."""
        # When simulated, the web tester can send text directly or invoke handle_user_text_input
        pass

    async def _dispatch_simulated_ai_response(self, text: str) -> None:
        """Simulate incremental token delivery and generate audible tone burst for testing."""
        self.transcript.append({"role": "assistant", "content": text})
        
        # Incremental transcript delivery
        words = text.split(" ")
        for w in words:
            if not self.is_active:
                break
            if self.on_transcript_delta:
                self.on_transcript_delta("assistant", w + " ")
            await asyncio.sleep(0.04)

        # Generate a mild synthetic audio beep/chime tone sequence so the user's browser/phone has audible feedback
        if self.on_audio_delta:
            synth_audio_b64 = self._generate_synthetic_speech_placeholder(len(text) * 40)
            self.on_audio_delta(synth_audio_b64)

    def _generate_synthetic_speech_placeholder(self, duration_ms: int = 1000) -> str:
        """Generate a subtle audible 440Hz/554Hz pleasant dual-tone placeholder in 24kHz PCM16."""
        import base64
        num_samples = int(24000 * (min(duration_ms, 2000) / 1000.0))
        samples = []
        for i in range(num_samples):
            t = i / 24000.0
            # Pleasant low-amplitude bell envelope
            env = math.exp(-2.5 * (i / num_samples))
            val = int(env * 1500 * (math.sin(2 * math.pi * 440 * t) + 0.5 * math.sin(2 * math.pi * 554 * t)))
            samples.append(val)
        pcm_bytes = struct.pack(f"<{len(samples)}h", *samples)
        return base64.b64encode(pcm_bytes).decode("ascii")

    async def close(self) -> None:
        """Gracefully end the session and return duration & transcript."""
        self.is_active = False
        if self.ws:
            try:
                await self.ws.close()
            except Exception:
                pass
            self.ws = None

    def get_duration(self) -> int:
        return int(time.time() - self.start_time) if self.start_time else 0
