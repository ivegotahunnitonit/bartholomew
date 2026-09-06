# Bartholomew Voice AI (BTP v5.4) — Outbound Cold Calling Engine

An in-house, low-latency, speech-to-speech outbound cold calling system engineered specifically to sell **Bartholomew (BTP v5.4)** to engineering leaders, AI engineers, and tech executives deploying autonomous agents.

---

## 1. System Architecture

```
                                      +---------------------------------------------+
                                      |          Bartholomew Voice Server           |
                                      |             (FastAPI + WebSockets)          |
                                      +---------------------------------------------+
                                                     |               |
             +---------------------------------------+               +---------------------------------------+
             |                                                                                               |
+--------------------------+                                                                   +---------------------------+
|      Twilio Voice        |                                                                   |    Browser Audio Bench    |
|   (Telephony Carrier)    |                                                                   |  (Web Audio Mic & Speaker)|
|  8kHz ITU-T G.711 μ-law  |                                                                   |       24kHz PCM16         |
+--------------------------+                                                                   +---------------------------+
             |                                                                                               |
             +----------------------------> [ AudioCodec ] <-------------------------------------------------+
                                      (mu-law <-> PCM16 24k)
                                                 |
                                                 v
                                   [ RealtimeVoiceSession ]
                               (OpenAI Realtime API / Simulator)
                                                 |
                         +-----------------------+-----------------------+
                         |                                               |
                         v                                               v
              [ Sales Persona: Alex ]                         [ Lead Queue Manager ]
        - Engineer-to-Engineer Pitch                    - Persistent JSON/CSV Storage
        - Sub-35μs AST Firewall Value                   - Automated Call Outcome Tracking
        - Objection Matrix (OpenAI, Cost, Integration)  - Full Conversation Transcripts
```

---

## 2. Quick Start: Test in 10 Seconds (Zero-Cost Simulation)

You can test the conversational AI and objection responses right from your computer without spending a dime on API credits or telephony:

1. **Start the Voice Server**:
   ```powershell
   python run_voice_agent.py
   ```
2. **Open the Web Audio Bench**:
   Navigate to [http://localhost:8765/voice](http://localhost:8765/voice) or the live hosted bench at [https://bartholomew.info/voice/](https://acn-26670.web.app/voice/).
3. **Click "Start Interactive Call"**:
   - Alex introduces himself with the engineer-to-engineer hook.
   - Click any objection button (e.g., *"Already have OpenAI guardrails"*, *"How much does it cost?"*, *"How hard to install?"*).
   - Listen to Alex's technical rebuttal and watch the live transcript stream in real time.

---

## 3. Connecting Real Outbound Calls (Twilio Carrier)

To place real phone calls to prospects' mobile phones:

### Step 1: Get a Twilio Number ($1.15/month)
1. Sign up or log into [twilio.com](https://www.twilio.com).
2. Go to **Phone Numbers** &rarr; **Buy a Number** (costs ~$1.15/mo).
3. Copy your:
   - `TWILIO_ACCOUNT_SID`
   - `TWILIO_AUTH_TOKEN`
   - `TWILIO_PHONE_NUMBER` (in E.164 format, e.g. `+14155551234`)

### Step 2: Configure Environment Variables
Add the following to your `.env` file or environment:
```env
TWILIO_ACCOUNT_SID=ACXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
TWILIO_AUTH_TOKEN=your_auth_token_here
TWILIO_PHONE_NUMBER=+14155551234
OPENAI_API_KEY=your_openai_api_key_here
VOICE_PUBLIC_BASE_URL=https://your-domain-or-ngrok.ngrok-free.app
```

### Step 3: Trigger Outbound Dialing
To dial a lead via the REST API:
```bash
curl -X POST "http://localhost:8765/api/dial?phone=+14155559876"
```
Or click **"Dial Real Phone Number"** directly in the Web Audio Bench!

---

## 4. Sales Script & Cold Calling Strategy

### Persona: "Alex" (Senior Infrastructure Engineer at Bartholomew)
- **Opening Hook**:
  > *"Hey [Name], this is Alex from Bartholomew. Saw your team is building with autonomous agents at [Company] — did I catch you in the middle of something?"*
- **Problem Formulation**:
  > *"We built Bartholomew — an open-source in-process AST firewall for AI agents. When agents have terminal or SQL tools, prompt injections or hallucinations can cause them to run destructive commands like `rm -rf` or drop tables. Have you guys run into tool-safety or spend runaway issues in your pipelines?"*
- **The Value Proposition**:
  > *"It's a deterministic Python AST gate that blocks dangerous commands in under 35 microseconds before anything hits the OS. Installs with `pip install btp-guard` and wraps CrewAI or LangGraph with 1 line of code."*
- **The Call-to-Action (CTA)**:
  > *"I'd love to send you our 2-page developer quickstart and the GitHub repo so you can inspect the code. What's the best email for you?"*

### Objection Handling Matrix
| Objection | Alex's Proven Response |
| :--- | :--- |
| **"We already use OpenAI system prompts / guardrails."** | *"Totally hear you. System prompts are great for tone, but prompt injections easily bypass them. Bartholomew is deterministic syntax parsing right before `subprocess` or database execution — so even if the model hallucinates or gets jailbroken, the OS never receives the bad command."* |
| **"How much does it cost?"** | *"The core engine is 100% free and open-source under Apache 2.0 via `pip install btp-guard`. We only have a $49/mo team plan if you need multi-tenant workspace keys or certified SOC 2 audit packages."* |
| **"How hard is it to integrate?"** | *"Literally one line. You import `BTPTaskGuard` and wrap your existing agent tasks. Zero architecture rewrites."* |
| **"I am too busy right now."** | *"Completely understand, I know you're in the middle of your day. Can I shoot you a quick 30-second link to `bartholomew.info` to check out whenever you have a minute?"* |
| **"Send me an email."** | *"You got it. What's the best email for you? I'll send over the GitHub repo and the 1-line integration snippet."* |

---

## 5. Queue Management & Lead Tracking

All outbound dialing state is persistently tracked in [`leads_queue.json`](file:///c:/Users/User/.gemini/antigravity/scratch/autonomous-circularity-network/leads_queue.json).

### Status States:
- `PENDING`: Ready to be dialed.
- `CALLING`: Dial in progress.
- `CONNECTED`: Prospect answered.
- `QUALIFIED`: Agreed to review docs or book engineering screen.
- `NOT_INTERESTED`: Gracefully declined.
- `VOICEMAIL`: Reached answering machine.
- `DO_NOT_CALL`: Opted out.

### Adding Leads via CSV:
Create a CSV with columns: `name,company,phone,email,role` and place it in the workspace, or use the `LeadManager.import_from_csv()` method.
