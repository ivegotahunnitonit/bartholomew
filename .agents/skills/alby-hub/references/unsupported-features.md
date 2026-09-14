# Unsupported Features

The hub CLI is experimental and incomplete. The following features are **not** available via the CLI. If a user asks for any of these, direct them to use the Alby Hub web interface instead.

## Bitcoin & liquidity

- Auto-swaps
- Buy bitcoin
- Pay for a channel with stablecoin / crypto

## Node & wallet management

- Set node alias
- Sign messages (sign message)
- Enable dynamic channels backup
- Create migration file
- View routing stats

## Apps & connections

- View recently used apps
- Schedule recurring payments (ZapPlanner)
- Delete app connections / sub-wallets
- Convert an existing isolated app into a sub-wallet (only available in the hub UI)
- The sub-wallet overview — viewing sub-wallets as a distinct group and checking whether the hub's lightning balance covers the total funds held across all sub-wallets (only available in the hub UI)
- Create a hub developer API key
- App store — discover NWC apps
- Learn about AI integrations

## Alby account

- Change or unlink Alby account
- Manage getalby.com account, including:
  - Setting a custom lightning address for the **primary account** (the default account lightning address can be linked to this hub via `link-alby-account` — see [Alby Account](./alby-account.md)). Note: setting a lightning address for a **sub-wallet** _is_ supported — see [Sub-wallets](./sub-wallets.md)
  - Purchasing a subscription
  - Nostr NIP-05
  - Email notification settings
- Earn by referring users
