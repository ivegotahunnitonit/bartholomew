import { loadConfig, config } from './src/config.ts';
import * as bitcoin from 'bitcoinjs-lib';
import * as ecc from 'tiny-secp256k1';
import { ECPairFactory } from 'ecpair';
import fetch from 'node-fetch';

const ECPair = ECPairFactory(ecc);
bitcoin.initEccLib(ecc);

async function sendMaxFunds() {
  loadConfig();
  const network = config.BITCOIN_NETWORK === 'mainnet' ? bitcoin.networks.bitcoin : bitcoin.networks.testnet;
  let rawWif = config.BTC_PRIVATE_KEY;
  if (rawWif.includes(':')) {
    rawWif = rawWif.split(':').slice(1).join(':').trim();
  }
  const keyPair = ECPair.fromWIF(rawWif, network);
  const { address } = bitcoin.payments.p2wpkh({ pubkey: keyPair.publicKey, network });

  const destinationAddress = config.ELECTRUM_WALLET_ADDRESS;
  console.log(`Source Address: ${address}`);
  console.log(`Destination Address: ${destinationAddress}`);

  const utxoRes = await fetch(`https://blockstream.info/${config.BITCOIN_NETWORK === 'mainnet' ? '' : 'testnet/'}api/address/${address}/utxo`);
  if (!utxoRes.ok) throw new Error('Failed to fetch UTXOs');

  const utxos = await utxoRes.json();
  const totalSats = utxos.reduce((sum: number, u: any) => sum + u.value, 0);

  if (totalSats === 0) {
    console.log('No funds available.');
    return;
  }

  const feeSats = 1000;
  const sendAmount = totalSats - feeSats;

  if (sendAmount <= 0) {
    console.log('Insufficient funds to cover network fees.');
    return;
  }

  console.log(`Sending ${sendAmount} satoshis (~$${(sendAmount / 1e8 * 65000).toFixed(2)} USD)...`);

  const psbt = new bitcoin.Psbt({ network });
  for (const u of utxos) {
    psbt.addInput({
      hash: u.txid,
      index: u.vout,
      witnessUtxo: {
        script: bitcoin.address.toOutputScript(address!, network),
        value: BigInt(u.value),
      },
    });
  }

  psbt.addOutput({
    address: destinationAddress,
    value: BigInt(sendAmount),
  });

  utxos.forEach((_, idx) => {
    psbt.signInput(idx, keyPair);
  });
  psbt.finalizeAllInputs();
  const rawTx = psbt.extractTransaction().toHex();

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
  console.log(`Success! Transaction ID: ${txId}`);
}

sendMaxFunds().catch(e => console.error(e));
