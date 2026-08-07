import * as bitcoin from 'bitcoinjs-lib';
import * as process from 'process';

// Usage: node compute_address.ts <pubkey_hex> [network]
const args = process.argv.slice(2);
const pubKeyHex = args[0] || '024b84f2f3414280348630c033b1a9607318b376dead5ef9f41b790c87e572fef9';
const net = args[1] && args[1].toLowerCase() === 'mainnet' ? bitcoin.networks.bitcoin : bitcoin.networks.testnet;

const pubKeyBuffer = Buffer.from(pubKeyHex, 'hex');

const { address } = bitcoin.payments.p2wpkh({ pubkey: pubKeyBuffer, network: net });
if (!address) {
  console.error('Failed to generate address');
  process.exit(1);
}
console.log(address);
