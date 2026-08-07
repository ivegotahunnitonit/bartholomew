import { loadConfig, config } from './src/config.ts';
import * as bitcoin from 'bitcoinjs-lib';
import * as ecc from 'tiny-secp256k1';
import { ECPairFactory } from 'ecpair';
import fetch from 'node-fetch';

const ECPair = ECPairFactory(ecc);
bitcoin.initEccLib(ecc);

async function checkBalance() {
  loadConfig();
  const network = config.BITCOIN_NETWORK === 'mainnet' ? bitcoin.networks.bitcoin : bitcoin.networks.testnet;
  let rawWif = config.BTC_PRIVATE_KEY;
  if (rawWif.includes(':')) {
    rawWif = rawWif.split(':').slice(1).join(':').trim();
  }
  const keyPair = ECPair.fromWIF(rawWif, network);
  const { address } = bitcoin.payments.p2wpkh({ pubkey: keyPair.publicKey, network });
  
  console.log(`Source Address: ${address}`);
  
  const utxoRes = await fetch(`https://blockstream.info/${config.BITCOIN_NETWORK === 'mainnet' ? '' : 'testnet/'}api/address/${address}/utxo`);
  if (!utxoRes.ok) throw new Error('Failed to fetch UTXOs');
  
  const utxos = await utxoRes.json();
  const totalSats = utxos.reduce((sum: number, u: any) => sum + u.value, 0);
  console.log(`Available Balance: ${totalSats} satoshis (~$${(totalSats / 1e8 * 65000).toFixed(2)} USD)`);
}

checkBalance();
