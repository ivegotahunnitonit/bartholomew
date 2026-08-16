# 📚 TECHNICAL DOCUMENTATION & DEPLOYMENT GUIDE

## Architecture Summary

Agentic-Eval is constructed as a decoupled, multi-language microservices architecture:

```
┌─────────────────────────────────────────────────────────────┐
│  GLASSMORPHISM FRONTEND UI (dashboard/orchestrator.html)     │
└──────────────────────────────┬──────────────────────────────┘
                               │ HTTP / REST API Calls
                               ▼
┌─────────────────────────────────────────────────────────────┐
│  FASTAPI PYTHON BACKEND (python_backend/app/main.py)         │
│  - Agentic QA Evaluation Engine (agent_eval_janitor.py)      │
│  - Cryptographic Security Engine (encryption_and_security.py)│
│  - AI Benchmark Leaderboard (agent_eval_leaderboard.py)     │
│  - Micro-SaaS Arbitrage Engine (domain_saas_arbitrage.py)   │
└──────────────────────────────┬──────────────────────────────┘
                               │ Local Inter-Service Calls
                               ▼
┌─────────────────────────────────────────────────────────────┐
│  GO SECURITY MICROSERVICE (go_services/main.go)              │
│  - Port 8085 High-Speed Security Probes                      │
└─────────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick 1-Click Deployment Setup

### Option 1: Render ($0.00 Free Hosting)
1. Fork or upload the repository to GitHub.
2. Go to `render.com` -> New Web Service -> Connect Repository.
3. Select `render.yaml`. Click **Apply**. Render will automatically build and deploy the service.

### Option 2: Vercel ($0.00 Free Hosting)
1. Install Vercel CLI: `npm install -g vercel`.
2. Run `vercel` in root directory. Vercel automatically reads `vercel.json` and provisions the static frontend and Python serverless functions.

---

## 🔌 Mounted API Endpoints

- `POST /api/janitor/audit` — Evaluates AI Agent step trajectory JSON for secret leaks and loop errors.
- `POST /api/security/ai-proof` — Generates SHA-256 checksum attestations and AES-256 ciphertext.
- `GET /api/benchmark/leaderboard` — Returns benchmark rankings for AI Agent frameworks.
- `POST /api/v1/mask-secrets` — Scrubs unmasked API credentials from text logs.
- `POST /api/v1/sanitize-trajectory` — Scrubs secrets, passwords, and sensitive keys from step trajectory dumps.
- `GET /api/v1/security-health` — Real-time system security posture, AES-256 state, and rate-limiter checkpoint.
- `GET /api/v1/onchain-context` — Real-time enriched EVM event data context feeds.
- `GET /api/arbitrage/opportunities` — Scans dropped domain flip opportunities.
- `POST /api/arbitrage/tier-manifest` — Generates structured 3-tier valuation manifest ($500 / $1,250 / $2,500).

---

## 🧪 System Verification

Run automated test suite:
```bash
python test_revenue_engines.py
```
*Executes 7 unit & integration tests across security, payment gateways, notary engines, yield aggregators, DePIN compute nodes, domain arbitrage, and trajectory sanitizers.*

