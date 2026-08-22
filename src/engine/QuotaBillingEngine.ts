// QuotaBillingEngine.ts
// Monetizes ACN search & listing query API results.
// Enforces premium per-dollar request quotas:
//   - Standard Tier: $10.00 USD = 1,000 search queries ($0.01 / request)
//   - Premium Feedstock Tier: $50.00 USD = 1,000 queries ($0.05 / request)

import { db } from '../database/db.ts';

const STANDARD_COST_PER_REQUEST = 0.01;  // $10.00 per 1,000 queries
const PREMIUM_COST_PER_REQUEST = 0.05;   // $50.00 per 1,000 queries

interface QuotaAccount {
  apiKey: string;
  ownerLabel: string;
  tier: 'standard' | 'premium';
  balanceUSD: number;
  remainingRequests: number;
  totalRequestsServed: number;
  totalSpentUSD: number;
}

let totalSearchRevenueUSD = 0;
let totalSearchQueriesMonetized = 0;

export class QuotaBillingEngine {
  /**
   * Deposit credits for an API Key
   */
  static depositCredits(apiKey: string, amountUSD: number, tier: 'standard' | 'premium' = 'standard'): QuotaAccount {
    const costPerReq = tier === 'premium' ? PREMIUM_COST_PER_REQUEST : STANDARD_COST_PER_REQUEST;
    const requestsToAdd = Math.floor(amountUSD / costPerReq);
    
    const existing = db.prepare('SELECT * FROM api_keys WHERE key = ?').get(apiKey) as any;
    if (existing) {
      db.prepare(`
        UPDATE api_keys 
        SET quota_balance = quota_balance + ?, remaining_requests = remaining_requests + ?
        WHERE key = ?
      `).run(amountUSD, requestsToAdd, apiKey);
    } else {
      db.prepare(`
        INSERT INTO api_keys (key, label, quota_balance, remaining_requests, created_at)
        VALUES (?, ?, ?, ?, ?)
      `).run(apiKey, `Subscriber (${tier.toUpperCase()})`, amountUSD, requestsToAdd, Date.now());
    }

    totalSearchRevenueUSD += amountUSD;
    console.log(`[QuotaBilling]  Credited $${amountUSD.toFixed(2)} (${tier.toUpperCase()}) to API Key ${apiKey.substring(0, 10)}... (+${requestsToAdd} queries at $${costPerReq}/req)`);

    return this.getAccount(apiKey)!;
  }

  /**
   * Check and consume 1 search query request quota.
   */
  static consumeQuota(apiKey: string, isPremiumQuery = false): { allowed: boolean; remainingRequests: number; costUSD: number; error?: string } {
    const costPerReq = isPremiumQuery ? PREMIUM_COST_PER_REQUEST : STANDARD_COST_PER_REQUEST;

    if (!apiKey) {
      // Unauthenticated fallback: strictly limited to 5 free preview queries
      return { allowed: true, remainingRequests: 5, costUSD: 0 };
    }

    const row = db.prepare('SELECT remaining_requests, quota_balance FROM api_keys WHERE key = ? AND status = "active"').get(apiKey) as any;
    if (!row) {
      return { allowed: false, remainingRequests: 0, costUSD: 0, error: 'Invalid or revoked API key' };
    }

    if (row.remaining_requests <= 0) {
      return { 
        allowed: false, 
        remainingRequests: 0, 
        costUSD: costPerReq, 
        error: `Quota exhausted ($10.00 = 1,000 standard queries, $50.00 = 1,000 premium queries). Please deposit funds to resume API access.` 
      };
    }

    db.prepare('UPDATE api_keys SET remaining_requests = remaining_requests - 1 WHERE key = ?').run(apiKey);
    totalSearchQueriesMonetized++;
    totalSearchRevenueUSD += costPerReq;

    return {
      allowed: true,
      remainingRequests: row.remaining_requests - 1,
      costUSD: costPerReq,
    };
  }

  static getAccount(apiKey: string): QuotaAccount | null {
    const row = db.prepare('SELECT * FROM api_keys WHERE key = ?').get(apiKey) as any;
    if (!row) return null;
    return {
      apiKey: row.key,
      ownerLabel: row.label || 'Subscriber',
      tier: row.label?.includes('PREMIUM') ? 'premium' : 'standard',
      balanceUSD: row.quota_balance || 0,
      remainingRequests: row.remaining_requests || 0,
      totalRequestsServed: row.queries_count || 0,
      totalSpentUSD: (row.queries_count || 0) * STANDARD_COST_PER_REQUEST,
    };
  }

  static getStats() {
    return {
      standardRateUSD: '$10.00 / 1,000 queries ($0.01 / req)',
      premiumRateUSD: '$50.00 / 1,000 queries ($0.05 / req)',
      totalSearchRevenueUSD: parseFloat(totalSearchRevenueUSD.toFixed(2)),
      totalSearchQueriesMonetized,
    };
  }
}
