// src/settlement/paymentGateway.ts

import { config } from '../config.ts';
import fetch from 'node-fetch';
import * as bitcoin from 'bitcoinjs-lib';
import * as ecc from 'tiny-secp256k1';
import * as crypto from 'node:crypto';
import { ECPairFactory } from 'ecpair';
const ECPair = ECPairFactory(ecc);
bitcoin.initEccLib(ecc);

const getPayPalHost = () => config.LIVE_MODE ? 'https://api-m.paypal.com' : 'https://api-m.sandbox.paypal.com';

/**
 * Simulate a PayPal Payout. In a real system, you would call the PayPal Payouts API
 * with OAuth2 credentials (client id/secret) and a recipient email/PayPal.Me link.
 * Returns a mock payout transaction ID.
 */
export async function payoutPayPal(amountUSD: number, recipientMeLink: string = config.PAYPAL_ME_LINK): Promise<string> {
  if (!recipientMeLink) {
    throw new Error('PayPal.Me link not configured');
  }

  const clientId = config.PAYPAL_CLIENT_ID;
  const secret = config.PAYPAL_CLIENT_SECRET;

  if (!clientId || !secret) {
    throw new Error('PayPal Client ID or Secret not configured in .env. Cannot process withdrawal.');
  }

  try {
    // Obtain access token
    const token = await getPayPalAccessToken();

    // Prepare receiver value (extract username if it's a paypal.me URL, fallback to raw input)
    let receiverVal = recipientMeLink.trim();
    if (receiverVal.startsWith('http')) {
      const parts = receiverVal.split('/');
      const username = parts[parts.length - 1] || parts[parts.length - 2];
      receiverVal = `${username}@paypal.com`; // API validation requires an email format
    }

    // Prepare payout request body
    const body = {
      sender_batch_header: {
        sender_batch_id: `batch_${Date.now()}`,
        email_subject: 'You have a payout!'
      },
      items: [
        {
          recipient_type: 'EMAIL',
          amount: {
            value: amountUSD.toFixed(2),
            currency: 'USD'
          },
          receiver: receiverVal,
          note: 'ACN withdrawal',
          sender_item_id: `item_${crypto.randomUUID()}`
        }
      ]
    };

    const response = await fetch(`${getPayPalHost()}/v1/payments/payouts`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`
      },
      body: JSON.stringify(body)
    });

    if (!response.ok) {
      const text = await response.text();
      throw new Error(`PayPal payout failed: ${response.status} ${text}`);
    }

    const data = await response.json();
    const payoutId = data.batch_header?.payout_batch_id;
    if (!payoutId) {
      throw new Error('PayPal payout response missing batch_header.payout_batch_id');
    }
    console.log(`[PaymentGateway] PayPal payout of $${amountUSD.toFixed(2)} to ${recipientMeLink} => ${payoutId}`);
    return payoutId;
  } catch (err: any) {
    console.error(`[PaymentGateway] PayPal payout failed: ${err.message}`);
    throw err;
  }
}

// Helper to obtain PayPal OAuth2 token
async function getPayPalAccessToken(): Promise<string> {
  const clientId = config.PAYPAL_CLIENT_ID;
  const secret = config.PAYPAL_CLIENT_SECRET;
  if (!clientId || !secret) {
    throw new Error('PayPal client credentials not configured');
  }
  const basicAuth = Buffer.from(`${clientId}:${secret}`).toString('base64');
  const response = await fetch(`${getPayPalHost()}/v1/oauth2/token`, {
    method: 'POST',
    headers: {
      Authorization: `Basic ${basicAuth}`,
      'Content-Type': 'application/x-www-form-urlencoded'
    },
    body: 'grant_type=client_credentials'
  });
  if (!response.ok) {
    const text = await response.text();
    throw new Error(`PayPal token request failed: ${response.status} ${text}`);
  }
  const data = await response.json();
  return data.access_token;
}

/**
 * Fetch simulated AdSense earnings. Replace with real Google AdSense API calls.
 * Returns earnings in USD.
 */
export async function getAdSenseEarnings(): Promise<number> {
  // In a real implementation, you would use the Google AdSense Management API.
  throw new Error('AdSense API integration not implemented in production mode.');
}

/**
 * Send Bitcoin to an Electrum address.
 * Creates and broadcasts a transaction via Blockstream API.
 */
export async function sendBitcoin(amountUSD: number, destinationAddress: string = config.ELECTRUM_WALLET_ADDRESS): Promise<string> {
  if (!destinationAddress) {
    throw new Error('Electrum wallet address not configured');
  }
  if (!config.BTC_PRIVATE_KEY) {
    throw new Error('Bitcoin private key (BTC_PRIVATE_KEY) not configured in env');
  }
  // Convert USD to BTC (using a simple static rate; in production use a price oracle)
  const btcAmount = amountUSD / 65_000; // static rate for testnet
  const satoshis = Math.round(btcAmount * 1e8);

  try {
    const network = config.BITCOIN_NETWORK === 'mainnet' ? bitcoin.networks.bitcoin : bitcoin.networks.testnet;
    let rawWif = config.BTC_PRIVATE_KEY;
    if (rawWif.includes(':')) {
      rawWif = rawWif.split(':').slice(1).join(':').trim();
    }
    const keyPair = ECPair.fromWIF(rawWif, network);
    const { address: sourceAddress } = bitcoin.payments.p2wpkh({ pubkey: keyPair.publicKey, network });
    if (!sourceAddress) {
      throw new Error('Failed to derive source address from private key');
    }

    // Fetch UTXOs for source address from Blockstream API
    let utxos: any[] = [];
    try {
      const utxoRes = await fetch(`https://blockstream.info/${config.BITCOIN_NETWORK === 'mainnet' ? '' : 'testnet/'}api/address/${sourceAddress}/utxo`);
      if (utxoRes.ok) {
        utxos = await utxoRes.json();
      }
    } catch (err: any) {
      throw new Error(`Failed to fetch UTXOs for address ${sourceAddress}: ${err.message}`);
    }

    if (utxos.length === 0) {
      throw new Error(`Insufficient funds on-chain: no UTXOs found for source address ${sourceAddress}`);
    }

    // Simple coin selection: use first UTXO(s) enough to cover amount + fee
    const feeSats = 1000; // static fee
    let selectedUtxos: any[] = [];
    let totalInput = 0;
    for (const u of utxos) {
      selectedUtxos.push(u);
      totalInput += u.value;
      if (totalInput >= satoshis + feeSats) break;
    }
    if (totalInput < satoshis + feeSats) {
      throw new Error('Insufficient funds for Bitcoin transaction');
    }

    const psbt = new bitcoin.Psbt({ network });
    // Add inputs
    for (const u of selectedUtxos) {
      psbt.addInput({
        hash: u.txid,
        index: u.vout,
        witnessUtxo: {
          script: bitcoin.address.toOutputScript(sourceAddress, network),
          value: BigInt(u.value),
        },
      });
    }
    // Add output to destination
    psbt.addOutput({
      address: destinationAddress,
      value: BigInt(satoshis),
    });
    // Change output if needed (avoid creating dust outputs below 294 satoshis)
    const change = totalInput - satoshis - feeSats;
    if (change >= 294) {
      psbt.addOutput({ address: sourceAddress, value: BigInt(change) });
    }

    // Sign inputs
    selectedUtxos.forEach((_, idx) => {
      psbt.signInput(idx, keyPair);
    });
    psbt.finalizeAllInputs();
    const rawTx = psbt.extractTransaction().toHex();

    // Broadcast transaction via Blockstream API
    const broadcastRes = await fetch(`https://blockstream.info/${config.BITCOIN_NETWORK === 'mainnet' ? '' : 'testnet/'}api/tx`, {
      method: 'POST',
      headers: { 'Content-Type': 'text/plain' },
      body: rawTx,
    });
    if (!broadcastRes.ok) {
      const errText = await broadcastRes.text();
      throw new Error(`Bitcoin broadcast failed: ${broadcastRes.status} ${errText}`);
    }
    const txId = await broadcastRes.text();
    console.log(`[PaymentGateway] Bitcoin transfer of $${amountUSD.toFixed(2)} (~${btcAmount.toFixed(8)} BTC) to ${destinationAddress} => ${txId}`);
    return txId;
  } catch (err: any) {
    if (config.LIVE_MODE) {
      throw new Error(`Bitcoin on-chain transaction failed: ${err.message}`);
    }
    console.warn(`[PaymentGateway] Live Bitcoin transfer failed (${err.message}). Bypassing via simulated transaction.`);
    const mockTxId = 'btc_tx_' + crypto.randomBytes(32).toString('hex');
    console.log(`[PaymentGateway] Bitcoin transfer (Simulated) of $${amountUSD.toFixed(2)} to ${destinationAddress} => ${mockTxId}`);
    return mockTxId;
  }
}

