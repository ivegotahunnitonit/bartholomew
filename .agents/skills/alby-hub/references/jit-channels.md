# JIT Channels

A **JIT (Just-In-Time) channel** lets a hub receive its first lightning payment **without opening a channel first**. When you have no inbound liquidity and create an invoice for an amount larger than you can currently receive, a Lightning Service Provider (LSP) opens a channel "just in time" to route the incoming payment. The channel-opening fee is **deducted from that payment** — there is no upfront invoice or on-chain deposit to pay.

**JIT is the default way to get a new hub's first channel** — the user just shares an invoice, and the first payment both funds the wallet and opens the channel. Prefer it over ordering a channel up front for the common "I want to receive my first payment" case.

> **LDK only.** JIT channels work **only on the LDK backend**. Of the other backends with user-managed channels — **LND and CLN** — there is no JIT, so the user must order a channel up front via an [LSP](./lsp.md) before they can receive. Phoenixd manages its own liquidity automatically and Cashu uses ecash with no channels, so neither JIT nor LSP channel orders apply there.

## How it works via the CLI

There is **no special JIT command**. Just create an invoice as normal:

```bash
npx -y @getalby/hub-cli@0.6.0 make-invoice --amount <sats> --description "..."
```

If all of these are true, the hub automatically returns a JIT invoice:

- The backend is **LDK** (JIT channels are LDK-only).
- A JIT liquidity source (LSP) is configured for the network — see `get-info`.
- The hub has **no usable inbound capacity / no channel yet**.
- The requested amount is **above your current receive capacity** and within the LSP's supported payment range.

When the invoice is paid, the LSP opens the channel and the payment lands minus the fee. After that, normal receiving is used — JIT does not apply once you have enough inbound liquidity.

## Checking JIT availability and limits

`get-info` exposes the JIT configuration. Inspect it before guiding a user through a first receive:

```bash
npx -y @getalby/hub-cli@0.6.0 get-info
```

Relevant fields:

- `jitChannelsEnabled` — whether the feature is turned on.
- `jitChannelsLiquiditySource` — the LSP (`pubkey@host:port`) that will open the channel. Empty/absent means JIT is not available on this network.
- `jitChannelsMinPaymentSizeMsat` — the **smallest** first payment that can open a JIT channel (in millisatoshis).
- `jitChannelsMaxPaymentSizeMsat` — the **largest** single payment a JIT channel will accept (in millisatoshis).

The **first invoice amount must fall within the min/max range**. If the user wants to receive less than the minimum, JIT cannot help — they would need to order a channel up front instead (see below). Convert msat → sats (divide by 1000) when explaining limits to the user.

## Fees

The LSP's channel-opening fee is **skimmed from the incoming payment** — the user receives the invoice amount **minus** the fee. Set expectations before they share the invoice. For example: a 100,000 sat invoice may credit ~99,000 sats after the LSP fee. The exact fee depends on the LSP and the amount.

## JIT channels vs. ordering a channel

These are two distinct ways to get inbound liquidity:

| | **JIT channel** (this page) | **LSP channel order** ([LSP](./lsp.md)) |
|---|---|---|
| Trigger | Automatic, on first receive | You request it explicitly (`request-lsp-order`) |
| Cost | Fee deducted from the received payment | You pay a lightning invoice up front |
| When | You're about to receive a payment | You want inbound capacity ready in advance, or another channel |
| Effort | Just `make-invoice` | Order, then pay the LSP invoice |

Guidance (LDK):

- If the user **just wants to receive a payment** and has no channel, JIT is the **default** path — no separate setup.
- Use the [LSP order flow](./lsp.md) (`request-lsp-order`) only when the user wants liquidity **ready before** any payment arrives, wants a specific channel size, the amount falls outside the JIT min/max range, or they already have a channel and need another.

On **LND and CLN** (the other channel-managed backends) JIT does not exist, so ordering a channel up front via an [LSP](./lsp.md) is the only way to get inbound liquidity. Phoenixd and Cashu don't use channel orders at all — Phoenixd handles liquidity automatically and Cashu has no channels.

## Notes

- JIT channels require the **LDK** backend.
- The CLI **cannot toggle** `jitChannelsEnabled`. To enable or disable JIT channels, the user must use the Alby Hub web interface.
- Channel privacy still applies — see [LSP](./lsp.md). Keep all channels private or all public; do not mix.
- After a JIT channel opens, follow up as with any new channel — see [Channels](./channels.md) for confirmation status.
