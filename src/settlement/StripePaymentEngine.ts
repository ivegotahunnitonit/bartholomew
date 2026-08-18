// StripePaymentEngine.ts
// Handles Stripe Direct Payouts (/v1/payouts) to Itsub Alemayehu's
// linked bank account (acct_1KCRy9DwLfE70w9S).

import { config } from '../config.ts';

const STRIPE_SECRET_KEY = process.env.STRIPE_SECRET_KEY || config.STRIPE_SECRET_KEY || '';

export class StripePaymentEngine {
  /**
   * Dispatch a direct payout sweep to the connected bank account (/v1/payouts)
   */
  static async createBankPayout(amountUSD: number, currency: string = 'cad') {
    const params = new URLSearchParams();
    const amountCents = Math.round(amountUSD * 100);
    params.append('amount', amountCents.toString());
    params.append('currency', currency.toLowerCase());
    params.append('description', 'ACN Automated Protocol Yield Sweep');

    const res = await fetch('https://api.stripe.com/v1/payouts', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${STRIPE_SECRET_KEY}`,
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: params.toString(),
    });

    if (!res.ok) {
      const errText = await res.text();
      throw new Error(`Stripe Payout Error: ${res.status} ${errText}`);
    }

    return await res.json();
  }

  /**
   * Cancel an active Checkout Session if expired/abandoned
   */
  static async expireCheckoutSession(sessionId: string) {
    const res = await fetch(`https://api.stripe.com/v1/checkout/sessions/${sessionId}/expire`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${STRIPE_SECRET_KEY}`,
      },
    });

    if (!res.ok) {
      const errText = await res.text();
      throw new Error(`Stripe Expire Error: ${res.status} ${errText}`);
    }

    return await res.json();
  }
}

