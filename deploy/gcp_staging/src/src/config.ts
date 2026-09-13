import * as fs from 'node:fs';
import * as path from 'node:path';
import * as crypto from 'node:crypto';
import { fileURLToPath } from 'node:url';
import process from 'node:process';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const ENV_PATH = path.resolve(process.cwd(), '.env');

const ENCRYPTION_PASSPHRASE = process.env.ACN_DECRYPT_KEY || 'solomonletishitsubeyuel';

function encryptEnv(text: string): string {
  const iv = crypto.randomBytes(16);
  const hashedKey = crypto.createHash('sha256').update(ENCRYPTION_PASSPHRASE).digest();
  const cipher = crypto.createCipheriv('aes-256-cbc', hashedKey, iv);
  let encrypted = cipher.update(text, 'utf8');
  encrypted = Buffer.concat([encrypted, cipher.final()]);
  return 'ACNENC:' + iv.toString('hex') + ':' + encrypted.toString('hex');
}

function decryptEnv(ciphertext: string): string {
  try {
    if (!ciphertext.startsWith('ACNENC:')) {
      return ciphertext; // fallback if already plain text (will be encrypted on save)
    }
    const parts = ciphertext.substring(7).split(':');
    const iv = Buffer.from(parts[0], 'hex');
    const encryptedText = Buffer.from(parts[1], 'hex');
    const hashedKey = crypto.createHash('sha256').update(ENCRYPTION_PASSPHRASE).digest();
    const decipher = crypto.createDecipheriv('aes-256-cbc', hashedKey, iv);
    let decrypted = decipher.update(encryptedText);
    decrypted = Buffer.concat([decrypted, decipher.final()]);
    return decrypted.toString('utf8');
  } catch (err: any) {
    throw new Error(`Failed to decrypt configuration file: ${err.message}. Please verify the ACN_DECRYPT_KEY or secret passphrase.`);
  }
}

// Default Configuration values
export interface AppConfig {
  NODE_ID: string;
  PORT: number;
  LAT: number;
  LNG: number;
  MAX_RADIUS_KM: number;
  FEE_RATE: number;
  BOOTSTRAP_PEERS: string[];
  WALLET_ADDRESS: string;
  AUTO_ACCEPT_ENABLED: boolean;
  AUTO_ACCEPT_THRESHOLD: number;
  SOLANA_WALLET_ADDRESS: string;
  BASE_WALLET_ADDRESS: string;
  BTC_WALLET_ADDRESS: string;
  ELECTRUM_WALLET_ADDRESS: string; // Electrum address for BTC withdrawals
  INTAKE_MODE: 'autonomous' | 'balanced' | 'hybrid';
  OWNER_ID: string; // custom owner identifier
  PAYPAL_ME_LINK: string; // PayPal.Me link for withdrawals
  PAYPAL_CLIENT_ID: string; // PayPal API client ID
  PAYPAL_CLIENT_SECRET: string; // PayPal API client secret
  STRIPE_SECRET_KEY: string; // Stripe secret key for Interac payouts
  BTC_PRIVATE_KEY: string; // WIF or hex private key for Bitcoin signing
  BITCOIN_NETWORK: 'testnet' | 'mainnet'; // Network selection
  ADSENSE_CLIENT_ID?: string;
  ADSENSE_AD_UNIT_ID?: string;
  ADSENSE_AD_SLOT?: string;
  AD_REVENUE_THRESHOLD?: number;
  AUTO_SETTLE_ON_MATCH: boolean;
  LIVE_MODE: boolean;
  AUTO_WITHDRAW_ENABLED: boolean;
  AUTO_WITHDRAW_METHOD: 'paypal' | 'electrum';
  AUTO_WITHDRAW_THRESHOLD: number;
  ACN_NETWORK_SECRET: string;
  MIN_PEERS_TARGET: number;
  MAX_PEERS_TARGET: number;
  SUPER_NODE_MODE: boolean;
}

