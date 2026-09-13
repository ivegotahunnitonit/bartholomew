import { PaymentManager } from "../settlement/PaymentManager.ts";
import { config } from "../config.ts";


/**
 * AdRevenueAgent
 * Periodically fetches AdSense earnings from the Netlify site and triggers
 * withdrawal when the configured threshold is reached.
 */
export class AdRevenueAgent {
  private static intervalId: NodeJS.Timer | null = null;

  /**
   * Starts the background agent.
   * The check interval is defined by AD_REVENUE_CHECK_INTERVAL_MS env var (default 30s).
   */
  static start(): void {
    const intervalMs = Number(process.env.AD_REVENUE_CHECK_INTERVAL_MS) || 30_000;
    if (this.intervalId) {
      clearInterval(this.intervalId);
    }
    this.intervalId = setInterval(async () => {
      try {
        await this.checkAndProcessRevenue();
      } catch (err) {
        console.error('[AdRevenueAgent] error:', err);
      }
    }, intervalMs);
    console.log(`[AdRevenueAgent] Started with interval ${intervalMs}ms`);
  }

  private static async fetchEarnings(): Promise<number> {
    // The Netlify URL is provided via env var AD_REVENUE_URL
    const url = process.env.AD_REVENUE_URL;
    if (!url) {
      console.warn('[AdRevenueAgent] AD_REVENUE_URL not set');
      return 0;
    }
    try {
      const res = await fetch(url);
      const html = await res.text();
      // Simple regex to extract a number like $12.34 from the page
      const match = html.match(/\$([0-9,]+\.?[0-9]*)/);
      if (match) {
        const raw = match[1].replace(/,/g, "");
        return parseFloat(raw);
      }
    } catch (e) {
      console.warn('[AdRevenueAgent] Failed to fetch earnings:', e);
    }
    return 0;
  }

  private static async checkAndProcessRevenue(): Promise<void> {
    const earnings = await this.fetchEarnings();
    console.log(`[AdRevenueAgent] Current earnings: $${earnings.toFixed(2)}`);
    const threshold = Number((config as any).AD_REVENUE_THRESHOLD) || 0;
    if (earnings >= threshold && threshold > 0) {
      console.log('[AdRevenueAgent] Threshold reached, invoking PaymentManager.processAdRevenue');
      // Directly call the processing method which will handle withdrawal
      await PaymentManager.processAdRevenue();
    }
  }
}
