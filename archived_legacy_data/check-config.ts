import { loadConfig, config } from './src/config.ts';

loadConfig();

console.log('BTC_PRIVATE_KEY (length):', config.BTC_PRIVATE_KEY ? config.BTC_PRIVATE_KEY.length : 0);
console.log('ELECTRUM_WALLET_ADDRESS:', config.ELECTRUM_WALLET_ADDRESS);
console.log('BTC_WALLET_ADDRESS:', config.BTC_WALLET_ADDRESS);
console.log('BITCOIN_NETWORK:', config.BITCOIN_NETWORK);
console.log('LIVE_MODE:', config.LIVE_MODE);
