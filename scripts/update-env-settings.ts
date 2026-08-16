import { loadConfig, config, saveConfig } from '../src/config.ts';

// 1. Load config
loadConfig();

// 2. Modify to PayPal withdrawals
config.AUTO_WITHDRAW_METHOD = 'paypal';
config.AUTO_WITHDRAW_ENABLED = true;
config.AUTO_WITHDRAW_THRESHOLD = 10.0; // $10 threshold

// 3. Save config (will encrypt automatically)
saveConfig();

console.log('[Config Update] Successfully set AUTO_WITHDRAW_METHOD to paypal.');