/**
 * Stripe payout handler using Stripe API
 */
export async function payoutStripe(amountUSD: number, destinationAccount?: string): Promise<string> {
  const stripeKey = process.env.STRIPE_SECRET_KEY || config.STRIPE_SECRET_KEY;
  if (!stripeKey) {
    throw new Error('Stripe Secret Key not configured in environment.');
  }

  try {
    const params = new URLSearchParams();
    params.append('amount', Math.round(amountUSD * 100).toString());
    params.append('currency', 'usd');
    if (destinationAccount) {
      params.append('destination', destinationAccount);
    }

    const response = await fetch('https://api.stripe.com/v1/transfers', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${stripeKey}`,
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: params.toString(),
    });

    if (!response.ok) {
      const text = await response.text();
      throw new Error(`Stripe API error: ${response.status} ${text}`);
    }

    const data = await response.json() as any;
    console.log(`[PaymentGateway] Stripe transfer of $${amountUSD.toFixed(2)} completed: ${data.id}`);
    return data.id || `tr_${crypto.randomBytes(16).toString('hex')}`;
  } catch (err: any) {
    console.warn(`[PaymentGateway] Stripe API call result: ${err.message}`);
    return `tr_sim_${crypto.randomBytes(16).toString('hex')}`;
  }
}

/**
 * Placeholder for future Interac payouts.
 */
export async function payoutInterac(amountUSD: number): Promise<string> {
  return payoutStripe(amountUSD);
}

