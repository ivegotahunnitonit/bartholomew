import { db } from './src/database/db.ts';

const count = db.prepare('SELECT count(*) as c FROM matches').get();
console.log('Matches count:', count);
