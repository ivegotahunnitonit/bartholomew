# Alby Account

Connecting an Alby account to your hub unlocks several benefits:

- **Lightning Address** — A personalized lightning address (e.g. `you@getalby.com`) to receive payments. Requires **linking** the account to this hub (see below) so the address routes here.
- **Email Notifications** — Notifications about incoming transactions and more. Enabled automatically when you connect — nothing to set up.
- **Encrypted Backups** — Automatic encrypted static channel backups saved to your Alby account, so you can always recover your funds. Happens automatically once connected — nothing to set up.
- **Support** — Human support via live chat when you need a helping hand.
- **Fiat Top-ups** — Top up with fiat and get bitcoin delivered to your Alby Hub.

> **Connect vs. link.** _Connecting_ (OAuth) authenticates the hub with the Alby account — this alone turns on encrypted backups and email notifications, with no further action. _Linking_ is a separate step that gives the alby account a budgeted NWC connection to this hub, allowing it to points your lightning address at **this** hub so it can generate invoices here.

## Connecting Your Alby Account

Connecting requires two steps:

**Step 1** — Get the authorization URL:

```bash
npx -y @getalby/hub-cli@0.6.0 connect-alby-account
```

This returns a JSON object with an `albyAuthUrl`. Tell the user to open that URL in their browser, sign in to their Alby account, and copy the authorization code they receive.

**Step 2** — Submit the authorization code:

```bash
npx -y @getalby/hub-cli@0.6.0 connect-alby-account --code <code>
```

On success, returns `{ "success": true }`. If the account is already connected, step 1 returns `{ "albyAccountConnected": true, "albyUserIdentifier": "..." }` instead of a URL.

Once connected, encrypted backups and email notifications are active automatically — there is nothing further to enable.

## Checking the Connected Account

To see the connected account's details — including the lightning address, email, name, and subscription:

```bash
npx -y @getalby/hub-cli@0.6.0 get-alby-account
```

Returns the account, e.g. `lightning_address`, `email`, `name`, `keysend_pubkey`, `shared_node`, and `subscription`. Use this to answer "what is my lightning address?". This requires the account to be connected first.

> If `lightning_address` is present but `keysend_pubkey` does not match this hub's node pubkey (or `shared_node` is `true`), the address is **not yet routing to this hub** — link the account (below).

## Linking Your Lightning Address to This Hub

To make your lightning address receive payments on **this** hub, link the account. This creates a budgeted NWC connection on getalby.com that forwards to your hub. The node must be started/unlocked.

```bash
npx -y @getalby/hub-cli@0.6.0 link-alby-account
```

Options (both optional):

- `--budget <sats>` — budget in sats for the Alby account connection (default `25000`).
- `--renewal <period>` — budget renewal period: `daily`, `weekly`, `monthly`, `yearly`, `never` (default `weekly`).

On success, returns `{ "success": true }`. After linking, `get-alby-account` will show `keysend_pubkey` matching this hub.

## Alby Service Status

To check Alby's service status — latest hub version, health, and any incidents:

```bash
npx -y @getalby/hub-cli@0.6.0 get-alby-status
```

Returns `hub.latestVersion`, `status`, `healthy`, `accountAvailable`, and any `incidents`. This does not require a connected account.
