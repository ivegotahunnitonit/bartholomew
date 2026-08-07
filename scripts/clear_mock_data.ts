import { DatabaseSync } from 'node:sqlite';
import * as path from 'node:path';
import * as fs from 'node:fs';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const DB_DIR = process.env.ACN_DATA_DIR
  ? path.resolve(process.env.ACN_DATA_DIR)
  : path.resolve(__dirname, '../data');
const DB_FILE = path.join(DB_DIR, 'acn.db');

console.log(`[Database Reset] Connecting to database at: ${DB_FILE}`);

try {
  const dbPaths = [
    path.join(__dirname, '../data/acn.db'),
    path.join(__dirname, '../data2/acn.db')
  ];

  for (const dbPath of dbPaths) {
    if (fs.existsSync(dbPath)) {
      console.log(`[Database Reset] Clearing: ${dbPath}`);
      const db = new DatabaseSync(dbPath);
      db.exec('DELETE FROM transactions;');
      db.exec('DELETE FROM matches;');
      db.exec('DELETE FROM listings;');
      db.exec('DELETE FROM source_receipts;');
    }
  }
  
  console.log('[Database Reset] SUCCESS: Successfully cleared both node databases.');
} catch (err: any) {
  console.error('[Database Reset] ERROR clearing database:', err.message);
  process.exit(1);
}

process.exit(0);
