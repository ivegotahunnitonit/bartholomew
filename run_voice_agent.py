"""
Bartholomew Trust Protocol (BTP v5.4) — Voice AI Outbound Caller Service Runner
Starts the FastAPI server with Twilio MediaStream WebSockets and the Web Audio Bench.
"""

import uvicorn
from src.voice.voice_config import config

def main():
    print("=" * 72)
    print("  Bartholomew (BTP v5.4) — Outbound Voice AI Cold Calling Engine")
    print("=" * 72)
    print(f"[*] Voice Server Host: {config.server_host}:{config.server_port}")
    print(f"[*] Interactive Browser Test Bench: http://localhost:{config.server_port}/voice")
    print(f"[*] Twilio Webhook URL: {config.public_base_url.rstrip('/')}/voice/twiml")
    print(f"[*] Twilio Status: {'CONNECTED' if config.is_twilio_ready() else 'SIMULATED (add TWILIO_* in .env to dial)'}")
    print(f"[*] OpenAI Voice Status: {'CONNECTED' if config.is_openai_ready() else 'SIMULATED (add OPENAI_API_KEY to stream)'}")
    print("=" * 72)
    
    uvicorn.run(
        "src.voice.twilio_server:app",
        host=config.server_host,
        port=config.server_port,
        log_level="info",
        reload=False
    )

if __name__ == "__main__":
    main()
