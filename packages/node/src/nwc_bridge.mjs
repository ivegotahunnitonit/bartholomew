#!/usr/bin/env node
/**
 * Bartholomew BTP — Alby Hub NWC CLI Bridge
 * Provides fast JSON-RPC interfacing with self-custodial Alby Hub over Nostr Wallet Connect.
 */

import { NWCClient } from '@getalby/sdk';

const nwcUrl = process.env.ALBY_NWC_URL || process.argv[3];
if (!nwcUrl) {
  console.error(JSON.stringify({ error: "Missing ALBY_NWC_URL" }));
  process.exit(1);
}

const client = new NWCClient({ nostrWalletConnectUrl: nwcUrl });

const action = process.argv[2];

async function main() {
  try {
    switch (action) {
      case 'info': {
        const info = await client.getInfo();
        console.log(JSON.stringify(info));
        break;
      }
      case 'balance': {
        const balance = await client.getBalance();
        console.log(JSON.stringify(balance));
        break;
      }
      case 'invoice': {
        const amountSats = parseInt(process.argv[4] || "1000", 10);
        const desc = process.argv[5] || "Bartholomew AST Audit Fee";
        const inv = await client.makeInvoice({
          amount: amountSats * 1000, // msats
          description: desc
        });
        console.log(JSON.stringify(inv));
        break;
      }
      case 'lookup': {
        const paymentHash = process.argv[4];
        if (!paymentHash) throw new Error("Missing payment hash");
        const res = await client.lookupInvoice({ payment_hash: paymentHash });
        console.log(JSON.stringify(res));
        break;
      }
      default:
        console.error(JSON.stringify({ error: `Unknown action: ${action}` }));
        process.exit(1);
    }
    process.exit(0);
  } catch (err) {
    console.error(JSON.stringify({ error: err.message || String(err) }));
    process.exit(1);
  }
}

main();
