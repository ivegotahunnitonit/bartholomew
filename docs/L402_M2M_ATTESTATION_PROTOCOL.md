# ⚡ L402 Machine-to-Machine (M2M) Attestation Protocol

Bartholomew implements native **HTTP 402 Payment Required** and **L402 Lightning Network** attestation for autonomous AI agent swarms.

Instead of human subscription accounts or manual invoicing, autonomous agents pay per signed cryptographic receipt directly on the wire in sub-millisecond settlement cycles.

---

## 1. How the M2M Flow Works

```
  [ Autonomous Agent Swarm ]                  [ Bartholomew Invariant Gate ]
              │                                             │
              ├─── 1. Proposed Tool Call (Payload) ────────►│
              │                                             │ (Evaluates AST Invariants <35µs)
              │◄── 2. HTTP 402 Challenge (L402 Macaroon) ──┤
              │                                             │
              ├─── 3. Lightning Preimage + Macaroon ───────►│ (Settles 10 sats)
              │                                             │
              │◄── 4. RFC 8785 Ed25519 Signed Receipt ──────┤ (Tamper-proof Attestation)
              ▼                                             ▼
```

### Protocol Specifications
- **Header:** `WWW-Authenticate: L402 token="<macaroon>", invoice="lnbc..."`
- **Cost:** 10 satoshis ($0.0001) per cryptographically signed attestation receipt.
- **Settlement Dest:** Lightning Network / Base EIP-712 Micro-Escrows.
- **Latency:** Execution gating runs in `<35µs`; receipts stream over persistent WebSocket / WireGuard tunnels.

---

## 2. Agent Swarm Integration

```python
from btp_guard import WireGuard, Guard

# Initialize autonomous M2M wire client with L402 wallet
wire = WireGuard(wallet_backend="l402", auto_settle=True)

# Every protected tool call automatically requests and pays for Ed25519 signed receipts
receipt = wire.attest_and_execute("rm -rf /tmp/cache")
print("Signed Attestation Hash:", receipt["signature"])
```
