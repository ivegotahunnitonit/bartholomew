# LSP

LSP (Lightning Service Provider) commands let you order a channel up front: an LSP opens a channel for you in exchange for a small fee paid via a lightning invoice — no on-chain bitcoin deposit required. You get both inbound (receive) and outbound (send) capacity immediately.

> **On LDK, you usually don't need to order a channel to receive a first payment** — a [JIT channel](./jit-channels.md) opens automatically instead. Use the order flow below only for liquidity in advance, a specific size, an extra channel, or on LND/CLN. See [JIT Channels](./jit-channels.md) for when each applies.

## Commands

```bash
# List available LSP providers with fees and channel size limits
npx -y @getalby/hub-cli@0.6.0 get-channel-suggestions

# Request a lightning invoice from an LSP to open an inbound channel
npx -y @getalby/hub-cli@0.6.0 request-lsp-order --amount <sats> --lsp-type <type> --lsp-identifier <identifier>

# Pay the LSP invoice to trigger channel opening (mainnet, requires funded wallet)
npx -y @getalby/hub-cli@0.6.0 pay-invoice <invoice>

# Request an Alby LSP channel offer (requires a linked Alby account)
npx -y @getalby/hub-cli@0.6.0 request-alby-lsp-channel-offer
```

## Typical LSP Channel Flow

```bash
# 1. List available LSPs (returned in priority order)
npx -y @getalby/hub-cli@0.6.0 get-channel-suggestions

# 2. Request an invoice from the chosen LSP
npx -y @getalby/hub-cli@0.6.0 request-lsp-order --amount <sats> --lsp-type <type> --lsp-identifier <identifier>

# 3. Pay the invoice to open the channel
npx -y @getalby/hub-cli@0.6.0 pay-invoice <invoice>
```

## Choosing an LSP

- `get-channel-suggestions` returns LSPs in **priority order** — use the first entry for which the hub does not already have an open channel with that LSP.
- **Do not open two channels with the same LSP** — prefer diversifying across providers.
- Filter the list to the user's active network (e.g. signet for Mutinynet, bitcoin for mainnet) before presenting options.

## Interpreting get-channel-suggestions Output

The `get-channel-suggestions` output includes fields like channel size and fee ranges per LSP. Key distinction:

- **Channel size** (e.g. `minimumChannelSize`, `maximumChannelSize`): The inbound capacity the LSP will open for you. This is NOT the amount you pay — it is what you _receive_ (ability to receive payments up to this amount). A 2,000,000 sat channel does not mean you need 2M sats.
- **Fee**: The small amount you actually pay to the LSP, via a lightning invoice returned by `request-lsp-order`. This is the only cost to the user.

When comparing LSPs for a user, compare fees (what they pay), not channel sizes. For example: "Provider A costs 5,762 sats to open a 2M sat channel" — not "if you have 2M sats available."

## Channel Size

Before requesting an invoice, **ask the user** how large a channel they want. Suggest **500,000 sats** as a reasonable default if they have no preference.

## Channel Privacy

**Private channels are the right choice for nearly all users — including for receiving payments.** Default to private and do not suggest public channels unless the user explicitly asks to run a public routing node.

### Private channels can receive payments — this is the default and it works

A private (unannounced) channel is **not** advertised in the public network graph, but that does **not** stop the node from receiving. When the hub has no public channels, it automatically embeds **route hints** in every BOLT11 invoice. A route hint tells the payer how to reach the node through its private channel's peer (typically a well-connected LSP), so the payment routes fine. This is a technical detail handled automatically — the user does not need to do anything, and they do **not** need a public channel.

- **Do NOT tell a user their node is "invisible" or "unreachable" because its channel is private.** With route hints, a private channel receives normally.
- **Do NOT recommend opening a public channel, an extra channel, or "inbound liquidity" as a fix simply because a channel is private.** Privacy is not the problem.

### When a payment can't be received

If receiving actually fails (e.g. "route not found" / "no route"), the cause is almost never channel privacy. Check, in order:

1. **Inbound (receiving) capacity** — the channel's remote balance must be at least the amount being received. A channel that is nearly empty on the remote side can't receive a large payment. Reserve also reduces usable capacity.
2. **Channel/peer online and confirmed** — the channel must be active and the peer reachable.
3. **Amount vs. capacity** — receiving more than the available inbound capacity will fail regardless of privacy.

The fix is usually more **inbound liquidity** on the existing private channel (e.g. an LSP order, or spending out so the remote side has room to receive) — **not** a public channel.

### Public channels

Public (announced) channels are only for users who want to **run a routing node** and forward other people's payments. They expose the node in the public graph and offer no receiving advantage for a normal user. Most users should never open one.

### DO NOT MIX CHANNELS

- All channels should be either **all private** (default) or **all public** — do not mix. A mix makes the private channels unusable for receiving, because the hub only adds private-channel route hints when there are no public channels.
- Default to private channels unless the user explicitly requests public.

## Invoice Display

Present the LSP invoice as a **single unbroken string** so the user can copy-paste it. If the terminal may wrap long lines, warn the user that they may need to manually remove any spaces introduced by wrapping. Alternatively, offer to display the invoice as a QR code — see [QR Codes](./qrcodes.md).

## Notes

- On Mutinynet (signet), a human must pay the LSP invoice via https://faucet.mutinynet.com — the agent cannot pay it automatically.
- `--amount` is the desired inbound capacity in satoshis.
- `--lsp-type` and `--lsp-identifier` come from the `get-channel-suggestions` output.
- See [Mutinynet](./mutinynet.md) for testing LSP flows without real bitcoin.
