"""
Bartholomew Trust Protocol (BTP v5.4) — Voice AI Engine Configuration
Handles environment credentials, audio formatting, and carrier settings.
"""

import os
from dataclasses import dataclass, field
from typing import Optional
from pathlib import Path

try:
    from dotenv import load_dotenv
    _env_path = Path(__file__).resolve().parent.parent.parent / ".env"
    if _env_path.exists():
        load_dotenv(dotenv_path=_env_path)
    else:
        load_dotenv()
except ImportError:
    pass


@dataclass
class VoiceConfig:
    """Configuration for Bartholomew Outbound Voice AI agent."""
    
    # Twilio Telephony Credentials
    twilio_account_sid: Optional[str] = field(
        default_factory=lambda: os.getenv("TWILIO_ACCOUNT_SID", "")
    )
    twilio_auth_token: Optional[str] = field(
        default_factory=lambda: os.getenv("TWILIO_AUTH_TOKEN", "")
    )
    twilio_phone_number: Optional[str] = field(
        default_factory=lambda: os.getenv("TWILIO_PHONE_NUMBER", "")
    )
    
    # OpenAI Realtime Voice API Credentials
    openai_api_key: Optional[str] = field(
        default_factory=lambda: os.getenv("OPENAI_API_KEY", "")
    )
    openai_realtime_model: str = field(
        default_factory=lambda: os.getenv(
            "OPENAI_REALTIME_MODEL", "gpt-4o-realtime-preview-2024-12-17"
        )
    )
    openai_voice: str = field(
        default_factory=lambda: os.getenv("OPENAI_VOICE", "alloy")
    )
    
    # Alternative Voice API (ElevenLabs / Cartesia / Deepgram)
    elevenlabs_api_key: Optional[str] = field(
        default_factory=lambda: os.getenv("ELEVENLABS_API_KEY", "")
    )
    deepgram_api_key: Optional[str] = field(
        default_factory=lambda: os.getenv("DEEPGRAM_API_KEY", "")
    )
    
    # Server & Webhook Networking
    server_host: str = field(
        default_factory=lambda: os.getenv("VOICE_SERVER_HOST", "0.0.0.0")
    )
    server_port: int = field(
        default_factory=lambda: int(os.getenv("VOICE_SERVER_PORT", "8765"))
    )
    public_base_url: str = field(
        default_factory=lambda: os.getenv("VOICE_PUBLIC_BASE_URL", "http://localhost:8765")
    )
    
    # Audio Engineering Specs
    twilio_sample_rate: int = 8000       # G.711 mu-law 8kHz mono
    openai_sample_rate: int = 24000      # Linear PCM16 24kHz mono
    browser_sample_rate: int = 24000     # Web Audio Linear PCM16 24kHz
    
    # Data Storage Paths
    leads_file_path: Path = field(
        default_factory=lambda: Path(__file__).resolve().parent.parent.parent / "leads_queue.json"
    )
    call_logs_path: Path = field(
        default_factory=lambda: Path(__file__).resolve().parent.parent.parent / "call_transcripts"
    )

    def is_twilio_ready(self) -> bool:
        """Check if real carrier credentials are provided."""
        return bool(
            self.twilio_account_sid 
            and self.twilio_auth_token 
            and self.twilio_phone_number
        )

    def is_openai_ready(self) -> bool:
        """Check if OpenAI Realtime key is present."""
        return bool(self.openai_api_key and len(self.openai_api_key.strip()) > 10)


# Global default configuration instance
config = VoiceConfig()
