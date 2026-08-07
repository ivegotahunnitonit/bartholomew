import { loadConfig, config } from '../src/config.ts';
import { PaymentManager } from '../src/settlement/PaymentManager.ts';

// Load configuration first
loadConfig();

// Optional: override Electrum address via command‑line argument
const addressArg = process.argv[2];
if (addressArg) {
  config.ELECTRUM_WALLET_ADDRESS = addressArg;
  console.log(`[fundElectrum] Overriding Electrum address to ${addressArg}`);
}

await PaymentManager.withdrawToElectrum(150);
process.exit(0);
