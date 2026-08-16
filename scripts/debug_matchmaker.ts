import { DatabaseSync } from 'node:sqlite';
import { Bartholomew } from '../src/engine/Bartholomew.ts';
import { isCompatible } from '../src/engine/Matchmaker.ts';
import * as path from 'node:path';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const DB_FILE = path.join(__dirname, '../data/acn.db');

const db = new DatabaseSync(DB_FILE);

const activeWastes = db.prepare("SELECT * FROM listings WHERE type = 'waste' AND status = 'active'").all() as any[];
const activeNeeds = db.prepare("SELECT * FROM listings WHERE type = 'need' AND status = 'active'").all() as any[];

console.log('Active Wastes count:', activeWastes.length);
console.log('Active Needs count:', activeNeeds.length);

for (const waste of activeWastes) {
  for (const need of activeNeeds) {
    console.log(`\nEvaluating: Waste ${waste.id} vs Need ${need.id}`);
    console.log(`- Node ID comparison: ${waste.node_id} vs ${need.node_id}`);
    if (waste.node_id === need.node_id && waste.node_id !== 'local_node') {
      console.log('  -> Rejected: Same node ID');
      continue;
    }
    const compatible = isCompatible(waste.resource, need.resource);
    console.log(`- Compatibility: ${compatible}`);
    if (!compatible) continue;

    const buyerTargetPrice = need.price;
    const sellerListingPrice = waste.price;
    let grossSavings = (buyerTargetPrice - sellerListingPrice) * Math.min(waste.quantity, need.quantity);
    console.log(`- Initial Gross Savings: ${grossSavings}`);

    if (grossSavings < 0) {
      const histAvg = Bartholomew.getAveragePrice(waste.resource);
      console.log(`  -> Historical Average Price: ${histAvg}`);
      if (histAvg !== null) {
        console.log(`  -> Range checks: ${buyerTargetPrice} >= ${histAvg * 0.80} && ${sellerListingPrice} <= ${histAvg * 1.20}`);
        if (buyerTargetPrice >= histAvg * 0.80 && sellerListingPrice <= histAvg * 1.20) {
          grossSavings = (histAvg * Math.min(waste.quantity, need.quantity)) * 0.10;
          console.log(`  -> MATCH RESOLVED WITH DYNAMIC PRICING! Gross Savings: ${grossSavings}`);
        } else {
          console.log('  -> Rejected: Prices outside acceptable range around historical average');
        }
      } else {
        console.log('  -> Rejected: No historical average found');
      }
    }
  }
}
process.exit(0);