export let config: AppConfig = {
  NODE_ID: '',
  PORT: 8080,
  LAT: 40.7128,  // Default to NYC coordinates (fallback)
  LNG: -74.0060,
  MAX_RADIUS_KM: 50.0,
  FEE_RATE: 0.02, // 2% coordination fee
  BOOTSTRAP_PEERS: [],
  WALLET_ADDRESS: '',
  AUTO_ACCEPT_ENABLED: true,
  AUTO_ACCEPT_THRESHOLD: 1.0,
  SOLANA_WALLET_ADDRESS: '',
  BASE_WALLET_ADDRESS: '',
  BTC_WALLET_ADDRESS: '',
  ELECTRUM_WALLET_ADDRESS: '',
  INTAKE_MODE: 'hybrid',
  OWNER_ID: '',
  PAYPAL_ME_LINK: '',
  PAYPAL_CLIENT_ID: '',
  PAYPAL_CLIENT_SECRET: '',
  STRIPE_SECRET_KEY: process.env.STRIPE_SECRET_KEY || 'YOUR_STRIPE_SECRET_KEY_HERE',
  BTC_PRIVATE_KEY: '',
  BITCOIN_NETWORK: 'testnet',
  AUTO_SETTLE_ON_MATCH: true,
  LIVE_MODE: true,
  AUTO_WITHDRAW_ENABLED: true,
  AUTO_WITHDRAW_METHOD: 'electrum',
  AUTO_WITHDRAW_THRESHOLD: 0.05,
  ACN_NETWORK_SECRET: 'solomonletishitsubeyuel',
  MIN_PEERS_TARGET: 50,
  MAX_PEERS_TARGET: 100,
  SUPER_NODE_MODE: true
};

/**
 * Loads configuration from .env, generating a Node ID and file if none exists.
 */
