import { db } from './src/database/db.ts';

const count = db.prepare("SELECT count(*) as c FROM peers WHERE status = 'online' AND lat IS NOT NULL AND lng IS NOT NULL").get();
console.log('Online peers count:', count);
