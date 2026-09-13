import { db } from '../database/db.ts';
import { payoutStripe } from '../settlement/paymentGateway.ts';

export interface MonitorSubscription {
  clientId: string;
  email: string;
  tier: 'basic' | 'pro' | 'enterprise';
  monthlyFeeUsd: number;
  createdAt: number;
  nextBillingAt: number;
  alerts: string[];
}

const TIER_PRICES: Record<string, number> = {
  basic: 49,
  pro: 149,
  enterprise: 299,
};

// In-memory subscriber registry (persists to DB in production)
const subscribers: MonitorSubscription[] = [];

export class MonitorAgent {
  private static isRunning = false;
  private static totalMRR = 0; // Monthly Recurring Revenue

  static start(intervalMs = 30000) {
    if (this.isRunning) return;
    this.isRunning = true;
    console.log('[MonitorAgent] Monitoring-as-a-Service engine started (30s billing check cycle)...');

    const cycle = () => {
      this.runMonitoringCycle();
      setTimeout(cycle, intervalMs);
    };
    cycle();
  }

  static subscribe(clientId: string, email: string, tier: 'basic' | 'pro' | 'enterprise'): MonitorSubscription {
    const monthlyFeeUsd = TIER_PRICES[tier];
    const sub: MonitorSubscription = {
      clientId,
      email,
      tier,
      monthlyFeeUsd,
      createdAt: Date.now(),
      nextBillingAt: Date.now() + 30 * 24 * 60 * 60 * 1000, // 30 days
      alerts: [],
    };
    subscribers.push(sub);
    this.totalMRR += monthlyFeeUsd;
    console.log(`[MonitorAgent] New subscriber: ${email} (${tier} tier @ $${monthlyFeeUsd}/mo). MRR: $${this.totalMRR}/mo`);
    return sub;
  }

  static runMonitoringCycle() {
    const now = Date.now();

    // Check for billing renewals
    for (const sub of subscribers) {
      if (now >= sub.nextBillingAt) {
        console.log(`[MonitorAgent] Billing renewal: ${sub.email} (${sub.tier}) $${sub.monthlyFeeUsd}`);
        payoutStripe(sub.monthlyFeeUsd, undefined).catch(() => {});
        sub.nextBillingAt = now + 30 * 24 * 60 * 60 * 1000;
      }
    }

    // Generate live health alerts for subscribers
    try {
      const activeListings = (db.prepare('SELECT count(*) as c FROM listings WHERE status=\'active\'').get() as any).c;
      const pendingMatches = (db.prepare('SELECT count(*) as c FROM matches WHERE status=\'proposed\'').get() as any).c;

      if (pendingMatches > 10) {
        subscribers.filter(s => s.tier !== 'basic').forEach(s => {
          s.alerts.push(`[ALERT ${new Date().toISOString()}] High match queue depth: ${pendingMatches} pending deals`);
        });
      }

      if (activeListings < 5) {
        subscribers.filter(s => s.tier === 'enterprise').forEach(s => {
          s.alerts.push(`[ALERT ${new Date().toISOString()}] Low liquidity warning: only ${activeListings} active listings`);
        });
      }
    } catch (_) {}
  }

  static getMRR(): number {
    return this.totalMRR;
  }

  static getSubscribers(): MonitorSubscription[] {
    return subscribers;
  }
}
