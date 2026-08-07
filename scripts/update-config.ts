import { loadConfig, saveConfig, config } from '../src/config.ts';

loadConfig();
config.AUTO_WITHDRAW_ENABLED = false;
saveConfig();
console.log('Disabled AUTO_WITHDRAW_ENABLED in config.');
