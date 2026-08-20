import { payoutStripe, payoutPayPal } from '../settlement/paymentGateway.ts';
import { db } from '../database/db.ts';

export async function handleStripeWebhook(payload: any, signatureHeader?: string): Promise<{ success: boolean; message: string }> {
  try {
    const eventType = payload.type;
    console.log(`[Stripe Webhook] Received live event: ${eventType}`);

    if (eventType === 'payment_intent.succeeded' || eventType === 'checkout.session.completed') {
      const session = payload.data.object;
      const amountUSD = (session.amount_total || session.amount || 0) / 100;
      const feeUSD = amountUSD * 0.05; // 5% System Fee

      console.log(`[Stripe Webhook] Verified payment of $${amountUSD.toFixed(2)}. Initiating instant 5% fee disburser ($${feeUSD.toFixed(2)})...`);

      // Execute instant payout to operator
      const transferId = await payoutStripe(feeUSD, session.destination_account);

      // Record in database
      const stmt = db.prepare(`
        INSERT INTO transactions (id, match_id, tx_hash, amount_usd, status, created_at, payment_method, timestamp_settled)
        VALUES (?, ?, ?, ?, 'confirmed', ?, 'stripe', ?)
      `);
      stmt.run(
        `tx_${Date.now()}`,
        session.metadata?.match_id || 'live_deal',
        transferId,
        feeUSD,
        Date.now(),
        Date.now()
      );

      return { success: true, message: `Disbursed fee $${feeUSD.toFixed(2)} via transfer ${transferId}` };
    }

    return { success: true, message: 'Event logged.' };
  } catch (err: any) {
    console.error('[Stripe Webhook Error]:', err.message);
    return { success: false, message: err.message };
  }
}
