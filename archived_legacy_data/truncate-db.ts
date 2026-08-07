import { db, initDatabase } from './src/database/db.ts';

try {
  console.log('Dropping matches and transactions tables...');
  db.exec('DROP TABLE IF EXISTS transactions;');
  db.exec('DROP TABLE IF EXISTS matches;');
  console.log('Tables dropped. Re-initializing database...');
  initDatabase();
  console.log('Database re-initialized successfully.');
} catch (e) {
  console.error(e);
}
