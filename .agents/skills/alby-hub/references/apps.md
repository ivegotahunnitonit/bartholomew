# Apps

Commands for managing NWC (Nostr Wallet Connect) app connections. NWC apps allow external applications to interact with the hub's wallet.

## Commands

```bash
# List NWC app connections
npx -y @getalby/hub-cli@0.6.0 list-apps

# Look up a single app by name (prefix match) — the response includes its balance
npx -y @getalby/hub-cli@0.6.0 list-apps --name "My App"

# Create a new NWC connection with default permissions
npx -y @getalby/hub-cli@0.6.0 create-app --name "My App"

# Create with custom scopes and a spending budget
npx -y @getalby/hub-cli@0.6.0 create-app --name "My App" \
  --scopes "pay_invoice,get_balance" \
  --max-amount 10000 \
  --budget-renewal monthly

# Create an isolated app (separate balance, but not a full sub-wallet — see Sub-wallets)
npx -y @getalby/hub-cli@0.6.0 create-app --name "Isolated App" --isolated --unlock-password YOUR_PASSWORD
```

> **Creating a sub-wallet?** Prefer the dedicated `create-sub-wallet` command — it applies the same defaults the Alby Hub web UI uses and supports funding, lightning addresses, and paying from the sub-wallet. See [Sub-wallets](./sub-wallets.md).

## App Balance vs. Wallet Balance

There are **two different balances** — do not confuse them:

- **Hub wallet balance** — the node's spendable lightning + on-chain funds, shared by all non-isolated apps. Get it with `get-balances`. See [Payments](./payments.md).
- **App balance** — the isolated balance held by a single **isolated app** or **sub-wallet**. Non-isolated (shared-balance) apps spend directly from the hub wallet and have no balance of their own (their `balanceSat` is `0`).

When a user asks for **"the balance of `<app name>`"**, they mean the app balance — **not** the hub wallet balance. Fetch the app by name and read its `balanceSat`:

```bash
# The response's `apps` array contains the matching app(s); read `balanceSat` from it
npx -y @getalby/hub-cli@0.6.0 list-apps --name "Alice"
```

- `balanceSat` (satoshis) is the app/sub-wallet balance. `balanceMsat` is the same value in millisatoshis; the legacy `balance` field is millisatoshis and deprecated — prefer `balanceSat`.
- `--name` is a **prefix** match and may return more than one app. Confirm the exact `name` field in the results before reporting a balance.
- If no app matches, `apps` is empty — tell the user no app by that name exists. Do **not** fall back to reporting the hub wallet balance as if it were the app's.
- For a shared (non-isolated) app, `balanceSat` is `0`; if the user wants the funds that app can spend, that is the hub wallet balance (`get-balances`).

## After Creating an App

After `create-app` succeeds, offer to display the `nostrWalletConnectUrl` (NWC connection string) as a QR code for easy scanning. See [QR Codes](./qrcodes.md).

> **IMPORTANT — connection secrets are sensitive.** The `nostrWalletConnectUrl` grants wallet access. Hand it to the user who requested the app and nowhere else — do not print it to logs, send it to any third party or external service, or echo it into unrelated output. Every part — pubkey, secret, relay — is sensitive. See [Security](../SKILL.md#security).

## Notes

- `create-app` returns a `nostrWalletConnectUrl` (NWC connection string) that the external app uses to connect.
- Isolated apps and sub-wallets have their own balance, separate from the main hub wallet — see [App Balance vs. Wallet Balance](#app-balance-vs-wallet-balance) above.
- `--budget-renewal` accepts: `daily`, `weekly`, `monthly`, `yearly`, `never`.
- Available scopes include: `pay_invoice`, `get_balance`, `get_info`, `make_invoice`, `lookup_invoice`, `list_transactions`, `sign_message`.
