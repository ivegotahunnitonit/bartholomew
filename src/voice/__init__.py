"""
Bartholomew Trust Protocol (BTP v5.4) — Voice AI Package
"""

from .voice_config import VoiceConfig, config
from .audio_codec import AudioCodec
from .sales_persona import COLD_CALL_SYSTEM_PROMPT, OBJECTIONS, generate_session_instructions
from .lead_manager import LeadManager, Lead, LeadStatus
from .realtime_session import RealtimeVoiceSession
from .twilio_server import app

__all__ = [
    "VoiceConfig",
    "config",
    "AudioCodec",
    "COLD_CALL_SYSTEM_PROMPT",
    "OBJECTIONS",
    "generate_session_instructions",
    "LeadManager",
    "Lead",
    "LeadStatus",
    "RealtimeVoiceSession",
    "app",
]
