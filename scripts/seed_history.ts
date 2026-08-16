import { DatabaseSync } from 'node:sqlite';
import * as path from 'node:path';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const DB_FILE = path.join(__dirname, '../data/acn.db');

const db = new DatabaseSync(DB_FILE);

try {
  // Clear any existing test items
  db.exec("DELETE FROM transactions WHERE id = 't_test'");
  db.exec("DELETE FROM matches WHERE id = 'm_test'");
  db.exec("DELETE FROM listings WHERE id IN ('w_test', 'n_test')");

  // Insert mock confirmed transaction history
  db.exec("INSERT INTO listings (id, node_id, type, resource, quantity, unit, price, lat, lng, created_at, expires_at, status) VALUES ('w_test', 'local', 'waste', 'spent brewer grain', 100, 'kg', 0.10, 40.7128, -74.006, 0, 0, 'completed')");
  db.exec("INSERT INTO listings (id, node_id, type, resource, quantity, unit, price, lat, lng, created_at, expires_at, status) VALUES ('n_test', 'local', 'need', 'spent brewer grain', 100, 'kg', 0.10, 40.7128, -74.006, 0, 0, 'completed')");
  db.exec("INSERT INTO matches (id, waste_listing_id, need_listing_id, distance_km, savings_usd, fee_usd, status, created_at) VALUES ('m_test', 'w_test', 'n_test', 0, 0, 0, 'completed', 0)");
  db.exec("INSERT INTO transactions (id, match_id, tx_hash, amount_usd, status, created_at, payment_method) VALUES ('t_test', 'm_test', 'tx_hash_test', 0.10, 'confirmed', 0, 'lightning')");
  
  console.log('[History Seed] SUCCESS: Seeded historical price trends for spent brewer grain.');
} catch (err: any) {
  console.error('[History Seed] ERROR:', err.message);
}
process.exit(0);