export function loadConfig() {
  let envContent = '';
  let isEncryptedFile = false;
  if (fs.existsSync(ENV_PATH)) {
    const rawContent = fs.readFileSync(ENV_PATH, 'utf8');
    if (rawContent.startsWith('ACNENC:')) {
      envContent = decryptEnv(rawContent);
      isEncryptedFile = true;
    } else {
      envContent = rawContent;
    }
  }

  const parsedEnv: Record<string, string> = {};
  envContent.split('\n').forEach((line) => {
    const trimmed = line.trim();
    if (trimmed && !trimmed.startsWith('#')) {
      const parts = trimmed.split('=');
      const key = parts[0].trim();
      const val = parts.slice(1).join('=').trim();
      parsedEnv[key] = val;
    }
  });

  // Verify or generate NODE_ID
  if (!parsedEnv.NODE_ID) {
    parsedEnv.NODE_ID = crypto.randomUUID();
    console.log(`[Config] Generated new Node ID: ${parsedEnv.NODE_ID}`);
  }

  // Combine parsed file variables with active process.env (so CLI environment variables override .env files)
  const envSource = { ...parsedEnv, ...process.env };

  // Set default values if missing
  config.NODE_ID = envSource.NODE_ID || crypto.randomUUID();
  config.PORT = envSource.API_PORT ? parseInt(envSource.API_PORT, 10) : (envSource.PORT ? parseInt(envSource.PORT, 10) : 8080);
  config.LAT = envSource.LAT ? parseFloat(envSource.LAT) : 40.7128;
  config.LNG = envSource.LNG ? parseFloat(envSource.LNG) : -74.0060;
  config.MAX_RADIUS_KM = envSource.MAX_RADIUS_KM ? parseFloat(envSource.MAX_RADIUS_KM) : 50.0;
  config.FEE_RATE = envSource.FEE_RATE ? parseFloat(envSource.FEE_RATE) : 0.02;
  config.BOOTSTRAP_PEERS = envSource.BOOTSTRAP_PEERS
    ? envSource.BOOTSTRAP_PEERS.split(',').map(p => p.trim()).filter(Boolean)
    : [];

  // Generate a stable wallet address if not yet stored
  // Simulates a Lightning/bech32 node wallet address derived from the Node ID
  if (!envSource.WALLET_ADDRESS) {
    const walletSeed = config.NODE_ID.replace(/-/g, '').substring(0, 20);
    envSource.WALLET_ADDRESS = `lnbc1acn${walletSeed}wallet`;
    console.log(`[Config] Generated new Wallet Address: ${envSource.WALLET_ADDRESS}`);
  }
  config.WALLET_ADDRESS = envSource.WALLET_ADDRESS;

  config.AUTO_ACCEPT_ENABLED = true;
  config.AUTO_ACCEPT_THRESHOLD = envSource.AUTO_ACCEPT_THRESHOLD ? parseFloat(envSource.AUTO_ACCEPT_THRESHOLD) : 0.0;

  config.SOLANA_WALLET_ADDRESS = envSource.SOLANA_WALLET_ADDRESS || '';
  config.BASE_WALLET_ADDRESS = envSource.BASE_WALLET_ADDRESS || '';
  config.BTC_WALLET_ADDRESS = envSource.BTC_WALLET_ADDRESS || '';
  config.ELECTRUM_WALLET_ADDRESS = envSource.ELECTRUM_WALLET_ADDRESS || '';
  // AdSense and ad revenue configuration
  config.ADSENSE_CLIENT_ID = envSource.ADSENSE_CLIENT_ID || '';
  config.ADSENSE_AD_UNIT_ID = envSource.ADSENSE_AD_UNIT_ID || '';
  config.ADSENSE_AD_SLOT = envSource.ADSENSE_AD_SLOT || '';
  config.AD_REVENUE_THRESHOLD = envSource.AD_REVENUE_THRESHOLD ? parseFloat(envSource.AD_REVENUE_THRESHOLD) : 100;

  config.INTAKE_MODE = (envSource.INTAKE_MODE as any) || 'hybrid';

  // New owner and payment config
  config.OWNER_ID = envSource.OWNER_ID || crypto.randomUUID();
  config.PAYPAL_ME_LINK = envSource.PAYPAL_ME_LINK || '';
  config.PAYPAL_CLIENT_ID = envSource.PAYPAL_CLIENT_ID || '';
  config.PAYPAL_CLIENT_SECRET = envSource.PAYPAL_CLIENT_SECRET || '';
  config.STRIPE_SECRET_KEY = envSource.STRIPE_SECRET_KEY || config.STRIPE_SECRET_KEY || 'YOUR_STRIPE_SECRET_KEY_HERE';
  config.BTC_PRIVATE_KEY = envSource.BTC_PRIVATE_KEY || '';
  config.BITCOIN_NETWORK = envSource.BITCOIN_NETWORK === 'mainnet' ? 'mainnet' : 'testnet';
  config.AUTO_SETTLE_ON_MATCH = envSource.AUTO_SETTLE_ON_MATCH ? envSource.AUTO_SETTLE_ON_MATCH === 'true' : true;
  config.LIVE_MODE = envSource.LIVE_MODE === 'true';
  config.AUTO_WITHDRAW_ENABLED = envSource.AUTO_WITHDRAW_ENABLED === 'true';
  config.AUTO_WITHDRAW_METHOD = envSource.AUTO_WITHDRAW_METHOD === 'paypal' ? 'paypal' : 'electrum';
  config.AUTO_WITHDRAW_THRESHOLD = envSource.AUTO_WITHDRAW_THRESHOLD !== undefined ? parseFloat(envSource.AUTO_WITHDRAW_THRESHOLD) : 0.05;
  config.ACN_NETWORK_SECRET = envSource.ACN_NETWORK_SECRET || 'solomonletishitsubeyuel';
  config.MIN_PEERS_TARGET = envSource.MIN_PEERS_TARGET ? parseInt(envSource.MIN_PEERS_TARGET, 10) : 50;
  config.MAX_PEERS_TARGET = envSource.MAX_PEERS_TARGET ? parseInt(envSource.MAX_PEERS_TARGET, 10) : 100;
  config.SUPER_NODE_MODE = envSource.SUPER_NODE_MODE !== 'false';

  // Save/Rewrite .env to make sure variables persist (bypassed if environment overrides are active)
  const isOverridden = !!(process.env.NODE_ID || process.env.PORT || process.env.ACN_DATA_DIR || process.env.NODE_ENV === 'test' || process.env.ACN_TEST);
  if (!isOverridden) {
    const newEnvContent = [
      `# Autonomous Circularity Network Node Config`,
      `NODE_ID=${config.NODE_ID}`,
      `PORT=${config.PORT}`,
      `LAT=${config.LAT}`,
      `LNG=${config.LNG}`,
      `MAX_RADIUS_KM=${config.MAX_RADIUS_KM}`,
      `FEE_RATE=${config.FEE_RATE}`,
      `BOOTSTRAP_PEERS=${config.BOOTSTRAP_PEERS.join(',')}`,
      `WALLET_ADDRESS=${config.WALLET_ADDRESS}`,
      `AUTO_ACCEPT_ENABLED=${config.AUTO_ACCEPT_ENABLED}`,
      `AUTO_ACCEPT_THRESHOLD=${config.AUTO_ACCEPT_THRESHOLD}`,
      `SOLANA_WALLET_ADDRESS=${config.SOLANA_WALLET_ADDRESS}`,
      `BASE_WALLET_ADDRESS=${config.BASE_WALLET_ADDRESS}`,
      `BTC_WALLET_ADDRESS=${config.BTC_WALLET_ADDRESS}`,
      `ELECTRUM_WALLET_ADDRESS=${config.ELECTRUM_WALLET_ADDRESS}`,
      `INTAKE_MODE=${config.INTAKE_MODE}`,
      `OWNER_ID=${config.OWNER_ID}`,
      `PAYPAL_ME_LINK=${config.PAYPAL_ME_LINK}`,
      `PAYPAL_CLIENT_ID=${config.PAYPAL_CLIENT_ID}`,
      `PAYPAL_CLIENT_SECRET=${config.PAYPAL_CLIENT_SECRET}`,
      `STRIPE_SECRET_KEY=${config.STRIPE_SECRET_KEY}`,
      `BTC_PRIVATE_KEY=${config.BTC_PRIVATE_KEY}`,
      `BITCOIN_NETWORK=${config.BITCOIN_NETWORK}`,
      `ADSENSE_CLIENT_ID=${config.ADSENSE_CLIENT_ID}`,
      `ADSENSE_AD_UNIT_ID=${config.ADSENSE_AD_UNIT_ID}`,
      `ADSENSE_AD_SLOT=${config.ADSENSE_AD_SLOT}`,
      `AD_REVENUE_THRESHOLD=${config.AD_REVENUE_THRESHOLD}`,
      `AUTO_SETTLE_ON_MATCH=${config.AUTO_SETTLE_ON_MATCH}`,
      `LIVE_MODE=${config.LIVE_MODE}`,
      `AUTO_WITHDRAW_ENABLED=${config.AUTO_WITHDRAW_ENABLED}`,
      `AUTO_WITHDRAW_METHOD=${config.AUTO_WITHDRAW_METHOD}`,
      `AUTO_WITHDRAW_THRESHOLD=${config.AUTO_WITHDRAW_THRESHOLD}`,
      `ACN_NETWORK_SECRET=${config.ACN_NETWORK_SECRET}`,
      `MIN_PEERS_TARGET=${config.MIN_PEERS_TARGET}`,
      `MAX_PEERS_TARGET=${config.MAX_PEERS_TARGET}`,
      `SUPER_NODE_MODE=${config.SUPER_NODE_MODE}`,
    ].join('\n');

    const encryptedContent = encryptEnv(newEnvContent);
    fs.writeFileSync(ENV_PATH, encryptedContent, 'utf8');
    console.log(`[Config] Configuration loaded and persisted encrypted at: ${ENV_PATH}`);
  } else {
    console.log(`[Config] Configuration loaded (persistence bypassed due to active environment overrides).`);
  }
}

