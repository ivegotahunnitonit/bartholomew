import { DatabaseSync } from 'node:sqlite';
import * as path from 'node:path';
import * as fs from 'node:fs';
import { fileURLToPath } from 'node:url';
import process from 'node:process';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Database file path - configurable via ACN_DATA_DIR for multi-node setups
const DB_DIR = process.env.ACN_DATA_DIR
  ? path.resolve(process.env.ACN_DATA_DIR)
  : path.resolve(__dirname, '../../data');
const DB_NAME = (process.env.NODE_ENV === 'test' || process.env.ACN_TEST) ? 'acn_test.db' : 'acn.db';
const DB_FILE = path.join(DB_DIR, DB_NAME);

// Ensure data directory exists
if (!fs.existsSync(DB_DIR)) {
  fs.mkdirSync(DB_DIR, { recursive: true });
}

// Initialize SQLite DatabaseSync
export const db = new DatabaseSync(DB_FILE);
db.exec('PRAGMA busy_timeout = 10000;');

/**
 * Initializes database tables if they do not exist
 */
export function initDatabase() {
  // Create listings table
  db.exec(`
    CREATE TABLE IF NOT EXISTS listings (
      id TEXT PRIMARY KEY,
      node_id TEXT NOT NULL,
      type TEXT NOT NULL CHECK(type IN ('waste', 'need')),
      resource TEXT NOT NULL,
      quantity REAL NOT NULL,
      unit TEXT NOT NULL,
      price REAL NOT NULL,
      lat REAL NOT NULL,
      lng REAL NOT NULL,
      created_at INTEGER NOT NULL,
      expires_at INTEGER NOT NULL,
      status TEXT NOT NULL DEFAULT 'active' CHECK(status IN ('active', 'matched', 'completed', 'expired')),
      signature TEXT,
      signer_address TEXT,
      declaration TEXT
    )
  `);

  // Create matches table
  db.exec(`
    CREATE TABLE IF NOT EXISTS matches (
      id TEXT PRIMARY KEY,
      waste_listing_id TEXT NOT NULL,
      need_listing_id TEXT NOT NULL,
      distance_km REAL NOT NULL,
      savings_usd REAL NOT NULL,
      fee_usd REAL NOT NULL,
      status TEXT NOT NULL DEFAULT 'proposed' CHECK(status IN ('proposed', 'accepted', 'completed', 'declined')),
      created_at INTEGER NOT NULL,
      signature TEXT,
      signer_address TEXT,
      FOREIGN KEY(waste_listing_id) REFERENCES listings(id),
      FOREIGN KEY(need_listing_id) REFERENCES listings(id)
    )
  `);

  // Create transactions table
  db.exec(`
    CREATE TABLE IF NOT EXISTS transactions (
      id TEXT PRIMARY KEY,
      match_id TEXT NOT NULL,
      tx_hash TEXT,
      amount_usd REAL NOT NULL,
      status TEXT NOT NULL DEFAULT 'pending' CHECK(status IN ('pending', 'confirming', 'confirmed', 'failed')),
      created_at INTEGER NOT NULL,
      signature TEXT,
      signer_address TEXT,
      FOREIGN KEY(match_id) REFERENCES matches(id)
    )
  `);

  // Recreating the table checks are no longer needed as the CREATE statement above and migrations handle schema consistency.

  // Migration: Add payment_method column if it doesn't exist
  try {
    db.exec(`ALTER TABLE transactions ADD COLUMN payment_method TEXT NOT NULL DEFAULT 'lightning'`);
    console.log('[Database] Migrated transactions table: added payment_method column.');
  } catch (err: any) {
    // Ignore error if column already exists
    if (!err.message.includes('duplicate column name') && !err.message.includes('already exists')) {
      console.warn('[Database] Column payment_method check failed:', err.message);
    }
  }

  // Migrations for signature and verification columns
  try {
    db.exec(`ALTER TABLE listings ADD COLUMN signature TEXT`);
  } catch (_) {}
  try {
    db.exec(`ALTER TABLE listings ADD COLUMN signer_address TEXT`);
  } catch (_) {}
  try {
    db.exec(`ALTER TABLE listings ADD COLUMN declaration TEXT`);
  } catch (_) {}

  try {
    db.exec(`ALTER TABLE matches ADD COLUMN signature TEXT`);
  } catch (_) {}
  try {
    db.exec(`ALTER TABLE matches ADD COLUMN signer_address TEXT`);
  } catch (_) {}

  try {
    db.exec(`ALTER TABLE transactions ADD COLUMN signature TEXT`);
  } catch (_) {}
  try {
    db.exec(`ALTER TABLE transactions ADD COLUMN signer_address TEXT`);
  } catch (_) {}
  try {
    db.exec(`ALTER TABLE transactions ADD COLUMN details TEXT`);
  } catch (_) {}


  // Seed system listings & matches for system transactions
  try {
    db.exec(`
      INSERT OR IGNORE INTO listings (id, node_id, type, resource, quantity, unit, price, lat, lng, created_at, expires_at, status)
      VALUES ('system-sys', 'system-node', 'waste', 'system', 1, 'unit', 0, 0, 0, 0, 9999999999, 'completed');

      INSERT OR IGNORE INTO matches (id, waste_listing_id, need_listing_id, distance_km, savings_usd, fee_usd, status, created_at)
      VALUES 
        ('match-compute', 'system-sys', 'system-sys', 0, 0, 0, 'completed', 0),
        ('match-freight', 'system-sys', 'system-sys', 0, 0, 0, 'completed', 0),
        ('match-depin', 'system-sys', 'system-sys', 0, 0, 0, 'completed', 0);
    `);
  } catch (_) {}

  // Create peers table for P2P networking
  db.exec(`
    CREATE TABLE IF NOT EXISTS peers (
      url TEXT PRIMARY KEY,
      node_id TEXT,
      lat REAL,
      lng REAL,
      last_seen INTEGER,
      status TEXT NOT NULL DEFAULT 'online' CHECK(status IN ('online', 'offline')),
      score REAL NOT NULL DEFAULT 1.0,
      uptime_count INTEGER NOT NULL DEFAULT 0,
      total_checks INTEGER NOT NULL DEFAULT 0
    )
  `);

  try {
    db.exec(`ALTER TABLE peers ADD COLUMN score REAL NOT NULL DEFAULT 1.0`);
  } catch (_) {}
  try {
    db.exec(`ALTER TABLE peers ADD COLUMN uptime_count INTEGER NOT NULL DEFAULT 0`);
  } catch (_) {}
  try {
    db.exec(`ALTER TABLE peers ADD COLUMN total_checks INTEGER NOT NULL DEFAULT 0`);
  } catch (_) {}

  // Premium and Supernode Cluster migrations
  try {
    db.exec(`ALTER TABLE listings ADD COLUMN verified_by_lab INTEGER NOT NULL DEFAULT 0`);
  } catch (_) {}
  try {
    db.exec(`ALTER TABLE listings ADD COLUMN safety_sheet_url TEXT`);
  } catch (_) {}
  try {
    db.exec(`ALTER TABLE listings ADD COLUMN priority_routing INTEGER NOT NULL DEFAULT 0`);
  } catch (_) {}
  try {
    db.exec(`ALTER TABLE matches ADD COLUMN routing_path TEXT`);
  } catch (_) {}

  console.log(`[Database] Initialized successfully at: ${DB_FILE}`);

  // Create source_receipts table — written by ExternalMatchScout whenever it finds something
  db.exec(`
    CREATE TABLE IF NOT EXISTS source_receipts (
      id TEXT PRIMARY KEY,
      discovered_at INTEGER NOT NULL,
      source_type TEXT NOT NULL,
      source_label TEXT NOT NULL,
      agent TEXT NOT NULL,
      resource TEXT NOT NULL,
      quantity REAL NOT NULL,
      unit TEXT NOT NULL,
      price_per_unit REAL NOT NULL,
      lat REAL NOT NULL,
      lng REAL NOT NULL,
      listing_type TEXT NOT NULL,
      listing_id TEXT,
      match_id TEXT,
      notes TEXT
    )
  `);

  // Create api_keys table for monetized external access
  db.exec(`
    CREATE TABLE IF NOT EXISTS api_keys (
      key TEXT PRIMARY KEY,
      label TEXT NOT NULL,
      status TEXT NOT NULL DEFAULT 'active' CHECK(status IN ('active', 'revoked')),
      created_at INTEGER NOT NULL,
      queries_count INTEGER NOT NULL DEFAULT 0,
      quota_balance REAL NOT NULL DEFAULT 0,
      remaining_requests INTEGER NOT NULL DEFAULT 0
    )
  `);

  try { db.exec(`ALTER TABLE api_keys ADD COLUMN quota_balance REAL NOT NULL DEFAULT 0`); } catch (_) {}
  try { db.exec(`ALTER TABLE api_keys ADD COLUMN remaining_requests INTEGER NOT NULL DEFAULT 0`); } catch (_) {}

  // Create defi_yield table for automated staking tracking
  db.exec(`
    CREATE TABLE IF NOT EXISTS defi_yield (
      id TEXT PRIMARY KEY,
      staked_balance REAL NOT NULL DEFAULT 0,
      yield_earned REAL NOT NULL DEFAULT 0,
      last_accrued INTEGER NOT NULL,
      auto_stake INTEGER NOT NULL DEFAULT 0
    )
  `);
  // Seed default row if empty
  try {
    const row = db.prepare("SELECT COUNT(*) as count FROM defi_yield").get() as any;
    if (row?.count === 0) {
      db.prepare("INSERT INTO defi_yield (id, staked_balance, yield_earned, last_accrued, auto_stake) VALUES ('singleton', 0, 0, ?, 1)")
        .run(Date.now());
    }
  } catch (e) {
    console.error('[Database] Failed to seed defi_yield row:', e);
  }

  // Migration: add transaction detail columns if missing
  const txMigrations = [
    { col: 'timestamp_settled', def: 'INTEGER' },
    { col: 'block_number',      def: 'INTEGER' },
    { col: 'network_gas_fee',   def: 'TEXT' },
    { col: 'confirmations',     def: 'INTEGER NOT NULL DEFAULT 0' },
    { col: 'details',           def: 'TEXT' },
  ];
  for (const m of txMigrations) {
    try {
      db.exec(`ALTER TABLE transactions ADD COLUMN ${m.col} ${m.def}`);
    } catch (_) { /* column already exists */ }
  }

  // Make match_id nullable if it isn't already (migration for older DBs)
  try {
    db.exec(`INSERT INTO transactions (id, amount_usd, status, created_at) VALUES ('__nullable_test__', 0, 'pending', 0)`);
    db.exec(`DELETE FROM transactions WHERE id = '__nullable_test__'`);
  } catch (_) {
    // match_id is still NOT NULL — drop and recreate
    console.log('[Database] Making match_id nullable in transactions table...');
    db.exec(`CREATE TABLE IF NOT EXISTS transactions_new (
      id TEXT PRIMARY KEY,
      match_id TEXT,
      tx_hash TEXT,
      amount_usd REAL NOT NULL,
      status TEXT NOT NULL DEFAULT 'pending' CHECK(status IN ('pending', 'confirming', 'confirmed', 'failed')),
      created_at INTEGER NOT NULL,
      payment_method TEXT NOT NULL DEFAULT 'lightning',
      timestamp_settled INTEGER,
      block_number INTEGER,
      network_gas_fee TEXT,
      confirmations INTEGER NOT NULL DEFAULT 0,
      details TEXT,
      FOREIGN KEY(match_id) REFERENCES matches(id)
    )`);
    db.exec(`INSERT OR IGNORE INTO transactions_new SELECT id, match_id, tx_hash, amount_usd, status, created_at, payment_method, timestamp_settled, block_number, network_gas_fee, confirmations, NULL FROM transactions`);
    db.exec(`DROP TABLE transactions`);
    db.exec(`ALTER TABLE transactions_new RENAME TO transactions`);
  }
}

// Automatically initialize database schema on module load
initDatabase();
