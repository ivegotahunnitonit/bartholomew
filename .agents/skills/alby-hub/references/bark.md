# Bark (Ark)

Bark is an [Ark](https://second.tech/) client backend. Instead of opening lightning channels, it connects to an **Ark server** that provides liquidity, so the user can send and receive lightning payments immediately with **no channel or on-chain management**. This is the simplest backend to get started with, but it has important trade-offs (see Limitations).

> **Bark is BETA — use at your own risk.**

## Setup

Bark has no CLI flags of its own — it's configured via environment variables read by the hub at startup, but the mainnet defaults work out of the box, so you only need `--backend BARK`. The mnemonic is generated automatically; do not pass `--mnemonic`.

```bash
npx -y @getalby/hub-cli@0.6.0 setup --password YOUR_PASSWORD --backend BARK
```

The backend is fixed at setup time and cannot be changed afterwards without re-initialising the hub.

## Next Steps: Add Funds

A Bark hub needs **no channels and no on-chain deposit** — funds are usable as soon as setup completes, so skip the LSP / channel-opening flow from [Initial Setup](./initial-setup.md).

To add funds, the user simply **receives a lightning payment**. Create an invoice and have them pay it from any other lightning wallet:

```bash
npx -y @getalby/hub-cli@0.6.0 make-invoice --amount <sats> --description "..."
```

> When telling the user what to do next, say they can **start by receiving a lightning payment**. Do **not** describe it as "funding via the Ark/bark server" — to the user it is just a normal incoming lightning payment; the Ark server only provides the liquidity behind the scenes.

## Configuration

| Env var | Default | Purpose |
| ------- | ------- | ------- |
| `LN_BACKEND_TYPE` | — | Set to `BARK` (or pass `--backend BARK` to `setup`) |
| `BARK_SERVER` | `https://ark.second.tech` | Ark server URL |
| `BARK_ESPLORA_SERVER` | `https://mempool.second.tech/api` | Esplora server URL for chain data |
| `BARK_SERVER_ACCESS_TOKEN` | (none) | Optional — only required for a private Ark server |
| `BARK_LOG_LEVEL` | `3` | Bark-specific log verbosity (higher is more verbose). Separate from the main app log level |

## Limitations

- **No channels.** Channel and peer commands (open/close/connect) are no-ops, and `list-channels` returns an empty list. Skip the LSP / channel-opening flow from [Initial Setup](./initial-setup.md) — funds are usable as soon as setup completes.
- **No on-chain.** On-chain address, balance, and send/receive are unsupported. Swaps, keysend, HOLD invoices, BOLT-12 offers, and message signing are also unsupported.
- **Periodic refresh fees.** Bark funds (VTXOs) are refreshed periodically, which incurs a small fee.
- **Limited recovery.** During beta, funds **cannot be recovered from the recovery phrase alone** — the local bark wallet data directory (`<workdir>/bark`) is also required. Make sure the user backs up that directory, not just the mnemonic.
- **Requires persistent storage.** Like Cashu, bark stores wallet state on local disk with no remote-backup mechanism, so it is **not available on Alby Cloud** or other environments without a persistent volume.

## Debugging

Bark exposes [debug tools](./debug-tools.md) for inspecting wallet internals and recovering stuck funds:

- `debug` — dumps the balance breakdown, **VTXOs**, claimable lightning receive balance, movement history and Ark server info. This is the first thing to run when a receive did not credit the balance.
- `claimlightningreceives` — claims pending/unclaimed lightning receives.
- `runmaintenance` — progresses pending rounds and refreshes VTXOs (funds stuck "pending in round").

```bash
npx -y @getalby/hub-cli@0.6.0 execute-custom-node-command "debug"
```

See [Debug Tools](./debug-tools.md) for the full list and usage.

## Supported NWC methods

`pay_invoice`, `multi_pay_invoice`, `make_invoice`, `lookup_invoice`, `list_transactions`, `get_balance`, `get_budget`, `get_info`.
