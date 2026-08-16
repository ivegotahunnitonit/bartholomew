import { loadConfig, config } from './src/config.ts';
import { sendBitcoin } from './src/settlement/paymentGateway.ts';

async function run() {
  loadConfig();
  console.log(`Starting real transaction of $500 to ${config.ELECTRUM_WALLET_ADDRESS}`);
  try {
    const txId = await sendBitcoin(500, config.ELECTRUM_WALLET_ADDRESS);
    console.log(`Success! Transaction ID: ${txId}`);
  } catch (err: any) {
    console.error(`Error: ${err.message}`);
  }
}

run();
