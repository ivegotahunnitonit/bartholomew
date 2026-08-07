import { db } from '../src/database/db.ts';

const confirmed = db.prepare("SELECT COUNT(*) as count, SUM(amount_usd) as total FROM transactions WHERE status = 'confirmed'").get() as any;
const pending = db.prepare("SELECT COUNT(*) as count, SUM(amount_usd) as total FROM transactions WHERE status = 'pending'").get() as any;
const totalListings = db.prepare("SELECT COUNT(*) as count FROM listings").get() as any;

console.log('Confirmed Ledger Transactions:', confirmed);
console.log('Pending Ledger Transactions:', pending);
console.log('Total Listings Registered:', totalListings);
