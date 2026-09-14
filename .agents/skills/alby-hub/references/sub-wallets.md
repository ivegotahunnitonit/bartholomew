# Sub-wallets

A **sub-wallet** holds **its own balance**, separate from the main hub wallet and from every other sub-wallet. One Alby Hub can host many sub-wallets — one per person, team, or purpose — while a single set of lightning channels backs them all. This is how a hub operator gives others a self-custodial-feeling wallet without each needing to run their own node.

A sub-wallet is a **superset of an isolated app**: it builds on an isolated NWC connection but adds capabilities a plain isolated app does not have — notably its own **lightning address**, and the hub UI surfaces sub-wallets separately (e.g. showing whether the hub's lightning balance covers the total funds held across all sub-wallets). A sub-wallet is created via `create-sub-wallet`, which is distinct from a plain `create-app` connection (which spends from the shared hub balance) and from a bare `create-app --isolated` app — `create-sub-wallet` applies the same defaults the Alby Hub web UI uses for sub-wallets.

## Create a sub-wallet

```bash
# Create a sub-wallet with default sub-wallet scopes
npx -y @getalby/hub-cli@0.6.0 create-sub-wallet --name "Alice"

# With a spending budget
npx -y @getalby/hub-cli@0.6.0 create-sub-wallet --name "Alice" \
  --max-amount 50000 \
  --budget-renewal monthly
```

- Returns a `nostrWalletConnectUrl` (NWC connection string) and an `id`. The `id` is the sub-wallet's app id — you need it for `transfer`, `create-sub-wallet-lightning-address`, and `pay-invoice --from-app-id`.
- Default scopes: `get_balance`, `get_info`, `list_transactions`, `lookup_invoice`, `make_invoice`, `notifications`, `pay_invoice`. Override with `--scopes`.
- `--budget-renewal` accepts: `daily`, `weekly`, `monthly`, `yearly`, `never`. With no `--max-amount` there is no spending limit.

> **IMPORTANT — connection secrets are sensitive.** The `nostrWalletConnectUrl` grants wallet access. Hand it to the user who owns the sub-wallet and nowhere else — offer to render it as a QR code (see [QR Codes](./qrcodes.md)). Do not print it to logs or share any part of it. See [Security](../SKILL.md#security).

## List sub-wallets

```bash
# List only sub-wallets, with their balances
npx -y @getalby/hub-cli@0.6.0 list-apps --sub-wallets

# Look up one sub-wallet by name to read its balance
npx -y @getalby/hub-cli@0.6.0 list-apps --name "Alice"
```

Each sub-wallet's own balance is the `balanceSat` field. This is **not** the hub wallet balance — see [App Balance vs. Wallet Balance](./apps.md#app-balance-vs-wallet-balance).

## Transfer funds to/from a sub-wallet

`transfer` moves funds internally — between the main hub wallet and a sub-wallet, or directly between two sub-wallets — with no on-chain or routed lightning payment and no fee. `--amount` is in **satoshis**.

```bash
# Fund a sub-wallet from the main hub wallet (omit --from-app-id)
npx -y @getalby/hub-cli@0.6.0 transfer --to-app-id 3 --amount 10000

# Withdraw from a sub-wallet back to the main hub wallet (omit --to-app-id)
npx -y @getalby/hub-cli@0.6.0 transfer --from-app-id 3 --amount 5000

# Move funds directly between two sub-wallets
npx -y @getalby/hub-cli@0.6.0 transfer --from-app-id 3 --to-app-id 4 --amount 2000
```

- Specify at least one of `--from-app-id` / `--to-app-id`. Omitting one end means the main hub wallet.
- Any app id you pass must be an **isolated** app/sub-wallet — transferring to or from a shared (non-isolated) app fails with `app is not isolated`.
- Funding a sub-wallet requires enough spendable balance in the source (the hub wallet needs lightning balance — see [Payments](./payments.md)).

## Lightning address for a sub-wallet

Give a sub-wallet its own lightning address so it can be paid by anyone. **Requires a connected Alby account** (the address is provisioned through getalby.com) — connect one first with `connect-alby-account` (see [Alby Account](./alby-account.md)); without it the command fails.

```bash
# Assign alice@getalby.com to sub-wallet id 3 (pass only the handle before the @)
npx -y @getalby/hub-cli@0.6.0 create-sub-wallet-lightning-address --app-id 3 --address alice

# Remove the lightning address
npx -y @getalby/hub-cli@0.6.0 delete-sub-wallet-lightning-address --app-id 3
```

Once set, the full address is stored on the sub-wallet and shows up as `lud16` in that app's `metadata` (visible via `list-apps`).

## Pay from a sub-wallet

By default `pay-invoice` spends from the main hub wallet. Pass `--from-app-id` to debit a specific sub-wallet instead:

```bash
npx -y @getalby/hub-cli@0.6.0 pay-invoice lnbc... --from-app-id 3
```

See [Payments](./payments.md) for invoice payment details.

## Notes

- Deleting a sub-wallet (the app connection itself) is **not** supported via the CLI — see [Unsupported Features](./unsupported-features.md).
- For plain NWC app connections — both shared-balance and bare isolated apps — see [Apps](./apps.md).
