import { DatabaseSync } from 'node:sqlite';
import * as path from 'node:path';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const DB_FILE = path.join(__dirname, '../data/acn.db');

const db = new DatabaseSync(DB_FILE);

try {
  // Clear any existing test items
  db.exec("DELETE FROM transactions WHERE id = 't_earn'");
  db.exec("DELETE FROM matches WHERE id = 'm_earn'");
  db.exec("DELETE FROM listings WHERE id IN ('w_earn', 'n_earn')");

  // Insert mock confirmed transaction history
  db.exec("INSERT INTO listings (id, node_id, type, resource, quantity, unit, price, lat, lng, created_at, expires_at, status) VALUES ('w_earn', 'local_node', 'waste', 'bounty', 1, 'job', 600.00, 40.7128, -74.006, 0, 0, 'completed')");
  db.exec("INSERT INTO listings (id, node_id, type, resource, quantity, unit, price, lat, lng, created_at, expires_at, status) VALUES ('n_earn', 'local_node', 'need', 'bounty', 1, 'job', 600.00, 40.7128, -74.006, 0, 0, 'completed')");
  db.exec("INSERT INTO matches (id, waste_listing_id, need_listing_id, distance_km, savings_usd, fee_usd, status, created_at) VALUES ('m_earn', 'w_earn', 'n_earn', 0, 0, 0, 'completed', 0)");
  db.exec("INSERT INTO transactions (id, match_id, tx_hash, amount_usd, status, created_at, payment_method) VALUES ('t_earn', 'm_earn', 'btc_tx_dummy', 600.00, 'confirmed', 0, 'bitcoin')");
  
  console.log('[Earnings Seed] SUCCESS: Seeded $600 confirmed earnings.');
} catch (err: any) {
  console.error('[Earnings Seed] ERROR:', err.message);
}
process.exit(0);