export function saveConfig() {
  const isOverridden = !!(process.env.NODE_ID || process.env.PORT || process.env.ACN_DATA_DIR || process.env.NODE_ENV === 'test' || process.env.ACN_TEST);
  if (isOverridden) {
    console.log(`[Config] saveConfig ignored: environment overrides are active.`);
    return;
  }

  const newEnvContent = [
    `# Autonomous Circularity Network Node Config`,
    `NODE_ID=${config.NODE_ID}`,
    `PORT=${config.PORT}`,
    `LAT=${config.LAT}`,
    `LNG=${config.LNG}`,
    `MAX_RADIUS_KM=${config.MAX_RADIUS_KM}`,
    `FEE_RATE=${config.FEE_RATE}`,
    `BOOTSTRAP_PEERS=${config.BOOTSTRAP_PEERS.join(',')}`,
    `WALLET_ADDRESS=${config.WALLET_ADDRESS}`,
    `AUTO_ACCEPT_ENABLED=${config.AUTO_ACCEPT_ENABLED}`,
    `AUTO_ACCEPT_THRESHOLD=${config.AUTO_ACCEPT_THRESHOLD}`,
    `SOLANA_WALLET_ADDRESS=${config.SOLANA_WALLET_ADDRESS}`,
    `BASE_WALLET_ADDRESS=${config.BASE_WALLET_ADDRESS}`,
    `BTC_WALLET_ADDRESS=${config.BTC_WALLET_ADDRESS}`,
    `ELECTRUM_WALLET_ADDRESS=${config.ELECTRUM_WALLET_ADDRESS}`,
    `INTAKE_MODE=${config.INTAKE_MODE}`,
    `OWNER_ID=${config.OWNER_ID}`,
    `PAYPAL_ME_LINK=${config.PAYPAL_ME_LINK}`,
    `PAYPAL_CLIENT_ID=${config.PAYPAL_CLIENT_ID}`,
    `PAYPAL_CLIENT_SECRET=${config.PAYPAL_CLIENT_SECRET}`,
    `STRIPE_SECRET_KEY=${config.STRIPE_SECRET_KEY}`,
    `BTC_PRIVATE_KEY=${config.BTC_PRIVATE_KEY}`,
    `BITCOIN_NETWORK=${config.BITCOIN_NETWORK}`,
    `ADSENSE_CLIENT_ID=${config.ADSENSE_CLIENT_ID}`,
    `ADSENSE_AD_UNIT_ID=${config.ADSENSE_AD_UNIT_ID}`,
    `ADSENSE_AD_SLOT=${config.ADSENSE_AD_SLOT}`,
    `AD_REVENUE_THRESHOLD=${config.AD_REVENUE_THRESHOLD}`,
    `AUTO_SETTLE_ON_MATCH=${config.AUTO_SETTLE_ON_MATCH}`,
    `LIVE_MODE=${config.LIVE_MODE}`,
    `AUTO_WITHDRAW_ENABLED=${config.AUTO_WITHDRAW_ENABLED}`,
    `AUTO_WITHDRAW_METHOD=${config.AUTO_WITHDRAW_METHOD}`,
    `AUTO_WITHDRAW_THRESHOLD=${config.AUTO_WITHDRAW_THRESHOLD}`,
    `ACN_NETWORK_SECRET=${config.ACN_NETWORK_SECRET}`,
    `MIN_PEERS_TARGET=${config.MIN_PEERS_TARGET}`,
    `MAX_PEERS_TARGET=${config.MAX_PEERS_TARGET}`,
    `SUPER_NODE_MODE=${config.SUPER_NODE_MODE}`,
  ].join('\n');

  const encryptedContent = encryptEnv(newEnvContent);
  fs.writeFileSync(ENV_PATH, encryptedContent, 'utf8');
  console.log(`[Config] Configuration saved encrypted at: ${ENV_PATH}`);
}

