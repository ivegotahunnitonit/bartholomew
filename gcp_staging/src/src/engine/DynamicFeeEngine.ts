import { config } from '../config.ts';
import { db } from '../database/db.ts';

interface CompetitorFee {
  nodeId: string;
  fee: number;
  lastSeen: number;
}

const COMPETITOR_NODES: CompetitorFee[] = [
  { nodeId: 'rival-node-alpha', fee: 0.05, lastSeen: Date.now() },
  { nodeId: 'rival-node-beta', fee: 0.048, lastSeen: Date.now() },
  { nodeId: 'rival-node-gamma', fee: 0.055, lastSeen: Date.now() },
];

// Base fee range boundaries
const MIN_FEE = 0.030;   // Never drop below 3.0%
const MAX_FEE = 0.075;   // Never raise above 7.5%
const DEFAULT_FEE = 0.05; // Default 5%
const UNDERCUT_MARGIN = 0.002; // Undercut rivals by 0.2%

export class DynamicFeeEngine {
  private static currentFee = DEFAULT_FEE;
  private static isRunning = false;

  static getCurrentFee(): number {
    return this.currentFee;
  }

  static start(intervalMs = 5000) {
    if (this.isRunning) return;
    this.isRunning = true;
    console.log('[DynamicFeeEngine] Competitive fee arbitrage engine started (5s cycle)...');

    const cycle = () => {
      this.rebalanceFee();
      setTimeout(cycle, intervalMs);
    };
    cycle();
  }

  static rebalanceFee() {
    // Simulate competitor fee discovery (in production: HTTP poll competitor /api/v1/health)
    const now = Date.now();
    const hourOfDay = new Date().getHours();

    // Simulate competitor fee fluctuation
    COMPETITOR_NODES.forEach(node => {
      const jitter = (Math.random() - 0.5) * 0.01;
      node.fee = Math.max(MIN_FEE, Math.min(MAX_FEE, node.fee + jitter));
      node.lastSeen = now;
    });

    const lowestCompetitorFee = Math.min(...COMPETITOR_NODES.map(n => n.fee));
    const lowestRival = COMPETITOR_NODES.find(n => n.fee === lowestCompetitorFee)!;

    let newFee: number;

    // Off-peak (midnight–6am): maximize fee
    if (hourOfDay >= 0 && hourOfDay < 6) {
      newFee = Math.min(MAX_FEE, DEFAULT_FEE + 0.02);
      console.log(`[DynamicFeeEngine] Off-peak hours: Maximizing fee to ${(newFee * 100).toFixed(1)}%`);
    }
    // If competitor is cheaper: undercut to win volume
    else if (lowestCompetitorFee < this.currentFee) {
      newFee = Math.max(MIN_FEE, lowestCompetitorFee - UNDERCUT_MARGIN);
      console.log(`[DynamicFeeEngine] Undercutting ${lowestRival.nodeId} (${(lowestCompetitorFee * 100).toFixed(1)}%) -> New fee: ${(newFee * 100).toFixed(1)}%`);
    }
    // Otherwise: hold at slight premium (better service justifies it)
    else {
      newFee = Math.min(MAX_FEE, lowestCompetitorFee + 0.005);
      console.log(`[DynamicFeeEngine] Premium position: Fee set to ${(newFee * 100).toFixed(1)}% (rival: ${(lowestCompetitorFee * 100).toFixed(1)}%)`);
    }

    this.currentFee = newFee;

    // Persist to DB for audit trail
    try {
      const stmt = db.prepare(`INSERT OR IGNORE INTO peers (node_id, url, lat, lng, last_seen, status, score)
        VALUES (?, ?, 0, 0, ?, 'fee_record', ?) ON CONFLICT(node_id) DO UPDATE SET score = excluded.score, last_seen = excluded.last_seen`);
      stmt.run('_fee_engine', 'internal', now, newFee);
    } catch (_) {}
  }

  // Apply dynamic fee to a trade amount
  static applyFee(tradeAmountUsd: number): { fee: number; feeUsd: number; competitorAdvantage: string } {
    const feeUsd = tradeAmountUsd * this.currentFee;
    const bestRival = Math.min(...COMPETITOR_NODES.map(n => n.fee));
    const savingVsRival = ((bestRival - this.currentFee) * tradeAmountUsd).toFixed(2);
    return {
      fee: this.currentFee,
      feeUsd,
      competitorAdvantage: `$${savingVsRival} cheaper than best competitor`,
    };
  }
}
