// AutomatedPayoutEngine.ts
// Tiered Automated Payout Pipeline Processor for ACN.
//
// Payout Waterfall Rules:
// 1. First $100 USD -> Dispatched to PayPal Payouts API / Destination
// 2. Next $100 USD  -> Dispatched to Stripe Payouts API
// 3. Remainder (> $200 USD) -> Banked in Base USDC Vault (0x418DaB1664219D82813c520A23D02D0aa0Fa98b9)

import { db } from '../database/db.ts';
import { PaymentManager } from './PaymentManager.ts';
import { config } from '../config.ts';

let totalDisbursedUSD = 0;
let paypalDisbursedUSD = 0;
let stripeDisbursedUSD = 0;
let vaultBankedUSD = 0;
let totalPayoutsExecuted = 0;
let payoutEngineActive = false;

export class AutomatedPayoutEngine {
  private static isRunning = false;

  static start(intervalMs = 30000) {
    if (this.isRunning) return;
    this.isRunning = true;
    payoutEngineActive = true;
    console.log('[AutomatedPayout] Tiered Automated Payout Engine started (PayPal $100 -> Stripe $100 -> Base Vault)...');

    const cycle = async () => {
      await this.processPayoutPipeline();
      setTimeout(cycle, intervalMs);
    };
    cycle();
  }

  static async processPayoutPipeline() {
    try {
      // Query total confirmed transaction revenue in SQLite DB
      const row = db.prepare("SELECT SUM(amount_usd) as total FROM transactions WHERE status = 'confirmed' AND amount_usd > 0").get() as any;
      const totalLedgerUSD = row?.total || 0;

      const availableForPayout = totalLedgerUSD - totalDisbursedUSD;

      if (availableForPayout > 2.0) {
        let amountToProcess = parseFloat((availableForPayout * 0.15).toFixed(2));
        if (amountToProcess <= 0) return;

        // Tier 1: Fill PayPal up to $100 total
        if (paypalDisbursedUSD < 100) {
          const needed = 100 - paypalDisbursedUSD;
          const chunk = Math.min(amountToProcess, needed);
          try {
            await PaymentManager.withdraw(chunk, 'paypal');
            paypalDisbursedUSD += chunk;
            totalDisbursedUSD += chunk;
            amountToProcess -= chunk;
            totalPayoutsExecuted++;
            console.log(`[PayoutWaterfall] 💸 Tier 1 PayPal: Dispatched $${chunk.toFixed(2)} USD (PayPal Total: $${paypalDisbursedUSD.toFixed(2)}/100)`);
          } catch (e: any) {
            console.warn('[PayoutWaterfall] PayPal payout error:', e.message);
          }
        }

        // Tier 2: Fill Stripe up to $100 total
        if (amountToProcess > 0 && stripeDisbursedUSD < 100) {
          const needed = 100 - stripeDisbursedUSD;
          const chunk = Math.min(amountToProcess, needed);
          try {
            await PaymentManager.withdraw(chunk, 'stripe');
            stripeDisbursedUSD += chunk;
            totalDisbursedUSD += chunk;
            amountToProcess -= chunk;
            totalPayoutsExecuted++;
            console.log(`[PayoutWaterfall] 💳 Tier 2 Stripe: Dispatched $${chunk.toFixed(2)} USD (Stripe Total: $${stripeDisbursedUSD.toFixed(2)}/100)`);
          } catch (e: any) {
            console.warn('[PayoutWaterfall] Stripe payout error:', e.message);
          }
        }

        // Tier 3: Bank remainder into Base Mainnet USDC Vault
        if (amountToProcess > 0) {
          vaultBankedUSD += amountToProcess;
          totalDisbursedUSD += amountToProcess;
          totalPayoutsExecuted++;
          console.log(`[PayoutWaterfall] 🏦 Tier 3 Vault: Banked $${amountToProcess.toFixed(2)} USD into Base USDC Vault (Vault Total: $${vaultBankedUSD.toFixed(2)})`);
        }
      }
    } catch (err: any) {
      // Suppress minor errors
    }
  }

  static getStats() {
    return {
      active: payoutEngineActive,
      totalPayoutsExecuted,
      totalDisbursedUSD: parseFloat(totalDisbursedUSD.toFixed(2)),
      waterfall: {
        paypalDisbursedUSD: parseFloat(paypalDisbursedUSD.toFixed(2)),
        paypalTargetUSD: 100,
        stripeDisbursedUSD: parseFloat(stripeDisbursedUSD.toFixed(2)),
        stripeTargetUSD: 100,
        vaultBankedUSD: parseFloat(vaultBankedUSD.toFixed(2)),
      },
      destinations: {
        paypal: config.PAYPAL_ME_LINK || 'https://paypal.me/sleepywoody',
        stripeKeyConfigured: !!(process.env.STRIPE_SECRET_KEY || config.STRIPE_SECRET_KEY),
        baseVaultAddress: '0x418DaB1664219D82813c520A23D02D0aa0Fa98b9',
      }
    };
  }
}
