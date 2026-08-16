import { db } from '../src/database/db.ts';

console.log('Running production reset: Wiping all simulated ledger data...');

try {
  // Clear all data
  db.exec('DELETE FROM transactions;');
  db.exec('DELETE FROM source_receipts;');
  db.exec('DELETE FROM matches;');
  db.exec('DELETE FROM listings;');
  
  console.log('Database successfully wiped. Node is now at zero state.');
} catch (err: any) {
  console.error('Failed to wipe database:', err.message);
}
