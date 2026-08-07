import sqlite3 from 'sqlite3';
import path from 'path';
import fs from 'fs';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const dbPath = path.resolve(__dirname, '../acn_node.db');

if (!fs.existsSync(dbPath)) {
  console.log('[DB Reset] Database file not found at', dbPath);
  process.exit(0);
}

const db = new sqlite3.Database(dbPath);

console.log('[DB Reset] Connected to SQLite database.');

db.serialize(() => {
  db.run('DELETE FROM defi_yield;', (err) => {
    if (err) console.error('Error clearing defi_yield:', err);
    else console.log('Cleared defi_yield table.');
  });
  
  db.run('DELETE FROM p2p_matches;', (err) => {
    if (err) console.error('Error clearing p2p_matches:', err);
    else console.log('Cleared p2p_matches table.');
  });

  db.run('DELETE FROM transactions;', (err) => {
    if (err) console.error('Error clearing transactions:', err);
    else console.log('Cleared transactions table.');
  });
});

db.close((err) => {
  if (err) {
    console.error('Error closing db:', err.message);
  } else {
    console.log('[DB Reset] Database successfully reset. All mock data cleared.');
  }
});
