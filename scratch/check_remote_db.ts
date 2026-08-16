import { db } from '../src/database/db.ts';

try {
  const txStats = db.prepare(`SELECT status, count(id) as count, sum(amount_usd) as total FROM transactions GROUP BY status`).all();
  console.log('--- REMOTE DB TRANSACTIONS ---');
  console.log(JSON.stringify(txStats, null, 2));

  const totalConfirmed = db.prepare(`SELECT sum(amount_usd) as total FROM transactions WHERE status = 'confirmed'`).get();
  console.log('Total Confirmed USD:', totalConfirmed);

  const payoutHistory = db.prepare(`SELECT * FROM transactions WHERE status = 'confirmed' ORDER BY created_at DESC LIMIT 10`).all();
  console.log('--- RECENT CONFIRMED PAYOUT TRANSACTIONS ---');
  console.log(JSON.stringify(payoutHistory, null, 2));
} catch (err: any) {
  console.error('Error querying DB:', err.message);
}
