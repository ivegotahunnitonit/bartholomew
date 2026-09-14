# Swaps

Swap between **on-chain bitcoin** and **lightning**, powered by [boltz.exchange](https://boltz.exchange):

- **Swap in** — on-chain bitcoin → lightning balance.
- **Swap out** — lightning balance → on-chain bitcoin (the hub's own on-chain wallet, or an external address).

Swaps are **bitcoin ↔ bitcoin**. The only "other cryptocurrency" path is via FixedFloat (see the end of this page).

## ⚠️ Fund safety — confirm before every swap

A swap moves real funds and **cannot be undone**. Before running any swap command, **always confirm with the user in plain language**:

1. **The direction** (in or out) and **the amount** in **satoshis** (sats).
2. **For swap out:** the destination — the hub's own on-chain wallet, or an **external on-chain address**. If external, **read the full address back to the user and get explicit confirmation** — a wrong address means irreversible loss of funds, and the address is not validated for you. Payment will be initiated immediately and cannot be reversed.
3. **For swap in:** how it will be funded — from the **hub's on-chain wallet** or an **external wallet** (see the flow below).
4. **That fees apply** (see below).

Only run the command once the user has confirmed. Never guess the amount or an address.

## Swap in (on-chain → lightning)

This is a **two-step** flow:

1. **Generate the swap** with `swap-in --amount <sats>`. This returns the swap details, including:
   - `lockupAddress` — the on-chain bitcoin address to deposit to.
   - `sendAmountSat` — the **exact** on-chain amount to deposit (this is higher than the requested amount; it includes the boltz fees).
   - `id` — the swap ID, and `state` (starts as `PENDING`).

   **Show the user the deposit address and the exact amount.** You can display it as a QR code (`bitcoin:<lockupAddress>?amount=<amountInBTC>`, where `amountInBTC = sendAmountSat / 100000000`) — see [QR Codes](./qrcodes.md).

2. **Fund the deposit.** Send exactly `sendAmountSat` to `lockupAddress` from any on-chain wallet — the user's external wallet, or the hub's own on-chain balance. The user sends the shown amount to the shown address themselves; there is no swap-specific CLI step for this. You can offer to pay with the hub's on-chain funds, but the human should confirm before any action is taken.

Once the deposit confirms on-chain, boltz pays the hub's lightning invoice and the swap reaches `SUCCESS`. Track progress with `lookup-swap <id>`.

```bash
# 1. Generate a swap to receive 100,000 sats on lightning
npx -y @getalby/hub-cli@0.6.0 swap-in --amount 100000

# 2. Send the shown sendAmountSat to the shown lockupAddress from any on-chain wallet
```

## Swap out (lightning → on-chain)

`swap-out` spends from the hub's lightning balance and pays the boltz invoice automatically, then claims the on-chain funds to the destination — there is no second step.

```bash
# Swap lightning out into the hub's own on-chain wallet (amount received on-chain, in sats)
npx -y @getalby/hub-cli@0.6.0 swap-out --amount 100000

# Swap lightning out to an external on-chain address
npx -y @getalby/hub-cli@0.6.0 swap-out --amount 100000 --destination bc1...
```

- `--amount` is the amount **received on-chain**, in **sats**. boltz adds its fees on top, so the lightning amount actually spent (`sendAmountSat`) is higher.
- Omitting `--destination` swaps into the hub's own on-chain wallet; providing it sends to an external on-chain address.

## Checking a swap

```bash
# Look up a swap by its swap ID (state is PENDING, SUCCESS, FAILED or REFUNDED)
npx -y @getalby/hub-cli@0.6.0 lookup-swap <swapId>
```

## Before swapping

- Check balances first with `get-balances`. Swap **out** needs enough **lightning** spendable balance (amount + fees); swap **in** funded from the hub needs enough **on-chain** spendable balance (`sendAmountSat` + on-chain fees).
- Fees are `albyServiceFee% + boltzServiceFee% + on-chain fees`. boltz also enforces minimum and maximum swap amounts; an out-of-range amount is rejected with an error message.

## Swap to/from another cryptocurrency

To swap into or out of a **different cryptocurrency** (e.g. an external ETH/USDT address), there is no boltz swap — it goes through [FixedFloat](https://ff.io):

- **Out to another coin:** send the user `https://ff.io/?from=BTCLN&ref=qnnjvywb`. They choose the target coin and address; FixedFloat returns a **lightning invoice**; pay it from the hub with `pay-invoice` (see [Payments](./payments.md)) after confirming the amount.
- **In from another coin:** create a lightning invoice with `make-invoice`, then send the user `https://ff.io/?to=BTCLN&address=<invoice>&ref=qnnjvywb` to pay it with their other cryptocurrency.

## Notes

- All swap amounts are in **sats**, not millisats (unlike `pay-invoice` / `make-invoice`).
- If a swap shows `FAILED`, advise the user that locked-up funds can be recovered via the **Swap Refund** tool in the Alby Hub web interface (Settings → Debug Tools). CLI refunds are not yet supported.
